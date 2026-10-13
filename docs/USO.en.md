# Usage — Clakettes

[ES](USO.md) · [EN](USO.en.md) · [FR](USO.fr.md) · [DE](USO.de.md) · [IT](USO.it.md) · [CA](USO.ca.md) · [EU](USO.eu.md) · [GL](USO.gl.md) · [OC](USO.oc.md)

## Quick start

| I want | Command |
|---|---|
| Everything locally | `.\start.ps1` or `./start.sh` (Docker if present, local otherwise) |
| Backend / frontend only | `-NoFrontend` / `-NoBackend` |
| Try in browser | `-Web` (local mode) |
| Local production | `-Final` (web build + serve) |
| Tests | `-TestBackend` / `-TestFrontend` |
| Migrations / with MariaDB | `-Migrate` / `-MariaDB` / `-TestMigration` |
| Stop everything | `-Kill` |
| Install missing dependencies | `-InstallMissing` (Windows: winget + git clone; Linux/macOS: OS package manager + git clone) |
| Check environment without starting | `-Check` (doctor: Docker, Python, Flutter, .venv, ports; exits 1 if something is missing) |
| Distributable builds | `-BuildAll` (`tools/build-all.ps1` → `builds/`) |

Without Docker, the launcher creates a local bare-metal environment: it detects Python 3.12+ and Flutter, shows how to install them for your OS and offers to install them with `-InstallMissing` (asks first unless the flag is passed).

Dev URLs: backend `http://localhost:8000` (Swagger at `/docs`), frontend `http://localhost:3000`.
If a port is busy it is reassigned automatically (watch `[PUERTO]` in the output).
Initial admin (non-prod only): `admin` / `setup` — change on sign-in.

## Configuration

| Variable / flag | Where | Effect |
|---|---|---|
| `BACKEND_URL` | `--dart-define` or backend screen in the app | API URL (persisted in SharedPreferences) |
| `DATABASE_URL` | `backend/.env` | `sqlite:///./clakettes.db` (dev; in Docker `./data/clakettes.db`) or `mariadb+pymysql://…?ssl_ca=…` (prod, mandatory TLS) |
| `SECRET_KEY` | env (required in `APP_ENV=production`) | JWT signing; insecure default blocks startup in prod |
| `CORS_ORIGINS` | env | Explicit origins in prod (`*` forbidden with credentials) |
| `APP_ENV` | env | `development` creates admin + `create_all`; `production` requires Alembic |

## Operation

- **Migrate**: `alembic upgrade head` from `backend/` (Docker: `-Migrate`).
- **SQLite → MariaDB**: `export_sqlite_to_mariadb.py`; back with `import_mariadb_to_sqlite.py` (details in [DATABASE.md](DATABASE.en.md)).
- **Backups**: SQLite = copy `*.db`; MariaDB = `mariadb-dump` (`db-data` volume in Docker).
- **Logs**: uvicorn stdout (DAV tokens already redacted); API errors in SnackBar + `debugPrint`.
- **Limits**: bodies ≤10 MB (413 if larger); rate limit with 429 + retry.

## User roles

`admin` (everything) → `organizer` (their festival: events, forms, committees) → `attendee`/`juror`/etc. (assigned by organizers; auto-join only grants `attendee`). Channels: `admin`/`moderator`/`member`; committees with member count in list.

## See also

- [README.md](../README.en.md): general project description and quick access
- [HERRAMIENTAS.md](HERRAMIENTAS.en.md): execution scripts and commands
- [ADMINISTRACION.md](ADMINISTRACION.en.md): deployment administration and secret rotation
- [SEGURIDAD.md](SEGURIDAD.en.md): production checklist and best practices
