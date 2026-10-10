# Clakettes Backend — Technical Reference

FastAPI + SQLAlchemy backend for the Clakettes film festival management platform.

## Quick Commands

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Development server (auto-reload)
python -m uvicorn app.main:app --reload --port 8000

# Run tests
python -m pytest tests/ -x -q --tb=short

# Lint
ruff check .

# Migrations
alembic upgrade head
alembic revision --autogenerate -m "description"

# Export SQLite → MariaDB
python export_sqlite_to_mariadb.py

# Import MariaDB → SQLite
python import_mariadb_to_sqlite.py
```

---

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, lifespan, middleware, routers
│   ├── config.py            # Pydantic Settings (.env)
│   ├── database.py          # Engine, SessionLocal, get_db()
│   ├── auth.py              # JWT, sessions, password hashing
│   ├── rate_limiter.py      # SQLite-backed rate limiting
│   ├── enums.py             # Shared enums (RoleScope, UserRoleStatus, etc.)
│   ├── models/              # 34 SQLAlchemy models
│   │   ├── __init__.py      # Exports all models
│   │   ├── base.py          # BaseModel (id, created_at, updated_at)
│   │   ├── user.py, festival.py, shortfilm.py, message.py
│   │   ├── user_festival.py, award.py, channel.py, committee.py
│   │   ├── event.py, event_screening.py, notification.py
│   │   ├── participant_tag.py, registration.py (incl. RegistrationForm)
│   │   ├── role.py, role_group.py, role_delegation.py, role_transition.py
│   │   ├── user_alias.py, user_key.py, user_role.py, user_session.py
│   │   ├── validation_rule.py, payment.py, group.py
│   │   ├── location.py, location_tag.py, location_image.py
│   │   ├── location_relation.py, festival_location.py
│   │   ├── shortfilm_location.py, festival_rulebook.py, app_setting.py
│   │   └── form_definition.py
│   ├── schemas/             # 32 Pydantic schemas
│   │   ├── __init__.py
│   │   ├── common.py        # Pagination, MessageResponse
│   │   ├── festival.py
│   │   ├── user.py
│   │   ├── shortfilm.py
│   │   ├── chat.py
│   │   ├── auth.py
│   │   ├── user_session.py
│   │   ├── user_role.py
│   │   ├── user_key.py
│   │   ├── user_alias.py
│   │   ├── validation_rule.py
│   │   ├── registration.py
│   │   ├── role.py
│   │   ├── role_group.py
│   │   ├── role_delegation.py
│   │   ├── participant_tag.py
│   │   ├── notification.py
│   │   ├── message.py
│   │   ├── location.py
│   │   ├── group.py
│   │   ├── form_definition.py
│   │   ├── committee.py
│   │   ├── channel.py
│   │   ├── award.py
│   │   ├── event.py
│   │   └── role_transition.py
│   ├── services/            # 33 business logic services
│   │   ├── __init__.py
│   │   ├── base_service.py  # Generic CRUD + paginate (clamp size≤100) + paginate_filtered
│   │   ├── user_service.py, festival_service.py, shortfilm_service.py
│   │   ├── message_service.py, auth_session_service.py, admin_service.py
│   │   ├── award_service.py, channel_service.py, group_service.py
│   │   │   # (committees, delegations, transitions)
│   │   ├── event_service.py, export_service.py (reportlab con import perezoso)
│   │   ├── form_service.py, location_service.py (+ location_tag/image/relation)
│   │   ├── festival_location_service.py, festival_rulebook_service.py
│   │   ├── shortfilm_location_service.py, notification_service.py
│   │   ├── participant_tag_service.py, registration_service.py
│   │   ├── role_service.py, search_service.py, payment_service.py
│   │   ├── user_alias_service.py, user_festival_service.py
│   │   ├── user_key_service.py, validation_rule_service.py
│   │   ├── calendar_service.py, dav_service.py, app_setting_service.py
│   │   ├── user_role_service.py
│   │   └── validation_rule_service.py
│   ├── routers/             # 23 API routers
│   │   ├── __init__.py
│   │   ├── festivals.py
│   │   ├── users.py
│   │   ├── shortfilms.py
│   │   ├── chat.py
│   │   ├── auth.py
│   │   ├── auth_sessions.py
│   │   ├── user_festival.py
│   │   ├── uploads.py
│   │   ├── search.py
│   │   ├── admin.py
│   │   ├── notifications.py
│   │   ├── roles.py
│   │   ├── events.py
│   │   ├── channels.py
│   │   ├── keys.py
│   │   ├── participant_tags.py
│   │   ├── user_roles.py
│   │   ├── user_aliases.py
│   │   ├── validation_rules.py
│   │   ├── registration_forms.py
│   │   ├── role_groups.py
│   │   ├── committees.py
│   │   ├── delegations.py
│   │   ├── locations.py
│   │   └── form_definitions.py
│   └── chat_backend/        # Real-time chat (WebSocket + REST)
│       ├── __init__.py
│       ├── base.py
│       ├── registry.py
│       └── websocket_backend.py
├── alembic/                 # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── tools/                   # Utility scripts
│   ├── export_sqlite_to_mariadb.py
│   └── import_mariadb_to_sqlite.py
├── tests/                   # pytest tests
├── uploads/avatars/         # Static file uploads
├── .env.example
├── requirements.txt
├── requirements-dev.txt
├── DATABASE.md              # Full schema documentation
└── README.md                # This file
```

