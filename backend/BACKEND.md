# Clakettes Backend — Technical Documentation

FastAPI backend for the Clakettes film festival management platform.

## Quick Start

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

### Layered Structure

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

### Key Design Principles

1. **Routers are thin** — delegate to services
2. **Services are stateless** — receive `db: Session` via dependency injection
3. **Models inherit `BaseModel`** — `id`, `created_at`, `updated_at` on all entities
4. **Enums centralized** — `app/enums.py` shared across models/schemas
5. **Generic CRUD base** — `BaseService` in `app/services/base_service.py`

---

## Configuration

All settings via `backend/.env` (loaded by `pydantic-settings`):

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./clakettes.db` | SQLAlchemy connection string |
| `SECRET_KEY` | `your-secret-key-change-in-production` | JWT signing key |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token TTL |
| `CORS_ORIGINS` | `None` (→ `["*"]`) | Comma-separated allowed origins |
| `PORT_BACKEND` | `8000` | Server port (used by Docker/start scripts) |

**Production `.env` example:**

```env
DATABASE_URL=mariadb+pymysql://user:pass@db:3306/clakettes_db
SECRET_KEY=super-secret-64-char-urlsafe-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=https://app.example.com,https://admin.example.com
```

Generate a strong `SECRET_KEY`:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

---

## Database

### Dual Database Support

| Environment | Database | Connection String |
|-------------|----------|-------------------|
| Development | SQLite | `sqlite:///./data/clakettes.db` |
| Production | MariaDB | `mariadb+pymysql://user:pass@host:3306/db` |

### Base Model

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
- Export/import scripts in `backend/tools/` handle type conversions

### Models Overview (31 models)

| Model | Table | Key Relationships |
|-------|-------|-------------------|
| `Festival` | `festivals` | ShortFilms, Users (M2M), Roles, Events, Awards, Committees, Locations |
| `User` | `users` | ShortFilms, Festivals (M2M), Sessions, Keys, Aliases, Roles, Tags |
| `ShortFilm` | `shortfilms` | Festival (FK), User (FK), Awards, Locations |
| `Message` | `messages` | Sender/Receiver (User), Channel (FK) |
| `UserFestival` | `user_festival` | M2M User↔Festival with role |
| `Award` | `awards` | Festival, Event, ShortFilm, User (recipient/verifier/creator) |
| `Channel` | `channels` | Creator (User), Members, Messages |
| `Committee` | `committees` | Festival, Role, Members |
| `Event` | `events` | Festival, Creator, TicketTypes, Seats, Reservations, Attendees |
| `Notification` | `notifications` | User (recipient), related_user |
| `ParticipantTag` | `participant_tags` | Global tags, festival-specific config |
| `RegistrationForm` | `registration_forms` | Festival, Sections, Links, Registrations |
| `Role` | `roles` | Hierarchy, groups, permissions, festival roles |
| `UserAlias` | `user_aliases` | User, per-context display names |
| `UserKey` | `user_keys` | User (1:1), X25519 public key for E2EE |
| `UserRole` | `user_roles` | User, Role, Festival, status, visibility |
| `UserSession` | `user_sessions` | User, token hashes, device info, expiry |
| `ValidationRule` | `validation_rules` | Field validation rules with groups |
| `FestivalRole` | `festival_roles` | Festival-specific role config |
| `RoleDependency` | `role_dependencies` | Role prerequisites |
| `RoleConflict` | `role_conflicts` | Mutually exclusive roles |
| `RoleGroup` | `role_groups` | Grouping of roles |
| `RoleGroupMembership` | `role_group_memberships` | Role ↔ Group links |
| `RoleDelegation` | `role_delegations` | User-to-user role delegation |
| `RoleTransition` | `role_transitions` | Role change history |
| `UserParticipantTag` | `user_participant_tags` | User ↔ Tag assignments |
| `FestivalParticipantTag` | `festival_participant_tags` | Festival-specific tag config |
| `ValidationRuleGroup` | `validation_rule_groups` | Groups of validation rules |
| `RegistrationFormSection` | `registration_form_sections` | Form sections with roles/tags |
| `RegistrationFormLink` | `registration_form_links` | Public/unique registration links |
| `EventTicketType` | `event_ticket_types` | Event ticket categories |
| `EventSeat` | `event_seats` | Seat map with positions |

