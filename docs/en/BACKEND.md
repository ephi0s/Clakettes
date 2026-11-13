# Clakettes Backend — Technical Documentation

[ES](../es/BACKEND.md) · [EN](BACKEND.md) · [FR](../fr/BACKEND.md) · [DE](../de/BACKEND.md) · [IT](../it/BACKEND.md) · [CA](../ca/BACKEND.md) · [EU](../eu/BACKEND.md) · [GL](../gl/BACKEND.md) · [OC](../oc/BACKEND.md)

FastAPI backend for the Clakettes film festival management platform.

## Quick start

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Architecture

### Layer structure

```
Routers (FastAPI) → Services (Business Logic) → Models (SQLAlchemy)
```

| Layer | Location | Responsibility |
|-------|----------|----------------|
| **Routers** | `app/routers/` | HTTP endpoints, request/response validation, pagination |
| **Services** | `app/services/` | Business logic, CRUD operations, cross-cutting concerns |
| **Models** | `app/models/` | SQLAlchemy ORM models, DB schema |
| **Schemas** | `app/schemas/` | Pydantic models for request/response |
| **Auth** | `app/auth.py` | JWT, sessions, password hashing |
| **Config** | `app/config.py` | Pydantic Settings from `.env` |
| **Database** | `app/database.py` | Engine, session factory, `get_db()` dependency |

### Key design principles

1. **Light routers** — delegate to services
2. **Stateless services** — receive `db: Session` via dependency injection
3. **Models inherit `BaseModel`** — `id`, `created_at`, `updated_at` on all entities
4. **Centralized enums** — `app/enums.py` shared between models and schemas
5. **Generic base CRUD** — `BaseService` in `app/services/base_service.py`

---

## Configuration

All configuration is done via `backend/.env` (loaded by `pydantic-settings`):

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./clakettes.db` | SQLAlchemy connection string |
| `SECRET_KEY` | (required, no default) | JWT signing key |
| `JWT_ISSUER` | `clakettes` | JWT issuer claim |
| `JWT_AUDIENCE` | `clakettes-api` | JWT audience claim |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token TTL |
| `CORS_ORIGINS` | `None` (→ `["*"]`) | Comma-separated allowed origins |
| `PORT_BACKEND` | `8000` | Server port (used by Docker/start scripts) |

**Example `.env` for production:**

```env
DATABASE_URL=mariadb+pymysql://user:pass@db:3306/clakettes_db
SECRET_KEY=super-secret-64-char-urlsafe-string
JWT_ISSUER=clakettes
JWT_AUDIENCE=clakettes-api
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=https://app.example.com,https://admin.example.com
```

Generate a robust `SECRET_KEY`:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

---

## Database

### Dual database compatibility

| Environment | Database | Connection String |
|-------------|----------|-------------------|
| Development | SQLite | `sqlite:///./data/clakettes.db` |
| Production | MariaDB | `mariadb+pymysql://user:pass@host:3306/db` |

### Base model

All models inherit from `BaseModel` (`app/models/base.py`):

```python
class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

### Migrations (Alembic)

```bash
cd backend

# Create new migration after model changes
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1

# Current revision
alembic current
```

**Migration notes (SQLite ↔ MariaDB):**
- SQLite `INTEGER PRIMARY KEY` → MariaDB `INT AUTO_INCREMENT`
- SQLite `TEXT` → MariaDB `TEXT`/`VARCHAR`
- SQLite `DATETIME` (stored as TEXT) → MariaDB native `DATETIME`
- The export/import scripts in `backend/tools/` handle type conversions automatically

See [DATABASE.md](DATABASE.md) for the complete schema documentation with ER diagrams.

---

## Authentication

### JWT + Session tracking

| Token Type | Format | TTL | Storage |
|------------|--------|-----|---------|
| **Access Token** | JWT (HS256) | 30 min (configurable) | Client memory |
| **Refresh Token** | Opaque (SHA-256 hash in DB) | 30 days | `UserSession.refresh_token_hash` |

### Login flow

```
POST /api/users/login
  {username, password}
