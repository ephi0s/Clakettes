# Clakettes Backend — Documentacion tecnica

[ES](../es/BACKEND.md) · [EN](../en/BACKEND.md) · [FR](../fr/BACKEND.md) · [DE](../de/BACKEND.md) · [IT](../it/BACKEND.md) · [CA](../ca/BACKEND.md) · [EU](../eu/BACKEND.md) · [GL](../gl/BACKEND.md) · [OC](BACKEND.md)

Backend FastAPI per la plataforma de gestion de festivals de cinèma Clakettes.

## Aviada rapida

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

## Arquitectura

### Estructura per capas

```
Routers (FastAPI) → Services (Business Logic) → Models (SQLAlchemy)
```

| Capa | Ubicación | Responsabilidad |
|-------|----------|----------------|
| **Routers** | `app/routers/` | HTTP endpoints, request/response validation, pagination |
| **Services** | `app/services/` | Business logic, CRUD operations, cross-cutting concerns |
| **Models** | `app/models/` | SQLAlchemy ORM models, DB schema |
| **Schemas** | `app/schemas/` | Pydantic models for request/response |
| **Auth** | `app/auth.py` | JWT, sessions, password hashing |
| **Config** | `app/config.py` | Pydantic Settings from `.env` |
| **Database** | `app/database.py` | Engine, session factory, `get_db()` dependency |

### Principis claus de concepcion

1. **Routers leugièrs** — delegan dins los servicis
2. **Servicis sens estat** — recebon `db: Session` mejançant injeccion de dependéncias
3. **Los modèls eiretan `BaseModel`** — `id`, `created_at`, `updated_at` en totas las entitats
4. **Enums centralizats** — `app/enums.py` partejat entre modèls e esquèmas
5. **CRUD de basa generica** — `BaseService` en `app/services/base_service.py`

---

## Configuracion

Tota la configuracion se fa mejançant `backend/.env` (cargat per `pydantic-settings`):

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./clakettes.db` | SQLAlchemy connection string |
| `SECRET_KEY` | (required, no default) | JWT signing key |
| `JWT_ISSUER` | `clakettes` | JWT issuer claim |
| `JWT_AUDIENCE` | `clakettes-api` | JWT audience claim |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token TTL |
| `CORS_ORIGINS` | `None` (→ `["*"]`) | Comma-separated allowed origins |
| `PORT_BACKEND` | `8000` | Server port (used by Docker/start scripts) |

**Exemple de `.env` en produccion:**

```env
DATABASE_URL=mariadb+pymysql://user:pass@db:3306/clakettes_db
SECRET_KEY=super-secret-64-char-urlsafe-string
JWT_ISSUER=clakettes
JWT_AUDIENCE=clakettes-api
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=https://app.example.com,https://admin.example.com
```

Generatz una clau `SECRET_KEY` robusta:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

---

## Banca de donadas

### Compatibilitat amb doas bancas de donadas

| Environment | Database | Connection String |
|-------------|----------|-------------------|
| Development | SQLite | `sqlite:///./data/clakettes.db` |
| Production | MariaDB | `mariadb+pymysql://user:pass@host:3306/db` |

### Modèl de basa

Totes los modèls eiretan de `BaseModel` (`app/models/base.py`):

```python
class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

### Migracions (Alembic)

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

**Nòtas de migracion (SQLite ↔ MariaDB):**
- SQLite `INTEGER PRIMARY KEY` → MariaDB `INT AUTO_INCREMENT`
- SQLite `TEXT` → MariaDB `TEXT`/`VARCHAR`
- SQLite `DATETIME` (stored as TEXT) → MariaDB native `DATETIME`
- Los scripts de exportación/importación en `backend/tools/` gestionan las conversiones de tipos

### Resumit de modèls (31 modèls)

| Modelo | Tabla | Relaciones clave |
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

Consultatz [DATABASE.md](DATABASE.md) per la documentacion completa de l'esquèma amb diagramas ER.

---

## Autentificacion

### JWT + Seguiment de sessions

| Token Type | Format | TTL | Storage |
|------------|--------|-----|---------|
| **Access Token** | JWT (HS256) | 30 min (configurable) | Client memory |
| **Refresh Token** | Opaque (SHA-256 hash in DB) | 30 days | `UserSession.refresh_token_hash` |

### Flux d'intrada

```
POST /api/users/login
  {username, password}
