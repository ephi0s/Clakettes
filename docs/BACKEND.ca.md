# Clakettes Backend — Documentació tècnica

[ES](BACKEND.md) · [EN](BACKEND.en.md) · [FR](BACKEND.fr.md) · [DE](BACKEND.de.md) · [IT](BACKEND.it.md) · [CA](BACKEND.ca.md) · [EU](BACKEND.eu.md) · [GL](BACKEND.gl.md) · [OC](BACKEND.oc.md)

Backend FastAPI per a la plataforma de gestió de festivals de cinema Clakettes.

## Inici ràpid

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

### Estructura per capes

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

### Principis clau de disseny

1. **Routers lleugers** — deleguen en els serveis
2. **Serveis sense estat** — reben `db: Session` mitjançant injecció de dependències
3. **Els models hereten `BaseModel`** — `id`, `created_at`, `updated_at` a totes les entitats
4. **Enums centralitzats** — `app/enums.py` compartit entre models i esquemes
5. **Base CRUD genèrica** — `BaseService` a `app/services/base_service.py`

---

## Configuració

Tota la configuració es fa mitjançant `backend/.env` (carregat per `pydantic-settings`):

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./clakettes.db` | SQLAlchemy connection string |
| `SECRET_KEY` | (required, no default) | JWT signing key |
| `JWT_ISSUER` | `clakettes` | JWT issuer claim |
| `JWT_AUDIENCE` | `clakettes-api` | JWT audience claim |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token TTL |
| `CORS_ORIGINS` | `None` (→ `["*"]`) | Comma-separated allowed origins |
| `PORT_BACKEND` | `8000` | Server port (used by Docker/start scripts) |

**Exemple de `.env` en producció:**

```env
DATABASE_URL=mariadb+pymysql://user:pass@db:3306/clakettes_db
SECRET_KEY=super-secret-64-char-urlsafe-string
JWT_ISSUER=clakettes
JWT_AUDIENCE=clakettes-api
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=https://app.example.com,https://admin.example.com
```

Genereu una clau `SECRET_KEY` robusta:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

---

## Base de dades

### Compatibilitat amb dues bases de dades

| Environment | Database | Connection String |
|-------------|----------|-------------------|
| Development | SQLite | `sqlite:///./data/clakettes.db` |
| Production | MariaDB | `mariadb+pymysql://user:pass@host:3306/db` |

### Model base

Tots els models hereten de `BaseModel` (`app/models/base.py`):

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

**Notes de migració (SQLite ↔ MariaDB):**
- SQLite `INTEGER PRIMARY KEY` → MariaDB `INT AUTO_INCREMENT`
- SQLite `TEXT` → MariaDB `TEXT`/`VARCHAR`
- SQLite `DATETIME` (stored as TEXT) → MariaDB native `DATETIME`
- Els scripts d'exportació/importació a `backend/tools/` gestionen les conversions de tipus

### Resum de models (31 models)

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

Consulteu [DATABASE.ca.md](DATABASE.ca.md) per a la documentació completa de l'esquema amb diagrames ER.

---

## Autenticació

### JWT + Seguiment de sessions

| Token Type | Format | TTL | Storage |
|------------|--------|-----|---------|
| **Access Token** | JWT (HS256) | 30 min (configurable) | Client memory |
| **Refresh Token** | Opaque (SHA-256 hash in DB) | 30 days | `UserSession.refresh_token_hash` |

### Flux d'inici de sessió

```
POST /api/users/login
  {username, password}
→ 200 {access_token, refresh_token, token_type: "bearer", user: {...}}
```

### Ús del token

```http
Authorization: Bearer <access_token>
```

### Flux de renovació

```
POST /api/users/refresh
  {refresh_token}
→ 200 {access_token, refresh_token, token_type: "bearer"}
```

### Gestió de sessions

- `GET /api/auth/sessions` — Llistar les sessions actives
- `DELETE /api/auth/sessions/{session_id}` — Revocar la sessió
- La sessió es crea en iniciar sessió amb informació del dispositiu (IP, UA, nom)
- Els tokens es roten en renovar; els tokens antics queden invalidats

### Hash de contrasenyes

- **bcrypt** mitjançant `passlib` (rounds=12)
- Hash desat a `User.password_hash`
- Es verifica mitjançant `pwd_context.verify(plain, hash)`

### Límit de peticions

- **100 requests / 60 seconds** per IP (amb suport en SQLite)
- S'aplica mitjançant `RateLimitMiddleware` a `main.py`
- Es desactiva quan s'estableix la variable d'entorn `TESTING=true`

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

Total: 33 routers

### Paginació i filtrat

Paràmetres de consulta estàndard als endpoints de llistat:

```
GET /api/festivals/?page=1&size=20&search=cannes&is_active=true
```

Envolvent de resposta:

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

## Xat en temps real

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

### Tipus de missatge

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

- Intercanvi de claus X25519 mitjançant `/api/users/{id}/keys`
- Claus públiques desades a `UserKey` (una activa per usuari)
- Xifrat/desxifrat al frontend (`e2ee_service.dart`)

---

## Pujada de fitxers

### Pujada d'avatar

