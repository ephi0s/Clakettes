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
| Verify node conformance | `python tools/federation_conformance.py <url> [--json]` | Root (`tools/`) |
| Regenerate API reference | `python tools/gen_api.py --all` | Root (`tools/`); combines prefixes from `main.py` and each `APIRouter` and detects auth dependencies |

The conformance CLI verifies manifest, JWKS, token, directory, users, WebFinger, reports, portability, chat bridge and event stream; it returns 1 if there are `critical`/`high` failures and 0 otherwise, and `--json` prints the full report.

## Improvements applied (09/10/2026)

1. **`.dockerignore` in build contexts** (`backend/`, `frontend/`). Previously they only existed in `backend/docker/` and `frontend/docker/`, which are NOT the context of `docker-compose.yml` (`./backend`, `./frontend`). Each `docker compose build` sent `.venv/` (hundreds of MB), `.dart_tool/`, `build/`, `*.db` and `*.hive` to the daemon. Now the context is minimal. Exception: `!pubspec.lock` is kept for reproducible builds.
2. **Unified pytest config**: removed `backend/pytest.ini` (duplicated and eclipsed `pyproject.toml`); all config lives in `[tool.pytest.ini_options]` (testpaths, patterns, markers).
3. **Coherent CI**:
   - GitHub: Flutter pinned to `3.47.3` (same as Dockerfile); `flutter pub run` (obsolete) → `dart run build_runner`.
   - GitHub and GitLab `backend-test`: `TESTING=true` and `SECRET_KEY=test-secret-key-for-ci-only-32bytes!` (36 bytes, avoids `InsecureKeyLengthWarning`; previously the rate limiter remained active in tests → sporadic 429s).
   - GitLab `frontend-test`: added Hive adapter generation before `flutter test` (parity with GitHub).
   - `pip install ruff` → `pip install "ruff==0.15.22"` in GitHub Actions; GitLab uses `pip install "ruff>=0.5.0"` and `requirements-dev.txt` pins `ruff==0.17.5` for local development.
4. **Multi-platform lints** (`analysis_options.yaml`): `avoid_print` and `avoid_web_libraries_in_flutter`. Verified: `flutter analyze` clean (conditional web/io import is the accepted pattern).
5. **Fix obsolete `onReorder`** → `onReorderItem` (no manual index adjustment); `flutter analyze` goes from 1 info to 0 issues.

## Proposals (not applied, with reason)

1. ~~**`ruff format --check` gate in CI**~~: already applied in GitHub and GitLab after fixing ~249 historical E501/W292 violations.
2. **Unify `.ps1`/`.sh`**: they double the port/process logic. The realistic path is to extract the port matrix to `tools/ports.*` or document a single entrypoint per OS, not rewrite both at once.
3. **CI coverage** (`pytest --cov`, `flutter test --coverage` + lcov): useful when expanding `syncAll` and uncovered routers tests (see roadmap in [../README.md](../../README.md)).
