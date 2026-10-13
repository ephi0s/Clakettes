# Clakettes Backend-a — Dokumentazio teknikoa

[ES](BACKEND.md) · [EN](BACKEND.en.md) · [FR](BACKEND.fr.md) · [DE](BACKEND.de.md) · [IT](BACKEND.it.md) · [CA](BACKEND.ca.md) · [EU](BACKEND.eu.md) · [GL](BACKEND.gl.md) · [OC](BACKEND.oc.md)

Clakettes zine-jaialdien kudeaketa plataformarako FastAPI backend-a.

## Hasiera azkarra

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

## Arkitektura

### Geruzazko egitura

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

### Diseinuko funtsezko printzipioak

1. **Router arinak** — zerbitzuetan delegatzen dute
2. **Egoerarik gabeko zerbitzuak** — `db: Session` mendekotasun-injekzioz jasotzen dute
3. **Modeloek `BaseModel` heredatzen dute** — `id`, `created_at`, `updated_at` entitate guztietan
4. **Enum zentralizatuak** — `app/enums.py` modelo eta eskemen artean partekatua
5. **Oinarrizko CRUD generikoa** — `BaseService` `app/services/base_service.py`-n

---

## Konfigurazioa

Konfigurazio guztia `backend/.env` bidez egiten da (`pydantic-settings`-ek kargatua):

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./clakettes.db` | SQLAlchemy connection string |
| `SECRET_KEY` | (required, no default) | JWT signing key |
| `JWT_ISSUER` | `clakettes` | JWT issuer claim |
| `JWT_AUDIENCE` | `clakettes-api` | JWT audience claim |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token TTL |
| `CORS_ORIGINS` | `None` (→ `["*"]`) | Comma-separated allowed origins |
| `PORT_BACKEND` | `8000` | Server port (used by Docker/start scripts) |

**`.env` adibidea ekoizpenean:**

```env
DATABASE_URL=mariadb+pymysql://user:pass@db:3306/clakettes_db
SECRET_KEY=super-secret-64-char-urlsafe-string
JWT_ISSUER=clakettes
JWT_AUDIENCE=clakettes-api
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=https://app.example.com,https://admin.example.com
```

Sortu `SECRET_KEY` sendo bat:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

---

## Datu-basea

### Bi datu-baserekiko bateragarritasuna

| Environment | Database | Connection String |
|-------------|----------|-------------------|
| Development | SQLite | `sqlite:///./data/clakettes.db` |
| Production | MariaDB | `mariadb+pymysql://user:pass@host:3306/db` |

### Oinarrizko eredua

Eredu guztiek `BaseModel`-etik heredatzen dute (`app/models/base.py`):

```python
class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

### Migrazioak (Alembic)

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

**Migrazio-oharrak (SQLite ↔ MariaDB):**
- SQLite `INTEGER PRIMARY KEY` → MariaDB `INT AUTO_INCREMENT`
- SQLite `TEXT` → MariaDB `TEXT`/`VARCHAR`
- SQLite `DATETIME` (stored as TEXT) → MariaDB native `DATETIME`
- Los scripts de exportación/importación en `backend/tools/` gestionan las conversiones de tipos

### Ereduen laburpena (31 modelo)

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

Ikusi [DATABASE.md](DATABASE.eu.md) eskema osoaren dokumentaziorako ER diagramekin.

---

## Autentikazioa

### JWT + Saioen jarraipena

| Token Type | Format | TTL | Storage |
|------------|--------|-----|---------|
| **Access Token** | JWT (HS256) | 30 min (configurable) | Client memory |
| **Refresh Token** | Opaque (SHA-256 hash in DB) | 30 days | `UserSession.refresh_token_hash` |

### Saio-hasierako fluxua

```
POST /api/users/login
  {username, password}
→ 200 {access_token, refresh_token, token_type: "bearer", user: {...}}
```

### Token-aren erabilera

```http
Authorization: Bearer <access_token>
```

### Berriztatze-fluxua

```
POST /api/users/refresh
  {refresh_token}
