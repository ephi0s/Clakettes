# Clakettes Backend — Documentacion tecnica

[ES](../es/BACKEND.md) · [EN](../en/BACKEND.md) · [FR](../fr/BACKEND.md) · [DE](../de/BACKEND.md) · [IT](../it/BACKEND.md) · [CA](../ca/BACKEND.md) · [EU](../eu/BACKEND.md) · [GL](../gl/BACKEND.md) · [CA](BACKEND.md) · [OC](BACKEND.md)

Backend FastAPI per la plataforma de gestion de festivals de cinema Clakettes.

## Arrancada rapida

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
Routers (FastAPI) → Services (Logica de negocis) → Models (SQLAlchemy)
```

| Capa | Ubicacion | Responsabilitat |
|------|-----------|----------------|
| Routers | `app/routers/` | Endpoints HTTP, validacion de solicitud/resposta, paginacion |
| Services | `app/services/` | Logica de negocis, operacions CRUD, preocupacions transversals |
| Models | `app/models/` | Models ORM SQLAlchemy, esquema DB |
| Schemas | `app/schemas/` | Models Pydantic per solicitud/resposta |
| Auth | `app/auth.py` | JWT, sessions, hash de contrasenias |
| Config | `app/config.py` | Pydantic Settings des de `.env` |
| Database | `app/database.py` | Motor, sessio factory, dependencia `get_db()` |

### Principis claus de diseny

1. Routers lleugers — delegan en services
2. Services sens estat — rebene `db: Session` per injectio de dependencias
3. Los models heredan de `BaseModel` — `id`, `created_at`, `updated_at` en totes les entitats
4. Enums centralitzats — `app/enums.py` compartit entre models i esquemes
5. Base CRUD generica — `BaseService` en `app/services/base_service.py`

---

## Configuracion

Tota la configuracion fa per `backend/.env` (carregat per `pydantic-settings`):

| Variable | Default | Descripcio |
|----------|---------|------------|
| `DATABASE_URL` | `sqlite:///./clakettes.db` | String de conexion SQLAlchemy |
| `SECRET_KEY` | (requerit, sens default) | Clau de firma JWT |
| `JWT_ISSUER` | `clakettes` | Reclamacio emissor JWT |
| `JWT_AUDIENCE` | `clakettes-api` | Reclamacio audiencia JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | TLL del token d'acces |
| `CORS_ORIGINS` | `None` (→ `["*"]`) | Origenes permises separades per comes |
| `PORT_BACKEND` | `8000` | Port del servidor (usat per Docker/scripts d'arrancada) |

**Exemple de `.env` per a productiu:**

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

## Base de datos

### Compatibilitat amb dos basses de datos

| Entorn | Base de datos | String de conexion |
|--------|---------------|--------------------|
| Desenvolupament | SQLite | `sqlite:///./data/clakettes.db` |
| Productiu | MariaDB | `mariadb+pymysql://user:pass@host:3306/db` |

### Model base

Totes les models heredan de `BaseModel` (`app/models/base.py`):

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

# Crea una nova migracio despres de cambis al model
alembic revision --autogenerate -m "descripcio"

# Aplica migracions
alembic upgrade head

# Torna enrere
alembic downgrade -1

# Revisio actual
alembic current
```

**Notes de migracio (SQLite ↔ MariaDB):**
- SQLite `INTEGER PRIMARY KEY` → MariaDB `INT AUTO_INCREMENT`
- SQLite `TEXT` → MariaDB `TEXT`/`VARCHAR`
- SQLite `DATETIME` (emmagatzemat com a text) → MariaDB `DATETIME` natiu
- Los scripts d'exportacio/importacio en `backend/tools/` gestionan les conversions de tipus automaticament

Consulte [DATABASE.md](DATABASE.md) per la documentacion completa de l'esquema amb diagrames ER.

---

## Autenticacio

### JWT + Seguito de sessions

| Tipus de token | Format | TLL | Emmagatzematge |
|----------------|--------|-----|----------------|
| Access Token | JWT (HS256) | 30 min (configurable) | Memoria del client |
| Refresh Token | Opac (hash SHA-256 en BD) | 30 dies | `UserSession.refresh_token_hash` |

### Flux d'inici de sessio

```
POST /api/users/login
  {username, password}
→ 200 {access_token, refresh_token, token_type: "bearer", user: {...}}
```

### Us del token

```http
Authorization: Bearer <access_token>
```

### Flux de renovacio

```
POST /api/auth/refresh
  {refresh_token}
→ 200 {access_token, refresh_token, token_type: "bearer"}
```

### Gestio de sessions

- `GET /api/auth/sessions` — Llista les sessions actives
- `DELETE /api/auth/sessions/{session_id}` — Revoca la sessio
- La sessio es crea al iniciar sessio amb informacio del dispositiu (IP, UA, nom)
- Los tokens rotan a la renovacio; los tokens antics es invaliden

### Hash de contrasenias

- **bcrypt** via `passlib` (rounds=12)
- Hash emmagatzemat en `User.password_hash`
- Verificat via `pwd_context.verify(plain, hash)`

### Limite de peticions

- **100 peticions / 60 segons** per IP (copia de seguretat en SQLite)
- Aplicat per `RateLimitMiddleware` en `main.py`
- Desactivat quan s'estableix la variable d'entorn `TESTING=true`

---

## Endpoints de l'API

### Registre de routers (`app/main.py`)

| Router | Prefix | Etiquetes | Descripcio |
|--------|--------|-----------|------------|
| `festivals` | `/api/festivals` | festivals | CRUD, cerca, membres |
| `users` | `/api/users` | users | CRUD, perfil, pujada d'avatar |
| `auth` | `/api/users` | auth | Inici de sessio, renovacio, registre |
| `auth_sessions` | `/api/auth` | auth | Llista/revocacio de sessions |
| `shortfilms` | `/api/shortfilms` | shortfilms | CRUD, vinculacio festival |
| `chat` | `/api/chat` | chat | Missatges, endpoint WS |
| `user_festival` | `/api/festivals` | user-festival | Unir-se/sortir, membres |
| `uploads` | `/api/uploads` | uploads | Pujada d'avatar |
| `search` | `/api/search` | search | Cerca global |
| `admin` | `/api/admin` | admin | Estadistiques, taules, audit-log, reset |
| `notifications` | `/api/notifications` | notifications | CRUD, comptador de no llegits |
| `roles` | `/api` | roles | Rols, grups, dependencies, conflictes |
| `participant_tags` | `/api` | participant-tags | Etiquetes, configuracio festival |
| `user_roles` | `/api` | user-roles | Assignacions de rols |
| `user_aliases` | `/api` | user-aliases | Alias de visualitzacio |
| `validation_rules` | `/api` | validation-rules | Validacio dinamica de formulari |
| `registration_forms` | `/api` | registration-forms | Fluxos de registre festival |
| `role_groups` | `/api` | role-groups | Agrupacio de rols |
| `committees` | `/api` | committees | Comitats festival |
| `delegations` | `/api` | delegations | Delegacions de rols |
| `events` | `/api` | events | Esdeveniments, tipus d'entrada, asientos, reserves |
| `channels` | `/api/channels` | channels | Canals de chat |
| `keys` | `/api/users` | e2ee | Gestion de claus publices E2EE |
| `locations` | `/api/locations` | locations | Geolocalitzacio, mapes |
| `location_tags` | `/api/locations/{location_id}/tags` | location-tags | Etiquetes de ubicacio |
| `location_images` | `/api/locations/{location_id}/images` | location-images | Imatges de ubicacio |
| `location_relations` | `/api/locations/{location_id}/relations` | location-relations | Relacions de ubicacio |
| `shortfilm_locations` | `/api/shortfilms/{shortfilm_id}/locations` | shortfilm-locations | Ubicacions de curtmetratge |
| `form_definitions` | `/api` | forms | Constructor de formulari |
| `federation` | `/api/federation` | federation | manifest, directori, nodes, informes, webfinger |
| `jury_votes` | `/api` | jury-votes | Vot del jurat (fasa 5) |
| `calendar` | `/api/calendar` | calendar | Agenda, CalDAV, configuracio |
| `badges` | `/api` | badges | Insignies, assignacions, elegibilitat |
| `posts` | `/api` | posts | Publicacions socials, respostes, moderacio |
| `payments` | `/api` | payments | Pagar, confirmar, reembolsar, webhook |
| `festival_rulebooks` | `/api/festivals/{festival_id}/rulebooks` | rulebooks | Reguladors del festival |
| `user_blocks` | `/api` | user-blocks | Bloc d'usagis |
| `moderation_reports` | `/api` | moderation-reports | Informes de moderacio |
| `node_policies` | `/api` | node-policies | Politiques de nodes de federacio |

Total: 38 routers amb `APIRouter` (40 fitxers de router, 2 auxiliars sens router).

### Paginacio i filtratge

Parametres de consulta estandard als endpoints de llistat:

```
GET /api/festivals/?page=1&size=20&search=cannes&is_active=true
```

Somiatge de resposta:

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

| Component | Descripcio |
|-----------|------------|
| `WebSocketChatBackend` | Implementacio per defecte (connexions en memoria) |
| `chat_backend_registry` | Registre singular per canvi de backend |
| `ConnectionManager` | Gestiona els mapeigats usagi↔WebSocket |

### Endpoints

| Metode | Ruta | Descripcio |
|--------|------|------------|
| `GET` | `/api/chat/ws` | Connexio WebSocket (auth via query `token`) |
| `POST` | `/api/chat/messages` | Enviar missatge (fallback REST) |
| `GET` | `/api/chat/messages` | Historial paginat |
| `PATCH` | `/api/chat/messages/{id}/read` | Marcar com llegit |

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

- Intercanvi de claus X25519 a través de `/api/users/{id}/keys`
- Claus publices emmagatzemades en `UserKey` (una clau activa per usagi)
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
- Servit de manera estatica a `/uploads/avatars/...`
- Mida maxima: 10 MB (aplicat per `RequestSizeLimitMiddleware`)

---

## Endpoints d'administracio

Requerix `role=admin` (verificat a `admin_service.py`):

| Endpoint | Descripcio |
|----------|------------|
| `GET /api/admin/stats` | Estadistiques de la plataforma |
| `GET /api/admin/tables` | Nombre de files per taula |
| `GET /api/admin/audit-log` | Pista d'auditoria (filtres `action`, `actor_user_id`) |
| `POST /api/admin/reset` | `drop_all + create_all` (sola no-produccio) |

---

## Provades

```bash
cd backend

# Executar totes les provades
python -m pytest tests/ -x -q --tb=short

# Executar amb cobertura
python -m pytest tests/ --cov=app --cov-report=term-missing

# Fitxer de provades especificar
python -m pytest tests/test_festivals.py -v
```

**Configuracio de provades** (`pyproject.toml` / `pytest.ini`):

```ini
[tool.pytest.ini_options]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_functions = test_*
```

**Fixures** (`tests/conftest.py`):
- `db_session` — sessio SQLite en memoria
- `client` — `AsyncClient` (httpx) contra l'aplicacio de provades
- `auth_headers` — capçaleres ja autenticades

---

## Lint i formatatge

```bash
# Comprovar
ruff check .

# Corregir auto-corregible
ruff check . --fix

# Formatar
ruff format .
```

**Configuracio** (`pyproject.toml`):

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

# Terminal 2: Frontend (si cal)
cd frontend
flutter run -d web-server --web-port 3000 --dart-define=BACKEND_URL=http://localhost:8000/api
```

### Desenvolupament amb Docker

```bash
# Des de l'arrel del projècte
docker compose up        # Backend:8000, Frontend:3000
docker compose --profile db up  # + MariaDB:3306
```

### Carrega inicial de la base de datos

No hi ha script de seed: en desenvolupament l'aplicacio crea l'admin inicial (`admin` / `setup`, canviar la contrasenya a l'entrar) e les taules mediante `create_all`. En productiu les dades arriben per l'API e l'esquema solament per Alembic.

### Comands habituals

```bash
# Generar adaptadors Hive (frontend)
cd frontend && flutter pub run build_runner build --delete-conflicting-outputs

# Executar migracions
cd backend && alembic upgrade head

# Crear migracio
cd backend && alembic revision --autogenerate -m "add column x"

# Exportar SQLite → MariaDB
cd backend && python tools/export_sqlite_to_mariadb.py

# Importar MariaDB → SQLite
cd backend && python tools/import_mariadb_to_sqlite.py
```

---

## Estructura del projècte

```
backend/
├── app/
│   ├── models/              # 40 models SQLAlchemy (+ base.py)
│   ├── schemas/             # 37 esquemes Pydantic
│   ├── services/            # 43 serveis de logica de negocis
│   ├── routers/             # 40 routers API (38 amb APIRouter)
│   ├── chat_backend/        # Implementacio WebSocket de xat
│   ├── auth.py              # JWT + autenticacio de sessio
│   ├── config.py            # Pydantic Settings
│   ├── database.py          # Motor, SessionLocal, get_db()
│   ├── main.py              # Aplicacio FastAPI, middleware, routers
│   ├── rate_limiter.py      # Limitador de velocitat SQLite
│   ├── enums.py             | Enums compartits
│   └── scripts/             # Scripts de seed/migracio
├── alembic/                 # Migracions (36 versions)
├── tools/                   # Scripts d'exportacio/importacio
├── tests/                   # Provades pytest (47 fitxers, 1439 funcions de provades)
├── uploads/                 | Fitxers pujats estatics
├── .env.example             | Plantilla de configuracio
├── requirements.txt         | Dependencies de productiu
├── requirements-dev.txt     | Dependencies de desenvolupament (pytest, ruff)
├── pyproject.toml           | Configuracio Ruff, pytest
└── pytest.ini               | Configuracio pytest
```

Documentacion a `docs/oc/BACKEND.md` (aquest fitxer) e `docs/oc/DATABASE.md`.

---

## Desplegament

### Docker (Productiu)

```yaml
# docker-compose.yml usa --profile prod
docker compose --profile prod up -d
```

Serveis:
- `backend-prod` — FastAPI (treballadors Uvicorn) a :8000
- `frontend-prod` — Nginx + Flutter web a :80
- `db` — MariaDB 11 (comprovacio d'estat)

Perfils dispoñibles:
- `dev` (per defecte): servidors de desenvolupament backend i frontend
- `db`: afegeix el contenidor MariaDB
- `prod`: pila de productiu amb nginx

### Variables d'entorn (Productiu)

```env
DATABASE_URL=mariadb+pymysql://user:pass@db:3306/clakettes_db
SECRET_KEY=<64-char-urlsafe>
CORS_ORIGINS=https://app.example.com
```

### Comprovacio d'estat

```bash
curl http://localhost:8000/health
# {"status": "healthy"}
```

---

## Checklist de seguretat

- [ ] Canviatz `SECRET_KEY` a productiu
- [ ] Estatziatz `CORS_ORIGINS` a dominis specifics
- [ ] Usetz MariaDB (no SQLite) a productiu
- [ ] Habilitezatz HTTPS (proxy invers: nginx/Traefik)
- [ ] Configurezzatz els hosts permesos en `TrustedHostMiddleware`
- [ ] Rotatzatz las claus JWT periodicamente
- [ ] Vigilezzatz los registres del limitador de velocitat
- [ ] Revisatzatz la contrasenya de l'usagi admin despres del primer acces

---

## Ampliar l'API

### Afegir un recurs nou

1. **Model** — `app/models/new_resource.py` (hereda `BaseModel`)
2. **Esquema** — `app/schemas/new_resource.py` (Pydantic)
3. **Servei** — `app/services/new_resource_service.py` (exten `BaseService`)
4. **Router** — `app/routers/new_resource.py` (incloure a `main.py`)
5. **Migracio** — `alembic revision --autogenerate -m "add new_resource"`
6. **Provades** — `tests/test_new_resource.py`

### Afegir un endpoint personalitzat a un router existent

```python
# Al fitxer del router
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

## Resolucio de problemas

| Problema | Solucio |
|----------|---------|
| `ModuleNotFoundError: app` | Executezatz des de `backend/` o `PYTHONPATH=backend` |
| `sqlite3.OperationalError: database is locked` | Un sol escriptor; assegurezzatz que no hi hagi processos obsolets |
| `alembic: Can't locate revision` | Esborrezatz `alembic/versions/`, executezzatz `alembic revision --autogenerate -m "init"` |
| `JWTError: Signature verification failed` | Incompatibilitat de `SECRET_KEY` entre l'entorn e el proces en execucio |
| `429 Too Many Requests` | Limite de velocitat assolita; esperezzatz 60s o establezzatz `TESTING=true` |
| WebSocket 403 | Token expirat; usezzatz un token d'acces valid en `?token=` |
| Error CORS | Comprovezatz que `CORS_ORIGINS` en `.env` coincideix amb l'origen del frontend |

---

## Referencies

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [Pydantic v2](https://docs.pydantic.dev/latest/)
- [Alembic](https://alembic.sqlalchemy.org/)
- [python-jose](https://github.com/mpdavis/python-jose)
- [passlib](https://passlib.readthedocs.io/)