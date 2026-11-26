"""Middleware y validaciones de seguridad de la API.

Este módulo concentra las defensas transversales (cabeceras, límite de cuerpo,
limitación de peticiones, redacción de tokens DAV y validación de arranque)
para que ``main.py`` solo se ocupe de componer la aplicación.
"""

import logging
import os
import re

from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.dav import auth as dav_auth
from app.http_utils import client_ip
from app.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

MAX_BODY_SIZE = 10 * 1024 * 1024
DAV_PREFIX = "/dav"
INSECURE_SECRET_KEYS = {
    "your-secret-key-change-in-production",
    "cambien-esto-por-una-clave-aleatoria-de-64-caracteres",
    "cambia-esta-clave-en-produccion",
    "dev-secret-change-in-production",
    "change-me",
    "secret",
}

# Dominios de nodo federado: hostname DNS sin puerto, path ni userinfo.
PEER_DOMAIN_RE = re.compile(r"^(?=.{1,253}$)(?!-)[a-z0-9-]{1,63}(?<!-)(\.(?!-)[a-z0-9-]{1,63}(?<!-))+$", re.IGNORECASE)


def is_safe_peer_domain(domain: object) -> bool:
    """Acepta solo nombres DNS que puedan ser un nodo federado.

    Rechaza direcciones IP, ``localhost``, puertos, rutas y cualquier carácter
    que permita construir una URL distinta a ``https://<dominio>/...``.
    """
    if not isinstance(domain, str) or not PEER_DOMAIN_RE.fullmatch(domain.strip()):
        return False
    candidate = domain.strip().lower()
    if candidate in {"localhost", "localhost.localdomain"} or candidate.endswith(".localhost"):
        return False
    if re.fullmatch(r"[0-9.]+", candidate):
        return False
    return True


def validate_secret_key() -> None:
    """Bloquea el arranque en producción con configuración insegura."""
    if settings.SECRET_KEY in INSECURE_SECRET_KEYS or len(settings.SECRET_KEY) < 32:
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
    if settings.is_production:
        if not settings.DATABASE_URL.startswith("mariadb"):
            raise RuntimeError(
                "DATABASE_URL must use MariaDB in production (APP_ENV=production), "
                "e.g. mariadb+pymysql://user:pass@host:3306/db?ssl_ca=/run/secrets/db-ca.pem"
            )
        from urllib.parse import parse_qsl, urlsplit

        query = dict(parse_qsl(urlsplit(settings.DATABASE_URL).query))
        tls_keys = {"ssl_ca", "ssl_cert", "ssl_key", "ssl_verify_cert", "ssl_verify_identity"}
        if "ssl" in query:
            raise RuntimeError(
                "DATABASE_URL uses '?ssl=...', which PyMySQL cannot parse. "
                "Use '?ssl_ca=/path/to/ca.pem' (or ssl_verify_identity=true) instead."
            )
        if not any(key in query for key in tls_keys):
            raise RuntimeError(
                "DATABASE_URL must enable TLS in production (APP_ENV=production), "
                "e.g. mariadb+pymysql://user:pass@host:3306/db?ssl_ca=/run/secrets/db-ca.pem"
            )
        if not (settings.PUBLIC_BASE_URL or "").strip():
            raise RuntimeError("PUBLIC_BASE_URL must be set to the public origin in production (APP_ENV=production).")


# Alias conservado para tests y herramientas que importaban el nombre antiguo.
_validate_secret_key = validate_secret_key


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Añade cabeceras de defensa en profundidad a cada respuesta."""

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        if request.url.path.lower().endswith(".svg"):
            # Los SVG son documentos XML ejecutables: nunca los sirvamos con
            # scripts activos, aunque pasaran el filtro de-subcadena de badges.
            response.headers["Content-Security-Policy"] = "default-src 'none'; sandbox"
        elif request.url.path in ("/docs", "/redoc", "/openapi.json"):
            response.headers["Content-Security-Policy"] = "frame-ancestors 'none'"
        else:
            response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"
        if settings.is_production:
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
        return response


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Rechaza peticiones cuyo cuerpo supera ``MAX_BODY_SIZE``."""

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > MAX_BODY_SIZE:
                    return JSONResponse(status_code=413, content={"detail": "Request body too large"})
            except ValueError:
                pass
            return await call_next(request)
        body = await request.body()
        if len(body) > MAX_BODY_SIZE:
            return JSONResponse(status_code=413, content={"detail": "Request body too large"})
        return await call_next(request)


def redact_dav_path(path: str) -> str:
    """Sustituye una credencial DAV de la URL por ``***`` en los logs."""
    if not path.startswith(DAV_PREFIX):
        return path
    rest = path[len(DAV_PREFIX) :].lstrip("/")
    principal, separator, tail = rest.partition("/")
    if not principal or dav_auth.PRINCIPAL_ID_RE.match(principal):
        return path
    return f"{DAV_PREFIX}/***{separator}{tail}"


_redact_dav_path = redact_dav_path


class RedactDavTokenMiddleware:
    """Reescribe el scope ASGI tras responder para que uvicorn no loguee el token."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        await self.app(scope, receive, send)
        if scope.get("type") != "http":
            return
        path = scope.get("path", "")
        redacted = redact_dav_path(path)
        if redacted != path:
            scope["path"] = redacted
            scope["raw_path"] = redacted.encode()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Limitador por IP con presupuesto propio para CalDAV."""

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
        if os.environ.get("TESTING", "").strip().lower() in ("1", "true", "yes", "on"):
            return await call_next(request)
        ip = client_ip(request)
        if request.url.path.startswith(DAV_PREFIX):
            key = f"dav:{ip}"
            max_requests, window = self.dav_max_requests, self.dav_window_seconds
        else:
            key = f"middleware:{ip}"
            max_requests, window = self.max_requests, self.window_seconds
        if not self._limiter.check(key, max_requests, window):
            return JSONResponse(status_code=429, content={"detail": "Too many requests"})
        return await call_next(request)


def configure_trusted_hosts(app) -> None:
    """Añade validación de Host solo cuando hay orígenes CORS explícitos."""
    if not settings.CORS_ORIGINS or not settings.CORS_ORIGINS.strip():
        return
    allowed_hosts = [
        h.strip().replace("https://", "").replace("http://", "").split(":")[0] for h in settings.cors_origins_list
    ]
    if allowed_hosts and "*" not in allowed_hosts:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)


def configure_cors(app) -> None:
    """Configura CORS sin comodín cuando se permiten credenciales."""
    allow_origins = settings.cors_origins_list
    if "*" in allow_origins and settings.cors_allow_credentials:
        allow_origins = []
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=settings.cors_allow_credentials and bool(allow_origins),
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Requested-With", "X-Webhook-Secret"],
    )
