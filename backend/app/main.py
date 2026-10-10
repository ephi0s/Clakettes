"""Clakettes API entry point.

Architecture: FastAPI app with layered structure (Routers → Services → Models).
Initializes database, middleware, routers, and WebSocket chat backend.
"""

import logging
import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
from app.rate_limiter import RateLimiter
from app.dav import auth as dav_auth
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.routers import (
    festival_rulebooks,
    festivals,
    users,
    shortfilms,
    chat,
    auth,
    auth_sessions,
    user_festival,
    uploads,
    search,
    admin,
    notifications,
    roles,
    events,
    channels,
    keys,
    participant_tags,
    user_roles,
    user_aliases,
    validation_rules,
    registration_forms,
    role_groups,
    committees,
    delegations,
    locations,
    location_tags,
    location_images,
    location_relations,
    shortfilm_locations,
    form_definitions,
    calendar,
    dav,
    payments,
)
from app.chat_backend import WebSocketChatBackend, chat_backend_registry
from app.database import engine, SessionLocal
from app.models.base import Base
from app.models.user import User
from app.services.user_service import hash_password
from app.config import settings

# Maximum request body size: 10 MB
MAX_BODY_SIZE = 10 * 1024 * 1024
DAV_PREFIX = "/dav"
# Default insecure key - must be overridden in production via SECRET_KEY env var
INSECURE_SECRET_KEY = "your-secret-key-change-in-production"

logger = logging.getLogger(__name__)


def _validate_secret_key():
    """Block startup in production when SECRET_KEY is not set via env.

    In production (APP_ENV=production), raises RuntimeError if the default
    insecure key is detected. In development, logs a warning only.
    """
    if settings.SECRET_KEY == INSECURE_SECRET_KEY:
        if settings.is_production:
            raise RuntimeError(
                "SECRET_KEY must be set via environment variables in production "
                "(APP_ENV=production). Generate one with: "
                'python -c "import secrets; print(secrets.token_urlsafe(64))"'
            )
        logger.warning(
            "SECRET_KEY is using the insecure default. Set SECRET_KEY in .env or the environment before deploying."
        )
    if settings.is_production and settings.cors_origins_list == ["*"]:
        raise RuntimeError(
            "CORS_ORIGINS must be set to explicit origins in production (APP_ENV=production). "
            "Wildcard '*' is not allowed with credentials."
        )


_validate_secret_key()


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds security headers to every response for defense-in-depth.

    Headers added:
    - X-Content-Type-Options: nosniff — Prevents MIME type sniffing
    - X-Frame-Options: DENY — Prevents clickjacking via iframes
    - X-XSS-Protection: 1; mode=block — Legacy XSS filter (older browsers)
    - Referrer-Policy: strict-origin-when-cross-origin — Controls referrer info
    - Permissions-Policy: camera=(), microphone=(), geolocation=() — Disables powerful features
    - X-Dev-Mode: true (only in dev) — Indicates insecure default key in use
    """

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return response


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Reject requests with bodies larger than MAX_BODY_SIZE (10 MB).

    Checks Content-Length header before processing request body.
    Returns 413 Payload Too Large if exceeded.
    """

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > MAX_BODY_SIZE:
                    return Response(
                        content='{"detail":"Request body too large"}',
                        status_code=413,
                        media_type="application/json",
                    )
            except ValueError:
                pass
        return await call_next(request)


def _redact_dav_path(path: str) -> str:
    """Replace a DAV credential in the path with ``***`` so access logs stay safe.

    A DAV token placed in the URL is a bearer credential: anything that can read
    the log can impersonate the user. ``u<id>`` principals carry no secret, so
    they are left readable to keep the logs useful.
    """
    if not path.startswith(DAV_PREFIX):
        return path
    rest = path[len(DAV_PREFIX) :].lstrip("/")
    principal, separator, tail = rest.partition("/")
    if not principal or dav_auth.PRINCIPAL_ID_RE.match(principal):
        return path
    return f"{DAV_PREFIX}/***{separator}{tail}"


