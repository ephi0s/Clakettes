# Clakettes Backend — Teknikoa dokumentazioa

[ES](../es/BACKEND.md) · [EN](../en/BACKEND.md) · [FR](../fr/BACKEND.md) · [DE](../de/BACKEND.md) · [IT](../it/BACKEND.md) · [CA](../ca/BACKEND.md) · [CA](BACKEND.md) · [EU](../eu/BACKEND.md) · [GL](../gl/BACKEND.md) · [OC](../oc/BACKEND.md)

FastAPI backend Clakettes filma-festival-ko kudeaketa platforma-ren barruan.

## Hasi urratski

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

### Nazioaren jatorria

```
Routers (FastAPI) → Serzerri (Lanak) → Modelak (SQLAlchemy)
```

| Nazioa | Non | Egiazkotasuna |
|--------|-----|---------------|
| **Routers** | `app/routers/` | HTTP endpointak, soliketa/respuesta egokitzea, paginazioa |
| **Zerbitzariak** | `app/services/` | lan-lerroa, CRUD operazioak, zebezzita idea-k |
| **Modeloak** | `app/models/` | SQLAlchemy ORM modelak, DB-eko eskema |
| **Eskaerak** | `app/schemas/` | Pydantic modelak soliketa/respuestarako |
| **Autentikazioa** | `app/auth.py` | JWT, sesioa, pasahitz-hash |
| **Konfigurazioa** | `app/config.py` | Pydantic Settings `.env` noitik |
| **Datu-basea** | `app/database.py` | Motor, session fabrikatua, `get_db()` eskainitza |

### Diren konbendio garrantzitsuak

1. **Routers lekuak** — zerbitzaritik eskatzen dute
2. **Zerbitzariak ingurune horretan** — `db: Session` eskainitza injecció bidez
3. **Modeloak `BaseModel`-etik heredan** — `id`, `created_at`, `updated_at` entitate guztietan
4. **Enums eskaintuta** — `app/enums.py` partage model eta eskera-ren artean
5. **Base CRUD jatorrizkoa** — `BaseService` `app/services/base_service.py`-an

---

## Konfigurazioa

Konfigurazioa osoa `backend/.env` fitxategian egiten da (`pydantic-settings` bidez kargatzen):

| Aldagaia | Default | Deskribapena |
|----------|---------|--------------|
| `DATABASE_URL` | `sqlite:///./clakettes.db` | SQLAlchemy-ko konexio-urlea |
| `SECRET_KEY` | (beharrezkoa, defaultrik gabe) | JWT-aren finkatzeko gakoa |
| `JWT_ISSUER` | `clakettes` | JWT-aren itsale deia |
| `JWT_AUDIENCE` | `clakettes-api` | JWT-aren aiketari deia |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access-ken ttl |
| `CORS_ORIGINS` | `None` (→ `["*"]`) | Komatxoekin beharrezko orokorrak |
| `PORT_BACKEND` | `8000` | zerbitzariaren porta (Docker/hasiera eskritatik) |

**Adibidea `.env` produktu batean:**

```env
DATABASE_URL=mariadb+pymysql://user:pass@db:3306/clakettes_db
SECRET_KEY=super-secret-64-char-urlsafe-string
JWT_ISSUER=clakettes
JWT_AUDIENCE=clakettes-api
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=https://app.example.com,https://admin.example.com
```

Sortzeko `SECRET_KEY`-ak robustu bat:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

---

## Datu-basea

### Datu-base dvojakea

| Entorra | Datu-basea | Konexio-urlea |
|---------|------------|---------------|
| Garapena | SQLite | `sqlite:///./data/clakettes.db` |
| Produktua | MariaDB | `mariadb+pymysql://user:pass@host:3306/db` |

### Base model

Modeloak guztiak `BaseModel`-etik heredan (`app/models/base.py`):

```python
class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

### Migrerak (Alembic)

```bash
cd backend

# Mutil gehiago aldatu ondoren berriro sortzeko
alembic revision --autogenerate -m "deskripzioa"