---

## Core Concepts

### BaseModel

All models inherit from `app.models.base.BaseModel`:

```python
class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

### BaseService

Generic CRUD service in `app.services.base_service.BaseService`:

```python
class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: int) -> Optional[ModelType]
    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[ModelType]
    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType
    def update(self, db: Session, *, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType
    def remove(self, db: Session, *, id: int) -> ModelType
```

Services extend this and add domain-specific methods.

### Enums (`app/enums.py`)

Centralized enums shared by models, schemas, and services:

```python
class RoleScope(str, Enum):
    GLOBAL = "global"
    FESTIVAL = "festival"

class UserRoleStatus(str, Enum):
    ACTIVE = "active"
    PENDING = "pending"
    REVOKED = "revoked"
    EXPIRED = "expired"

class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    VCARD = "vcard"
    ICAL = "ical"
    LOCATION = "location"
    SYSTEM = "system"
```

---

## Authentication & Authorization

### Token Flow

```
POST /api/users/login
  {username, password}
→ 200 {access_token, refresh_token, token_type: "bearer", user: {...}}

Authorization: Bearer <access_token>  (on all protected endpoints)
```

### Token Details

| Token | Type | TTL | Storage |
|-------|------|-----|---------|
| Access | JWT (HS256) | 30 min (config) | Client memory |
| Refresh | Opaque (SHA-256 hash in DB) | 30 days | `UserSession.refresh_token_hash` |

### Session Model (`UserSession`)

```python
user_id: int
token_hash: str           # SHA-256 of access token
refresh_token_hash: str   # SHA-256 of refresh token
device_name: str
ip_address: str
user_agent: str
last_used_at: datetime
expires_at: datetime      # 30 days from creation
revoked_at: datetime | None
is_active: bool
```

### Protected Dependency

```python
# app/auth.py
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    # 1. Decode JWT
    # 2. Verify session exists, active, not revoked
    # 3. Load User from DB
    # 4. Return User or raise 401
```

### Role-Based Access

- User has global `role` field: `admin`, `organizer`, `user`, `jury`
- Per-festival roles via `UserRole` (M2M User↔Festival↔Role)
- Permissions encoded in `Role.permissions` (JSON)
- Check in services/routers: `user.role == "admin"` or `user_role_service.has_permission(...)`

---

## Database

### SQLite (Dev) / MariaDB (Prod)

| Setting | Dev | Prod |
|---------|-----|------|
| `DATABASE_URL` | `sqlite:///./data/clakettes.db` | `mariadb+pymysql://user:pass@host:3306/db` |
| Driver | `sqlite3` (stdlib) | `PyMySQL` |
| Migrations | Alembic | Alembic |

### Migration Workflow

```bash
# After model changes
cd backend
alembic revision --autogenerate -m "add field to user"

# Apply
alembic upgrade head

# Check current
alembic current

# Rollback
alembic downgrade -1
```

### SQLite ↔ MariaDB Sync

```bash
# Dev → Prod (one-time or periodic)
python export_sqlite_to_mariadb.py

# Prod → Dev (for local debugging)
python import_mariadb_to_sqlite.py
```

Handles type conversions:
- `INTEGER PRIMARY KEY` → `INT AUTO_INCREMENT`
- `TEXT` → `TEXT`/`VARCHAR`
- `DATETIME` (TEXT) → `DATETIME`

See `DATABASE.md` for full schema.

---

## API Reference

### Pagination

All list endpoints support:

```
GET /api/festivals/?page=1&size=20
```

Response:

```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "size": 20,
  "pages": 8
}
```

### Filtering

Common filters (varies by endpoint):

```
GET /api/festivals/?is_active=true&search=madrid
GET /api/users/?role=organizer&festival_id=5
GET /api/shortfilms/?festival_id=3&is_public=true
```

### Error Format

```json
{
  "detail": "Human-readable error message"
}
```

Validation errors (422):

```json
{
  "detail": [
    {"loc": ["body", "email"], "msg": "value is not a valid email address", "type": "value_error.email"}
  ]
}
```

---

### Auth Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/users/login` | Login, returns access + refresh tokens |
| POST | `/api/users/refresh` | Refresh access token |
| POST | `/api/users/register` | Register new user |
| GET | `/api/users/me` | Current user profile |
| PATCH | `/api/users/me` | Update profile |
| POST | `/api/users/me/avatar` | Upload avatar |
| GET | `/api/auth/sessions` | List active sessions |
| DELETE | `/api/auth/sessions/{id}` | Revoke session |

### Festivals

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/festivals/` | List (paginated, filterable) |
| POST | `/api/festivals/` | Create (organizer/admin) |
| GET | `/api/festivals/{id}` | Get by ID |
| PATCH | `/api/festivals/{id}` | Update |
| DELETE | `/api/festivals/{id}` | Delete |
| GET | `/api/festivals/{id}/members` | Festival members |
| POST | `/api/festivals/{id}/join` | Join festival |
| DELETE | `/api/festivals/{id}/leave` | Leave festival |

### Users

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/users/` | List users |
| POST | `/api/users/` | Create user (admin) |
| GET | `/api/users/{id}` | Get user |
| PATCH | `/api/users/{id}` | Update user |
| DELETE | `/api/users/{id}` | Delete user |
| GET | `/api/users/{id}/festivals` | User's festivals |
| GET | `/api/users/{id}/shortfilms` | User's short films |

### Short Films

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/shortfilms/` | List |
| POST | `/api/shortfilms/` | Submit film |
| GET | `/api/shortfilms/{id}` | Get film |
| PATCH | `/api/shortfilms/{id}` | Update |
| DELETE | `/api/shortfilms/{id}` | Delete |
| POST | `/api/shortfilms/{id}/submit` | Submit to festival |

### Chat

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/chat/messages` | List messages (paginated) |
| POST | `/api/chat/messages` | Send message |
| PATCH | `/api/chat/messages/{id}/read` | Mark as read |
| WS | `/ws/chat` | WebSocket connection |

### Events

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/events/` | List events |
| POST | `/api/events/` | Create event |
| GET | `/api/events/{id}` | Get event |
| GET | `/api/events/{id}/tickets` | Ticket types |
| POST | `/api/events/{id}/tickets` | Create ticket type |
| GET | `/api/events/{id}/seats` | Seat map |
| POST | `/api/events/{id}/reservations` | Create reservation |
| GET | `/api/events/{id}/attendees` | Attendees |

### Search

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/search/` | Global search (festivals, users, films) |

Query: `?q=madrid&type=festivals&page=1&size=20`

### Admin

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/admin/stats` | Platform statistics |
| GET | `/api/admin/activity` | Recent activity |
| POST | `/api/admin/seed` | Seed development data |

### WebSocket Chat

```
WS /ws/chat?token=<access_token>

Client → Server:
  {"type": "send", "content": "Hello", "receiver_id": 5}
  {"type": "send_group", "group_id": "festival_3", "content": "Hi all"}

Server → Client:
  {"type": "message", "id": 123, "sender_id": 5, "content": "Hello", ...}
  {"type": "read_receipt", "message_id": 123, "reader_id": 5}
  {"type": "user_status", "user_id": 5, "status": "online"}
```

---

## Services Reference

### UserService (`user_service.py`)

```python
service = UserService()
user = service.get(db, user_id)
user = service.get_by_email(db, email)
user = service.get_by_username(db, username)
user = service.create(db, obj_in=UserCreate(...))
user = service.update(db, db_obj=user, obj_in=UserUpdate(...))
service.authenticate(db, username, password)  # Returns User or None
service.change_password(db, user, new_password)
```

### FestivalService (`festival_service.py`)

```python
service = FestivalService()
festival = service.get_with_relations(db, festival_id)  # Eager loads members, events
festivals = service.get_user_festivals(db, user_id)
service.join_festival(db, festival_id, user_id, role="participant")
service.leave_festival(db, festival_id, user_id)
```

### ShortFilmService (`shortfilm_service.py`)

```python
service = ShortFilmService()
film = service.submit_to_festival(db, film_id, festival_id, user_id)
films = service.get_festival_films(db, festival_id, status="approved")
```

### MessageService (`message_service.py`)

```python
service = MessageService()
messages = service.get_conversation(db, user1_id, user2_id, limit=50)
messages = service.get_group_messages(db, group_id, limit=50)
service.mark_as_read(db, message_ids, user_id)
```

### AuthSessionService (`auth_session_service.py`)

```python
service = AuthSessionService()
sessions = service.get_user_sessions(db, user_id)
service.revoke_session(db, session_id, user_id)
service.revoke_all_sessions(db, user_id, except_session_id=None)
```

### Sync & Offline (Frontend-related)

Backend supports offline-first via:
- `last_synced_at` on models where applicable
- ETags / `If-None-Match` on list endpoints
- Bulk create/update endpoints for sync replay

---

## Real-time Chat Backend

### Architecture

```
app/chat_backend/
├── base.py              # Abstract ChatBackend interface
├── registry.py          # Global registry (single backend instance)
└── websocket_backend.py # WebSocket implementation
```

### WebSocketBackend

- Manages connections: `Dict[user_id, Set[WebSocket]]`
- Handles: private messages, group/channel messages, presence
- Integrates with REST API for persistence
- E2EE: relays encrypted payloads; keys managed via `/api/users/{id}/keys`

### Registration in `main.py`

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    chat_backend = WebSocketChatBackend()
    chat_backend_registry.register(chat_backend)
    await chat_backend.start()
    yield
    await chat_backend.stop()
```

### Router Integration

`chat.router` uses `chat_backend_registry.get()` to access backend for:
- Broadcasting new messages after REST create
- Presence updates
- Group membership changes

---

## Rate Limiting

### Middleware: `RateLimitMiddleware`

- **Limit**: 100 requests / 60 seconds per IP
- **Storage**: SQLite database (`rate_limits.db`)
- **Key**: `middleware:{ip}`
- **Disabled** when `TESTING=true` env var set

### Custom Limits

Apply per-route via dependency:

```python
from app.rate_limiter import RateLimiter

limiter = RateLimiter(max_requests=10, window_seconds=60)

@router.post("/sensitive")
async def sensitive_endpoint(
    request: Request,
    _: None = Depends(limiter.limit("sensitive:{ip}")),
):
    ...
```

---

## File Uploads

### Avatar Upload

```
POST /api/uploads/avatar
Content-Type: multipart/form-data

Form field: file (image/*)
Max size: 10 MB (enforced by RequestSizeLimitMiddleware)
```

Saves to `uploads/avatars/{user_id}_{uuid}.{ext}`, returns URL.

### Static Files

```
GET /uploads/avatars/{filename}
```

Mounted via `StaticFiles` in `main.py`.

---

## CORS Configuration

```python
# app/config.py
cors_origins_list = ["*"]  # or parsed from CORS_ORIGINS env
```

Set in `.env`:

```env
CORS_ORIGINS=https://app.example.com,https://admin.example.com
```

---

## Testing

### Run All Tests

```bash
cd backend
python -m pytest tests/ -x -q --tb=short
```

### Test Structure

```
tests/
├── conftest.py          # Fixtures: db, client, auth headers
├── test_auth.py         # Login, refresh, sessions
├── test_users.py        # CRUD, roles, profile
├── test_festivals.py    # CRUD, join/leave, members
├── test_shortfilms.py   # Submit, approve, list
├── test_chat.py         # Messages, WS
├── test_events.py       # Events, tickets, seats
└── test_admin.py        # Stats, seed
```

### Key Fixtures (`conftest.py`)

```python
@pytest.fixture
def db() -> Generator[Session, None, None]:
    """Override get_db with test SQLite in memory."""
    ...

@pytest.fixture
def client(db: Session) -> TestClient:
    """FastAPI TestClient with db override."""
    ...

@pytest.fixture
def auth_headers(client: TestClient) -> dict:
    """Login as test user, return {'Authorization': 'Bearer ...'}."""
    ...
```

### Async Tests

```python
@pytest.mark.asyncio
async def test_websocket_chat():
    async with client.websocket_connect("/ws/chat?token=...") as ws:
        await ws.send_json({"type": "send", "content": "hi", "receiver_id": 2})
        msg = await ws.receive_json()
        assert msg["type"] == "message"
```

---

## Deployment

### Docker (Production)

```yaml
# docker-compose.yml (prod profile)
services:
  backend-prod:
    build:
      context: ./backend
      target: prod
    environment:
      - DATABASE_URL=mariadb+pymysql://user:pass@db:3306/clakettes
      - SECRET_KEY=${SECRET_KEY}
      - CORS_ORIGINS=https://app.example.com
    depends_on:
      db:
        condition: service_healthy
```

### Build Image

```bash
docker compose build backend-prod
```

### Manual (Non-Docker)

```bash
# On server
cd /opt/clakettes/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Edit with production values
alembic upgrade head
# Run with process manager (systemd, supervisor, PM2)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Systemd Service Example

```ini
# /etc/systemd/system/clakettes-backend.service
[Unit]
Description=Clakettes Backend
After=network.target mariadb.service

[Service]
Type=exec
User=clakettes
WorkingDirectory=/opt/clakettes/backend
EnvironmentFile=/opt/clakettes/backend/.env
ExecStart=/opt/clakettes/backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | No | `sqlite:///./clakettes.db` | SQLAlchemy connection string |
| `SECRET_KEY` | **Yes** | `your-secret-key...` | JWT signing key |
| `ALGORITHM` | No | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `30` | Access token TTL |
| `CORS_ORIGINS` | No | `*` | Comma-separated allowed origins |
| `PORT_BACKEND` | No | `8000` | Server port (Docker/start scripts) |

---

## Adding New Features

### 1. Model

```python
# app/models/new_feature.py
from app.models.base import BaseModel
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

class NewFeature(BaseModel):
    __tablename__ = "new_features"
    name = Column(String(100), nullable=False)
    festival_id = Column(Integer, ForeignKey("festivals.id"))
    festival = relationship("Festival", back_populates="new_features")
```

Add to `app/models/__init__.py`.

### 2. Schema

```python
# app/schemas/new_feature.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NewFeatureBase(BaseModel):
    name: str

class NewFeatureCreate(NewFeatureBase):
    festival_id: int

class NewFeatureUpdate(NewFeatureBase):
    name: Optional[str] = None

class NewFeatureResponse(NewFeatureBase):
    id: int
    festival_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

### 3. Service

```python
# app/services/new_feature_service.py
from app.services.base_service import BaseService
from app.models.new_feature import NewFeature
from app.schemas.new_feature import NewFeatureCreate, NewFeatureUpdate

class NewFeatureService(BaseService[NewFeature, NewFeatureCreate, NewFeatureUpdate]):
    def __init__(self):
        super().__init__(NewFeature)

    def get_by_festival(self, db: Session, festival_id: int):
        return db.query(NewFeature).filter(NewFeature.festival_id == festival_id).all()
```

### 4. Router

```python
# app/routers/new_features.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.new_feature_service import NewFeatureService
from app.schemas.new_feature import NewFeatureCreate, NewFeatureUpdate, NewFeatureResponse

router = APIRouter(prefix="/api/new-features", tags=["new-features"])
service = NewFeatureService()

@router.get("/", response_model=List[NewFeatureResponse])
def list_features(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    return service.get_multi(db, skip=skip, limit=limit)

@router.post("/", response_model=NewFeatureResponse)
def create_feature(data: NewFeatureCreate, db: Session = Depends(get_db)):
    return service.create(db, obj_in=data)

# ...
```

### 5. Register Router

```python
# app/main.py
from app.routers import new_features
app.include_router(new_features.router, prefix="/api/new-features", tags=["new-features"])
```

### 6. Migration

```bash
alembic revision --autogenerate -m "add new_features table"
alembic upgrade head
```

---

## Common Patterns

### Dependency Injection

```python
# Router
def get_festival_service() -> FestivalService:
    return FestivalService()

@router.get("/{id}")
def get_festival(
    id: int,
    service: FestivalService = Depends(get_festival_service),
    db: Session = Depends(get_db),
):
    return service.get(db, id)
```

### Eager Loading

```python
# In service
def get_with_relations(self, db: Session, id: int):
    return db.query(self.model).options(
        joinedload(Festival.events),
        joinedload(Festival.members).joinedload(UserFestival.user)
    ).filter(self.model.id == id).first()
```

### Bulk Operations

```python
def bulk_create(self, db: Session, objs_in: List[CreateSchema]) -> List[Model]:
    db_objs = [self.model(**obj.dict()) for obj in objs_in]
    db.bulk_save_objects(db_objs)
    db.commit()
    return db_objs
```

### Soft Delete Pattern

```python
# Model
deleted_at = Column(DateTime, nullable=True)

# Service
def remove(self, db: Session, id: int):
    obj = self.get(db, id)
    obj.deleted_at = datetime.utcnow()
    db.commit()
    return obj

def get_multi(self, db: Session, *, skip=0, limit=100, include_deleted=False):
    query = db.query(self.model)
    if not include_deleted:
        query = query.filter(self.model.deleted_at.is_(None))
    return query.offset(skip).limit(limit).all()
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: app` | Run from `backend/` dir or `PYTHONPATH=backend` |
| `sqlite3.OperationalError: database is locked` | Enable WAL: `PRAGMA journal_mode=WAL;` or use separate DB per test |
| `alembic: Target database not up to date` | Run `alembic upgrade head` |
| `JWT decode error` | Check `SECRET_KEY` matches between services |
| `CORS error in browser` | Set `CORS_ORIGINS` to exact frontend origin (no trailing slash) |
| `Rate limited immediately` | Disable in tests: `export TESTING=true` |
| `WebSocket 403` | Pass `?token=<access_token>` in WS URL |
| `MariaDB connection refused` | Check host/port, ensure `db` service healthy in Docker |

---

## Useful Scripts

```bash
# Seed admin user (idempotent)
python -c "
from app.database import SessionLocal
from app.models.user import User
from app.services.user_service import pwd_context
db = SessionLocal()
if not db.query(User).filter(User.username=='admin').first():
    u = User(username='admin', email='admin@clakettes.com', password_hash=pwd_context.hash('Admin123!'), full_name='Admin', role='admin', is_active=True, is_public=True)
    db.add(u); db.commit()
    print('Admin created: admin / Admin123!')
else:
    print('Admin already exists')
"

# List all tables
python -c "
from app.database import engine
from sqlalchemy import inspect
print(inspect(engine).get_table_names())
"

# Check migration status
alembic current
alembic history
```