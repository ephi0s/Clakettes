# Clakettes Backend — Documentación técnica

[ES](../es/BACKEND.md) · [EN](../en/BACKEND.md) · [FR](../fr/BACKEND.md) · [DE](../de/BACKEND.md) · [IT](../it/BACKEND.md) · [CA](../ca/BACKEND.md) · [EU](../eu/BACKEND.md) · [CA](BACKEND.md) · [GL](BACKEND.md) · [OC](../oc/BACKEND.md)

Backend FastAPI para a plataforma de xestión de festivais de cinema Clakettes.

## Inicio rápido

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

### Estrutura por capas

```
Routers (FastAPI) → Servizos (Lóxica de negócios) → Modelos (SQLAlchemy)
```

| Capa | Ubicación | Responsabilidade |
|------|-----------|------------------|
| **Routers** | `app/routers/` | Endpoints HTTP, validación de solicitud/resposta, paginación |
| **Servizos** | `app/services/` | Lóxica de negocios, operacións CRUD, preocupacións transversais |
| **Modelos** | `app/models/` | Modelos ORM SQLAlchemy, esquema DB |
| **Schemas** | `app/schemas/` | Modelos Pydantic para solicitud/resposta |
| **Auth** | `app/auth.py` | JWT, sesións, hash de contrasinais |
| **Config** | `app/config.py` | Pydantic Settings desde `.env` |
| **Database** | `app/database.py` | Motor, sesión factory, dependencia `get_db()` |

### Princípios chave de deseño

1. **Routers lixeiros** — delegan aos servizos
2. **Servizos sen estado** — reciben `db: Session` mediante inyección de dependencias
3. **Os modelos heredan `BaseModel`** — `id`, `created_at`, `updated_at` en todas as entidades
4. **Enums centralizados** — `app/enums.py` compartido entre modelos e esquemas
5. **Base CRUD xenerica** — `BaseService` en `app/services/base_service.py`

---

## Configuración

Toda a configuración faise por `backend/.env` (cargado por `pydantic-settings`):

| Variable | Default | Descrición |
|----------|---------|------------|
| `DATABASE_URL` | `sqlite:///./clakettes.db` | String de conexión SQLAlchemy |
| `SECRET_KEY` | (requerido, sen default) | Chave de firma JWT |
| `JWT_ISSUER` | `clakettes` | Reivindicación emisor JWT |
| `JWT_AUDIENCE` | `clakettes-api` | Reivindicación audiencia JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | TTL do token de acceso |
| `CORS_ORIGINS` | `None` (→ `["*"]`) | Oríxenes permitidas separadas por comas |
| `PORT_BACKEND` | `8000` | Puerto do servidor (usado por Docker/scripts de arranque) |

**Exemplo de `.env` en produción:**

```env
DATABASE_URL=mariadb+pymysql://user:pass@db:3306/clakettes_db
SECRET_KEY=super-secret-64-char-urlsafe-string
JWT_ISSUER=clakettes
JWT_AUDIENCE=clakettes-api
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=https://app.example.com,https://admin.example.com
```

Xerar unha chave `SECRET_KEY` robusta:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

---

## Base de datos

### Compatibilidade con dous bancos de datos

| Entorno | Base de datos | String de conexión |
|---------|---------------|--------------------|
| Desenvolvemento | SQLite | `sqlite:///./data/clakettes.db` |
| Produción | MariaDB | `mariadb+pymysql://user:pass@host:3306/db` |

### Modelo base

Todos os modelos heredan de `BaseModel` (`app/models/base.py`):

```python
class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

### Migracións (Alembic)

```bash
cd backend

# Crear nova migración despois de cambios no modelo
alembic revision --autogenerate -m "descrición"

# Aplicar migracións
alembic upgrade head

# Reverter
alembic downgrade -1

# Revisión actual
alembic current
```

**Notas de migración (SQLite ↔ MariaDB):**
- SQLite `INTEGER PRIMARY KEY` → MariaDB `INT AUTO_INCREMENT`
- SQLite `TEXT` → MariaDB `TEXT`/`VARCHAR`
- SQLite `DATETIME` (almacenado como texto) → MariaDB `DATETIME` nativo
- Os scripts de exportación/importación en `backend/tools/` xestionan as conversións de tipos automáticamente

Consulte [DATABASE.md](DATABASE.md) para a documentación completa do esquema con diagramas ER.

---

## Autenticación

### JWT + Seguimento de sesións

| Tipo de token | Formato | TTL | Almacenamiento |
|---------------|---------|-----|----------------|
| **Access Token** | JWT (HS256) | 30 min (configurable) | Memoria do cliente |
| **Refresh Token** | Opaco (hash SHA-256 na DB) | 30 días | `UserSession.refresh_token_hash` |

### Fluzo de inicio de sesión

```
POST /api/users/login
  {username, password}