→ 200 {access_token, refresh_token, token_type: "bearer"}
```

### Saioen kudeaketa

- `GET /api/auth/sessions` — Saio aktiboak zerrendatu
- `DELETE /api/auth/sessions/{session_id}` — Saioa ezeztatu
- Saioa login-ean sortzen da gailuaren infoarekin (IP, UA, izena)
- Token-ak berriztatzean errotatzen dira; zaharrak baliogabetuta geratzen dira

### Pasahitz-hash-a

- **bcrypt** `passlib` bidez (rounds=12)
- Hash-a `User.password_hash`-en gordeta
- `pwd_context.verify(plain, hash)` bidez egiaztatzen da

### Eskaera-muga

- **100 requests / 60 seconds** IP-ko (SQLite babesarekin)
- `RateLimitMiddleware` bidez aplikatzen da `main.py`-n
- Desaktibatu egiten da `TESTING=true` ingurune-aldagaia ezartzean

---

## API endpoint-ak

### Router-en erregistroa (`app/main.py`)

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

Guztira: 33 router

### Paginazioa eta iragazketa

Kontsulta-parametro estandarrak zerrenda-endpoint-etan:

```
GET /api/festivals/?page=1&size=20&search=cannes&is_active=true
```

Erantzun-bilgarria:

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

## Denbora errealeko txata

### WebSocket Backend-a (`app/chat_backend/`)

| Component | Description |
|-----------|-------------|
| `WebSocketChatBackend` | Default implementation (in-memory connections) |
| `chat_backend_registry` | Singleton registry for backend swapping |
| `ConnectionManager` | Manages user↔WebSocket mappings |

### Endpoint-ak

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/chat/ws` | WebSocket connection (auth via query `token`) |
| `POST` | `/api/chat/messages` | Send message (REST fallback) |
| `GET` | `/api/chat/messages` | Paginated history |
| `PATCH` | `/api/chat/messages/{id}/read` | Mark read |

### Mezu-motak

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

- X25519 giltza-trukea `/api/users/{id}/keys` bidez
- Giltza publikoak `UserKey`-n gordeta (aktibo bat erabiltzaileko)
- Zifratzea/des-zifratzea frontend-ean (`e2ee_service.dart`)

---

## Fitxategi-igoera

### Avatar-igoera

```
POST /api/uploads/avatar
Content-Type: multipart/form-data
Authorization: Bearer <token>

file: <image/*>
```

- `backend/uploads/avatars/{user_id}_{uuid}.{ext}`-n gordeta
- Estatiko gisa zerbitzatuta `/uploads/avatars/...`-n
- Gehienezko tamaina: 10 MB (`RequestSizeLimitMiddleware`-ek aplikatua)

---

## Administrazio-endpoint-ak

`role=admin` behar du (`admin_service.py`-n egiaztatua):

| Endpoint | Descripción |
|----------|-------------|
| `GET /api/admin/stats` | Platform statistics |
| `GET /api/admin/tables` | Row counts per table |
| `GET /api/admin/audit-log` | Audit trail (filtros `action`, `actor_user_id`) |

---

## Probak

```bash
cd backend

# Run all tests
python -m pytest tests/ -x -q --tb=short

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=term-missing

# Specific test file
python -m pytest tests/test_festivals.py -v
```

**Probakonfigurazioa** (`pyproject.toml` / `pytest.ini`):

```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_functions = test_*
```

**Fixture-ak** (`tests/conftest.py`):
- `db_session` — memoriako SQLite saioa
- `client` — `AsyncClient` (httpx) proba-app-aren aurka
- `auth_headers` — jada autentikatutako goiburuak

**Oharra**: `conftest.py` bikoiztua dago `tests/services/`-n — bateratu beharko lirateke.

---

## Lint eta formatua

```bash
# Check
ruff check .

# Fix auto-fixable
ruff check . --fix

# Format
ruff format .
```

**Konfigurazioa** (`pyproject.toml`):

