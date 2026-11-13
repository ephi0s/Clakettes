# Build / test / dev tools — Clakettes

[ES](../es/HERRAMIENTAS.md) · [EN](HERRAMIENTAS.md) · [FR](../fr/HERRAMIENTAS.md) · [DE](../de/HERRAMIENTAS.md) · [IT](../it/HERRAMIENTAS.md) · [CA](../ca/HERRAMIENTAS.md) · [EU](../eu/HERRAMIENTAS.md) · [GL](../gl/HERRAMIENTAS.md) · [OC](../oc/HERRAMIENTAS.md)

## Command matrix

| Goal | Command | Where |
|---|---|---|
| Dev backend+frontend | `.\start.ps1` / `./start.sh` | Root (Docker if available, local if not) |
| Only backend / frontend | `-NoFrontend` / `-NoBackend` | `start.ps1` / `--no-frontend` in `start.sh` |
| Web in browser | `-Web` | Local mode only |
| Local production (web build + serve) | `-Final` | `start.ps1` / `start.sh` |
| Backend tests | `-TestBackend` | pytest in `.venv` or Docker |
| Frontend tests | `-TestFrontend` | `flutter test` or Docker |
| Migrations | `-Migrate` / `-TestMigration` (MariaDB) | alembic |
| Check environment without starting | `-Check` | Doctor: Docker, Python, Flutter, .venv, ports |
| Install missing dependencies | `-InstallMissing` | winget / OS package manager + git clone |
| Partial builds | `-BuildFrontend` / `-BuildBackend` | Require Docker |
| Android APK | `flutter build apk --release --dart-define=BACKEND_URL=<url>` | `frontend/` |
| AppBundle (Play Store) | `flutter build appbundle --release --dart-define=BACKEND_URL=<url>` | `frontend/` |
| iOS/iPad (requires macOS) | `tools/build-ios.sh` | Only on Mac with Xcode |
| macOS / Windows / Linux | `tools/build-macos.sh` / `flutter build windows` / `flutter build linux` | Corresponding host |
| Docker multi-target | `tools/build-all.ps1` | Requires Docker |

## Improvements applied (09/10/2026)

1. **`.dockerignore` in build contexts** (`backend/`, `frontend/`). Previously they only existed in `backend/docker/` and `frontend/docker/`, which are NOT the context of `docker-compose.yml` (`./backend`, `./frontend`). Each `docker compose build` sent `.venv/` (hundreds of MB), `.dart_tool/`, `build/`, `*.db` and `*.hive` to the daemon. Now the context is minimal. Exception: `!pubspec.lock` is kept for reproducible builds.
2. **Unified pytest config**: removed `backend/pytest.ini` (duplicated and eclipsed `pyproject.toml`); all config lives in `[tool.pytest.ini_options]` (testpaths, patterns, markers).
3. **Coherent CI**:
   - GitHub: Flutter `3.22.0` → `3.24.0` (same as Dockerfile); `flutter pub run` (obsolete) → `dart run build_runner`.
   - GitLab `backend-test`: added `TESTING=true` and `SECRET_KEY` (previously the rate limiter remained active in tests → sporadic 429s).
   - GitLab `frontend-test`: added Hive adapter generation before `flutter test` (parity with GitHub).
   - `pip install ruff` → `pip install "ruff>=0.5.0"` (same as `requirements-dev.txt`).
4. **Multi-platform lints** (`analysis_options.yaml`): `avoid_print` and `avoid_web_libraries_in_flutter`. Verified: `flutter analyze` clean (conditional web/io import is the accepted pattern).
5. **Fix obsolete `onReorder`** → `onReorderItem` (no manual index adjustment); `flutter analyze` goes from 1 info to 0 issues.

## Proposals (not applied, with reason)

1. **`ruff format --check` gate in CI**: blocked by ~249 existing E501/W292 violations. Steps: `ruff format .`, review diff, `ruff check --fix`, then add the gate.
2. **Unify `start.bat/.ps1/.sh`**: they triple the port/process logic. The realistic path is to extract the port matrix to `tools/ports.*` or document a single entrypoint per OS, not rewrite all three at once.
3. **CI coverage** (`pytest --cov`, `flutter test --coverage` + lcov): useful when expanding `syncAll` and uncovered routers tests (see roadmap in [../README.md](../../README.en.md)).