→ 200 {access_token, refresh_token, token_type: "bearer", user: {...}}
```

### Usatge del token

```http
Authorization: Bearer <access_token>
```

### Flux de renovelament

```
POST /api/users/refresh
  {refresh_token}
→ 200 {access_token, refresh_token, token_type: "bearer"}
```

### Gestion de sessions

- `GET /api/auth/sessions` — Listar las sessions activas
- `DELETE /api/auth/sessions/{session_id}` — Revocar la session
- La session se crea en iniciar session amb informacion del dispositiu (IP, UA, nom)
- Los tokens se rotan en renovar; los tokens ancians demòran invalidats

### Hash de senhals

- **bcrypt** mejançant `passlib` (rounds=12)
- Hash gardat en `User.password_hash`
- Se verifica mejançant `pwd_context.verify(plain, hash)`

### Limit de requèstas

- **100 requests / 60 seconds** per IP (amb sosten en SQLite)
- S'aplica mejançant `RateLimitMiddleware` en `main.py`
- S'atomba quand s'establís la variabla d'environa `TESTING=true`

---

## Endpoints de l'API

### Registre de routers (`app/main.py`)

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

Totau: 33 routers

### Paginacion e filtratge

Paramètres de consulta estandard dins los endpoints de listat:

```
GET /api/festivals/?page=1&size=20&search=cannes&is_active=true
```

Embalatge de responsa:

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

## Chat en temps reau

### Backend WebSocket (`app/chat_backend/`)

| Component | Description |
|-----------|-------------|
| `WebSocketChatBackend` | Default implementation (in-memory connections) |
| `chat_backend_registry` | Singleton registry for backend swapping |
| `ConnectionManager` | Manages user↔WebSocket mappings |

### Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/chat/ws` | WebSocket connection (auth via query `token`) |
| `POST` | `/api/chat/messages` | Send message (REST fallback) |
| `GET` | `/api/chat/messages` | Paginated history |
| `PATCH` | `/api/chat/messages/{id}/read` | Mark read |

### Tipus de messatge

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

- Escambi de claus X25519 mejançant `/api/users/{id}/keys`
- Claus publicas gardadas en `UserKey` (una activa per utilizaire)
- Chiframent/deschiframent dins lo frontend (`e2ee_service.dart`)

---

## Pujada de fichièrs

### Pujada d'avatar

```
POST /api/uploads/avatar
Content-Type: multipart/form-data
Authorization: Bearer <token>

file: <image/*>
```

- Gardat en `backend/uploads/avatars/{user_id}_{uuid}.{ext}`
- Servit de forma estatica en `/uploads/avatars/...`
- Talha maximala: 10 MB (aplicat per `RequestSizeLimitMiddleware`)

---

## Endpoints d'administracion

Requerís `role=admin` (contrarotlat en `admin_service.py`):

| Endpoint | Descripción |
|----------|-------------|
| `GET /api/admin/stats` | Platform statistics |
| `GET /api/admin/tables` | Row counts per table |
| `GET /api/admin/audit-log` | Audit trail (filtros `action`, `actor_user_id`) |

---

## Tèsts

```bash
cd backend

# Run all tests
python -m pytest tests/ -x -q --tb=short

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=term-missing

# Specific test file
python -m pytest tests/test_festivals.py -v
```

**Configuracion de tèsts** (`pyproject.toml` / `pytest.ini`):

```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_functions = test_*
```

**Fixtures** (`tests/conftest.py`):
- `db_session` — session SQLite en memòria
- `client` — `AsyncClient` (httpx) contra l'app de pròva
- `auth_headers` — entèstas ja autenticadas

**Nòta**: I a un `conftest.py` duplicat en `tests/services/` — caldriá l'unificar.

---

## Lint e formatatge

```bash
# Check
ruff check .

# Fix auto-fixable
ruff check . --fix

# Format
ruff format .
```

**Configuracion** (`pyproject.toml`):

```toml
[tool.ruff]
line-length = 120
target-version = "py312"
select = ["E", "F", "I", "UP", "B", "C4", "PTH", "T20", "SIM", "ARG"]
ignore = ["E501", "SIM102", "SIM103"]
```

---

## Flux de desvolopament

### Desvolopament locau

