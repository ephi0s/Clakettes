# Clakettes

Plataforma multiplataforma para la gestión de festivales de cine y cortos express

[![Licencia MIT](https://img.shields.io/badge/Licencia-MIT-green)](LICENSE)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)](https://fastapi.tiangolo.com/)
[![Flutter](https://img.shields.io/badge/Frontend-Flutter-blue)](https://flutter.dev/)
[![WCAG](https://img.shields.io/badge/Accessibility-WCAG%202.1-success)](https://www.w3.org/WAI/WCAG21/quickref/)
[![i18n](https://img.shields.io/badge/i18n-EN%2FES%2FFR%2FDE%2FIT%2FCA%2FEU%2FGL%2FOC-blue)](https://flutter.dev/docs/development/accessibility-and-localization/internationalization)

## Descripción

Clakettes es una aplicación multiplataforma desarrollada en **Flutter** con backend en **FastAPI** que permite gestionar festivales de cine, publicar cortometrajes en concursos de cortos express, crear perfiles especializados para profesionales de la industria y facilitar el contacto entre usuarios.

> **Para desarrolladores:** Consulta [`AGENTS.md`](AGENTS.md) para documentación técnica detallada, comandos de setup y arquitectura interna.

---

## Características principales

### Gestión de festivales
- Gestión integral de festivales de cine y convocatorias (cada festival puede tener 0, 1 o varias convocatorias)
- Localizaciones con geolocalización, etiquetas tipo hashtag categorizables
- Publicación de imágenes y mensajes cortos en perfiles
- Comités de festival con roles y miembros asignables
- Delegaciones de roles entre usuarios

### Concursos express
- Concursos de cortos express con geolocalización de participantes
- Organización para creación de reportajes e interconexión de grupos de grabación

### Perfiles especializados
Roles soportados: sonidista, actor/actriz, director/directora, iluminación, script, guionista, utillero/utillera, vestuario, maquillaje y peluquería, figurante, doblador/dobladora, editor/montador/editora/montadora, folley, director/directora de festival, prensa, productora, distribuidora, entre otros

### Palmarés
- Vinculado a festivales de la plataforma (tanto para perfiles de festivales como de usuarios)
- Posibilidad de referenciar palmarés externos mediante enlaces

### Privacidad
- Perfiles públicos y privados para usuarios y festivales
- Control granular de qué información hacer pública (email, bio, ubicación)

### Chat
- Chat P2P y grupal
- Filtrado de usuarios por rol en cada festival
- Cifrado E2EE (pointycastle + X25519)
- WebSocket + REST dual backend

### Localizaciones
- Sección de localizaciones con mapas interactivos (flutter_map + latlong2)
- Geolocalización de participantes (geolocator)

### Vídeos
- Subida de vídeos de usuarios a festivales
- Los festivales pueden mostrar vídeos de convocatorias, contenido promocional, publicitario o funcional

### Modo offline
- Almacenamiento local con Hive
- Sincronización automática con el backend al recuperar conexión
- Cola de sincronización (SyncQueue) con HMAC

### Multiplataforma
- Soporte para Web, Android, iOS y escritorio (Windows, macOS, Linux)
- Navegación adaptativa: NavigationRail (>800px) / NavigationBar (<800px)

### Filtrado
- Usuarios pueden formar parte de 0, 1 o varios festivales
- Filtrado por rol de usuario en cada festival

---

## Accesibilidad y Localización

### Accesibilidad (WCAG 2.1 / ARIA)

La aplicación cumple con los estándares de accesibilidad WCAG 2.1 mediante:

| Característica | Detalle |
|----------------|---------|
| **Widgets Semantics** | 94+ widgets `Semantics` distribuidos en toda la app para soporte de lectores de pantalla (VoiceOver, TalkBack) |
| **Widgets reutilizables accesibles** | En `lib/widgets/reusable_widgets.dart`: `ProfileAvatar`, `InfoRow`, `StatusIndicator`, `ListItemCard`, `SemanticHeader`, `SemanticTextField` |
| **Tooltips** | 26+ tooltips en elementos interactivos para contexto adicional |
| **ExcludeSemantics** | Usado estratégicamente para evitar anuncios redundantes de iconos decorativos (8+ instancias) |
| **SnackBarBehavior.floating** | Para mejor visibilidad (29+ ocurrencias) |
| **Validación de formularios** | `autovalidateMode: AutovalidateMode.onUserInteraction` con mensajes localizados |
| **Navegación por teclado** | `TextInputAction` (next, done) y callbacks `onSubmitted` |
| **Contraste de colores** | Compatible con Material 3 y modo oscuro |

### Internacionalización (i18n)

La aplicación soporta **9 idiomas** con **71+ cadenas traducidas** cada uno:

| # | Idioma | Código | Archivo |
|---|--------|--------|---------|
| 1 | Inglés | `en` | `assets/l10n/app_en.arb` |
| 2 | Español | `es` | `assets/l10n/app_es.arb` |
| 3 | Francés | `fr` | `assets/l10n/app_fr.arb` |
| 4 | Alemán | `de` | `assets/l10n/app_de.arb` |
| 5 | Italiano | `it` | `assets/l10n/app_it.arb` |
| 6 | Catalán | `ca` | `assets/l10n/app_ca.arb` |
| 7 | Euskera | `eu` | `assets/l10n/app_eu.arb` |
| 8 | Gallego | `gl` | `assets/l10n/app_gl.arb` |
| 9 | Aranés/Occitano | `oc` | `assets/l10n/app_oc.arb` |

**Implementación:**
- Detección automática del idioma del sistema operativo (sin selector en la UI)
- Implementación manual vía `lib/l10n/app_localizations.dart` (238 líneas, sin `gen-l10n`)
- Fallback automático al inglés si el idioma no está soportado
- Uso de `AppLocalizations.of(context)` en todas las pantallas
- Interpolación de parámetros (`{param}`) en cadenas
- JSON anidado para roles/validación

**Elementos traducidos (71+ cadenas por idioma):**
- Etiquetas de UI: `appTitle`, `festivals`, `users`, `shortFilms`, `chat`, `locations`, `profile`
- Campos de formulario: `username`, `email`, `fullName`, `role`, `bio`, `password`
- Mensajes de validación: `required`, `emailInvalid`, `minLength`, `maxLength` (con valores parametrizados)
- Nombres de roles: `admin`, `organizer`, `user`, `jury` (estructura JSON anidada)
- Etiquetas de estado: `active`/`inactive`, `public`/`private`
- Botones de acción: `edit`, `save`, `cancel`, `accept`, `delete`, `refresh`, `search`, `filter`
- Mensajes de éxito/error: `userCreated`, `profileUpdated`, `confirmDelete`
- Elementos de chat: `sendMessage`, `writeMessage`, `welcomeChat`, `attachFile`, `groupChats`

---

## Arquitectura técnica

### Backend (Python + FastAPI)

Arquitectura escalable en capas:

```
Routers (FastAPI) → Services (Lógica de negocio) → Models (SQLAlchemy)
```

**Componentes principales:**

| Componente | Ubicación | Descripción |
|------------|-----------|-------------|
| **API Routers** | `backend/app/routers/` | Endpoints RESTful con paginación y filtros (33 routers) |
| **Services Layer** | `backend/app/services/` | Capa de lógica de negocio con CRUD genérico y operaciones específicas (29 servicios) |
| **Schemas** | `backend/app/schemas/` | Modelos Pydantic centralizados con validación de datos (30 esquemas) |
| **Models** | `backend/app/models/` | Modelos SQLAlchemy (34 modelos, heredan de `BaseModel`) |
| **Database** | `backend/app/database.py` | SQLAlchemy con soporte para SQLite (dev) y MariaDB (prod) |
| **Migrations** | `backend/alembic/` | Alembic para control de versiones de esquema de BD (15 migraciones) |
| **Auth** | `backend/app/auth.py` | JWT (JSON Web Tokens) con bcrypt para hash de contraseñas |
| **Rate Limiter** | `backend/app/rate_limiter.py` | SQLite-backed (100 req/60s) |
| **Config** | `backend/app/config.py` | Configuración via Pydantic Settings (`.env`) |
| **Chat Backend** | `backend/app/chat_backend/` | Chat en tiempo real (WebSocket + REST) |

**API Endpoints (23 grupos de routers):**

| Recurso | Endpoints |
|---------|-----------|
| Festivals | CRUD `/api/festivals/` |
| Users | CRUD `/api/users/`, login, refresh |
| Short Films | CRUD `/api/shortfilms/` |
| Chat | CRUD `/api/chat/messages`, mark read, WebSocket |
| Auth | login/refresh `/api/users/login` |
| Auth Sessions | list/revoke `/api/auth/sessions` |
| Notifications | CRUD `/api/notifications/`, unread count |
| User-Festival | join/leave/members `/api/festivals/{id}/` |
| Search | `GET /api/search/` |
| Uploads | `POST /api/uploads/avatar` |
| Admin | stats, activity, seed data `/api/admin/` |
| Roles, Groups, Dependencies, Conflicts | CRUD en `roles.py` bajo `/api` |
| Events | CRUD + tickets/seats/reservations/attendees `/api/events/` |
| Channels | CRUD + join/leave/messages `/api/channels/` |
| E2EE Keys | gestión de claves públicas `/api/users/{id}/keys` |
| Locations | CRUD + tags/images/relations `/api/locations/` |
| Participant Tags | Global + festival config `/api/` |
| User Roles | Assign/manage roles `/api/` |
| User Aliases | Display name aliases `/api/` |
| Validation Rules | Dynamic form validation `/api/` |
| Registration Forms | Festival registration flows `/api/` |
| Role Groups | Group roles `/api/` |
| Committees | Festival committees `/api/` |
| Delegations | Role delegations `/api/` |
| Form Definitions | Form builder `/api/` |
| ShortFilm Locations | Link shortfilms to locations `/api/shortfilms/{id}/locations/` |
| Location Tags/Images/Relations | Nested under `/api/locations/{id}/` |

Ver `backend/app/main.py` para la lista completa de routers registrados.

### Frontend (Flutter)

| Área | Tecnología / Patrón |
|------|---------------------|
| **State Management** | Singletons (AuthService, ApiService, ConnectivityMonitor, OfflineCacheService, SyncQueueService, LocaleService) + `StatefulWidget.setState()` + Streams — **NO Provider, NO flutter_it** |
| **Local Storage** | Hive para modo offline + sync queue |
| **Chat** | WebSocket + REST dual backend, con cifrado E2EE (pointycastle) |
| **Maps** | flutter_map + latlong2 + geolocator |
| **Internacionalización** | 9 idiomas (EN, ES, FR, DE, IT, CA, EU, GL, OC) manual, vía ARB files |
| **Accesibilidad** | Cumplimiento WCAG/ARIA con widgets Semantics (94+) |
| **Responsive** | Adaptativo para móvil (NavigationBar) y escritorio (NavigationRail) |
| **Theming** | Material 3 con soporte para modo oscuro (seed color #B8956E) |

---

## Tecnologías

### Backend
| Categoría | Tecnología | Versión |
|-----------|------------|---------|
| Framework | FastAPI | 0.110.0+ |
| ORM | SQLAlchemy | 2.0.51 (34 modelos) |
| Validación | Pydantic | 2.5.3+ + Pydantic Settings 2.1.0+ |
| Base de datos | SQLite (dev) / MariaDB (prod) | PyMySQL 1.1.0+ |
| Migraciones | Alembic | 1.13.0+ (15 migraciones) |
| Autenticación | python-jose + passlib[bcrypt] | JWT 30 min + refresh 30 días |
| Rate limiting | SQLite-backed | 100 req/60s |
| Chat tiempo real | WebSocket + REST | - |
| Geo | geopy | 2.4.0+ |
| Servidor | Uvicorn | ASGI |
| Testing | pytest + httpx | asyncio_mode = auto |
| Lint/Format | Ruff | line-length 120 |

### Frontend
| Categoría | Tecnología |
|-----------|------------|
| Framework | Flutter 3.0+ (web, Windows, Android, iOS, macOS, Linux) |
| Almacenamiento | Hive Flutter + hive_generator + build_runner |
| Estado | Singletons + setState() + Streams (NO Provider, NO flutter_it) |
| Red | http + web_socket_channel + connectivity_plus |
| Multimedia | video_player, image_picker |
| Ubicación | geolocator + flutter_map + latlong2 + flutter_map_cancellable_tile_provider |
| Chat | WebSocket + REST, E2EE (pointycastle + crypto) |
| Notificaciones | flutter_local_notifications |
| URLs | url_launcher |
| IDs | uuid |
| Internacionalización | flutter_localizations + intl (9 idiomas, manual sin gen-l10n) |
| Accesibilidad | 94+ Semantics widgets, 26+ Tooltips, WCAG 2.1 |
| Lint | flutter analyze |

---

## Requisitos previos

- **Python 3.12+**
- **Flutter SDK** (para desarrollo frontend)
- **MariaDB** (opcional, para producción)
- **Docker Desktop** (opcional, para desarrollo contenerizado)

---

## Instalación y ejecución

### Lanzamiento rápido (scripts)

| Script | Uso | Descripción |
|--------|-----|-------------|
| `start.bat` / `start.ps1` | `start.bat` | Backend + frontend Windows desktop |
| | `start.bat --web` | Backend + frontend web (con Brave/Chrome) |
| | `start.bat --dev` | Modo desarrollo (default) |
| | `start.bat --final` | Build + serve producción |
| | `start.bat --no-backend` | Solo frontend |
| | `start.bat --no-frontend` | Solo backend |
| | `start.bat --mariadb` | Incluye MariaDB (Docker profile db) |
| | `start.bat --migrate` | Ejecuta migraciones Alembic |
| | `start.bat --test-migration` | Prueba migración completa con MariaDB |
| | `start.bat --test-backend` | Ejecuta tests backend (pytest) |
| | `start.bat --test-frontend` | Ejecuta tests frontend (flutter test) |
| | `start.bat --build` | `docker compose build dev` |
| | `start.bat --build-all` | Construye paquetes distribubles (`tools\build-all.ps1`) |
| | `start.bat --build-frontend` | Construye solo frontend (Docker) |
| | `start.bat --build-backend` | Construye solo backend (Docker) |
| | `start.bat --kill` | Mata procesos + `docker compose down` |
| | `start.bat --help` | Muestra ayuda |

Los scripts detectan automáticamente Brave/Chrome y establecen `CHROME_EXECUTABLE`. Crean `.venv` y ejecutan `flutter pub get` automáticamente.

### Backend (manual)

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # Configurar variables de entorno
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

El backend estará disponible en `http://localhost:8000` con documentación interactiva en:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Frontend (manual)

```bash
cd frontend
flutter pub get
```

**Web (con Brave o Chrome):**
```bash
set CHROME_EXECUTABLE="C:\Program Files\BraveSoftware\Brave-Browser-Beta\Application\brave.exe"
flutter run -d chrome
```

**Windows desktop:**
```bash
flutter run -d windows
```

**Generación de código Hive:**
```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

### Navegadores basados en Chromium

Si usas Brave, Edge u otro navegador Chromium, establece la variable de entorno `CHROME_EXECUTABLE`:

```cmd
:: CMD
set CHROME_EXECUTABLE="C:\Program Files\BraveSoftware\Brave-Browser-Beta\Application\brave.exe"
flutter run -d chrome
```

```powershell
# PowerShell
$env:CHROME_EXECUTABLE="C:\Program Files\BraveSoftware\Brave-Browser-Beta\Application\brave.exe"; flutter run -d chrome
```

Para hacerlo permanente (ámbito de usuario):
```powershell
[System.Environment]::SetEnvironmentVariable("CHROME_EXECUTABLE", "C:\Program Files\BraveSoftware\Brave-Browser-Beta\Application\brave.exe", "User")
```

### Migraciones de base de datos (producción)

```bash
cd backend
alembic upgrade head
```

---

## Configuración

Editar `backend/.env` para configurar:

| Variable | Descripción | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Conexión a base de datos | `sqlite:///./data/clakettes.db` |
| `SECRET_KEY` | Clave secreta para JWT | **Cambiar en producción** |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiración access token | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Expiración refresh token | `30` |
| `CORS_ORIGINS` | Orígenes permitidos (CSV) | `*` |
| `PORT_BACKEND` | Puerto backend | `8000` |
| `PORT_FRONTEND` | Puerto frontend dev | `3000` |
| `PORT_FRONTEND_PROD` | Puerto frontend prod | `80` |
| `BACKEND_URL` | URL base del backend (Flutter) | `http://localhost:8000/api` |

**Ejemplo `.env` producción:**
```env
DATABASE_URL=mariadb+pymysql://user:pass@db:3306/clakettes_db
SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30
CORS_ORIGINS=https://tudominio.com,https://app.tudominio.com
```

---

## Estructura del proyecto

```
cine/
├── backend/                     # Python + FastAPI
│   ├── app/
│   │   ├── models/              # 34 modelos SQLAlchemy
│   │   ├── schemas/             # 30 esquemas Pydantic
│   │   ├── services/            # 33 servicios de negocio
│   │   ├── routers/             # 33 routers API
│   │   ├── auth.py              # Autenticación JWT + sesiones
│   │   ├── config.py            # Configuración (pydantic-settings)
│   │   ├── database.py          # Conexión y sesiones SQLAlchemy
│   │   ├── main.py              # Entrada FastAPI
│   │   ├── rate_limiter.py      # Rate limiting (SQLite)
│   │   ├── enums.py             # Enums compartidos
│   │   └── chat_backend/        # Chat en tiempo real (WebSocket + REST)
│   ├── alembic/                 # Migraciones de base de datos (9 versiones)
│   ├── tools/                   # Scripts de utilidad (export/import BD)
│   ├── tests/                   # Tests del backend (22 archivos)
│   ├── uploads/avatars/         # Archivos subidos
│   ├── DATABASE.md              # Documentación del esquema de BD
│   ├── BACKEND.md               # Documentación técnica backend
│   ├── .env.example             # Plantilla de configuración
│   ├── requirements.txt         # Dependencias Python
│   ├── requirements-dev.txt     # Dependencias de desarrollo
│   ├── pyproject.toml           # Configuración Ruff, pytest
│   └── pytest.ini               # Configuración pytest
├── frontend/                    # Flutter
│   ├── lib/
│   │   ├── l10n/               # Código Dart de internacionalización (manual)
│   │   ├── models/              # 40 modelos Dart (Hive + code gen)
│   │   ├── screens/             # 36 pantallas Flutter
│   │   ├── widgets/             # 24 widgets reutilizables
│   │   ├── services/            # 17 servicios + api/ (9 dominios)
│   │   ├── main.dart            # Entry point (Material 3, dark mode)
│   │   ├── main_scaffold.dart   # Navegación adaptativa (Rail/Bar + Drawer)
│   │   └── auth_wrapper.dart    # Control de autenticación
│   ├── assets/l10n/             # Archivos ARB de traducción (9 idiomas)
│   ├── web/                     # Configuración específica web
│   ├── test/                    # Tests Flutter (1 archivo base)
│   ├── pubspec.yaml             # Dependencias Flutter
│   ├── analysis_options.yaml    # Reglas de análisis Dart
│   └── build.yaml               # Configuración build_runner
├── .agents/skills/              # 18 skills de desarrollo Flutter/Backend
├── .opencode/                   # Configuración de OpenCode
├── AGENTS.md                    # Documentación para agentes IA
├── MEJORAS.md                   # Mejoras propuestas y análisis técnico
├── start.bat / start.ps1 / start.sh  # Scripts de lanzamiento multiplataforma
├── docker-compose.yml           # Orquestación multi-contenedor
├── .gitlab-ci.yml               # GitLab CI/CD
├── .github/workflows/ci.yml     # GitHub Actions CI
├── tools/                       # Scripts de build multiplataforma
└── README.md                    # Este archivo
```

---

## Desarrollo

### Flujo de trabajo recomendado

1. **Iniciar entorno de desarrollo:**
   ```bash
   start.bat --dev    # O start.ps1 -Dev
   ```

2. **Backend:** Los cambios en `backend/app/` se recargan automáticamente (uvicorn --reload)

3. **Frontend:** Hot reload disponible en `flutter run -d chrome` o `flutter run -d windows`

4. **Generar código Hive** (tras modificar modelos):
   ```bash
   cd frontend && flutter pub run build_runner build --delete-conflicting-outputs
   ```

5. **Ejecutar tests:**
   ```bash
   # Backend
   cd backend && python -m pytest tests/ -x -q --tb=short
   
   # Frontend
   cd frontend && flutter test
   ```

6. **Linting:**
   ```bash
   # Backend
   cd backend && ruff check .
   
   # Frontend
   cd frontend && flutter analyze
   ```

### Comandos útiles Docker

```bash
# Desarrollo (default profile) - Backend:8000, Frontend:3000
docker compose up

# Con MariaDB - + MariaDB:3306
docker compose --profile db up

# Producción - Backend, Frontend (nginx), MariaDB
docker compose --profile prod up -d

# Migraciones
docker compose run --rm backend alembic upgrade head

# Tests en Docker
docker compose run --rm backend python -m pytest tests/ -x -q --tb=short
docker compose run --rm frontend flutter test

# Build imágenes
docker compose build
```

### Migración SQLite ↔ MariaDB

```bash
# Dev → Prod (SQLite to MariaDB)
cd backend
python export_sqlite_to_mariadb.py

# Prod → Dev (MariaDB to SQLite)
python import_mariadb_to_sqlite.py
```

Ver `backend/DATABASE.md` para detalles del esquema y notas de migración.

---

## Testing

### Backend
```bash
cd backend
# Tests unitarios + integración
python -m pytest tests/ -x -q --tb=short

# Con cobertura
python -m pytest tests/ --cov=app --cov-report=term-missing
```

### Frontend
```bash
cd flutter
# Tests de widget
flutter test

# Tests de integración (requiere dispositivo/emulador)
flutter test integration_test/
```

---

## CI/CD

### GitHub Actions (`.github/workflows/ci.yml`)
- **Lint**: `ruff check .` (backend) + `flutter analyze` (frontend)
- **Test**: `pytest` + `flutter test`
- **Docker Build**: Multi-stage build en push/PR a main

### GitLab CI (`.gitlab-ci.yml`)
- Stages: lint → test → build
- Cache para pip, pub, dart_tool
- Docker build solo en branch `main`

---

## Despliegue

### Docker Compose (Producción)

```bash
# Configurar variables de entorno en .env
docker compose --profile prod up -d
```

Servicios en producción:
- **Backend**: Puerto 8000 (interno), expuesto vía reverse proxy
- **Frontend**: Puerto 80 (nginx sirviendo build web estático)
- **MariaDB**: Puerto 3306 (interno)

### Builds distribubles

```bash
# Todo (requiere Docker + Windows containers para Windows builds)
start.bat --build-all

# O manualmente:
./tools/build-all.ps1
```

Genera en `builds/`:
- `frontend-web/` — Flutter web build
- `frontend-windows-x86_64/` — Windows 64-bit
- `frontend-linux-x86_64/` — Linux 64-bit bundle / AppImage
- `frontend-android/` — APK y AAB
- `backend-linux-x86_64/` — PyInstaller binary
- *(macOS/iOS requieren máquina macOS nativa)*

---

## Accesibilidad - Guía rápida para desarrolladores

Al añadir nuevos widgets:

1. **Usa `Semantics`** para elementos interactivos sin etiqueta intrínseca
2. **`SemanticHeader`** para encabezados de sección (screen readers)
3. **`SemanticTextField`** para inputs de formulario
4. **`ExcludeSemantics`** para iconos decorativos
5. **Tooltip** en botones icon-only
6. **`SnackBarBehavior.floating`** para snackbars
7. **`autovalidateMode: AutovalidateMode.onUserInteraction`** en formularios
8. **`TextInputAction.next` / `done`** + `onSubmitted` para navegación teclado
9. Verifica contraste en modo claro/oscuro (Material 3 lo gestiona automáticamente)

Ver `lib/widgets/reusable_widgets.dart` para widgets base accesibles.

---

## Internacionalización - Guía rápida

Para añadir traducciones:

1. Edita `assets/l10n/app_en.arb` (fuente)
2. Añade la clave y valor en inglés
3. Repite en los otros 8 archivos `.arb`
4. Usa interpolación: `"hello": "Hello {name}!"`
5. En Dart: `AppLocalizations.of(context)!.hello(name: "Juan")`

Estructura anidada para roles:
```json
"roles": {
  "admin": "Administrador",
  "organizer": "Organizador"
}
```
Acceso: `AppLocalizations.of(context)!.roles['admin']`

---

## Licencia

Este proyecto está bajo la **Licencia MIT**.

Consulta el archivo [LICENSE](LICENSE) para más detalles.

---

## Estado del proyecto

🚧 **En desarrollo activo** — Backend con arquitectura en capas (31 modelos, 30 esquemas, 29 servicios, 32 routers), frontend Material 3 con dark mode, accesibilidad WCAG 2.1 completa, internacionalización 9 idiomas (manual), modo offline con Hive + SyncQueue HMAC.

**Roadmap próximo:**
- [ ] Tests de integración frontend (actualmente 1 test base)
- [ ] Tests backend para routers sin cobertura (auth_sessions, committees, delegations, role_groups, shortfilm_locations, location_images, location_relations, location_tags, uploads, search, user_festival, chat/WS)
- [ ] Notificaciones push (Firebase/APNs)
- [ ] AppImage Linux firmado
- [ ] Windows MSI installer
- [ ] Documentación API OpenAPI exportable
- [ ] Resolver ~25 endpoints sin autorización por rol (ver MEJORAS.md)
- [ ] Migrar 17 endpoints con paginación en memoria a BD
- [ ] Añadir índices en tablas calientes (Message, Festival, User)

---

## Contribuir

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'feat: añade nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

**Convenciones:**
- Commits: [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`)
- Lint: `ruff check .` (backend) / `flutter analyze` (frontend) deben pasar
- Tests: `pytest` / `flutter test` deben pasar