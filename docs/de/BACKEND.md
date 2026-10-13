# Clakettes Backend — Technische Dokumentation

[ES](../es/BACKEND.md) · [EN](../en/BACKEND.md) · [FR](../fr/BACKEND.md) · [DE](BACKEND.md) · [IT](../it/BACKEND.md) · [CA](../ca/BACKEND.md) · [EU](../eu/BACKEND.md) · [GL](../gl/BACKEND.md) · [OC](../oc/BACKEND.md)

FastAPI-Backend für die Filmfestival-Management-Plattform Clakettes.

## Schnellstart

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

## Architektur

### Schichtenstruktur

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

### Zentrale Designprinzipien

1. **Schlanke Router** — delegieren an die Services
2. **Zustandslose Services** — erhalten `db: Session` per Dependency Injection
3. **Models erben von `BaseModel`** — `id`, `created_at`, `updated_at` in allen Entitäten
4. **Zentralisierte Enums** — `app/enums.py` gemeinsam für Models und Schemas
5. **Generisches CRUD-Basismodul** — `BaseService` in `app/services/base_service.py`

---

## Konfiguration

Die gesamte Konfiguration erfolgt über `backend/.env` (geladen von `pydantic-settings`):

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./clakettes.db` | SQLAlchemy connection string |
| `SECRET_KEY` | (required, no default) | JWT signing key |
| `JWT_ISSUER` | `clakettes` | JWT issuer claim |
| `JWT_AUDIENCE` | `clakettes-api` | JWT audience claim |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token TTL |
| `CORS_ORIGINS` | `None` (→ `["*"]`) | Comma-separated allowed origins |
| `PORT_BACKEND` | `8000` | Server port (used by Docker/start scripts) |

**Beispiel-`.env` in Produktion:**

```env
DATABASE_URL=mariadb+pymysql://user:pass@db:3306/clakettes_db
SECRET_KEY=super-secret-64-char-urlsafe-string
JWT_ISSUER=clakettes
JWT_AUDIENCE=clakettes-api
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=https://app.example.com,https://admin.example.com
```

Einen robusten `SECRET_KEY` erzeugen:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

---

## Datenbank

### Zwei-Datenbank-Kompatibilität

| Environment | Database | Connection String |
|-------------|----------|-------------------|
| Development | SQLite | `sqlite:///./data/clakettes.db` |
| Production | MariaDB | `mariadb+pymysql://user:pass@host:3306/db` |

### Basismodell

Alle Modelle erben von `BaseModel` (`app/models/base.py`):

```python
class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

### Migrationen (Alembic)

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

**Migrationshinweise (SQLite ↔ MariaDB):**
- SQLite `INTEGER PRIMARY KEY` → MariaDB `INT AUTO_INCREMENT`
- SQLite `TEXT` → MariaDB `TEXT`/`VARCHAR`
- SQLite `DATETIME` (stored as TEXT) → MariaDB native `DATETIME`
- Die Export-/Import-Skripte in `backend/tools/` behandeln die Typkonvertierungen

### Modellübersicht (31 Modelle)

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

Siehe [DATABASE.md](DATABASE.md) für die vollständige Schema-Dokumentation mit ER-Diagrammen.

---

## Authentifizierung

### JWT + Sitzungsverfolgung

| Token Type | Format | TTL | Storage |
|------------|--------|-----|---------|
| **Access Token** | JWT (HS256) | 30 min (configurable) | Client memory |
| **Refresh Token** | Opaque (SHA-256 hash in DB) | 30 days | `UserSession.refresh_token_hash` |

### Login-Ablauf

```
POST /api/users/login
  {username, password}
→ 200 {access_token, refresh_token, token_type: "bearer", user: {...}}
```

### Token-Verwendung

```http
Authorization: Bearer <access_token>
```

### Erneuerungsablauf

```
POST /api/users/refresh
  {refresh_token}
→ 200 {access_token, refresh_token, token_type: "bearer"}
```

### Sitzungsverwaltung

- `GET /api/auth/sessions` — Aktive Sitzungen auflisten
- `DELETE /api/auth/sessions/{session_id}` — Sitzung widerrufen
- Die Sitzung wird beim Login mit Geräteinfo erstellt (IP, UA, Name)
- Tokens werden bei Erneuerung rotiert; alte Tokens werden ungültig

### Passwort-Hashing

- **bcrypt** via `passlib` (rounds=12)
- Hash gespeichert in `User.password_hash`
- Verifikation via `pwd_context.verify(plain, hash)`

### Request-Limit

- **100 requests / 60 seconds** pro IP (mit SQLite-Backend)
- Angewandt via `RateLimitMiddleware` in `main.py`
- Deaktiviert wenn die Env-Variable `TESTING=true` gesetzt ist

---

## API-Endpunkte

### Router-Registrierung (`app/main.py`)

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

### Paginierung und Filterung

Standard-Query-Parameter in Listen-Endpunkten:

```
GET /api/festivals/?page=1&size=20&search=cannes&is_active=true
```

Antwort-Hülle:

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

## Echtzeit-Chat

### WebSocket-Backend (`app/chat_backend/`)

| Component | Description |
|-----------|-------------|
| `WebSocketChatBackend` | Default implementation (in-memory connections) |
| `chat_backend_registry` | Singleton registry for backend swapping |
| `ConnectionManager` | Manages user↔WebSocket mappings |

### Endpunkte

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/chat/ws` | WebSocket connection (auth via query `token`) |
| `POST` | `/api/chat/messages` | Send message (REST fallback) |
| `GET` | `/api/chat/messages` | Paginated history |
| `PATCH` | `/api/chat/messages/{id}/read` | Mark read |

