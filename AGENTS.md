# AGENTS.md

## Proyecto

Clakettes — Flutter (Material 3, dark mode) + FastAPI (gestión de festivales de cine). MIT.

## Arquitectura

### Backend (`backend/`)

- Python 3.12+, FastAPI, SQLAlchemy, SQLite (dev) / MariaDB (prod)
- Capas: Routers (`app/routers/`) → Services (`app/services/`) → Models (`app/models/`, con `base.py`) y Schemas (`app/schemas/`). Models y schemas usan `app.enums`
- Entry: `python -m uvicorn app.main:app --reload` (8000); usa `.venv/` si existe
- Auth: JWT (`POST /api/users/login`, 30 min, Bearer) + refresh token (30 d). Rate limit: 100/60s global, 600/60s en `/dav`, 5/300s login, 20/60s refresh, 3/300s reset. `TESTING` ∈ {1,true,yes,on} (helper `app.config.is_testing()`) desactiva límites y auto-migración
- Paginación: `?page=1&size=20`
- Migraciones: automáticas al arrancar (lifespan + sello de DB nuevas; `SKIP_AUTO_MIGRATE=1` para omitir) o manuales con `alembic upgrade head`. `python -m alembic` falla con cwd=backend (la carpeta `alembic/` oculta al paquete): usa `.venv/Scripts/alembic.exe` o la API interna `_alembic_api()`

### Frontend (`frontend/`)

- Flutter web/desktop/Android/iOS/macOS/Linux. SDK >=3.0.0 <4.0.0
- UI desde `material_ui`/`cupertino_ui` (Flutter 3.50+), no desde `package:flutter/material.dart`; los delegates viven en `GlobalMaterialLocalizations.delegates`
- Init: `main()` → `DatabaseService.init()` (boxes: festivals, users, shortfilms, messages) → OfflineCache, SyncQueue, NodeService, ConnectivityMonitor, LocaleService, NotificationService
- Estado: singletons + `setState()` + streams. Hive + SharedPreferences offline
- API: `api_service.dart`, base `http://localhost:8000/api`; override con `--dart-define=BACKEND_URL=...`
- Navegación: NavigationRail (>800px) / NavigationBar (<800px) + Drawer en `main_scaffold.dart`
- Widgets: `reusable_widgets.dart` (ProfileAvatar, InfoRow, StatusIndicator, ListItemCard, SemanticHeader, SemanticTextField) y el resto en `lib/widgets/`
- i18n: ARB en `frontend/assets/l10n/` con `app_en.arb` como fallback, `app_localizations.dart` manual, paridad con `test/l10n/arb_parity_test.dart`; `LocaleService` detecta el locale del SO y persiste el resuelto
- Code gen Hive: `flutter pub run build_runner build --delete-conflicting-outputs`

## Comandos rápidos

### Backend (`cd backend`)

```bash
python -m uvicorn app.main:app --reload          # entry (8000), usa .venv/ si existe
python -m pytest tests/ -x -q --tb=short          # en CI se añade -m "not interop"
ruff check . && ruff format --check .             # line-length 120
.venv/Scripts/alembic.exe upgrade head            # migraciones
```

### Frontend (`cd frontend`)

```bash
flutter test
flutter analyze
flutter pub run build_runner build --delete-conflicting-outputs
```

### Puertas de calidad (`tools/`)

```bash
tools/check.ps1 -Quick                              # o tools/check.sh --quick: ruff + analyze
tools/check.ps1                                     # completa: + pytest (sin interop) + flutter test
tools/check.ps1 -Backend -TestFilter patron         # filtro de tests: -k / --plain-name
python tools/gen_api.py --all --check               # verifica que las API.md estén regeneradas
```

### Solución de problemas

- Backend no arranca: verifica Python 3.12+ y `backend/.env`; ejecuta uvicorn directamente para ver el error
- App no conecta con la API: backend en `http://localhost:8000`, `BACKEND_URL` con `--dart-define`, API en `/docs`
- BBDD/migraciones: `alembic upgrade head`; SQLite ↔ MariaDB en `docs/es/USO.md` y `docs/es/DATABASE.md`
- Flutter: `flutter pub get`; code gen Hive/build_runner en `docs/es/ARQUITECTURA.md`

## Arranque (`.ps1` / `.sh`)

- `--dev` (default): backend + frontend + navegador de desarrollo | `--final`: build + serve | `--web`: modo local con navegador de desarrollo
- `--no-backend` / `--no-frontend` | `--kill`: mata procesos + `docker compose down`
- `--migrate`: alembic upgrade head | `--mariadb`: usa MariaDB
- `--test-backend` / `--test-frontend` | `--test-migration`: MariaDB + migrate + validate
- `--test-filter=EXPR` (o `-TestFilter EXPR`): pasa `-k` a pytest y `--plain-name` a Flutter
- `--build`: `docker compose build` | `--build-all`: vía `tools\build-all.ps1`
- `--install-missing`: instala deps bare-metal (winget/apt/dnf/brew + git clone); si no, guía por SO y pregunta
- Detecta Brave/Chrome para `CHROME_EXECUTABLE`; crea `.venv` y ejecuta `flutter pub get`
- Los launchers usan 65081/65080 por defecto; `docker compose` usa 8000/3000 salvo `PORT_BACKEND`/`PORT_FRONTEND`

