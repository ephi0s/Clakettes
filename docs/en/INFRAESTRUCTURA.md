# Infrastructure — Clakettes

[ES](../es/INFRAESTRUCTURA.md) · [EN](INFRAESTRUCTURA.md) · [FR](../fr/INFRAESTRUCTURA.md) · [DE](../de/INFRAESTRUCTURA.md) · [IT](../it/INFRAESTRUCTURA.md) · [CA](../ca/INFRAESTRUCTURA.md) · [EU](../eu/INFRAESTRUCTURA.md) · [GL](../gl/INFRAESTRUCTURA.md) · [OC](../oc/INFRAESTRUCTURA.md)

Profiles, ports, environment and CI. Daily operation in [USO.md](USO.md), hardening checklist in [SEGURIDAD.md](SEGURIDAD.md).

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
- Frontend build `ubuntu:24.04 + Flutter 3.50.1` (ARG `BACKEND_URL`); dev `flutter run -d web-server` on 3000; prod `nginx:alpine` on 80 with `try_files $uri $uri/ /index.html` (SPA).

## Environment (`backend/.env`, see `.env.example`)

| Variable | Effect |
|---|---|
| `APP_ENV` | `development` creates admin `admin/setup` + `create_all`; `production` requires Alembic and blocks default `SECRET_KEY` and CORS `*` |
| `SECRET_KEY` | Signs JWT (`HS256`); access expires 30 min, refresh 30 d |
| `DATABASE_URL` | `sqlite:///./clakettes.db` (dev) or `mariadb+pymysql://…` (prod) |
| `CORS_ORIGINS` | Empty = `*` without credentials (dev only); prod requires explicit origins |
| `PUBLIC_BASE_URL`, `FORWARDED_ALLOW_IPS` | Public URL of the node (manifest and bundles) and trusted proxies (frontend TLS mandatory in prod: DAV tokens travel in URL) |
| `MTLS_REQUIRED`, `MTLS_CA_BUNDLE_PATH`, `MTLS_CLIENT_CERT_PATH`, `MTLS_CLIENT_KEY_PATH` | Federated mTLS (CN and PEM of the certificate), root CA to validate peers and PEM/key that sign the RSA-SHA256 manifest |
| `TESTING` | `1/true/yes/on` (case-insensitive, `app.config.is_testing()`): disables all rate limits (global 100/60 s, `/dav` 600/60 s, login 5/300 s, refresh 20/60 s, reset 3/300 s, federation 60/60 s) and auto-migration |
| `SKIP_AUTO_MIGRATE` | `1/true/yes/on`: skips `alembic upgrade head` in lifespan (externally managed DB) |
| `RATE_LIMITS_DB_PATH` | Path to the rate limiter's SQLite DB (by default `backend/rate_limits.db`) |
| `JWT_ISSUER`, `JWT_AUDIENCE`, `ACCESS_TOKEN_EXPIRE_MINUTES` | Validated claims and access token TTL (`clakettes`, `clakettes-api`, 30 min) |
| `PAYMENTS_PROVIDER`, `MOCK_WEBHOOK_SECRET`, `MOCK_PAYMENTS_FORCE_FAIL` | Provider (`mock` by default) and simulated webhook secret |
| `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `REDSYS_MERCHANT_CODE`, `REDSYS_TERMINAL`, `REDSYS_SECRET_KEY`, `REDSYS_SANDBOX`, `REDSYS_CURRENCY` | Stripe/Redsys credentials (sandbox by default, currency `978`) |
| `BACKEND_URL` | `--dart-define` for the Flutter app (also changeable on the backend screen; persisted in SharedPreferences) |

## Health and observables

- `GET /health` → `{"status":"healthy","db_revision":…}`; `GET /` → the version returned by `APP_VERSION`. `ConnectivityMonitor` in the app uses them as a real probe: per-node `NodeHealth` (`testNode()`, latency, `offlineNodeCount`, `isDegraded`) degrades the Hive cache gracefully and shows `DegradedNodesBanner` with a count and a retry button.
- Federation: `GET /api/federation/resilience/health` and `/metrics` (p50/p95, latency, failures and retries); `GET /api/federation/events/stream` keeps the SSE with a heartbeat every 15 s; `python tools/federation_conformance.py <url> [--json]` verifies third-party nodes.
- Logs: uvicorn stdout (DAV tokens redacted); API errors in SnackBar + `debugPrint`.
- Limits: body ≤10 MB (413), avatar/image ≤5 MB (`jpeg/png/webp/gif` with magic-bytes), video ≤100 MB (`mp4/webm/quicktime`), docs ≤10 MB (pdf); rate limit 100 req/60s per IP (429; `/dav*` 600/60s; bypass with `TESTING` ∈ {1,true,yes,on}).

## CI

- **GitHub** (push/PR to `main,develop`): `backend-lint` + `frontend-lint` + `docs-api` (checks that `API.md` is regenerated) + `backend-test` (SQLite, `TESTING=true`, pytest with `-m "not interop"`) + `backend-migration` (MariaDB 11 + `alembic upgrade head`) + `frontend-test` (build_runner + `flutter test`) → `docker-build` (the backend and frontend images, dev and prod).
- **GitLab**: stages `lint → test → build`; lint jobs include `docs-api` (checks that `API.md` is regenerated); `docker-build` only on `main` with push to registry.

### Dependency updates

- `.github/dependabot.yml`: pip in `/backend` and pub in `/frontend`, weekly (Monday), groups `backend-deps`/`frontend-deps`, up to 10 open PRs, labels `backend`/`frontend` + `dependencies`, assignee `ephi0s` and prefixes `build(backend):`/`build(frontend):`. `version-update:semver-major` updates are ignored.
- `.github/workflows/dependabot-automerge.yml`: `pull_request_target`, only for `dependabot[bot]`; uses `dependabot/fetch-metadata@v2` and enables `gh pr merge --auto --squash` only for patch/minor. Major updates stay for manual review and the actual merge requires green CI.
- `.github/workflows/dependabot-rebase.yml`: Monday 04:17 UTC (`17 4 * * 1`) and `workflow_dispatch`; rebases open Dependabot PR branches via `PUT /repos/{repo}/pulls/{n}/update-branch`.

## See also

- [USO.md](USO.md): daily deployment use
- [ADMINISTRACION.md](ADMINISTRACION.md): operations and recovery
- [SEGURIDAD.md](SEGURIDAD.md): controls and production parameters
- [HERRAMIENTAS.md](HERRAMIENTAS.md): scripts and build/test commands
