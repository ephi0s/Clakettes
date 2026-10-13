# Clakettes Backend — Documentation technique

[ES](../es/BACKEND.md) · [EN](../en/BACKEND.md) · [FR](BACKEND.md) · [DE](../de/BACKEND.md) · [IT](../it/BACKEND.md) · [CA](../ca/BACKEND.md) · [EU](../eu/BACKEND.md) · [GL](../gl/BACKEND.md) · [OC](../oc/BACKEND.md)

Backend FastAPI pour la plateforme de gestion de festivals de cinéma Clakettes.

## Démarrage rapide

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

### Structure en couches

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

### Principes clés de conception

1. **Routers légers** — délèguent aux services
2. **Services sans état** — reçoivent `db: Session` par injection de dépendances
3. **Les modèles héritent de `BaseModel`** — `id`, `created_at`, `updated_at` dans toutes les entités
4. **Enums centralisés** — `app/enums.py` partagé entre modèles et schémas
5. **CRUD de base générique** — `BaseService` dans `app/services/base_service.py`

---

## Configuration

Toute la configuration se fait via `backend/.env` (chargé par `pydantic-settings`) :

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./clakettes.db` | SQLAlchemy connection string |
| `SECRET_KEY` | (required, no default) | JWT signing key |
| `JWT_ISSUER` | `clakettes` | JWT issuer claim |
| `JWT_AUDIENCE` | `clakettes-api` | JWT audience claim |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token TTL |
| `CORS_ORIGINS` | `None` (→ `["*"]`) | Comma-separated allowed origins |
| `PORT_BACKEND` | `8000` | Server port (used by Docker/start scripts) |

**Exemple de `.env` en production :**

```env
DATABASE_URL=mariadb+pymysql://user:pass@db:3306/clakettes_db
SECRET_KEY=super-secret-64-char-urlsafe-string
JWT_ISSUER=clakettes
JWT_AUDIENCE=clakettes-api
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=https://app.example.com,https://admin.example.com
```

Générez une clé `SECRET_KEY` robuste :

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

---

## Base de données

### Compatibilité avec deux bases de données

| Environment | Database | Connection String |
|-------------|----------|-------------------|
| Development | SQLite | `sqlite:///./data/clakettes.db` |
| Production | MariaDB | `mariadb+pymysql://user:pass@host:3306/db` |

### Modèle de base

Tous les modèles héritent de `BaseModel` (`app/models/base.py`) :

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

**Notes de migration (SQLite ↔ MariaDB) :**
- SQLite `INTEGER PRIMARY KEY` → MariaDB `INT AUTO_INCREMENT`
- SQLite `TEXT` → MariaDB `TEXT`/`VARCHAR`
- SQLite `DATETIME` (stored as TEXT) → MariaDB native `DATETIME`
- Les scripts d'exportation/importation dans `backend/tools/` gèrent les conversions de types

### Résumé des modèles (31 modèles)

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

Consultez [DATABASE.md](DATABASE.md) pour la documentation complète du schéma avec diagrammes ER.

---

## Authentification

### JWT + Suivi de sessions

| Token Type | Format | TTL | Storage |
|------------|--------|-----|---------|
| **Access Token** | JWT (HS256) | 30 min (configurable) | Client memory |
| **Refresh Token** | Opaque (SHA-256 hash in DB) | 30 days | `UserSession.refresh_token_hash` |

### Flux de connexion

```
POST /api/users/login
  {username, password}
→ 200 {access_token, refresh_token, token_type: "bearer", user: {...}}
```

### Usage du token

```http
Authorization: Bearer <access_token>
```

### Flux de renouvellement

```
POST /api/users/refresh
  {refresh_token}
→ 200 {access_token, refresh_token, token_type: "bearer"}
```

### Gestion des sessions

- `GET /api/auth/sessions` — Lister les sessions actives
- `DELETE /api/auth/sessions/{session_id}` — Révoquer la session
- La session est créée à la connexion avec information du dispositif (IP, UA, nom)
- Les tokens sont pivotés au renouvellement ; les anciens tokens restent invalidés

### Hachage des mots de passe

- **bcrypt** via `passlib` (rounds=12)
- Hash gardé dans `User.password_hash`
- Vérifié via `pwd_context.verify(plain, hash)`

### Limite de requêtes

- **100 requests / 60 seconds** par IP (avec appui sur SQLite)
- Appliquée via `RateLimitMiddleware` dans `main.py`
- Désactivée quand la variable d'environnement `TESTING=true` est établie

---

## Endpoints de l'API

### Registre des routers (`app/main.py`)

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

Total : 33 routers

### Pagination et filtrage

Paramètres de requête standard dans les endpoints de liste :

```
GET /api/festivals/?page=1&size=20&search=cannes&is_active=true
```

Enveloppe de réponse :

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

## Chat en temps réel

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

### Types de message

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

