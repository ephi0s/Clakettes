# Clakettes Backend — Technische Dokumentation

[ES](../es/BACKEND.md) · [EN](../en/BACKEND.md) · [FR](../fr/BACKEND.md) · [DE](BACKEND.md) · [IT](../it/BACKEND.md) · [CA](../ca/BACKEND.md) · [EU](../eu/BACKEND.md) · [GL](../gl/BACKEND.md) · [OC](../oc/BACKEND.md)

FastAPI-Backend für die Clakettes Filmfestival-Verwaltungsplattform.

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

### Ebenenstruktur

```
Routers (FastAPI) → Services (Business Logic) → Models (SQLAlchemy)
```

| Ebene | Ort | Verantwortung |
|-------|-----|---------------|
| **Routers** | `app/routers/` | HTTP-Endpunkte, Anfrage/Antwort-Validierung, Paginierung |
| **Services** | `app/services/` | Business-Logik, CRUD-Operationen, querbezogene Anliegen |
| **Models** | `app/models/` | SQLAlchemy ORM-Modelle, DB-Schema |
| **Schemas** | `app/schemas/` | Pydantic-Modelle für Anfrage/Antwort |
| **Auth** | `app/auth.py` | JWT, Sessions, Passwort-Hashing |
| **Config** | `app/config.py` | Pydantic Settings aus `.env` |
| **Database** | `app/database.py` | Engine, Session-Factory, `get_db()`-Dependency |

### Zentrale Designprinzipien

1. **Leichte Router** — delegieren an Services
2. **Zustandslose Services** — erhalten `db: Session` via Dependency Injection
3. **Modelle erben `BaseModel`** — `id`, `created_at`, `updated_at` auf allen Entitäten
4. **Zentrale Enums** — `app/enums.py` geteilt zwischen Modellen und Schemas
5. **Generische Basis-CRUD** — `BaseService` in `app/services/base_service.py`

---

## Konfiguration

Die gesamte Konfiguration erfolgt über `backend/.env` (geladen von `pydantic-settings`):

| Variable | Standard | Beschreibung |
|----------|----------|--------------|
| `DATABASE_URL` | `sqlite:///./clakettes.db` | SQLAlchemy-Verbindungsstring |
| `SECRET_KEY` | (erforderlich, kein Standard) | JWT-Signierungsschlüssel |
| `JWT_ISSUER` | `clakettes` | JWT-Issuer-Claim |
| `JWT_AUDIENCE` | `clakettes-api` | JWT-Audience-Claim |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access-Token-TTL |
| `CORS_ORIGINS` | `None` (→ `["*"]`) | Kommagetrennte erlaubte Ursprünge |
| `PORT_BACKEND` | `8000` | Server-Port (verwendet von Docker/Start-Skripten) |

**Beispiel `.env` für Produktion:**

```env
DATABASE_URL=mariadb+pymysql://user:pass@db:3306/clakettes_db
SECRET_KEY=super-secret-64-char-urlsafe-string
JWT_ISSUER=clakettes
JWT_AUDIENCE=clakettes-api
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=https://app.example.com,https://admin.example.com
```

Erzeugen Sie einen robusten `SECRET_KEY`:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

---

## Datenbank

### Duale Datenbank-Kompatibilität

| Umgebung | Datenbank | Verbindungsstring |
|----------|-----------|-------------------|
| Entwicklung | SQLite | `sqlite:///./data/clakettes.db` |
| Produktion | MariaDB | `mariadb+pymysql://user:pass@host:3306/db` |

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

# Neue Migration nach Modelländerungen erstellen
alembic revision --autogenerate -m "description"

# Migrationen anwenden
alembic upgrade head

# Rollback
alembic downgrade -1

# Aktuelle Revision
alembic current
```

**Migrationshinweise (SQLite ↔ MariaDB):**
- SQLite `INTEGER PRIMARY KEY` → MariaDB `INT AUTO_INCREMENT`
- SQLite `TEXT` → MariaDB `TEXT`/`VARCHAR`
- SQLite `DATETIME` (als Text gespeichert) → MariaDB nativer `DATETIME`
- Die Export-/Import-Skripte in `backend/tools/` übernehmen die Typkonvertierungen automatisch

Siehe [DATABASE.md](DATABASE.md) für die vollständige Schemadokumentation mit ER-Diagrammen.

---

## Authentifizierung

### JWT + Session-Tracking

| Token-Typ | Format | TTL | Speicher |
|-----------|--------|-----|----------|
| **Access Token** | JWT (HS256) | 30 Min (konfigurierbar) | Client-Speicher |
| **Refresh Token** | Opaque (SHA-256-Hash in DB) | 30 Tage | `UserSession.refresh_token_hash` |

### Login-Flow

```
POST /api/users/login
  {username, password}
