# AGENTS.md

## Proyecto
Clakettes — Flutter (Material 3, dark mode) + FastAPI (gestión festivales cine). MIT.

## Backend (`backend/`)
- Python 3.12+, FastAPI, SQLAlchemy, SQLite (dev) / MariaDB (prod)
- Entry: `python -m uvicorn app.main:app --reload` (8000). Usa `.venv/` si existe.
- Migraciones: auto al arrancar (`alembic upgrade head` en lifespan + sello de DB nuevas; `SKIP_AUTO_MIGRATE=1` para omitir) o manual desde `backend/` (21 versiones). Ojo: `python -m alembic` falla con cwd=backend (la carpeta `alembic/` oculta al paquete); usa `.venv/Scripts/alembic.exe` o la API interna `_alembic_api()`
- Capas: Routers (36 archivos, 33 con APIRouter) → Services (36) → Models (34). Models/Schemas via `app.enums`
- Auth: JWT (POST /api/users/login, 30 min, Bearer) + refresh token (30 d). Rate limit: 100/60s (SQLite)
- Paginación: `?page=1&size=20`
- Tests: `pytest tests/ -x -q --tb=short` (37 archivos, ~1400 tests)
- Lint: `ruff check .` luego `ruff format --check .` (line-length 120)

## Frontend (`frontend/`)
- Flutter web/desktop/Android/iOS/macOS/Linux. SDK >=3.0.0 <4.0.0
- Entry: `main()` → `DatabaseService.init()` (boxes: festivals, users, shortfilms, messages). Luego OfflineCache, SyncQueue, ConnectivityMonitor, LocaleService.
- API: `api_service.dart` base `http://localhost:8000/api`. Config: `--dart-define=BACKEND_URL=...`
- Estado: singletons + setState() + streams. Hive + SharedPreferences offline.
- i18n: 9 locales (en,es,fr,de,it,ca,eu,gl,oc) ARB + `app_localizations.dart` manual (sin gen-l10n)
- Navegación: NavigationRail (>800px) / NavigationBar (<800px) + Drawer en `main_scaffold.dart`
- Widgets: `reusable_widgets.dart` (ProfileAvatar, InfoRow, StatusIndicator, ListItemCard, SemanticHeader, SemanticTextField) + 23 más (24 en `lib/widgets/`)
- Code gen Hive: `flutter pub run build_runner build --delete-conflicting-outputs`
- Tests: `flutter test` (69 archivos) | Lint: `flutter analyze`

## Inicio (`start.bat` / `.ps1` / `.sh`)
- `--dev` (default): backend + frontend | `--final`: build + serve | `--web`: abre navegador
- `--no-backend` / `--no-frontend` | `--kill`: mata procesos + docker compose down
- `--migrate`: alembic upgrade head | `--mariadb`: usa MariaDB
- `--test-backend` / `--test-frontend` | `--test-migration`: MariaDB + migrate + validate
- `--build`: `docker compose build dev` | `--build-all`: via `tools\build-all.ps1`
- Detecta Brave/Chrome para `CHROME_EXECUTABLE`. Crea `.venv` + `flutter pub get`.
- `--install-missing`: instala deps bare-metal (winget/apt/dnf/brew + git clone); si no, guía por SO + pregunta.

## CI
- `.github/workflows/ci.yml`: GitHub Actions (lint → test → docker build on push/PR)
- `.gitlab-ci.yml`: GitLab CI (ruff, flutter analyze, pytest, flutter test, docker build on main)

## Grafos (`graphify-out/`)
- `graphify query "<pregunta>"` responde sobre arquitectura sin leer archivos
- `graphify .` para regenerar (o skill graphify)

## Docs ([docs/es/README.md](docs/es/README.md))
- Índice por audiencia (usuario/admin/dev/IA); canónicos: [docs/es/SEGURIDAD.md](docs/es/SEGURIDAD.md), [docs/es/USO.md](docs/es/USO.md), [docs/es/DATABASE.md](docs/es/DATABASE.md), [docs/es/API.md](docs/es/API.md)
- La documentación es oro y va en español (estilo canario, ustedes): al cambiar
  código que la afecte, actualiza TODA la info pertinente en el mismo cambio —
  cifras (routers/servicios/modelos/migraciones/tests), endpoints nuevos o
  movidos (`python tools/gen_api.py --all` para `docs/<idioma>/API.md`), flags de arranque,
  roadmap del README y variables de `.env.example`. Nunca dejes docs desfasadas.
- La documentación vive en las carpetas `docs/es/`, `docs/en/`, `docs/fr/`,
  `docs/de/`, `docs/it/`, `docs/ca/`, `docs/eu/`, `docs/gl/` y `docs/oc/`.
  El español es canónico: todo cambio en una doc en español se replica a sus
  8 hermanas (`docs/<idioma>/X.md`, `README.<lang>.md`, `frontend/README.<lang>.md`).

## Tareas pendientes
Si existe `TASKS.md`, léelo. Al completar ítems, elimínalos. Cuando vacío, elimínalo.

## Subagentes
Usa Explore para búsquedas/lecturas previas. Llama en paralelo.

## Verificación post-task
- Frontend: `flutter analyze` | Backend: `ruff check .` o `pytest tests/ -x -q --tb=short`
Corrige si falla. Solo se ejecuta si se considera necesario.

## A tener en cuenta
- Responde en 1-3 líneas. Sin introducciones/resúmenes/explicaciones. Sin emojis.
- Código solo en herramientas (write/edit), no en texto.
- Tras editar, no expliques — sigue con la tarea. No preguntes "X o Y?" — asume.
- **PowerShell**: `; if ($?) { }` en vez de `&&` (PS 5.1)
- **Sin comentarios** en código salvo que el usuario lo pida
- **backend**: backend-python-fastapi-expert
- **ops**: docker-devops-expert, database-expert, quality-gate-ci
- **frontend**: flutter-material-3-theming, flutter-accessibility-wcag, flutter-state-management-pattern, flutter-localization-arb, flutter-offline-sync-hive, flutter-maps-geo-osm
- skills en `.agents/skills/` (18). Cargar con `<skill name="...">` solo si la tarea lo pide.
- Usa subagentes siempre que sea posible para ahorrar tokens
