# Clakettes Backend — Documentazione tecnica

[ES](../es/BACKEND.md) · [EN](../en/BACKEND.md) · [FR](../fr/BACKEND.md) · [DE](../de/BACKEND.md) · [IT](BACKEND.md) · [CA](../ca/BACKEND.md) · [EU](../eu/BACKEND.md) · [GL](../gl/BACKEND.md) · [OC](../oc/BACKEND.md)

Backend FastAPI per la piattaforma di gestione festival cinematografici Clakettes.

## Avvio rapido

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

## Architettura

### Struttura a strati

```
Routers (FastAPI) → Services (Logica di business) → Modelli (SQLAlchemy)
```

| Strato | Posizione | Responsabilità |
|--------|-----------|----------------|
| **Routers** | `app/routers/` | Endpoint HTTP, validazione richiesta/risposta, paginazione |
| **Services** | `app/services/` | Logica di business, operazioni CRUD, problematiche trasversali |
| **Models** | `app/models/` | Modelli ORM SQLAlchemy, schema DB |
| **Schemas** | `app/schemas/` | Modelli Pydantic per richiesta/risposta |
| **Auth** | `app/auth.py` | JWT, sessione, hash password |
| **Config** | `app/config.py` | Pydantic Settings da `.env` |
| **Database** | `app/database.py` | Engine, session factory, dipendenza `get_db()` |

### Principi di design chiave

1. **Router leggeri** — delegano ai servizi
2. **Services senza stato** — ricevono `db: Session` tramite iniezione di dipendenze
3. **I modelli ereditano `BaseModel`** — `id`, `created_at`, `updated_at` su tutte le entità
4. **Enum centralizzati** — `app/enums.py` condiviso tra modelli e schemi
5. **Base CRUD generica** — `BaseService` in `app/services/base_service.py`

---

## Configurazione

Tutta la configurazione avviene tramite `backend/.env` (caricato da `pydantic-settings`):

| Variabile | Default | Descrizione |
|-----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./clakettes.db` | Stringa di connessione SQLAlchemy |
| `SECRET_KEY` | (richiesta, nessun default) | Chiave di firma JWT |
| `JWT_ISSUER` | `clakettes` | Rivendicazione emittente JWT |
| `JWT_AUDIENCE` | `clakettes-api` | Rivendicazione audience JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | TTL token di accesso |
| `CORS_ORIGINS` | `None` (→ `["*"]`) | Origini consentite separate da virgola |
| `PORT_BACKEND` | `8000` | Porta del server (usata da Docker/script di avvio) |

**Esempio `.env` per produzione:**

```env
DATABASE_URL=mariadb+pymysql://user:pass@db:3306/clakettes_db
SECRET_KEY=super-secret-64-char-urlsafe-string
JWT_ISSUER=clakettes
JWT_AUDIENCE=clakettes-api
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=https://app.example.com,https://admin.example.com
```

Generare una chiave `SECRET_KEY` robusta:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

---

## Database

### Compatibilità a doppio database

| Ambiente | Database | Stringa di connessione |
|----------|----------|----------------------|
| Sviluppo | SQLite | `sqlite:///./data/clakettes.db` |
| Produzione | MariaDB | `mariadb+pymysql://user:pass@host:3306/db` |

### Modello base

Tutti i modelli ereditano da `BaseModel` (`app/models/base.py`):

```python
class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

### Migrazioni (Alembic)

```bash
cd backend

# Crea nuova migrazione dopo modifiche al modello
alembic revision --autogenerate -m "description"

# Applica migrazioni
alembic upgrade head

# Rollback
alembic downgrade -1

# Revisione corrente
alembic current
```

**Note di migrazione (SQLite ↔ MariaDB):**
- SQLite `INTEGER PRIMARY KEY` → MariaDB `INT AUTO_INCREMENT`
- SQLite `TEXT` → MariaDB `TEXT`/`VARCHAR`
- SQLite `DATETIME` (memorizzato come testo) → MariaDB `DATETIME` nativo
- Gli script di export/import in `backend/tools/` gestiscono le conversioni di tipo automaticamente

Consulta [DATABASE.md](DATABASE.md) per la documentazione completa dello schema con diagrammi ER.

---

## Autenticazione

### JWT + Tracciamento sessione

| Tipo di token | Formato | TTL | Archiviazione |
|---------------|---------|-----|---------------|
| **Access Token** | JWT (HS256) | 30 min (configurabile) | Memoria client |
| **Refresh Token** | Opaque (hash SHA-256 in DB) | 30 giorni | `UserSession.refresh_token_hash` |

### Flusso di login

```
POST /api/users/login
  {username, password}