### Nachrichtentypen

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

- X25519-Schlüsselaustausch via `/api/users/{id}/keys`
- Öffentliche Schlüssel in `UserKey` gespeichert (einer aktiv pro Nutzer)
- Ver-/Entschlüsselung im Frontend (`e2ee_service.dart`)

---

## Datei-Upload

### Avatar-Upload

```
POST /api/uploads/avatar
Content-Type: multipart/form-data
Authorization: Bearer <token>

file: <image/*>
```

- Gespeichert in `backend/uploads/avatars/{user_id}_{uuid}.{ext}`
- Statisch serviert unter `/uploads/avatars/...`
- Max-Größe: 10 MB (angewandt durch `RequestSizeLimitMiddleware`)

---

## Administrations-Endpunkte

Erfordert `role=admin` (geprüft in `admin_service.py`):

| Endpoint | Descripción |
|----------|-------------|
| `GET /api/admin/stats` | Platform statistics |
| `GET /api/admin/tables` | Row counts per table |
| `GET /api/admin/audit-log` | Audit trail (filtros `action`, `actor_user_id`) |

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

**Testkonfiguration** (`pyproject.toml` / `pytest.ini`):

```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_functions = test_*
```

**Fixtures** (`tests/conftest.py`):
- `db_session` — SQLite-In-Memory-Sitzung
- `client` — `AsyncClient` (httpx) gegen die Test-App
- `auth_headers` — bereits authentifizierte Header

**Hinweis**: Es gibt ein doppeltes `conftest.py` in `tests/services/` — sie sollten vereinheitlicht werden.

---

## Lint und Format

```bash
# Check
ruff check .

# Fix auto-fixable
ruff check . --fix

# Format
ruff format .
```

**Konfiguration** (`pyproject.toml`):

```toml
[tool.ruff]
line-length = 120
target-version = "py312"
select = ["E", "F", "I", "UP", "B", "C4", "PTH", "T20", "SIM", "ARG"]
ignore = ["E501", "SIM102", "SIM103"]
```

---

## Entwicklungsablauf

### Lokale Entwicklung

```bash
# Terminal 1: Backend
cd backend
python -m uvicorn app.main:app --reload

# Terminal 2: Frontend (if needed)
cd frontend
flutter run -d web-server --web-port 3000 --dart-define=BACKEND_URL=http://localhost:8000/api
```

### Entwicklung mit Docker

```bash
# From project root
docker compose up        # Backend:8000, Frontend:3000
docker compose --profile db up  # + MariaDB:3306
```

### Initiale Datenbankbefüllung

Kein Seed-Skript: in Entwicklung erstellt die App den initialen Admin (`admin` /
`setup`, Passwort nach dem Login ändern) und die Tabellen via `create_all`. In Produktion kommen die
Daten über die API und das Schema nur via Alembic.

### Übliche Befehle

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

## Projektstruktur

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

Docs in `docs/de/BACKEND.md` (diese Datei) und `docs/de/DATABASE.md`.

---

## Deployment

### Docker (Produktion)

```yaml
# docker-compose.yml uses --profile prod
docker compose --profile prod up -d
```

Dienste:
- `backend-prod` — FastAPI (Uvicorn-Worker) auf :8000
- `frontend-prod` — Nginx + Flutter-Web auf :80
- `db` — MariaDB 11 (Healthcheck)

Verfügbare Profile:
- `dev` (Standard): Backend- und Frontend-Dev-Server
- `db`: fügt den MariaDB-Container hinzu
- `prod`: Produktions-Stack mit Nginx

### Umgebungsvariablen (Produktion)

```env
DATABASE_URL=mariadb+pymysql://user:pass@db:3306/clakettes_db
SECRET_KEY=<64-char-urlsafe>
CORS_ORIGINS=https://app.example.com
```

### Gesundheitsprüfung

```bash
curl http://localhost:8000/health
# {"status": "healthy"}
```

---

## Sicherheits-Checkliste

- [ ] `SECRET_KEY` in Produktion ändern
- [ ] `CORS_ORIGINS` auf spezifische Domains setzen
- [ ] MariaDB (nicht SQLite) in Produktion nutzen
- [ ] HTTPS aktivieren (Reverse-Proxy: nginx/Traefik)
- [ ] Erlaubte Hosts in `TrustedHostMiddleware` konfigurieren
- [ ] JWT-Schlüssel regelmäßig rotieren
- [ ] Logs des Request-Limiters überwachen
- [ ] Admin-Passwort nach dem ersten Login prüfen

---

## API erweitern

### Neue Ressource hinzufügen

1. **Modell** — `app/models/new_resource.py` (erbt `BaseModel`)
2. **Schema** — `app/schemas/new_resource.py` (Pydantic)
3. **Service** — `app/services/new_resource_service.py` (erweitert `BaseService`)
4. **Router** — `app/routers/new_resource.py` (in `main.py` einbinden)
5. **Migration** — `alembic revision --autogenerate -m "add new_resource"`
6. **Tests** — `tests/test_new_resource.py`

### Benutzerdefinierten Endpunkt zu bestehendem Router hinzufügen

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

## Fehlerbehebung

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

## Referenzen

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [Pydantic v2](https://docs.pydantic.dev/latest/)
- [Alembic](https://alembic.sqlalchemy.org/)
- [python-jose](https://github.com/mpdavis/python-jose)
- [passlib](https://passlib.readthedocs.io/)