class RedactDavTokenMiddleware:
    """Scrub DAV tokens out of the ASGI scope once the response is produced.

    Uvicorn builds its access-log line from ``scope["path"]`` after the app call
    returns, so rewriting the scope here removes the credential from the log
    without touching routing or authentication, which have already happened.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        await self.app(scope, receive, send)
        if scope.get("type") != "http":
            return
        path = scope.get("path", "")
        redacted = _redact_dav_path(path)
        if redacted != path:
            scope["path"] = redacted
            scope["raw_path"] = redacted.encode()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """SQLite-backed rate limiter that works across multiple workers.

    Single RateLimiter instance with two key-prefixed buckets: everything
    outside ``/dav`` shares the default budget (100/60s), while ``/dav``
    gets its own larger budget (600/60s) because CalDAV clients poll
    aggressively and a 429 breaks a subscription.
    Disabled when TESTING=true environment variable is set.
    """

    def __init__(
        self,
        app,
        max_requests: int = 100,
        window_seconds: int = 60,
        dav_max_requests: int = 600,
        dav_window_seconds: int = 60,
    ):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.dav_max_requests = dav_max_requests
        self.dav_window_seconds = dav_window_seconds
        self._limiter = RateLimiter()

    async def dispatch(self, request: Request, call_next):
        if os.environ.get("TESTING", "").lower() in ("true", "1"):
            return await call_next(request)
        ip = request.client.host if request.client else "unknown"
        if request.url.path.startswith(DAV_PREFIX):
            key = f"dav:{ip}"
            max_requests, window = self.dav_max_requests, self.dav_window_seconds
        else:
            key = f"middleware:{ip}"
            max_requests, window = self.max_requests, self.window_seconds
        if not self._limiter.check(key, max_requests, window):
            return Response(content='{"detail":"Too many requests"}', status_code=429, media_type="application/json")
        return await call_next(request)


def _warn_about_dav_transport():
    """Warn when a production deployment may expose DAV tokens over plain HTTP.

    The DAV token is a long-lived bearer credential that clients are expected to
    put in the URL. Over HTTP it leaks to proxies and to anyone reading the
    network, so a production run without a trusted proxy in front cannot be
    verified as TLS-terminated.
    """
    if not settings.is_production:
        return
    logger.warning(
        "CalDAV tokens are bearer credentials sent in the URL. "
        "Terminate TLS in front of this service; the token is redacted from "
        "access logs but never from the wire."
    )
    if not os.environ.get("FORWARDED_ALLOW_IPS"):
        logger.warning(
            "FORWARDED_ALLOW_IPS is not set, so this process cannot verify that "
            "requests arrived over HTTPS. Set it to the address of your reverse "
            "proxy and run uvicorn with --proxy-headers."
        )


def _init_admin_user():
    """Create the default admin user on first startup (development only).

    Only runs in non-production environments. Creates user 'admin' with
    password 'setup' — MUST be changed on first login.
    Skipped if admin user already exists.
    """
    if settings.is_production:
        return
    db = SessionLocal()
    try:
        if db.query(User).filter(User.username == "admin").first():
            return
        admin = User(
            username="admin",
            email="admin@clakettes.com",
            password_hash=hash_password("setup"),
            full_name="Administrator",
            role="admin",
            bio="Platform administrator for Clakettes",
            is_active=True,
            is_public=True,
        )
        db.add(admin)
        db.commit()
        logger.info("Default admin user created (username=admin, password=setup)")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Application lifespan manager.

    Startup:
    1. Create database tables (dev only; prod uses Alembic migrations)
    2. Create default admin user (dev only)
    3. Initialize WebSocket chat backend

    Shutdown:
    - Stop chat backend gracefully
    """
    if not settings.is_production:
        Base.metadata.create_all(bind=engine)

    _warn_about_dav_transport()

    _init_admin_user()

    # Initialise the real-time chat backend (WebSockets by default).
    chat_backend = WebSocketChatBackend()
    chat_backend_registry.register(chat_backend)
    await chat_backend.start()

    yield

    await chat_backend.stop()


app = FastAPI(
    title="Clakettes API",
    description="Backend API for Clakettes film festival management platform",
    version="0.3.0",
    lifespan=lifespan,
)