See [DATABASE.md](DATABASE.md) for complete schema documentation with ER diagrams.

---

## Authentication

### JWT + Session Tracking

| Token Type | Format | TTL | Storage |
|------------|--------|-----|---------|
| **Access Token** | JWT (HS256) | 30 min (configurable) | Client memory |
| **Refresh Token** | Opaque (SHA-256 hash in DB) | 30 days | `UserSession.refresh_token_hash` |

### Login Flow

```
POST /api/users/login
  {username, password}
→ 200 {access_token, refresh_token, token_type: "bearer", user: {...}}
```

### Token Usage

```http
Authorization: Bearer <access_token>
```

### Refresh Flow

```
POST /api/users/refresh
  {refresh_token}
→ 200 {access_token, refresh_token, token_type: "bearer"}
```

### Session Management

- `GET /api/auth/sessions` — List active sessions
- `DELETE /api/auth/sessions/{session_id}` — Revoke session
- Session created on login with device info (IP, UA, name)
- Tokens rotated on refresh; old tokens invalidated

### Password Hashing

- **bcrypt** via `passlib` (rounds=12)
- Hash stored in `User.password_hash`
- Verified via `pwd_context.verify(plain, hash)`

### Rate Limiting

- **100 requests / 60 seconds** per IP (SQLite-backed)
- Applied via `RateLimitMiddleware` in `main.py`
- Disabled when `TESTING=true` env var set

---

## API Endpoints

### Router Registry (`app/main.py`)

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
| `admin` | `/api/admin` | admin | Stats, seed, activity |
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

Total: 32 routers

### Pagination & Filtering

Standard query params on list endpoints:

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

## Real-time Chat

### WebSocket Backend (`app/chat_backend/`)

| Component | Description |
|-----------|-------------|
| `WebSocketChatBackend` | Default implementation (in-memory connections) |
| `chat_backend_registry` | Singleton registry for backend swapping |
| `ConnectionManager` | Manages user↔WebSocket mappings |

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/chat/ws` | WebSocket connection (auth via query `token`) |
| `POST` | `/api/chat/messages` | Send message (REST fallback) |
| `GET` | `/api/chat/messages` | Paginated history |
| `PATCH` | `/api/chat/messages/{id}/read` | Mark read |

### Message Types

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
- Encryption/decryption in frontend (`e2ee_service.dart`)

---

## File Uploads

### Avatar Upload

```
POST /api/uploads/avatar
Content-Type: multipart/form-data
Authorization: Bearer <token>