→ 200 {access_token, refresh_token, token_type: "bearer", user: {...}}
```

### Token usage

```http
Authorization: Bearer <access_token>
```

### Refresh flow

```
POST /api/auth/refresh
  {refresh_token}
→ 200 {access_token, refresh_token, token_type: "bearer"}
```

### Session management

- `GET /api/auth/sessions` — List active sessions
- `DELETE /api/auth/sessions/{session_id}` — Revoke session
- Session is created at login with device info (IP, UA, name)
- Tokens are rotated on refresh; old tokens are invalidated

### Password hashing

- **bcrypt** via `passlib` (rounds=12)
- Hash stored in `User.password_hash`
- Verified via `pwd_context.verify(plain, hash)`

### Rate limit

- **100 requests / 60 seconds** per IP (SQLite-backed)
- Applied via `RateLimitMiddleware` in `main.py`
- Disabled when `TESTING=true` environment variable is set

---

## API endpoints

### Router registration (`app/main.py`)

| Router | Prefix | Tags | Description |
|--------|--------|------|-------------|
| `festivals` | `/api/festivals` | festivals | CRUD, search, members |
| `users` | `/api/users` | users | CRUD, profile, avatar upload |
| `auth` | `/api/users` | auth | Login, refresh, register |
| `auth_sessions` | `/api/auth` | auth | Session list/revoke |
| `shortfilms` | `/api/shortfilms` | shortfilms | CRUD, festival linkage |
| `chat` | `/api/chat` | chat | Messages, WS endpoint |
| `user_festival` | `/api/festivals` | user-festival | Join/leave, members |
| `uploads` | `/api/uploads` | uploads | Avatar upload |
| `search` | `/api/search` | search | Global search |
| `admin` | `/api/admin` | admin | Stats, tables, audit-log, reset |
| `notifications` | `/api/notifications` | notifications | CRUD, unread count |
| `roles` | `/api` | roles | Roles, groups, deps, conflicts |
| `participant_tags` | `/api` | participant-tags | Tags, festival config |
| `user_roles` | `/api` | user-roles | Role assignments |
| `user_aliases` | `/api` | user-aliases | Display name aliases |
| `validation_rules` | `/api` | validation-rules | Dynamic form validation |
| `registration_forms` | `/api` | registration-forms | Festival registration flows |
| `role_groups` | `/api` | role-groups | Role grouping |
| `committees` | `/api` | committees | Festival committees |
| `delegations` | `/api` | delegations | Role delegations |
| `events` | `/api` | events | Events, tickets, seats, reservations |
| `channels` | `/api/channels` | channels | Chat channels |
| `keys` | `/api/users` | e2ee | E2EE public key mgmt |
| `locations` | `/api/locations` | locations | Geolocation, maps |
| `location_tags` | `/api/locations/{location_id}/tags` | location-tags | Location tags |
| `location_images` | `/api/locations/{location_id}/images` | location-images | Location images |
| `location_relations` | `/api/locations/{location_id}/relations` | location-relations | Location relations |
| `shortfilm_locations` | `/api/shortfilms/{shortfilm_id}/locations` | shortfilm-locations | Shortfilm locations |
| `form_definitions` | `/api` | forms | Form builder |
| `federation` | `/api/federation` | federation | manifest, directory, nodes, reports, webfinger |
| `jury_votes` | `/api` | jury-votes | Jury voting (phase 5) |
| `calendar` | `/api/calendar` | calendar | Agenda, CalDAV, settings |
| `badges` | `/api` | badges | Badges, assignments, eligibility |
| `posts` | `/api` | posts | Social posts, replies, moderation |
| `payments` | `/api` | payments | Checkout, confirm, refund, webhook |
| `festival_rulebooks` | `/api/festivals/{festival_id}/rulebooks` | rulebooks | Festival rulebooks |
| `user_blocks` | `/api` | user-blocks | User blocking |
| `moderation_reports` | `/api` | moderation-reports | Moderation reports |
| `node_policies` | `/api` | node-policies | Federation node policies |

Total: 38 routers with `APIRouter` (40 router files, 2 helpers without router).

### Pagination and filtering

Standard query parameters on list endpoints:

```
GET /api/festivals/?page=1&size=20&search=cannes&is_active=true
```

Response envelope:

```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "size": 20,
  "pages": 8
}
```

---

## Realtime chat

### Backend WebSocket (`app/chat_backend/`)

| Component | Description |
|-----------|-------------|
| `WebSocketChatBackend` | Default implementation (in-memory connections) |
| `chat_backend_registry` | Singleton registry for backend swapping |
| `ConnectionManager` | Manages user↔WebSocket mappings |

### Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/api/chat/ws` | WebSocket connection (auth via query `token`) |
| `POST` | `/api/chat/messages` | Send message (REST fallback) |
| `GET` | `/api/chat/messages` | Paginated history |
| `PATCH` | `/api/chat/messages/{id}/read` | Mark read |