# Aplikatzea
alembic upgrade head

# Aurrera-eta
alembic downgrade -1

# Bertsioa duen
alembic current
```

**Migreraren azkena (SQLite ↔ MariaDB):**
- SQLite `INTEGER PRIMARY KEY` → MariaDB `INT AUTO_INCREMENT`
- SQLite `TEXT` → MariaDB `TEXT`/`VARCHAR`
- SQLite `DATETIME` (testua bezala)gorde → MariaDB `DATETIME` nativoa
- `export_sqlite_to_mariadb.py` eta `import_mariadb_to_sqlite.py` eskriptuak tipi-biderkatzea egiten dute

Ikusi [DATABASE.md](DATABASE.md) eskemaaren dokumentazioa oso eta ER-diagramak.

---

## Autentikazioa

### JWT + Sesio-en kontrola

| Tipusa | Formatoa | Ttl | Gorde-eremua |
|--------|----------|-----|--------------|
| **Access Token** | JWT (HS256) | 30 min (egokitzea) | Erraz eragina |
| **Refresh Token** | Opako (SHA-256 hash BD-n) | 30 egun | `UserSession.refresh_token_hash` |

### Hasiera-prozedura

```
POST /api/users/login
  {username, password}
→ 200 {access_token, refresh_token, token_type: "bearer", user: {...}}
```

### Token-aren erabilera

```http
Authorization: Bearer <access_token>
```

### Berritze-prozedura

```
POST /api/auth/refresh
  {refresh_token}
