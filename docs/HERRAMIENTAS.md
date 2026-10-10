# Herramientas build / test / dev — Clakettes

## Matriz de comandos

| Objetivo | Comando | Dónde |
|---|---|---|
| Dev backend+frontend | `.\start.ps1` / `./start.sh` | Raíz (Docker si disponible, local si no) |
| Solo backend / frontend | `-NoFrontend` / `-NoBackend` | `start.ps1` / `--no-frontend` en `start.sh` |
| Web en navegador | `-Web` | Solo modo local |
| Prod local (build web + serve) | `-Final` | `start.ps1` / `start.sh` |
| Tests backend | `-TestBackend` | pytest en `.venv` o Docker |
| Tests frontend | `-TestFrontend` | `flutter test` o Docker |
| Migraciones | `-Migrate` / `-TestMigration` (MariaDB) | alembic |
| APK Android | `flutter build apk --release --dart-define=BACKEND_URL=<url>` | `frontend/` |
| AppBundle (Play Store) | `flutter build appbundle --release --dart-define=BACKEND_URL=<url>` | `frontend/` |
| iOS/iPad (requiere macOS) | `tools/build-ios.sh` | Solo en Mac con Xcode |
| macOS / Windows / Linux | `tools/build-macos.sh` / `flutter build windows` / `flutter build linux` | Host correspondiente |
| Docker multi-target | `tools/build-all.ps1` | Requiere Docker |

## Mejoras aplicadas (09/10/2026)

1. **`.dockerignore` en los contextos de build** (`backend/`, `frontend/`).
   Antes solo existían en `backend/docker/` y `frontend/docker/`, que NO son el
   contexto de `docker-compose.yml` (`./backend`, `./frontend`). Cada
   `docker compose build` enviaba `.venv/` (cientos de MB), `.dart_tool/`,
   `build/`, `*.db` y `*.hive` al daemon. Ahora el contexto es mínimo.
   Excepción: `!pubspec.lock` se conserva para builds reproducibles.
2. **Config pytest unificada**: eliminado `backend/pytest.ini` (duplicaba y
   eclipsaba a `pyproject.toml`); toda la config vive en
   `[tool.pytest.ini_options]` (testpaths, patrones, markers).
3. **CI coherente**:
   - GitHub: Flutter `3.22.0` → `3.24.0` (igual que el Dockerfile);
     `flutter pub run` (obsoleto) → `dart run build_runner`.
   - GitLab `backend-test`: añadidos `TESTING=true` y `SECRET_KEY`
     (antes el rate limiter seguía activo en tests → 429 esporádicos).
   - GitLab `frontend-test`: añadida generación de adaptadores Hive antes
     de `flutter test` (paridad con GitHub).
   - `pip install ruff` → `pip install "ruff>=0.5.0"` (igual que
     `requirements-dev.txt`).
4. **Lints multiplataforma** (`analysis_options.yaml`): `avoid_print` y
   `avoid_web_libraries_in_flutter`. Verificado: `flutter analyze` limpio
   (el import condicional web/io es el patrón aceptado).
5. **Fix `onReorder` obsoleto** → `onReorderItem` (sin ajuste manual de
   índice); `flutter analyze` pasa de 1 info a 0 issues.

## Propuestas (no aplicadas, con motivo)

1. **Gate `ruff format --check` en CI**: bloqueado por ~249 violaciones
   E501/W292 existentes. Pasos: `ruff format .`, revisar diff,
   `ruff check --fix`, y entonces añadir el gate.
2. **Unificar `start.bat/.ps1/.sh`**: triplican la lógica de puertos/procesos.
   La vía realista es extraer la matriz de puertos a `tools/ports.*` o
   documentar un único entrypoint por OS, no reescribir los tres a la vez.
3. **Cobertura en CI** (`pytest --cov`, `flutter test --coverage` + lcov):
   útil cuando se amplíen tests de `syncAll` y routers sin cubrir (ver
   `MEJORAS.md` §20).