→ 200 {access_token, refresh_token, token_type: "bearer", user: {...}}
```

### Token-Nutzung

```http
Authorization: Bearer <access_token>
```

### Refresh-Flow

```
POST /api/auth/refresh
  {refresh_token}
→ 200 {access_token, refresh_token, token_type: "bearer"}
```

### Session-Management

- `GET /api/auth/sessions` — Aktive Sessions auflisten
- `DELETE /api/auth/sessions/{session_id}` — Session widerrufen
- Die Session wird beim Login mit Geräteinformationen (IP, UA, Name) erstellt
- Tokens werden beim Refresh rotiert; alte Tokens werden ungültig

### Passwort-Hashing

- **bcrypt** via `passlib` (rounds=12)
- Hash gespeichert in `User.password_hash`
- Verifiziert via `pwd_context.verify(plain, hash)`

### Ratenlimit

- **100 Anfragen / 60 Sekunden** pro IP (SQLite-gesichert)
- Angewandt über `RateLimitMiddleware` in `main.py`
- Deaktiviert wenn `TESTING=true` Umgebungsvariable gesetzt ist

---

## API-Endpunkte

### Router-Registrierung (`app/main.py`)

| Router | Präfix | Tags | Beschreibung |
|--------|--------|------|--------------|
| `festivals` | `/api/festivals` | festivals | CRUD, Suche, Mitglieder |
| `users` | `/api/users` | users | CRUD, Profil, Avatar-Upload |
| `auth` | `/api/users` | auth | Login, Refresh, Registrierung |
| `auth_sessions` | `/api/auth` | auth | Session-Liste/Widerruf |
| `shortfilms` | `/api/shortfilms` | shortfilms | CRUD, Festival-Verknüpfung |
| `chat` | `/api/chat` | chat | Nachrichten, WS-Endpunkt |
| `user_festival` | `/api/festivals` | user-festival | Beitreten/Verlassen, Mitglieder |
| `uploads` | `/api/uploads` | uploads | Avatar-Upload |
| `search` | `/api/search` | search | Globale Suche |
| `admin` | `/api/admin` | admin | Stats, Tabellen, Audit-Log, Reset |
| `notifications` | `/api/notifications` | notifications | CRUD, ungelesen-Anzahl |
| `roles` | `/api` | roles | Rollen, Gruppen, Abhängigkeiten, Konflikte |
| `participant_tags` | `/api` | participant-tags | Tags, Festival-Konfiguration |
| `user_roles` | `/api` | user-roles | Rollenzuweisungen |
| `user_aliases` | `/api` | user-aliases | Anzeigenamen-Aliase |
| `validation_rules` | `/api` | validation-rules | Dynamische Formularvalidierung |
| `registration_forms` | `/api` | registration-forms | Festival-Registrierungsflows |
| `role_groups` | `/api` | role-groups | Rollen-Gruppierung |
| `committees` | `/api` | committees | Festival-Komitees |
| `delegations` | `/api` | delegations | Rollendelegationen |
| `events` | `/api` | events | Events, Tickets, Sitze, Reservierungen |
| `channels` | `/api/channels` | channels | Chat-Kanäle |
| `keys` | `/api/users` | e2ee | E2EE-Öffentlichkeitschlüssel-Verwaltung |
| `locations` | `/api/locations` | locations | Geolokalisierung, Karten |
| `location_tags` | `/api/locations/{location_id}/tags` | location-tags | Standort-Tags |
| `location_images` | `/api/locations/{location_id}/images` | location-images | Standortbilder |
| `location_relations` | `/api/locations/{location_id}/relations` | location-relations | Standortbeziehungen |
| `shortfilm_locations` | `/api/shortfilms/{shortfilm_id}/locations` | shortfilm-locations | Kurzfilm-Standorte |
| `form_definitions` | `/api` | forms | Formular-Builder |
| `federation` | `/api/federation` | federation | Manifest, Verzeichnis, Knoten, Berichte, WebFinger |
| `jury_votes` | `/api` | jury-votes | Juryabstimmung (Phase 5) |
| `calendar` | `/api/calendar` | calendar | Agenda, CalDAV, Einstellungen |
| `badges` | `/api` | badges | Badges, Zuweisungen, Berechtigung |
| `posts` | `/api` | posts | Social-Posts, Antworten, Moderation |
| `payments` | `/api` | payments | Checkout, Bestätigung, Rückerstattung, Webhook |
| `festival_rulebooks` | `/api/festivals/{festival_id}/rulebooks` | rulebooks | Festival-Regelwerke |
| `user_blocks` | `/api` | user-blocks | Benutzerblockierung |
| `moderation_reports` | `/api` | moderation-reports | Moderationsberichte |
| `node_policies` | `/api` | node-policies | Föderations-Knotenrichtlinien |

Gesamt: 38 Router mit `APIRouter` (40 Router-Dateien, 2 Helfer ohne Router).

### Paginierung und Filterung

Standard-Abfrageparameter auf List-Endpunkten:

```
GET /api/festivals/?page=1&size=20&search=cannes&is_active=true
```

Antwort-Umschlag:

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

### Backend-WebSocket (`app/chat_backend/`)

| Komponente | Beschreibung |
|------------|--------------|
| `WebSocketChatBackend` | Standardimplementierung (In-Memory-Verbindungen) |
| `chat_backend_registry` | Singleton-Registry für Backend-Austausch |
| `ConnectionManager` | Verwaltet Nutzer↔WebSocket-Mappings |

### Endpunkte

| Methode | Route | Beschreibung |
|---------|-------|--------------|
| `GET` | `/api/chat/ws` | WebSocket-Verbindung (Auth via Query `token`) |
| `POST` | `/api/chat/messages` | Nachricht senden (REST-Fallback) |
| `GET` | `/api/chat/messages` | Paginierter Verlauf |
| `PATCH` | `/api/chat/messages/{id}/read` | Als gelesen markieren |

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
- Öffentliche Schlüssel gespeichert in `UserKey` (ein aktiver Schlüssel pro Nutzer)
- Verschlüsselung/Entschlüsselung im Frontend (`e2ee_service.dart`)

---

## Datei-Uploads

### Avatar-Upload

```
POST /api/uploads/avatar
Content-Type: multipart/form-data
Authorization: Bearer <token>