### Message types

```python
class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    LOCATION = "location"
    VCARD = "vcard"
    ICAL = "ical"
    SYSTEM = "system"
```

### E2EE

- X25519 key exchange via `/api/users/{id}/keys`
- Public keys stored in `UserKey` (one active per user)
- Encryption/decryption in the frontend (`e2ee_service.dart`)

---

## File uploads

### Avatar upload

```
POST /api/uploads/avatar
Content-Type: multipart/form-data
Authorization: Bearer <token>

file: <image/*>
```

- Saved to `backend/uploads/avatars/{user_id}_{uuid}.{ext}`
- Served statically at `/uploads/avatars/...`
- Max size: 10 MB (applied by `RequestSizeLimitMiddleware`)

---

## Admin endpoints

Requires `role=admin` (checked in `admin_service.py`):

| Endpoint | Description |
|----------|-------------|
| `GET /api/admin/stats` | Platform statistics |
| `GET /api/admin/tables` | Row counts per table |
| `GET /api/admin/audit-log` | Audit trail (filters `action`, `actor_user_id`) |
| `POST /api/admin/reset` | `drop_all + create_all` (non-prod only) |

---

## Tests

```bash
cd backend

# Run all tests
python -m pytest tests/ -x -q --tb=short

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=term-missing

# Specific test file
python -m pytest tests/test_festivals.py -v
```

**Test configuration** (`pyproject.toml` / `pytest.ini`):

```ini
[tool.pytest.ini_options]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_functions = test_*
```

**Fixtures** (`tests/conftest.py`):
- `db_session` — in-memory SQLite session
- `client` — `AsyncClient` (httpx) against the test app
- `auth_headers` — pre-authenticated headers

---

## Lint and formatting

```bash
# Check
ruff check .

# Fix auto-fixable
ruff check . --fix

# Format
ruff format .
```

**Configuration** (`pyproject.toml`):

```toml
[tool.ruff]
line-length = 120
target-version = "py312"
select = ["E", "F", "I", "UP", "B", "C4", "PTH", "T20", "SIM", "ARG"]
ignore = ["E501", "SIM102", "SIM103"]
```

---

## Development workflow

### Local development

```bash
# Terminal 1: Backend
cd backend
python -m uvicorn app.main:app --reload

# Terminal 2: Frontend (if needed)
cd frontend
flutter run -d web-server --web-port 3000 --dart-define=BACKEND_URL=http://localhost:8000/api
```

### Development with Docker

```bash
# From project root
docker compose up        # Backend:8000, Frontend:3000
docker compose --profile db up  # + MariaDB:3306
```

### Initial database load

No seed script: in development the app creates the initial admin (`admin` /
`setup`, change the password on first login) and tables via `create_all`. In production
data arrives via the API and the schema only via Alembic.

### Common commands

```bash
# Generate Hive adapters (frontend)
cd frontend && flutter pub run build_runner build --delete-conflicting-outputs

# Run migrations
cd backend && alembic upgrade head

# Create migration
cd backend && alembic revision --autogenerate -m "add column x"

# Export SQLite → MariaDB
cd backend && python tools/export_sqlite_to_mariadb.py

# Import MariaDB → SQLite
cd backend && python tools/import_mariadb_to_sqlite.py
```

---

## Project structure

