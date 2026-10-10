# AGENTS.md

## Proyecto
Clakettes — Flutter (Material 3, dark mode) + FastAPI (gestión festivales cine). MIT.

## Backend (`backend/`)
- Python 3.12+, FastAPI, SQLAlchemy, SQLite (dev) / MariaDB (prod)
- Entry: `python -m uvicorn app.main:app --reload` (8000). Usa `.venv/` si existe.
- Migraciones: `alembic upgrade head` desde `backend/` (15 versiones)
- Capas: Routers (33) → Services (33) → Models (34). Models/Schemas via `app.enums`
- Auth: JWT (POST /api/users/login, 30 min, Bearer) + refresh token (30 d). Rate limit: 100/60s (SQLite)
- Paginación: `?page=1&size=20`
- Tests: `pytest tests/ -x -q --tb=short` (22 archivos, 1366 tests)
- Lint: `ruff format .` luego `ruff check .` (line-length 120)

## Frontend (`frontend/`)
- Flutter web/desktop/Android/iOS/macOS/Linux. SDK >=3.0.0 <4.0.0
- Entry: `main()` → `DatabaseService.init()` (boxes: festivals, users, shortfilms, messages). Luego OfflineCache, SyncQueue, ConnectivityMonitor, LocaleService.
- API: `api_service.dart` base `http://localhost:8000/api`. Config: `--dart-define=BACKEND_URL=...`
- Estado: singletons + setState() + streams. Hive + SharedPreferences offline.
- i18n: 9 locales (en,es,fr,de,it,ca,eu,gl,oc) ARB + `app_localizations.dart` manual (sin gen-l10n)
- Navegación: NavigationRail (>800px) / NavigationBar (<800px) + Drawer en `main_scaffold.dart`
- Widgets: `reusable_widgets.dart` (ProfileAvatar, InfoRow, StatusIndicator, ListItemCard, SemanticHeader, SemanticTextField) + 7 más
- Code gen Hive: `flutter pub run build_runner build --delete-conflicting-outputs`
- Tests: `flutter test` (1 test base) | Lint: `flutter analyze`

## Inicio (`start.bat` / `.ps1` / `.sh`)
- `--dev` (default): backend + frontend | `--final`: build + serve | `--web`: abre navegador
- `--no-backend` / `--no-frontend` | `--kill`: mata procesos + docker compose down
- `--migrate`: alembic upgrade head | `--mariadb`: usa MariaDB
- `--test-backend` / `--test-frontend` | `--test-migration`: MariaDB + migrate + validate
- `--build`: `docker compose build dev` | `--build-all`: via `tools\build-all.ps1`
- Detecta Brave/Chrome para `CHROME_EXECUTABLE`. Crea `.venv` + `flutter pub get`.

## CI
- `.github/workflows/ci.yml`: GitHub Actions (lint → test → docker build on push/PR)
- `.gitlab-ci.yml`: GitLab CI (ruff, flutter analyze, pytest, flutter test, docker build on main)

## Grafos (`graphify-out/`)
- `graphify query "<pregunta>"` responde sobre arquitectura sin leer archivos
- `graphify .` para regenerar (o skill graphify)

## Tareas pendientes
Si existe `TASKS.md`, léelo. Al completar ítems, elimínalos. Cuando vacío, elimínalo.
Ver `MEJORAS.md` para análisis técnico detallado (21 mejoras priorizadas).

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
- **ops**: docker-devops-expert, database-expert
- **flutter_it**: flutter-it, get-it-expert, watch-it-expert, listen-it-expert, command-it-expert, feed-datasource-expert, flutter-architecture-expert
- **frontend**: flutter-material-3-theming, flutter-accessibility-wcag, flutter-state-management-pattern, flutter-localization-arb
- skills en `.agents/skills/`. Cargar con `<skill name="...">`.
- Usa subagentes siempre que sea posible para ahorrar tokens
