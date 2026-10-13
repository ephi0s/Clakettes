# Infrastructure — Clakettes

Profiles, ports, environment and CI. Daily operations in [USO.md](USO.en.md), hardening checklist in [SEGURIDAD.md](SEGURIDAD.en.md).

## Docker profiles (`docker-compose.yml`)

| Profile | Command | Services |
|---|---|---|
| dev (no profile) | `docker compose up` | backend + frontend |
| db | `docker compose --profile db up` | + MariaDB 11 |
| prod | `docker compose --profile prod up -d` | backend-prod + frontend-prod + db |
| build | `[build]` profiles in `frontend/docker/compose` | web, linux-x64, linux-appimage, android |
| windows / ci / dev | same compose | windows-x64+installer, test+analyze, dev web |

## Ports and volumes

| Port | Service | Variable |
|---|---|---|
| `8000` | backend and backend-prod | `PORT_BACKEND` |
| `3000` | frontend dev | `PORT_FRONTEND` |
| `80` | frontend-prod (nginx, static web build) | `PORT_FRONTEND_PROD` |
| `3306` | MariaDB (internal) | `PORT_DB` |

Volumes: `./backend:/app` + `backend-data:/app/data`, `./frontend:/app`, `db-data:/var/lib/mysql`. Backups: SQLite = copy `*.db`; MariaDB = `mariadb-dump` on `db-data`.

## Images

- Backend `python:3.12-alpine`, EXPOSE 8000; dev with `uvicorn --reload`, prod as non-root user `appuser`.
- Frontend build `ubuntu:24.04 + Flutter 3.47.3` (ARG `BACKEND_URL`); dev `flutter run -d web-server` on 3000; prod `nginx:alpine` on 80 with `try_files $uri $uri/ /index.html` (SPA).

## Environment (`backend/.env`, see `.env.example`)

| Variable | Effect |
|---|---|
| `APP_ENV` | `development` creates admin `admin/setup` + `create_all`; `production` requires Alembic and blocks default `SECRET_KEY` and `*` CORS |
| `SECRET_KEY` | JWT signing (`HS256`); access expires in 30 min, refresh in 30 d |
| `DATABASE_URL` | `sqlite:///./clakettes.db` (dev) or `mariadb+pymysql://…` (prod) |
| `CORS_ORIGINS` | Empty = `*` without credentials (dev only); prod requires explicit origins |
| `PUBLIC_BASE_URL`, `FORWARDED_ALLOW_IPS` | Public URL and trusted proxies (front TLS required in prod: DAV tokens travel in the URL) |
| `BACKEND_URL` | `--dart-define` for the Flutter app (also changeable on the backend screen; persisted in SharedPreferences) |

## Health and observables

- `GET /health` → `{"status":"healthy"}`; `GET /` → version (`0.3.0`). `ConnectivityMonitor` in the app uses them as a live probe.
- Logs: uvicorn stdout (DAV tokens redacted); API errors in SnackBar + `debugPrint`.
- Limits: body ≤10 MB (413), avatar/image ≤5 MB (`jpeg/png/webp/gif` with magic bytes), video ≤100 MB (`mp4/webm/quicktime`), docs ≤10 MB (pdf); rate limit 100 req/60s per IP (429; `/dav*` 600/60s; bypass with `TESTING=true`).

## CI

- **GitHub** (push/PR to `main,develop`): `backend-lint` + `frontend-lint` + `backend-test` (MariaDB 11 + `alembic upgrade head` + pytest) + `frontend-test` (build_runner + `flutter test`) → `docker-build` (4 images).
- **GitLab**: stages `lint → test → build`; `docker-build` only on `main` with registry push.

Local gate (same as CI): `ruff check .` + `ruff format --check .` + `pytest tests/ -x -q --tb=short` (from `backend/`), `flutter analyze` + `flutter test` (from `frontend/`).

## See also

- [USO.md](USO.en.md): daily use of the deployment
- [ADMINISTRACION.md](ADMINISTRACION.en.md): operations and recovery
- [SEGURIDAD.md](SEGURIDAD.en.md): production controls and settings
- [HERRAMIENTAS.md](HERRAMIENTAS.en.md): build/test scripts and commands