```
backend/
├── app/
│   ├── models/              # 40 SQLAlchemy models (+ base.py)
│   ├── schemas/             # 37 Pydantic schemas
│   ├── services/            # 43 business logic services
│   ├── routers/             # 40 API routers (38 con APIRouter)
│   ├── chat_backend/        # WebSocket chat implementation
│   ├── auth.py              # JWT + session auth
│   ├── config.py            # Pydantic Settings
│   ├── database.py          # Engine, SessionLocal, get_db()
│   ├── main.py              # FastAPI app, middleware, routers
│   ├── rate_limiter.py      # SQLite rate limiter
│   ├── enums.py             # Shared enums
│   └── scripts/             # Seed/migration scripts
├── alembic/                 # Migrations (36 versions)
├── tools/                   # Export/import scripts
├── tests/                   # pytest tests (47 files, 1439 test functions)
├── uploads/                 # Static file uploads
├── .env.example             # Config template
├── requirements.txt         # Production deps
├── requirements-dev.txt     # Dev deps (pytest, ruff)
├── pyproject.toml           # Ruff, pytest config
└── pytest.ini               # Pytest config
```

Docs in `docs/en/BACKEND.md` (this file) and `docs/en/DATABASE.md`.

---

## Deployment

### Docker (Production)

```yaml
# docker-compose.yml uses --profile prod
docker compose --profile prod up -d
```

Services:
- `backend-prod` — FastAPI (Uvicorn workers) on :8000
- `frontend-prod` — Nginx + Flutter web on :80
- `db` — MariaDB 11 (health check)

Available profiles:
- `dev` (default): backend and frontend dev servers
- `db`: adds the MariaDB container
- `prod`: production stack with nginx

### Production environment variables

```env
DATABASE_URL=mariadb+pymysql://user:pass@db:3306/clakettes_db
SECRET_KEY=<64-char-urlsafe>
CORS_ORIGINS=https://app.example.com
```

### Health check

```bash
curl http://localhost:8000/health
# {"status": "healthy"}
```

---

## Security checklist

- [ ] Change `SECRET_KEY` in production
- [ ] Set `CORS_ORIGINS` to specific domains
- [ ] Use MariaDB (not SQLite) in production
- [ ] Enable HTTPS (reverse proxy: nginx/Traefik)
- [ ] Configure allowed hosts in `TrustedHostMiddleware`
- [ ] Rotate JWT keys periodically
- [ ] Monitor rate limiter logs
- [ ] Review admin user password after first login

---

## Extending the API

### Add a new resource

1. **Model** — `app/models/new_resource.py` (inherits `BaseModel`)
2. **Schema** — `app/schemas/new_resource.py` (Pydantic)
3. **Service** — `app/services/new_resource_service.py` (extends `BaseService`)
4. **Router** — `app/routers/new_resource.py` (include in `main.py`)
5. **Migration** — `alembic revision --autogenerate -m "add new_resource"`
6. **Tests** — `tests/test_new_resource.py`

### Add a custom endpoint to an existing router

```python
# In router file
@router.post("/{festival_id}/custom-action", response_model=CustomResponse)
async def custom_action(
    festival_id: int,
    payload: CustomRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.custom_action(db, festival_id, payload, current_user)
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: app` | Run from `backend/` dir or `PYTHONPATH=backend` |
| `sqlite3.OperationalError: database is locked` | Single writer; ensure no stale processes |
| `alembic: Can't locate revision` | Delete `alembic/versions/`, run `alembic revision --autogenerate -m "init"` |
| `JWTError: Signature verification failed` | `SECRET_KEY` mismatch between env and running process |
| `429 Too Many Requests` | Rate limit hit; wait 60s or set `TESTING=true` |
| WebSocket 403 | Token expired; use valid access token in `?token=` query |
| CORS error | Check `CORS_ORIGINS` in `.env` matches frontend origin |

---

## References

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [Pydantic v2](https://docs.pydantic.dev/latest/)
- [Alembic](https://alembic.sqlalchemy.org/)
- [python-jose](https://github.com/mpdavis/python-jose)
- [passlib](https://passlib.readthedocs.io/)