```toml
[tool.ruff]
line-length = 120
target-version = "py312"
select = ["E", "F", "I", "UP", "B", "C4", "PTH", "T20", "SIM", "ARG"]
ignore = ["E501", "SIM102", "SIM103"]
```

---

## Garapen-fluxua

### Tokiko garapena

```bash
# Terminal 1: Backend
cd backend
python -m uvicorn app.main:app --reload

# Terminal 2: Frontend (if needed)
cd frontend
flutter run -d web-server --web-port 3000 --dart-define=BACKEND_URL=http://localhost:8000/api
```

### Garapena Docker-rekin

```bash
# From project root
docker compose up        # Backend:8000, Frontend:3000
docker compose --profile db up  # + MariaDB:3306
```

### Datu-basearen hasierako karga

Seed script-ik ez dago: garapenean app-ak hasierako admin-a sortzen du (`admin` /
`setup`, aldatu pasahitza sartzean) eta taulak `create_all` bidez. Ekoizpenean
datuak API-tik datoz eta eskema Alembic bidez soilik.

### Ohiko komandoak

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

## Proiektuaren egitura

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

Doc-ak `docs/BACKEND.md` (fitxategi hau euskaraz: [BACKEND.eu.md](BACKEND.eu.md)) eta `docs/DATABASE.md`-n.

---

## Hedapena

### Docker (Ekoizpena)

```yaml
# docker-compose.yml uses --profile prod
docker compose --profile prod up -d
```

Zerbitzuak:
- `backend-prod` — FastAPI (workers Uvicorn) :8000-n
- `frontend-prod` — Nginx + Flutter web :80-n
- `db` — MariaDB 11 (comprobación de estado)

Profil erabilgarriak:
- `dev` (lehenetsia): backend eta frontend garapen-zerbitzariak
- `db`: MariaDB edukiontzia gehitzen du
- `prod`: nginx-dun ekoizpen-pila

### Ingurune-aldagaiak (Ekoizpena)

```env
DATABASE_URL=mariadb+pymysql://user:pass@db:3306/clakettes_db
SECRET_KEY=<64-char-urlsafe>
CORS_ORIGINS=https://app.example.com
```

### Egoera-egiaztapena

```bash
curl http://localhost:8000/health
# {"status": "healthy"}
```

---

## Segurtasun-egiaztapen zerrenda

- [ ] Aldatu `SECRET_KEY` ekoizpenean
- [ ] Ezarri `CORS_ORIGINS` domeinu espezifikoetan
- [ ] Erabili MariaDB (ez SQLite) ekoizpenean
- [ ] Gaitu HTTPS (alderantzizko proxy-a: nginx/Traefik)
- [ ] Konfiguratu baimendutako host-ak `TrustedHostMiddleware`-n
- [ ] Errotatu JWT giltzak aldian-aldian
- [ ] Zaindu eskaera-mugatzailearen erregistroak
- [ ] Berrikusi admin erabiltzailearen pasahitza lehen saio-hasieraren ondoren

---

## APIa zabaltzea

### Baliabide berri bat gehitzea

1. **Eredua** — `app/models/new_resource.py` (`BaseModel` heredatzen du)
2. **Eskema** — `app/schemas/new_resource.py` (Pydantic)
3. **Zerbitzua** — `app/services/new_resource_service.py` (`BaseService` hedatzen du)
4. **Router-a** — `app/routers/new_resource.py` (`main.py`-n barne hartu)
5. **Migrazioa** — `alembic revision --autogenerate -m "add new_resource"`
6. **Probak** — `tests/test_new_resource.py`

### Endpoint pertsonalizatu bat gehitzea lehendik dagoen router batean

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

## Arazoen konponbidea

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

## Erreferentziak

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [Pydantic v2](https://docs.pydantic.dev/latest/)
- [Alembic](https://alembic.sqlalchemy.org/)
- [python-jose](https://github.com/mpdavis/python-jose)
- [passlib](https://passlib.readthedocs.io/)
