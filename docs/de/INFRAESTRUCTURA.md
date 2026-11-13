# Infrastruktur — Clakettes

[ES](../es/INFRAESTRUCTURA.md) · [EN](../en/INFRAESTRUCTURA.md) · [FR](../fr/INFRAESTRUCTURA.md) · [DE](INFRAESTRUCTURA.md) · [IT](../it/INFRAESTRUCTURA.md) · [CA](../ca/INFRAESTRUCTURA.md) · [EU](../eu/INFRAESTRUCTURA.md) · [GL](../gl/INFRAESTRUCTURA.md) · [OC](../oc/INFRAESTRUCTURA.md)

Profile, Ports, Umgebung und CI. Täglicher Betrieb in [USO.md](USO.md), Härtungs-Checkliste in [SEGURIDAD.md](SEGURIDAD.md).

## Docker-Profile (`docker-compose.yml`)

| Profil | Befehl | Dienste |
|--------|--------|---------|
| dev (ohne Profil) | `docker compose up` | Backend + Frontend |
| db | `docker compose --profile db up` | + MariaDB 11 |
| prod | `docker compose --profile prod up -d` | Backend-prod + Frontend-prod + DB |
| build | `[build]`-Profile in `frontend/docker/compose` | Web, linux-x64, linux-appimage, Android |
| windows / ci / dev | gleicher Compose | Windows-x64+Installer, Test+Analyze, dev Web |

## Ports und Volumes

| Port | Dienst | Variable |
|------|--------|----------|
| `8000` | Backend und Backend-prod | `PORT_BACKEND` |
| `3000` | Frontend dev | `PORT_FRONTEND` |
| `80` | Frontend-prod (Nginx, statischer Web-Build) | `PORT_FRONTEND_PROD` |
| `3306` | MariaDB (intern) | `PORT_DB` |

Volumes: `./backend:/app` + `backend-data:/app/data`, `./frontend:/app`, `db-data:/var/lib/mysql`. Backups: SQLite = `*.db` kopieren; MariaDB = `mariadb-dump` auf `db-data`.

## Images

- Backend `python:3.12-alpine`, EXPOSE 8000; Dev mit `uvicorn --reload`, Prod als Nicht-Root-User `appuser`.
- Frontend-Build `ubuntu:24.04 + Flutter 3.47.3` (ARG `BACKEND_URL`); Dev `flutter run -d web-server` auf 3000; Prod `nginx:alpine` auf 80 mit `try_files $uri $uri/ /index.html` (SPA).

## Umgebung (`backend/.env`, siehe `.env.example`)

| Variable | Wirkung |
|----------|---------|
| `APP_ENV` | `development` erstellt Admin `admin/setup` + `create_all`; `production` erfordert Alembic und blockiert Standard-`SECRET_KEY` und CORS `*` |
| `SECRET_KEY` | Signiert JWT (`HS256`); Access verfällt 30 Min, Refresh 30 Tage |
| `DATABASE_URL` | `sqlite:///./clakettes.db` (dev) oder `mariadb+pymysql://…` (Prod) |
| `CORS_ORIGINS` | Leer = `*` ohne Credentials (nur Dev); Prod erfordert explizite Ursprünge |
| `PUBLIC_BASE_URL`, `FORWARDED_ALLOW_IPS` | Öffentliche URL und vertrauenswürdige Proxies (TLS-Vorfranz obligatorisch in Prod: DAV-Tokens reisen in URL) |
| `BACKEND_URL` | `--dart-define` für die Flutter-App (auch änderbar auf dem Backend-Bildschirm; persistiert in SharedPreferences) |

## Gesundheit und Observables

- `GET /health` → `{"status":"healthy"}`; `GET /` → Version (`0.3.0`). `ConnectivityMonitor` in der App verwendet sie als reale Sonde.
- Logs: uvicorn stdout (DAV-Tokens redacted); API-Fehler in SnackBar + `debugPrint`.
- Limits: Körper ≤10 MB (413), Avatar/Bild ≤5 MB (`jpeg/png/webp/gif` mit Magic-Bytes), Video ≤100 MB (`mp4/webm/quicktime`), Docs ≤10 MB (PDF); Rate-Limit 100 req/60s pro IP (429; `/dav*` 600/60s; Umgehung mit `TESTING=true`).

## CI

- **GitHub** (Push/PR auf `main,develop`): `backend-lint` + `frontend-lint` + `backend-test` (MariaDB 11 + `alembic upgrade head` + pytest) + `frontend-test` (build_runner + `flutter test`) → `docker-build` (4 Images).
- **GitLab**: Stages `lint → test → build`; `docker-build` nur auf `main` mit Push zur Registry.

Lokales Tor (gleich wie CI): `ruff check .` + `ruff format --check .` + `pytest tests/ -x -q --tb=short` (von `backend/`), `flutter analyze` + `flutter test` (von `frontend/`).

## Siehe auch

- [USO.md](USO.md): tägliche Bereitstellungsnutzung
- [ADMINISTRACION.md](ADMINISTRACION.md): Betrieb und Wiederherstellung
- [SEGURIDAD.md](SEGURIDAD.md): Kontrollen und Produktionsparameter
- [HERRAMIENTAS.md](HERRAMIENTAS.md): Skripte und Build/Test-Befehle