→ 200 {access_token, refresh_token, token_type: "bearer"}
```

### Sesio-aren kudeaketa

- `GET /api/auth/sessions` — Sesio guztien zerrendatua
- `DELETE /api/auth/sessions/{session_id}` — Sesio-a ukatu
- Sesioa hasiera eraman da nahiz eta datorren informazioarekin (IP, UA, izena)
- Tokenak berritzean berritzen dira; kode guztiak inertxatu egiten dira

### Pasahitz-hash-ak

- **bcrypt** `passlib`-ekin (rounds=12)
- Hash gordetzen da `User.password_hash`-en
- `pwd_context.verify(plain, hash)` bidez egiaztatzen da

### Esaskera-kontrole

- **100 esakra / 60 segundu** IP-eko (SQLite-ko kopia)
- `RateLimitMiddleware`-penean `main.py`-an aplikatzen da
- `TESTING=true` aldagaia ez badago desaktibatze da

---

## API-ko endpoint-ak

### Registratzea (`app/main.py`-ko router-ak)

| Router | Prefix | Tagak | Deskribapena |
|--------|--------|-------|--------------|
| `festivals` | `/api/festivals` | festivals | CRUD, bilaketa, kideak |
| `users` | `/api/users` | users | CRUD, profila, avatar eskaintzea |
| `auth` | `/api/users` | auth | Hasi saioa, berritzea, erregistroa |
| `auth_sessions` | `/api/auth` | auth | sesio-zerrenda / ukatu |
| `shortfilms` | `/api/shortfilms` | shortfilms | CRUD, festival-ko aukera |
| `chat` | `/api/chat` | chat | mezuak, WS endpoint |
| `user_festival` | `/api/festivals` | user-festival | sarbidea / irten, kideak |
| `uploads` | `/api/uploads` | uploads | avatar eskaintza |
| `search` | `/api/search` | search | bilaketa osoa |
| `admin` | `/api/admin` | admin | estatistak, taulak, audit-log, erreset |
| `notifications` | `/api/notifications` | notifications | CRUD, ia-oi kopurua |
| `roles` | `/api` | roles | rolekak, taldea, herrialdiak, konfiktsuak |
| `participant_tags` | `/api` | participant-tags | etiketak, festival-ko konfigurazioa |
| `user_roles` | `/api` | user-roles | rolek-en eskaintzak |
| `user_aliases` | `/api` | user-aliases | erakusteko alias-ak |
| `validation_rules` | `/api` | validation-rules | formulari-eko dinamikoa |
| `registration_forms` | `/api` | registration-forms | festival-ko erregistro-prozedura |
| `role_groups` | `/api` | role-groups | rolen taldea |
| `committees` | `/api` | committees | festival-ko komiteak |
| `delegations` | `/api` | delegations | rolen delegazioak |
| `events` | `/api` | events | txarpinak, ticket-ak, sittingak, reserva-k |
| `channels` | `/api/channels` | channels | txat-kanalak |
| `keys` | `/api/users` | e2ee | E2EE publikoak kudeaketa |
| `locations` | `/api/locations` | locations | mapa-ko kudeaketa |
| `location_tags` | `/api/locations/{location_id}/tags` | location-tags | kokatzeko etiketak |
| `location_images` | `/api/locations/{location_id}/images` | location-images | kokatzeko irudiak |
| `location_relations` | `/api/locations/{location_id}/relations` | location-relations | kokatzeko erlazionak |
| `shortfilm_locations` | `/api/shortfilms/{shortfilm_id}/locations` | shortfilm-locations | kurdiak kokatzeko |
| `form_definitions` | `/api` | forms | formulario-ko editorea |
| `federation` | `/api/federation` | federation | esku-menua, direktorioa, nodoak, webfinger |
| `jury_votes` | `/api` | jury-votes | juradoaren botoa (fase 5) |
| `calendar` | `/api/calendar` | calendar | agenda, CalDAV, konfigurazioa |
| `badges` | `/api` | badges | insignak, eskaintzak, aukeratzea |
| `posts` | `/api` | posts | publikatuko sozialak, erantzunak, moderazioa |
| `payments` | `/api` | payments | txartel, kontua, berrita, webhook |
| `festival_rulebooks` | `/api/festivals/{festival_id}/rulebooks` | rulebooks | festival-ko liburu-gauzak |
| `user_blocks` | `/api` | user-blocks | erabiltzaile-blokeoak |
| `moderation_reports` | `/api` | moderation-reports | moderazio-itzulpenak |
| `node_policies` | `/api` | node-policies | nodo-eko federazio-politikoak |

Guztira: 38 router `APIRouter`-ekin (40 router-fitxategia, 2 erabiltzaile-roker gabe).

### Paginazioa eta filtratzea

Esku-menuko ezazu betikareांक:

```
GET /api/festivals/?page=1&size=20&search=cannes&is_active=true
```

Erantzun-sakura:

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

## Txat-egoitza

### WebSocket Backend-a (`app/chat_backend/`)

| Eskura | Deskribapena |
|--------|--------------|
| `WebSocketChatBackend` | Default-implementazioa (memoria-ko konexioak) |
| `chat_backend_registry` | Singleton erregistroa zerbitzari-alkeria-erasketze |
| `ConnectionManager` | erabiltzailea↔WebSocket-eko mapatzeak eskaintzen du |

### Endpoint-ak

| Metodoa | Ruta | Deskribapena |
|---------|------|--------------|
| `GET` | `/api/chat/ws` | WebSocket-ko konexioa (`token` query-kin autentikazioa) |
| `POST` | `/api/chat/messages` | Mezua bidali (REST-egaia) |
| `GET` | `/api/chat/messages` | historiaren kontua |
| `PATCH` | `/api/chat/messages/{id}/read` | Irisgarritzen |

### Mezua-aka

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

- X25519 gako-eratibaketa `/api/users/{id}/keys`-rekin
- Publikoak gordetzen dira `UserKey`-n (bat zerbitzari-ko erabiltzailea)
- Xifratuta/desxifratutafrontend-en (`e2ee_service.dart`)

---

## Fitxategi-eskaintzak

### Avatar-ko eskaintza

```
POST /api/uploads/avatar
Content-Type: multipart/form-data
Authorization: Bearer <token>

