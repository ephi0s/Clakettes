---
name: backend-python-fastapi-expert
description: Expert guidance for Clakettes FastAPI backend. Covers project structure (Routers → Services → Models), JWT auth with session tracking (access + refresh tokens), SQLite-backed rate limiter (100/60s), pytest with httpx (asyncio_mode=auto), SQLAlchemy patterns (SQLite/MariaDB dual), pydantic-settings, Alembic migrations, and enums.py shared across layers. Use when working on backend API endpoints, services, models, or tests.
metadata:
  model: models/gemini-3.1-pro-preview
  last_modified: Tue, 23 Jun 2026 01:43:00 GMT
---
# Backend Python/FastAPI Expert

## Architecture Layers

`backend/app/`: **Routers** (24) → **Services** (business logic) → **Models** (SQLAlchemy, 25+)

- **Routers** (`routers/`): Define endpoints, validate with Pydantic schemas (`schemas/`), call services.
- **Services** (`services/`): Business logic, CRUD, orchestration. `base_service.py` provides generic CRUD.
- **Models** (`models/`): SQLAlchemy ORM. All inherit from `BaseModel` (`models/base.py`) providing `id`, `created_at`, `updated_at` (via `datetime.now(timezone.utc)`, not `func.now()`).
- **Schemas** (`schemas/`): Pydantic models for request/response validation.
- **Enums** (`enums.py`): Shared enumerations (RoleScope, UserRoleStatus, EventType, etc.) — the only cross-layer type.

**Golden rule**: Models never import schemas, schemas never import models. Both use `app.enums`.

## Entrypoint

`app/main.py` creates the FastAPI app with:
- `lifespan` handler: `Base.metadata.create_all()`, seeds admin user (`admin`/`setup`), starts WebSocket chat backend
- Middleware (last added = first executed): CORS → TrustedHost (non-dev only) → RateLimit (100/60s, skips when TESTING=true) → SecurityHeaders
- 24 routers registered under `/api/...`, plus `/health` and `/api/health`
- Static files mounted at `/uploads`

## Auth

- `POST /api/users/login` → `access_token` (30 min JWT) + `refresh_token` (30 days opaque token, `secrets.token_hex(48)`)
- Bearer via `OAuth2PasswordBearer(tokenUrl="/api/users/login")`
- Refresh: `POST /api/auth/refresh` with `refresh_token` body param
- Sessions: `UserSession` model with `token_hash` / `refresh_token_hash` (SHA-256), `is_active`, `revoked_at`
- Password hashing: passlib[bcrypt]
- `get_current_user()` dependency: decodes JWT, verifies active session, touches `last_used_at`, returns `User`

## Rate Limiting

- `RateLimitMiddleware` in `main.py`: 100 req/60s per IP
- Backed by SQLite (`rate_limits.db`) via `RateLimiter` class in `rate_limiter.py`
- WAL mode, thread-safe via `threading.local()`
- Skipped when `TESTING=true`

## Database

- **Dev**: SQLite (`sqlite:///./clakettes.db`), `check_same_thread=False`, `StaticPool`
- **Prod**: MariaDB via `DATABASE_URL` env var, `pool_size=10`, `max_overflow=20`, `pool_pre_ping=True`, `pool_recycle=3600`
- Session: `get_db()` FastAPI dependency — yields session, rolls back on exception, always closes
- Settings in `config.py` via `pydantic-settings` from `.env` file

## Tests & Lint

- `pytest tests/ -x -q --tb=short` — stop on first failure, quiet, short traceback
- `asyncio_mode = auto` in `pytest.ini` — no async markers needed
- Uses `httpx` for async HTTP testing
- Test env: set `TESTING=true` to bypass rate limiter
- Lint: `ruff check .` from `backend/` — line-length 120 (`pyproject.toml: [tool.ruff] line-length = 120`), rules E, F, W

## Migrations

- `alembic upgrade head` from `backend/`
- Config in `alembic.ini`: default `sqlite:///./clakettes.db`, override via `DATABASE_URL` env