→ 200 {access_token, refresh_token, token_type: "bearer", user: {...}}
```

### Uso do token

```http
Authorization: Bearer <access_token>
```

### Fluzo de renovación

```
POST /api/auth/refresh
  {refresh_token}
→ 200 {access_token, refresh_token, token_type: "bearer"}
```

### Xestión de sesións

- `GET /api/auth/sessions` — Listar as sesións activas
- `DELETE /api/auth/sessions/{session_id}` — Revocar a sesión
- A sesión créase ao iniciar sesión con información do dispositivo (IP, UA, nome)
- Os tokens rotanse ao renovar; os tokens antigos invalidanse

### Hash de contrasinais

- **bcrypt** mediante `passlib` (rounds=12)
- Hash gardado en `User.password_hash`
- Verificado mediante `pwd_context.verify(plain, hash)`

### Límite de peticións

- **100 peticións / 60 segundos** por IP (copia de seguridade en SQLite)
- Aplicado mediante `RateLimitMiddleware` en `main.py`
- Desactivado cando se establece a variable de entorno `TESTING=true`

---

## Endpoints da API

### Rexistro de routers (`app/main.py`)

| Router | Prefix | Tags | Descrición |
|--------|--------|------|------------|
| `festivals` | `/api/festivals` | festivals | CRUD, busca, membros |
| `users` | `/api/users` | users | CRUD, perfil, subida de avatar |
| `auth` | `/api/users` | auth | Login, refresh, rexistro |
| `auth_sessions` | `/api/auth` | auth | Lista/revocación de sesións |
| `shortfilms` | `/api/shortfilms` | shortfilms | CRUD, vinculación festival |
| `chat` | `/api/chat` | chat | Mensaxes, endpoint WS |
| `user_festival` | `/api/festivals` | user-festival | Unirse/sair, membros |
| `uploads` | `/api/uploads` | uploads | Subida de avatar |
| `search` | `/api/search` | search | Busca global |
| `admin` | `/api/admin` | admin | Estatísticas, táboas, audit-log, reset |
| `notifications` | `/api/notifications` | notifications | CRUD, non lidos count |
| `roles` | `/api` | roles | Roles, grupos, dep., conflitos |
| `participant_tags` | `/api` | participant-tags | Tags, configuración festival |
| `user_roles` | `/api` | user-roles | Asignacións de roles |
| `user_aliases` | `/api` | user-aliases | Aliases de visualización |
| `validation_rules` | `/api` | validation-rules | Validación dinámica de formularios |
| `registration_forms` | `/api` | registration-forms | Fluxos de rexistro festival |
| `role_groups` | `/api` | role-groups | Agrupación de roles |
| `committees` | `/api` | committees | Comités festival |
| `delegations` | `/api` | delegations | Delegacións de roles |
| `events` | `/api` | events | Eventos, tipos de entrada, asientos, reservas |
| `channels` | `/api/channels` | channels | Canles de chat |
| `keys` | `/api/users` | e2ee | Xestión de chaves públicas E2EE |
| `locations` | `/api/locations` | locations | xeolocalización, mapas |
| `location_tags` | `/api/locations/{location_id}/tags` | location-tags | Tags de ubicación |
| `location_images` | `/api/locations/{location_id}/images` | location-images | Imaxes de ubicación |
| `location_relations` | `/api/locations/{location_id}/relations` | location-relations | Relacións de ubicación |
| `shortfilm_locations` | `/api/shortfilms/{shortfilm_id}/locations` | shortfilm-locations | Ubicacións de curtametraxe |
| `form_definitions` | `/api` | forms | Creador de formularios |
| `federation` | `/api/federation` | federation | manifest, directorio, nodos, informes, webfinger |
| `jury_votes` | `/api` | jury-votes | Votaxe do xurado (fase 5) |
| `calendar` | `/api/calendar` | calendar | Agenda, CalDAV, configuracións |
| `badges` | `/api` | badges | Insignias, asignacións, elegibilidade |
| `posts` | `/api` | posts | Publicacións sociais, resposta, moderación |
| `payments` | `/api` | payments | Checkout, confirmar, reembolso, webhook |
| `festival_rulebooks` | `/api/festivals/{festival_id}/rulebooks` | rulebooks | Reglamentos festival |
| `user_blocks` | `/api` | user-blocks | Bloqueo de usuarios |
| `moderation_reports` | `/api` | moderation-reports | Informes de moderación |
| `node_policies` | `/api` | node-policies | Políticas de nodos de federación |

Total: 38 routers con `APIRouter` (40 arquivos de router, 2 auxiliares sen router).

### Paginación e filtrado

Parámetros de consulta estándar nos endpoints de listado:

```
GET /api/festivals/?page=1&size=20&search=cannes&is_active=true
```

Sobre de resposta:

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

## Chateo en tempo real

### Backend WebSocket (`app/chat_backend/`)

| Componente | Descrición |
|------------|------------|
| `WebSocketChatBackend` | Implementación por defecto (conexións en memoria) |
| `chat_backend_registry` | Rexistro singular para cambio de backend |
| `ConnectionManager` | Xestiona mapeos usuario↔WebSocket |

### Endpoints

| Método | Ruta | Descrición |
|--------|------|------------|
| `GET` | `/api/chat/ws` | Conexión WebSocket (auth via query `token`) |
| `POST` | `/api/chat/messages` | Enviar mensaxe (fallback REST) |
| `GET` | `/api/chat/messages` | Historial paginado |
| `PATCH` | `/api/chat/messages/{id}/read` | Marcar como lido |

### Tipos de mensaxe

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

- Intercambio de chaves X25519 vía `/api/users/{id}/keys`
- Chaves públicas gardadas en `UserKey` (unha chave activa por usuario)
- Encriptación/descriptación no frontend (`e2ee_service.dart`)

---

## Subida de archivos

### Subida de avatar

```
POST /api/uploads/avatar
Content-Type: multipart/form-data
Authorization: Bearer <token>

