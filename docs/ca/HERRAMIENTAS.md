# Eines build / test / dev — Clakettes

[ES](../es/HERRAMIENTAS.md) · [EN](../en/HERRAMIENTAS.md) · [FR](../fr/HERRAMIENTAS.md) · [DE](../de/HERRAMIENTAS.md) · [IT](../it/HERRAMIENTAS.md) · [CA](HERRAMIENTAS.md) · [EU](../eu/HERRAMIENTAS.md) · [GL](../gl/HERRAMIENTAS.md) · [OC](../oc/HERRAMIENTAS.md)

## Matriu d'ordres

| Objetivo | Comando | Dónde |
|---|---|---|
| Dev backend+frontend | `.\start.ps1` / `./start.sh` | Raíz (Docker si disponible, local si no) |
| Solo backend / frontend | `-NoFrontend` / `-NoBackend` | `start.ps1` / `--no-frontend` en `start.sh` |
| Web en navegador | `-Web` | Solo modo local |
| Prod local (build web + serve) | `-Final` | `start.ps1` / `start.sh` |
| Tests backend | `-TestBackend` | pytest en `.venv` o Docker |
| Tests frontend | `-TestFrontend` | `flutter test` o Docker |
| Migraciones | `-Migrate` / `-TestMigration` (MariaDB) | alembic |
| Revisar entorno sin arrancar | `-Check` | Doctor: Docker, Python, Flutter, .venv, puertos |
| Instalar dependencias que falten | `-InstallMissing` | winget / gestor del SO + git clone |
| Builds parciales | `-BuildFrontend` / `-BuildBackend` | Requieren Docker |
| APK Android | `flutter build apk --release --dart-define=BACKEND_URL=<url>` | `frontend/` |
| AppBundle (Play Store) | `flutter build appbundle --release --dart-define=BACKEND_URL=<url>` | `frontend/` |
| iOS/iPad (requiere macOS) | `tools/build-ios.sh` | Solo en Mac con Xcode |
| macOS / Windows / Linux | `tools/build-macos.sh` / `flutter build windows` / `flutter build linux` | Host correspondiente |
| Docker multi-target | `tools/build-all.ps1` | Requiere Docker |

## Millores aplicades (09/10/2026)

1. **`.dockerignore` als contextos de build** (`backend/`, `frontend/`).
   Abans només existien a `backend/docker/` i `frontend/docker/`, que NO són el
   context de `docker-compose.yml` (`./backend`, `./frontend`). Cada
   `docker compose build` enviava `.venv/` (cents de MB), `.dart_tool/`,
   `build/`, `*.db` i `*.hive` al daemon. Ara el context és mínim.
   Excepció: `!pubspec.lock` es conserva per a builds reproduïbles.
2. **Config pytest unificada**: eliminat `backend/pytest.ini` (duplicava i
   eclipsava `pyproject.toml`); tota la config viu a
   `[tool.pytest.ini_options]` (testpaths, patrons, markers).
3. **CI coherent**:
   - GitHub: Flutter `3.22.0` → `3.24.0` (igual que el Dockerfile);
     `flutter pub run` (obsolet) → `dart run build_runner`.
   - GitLab `backend-test`: afegits `TESTING=true` i `SECRET_KEY`
     (abans el rate limiter seguia actiu en tests → 429 esporàdics).
   - GitLab `frontend-test`: afegida generació d'adaptadors Hive abans
     de `flutter test` (paritat amb GitHub).
   - `pip install ruff` → `pip install "ruff>=0.5.0"` (igual que
     `requirements-dev.txt`).
4. **Lints multiplataforma** (`analysis_options.yaml`): `avoid_print` i
   `avoid_web_libraries_in_flutter`. Verificat: `flutter analyze` net
   (l'import condicional web/io és el patró acceptat).
5. **Fix `onReorder` obsolet** → `onReorderItem` (sense ajust manual d'
   índex); `flutter analyze` passa de 1 info a 0 issues.

## Propostes (no aplicades, amb motiu)

1. **Gate `ruff format --check` en CI**: bloquejat per ~249 violacions
   E501/W292 existents. Passos: `ruff format .`, revisar diff,
   `ruff check --fix`, i llavors afegir el gate.
2. **Unificar `start.bat/.ps1/.sh`**: tripliquen la lògica de ports/processos.
   La via realista és extreure la matriu de ports a `tools/ports.*` o
   documentar un únic entrypoint per OS, no reescriure els tres a la vegada.
3. **Cobertura en CI** (`pytest --cov`, `flutter test --coverage` + lcov):
    útil quan s'ampliïn tests de `syncAll` i routers sense cobrir (vegeu
    roadmap a [../README.ca.md](../../README.ca.md)).
