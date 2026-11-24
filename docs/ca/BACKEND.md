# Clakettes Backend — Documentació tècnica

[ES](../es/BACKEND.md) · [EN](../en/BACKEND.md) · [FR](../fr/BACKEND.md) · [DE](../de/BACKEND.md) · [IT](../it/BACKEND.md) · [CA](BACKEND.md) · [EU](../eu/BACKEND.md) · [GL](../gl/BACKEND.md) · [OC](../oc/BACKEND.md)

Backend FastAPI per a la plataforma de gestió de festivals de cinema Clakettes.

## Arrancada ràpida

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
Routers (FastAPI) → Serveis (Lògica de negoci) → Models (SQLAlchemy)
```

| Capa | Ubicació | Responsabilitat |
|------|----------|-----------------|
| **Routers** | `app/routers/` | Endpoints HTTP, validació de sol·licitud/resposta, paginació |
| **Serveis** | `app/services/` | Lògica de negoci, operacions CRUD, preocupacions transversals |
| **Models** | `app/models/` | Models ORM SQLAlchemy, esquema BD |
| **Esquemes** | `app/schemas/` | Models Pydantic per sol·licitud/resposta |
| **Autenticació** | `app/auth.py` | JWT, sessions, hash de contrasenyes |
| **Configuració** | `app/config.py` | Pydantic Settings des de `.env` |
| **Base de dades** | `app/database.py` | Motor, fàbrica de sessions, dependència `get_db()` |

### Principis clau de disseny

1. **Routers lleugers** — deleguen als serveis
2. **Serveis sense estat** — rebren `db: Session` mitjançant injecció de dependències
3. **Els models hereten de `BaseModel`** — `id`, `created_at`, `updated_at` a totes les entitats
4. **Enums centralitzats** — `app/enums.py` compartit entre models i esquemes
5. **Base CRUD genèrica** — `BaseService` a `app/services/base_service.py`

---

## Configuració

Tota la configuració es realitza a través de `backend/.env` (carregat per `pydantic-settings`):

| Variable | Valor per defecte | Descripció |
|----------|-------------------|------------|
| `DATABASE_URL` | `sqlite:///./clakettes.db` | String de connexió SQLAlchemy |
| `SECRET_KEY` | (requerit, sense valor per defecte) | Clau de signat JWT |
| `JWT_ISSUER` | `clakettes` | Reclamació d'emissor JWT |
| `JWT_AUDIENCE` | `clakettes-api` | Reclamació d'audiència JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | TLL del token d'accés |
| `CORS_ORIGINS` | `None` (→ `["*"]`) | Orígens permesos separats per comes |
| `APP_ENV` | `development` | `production` exigeix `SECRET_KEY` robusta, CORS explícit i esquema via Alembic |
| `TESTING` | desactivat | `1/true/yes/on` desactiva rate limits i auto-migració (`app.config.is_testing()`) |
| `PUBLIC_BASE_URL` | `None` | Origen públic del node (manifest, bundles, ICS absolut) |
| `MTLS_REQUIRED` | `False` | Exigeix mTLS verificat a `/api/federation` |
| `MTLS_CA_BUNDLE_PATH` | `None` | CA arrel per validar certificats de clients |
| `MTLS_CLIENT_CERT_PATH`, `MTLS_CLIENT_KEY_PATH` | `None` | Certificat i clau propis (firma del manifest RSA-SHA256) |
| `RATE_LIMITS_DB_PATH` | `backend/rate_limits.db` | Fitxer SQLite del limitador de peticions |
| `SKIP_AUTO_MIGRATE` | desactivat | `1/true/yes/on` omite `alembic upgrade head` a l'arrancada |
| `PAYMENTS_PROVIDER`, `MOCK_WEBHOOK_SECRET`, `MOCK_PAYMENTS_FORCE_FAIL` | `mock`, buit, `False` | Proveïdor de pagaments mock i secret de webhook |
| `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` | buit | Credencials Stripe (SDK perezós) |
| `REDSYS_MERCHANT_CODE`, `REDSYS_TERMINAL`, `REDSYS_SECRET_KEY`, `REDSYS_SANDBOX`, `REDSYS_CURRENCY` | —, `1`, buit, `True`, `978` | Signatura HMAC Redsys i sandbox |
| `PORT_BACKEND` | `8000` | Port del servidor (utilitzat per Docker/scripts d'arrancada) |

**Exemple de `.env` per a producció:**

```env
DATABASE_URL=mariadb+pymysql://user:pass@db:3306/clakettes_db
SECRET_KEY=super-secret-64-char-urlsafe-string
JWT_ISSUER=clakettes
JWT_AUDIENCE=clakettes-api
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=https://app.example.com,https://admin.example.com
```

Generiu una clau `SECRET_KEY` robusta:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

---

## Base de dades

### Compatibilitat amb dues bases de dades

| Entorn | Base de dades | String de connexió |
|--------|---------------|--------------------|
| Desenvolupament | SQLite | `sqlite:///./data/clakettes.db` |
| Producció | MariaDB | `mariadb+pymysql://user:pass@host:3306/db` |

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

# Crea una nova migració després de canvis al model
alembic revision --autogenerate -m "description"

# Aplica migracions
alembic upgrade head

# Retrocedeix
alembic downgrade -1

# Revisió actual
alembic current
```

**Notes de migració (SQLite ↔ MariaDB):**
- SQLite `INTEGER PRIMARY KEY` → MariaDB `INT AUTO_INCREMENT`
- SQLite `TEXT` → MariaDB `TEXT`/`VARCHAR`
- SQLite `DATETIME` (emmagatzemat com a text) → MariaDB `DATETIME` natiu
- Els scripts d'exportació/importació a `backend/tools/` gestionen les conversions de tipus automàticament

Consulteu [DATABASE.md](DATABASE.md) per a la documentació completa de l'esquema amb diagrames ER.

---

## Autenticació

### JWT + Seguiment de sessions

| Tipus de token | Format | TLL | Emmagatzematge |
|----------------|--------|-----|----------------|
| **Token d'accés** | JWT (HS256) | 30 min (configurable) | Memòria del client |
| **Token de renovació** | Opaque (hash SHA-256 a la BD) | 30 dies | `UserSession.refresh_token_hash` |

### Fluix d'inici de sessió

```
POST /api/users/login
  {username, password}
→ 200 {access_token, refresh_token, token_type: "bearer", user: {...}}
```

### Ús del token

```http
Authorization: Bearer <access_token>
```

### Fluix de renovació

```
POST /api/auth/refresh
  {refresh_token}
→ 200 {access_token, refresh_token, token_type: "bearer"}
```

### Gestió de sessions

- `GET /api/auth/sessions` — Llista les sessions actives
- `DELETE /api/auth/sessions/{session_id}` — Revoca la sessió
- La sessió es crea a l'inici de sessió amb informació del dispositiu (IP, UA, nom)
- Els tokens es roten a la renovació; els tokens antics es invaliden

### Hash de contrasenyes

- **bcrypt** directe (`bcrypt.hashpw` + `bcrypt.gensalt()`), sense `passlib`
- Hash emmagatzemat a `User.password_hash`
- Verificat via `bcrypt.checkpw(plain, hash)` (`app/services/user_service.py`)

### Límit de peticions

- **100 peticions / 60 segons** per IP (còpia de seguretat SQLite)
- Aplicat per `RateLimitMiddleware` a `main.py`
- Desactivat amb `TESTING` ∈ {1, true, yes, on} (helper `app.config.is_testing()`), inclòs el limitador de refresh 20/60 s a `routers/auth_sessions.py`

---

## Endpoints de l'API

### Registre de routers (`app/main.py`)

| Router | Prefix | Etiquetes | Descripció |
|--------|--------|-----------|------------|
| `festivals` | `/api/festivals` | festivals | CRUD, cerca, membres |
| `users` | `/api/users` | users | CRUD, perfil, pujada d'avatar |
| `auth` | `/api/users` | auth | Inici de sessió, renovació, registre |
| `auth_sessions` | `/api/auth` | auth | Llista/revocació de sessions |
| `shortfilms` | `/api/shortfilms` | shortfilms | CRUD anidat a `/api/festivals/{festival_id}/shortfilms` (GET/POST de llista i GET/PUT/DELETE de detall, filtre `?contest_type=`); els endpoints plans segueixen disponibles però marcats `deprecated=True` |
| `chat` | `/api/chat` | chat | Missatges, endpoint WS |
| `user_festival` | `/api/festivals` | user-festival | Unir-se/sortir, membres |
| `uploads` | `/api/uploads` | uploads | Pujada multipart d'avatar, thumbnail, vídeo, document i imatge de xat; retorna rutes relatives `/uploads/...` |
| `search` | `/api/search` | search | Cerca global |
| `admin` | `/api/admin` | admin | Estadístiques, taules, audit-log, reset |
| `notifications` | `/api/notifications` | notifications | CRUD, comptador de no llegits |
| `roles` | `/api` | roles | Rols, grups, dependències, conflictes |
| `participant_tags` | `/api` | participant-tags | Etiquetes, configuració festival |
| `user_roles` | `/api` | user-roles | Assignacions de rols |
| `user_aliases` | `/api` | user-aliases | Alias de visualització |
| `validation_rules` | `/api` | validation-rules | Validació dinàmica de formularis |
| `registration_forms` | `/api` | registration-forms | Fluxos de registre festival |
| `role_groups` | `/api` | role-groups | Agrupació de rols |
| `committees` | `/api` | committees | Comitats festival |
| `delegations` | `/api` | delegations | Delegacions de rols |
| `events` | `/api` | events | Esdeveniments, tipus d'entrada, seies, reserves |
| `channels` | `/api/channels` | channels | Canals de xat |
| `keys` | `/api/users` | e2ee | Gestió de claus públiques E2EE |
| `locations` | `/api/locations` | locations | Geolocalització, mapes |
| `location_tags` | `/api/locations/{location_id}/tags` | location-tags | Etiquetes de ubicació |
| `location_images` | `/api/locations/{location_id}/images` | location-images | Imatges de ubicació |
| `location_relations` | `/api/locations/{location_id}/relations` | location-relations | Relacions de ubicació |
| `shortfilm_locations` | `/api/shortfilms/{shortfilm_id}/locations` | shortfilm-locations | Ubicacions de curtmetratge |
| `form_definitions` | `/api` | forms | Constructor de formularis |
| `federation` | `/api/federation` | federation | manifest, directori, nodes, informes, webfinger, `whoami`, JWKS, peers/verify, mTLS |
| `federation_chat_bridge` | `/api/federation/chat` | federation-chat-bridge | Bridge de xat signat RS256, configuració i missatges |
| `federation_events` | `/api/federation/events` | federation-events | SSE amb `token` obligatori, publicació i reintent |
| `federation_portability` | `/api/federation/portability` | federation-portability | Bundles, imports, migració i redirects |
| `federation_resilience` | `/api/federation/resilience` | federation-resilience | Health, heartbeat, mètriques, revocació i incident |
| `chat_moderation` | `/api/chat/moderation` | chat-moderation | Reportes, silenciaments, moderació i límits |
| `jury_votes` | `/api` | jury-votes | Vot del jurat (fase 5) |
| `calendar` | `/api/calendar` | calendar | Agenda, CalDAV, configuració |
| `badges` | `/api` | badges | Insígnies, assignacions, elegibilitat |
| `posts` | `/api` | posts | Publicacions socials, respostes, moderació |
| `payments` | `/api` | payments | Pagar, confirmar, reembolsar, webhook |
| `festival_rulebooks` | `/api/festivals/{festival_id}/rulebooks` | rulebooks | Reguladors del festival |
| `user_blocks` | `/api` | user-blocks | Bloc d'usuaris (propietari o admin) |



### Paginació i filtratge

Paràmetres de consulta estàndard als endpoints de llistat:

```
GET /api/festivals/?page=1&size=20&search=cannes&is_active=true
```

Somiatre de resposta:

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

| Component | Descripció |
|-----------|------------|
| `WebSocketChatBackend` | Implementació per defecte (connexions en memòria) |
| `chat_backend_registry` | Registre singleton per canvi de backend |
| `ConnectionManager` | Gestiona els mapatges usuari↔WebSocket |

### Endpoints

| Mètode | Ruta | Descripció |
|--------|------|------------|
| `GET` | `/api/chat/ws` | Connexió WebSocket (auth via query `token`) |
| `POST` | `/api/chat/messages` | Enviar missatge (fallback REST) |
| `GET` | `/api/chat/messages` | Historial paginat |
| `PUT` | `/api/chat/messages/{message_id}/read` | Marcar com llegit |

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

- Intercanvi de claus ECDH P-256 a través de `POST /api/users/me/public-key` i `GET /api/users/{user_id}/public-key` (`routers/keys.py`)
- Claus públiques emmagatzemades a `UserKey` (una clau activa per usuari)
- Cifrat/descifrat AES-GCM al frontend (`services/crypto_utils.dart`)

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
- Servit de manera estàtica a `/uploads/avatars/...`
- Mida màxima: 5 MB per a imatges (`MAX_IMAGE_SIZE` a `routers/uploads.py`); el límit global del cos segueix sent 10 MB

### Totes les pujades

- Els endpoints `avatar`, `thumbnail`, `video`, `document` i `chat-image` retornen una ruta relativa `/uploads/<carpeta>/<archivo>`; el client la resol amb `resolveMediaUrl()` contra el node actiu.
- Si falta el content-type o arriba `application/octet-stream`, `uploads._sniff_content_type()` detecta el tipus per magic bytes (JPEG, PNG, GIF, WebP, PDF i MP4); l'error 400 indica `Use JPEG, PNG, WebP, GIF, PDF or MP4.`
- `logo_url`, `banner_url`, `video_url` i `thumbnail_url` fan servir el tipus `MediaUrl`: accepten rutes relatives (i cadena buida) o URLs http(s) vàlides; una URL invàlida retorna 422.

---

## Endpoints d'administració

Requerix `role=admin` (verificat a `admin_service.py`):

| Endpoint | Descripció |
|----------|------------|
| `GET /api/admin/stats` | Estadístiques de la plataforma |
| `GET /api/admin/tables` | Nombre de files per taula |
| `GET /api/admin/audit-log` | Pista d'auditoria (filtres `action`, `actor_user_id`) |
| `POST /api/admin/reset` | `drop_all + create_all` (només no-producció) |

---

## Proves

```bash
cd backend

# Executar totes les proves
python -m pytest tests/ -x -q --tb=short

# Executar amb cobertura
python -m pytest tests/ --cov=app --cov-report=term-missing

# Fitxer de proves específic
python -m pytest tests/test_festivals.py -v
```

**Configuració de proves** (`pyproject.toml`):

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
markers = ["interop: interoperability tests that drive the real caldav client against a live server"]
```

Les proves asíncrones fan servir `pytest.mark.asyncio`; no hi ha `asyncio_mode` global.

**Fixture** (`tests/conftest.py`):
- `db_session` — sessió SQLite en memòria
- `client` — `AsyncClient` (httpx) contra l'aplicació de proves
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

**Configuració** (`pyproject.toml`):

```toml
[tool.ruff]
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "W"]
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
# Des de l'arrel del projecte
docker compose up        # Backend:8000, Frontend:3000
docker compose --profile db up  # + MariaDB:3306
```

### Carrega inicial de la base de dades

No hi ha script de seed: en desenvolupament l'aplicació crea l'admin inicial (`admin` / `setup`, canviar la contrasenya a l'entrar) i les taules mitjançant `create_all`. En producció les dades arriben per l'API i l'esquema només mitjançant Alembic.

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



---

## Despliegament

### Docker (Producció)

```yaml
# docker-compose.yml usa --profile prod
docker compose --profile prod up -d
```

Serveis:
- `backend-prod` — FastAPI (treballadors Uvicorn) a :8000
- `frontend-prod` — Nginx + Flutter web a :80
- `db` — MariaDB 11 (comprovació d'estat)

Perfils disponibles:
- `dev` (per defecte): servidors de desenvolupament backend i frontend
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
# {"status": "healthy", "db_revision": "<revisió actual>"}
```

---

## Lista de comprovació de seguretat

- [ ] Canvieu `SECRET_KEY` a producció
- [ ] Establiu `CORS_ORIGINS` a dominis específics
- [ ] Useu MariaDB (no SQLite) a producció
- [ ] Habiliteu HTTPS (proxy invers: nginx/Traefik)
- [ ] Configureu els hostos permesos en `TrustedHostMiddleware`
- [ ] Roteu les claus JWT periòdicament
- [ ] Vigileu els registres del limitador de velocitat
- [ ] Revisau la contrasenya de l'usuari admin després del primer inici de sessió

---

## Ampliar l'API

### Afegir un recurs nou

1. **Model** — `app/models/new_resource.py` (hereda `BaseModel`)
2. **Esquema** — `app/schemas/new_resource.py` (Pydantic)
3. **Servei** — `app/services/new_resource_service.py` (extén `BaseService`)
4. **Router** — `app/routers/new_resource.py` (incloure a `main.py`)
5. **Migració** — `alembic revision --autogenerate -m "add new_resource"`
6. **Proves** — `tests/test_new_resource.py`

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

## Resolució de problemes

| Problema | Solució |
|----------|---------|
| `ModuleNotFoundError: app` | Executeu des de `backend/` o `PYTHONPATH=backend` |
| `sqlite3.OperationalError: database is locked` | Un sol escriptor; assegureu-vos que no hi hagi processos obsolets |
| `alembic: Can't locate revision` | Esborreu `alembic/versions/`, executeu `alembic revision --autogenerate -m "init"` |
| `JWTError: Signature verification failed` | Incompatibilitat de `SECRET_KEY` entre l'entorn i el procés en execució |
| `429 Too Many Requests` | Límit de velocitat assolit; espereu 60s o estableixeu `TESTING=true` |
| WebSocket 403 | Token expirat; useu un token d'accés vàlid a `?token=` |
| Error CORS | Comproveu que `CORS_ORIGINS` a `.env` coincideix amb l'origen del frontend |

---

## Referències

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [Pydantic v2](https://docs.pydantic.dev/latest/)
- [Alembic](https://alembic.sqlalchemy.org/)
- [PyJWT](https://github.com/jpadilla/pyjwt)
- [bcrypt](https://github.com/pyca/bcrypt/)