## Despliegue

`docker compose --profile prod up -d` → backend + frontend (nginx) + MariaDB. Builds distribuidos (web, Windows, Linux, Android) con `.ps1 --build-all` y los scripts de `docs/es/HERRAMIENTAS.md`.

## CI

- `.github/workflows/ci.yml`: GitHub Actions (lint → test → docker build en push/PR)
- `.gitlab-ci.yml`: GitLab CI (ruff, flutter analyze, pytest, flutter test, docker build en main)
- Ambos CI ejecutan `python tools/gen_api.py --all --check` (job `docs-api`): las `API.md` deben estar regeneradas

## Grafos (`graphify-out/`)

- `graphify query "<pregunta>"`: responde sobre arquitectura sin leer archivos
- `graphify . --no-viz --code-only`: regenera sin `graph.html` y sin API key (omite docs/imágenes)
- `graphify-out/` está en `.gitignore`; no se sube al repositorio

## Documentación

- Índice por audiencia y docos canónicos en [docs/es/README.md](docs/es/README.md): [SEGURIDAD](docs/es/SEGURIDAD.md), [USO](docs/es/USO.md), [DATABASE](docs/es/DATABASE.md), [API](docs/es/API.md), [BACKEND](docs/es/BACKEND.md), [ARQUITECTURA](docs/es/ARQUITECTURA.md), [FUNCIONAL](docs/es/FUNCIONAL.md), [FEDERATION_PROTOCOL](docs/es/FEDERATION_PROTOCOL.md), [FEDERATION_SCHEMA](docs/es/FEDERATION_SCHEMA.md), [FEDERATION_SECURITY](docs/es/FEDERATION_SECURITY.md), [PUSH](docs/es/PUSH.md), [AUDITORIA](docs/es/AUDITORIA.md), [ADMINISTRACION](docs/es/ADMINISTRACION.md), [INFRAESTRUCTURA](docs/es/INFRAESTRUCTURA.md), [HERRAMIENTAS](docs/es/HERRAMIENTAS.md), [DESARROLLO](docs/es/DESARROLLO.md), [FEDERATION_CHAT_BROKER](docs/es/FEDERATION_CHAT_BROKER.md)
- Documentación en `docs/es/`, `docs/en/`, `docs/fr/`, `docs/de/`, `docs/it/`, `docs/ca/`, `docs/eu/`, `docs/gl/` y `docs/oc/`. `docs/es/` añade `AMENAZAS_NODOS_FEDERACION.md` y `MODELO_CONFIANZA_NODOS.md`
- Español canónico (estilo canario, ustedes): todo cambio en una doc en español se replica a todas las hermanas (`docs/<idioma>/X.md`, `README.<lang>.md`, `frontend/README.<lang>.md`)
- Al cambiar código que afecte a la documentación, actualiza en el mismo cambio endpoints (`python tools/gen_api.py --all`), estructura, flags de arranque, roadmap del README y variables de `.env.example`. Nunca dejes docs desfasadas; no mantengas recuentos de archivos ni de tests en las docs, se desactualizan solos

## Flujo de trabajo para agentes

### Al iniciar

```bash
git fetch origin
git status -sb
git log --oneline '@{u}..HEAD'
```

Si hay commits de `origin/main` que falten en local: `git pull --ff-only`. Si existe `TASKS.md`, léelo; elimina ítems completados y el archivo cuando quede vacío.

### Durante el trabajo

- Usa subagentes Explore en paralelo para búsquedas/lecturas previas; úsalos siempre que sea posible para ahorrar tokens
- Usa la CLI de `gh` para administrar el repositorio: inspeccionar workflows, runs y jobs, PRs, issues y ajustes de GitHub; prefiere `gh api` sobre peticiones web o `curl`
- Nunca escribas tokens, correos ni identificadores de cuenta en archivos del repositorio
- Búsquedas y reemplazos con `grep`/`edit` de OpenCode, nunca scripts auxiliares salvo que sea imprescindible
- Carga skills solo si la tarea lo pide:
  - Backend: `backend-python-fastapi-expert`
  - Ops: `docker-devops-expert`, `database-expert`, `quality-gate-ci`
  - Frontend: `flutter-apply-architecture-best-practices`, `flutter-material-3-theming`, `flutter-accessibility-wcag`, `flutter-localization-arb`, `flutter-offline-sync-hive`, `flutter-maps-geo-osm`
  - Resto de skills en `.agents/skills/`, incluido `docs-i18n-sync`

### Verificación

- Puerta única: `tools/check.ps1` / `tools/check.sh` (añade `-Quick`/`--quick` para solo ruff + analyze)
- Durante desarrollo: `ruff check .` / `flutter analyze` y, como mucho, tests puntuales. Corrige si falla
- Tests completos solo al terminar todos los cambios del área: `pytest tests/ -x -q --tb=short` (~30 min) y `flutter test` (lento)

### Estilo de respuesta

- 1-3 líneas; sin introducciones, resúmenes ni explicaciones; sin emojis
- Código solo en herramientas (write/edit), no en texto; sin comentarios en código salvo petición
- Tras editar, no expliques ni preguntes "X o Y?": asume
- PowerShell 5.1: `; if ($?) { }` en vez de `&&`