file: <image/*>
```

- Gespeichert unter `backend/uploads/avatars/{user_id}_{uuid}.{ext}`
- Statisch serviert unter `/uploads/avatars/...`
- Max. Größe: 10 MB (angewendet durch `RequestSizeLimitMiddleware`)

---

## Admin-Endpunkte

Erfordert `role=admin` (geprüft in `admin_service.py`):

| Endpunkt | Beschreibung |
|----------|--------------|
| `GET /api/admin/stats` | Plattformstatistiken |
| `GET /api/admin/tables` | Zeilenanzahl pro Tabelle |
| `GET /api/admin/audit-log` | Audit-Spur (Filter `action`, `actor_user_id`) |
| `POST /api/admin/reset` | `drop_all + create_all` (nur Nicht-Produktion) |

---

## Tests

```bash
cd backend

# Alle Tests ausführen
python -m pytest tests/ -x -q --tb=short

# Mit Coverage ausführen
python -m pytest tests/ --cov=app --cov-report=term-missing

# Spezifische Testdatei
python -m pytest tests/test_festivals.py -v
```

**Test-Konfiguration** (`pyproject.toml` / `pytest.ini`):

```ini
[tool.pytest.ini_options]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_functions = test_*
```

**Fixtures** (`tests/conftest.py`):
- `db_session` — In-Memory-SQLite-Session
- `client` — `AsyncClient` (httpx) gegen die Test-App
- `auth_headers` — Vorauthentifizierte Header

---

## Lint und Formatierung

```bash
# Prüfen
ruff check .

# Auto-fixbare beheben
ruff check . --fix

# Formatieren
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

## Entwicklungsworkflow

### Lokale Entwicklung

```bash
# Terminal 1: Backend
cd backend
python -m uvicorn app.main:app --reload

# Terminal 2: Frontend (falls benötigt)
cd frontend
flutter run -d web-server --web-port 3000 --dart-define=BACKEND_URL=http://localhost:8000/api
```

### Entwicklung mit Docker

```bash
# Vom Projektstamm aus
docker compose up        # Backend:8000, Frontend:3000
docker compose --profile db up  # + MariaDB:3306
```

### Erstes Datenbank-Laden

Kein Seed-Skript: in Entwicklung erstellt die App den ersten Admin (`admin` / `setup`, Passwort beim ersten Login ändern) und Tabellen via `create_all`. In Produktion kommen Daten über die API und das Schema nur über Alembic.

### Häufige Befehle

```bash
# Hive-Adapter generieren (frontend)
cd frontend && flutter pub run build_runner build --delete-conflicting-outputs

# Migrationen ausführen
cd backend && alembic upgrade head

# Migration erstellen
cd backend && alembic revision --autogenerate -m "add column x"

# SQLite → MariaDB exportieren
cd backend && python tools/export_sqlite_to_mariadb.py

# MariaDB → SQLite importieren
cd backend && python tools/import_mariadb_to_sqlite.py
```

---

## Projektstruktur

```
backend/
├── app/
│   ├── models/              # 40 SQLAlchemy-Modelle (+ base.py)
│   ├── schemas/             # 37 Pydantic-Schemas
│   ├── services/            # 43 Business-Logik-Dienste
│   ├── routers/             # 40 API-Router (38 mit APIRouter)
│   ├── chat_backend/        # WebSocket-Chat-Implementierung
│   ├── auth.py              # JWT + Session-Auth
│   ├── config.py            # Pydantic-Settings
│   ├── database.py          # Engine, SessionLocal, get_db()
│   ├── main.py              # FastAPI-App, Middleware, Router
│   ├── rate_limiter.py      # SQLite-Ratenlimit
│   ├── enums.py             # Gemeinsame Enums
│   └── scripts/             # Seed-/Migration-Skripte
├── alembic/                 # Migrationen (36 Versionen)
├── tools/                   # Export-/Import-Skripte
├── tests/                   # pytest-Tests (47 Dateien, 1439 Testfunktionen)
├── uploads/                 # Statische Datei-Uploads
├── .env.example             # Konfigurationsvorlage
├── requirements.txt         # Produktions-Abhängigkeiten
├── requirements-dev.txt     # Dev-Abhängigkeiten (pytest, ruff)
├── pyproject.toml           # Ruff, pytest-Konfiguration
└── pytest.ini               # pytest-Konfiguration
```

Docs in `docs/de/BACKEND.md` (diese Datei) und `docs/de/DATABASE.md`.

---

## Bereitstellung

### Docker (Produktion)

```yaml
# docker-compose.yml verwendet --profile prod
docker compose --profile prod up -d
```

Dienste:
- `backend-prod` — FastAPI (Uvicorn-Workers) auf :8000
- `frontend-prod` — Nginx + Flutter Web auf :80
- `db` — MariaDB 11 (Health-Check)

Verfügbare Profile:
- `dev` (Standard): Backend- und Frontend-Entwicklungsserver
- `db`: fügt den MariaDB-Container hinzu
- `prod`: Produktionsstapel mit Nginx

### Produktions-Umgebungsvariablen

```env
DATABASE_URL=mariadb+pymysql://user:pass@db:3306/clakettes_db
SECRET_KEY=<64-char-urlsafe>
CORS_ORIGINS=https://app.example.com
```

### Health-Check

```bash
curl http://localhost:8000/health
# {"status": "healthy"}
```

---

## Sicherheits-Checkliste

- [ ] `SECRET_KEY` in Produktion ändern
- [ ] `CORS_ORIGINS` auf bestimmte Domains setzen
- [ ] MariaDB (nicht SQLite) in Produktion verwenden
- [ ] HTTPS aktivieren (Reverse-Proxy: Nginx/Traefik)
- [ ] Erlaubte Hosts in `TrustedHostMiddleware` konfigurieren
- [ ] JWT-Schlüssel regelmäßig rotieren
- [ ] Ratenlimit-Logs überwachen
- [ ] Admin-Benutzerpasswort nach erstem Login prüfen

---

## API erweitern

### Neue Ressource hinzufügen

1. **Modell** — `app/models/new_resource.py` (erbt `BaseModel`)
2. **Schema** — `app/schemas/new_resource.py` (Pydantic)
3. **Service** — `app/services/new_resource_service.py` (erweitert `BaseService`)
4. **Router** — `app/routers/new_resource.py` (in `main.py` einbinden)
5. **Migration** — `alembic revision --autogenerate -m "add new_resource"`
6. **Tests** — `tests/test_new_resource.py`

### Benutzerdefinierten Endpunkt zu einem bestehenden Router hinzufügen

```python
# In der Router-Datei
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

| Problem | Lösung |
|---------|--------|
| `ModuleNotFoundError: app` | Aus dem Verzeichnis `backend/` ausführen oder `PYTHONPATH=backend` |
| `sqlite3.OperationalError: database is locked` | Einzelner Schreiber; keine veralteten Prozesse sicherstellen |
| `alembic: Can't locate revision` | `alembic/versions/` löschen, `alembic revision --autogenerate -m "init"` ausführen |
| `JWTError: Signature verification failed` | `SECRET_KEY`-Unterschied zwischen Umgebung und laufendem Prozess |
| `429 Too Many Requests` | Ratenlimit erreicht; 60s warten oder `TESTING=true` setzen |
| WebSocket 403 | Token abgelaufen; gültigen Access-Token in `?token=` verwenden |
| CORS-Fehler | Prüfen, ob `CORS_ORIGINS` in `.env` zum Frontend-Ursprung passt |

---

## Referenzen

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [Pydantic v2](https://docs.pydantic.dev/latest/)
- [Alembic](https://alembic.sqlalchemy.org/)
- [python-jose](https://github.com/mpdavis/python-jose)
- [passlib](https://passlib.readthedocs.io/)