file: <image/*>
```

- Gardado en `backend/uploads/avatars/{user_id}_{uuid}.{ext}`
- Servido de forma estática en `/uploads/avatars/...`
- Tamaño máximo: 10 MB (aplicado por `RequestSizeLimitMiddleware`)

---

## Endpoints de administración

Requere `role=admin` (probado en `admin_service.py`):

| Endpoint | Descrición |
|----------|------------|
| `GET /api/admin/stats` | Estatísticas da plataforma |
| `GET /api/admin/tables` | Contos de filas por táboa |
| `GET /api/admin/audit-log` | Rastro de auditoría (filtros `action`, `actor_user_id`) |
| `POST /api/admin/reset` | `drop_all + create_all` (só no-prod) |

---

## Probas

```bash
cd backend

# Executar todas as probas
python -m pytest tests/ -x -q --tb=short

# Executar con cobertura
python -m pytest tests/ --cov=app --cov-report=term-missing

# Proba específica
python -m pytest tests/test_festivals.py -v
```

**Configuración de probas** (`pyproject.toml` / `pytest.ini`):

```ini
[tool.pytest.ini_options]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_functions = test_*
```

**Fixos** (`tests/conftest.py`):
- `db_session` — sesión SQLite en memoria
- `client` — `AsyncClient` (httpx) contra a app de probas
- `auth_headers` — cabeceiros xa autenticados

---

## Lint e formatado

```bash
# Comprobar
ruff check .

# Fix auto-arreglable
ruff check . --fix

# Formatar
ruff format .
```

**Configuración** (`pyproject.toml`):

```toml
[tool.ruff]
line-length = 120
target-version = "py312"
select = ["E", "F", "I", "UP", "B", "C4", "PTH", "T20", "SIM", "ARG"]
ignore = ["E501", "SIM102", "SIM103"]
```

---

## Fluzo de desenvolvemento

### Desenvolvemento local

```bash
# Terminal 1: Backend
cd backend
python -m uvicorn app.main:app --reload

# Terminal 2: Frontend (se necesario)
cd frontend
flutter run -d web-server --web-port 3000 --dart-define=BACKEND_URL=http://localhost:8000/api
```

### Desenvolvemento con Docker

```bash
# Desde a raíz do proxecto
docker compose up        # Backend:8000, Frontend:3000
docker compose --profile db up  # + MariaDB:3306
```

### Carga inicial da base de datos

Non hai script de seed: en desenvolvemento a app crea o admin inicial (`admin` /
`setup`, cambia o contrasinal ao entrar) e as táboas mediante `create_all`. En produción os
datos chegoun via a API e o esquema só mediante Alembic.

### Comandos habituales

```bash
# Xerar adaptadores Hive (frontend)
cd frontend && flutter pub run build_runner build --delete-conflicting-outputs

# Executar migracións
cd backend && alembic upgrade head

# Crear migración
cd backend && alembic revision --autogenerate -m "add column x"

# Exportar SQLite → MariaDB
cd backend && python tools/export_sqlite_to_mariadb.py

# Importar MariaDB → SQLite
cd backend && python tools/import_mariadb_to_sqlite.py
```

---

## Estrutura do proxecto

```
backend/
├── app/
│   ├── models/              # 40 modelos SQLAlchemy (+ base.py)
│   ├── schemas/             # 37 esquemas Pydantic
│   ├── servizos/            # 43 servizos de lóxica de negócios
│   ├── routers/             # 40 routers API (38 con APIRouter)
│   ├── chat_backend/        # Implementación WebSocket do chateo
│   ├── auth.py              # Autenticación JWT + sesión
│   ├── config.py            # Pydantic Settings
│   ├── database.py          # Motor, SessionLocal, get_db()
│   ├── main.py              # App FastAPI, middleware, routers
│   ├── rate_limiter.py      # Limite de peticións SQLite
│   ├── enums.py             # Enums compartidos
│   └── scripts/             # Scripts de seed/migración
├── alembic/                 # Migracións (36 versións)
├── tools/                   # Scripts de exportación/importación
├── tests/                   # Probas pytest (47 arquivos, 1439 funcións de proba)
├── uploads/                 # Arquivos subidos estáticos
├── .env.example             # Template de configuración
├── requirements.txt         # Dependencias de produción
├── requirements-dev.txt     # Dependencias de desenvolvemento (pytest, ruff)
├── pyproject.toml           # Configuración Ruff, pytest
└── pytest.ini               # Configuración pytest
```

Documentación en `docs/gl/BACKEND.md` (este arquivo) e `docs/gl/DATABASE.md`.

---

## Desployo

### Docker (Produción)

```yaml
# docker-compose.yml usa --profile prod
docker compose --profile prod up -d
```

Servizos:
- `backend-prod` — FastAPI (traballadores Uvicorn) en :8000
- `frontend-prod` — Nginx + Flutter web en :80
- `db` — MariaDB 11 (proba de estado)

Perfís dispoñibles:
- `dev` (predeterminado): servidores de desenvolvemento backend e frontend
- `db`: engade o contedor MariaDB
- `prod`: pila de produción con nginx

### Variables de entorno (Produción)

```env
DATABASE_URL=mariadb+pymysql://user:pass@db:3306/clakettes_db
SECRET_KEY=<64-char-urlsafe>
CORS_ORIGINS=https://app.example.com
```

### Proba de estado

```bash
curl http://localhost:8000/health
# {"status": "healthy"}
```

---

## Lista de comprobación de seguridade

- [ ] Cambia `SECRET_KEY` en produción
- [ ] Establécese `CORS_ORIGINS` en dominios específicos
- [ ] Use MariaDB (non SQLite) en produción
- [ ] Habilita HTTPS (proxy inverso: nginx/Traefik)
- [ ] Configura os hosts permitidos en `TrustedHostMiddleware`
- [ ] Rota as chaves JWT periódicamente
- [ ] Vigila os rexistros do límite de peticións
- [ ] Revisa o contrasinal do usuario admin despois do primeiro acceso

---

## Ampliar a API

### Engadir un recurso novo

1. **Modelo** — `app/models/new_resource.py` (herda `BaseModel`)
2. **Esquema** — `app/schemas/new_resource.py` (Pydantic)
3. **Servizo** — `app/services/new_resource_service.py` (extende `BaseService`)
4. **Router** — `app/routers/new_resource.py` (incluír en `main.py`)
5. **Migración** — `alembic revision --autogenerate -m "add new_resource"`
6. **Probas** — `tests/test_new_resource.py`

### Engadir un endpoint personalizado a un router existente

```python
# No arquivo do router
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

## Solución de problemas

| Problema | Solución |
|----------|----------|
| `ModuleNotFoundError: app` | Executar desde o directorio `backend/` ou `PYTHONPATH=backend` |
| `sqlite3.OperationalError: database is locked` | Escritor único; asegúrese de que non hai procesos obsoletos |
| `alembic: Can't locate revision` | Elimine `alembic/versions/`, execute `alembic revision --autogenerate -m "init"` |
| `JWTError: Signature verification failed` | `SECRET_URL` incompatibles entre o entorno e o proceso en execución |
| `429 Too Many Requests` | Límite de peticións alcanzado; espere 60s ou estableza `TESTING=true` |
| WebSocket 403 | Token expirado; use un token de acceso válido en `?token=` |
| Erro CORS | Comprobe que `CORS_ORIGINS` en `.env` corresponde co orixe do frontend |

---

## Referencias

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [Pydantic v2](https://docs.pydantic.dev/latest/)
- [Alembic](https://alembic.sqlalchemy.org/)
- [python-jose](https://github.com/mpdavis/python-jose)
- [passlib](https://passlib.readthedocs.io/)