file: <image/*>
```

- Saved to `backend/uploads/avatars/{user_id}_{uuid}.{ext}`
- Served statically at `/uploads/avatars/...`
- Max size: 10 MB (enforced by `RequestSizeLimitMiddleware`)

---

## Admin Endpoints

Require `role=admin` (checked in `admin_service.py`):

| Endpoint | Description |
|----------|-------------|
| `GET /api/admin/stats` | Platform statistics |
| `GET /api/admin/activity` | Recent activity feed |
| `POST /api/admin/seed` | Seed development data |
| `GET /api/admin/users` | Paginated user list with filters |

---

## Testing

```bash
cd backend

# Run all tests
python -m pytest tests/ -x -q --tb=short

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=term-missing

# Specific test file
python -m pytest tests/test_festivals.py -v
```

**Test config** (`pyproject.toml` / `pytest.ini`):

```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_functions = test_*
```

**Fixtures** (`tests/conftest.py`):
- `db_session` — SQLite in-memory session
- `client` — `AsyncClient` (httpx) against test app
- `auth_headers` — Pre-authenticated headers

**Note**: There's a duplicate `conftest.py` in `tests/services/` — should be consolidated.

---

## Linting & Formatting

```bash
# Check
ruff check .

# Fix auto-fixable
ruff check . --fix

# Format
ruff format .
```

**Config** (`pyproject.toml`):

```toml
[tool.ruff]
line-length = 120
target-version = "py312"
select = ["E", "F", "I", "UP", "B", "C4", "PTH", "T20", "SIM", "ARG"]
ignore = ["E501", "SIM102", "SIM103"]
```

---

## Development Workflow

### Local Development

```bash
# Terminal 1: Backend
cd backend
python -m uvicorn app.main:app --reload

# Terminal 2: Frontend (if needed)
cd frontend
flutter run -d web-server --web-port 3000 --dart-define=BACKEND_URL=http://localhost:8000/api
```

### Docker Development

```bash
# From project root
docker compose up        # Backend:8000, Frontend:3000
docker compose --profile db up  # + MariaDB:3306
```

### Database Seeding

```bash
cd backend
python -m app.scripts.seed_dev_data
```

Or via API:
```bash
curl -X POST http://localhost:8000/api/admin/seed \
  -H "Authorization: Bearer <admin_token>"
```

### Common Commands

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

## Project Structure

```
backend/
├── app/
│   ├── models/              # 31 SQLAlchemy models
│   ├── schemas/             # 30 Pydantic schemas
│   ├── services/            # 29 business logic services
│   ├── routers/             # 32 API routers
│   ├── chat_backend/        # WebSocket chat implementation
│   ├── auth.py              # JWT + session auth
│   ├── config.py            # Pydantic Settings
│   ├── database.py          # Engine, SessionLocal, get_db()
│   ├── main.py              # FastAPI app, middleware, routers
│   ├── rate_limiter.py      # SQLite rate limiter
│   ├── enums.py             # Shared enums
│   └── scripts/             # Seed/migration scripts
├── alembic/                 # Migrations (9 versions)
├── tools/                   # Export/import scripts
├── tests/                   # pytest tests (17 files)
├── uploads/                 # Static file uploads
├── .env.example             # Config template
├── requirements.txt         # Production deps
├── requirements-dev.txt     # Dev deps (pytest, ruff)
├── DATABASE.md              # Full schema docs
├── BACKEND.md               # This file
├── pyproject.toml           # Ruff, pytest config
└── pytest.ini               # Pytest config
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
- `db` — MariaDB 11 (healthy check)

Profiles available:
- `dev` (default): backend + frontend dev servers
- `db`: adds MariaDB container
- `prod`: production stack with nginx

### Environment Variables (Production)

```env
DATABASE_URL=mariadb+pymysql://user:pass@db:3306/clakettes_db
SECRET_KEY=<64-char-urlsafe>
CORS_ORIGINS=https://app.example.com
```

### Health Check

```bash
curl http://localhost:8000/health
# {"status": "healthy"}
```

---

## Security Checklist

- [ ] Change `SECRET_KEY` in production
- [ ] Set `CORS_ORIGINS` to specific domains
- [ ] Use MariaDB (not SQLite) in production
- [ ] Enable HTTPS (reverse proxy: nginx/Traefik)
- [ ] Set `TrustedHostMiddleware` allowed hosts
- [ ] Rotate JWT keys periodically
- [ ] Monitor rate limiter logs
- [ ] Review admin user password after first login

---

## Extending the API

### Adding a New Resource

1. **Model** — `app/models/new_resource.py` (inherit `BaseModel`)
2. **Schema** — `app/schemas/new_resource.py` (Pydantic)
3. **Service** — `app/services/new_resource_service.py` (extend `BaseService`)
4. **Router** — `app/routers/new_resource.py` (include in `main.py`)
5. **Migration** — `alembic revision --autogenerate -m "add new_resource"`
6. **Tests** — `tests/test_new_resource.py`

### Adding a Custom Endpoint to Existing Router

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