→ 200 {access_token, refresh_token, token_type: "bearer", user: {...}}
```

### Uso del token

```http
Authorization: Bearer <access_token>
```

### Flusso di refresh

```
POST /api/auth/refresh
  {refresh_token}
→ 200 {access_token, refresh_token, token_type: "bearer"}
```

### Gestione sessione

- `GET /api/auth/sessions` — Elenca le sessioni attive
- `DELETE /api/auth/sessions/{session_id}` — Revoca sessione
- La sessione viene creata al login con informazioni del dispositivo (IP, UA, nome)
- I token vengono ruotati al refresh; i vecchi token vengono invalidati

### Hash delle password

- **bcrypt** tramite `passlib` (rounds=12)
- Hash memorizzato in `User.password_hash`
- Verificato tramite `pwd_context.verify(plain, hash)`

### Limite di richieste

- **100 richieste / 60 secondi** per IP (backup SQLite)
- Applicato tramite `RateLimitMiddleware` in `main.py`
- Disattivato quando si imposta la variabile d'ambiente `TESTING=true`

---

## Endpoint dell'API

### Registrazione router (`app/main.py`)

| Router | Prefisso | Tag | Descrizione |
|--------|----------|-----|-------------|
| `festivals` | `/api/festivals` | festivals | CRUD, ricerca, membri |
| `users` | `/api/users` | users | CRUD, profilo, caricamento avatar |
| `auth` | `/api/users` | auth | Login, refresh, registrazione |
| `auth_sessions` | `/api/auth` | auth | Lista/revoca sessioni |
| `shortfilms` | `/api/shortfilms` | shortfilms | CRUD, collegamento festival |
| `chat` | `/api/chat` | chat | Messaggi, endpoint WS |
| `user_festival` | `/api/festivals` | user-festival | Iscrizione/uscita, membri |
| `uploads` | `/api/uploads` | uploads | Caricamento avatar |
| `search` | `/api/search` | search | Ricerca globale |
| `admin` | `/api/admin` | admin | Statistiche, tabelle, audit-log, reset |
| `notifications` | `/api/notifications` | notifications | CRUD, conteggio non letti |
| `roles` | `/api` | roles | Ruoli, gruppi, dipendenze, conflitti |
| `participant_tags` | `/api` | participant-tags | Tag, configurazione festival |
| `user_roles` | `/api` | user-roles | Assegnazioni ruolo |
| `user_aliases` | `/api` | user-aliases | Alias di visualizzazione |
| `validation_rules` | `/api` | validation-rules | Validazione form dinamica |
| `registration_forms` | `/api` | registration-forms | Flussi di registrazione festival |
| `role_groups` | `/api` | role-groups | Raggruppamento ruoli |
| `committees` | `/api` | committees | Comitati festival |
| `delegations` | `/api` | delegations | Deleghe di ruolo |
| `events` | `/api` | events | Eventi, biglietti, posti, prenotazioni |
| `channels` | `/api/channels` | channels | Canali chat |
| `keys` | `/api/users` | e2ee | Gestione chiavi pubbliche E2EE |
| `locations` | `/api/locations` | locations | Geolocalizzazione, mappe |
| `location_tags` | `/api/locations/{location_id}/tags` | location-tags | Tag posizione |
| `location_images` | `/api/locations/{location_id}/images` | location-images | Immagini posizione |
| `location_relations` | `/api/locations/{location_id}/relations` | location-relations | Relazioni posizione |
| `shortfilm_locations` | `/api/shortfilms/{shortfilm_id}/locations` | shortfilm-locations | Posizioni cortometraggio |
| `form_definitions` | `/api` | forms | Builder form |
| `federation` | `/api/federation` | federation | manifest, directory, nodi, report, webfinger |
| `jury_votes` | `/api` | jury-votes | Voto giuria (fase 5) |
| `calendar` | `/api/calendar` | calendar | Agenda, CalDAV, impostazioni |
| `badges` | `/api` | badges | Badge, assegnazioni, idoneità |
| `posts` | `/api` | posts | Post social, risposte, moderazione |
| `payments` | `/api` | payments | Checkout, conferma, rimborso, webhook |
| `festival_rulebooks` | `/api/festivals/{festival_id}/rulebooks` | rulebooks | Regolamenti festival |
| `user_blocks` | `/api` | user-blocks | Blocco utente |
| `moderation_reports` | `/api` | moderation-reports | Report moderazione |
| `node_policies` | `/api` | node-policies | Politiche nodi federazione |

Totale: 38 router con `APIRouter` (40 file di router, 2 helper senza router).

### Paginazione e filtraggio

Parametri di query standard sugli endpoint di elenco:

```
GET /api/festivals/?page=1&size=20&search=cannes&is_active=true
```

Busta di risposta:

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

## Chat in tempo reale

### Backend WebSocket (`app/chat_backend/`)

| Componente | Descrizione |
|------------|-------------|
| `WebSocketChatBackend` | Implementazione predefinita (connessioni in memoria) |
| `chat_backend_registry` | Registro singleton per scambio backend |
| `ConnectionManager` | Gestisce mapping utente↔WebSocket |

### Endpoint

| Metodo | Route | Descrizione |
|--------|-------|-------------|
| `GET` | `/api/chat/ws` | Connessione WebSocket (auth via query `token`) |
| `POST` | `/api/chat/messages` | Invia messaggio (fallback REST) |
| `GET` | `/api/chat/messages` | Cronologia paginata |
| `PATCH` | `/api/chat/messages/{id}/read` | Segna come letto |

### Tipi di messaggio

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

- Scambio chiavi X25519 tramite `/api/users/{id}/keys`
- Chiavi pubbliche memorizzate in `UserKey` (una chiave attiva per utente)
- Cifratura/decifratura nel frontend (`e2ee_service.dart`)

---

## Caricamento file

### Caricamento avatar

```
POST /api/uploads/avatar
Content-Type: multipart/form-data
Authorization: Bearer <token>