file: <image/*>
```

- `backend/uploads/avatars/{user_id}_{uuid}.{ext}`-ko gordetzea
-静okoki eskaintzen da `/uploads/avatars/...`-en
- 10 MB max tamaina (`RequestSizeLimitMiddleware`-kin aplikatzen)

---

## Admin-eko endpoint-ak

`role=admin` beharrezkoa da (`admin_service.py`-n egiaztatzeak):

| Endpoint | Deskribapena |
|----------|--------------|
| `GET /api/admin/stats` | platforma-ko estatistikak |
| `GET /api/admin/tables` | taula-ko erregistratzen kopurua |
| `GET /api/admin/audit-log` | audit-trace (ezazu `action`, `actor_user_id`) |
| `POST /api/admin/reset` | `drop_all + create_all` (ez produktu batean) |

---

## Ezakutagarriak

```bash
cd backend

# Baina erastun bidez
python -m pytest tests/ -x -q --tb=short

# Eta-kiemena
python -m pytest tests/ --cov=app --cov-report=term-missing

# Eskuratze-fitxategia beste bat
python -m pytest tests/test_festivals.py -v
```

**Ezakutagarrien konfigurazioa** (`pyproject.toml` / `pytest.ini`):

```ini
[tool.pytest.ini_options]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_functions = test_*
```

**Ezabaketa** (`tests/conftest.py`):
- `db_session` — memoria-ko SQLite-sesioa
- `client` — `AsyncClient` (httpx) erastunekin aplikazioan
- `auth_headers` — autentikatutako erantzunak

---

## Lint eta formatatzea

```bash
# Eskuratu
ruff check .

# Auto-fixing autokorrigatu
ruff check . --fix

# Format sortu
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

## Garapene-prozedura

### Garapen lokal

```bash
# Terminal 1: Backend
cd backend
python -m uvicorn app.main:app --reload

# Terminal 2: Frontend (behar bada)
cd frontend
flutter run -d web-server --web-port 3000 --dart-define=BACKEND_URL=http://localhost:8000/api
```

### Garapen Docker bidez

```bash
# Proiektuko goialde-tik
docker compose up        # Backend:8000, Frontend:3000
docker compose --profile db up  # + MariaDB:3306
```

### DB-ko hasiera-karga

Ez dago script-edergara: garapenean aplikazioa admin-a sortzen du (`admin` / `setup`, pasahitza aldatu hasieran) eta taulak `create_all`-ear. Produktean datuak API bidez iraungo dira eta eskema aldakorik Alembic bidez.

### Ahazosgarriak

```bash
# Hive-eko adaptadoreak sortzeko (frontend)
cd frontend && flutter pub run build_runner build --delete-conflicting-outputs

# Migrerak aplikatzeko
cd backend && alembic upgrade head

# Mutil-a sortzeko
cd backend && alembic revision --autogenerate -m "add column x"

# SQLite → MariaDB eskaintzea
cd backend && python tools/export_sqlite_to_mariadb.py

# MariaDB → SQLite importatzea
cd backend && python tools/import_mariadb_to_sqlite.py
```

---

## Proiektuko eremu-ra

```
backend/
├── app/
│   ├── models/              # 40 SQLAlchemy modelak (+ base.py)
│   ├── schemas/             # 37 Pydantic eskera
│   ├── services/            # 43 lan-erako zerbitzuak
│   ├── routers/             # 40 API-router-ak (38 `APIRouter`-ekin)
│   ├── chat_backend/        # WebSocket txat-eramoa
│   ├── auth.py              # JWT + sesioa autentikazioa
│   ├── config.py            # Pydantic Settings
│   ├── database.py          # Motor, SessionLocal, get_db()
│   ├── main.py              # FastAPI aplikazioa, middleware, router-ak
│   ├── rate_limiter.py      # SQLite rate-limit
│   ├── enums.py             # shared enums
│   └── scripts/             # Seed/migazio eskriptuak
├── alembic/                 # Migrerak (36 bertsioa)
├── tools/                   # Eskaintza/importatutako eskriptuak
├── tests/                   # Proveek pytest-ak (47 fitxategi, 1439 prove-funtzioak)
├── uploads/                 # eskaintzea
├── .env.example             # konfigurazio-mikroa
├── requirements.txt         # produktu-ko jarduera
├── requirements-dev.txt     # garapene-ko� Anforderungen (pytest, ruff)
├── pyproject.toml           # Ruff, pytest-eko konfigurazioa
└── pytest.ini               # pytest-eko konfigurazioa
```

Dokumentazioa `docs/eu/BACKEND.md` (hau da) eta `docs/eu/DATABASE.md` fitxategian.

---

## Desploiamentua

### Docker (Produktua)

```yaml
# docker-compose.yml `--profile prod` erabiltzen du
docker compose --profile prod up -d
```

Erazkinak:
- `backend-prod` — FastAPI (Uvicorn taldeek) :8000an
- `frontend-prod` — Nginx + Flutter web :80an
- `db` — MariaDB 11 (egon-tasa)

Desploiamentuak:
- `dev` (default): garapene-ko zerbitzariak backend eta frontend
- `db`: MariaDB-ko kontenitore-a eskuragarri egiten du
- `prod`: produkcione-ko pila nginx-arekin

### Aldagaiak (Produktua)

```env
DATABASE_URL=mariadb+pymysql://user:pass@db:3306/clakettes_db
SECRET_KEY=<64-char-urlsafe>
CORS_ORIGINS=https://app.example.com
```

### Ego-tasa

```bash
curl http://localhost:8000/health
# {"status": "healthy"}
```

---

## Seguritate-zerrenda

- [ ] Aldatu `SECRET_KEY` produktu batean
- [ ] Egin `CORS_ORIGINS` domein-eko uri-kin
- [ ] Egin MariaDB (ez SQLite) produktu batean
- [ ] Egin HTTPS (nginx/Traefik proxy-arekin)
- [ ] Konfiguratu `TrustedHostMiddleware`-ren aurkezpena
- [ ] Berritze JWT-gakoak askoen arabera
- [ ] Begiratu rate-limit log-ak
- [ ] Begiratu admin-ko erabiltzailea pasahitza hasiera saioan

---

## API-alde gehiago

### Eskuriagoa

1. **Modelo** — `app/models/new_resource.py` (`BaseModel`-etik heredan)
2. **Eskaera** — `app/schemas/new_resource.py` (Pydantic)
3. **Zerbitzaria** — `app/services/new_resource_service.py` (`BaseService`-ekin)
4. **Router** — `app/routers/new_resource.py` (`main.py`-ra sartzen)
5. **Mutil-a** — `alembic revision --autogenerate -m "add new_resource"`
6. **Proba** — `tests/test_new_resource.py`

### Endpoint-a router-eko barruan

```python
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

## Erlasten barnera

| Erlasia | Erantzuna |
|---------|-----------|
| `ModuleNotFoundError: app` | `backend/` barruan executa edota `PYTHONPATH=backend` |
| `sqlite3.OperationalError: database is locked` | Erraz writer-ak; ziur egin beste-prozesu-rik ez dela |
| `alembic: Can't locate revision` | `alembic/versions/` kendu, `alembic revision --autogenerate -m "init"` exekutatu |
| `JWTError: Signature verification failed` | `SECRET_KEY` desbiderakuntu da entornotan eta exekutatzean |
| `429 Too Many Requests` | Rate-limit idi; egone 60s edo `TESTING=true` ezarri |
| WebSocket 403 | token-kaduta egin da; `?token=`-rekin token-a eskaintza |
| CORS errore | `CORS_ORIGINS` `.env`-en frontend-aren stammenarekin bat egiten da |

---

## Eduriketak

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [Pydantic v2](https://docs.pydantic.dev/latest/)
- [Alembic](https://alembic.sqlalchemy.org/)
- [python-jose](https://github.com/mpdavis/python-jose)
- [passlib](https://passlib.readthedocs.io/)