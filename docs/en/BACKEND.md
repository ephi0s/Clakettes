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
| `APP_ENV` | `development` | `production` requires a strong `SECRET_KEY`, explicit CORS and schema via Alembic |
| `TESTING` | disabled | `1/true/yes/on` disables rate limits and auto-migration (`app.config.is_testing()`) |
| `PUBLIC_BASE_URL` | `None` | Public origin of the node (manifest, bundles, absolute ICS) |
| `MTLS_REQUIRED` | `False` | Requires verified mTLS on `/api/federation` |
| `MTLS_CA_BUNDLE_PATH` | `None` | Root CA to validate client certificates |
| `MTLS_CLIENT_CERT_PATH`, `MTLS_CLIENT_KEY_PATH` | `None` | Own certificate and key (RSA-SHA256 manifest signing) |
| `RATE_LIMITS_DB_PATH` | `backend/rate_limits.db` | SQLite file backing the rate limiter |
| `SKIP_AUTO_MIGRATE` | disabled | `1/true/yes/on` skips `alembic upgrade head` on startup |
| `PAYMENTS_PROVIDER`, `MOCK_WEBHOOK_SECRET`, `MOCK_PAYMENTS_FORCE_FAIL` | `mock`, empty, `False` | Mock payment provider and webhook secret |
| `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` | empty | Stripe credentials (lazy SDK) |
| `REDSYS_MERCHANT_CODE`, `REDSYS_TERMINAL`, `REDSYS_SECRET_KEY`, `REDSYS_SANDBOX`, `REDSYS_CURRENCY` | —, `1`, empty, `True`, `978` | Redsys HMAC signing and sandbox |
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

- **bcrypt** direct (`bcrypt.hashpw` + `bcrypt.gensalt()`), without `passlib`
- Hash stored in `User.password_hash`
- Verified via `bcrypt.checkpw(plain, hash)` (`app/services/user_service.py`)

### Rate limit

- **100 requests / 60 seconds** per IP (SQLite-backed)
- Applied via `RateLimitMiddleware` in `main.py`
- Disabled with `TESTING` ∈ {1, true, yes, on} (helper `app.config.is_testing()`), including the 20/60 s refresh limiter in `routers/auth_sessions.py`

---

## API endpoints

### Router registration (`app/main.py`)

| Router | Prefix | Tags | Description |
|--------|--------|------|-------------|
| `festivals` | `/api/festivals` | festivals | CRUD, search, members |
| `users` | `/api/users` | users | CRUD, profile, avatar upload |
| `auth` | `/api/users` | auth | Login, refresh, register |
| `auth_sessions` | `/api/auth` | auth | Session list/revoke |
| `shortfilms` | `/api/shortfilms` | shortfilms | CRUD nested under `/api/festivals/{festival_id}/shortfilms` (list GET/POST and detail GET/PUT/DELETE, `?contest_type=` filter); the flat endpoints remain available but are marked `deprecated=True` |
| `chat` | `/api/chat` | chat | Messages, WS endpoint |
| `user_festival` | `/api/festivals` | user-festival | Join/leave, members |
| `uploads` | `/api/uploads` | uploads | Multipart upload of avatar, thumbnail, video, document and chat image; returns relative paths `/uploads/...` |
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
| `federation` | `/api/federation` | federation | manifest, directory, nodes, reports, webfinger, `whoami`, JWKS, peers/verify, mTLS |
| `federation_chat_bridge` | `/api/federation/chat` | federation-chat-bridge | RS256-signed chat bridge, config and messages |
| `federation_events` | `/api/federation/events` | federation-events | SSE with mandatory `token`, publish and retry |
| `federation_portability` | `/api/federation/portability` | federation-portability | Bundles, imports, migration and redirects |
| `federation_resilience` | `/api/federation/resilience` | federation-resilience | Health, heartbeat, metrics, revocation and incident |
| `chat_moderation` | `/api/chat/moderation` | chat-moderation | Reports, mutes, moderation and limits |
| `jury_votes` | `/api` | jury-votes | Jury voting (phase 5) |
| `calendar` | `/api/calendar` | calendar | Agenda, CalDAV, settings |
| `badges` | `/api` | badges | Badges, assignments, eligibility |
| `posts` | `/api` | posts | Social posts, replies, moderation |
| `payments` | `/api` | payments | Checkout, confirm, refund, webhook |
| `festival_rulebooks` | `/api/festivals/{festival_id}/rulebooks` | rulebooks | Festival rulebooks |
| `user_blocks` | `/api` | user-blocks | User blocking (owner or admin) |



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
| `PUT` | `/api/chat/messages/{message_id}/read` | Mark read |

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

- ECDH P-256 key exchange via `POST /api/users/me/public-key` and `GET /api/users/{user_id}/public-key` (`routers/keys.py`)
- Public keys stored in `UserKey` (one active per user)
- AES-GCM encryption/decryption in the frontend (`services/crypto_utils.dart`)

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
- Max size: 5 MB for images (`MAX_IMAGE_SIZE` in `routers/uploads.py`); the global body limit remains 10 MB

### All uploads

- The `avatar`, `thumbnail`, `video`, `document` and `chat-image` endpoints return a relative path `/uploads/<folder>/<file>`; the client resolves it with `resolveMediaUrl()` against the active node.
- If the content-type is missing or arrives as `application/octet-stream`, `uploads._sniff_content_type()` detects the type by magic bytes (JPEG, PNG, GIF, WebP, PDF and MP4); the 400 error says `Use JPEG, PNG, WebP, GIF, PDF or MP4.`
- `logo_url`, `banner_url`, `video_url` and `thumbnail_url` use the `MediaUrl` type: they accept relative paths (and an empty string) or valid http(s) URLs; an invalid URL returns 422.

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

**Test configuration** (`pyproject.toml`):

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
markers = ["interop: interoperability tests that drive the real caldav client against a live server"]
```

Async tests use `pytest.mark.asyncio`; there is no global `asyncio_mode`.

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

[tool.ruff.lint]
select = ["E", "F", "W"]
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
# {"status": "healthy", "db_revision": "<current revision>"}
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
- [PyJWT](https://github.com/jpadilla/pyjwt)
- [bcrypt](https://github.com/pyca/bcrypt/)