# --- Exception handlers ---


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler — catches unhandled exceptions and returns 500.

    Logs full traceback for debugging. Returns generic error message to client
    to avoid leaking internal details.
    """
    import logging

    logger = logging.getLogger(__name__)
    logger.exception("Unhandled exception: %s", exc)
    return Response(
        content='{"detail":"Internal server error"}',
        status_code=500,
        media_type="application/json",
    )


# --- Middleware (order matters: last added = first executed) ---
# Execution order (outermost to innermost):
# 1. GZipMiddleware - compress responses > 1KB
# 2. SecurityHeadersMiddleware - add security headers
# 3. RequestSizeLimitMiddleware - reject oversized payloads
# 4. RateLimitMiddleware - limit requests per IP (100/60s, /dav gets 600/60s)
# 5. TrustedHostMiddleware - validate Host header (if explicit CORS origins)
# 6. CORSMiddleware - handle CORS preflight and headers
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestSizeLimitMiddleware)
app.add_middleware(
    RateLimitMiddleware, max_requests=100, window_seconds=60, dav_max_requests=600, dav_window_seconds=60
)

uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

# TrustedHostMiddleware only added when explicit CORS origins configured
# (not wildcard) to prevent Host header injection
if settings.CORS_ORIGINS and settings.CORS_ORIGINS.strip():
    allowed_hosts = [
        h.strip().replace("https://", "").replace("http://", "").split(":")[0] for h in settings.cors_origins_list
    ]
    if allowed_hosts and "*" not in allowed_hosts:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Outermost on purpose: it rewrites the ASGI scope after every inner layer has
# answered, so uvicorn logs a redacted path while routing and auth stay intact.
app.add_middleware(RedactDavTokenMiddleware)

# --- Routers (34 total) ---
# Organized by domain. Prefix determines URL path.
# Tags used for OpenAPI/Swagger grouping.
app.include_router(festivals.router, prefix="/api/festivals", tags=["festivals"])
app.include_router(
    festival_rulebooks.router,
    prefix="/api/festivals/{festival_id}/rulebooks",
    tags=["festival-rulebooks"],
)
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(shortfilms.router, prefix="/api/shortfilms", tags=["shortfilms"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(auth.router, prefix="/api/users", tags=["auth"])
app.include_router(auth_sessions.router, prefix="/api/auth", tags=["auth"])
app.include_router(user_festival.router, prefix="/api/festivals", tags=["user-festival"])
app.include_router(uploads.router, prefix="/api/uploads", tags=["uploads"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(roles.router, prefix="/api", tags=["roles"])
app.include_router(participant_tags.router, prefix="/api", tags=["participant-tags"])
app.include_router(user_roles.router, prefix="/api", tags=["user-roles"])
app.include_router(user_aliases.router, prefix="/api", tags=["user-aliases"])
app.include_router(validation_rules.router, prefix="/api", tags=["validation-rules"])
app.include_router(registration_forms.router, prefix="/api", tags=["registration-forms"])
app.include_router(role_groups.router, prefix="/api", tags=["role-groups"])
app.include_router(committees.router, prefix="/api", tags=["committees"])
app.include_router(delegations.router, prefix="/api", tags=["delegations"])
app.include_router(events.router, prefix="/api", tags=["events"])
app.include_router(channels.router, prefix="/api/channels", tags=["channels"])
app.include_router(keys.router, prefix="/api/users", tags=["e2ee"])
app.include_router(locations.router, prefix="/api/locations", tags=["locations"])
app.include_router(location_tags.router, prefix="/api/locations/{location_id}/tags", tags=["location-tags"])
app.include_router(
    location_images.router,
    prefix="/api/locations/{location_id}/images",
    tags=["location-images"],
)
app.include_router(
    location_relations.router,
    prefix="/api/locations/{location_id}/relations",
    tags=["location-relations"],
)
app.include_router(
    shortfilm_locations.router,
    prefix="/api/shortfilms/{shortfilm_id}/locations",
    tags=["shortfilm-locations"],
)
app.include_router(form_definitions.router, prefix="/api", tags=["forms"])
app.include_router(calendar.router, prefix="/api/calendar", tags=["calendar"])
app.include_router(payments.router, prefix="/api", tags=["payments"])
app.include_router(dav.router, prefix="/dav", tags=["dav"])


@app.get("/")
async def root():
    return {"message": "Clakettes API is running", "version": "0.3.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