```bash
# Terminal 1: Backend
cd backend
python -m uvicorn app.main:app --reload

# Terminal 2: Frontend (if needed)
cd frontend
flutter run -d web-server --web-port 3000 --dart-define=BACKEND_URL=http://localhost:8000/api
```

### Desvolopament amb Docker

```bash
# From project root
docker compose up        # Backend:8000, Frontend:3000
docker compose --profile db up  # + MariaDB:3306
```

### Carga iniciala de la banca de donadas

I a pas de script de seed: en desvolopament l'app crea l'admin iniciau (`admin` /
`setup`, cambiatz lo senhal en intrar) e las taulas mejançant `create_all`. En produccion las
donadas arriban per l'API e l'esquèma sonque mejançant Alembic.

### Comandas usualas

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

## Estructura del projècte

```
backend/
├── app/
│   ├── models/              # 34 SQLAlchemy models
│   ├── schemas/             # 33 Pydantic schemas
│   ├── services/            # 36 business logic services
│   ├── routers/             # 36 API routers (33 con APIRouter)
│   ├── chat_backend/        # WebSocket chat implementation
│   ├── auth.py              # JWT + session auth
│   ├── config.py            # Pydantic Settings
│   ├── database.py          # Engine, SessionLocal, get_db()
│   ├── main.py              # FastAPI app, middleware, routers
│   ├── rate_limiter.py      # SQLite rate limiter
│   ├── enums.py             # Shared enums
│   └── scripts/             # Seed/migration scripts
├── alembic/                 # Migrations (18 versions)
├── tools/                   # Export/import scripts
├── tests/                   # pytest tests (37 files)
├── uploads/                 # Static file uploads
├── .env.example             # Config template
├── requirements.txt         # Production deps
├── requirements-dev.txt     # Dev deps (pytest, ruff)
├── pyproject.toml           # Ruff, pytest config
└── pytest.ini               # Pytest config
```

Docs en `docs/oc/BACKEND.md` (aqueste fichièr) e `docs/oc/DATABASE.md`.

---

## Desplegament

### Docker (Produccion)

```yaml
# docker-compose.yml uses --profile prod
docker compose --profile prod up -d
```

Servicis:
- `backend-prod` — FastAPI (workers Uvicorn) en :8000
- `frontend-prod` — Nginx + Flutter web en :80
- `db` — MariaDB 11 (comprobación de estado)

Perfils disponibles:
- `dev` (predeterminado): servidores de desarrollo de backend y frontend
- `db`: añade el contenedor MariaDB
- `prod`: pila de producción con nginx

### Variablas d'environa (Produccion)

```env
DATABASE_URL=mariadb+pymysql://user:pass@db:3306/clakettes_db
SECRET_KEY=<64-char-urlsafe>
CORS_ORIGINS=https://app.example.com
```

### Contraròtle de santat

```bash
curl http://localhost:8000/health
# {"status": "healthy"}
```

---

## Lista de contraròtle de seguretat

- [ ] Cambiatz `SECRET_KEY` en produccion
- [ ] Establissètz `CORS_ORIGINS` en dominis especifics
- [ ] Utilizatz MariaDB (non SQLite) en produccion
- [ ] Abilitatz HTTPS (proxy invèrs: nginx/Traefik)
- [ ] Configuratz los òstes permeses en `TrustedHostMiddleware`
- [ ] Rotatz las claus JWT periodicament
- [ ] Velhatz los registres del limitador de requèstas
- [ ] Revisatz lo senhal de l'utilizaire admin aprèp lo primièr intrada

---

## Ampliar l'API

### Apondre una ressorsa nòva

1. **Modèl** — `app/models/new_resource.py` (eireta `BaseModel`)
2. **Esquèma** — `app/schemas/new_resource.py` (Pydantic)
3. **Servici** — `app/services/new_resource_service.py` (estend `BaseService`)
4. **Router** — `app/routers/new_resource.py` (inclure en `main.py`)
5. **Migracion** — `alembic revision --autogenerate -m "add new_resource"`
6. **Pròvas** — `tests/test_new_resource.py`

### Apondre un endpoint personalizat a un router existent

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

## Resolucion de problèmas

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

## Referéncias

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [Pydantic v2](https://docs.pydantic.dev/latest/)
- [Alembic](https://alembic.sqlalchemy.org/)
- [python-jose](https://github.com/mpdavis/python-jose)
- [passlib](https://passlib.readthedocs.io/)