- Échange de clés X25519 via `/api/users/{id}/keys`
- Clés publiques gardées dans `UserKey` (une active par utilisateur)
- Chiffrement/déchiffrement dans le frontend (`e2ee_service.dart`)

---

## Envoi de fichiers

### Envoi d'avatar

```
POST /api/uploads/avatar
Content-Type: multipart/form-data
Authorization: Bearer <token>

file: <image/*>
```

- Gardé dans `backend/uploads/avatars/{user_id}_{uuid}.{ext}`
- Servi de façon statique sur `/uploads/avatars/...`
- Taille maximale : 10 MB (appliqué par `RequestSizeLimitMiddleware`)

---

## Endpoints d'administration

Requiert `role=admin` (vérifié dans `admin_service.py`) :

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

**Configuration de tests** (`pyproject.toml` / `pytest.ini`) :

```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_functions = test_*
```

**Fixtures** (`tests/conftest.py`) :
- `db_session` — session SQLite en mémoire
- `client` — `AsyncClient` (httpx) contre l'app de tests
- `auth_headers` — en-têtes déjà authentifiées

**Note** : Il y a un `conftest.py` dupliqué dans `tests/services/` — ils devraient l'unifier.

---

## Lint et format

```bash
# Check
ruff check .

# Fix auto-fixable
ruff check . --fix

# Format
ruff format .
```

**Configuration** (`pyproject.toml`) :

```toml
[tool.ruff]
line-length = 120
target-version = "py312"
select = ["E", "F", "I", "UP", "B", "C4", "PTH", "T20", "SIM", "ARG"]
ignore = ["E501", "SIM102", "SIM103"]
```

---

## Flux de développement

### Développement local

```bash
# Terminal 1: Backend
cd backend
python -m uvicorn app.main:app --reload

# Terminal 2: Frontend (if needed)
cd frontend
flutter run -d web-server --web-port 3000 --dart-define=BACKEND_URL=http://localhost:8000/api
```

### Développement avec Docker

```bash
# From project root
docker compose up        # Backend:8000, Frontend:3000
docker compose --profile db up  # + MariaDB:3306
```

### Charge initiale de la base de données

Pas de script de seed : en développement l'app crée l'admin initial (`admin` /
`setup`, changez le mot de passe en entrant) et les tables via `create_all`. En production les
données arrivent par l'API et le schéma uniquement via Alembic.

### Commandes habituelles

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

## Structure du projet

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

Docs dans `docs/fr/BACKEND.md` (ce fichier) et `docs/fr/DATABASE.md`.

---

## Déploiement

### Docker (Production)

```yaml
# docker-compose.yml uses --profile prod
docker compose --profile prod up -d
```

Services :
- `backend-prod` — FastAPI (workers Uvicorn) sur :8000
- `frontend-prod` — Nginx + Flutter web sur :80
- `db` — MariaDB 11 (vérification d'état)

Profils disponibles :
- `dev` (par défaut) : serveurs de développement backend et frontend
- `db` : ajoute le conteneur MariaDB
- `prod` : pile de production avec nginx

### Variables d'environnement (Production)

```env
DATABASE_URL=mariadb+pymysql://user:pass@db:3306/clakettes_db
SECRET_KEY=<64-char-urlsafe>
CORS_ORIGINS=https://app.example.com
```

### Vérification d'état

```bash
curl http://localhost:8000/health
# {"status": "healthy"}
```

---

## Liste de contrôle de sécurité

- [ ] Changez `SECRET_KEY` en production
- [ ] Établissez `CORS_ORIGINS` sur des domaines spécifiques
- [ ] Utilisez MariaDB (pas SQLite) en production
- [ ] Activez HTTPS (proxy inverse : nginx/Traefik)
- [ ] Configurez les hôtes permis dans `TrustedHostMiddleware`
- [ ] Pivotez les clés JWT périodiquement
- [ ] Surveillez les registres du limiteur de requêtes
- [ ] Révisez le mot de passe de l'utilisateur admin après la première connexion

---

## Étendre l'API

### Ajouter une ressource nouvelle

1. **Modèle** — `app/models/new_resource.py` (hérite `BaseModel`)
2. **Schéma** — `app/schemas/new_resource.py` (Pydantic)
3. **Service** — `app/services/new_resource_service.py` (étend `BaseService`)
4. **Router** — `app/routers/new_resource.py` (inclure dans `main.py`)
5. **Migration** — `alembic revision --autogenerate -m "add new_resource"`
6. **Tests** — `tests/test_new_resource.py`

### Ajouter un endpoint personnalisé à un router existant

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

## Résolution de problèmes

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

## Références

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [Pydantic v2](https://docs.pydantic.dev/latest/)
- [Alembic](https://alembic.sqlalchemy.org/)
- [python-jose](https://github.com/mpdavis/python-jose)
- [passlib](https://passlib.readthedocs.io/)