file: <image/*>
```

- Salvato in `backend/uploads/avatars/{user_id}_{uuid}.{ext}`
- Servito staticamente in `/uploads/avatars/...`
- Dimensione massima: 10 MB (applicato da `RequestSizeLimitMiddleware`)

---

## Endpoint amministrativi

Richiede `role=admin` (verificato in `admin_service.py`):

| Endpoint | Descrizione |
|----------|-------------|
| `GET /api/admin/stats` | Statistiche della piattaforma |
| `GET /api/admin/tables` | Conteggio righe per tabella |
| `GET /api/admin/audit-log` | Tracce di audit (filtri `action`, `actor_user_id`) |
| `POST /api/admin/reset` | `drop_all + create_all` (solo non-prod) |

---

## Test

```bash
cd backend

# Esegui tutti i test
python -m pytest tests/ -x -q --tb=short

# Esegui con copertura
python -m pytest tests/ --cov=app --cov-report=term-missing

# File di test specifico
python -m pytest tests/test_festivals.py -v
```

**Configurazione test** (`pyproject.toml` / `pytest.ini`):

```ini
[tool.pytest.ini_options]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_functions = test_*
```

**Fixture** (`tests/conftest.py`):
- `db_session` — sessione SQLite in memoria
- `client` — `AsyncClient` (httpx) contro l'app di test
- `auth_headers` — header già autenticati

---

## Lint e formattazione

```bash
# Controllo
ruff check .

# Correzione auto-corregibile
ruff check . --fix

# Formatta
ruff format .
```

**Configurazione** (`pyproject.toml`):

```toml
[tool.ruff]
line-length = 120
target-version = "py312"
select = ["E", "F", "I", "UP", "B", "C4", "PTH", "T20", "SIM", "ARG"]
ignore = ["E501", "SIM102", "SIM103"]
```

---

## Flusso di sviluppo

### Sviluppo locale

```bash
# Terminale 1: Backend
cd backend
python -m uvicorn app.main:app --reload

# Terminale 2: Frontend (se necessario)
cd frontend
flutter run -d web-server --web-port 3000 --dart-define=BACKEND_URL=http://localhost:8000/api
```

### Sviluppo con Docker

```bash
# Dalla radice del progetto
docker compose up        # Backend:8000, Frontend:3000
docker compose --profile db up  # + MariaDB:3306
```

### Carico iniziale del database

Non c'è script di seed: in sviluppo l'app crea l'admin iniziale (`admin` /
`setup`, cambiare la password al primo accesso) e le tabelle tramite `create_all`. In produzione
i dati arrivano tramite l'API e lo schema solo tramite Alembic.

### Comandi frequenti

```bash
# Genera adattatori Hive (frontend)
cd frontend && flutter pub run build_runner build --delete-conflicting-outputs

# Esegui migrazioni
cd backend && alembic upgrade head

# Crea migrazione
cd backend && alembic revision --autogenerate -m "add column x"

# Esporta SQLite → MariaDB
cd backend && python tools/export_sqlite_to_mariadb.py

# Importa MariaDB → SQLite
cd backend && python tools/import_mariadb_to_sqlite.py
```

---

## Struttura del progetto

```
backend/
├── app/
│   ├── models/              # 40 modelli SQLAlchemy (+ base.py)
│   ├── schemas/             # 37 schemi Pydantic
│   ├── services/            # 43 servizi di logica di business
│   ├── routers/             # 40 router API (38 con APIRouter)
│   ├── chat_backend/        # Implementazione WebSocket chat
│   ├── auth.py              # Auth JWT + sessione
│   ├── config.py            # Pydantic Settings
│   ├── database.py          # Engine, SessionLocal, get_db()
│   ├── main.py              # App FastAPI, middleware, router
│   ├── rate_limiter.py      # Limitatore di velocità SQLite
│   ├── enums.py             # Enum condivisi
│   └── scripts/             # Script seed/migrazione
├── alembic/                 # Migrazioni (36 versioni)
├── tools/                   # Script export/import
├── tests/                   # Test pytest (47 file, 1439 funzioni di test)
├── uploads/                 # File caricati statici
├── .env.example             # Template configurazione
├── requirements.txt         # Dipendenze produzione
├── requirements-dev.txt     # Dipendenze dev (pytest, ruff)
├── pyproject.toml           # Config Ruff, pytest
└── pytest.ini               # Config pytest
```

Documentazione in `docs/it/BACKEND.md` (questo file) e `docs/it/DATABASE.md`.

---

## Deployment

### Docker (Produzione)

```yaml
# docker-compose.yml usa --profile prod
docker compose --profile prod up -d
```

Servizi:
- `backend-prod` — FastAPI (worker Uvicorn) su :8000
- `frontend-prod` — Nginx + Flutter web su :80
- `db` — MariaDB 11 (controllo stato)

Profili disponibili:
- `dev` (predefinito): server di sviluppo backend e frontend
- `db`: aggiunge il contenitore MariaDB
- `prod`: pila di produzione con nginx

### Variabili d'ambiente (Produzione)

```env
DATABASE_URL=mariadb+pymysql://user:pass@db:3306/clakettes_db
SECRET_KEY=<64-char-urlsafe>
CORS_ORIGINS=https://app.example.com
```

### Controllo di stato

```bash
curl http://localhost:8000/health
# {"status": "healthy"}
```

---

## Checklist di sicurezza

- [ ] Cambia `SECRET_KEY` in produzione
- [ ] Imposta `CORS_ORIGINS` su domini specifici
- [ ] Usa MariaDB (non SQLite) in produzione
- [ ] Abilita HTTPS (proxy inverso: nginx/Traefik)
- [ ] Configura host consentiti in `TrustedHostMiddleware`
- [ ] Ruota le chiavi JWT periodicamente
- [ ] Monitora i log del limitatore di velocità
- [ ] Controlla la password dell'admin dopo il primo accesso

---

## Espandere l'API

### Aggiungere una nuova risorsa

1. **Modello** — `app/models/new_resource.py` (eredita `BaseModel`)
2. **Schema** — `app/schemas/new_resource.py` (Pydantic)
3. **Servizio** — `app/services/new_resource_service.py` (estende `BaseService`)
4. **Router** — `app/routers/new_resource.py` (includere in `main.py`)
5. **Migrazione** — `alembic revision --autogenerate -m "add new_resource"`
6. **Test** — `tests/test_new_resource.py`

### Aggiungere un endpoint personalizzato a un router esistente

```python
# Nel file del router
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

## Risoluzione problemi

| Problema | Soluzione |
|----------|-----------|
| `ModuleNotFoundError: app` | Esegui dalla directory `backend/` o imposta `PYTHONPATH=backend` |
| `sqlite3.OperationalError: database is locked` | Singolo scrittore; assicurati nessun processo residuo |
| `alembic: Can't locate revision` | Elimina `alembic/versions/`, esegui `alembic revision --autogenerate -m "init"` |
| `JWTError: Signature verification failed` | `SECRET_KEY` incompatibile tra env e processo in esecuzione |
| `429 Too Many Requests` | Limite di velocità raggiunto; aspetta 60s o imposta `TESTING=true` |
| WebSocket 403 | Token scaduto; usa un token di accesso valido in `?token=` |
| Errore CORS | Verifica che `CORS_ORIGINS` in `.env` corrisponda all'origine del frontend |

---

## Riferimenti

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [Pydantic v2](https://docs.pydantic.dev/latest/)
- [Alembic](https://alembic.sqlalchemy.org/)
- [python-jose](https://github.com/mpdavis/python-jose)
- [passlib](https://passlib.readthedocs.io/)