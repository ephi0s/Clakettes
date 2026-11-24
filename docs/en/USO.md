# Usage — Clakettes

[ES](../es/USO.md) · [EN](USO.md) · [FR](../fr/USO.md) · [DE](../de/USO.md) · [IT](../it/USO.md) · [CA](../ca/USO.md) · [EU](../eu/USO.md) · [GL](../gl/USO.md) · [OC](../oc/USO.md)

## Quick start

| I want | Command |
|---|---|
| Everything local | `.\start.ps1` or `./start.sh` (Docker if available, local if not) |
| Only backend / frontend | `-NoFrontend` / `-NoBackend` |
| Test in development browser | default / `-Dev` (or `-Web` to force local mode) |
| Local production | `-Final` (web build + serve) |
| Tests | `-TestBackend` / `-TestFrontend` |
| Migrations / with MariaDB | `-Migrate` / `-MariaDB` / `-TestMigration` |
| Stop everything | `-Kill` |
| Install missing dependencies | `-InstallMissing` (Windows: winget + git clone; Linux/macOS: OS package manager + git clone) |
| Check environment without starting | `-Check` (doctor: Docker, Python, Flutter, .venv, ports; exits 1 if something is missing) |
| Distributable builds | `-BuildAll` (`tools/build-all.ps1` → `builds/`) |

Without Docker, the launcher creates a bare-metal local environment: detects Python 3.12+ and Flutter, shows how to install them according to your OS and offers to install them with `-InstallMissing` (asks before unless you pass the flag).

Dev URLs: backend `http://localhost:8000` (Swagger at `/docs`), frontend `http://localhost:3000`.
If the port is occupied it is reassigned automatically (see `[PUERTO]` in the output).
Initial admin (non-prod only): `admin` / `setup` — change on first login.

## Configuration

| Variable / flag | Where | Effect |
|---|---|---|
| `BACKEND_URL` | `--dart-define` or backend screen in the app | API URL (persisted in SharedPreferences) |
| `DATABASE_URL` | `backend/.env` | `sqlite:///./clakettes.db` (dev; in Docker `./data/clakettes.db`) or `mariadb+pymysql://…?ssl_ca=…` (prod, TLS mandatory) |
| `SECRET_KEY` | env (mandatory in `APP_ENV=production`) | Signs JWT; insecure default blocks startup in prod |
| `CORS_ORIGINS` | env | Explicit origins in prod (`*` prohibited with credentials) |
| `APP_ENV` | env | `development` creates admin + `create_all`; `production` requires Alembic |
| `PUBLIC_BASE_URL` | `backend/.env` | Public domain of the node; appears in the manifest and portability bundles |
| `MTLS_REQUIRED` | env | Forces verified peer mTLS in federation (CN and PEM of the certificate) |
| `MTLS_CA_BUNDLE_PATH` | env | Root CA to validate federated client certificates |
| `MTLS_CLIENT_CERT_PATH`, `MTLS_CLIENT_KEY_PATH` | env | PEM of the certificate and private key that sign the manifest (RSA-SHA256) |
| `TESTING`, `SKIP_AUTO_MIGRATE` | env | `1/true/yes/on`: `TESTING` disables rate limits and auto-migration; `SKIP_AUTO_MIGRATE` skips only auto-migration |
| `RATE_LIMITS_DB_PATH` | env | Path to the SQLite rate-limit DB (default `backend/rate_limits.db`) |
| `JWT_ISSUER`, `JWT_AUDIENCE`, `ACCESS_TOKEN_EXPIRE_MINUTES` | env | Claims and TTL of the access JWT |
| `PAYMENTS_PROVIDER`, `MOCK_WEBHOOK_SECRET`, `MOCK_PAYMENTS_FORCE_FAIL` | env | Payment provider (`mock` by default) and simulated webhook secrets |
| `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `REDSYS_*` | env | Real payment credentials; detail in [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) |

**Payment note**: `PAYMENTS_PROVIDER=mock` is the default value (`backend/app/config.py`). Stripe and Redsys are NOT operational until their webhooks are wired (`POST /api/payments/webhook/{stripe,redsys}`); only the simulated one works today. Redsys `confirm` always returns `"pending"`.
| `TESTING`, `SKIP_AUTO_MIGRATE` | env | `1/true/yes/on`: `TESTING` disables rate limits and auto-migration; `SKIP_AUTO_MIGRATE` skips only auto-migration |

## Operation

- **Migrate**: `alembic upgrade head` from `backend/` (Docker: `-Migrate`).
- **Automatic migration**: the app migrates the DB itself on startup and seals new DBs with the current revision; `SKIP_AUTO_MIGRATE=1` to skip it (externally managed DBs).
- **SQLite → MariaDB**: `export_sqlite_to_mariadb.py`; back with `import_mariadb_to_sqlite.py` (detail in [DATABASE.md](DATABASE.md)).
- **Backups**: SQLite = copy `*.db`; MariaDB = `mariadb-dump` (volume `db-data` in Docker).
- **Logs**: uvicorn stdout (DAV tokens redacted); API errors in SnackBar + `debugPrint`.
- **Limits**: bodies ≤10 MB (413 if larger); rate limit with 429 + retry (global 100/60 s per IP, `/dav` 600/60 s, login 5/300 s, refresh 20/60 s, reset 3/300 s, federation 60/60 s; chat 10/60 s per node and user). `TESTING` ∈ {1,true,yes,on} disables all limits.
- **Offline**: the Hive cache stores each node's origin; `reconcile` merges on reconnect and `clearOrigin` discards a node. If some nodes do not respond but the main one does, `DegradedNodesBanner` shows the count and a reload button.
- **Media**: the `/uploads/...` paths returned by the API are prefixed with the active server on the client (`resolveMediaUrl()`); `http(s)` URLs are used as-is.
- **Federation**: check a third-party node with `python tools/federation_conformance.py <url> [--json]`; peering health is at `/api/federation/resilience/health` and p50/p95 metrics at `/metrics`.
- **Portability**: export/import bundles from `/api/federation/portability/{bundles,imports}` and consult identity redirects at `/redirects/{ref}`.

## User roles

`admin` (everything) → `organizer` (their festival: events, forms, committees) → `attendee`/`juror`/etc. (assigned by organizers; auto-join only gives `attendee`). Channels: `admin`/`moderator`/`member`; committees with member count in list.

## Functions in active development

🚧 The following functions are in active development and may change:

- **Social profiles**: publication walls (microblogging with Markdown and video/podcast embeds) on user and festival profiles, with optional reply threads per publication and moderation by roles (administrators, festival management, moderators). No reactions, stickers or GIFs for now.
- **Profile customization**: cover, tagline and social links on users and festivals.
- **Badges**: deactivated by default; only the admin team can activate them (`PUT /api/badges/settings`). Platform badges are granted by administrators; festival merit badges (veteran, popular, role, special award), their management. Each badge carries an image (SVG preferred).
- **Jury voting**: already operational (scoring per work, aggregation and optional anonymity); only accepts shorts from the assigned festival.

## See also

- [README.md](../../README.md): general project description and quick access
- [HERRAMIENTAS.md](HERRAMIENTAS.md): scripts and execution commands
- [ADMINISTRACION.md](ADMINISTRACION.md): deployment administration and secret rotation
- [SEGURIDAD.md](SEGURIDAD.md): checklist and production best practices