```
POST /api/uploads/avatar
Content-Type: multipart/form-data
Authorization: Bearer <token>

file: <image/*>
```

- Desat a `backend/uploads/avatars/{user_id}_{uuid}.{ext}`
- Servit de forma estàtica a `/uploads/avatars/...`
- Mida màxima: 10 MB (aplicat per `RequestSizeLimitMiddleware`)

---

## Endpoints d'administració

Requereix `role=admin` (comprovat a `admin_service.py`):

| Endpoint | Descripción |
|----------|-------------|
| `GET /api/admin/stats` | Platform statistics |
| `GET /api/admin/tables` | Row counts per table |
| `GET /api/admin/audit-log` | Audit trail (filtros `action`, `actor_user_id`) |

---

## Proves

```bash
cd backend

# Run all tests
python -m pytest tests/ -x -q --tb=short

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=term-missing

# Specific test file
python -m pytest tests/test_festivals.py -v
```

**Configuració de proves** (`pyproject.toml` / `pytest.ini`):

```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_functions = test_*
```

**Fixtures** (`tests/conftest.py`):
- `db_session` — sessió SQLite en memòria
- `client` — `AsyncClient` (httpx) contra l'app de proves
- `auth_headers` — capçaleres ja autenticades

**Nota**: Hi ha un `conftest.py` duplicat a `tests/services/` — caldria unificar-lo.

---

## Lint i format

```bash
# Check
ruff check .

# Fix auto-fixable
ruff check . --fix

# Format
ruff format .
```

**Configuració** (`pyproject.toml`):

```toml
[tool.ruff]
line-length = 120
target-version = "py312"
select = ["E", "F", "I", "UP", "B", "C4", "PTH", "T20", "SIM", "ARG"]
ignore = ["E501", "SIM102", "SIM103"]
```

---

## Flux de desenvolupament

### Desenvolupament local

```bash
# Terminal 1: Backend
cd backend
python -m uvicorn app.main:app --reload

# Terminal 2: Frontend (if needed)
cd frontend
flutter run -d web-server --web-port 3000 --dart-define=BACKEND_URL=http://localhost:8000/api
```

### Desenvolupament amb Docker

```bash
# From project root
docker compose up        # Backend:8000, Frontend:3000
docker compose --profile db up  # + MariaDB:3306
```

### Càrrega inicial de la base de dades

No hi ha script de seed: en desenvolupament l'app crea l'admin inicial (`admin` /
`setup`, canvieu la contrasenya en entrar) i les taules mitjançant `create_all`. En producció les
dades arriben per l'API i l'esquema només mitjançant Alembic.

### Ordres habituals

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

## Estructura del projecte

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

Docs a `docs/BACKEND.ca.md` (aquest fitxer) i `docs/DATABASE.ca.md`.

---

## Desplegament

### Docker (Producció)

```yaml
# docker-compose.yml uses --profile prod
docker compose --profile prod up -d
```

Serveis:
- `backend-prod` — FastAPI (workers Uvicorn) a :8000
- `frontend-prod` — Nginx + Flutter web a :80
- `db` — MariaDB 11 (comprovació d'estat)

Perfils disponibles:
- `dev` (predeterminat): servidors de desenvolupament de backend i frontend
- `db`: afegeix el contenidor MariaDB
- `prod`: pila de producció amb nginx

### Variables d'entorn (Producció)

```env
DATABASE_URL=mariadb+pymysql://user:pass@db:3306/clakettes_db
SECRET_KEY=<64-char-urlsafe>
CORS_ORIGINS=https://app.example.com
```

### Comprovació d'estat

```bash
curl http://localhost:8000/health
# {"status": "healthy"}
```

---

## Llista de comprovació de seguretat

- [ ] Canvieu `SECRET_KEY` en producció
- [ ] Establiu `CORS_ORIGINS` a dominis específics
- [ ] Utilitzeu MariaDB (no SQLite) en producció
- [ ] Habiliteu HTTPS (proxy invers: nginx/Traefik)
- [ ] Configureu els hosts permesos a `TrustedHostMiddleware`
- [ ] Roteu les claus JWT periòdicament
- [ ] Vigileu els registres del limitador de peticions
- [ ] Reviseu la contrasenya de l'usuari admin després del primer inici de sessió

---

## Ampliar l'API

### Afegir un recurs nou

1. **Model** — `app/models/new_resource.py` (hereta `BaseModel`)
2. **Esquema** — `app/schemas/new_resource.py` (Pydantic)
3. **Servei** — `app/services/new_resource_service.py` (estén `BaseService`)
4. **Router** — `app/routers/new_resource.py` (incloure a `main.py`)
5. **Migració** — `alembic revision --autogenerate -m "add new_resource"`
6. **Proves** — `tests/test_new_resource.py`

### Afegir un endpoint personalitzat a un router existent

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

## Resolució de problemes

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

## Referències

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [Pydantic v2](https://docs.pydantic.dev/latest/)
- [Alembic](https://alembic.sqlalchemy.org/)
- [python-jose](https://github.com/mpdavis/python-jose)
- [passlib](https://passlib.readthedocs.io/)
