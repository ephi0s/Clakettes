# Infrastruktur — Clakettes

[ES](../es/INFRAESTRUCTURA.md) · [EN](../en/INFRAESTRUCTURA.md) · [FR](../fr/INFRAESTRUCTURA.md) · [DE](INFRAESTRUCTURA.md) · [IT](../it/INFRAESTRUCTURA.md) · [CA](../ca/INFRAESTRUCTURA.md) · [EU](../eu/INFRAESTRUCTURA.md) · [GL](../gl/INFRAESTRUCTURA.md) · [OC](../oc/INFRAESTRUCTURA.md)

Profile, Ports, Umgebung und CI. Tägliches Operatives in [USO.md](USO.md), Härtungs-Checkliste in [SEGURIDAD.md](SEGURIDAD.md).

## Docker-Profile (`docker-compose.yml`)

| Perfil | Comando | Servicios |
|---|---|---|
| dev (sin perfil) | `docker compose up` | backend + frontend |
| db | `docker compose --profile db up` | + MariaDB 11 |
| prod | `docker compose --profile prod up -d` | backend-prod + frontend-prod + db |
| build | perfiles `[build]` en `frontend/docker/compose` | web, linux-x64, linux-appimage, android |
| windows / ci / dev | mismo compose | windows-x64+installer, test+analyze, dev web |

## Ports und Volumes

| Puerto | Servicio | Variable |
|---|---|---|
| `8000` | backend y backend-prod | `PORT_BACKEND` |
| `3000` | frontend dev | `PORT_FRONTEND` |
| `80` | frontend-prod (nginx, build web estático) | `PORT_FRONTEND_PROD` |
| `3306` | MariaDB (interno) | `PORT_DB` |

Volumes: `./backend:/app` + `backend-data:/app/data`, `./frontend:/app`, `db-data:/var/lib/mysql`. Backups: SQLite = `*.db` kopieren; MariaDB = `mariadb-dump` über `db-data`.

## Images

- Backend `python:3.12-alpine`, EXPOSE 8000; Dev mit `uvicorn --reload`, Prod als Nicht-Root-User `appuser`.
- Frontend-Build `ubuntu:24.04 + Flutter 3.47.3` (ARG `BACKEND_URL`); Dev `flutter run -d web-server` auf 3000; Prod `nginx:alpine` auf 80 mit `try_files $uri $uri/ /index.html` (SPA).

## Umgebung (`backend/.env`, siehe `.env.example`)

| Variable | Efecto |
|---|---|
| `APP_ENV` | `development` crea admin `admin/setup` + `create_all`; `production` exige Alembic y bloquea `SECRET_KEY` por defecto y CORS `*` |
| `SECRET_KEY` | Firma JWT (`HS256`); caduca access 30 min, refresh 30 d |
| `DATABASE_URL` | `sqlite:///./clakettes.db` (dev) o `mariadb+pymysql://…` (prod) |
| `CORS_ORIGINS` | Vacío = `*` sin credenciales (solo dev); prod exige orígenes explícitos |
| `PUBLIC_BASE_URL`, `FORWARDED_ALLOW_IPS` | URL pública y proxies de confianza (TLS frontal obligatorio en prod: los tokens DAV viajan en URL) |
| `BACKEND_URL` | `--dart-define` para la app Flutter (también cambiable en la pantalla de backend; persiste en SharedPreferences) |

## Gesundheit und Observables

- `GET /health` → `{"status":"healthy"}`; `GET /` → Version (`0.3.0`). `ConnectivityMonitor` in der App nutzt sie als echte Sonde.
- Logs: Uvicorn-Stdout (DAV-Tokens redigiert); API-Fehler in SnackBar + `debugPrint`.
- Limits: Body ≤10 MB (413), Avatar/Bild ≤5 MB (`jpeg/png/webp/gif` mit Magic-Bytes), Video ≤100 MB (`mp4/webm/quicktime`), Docs ≤10 MB (pdf); Rate-Limit 100 Req/60s pro IP (429; `/dav*` 600/60s; Bypass mit `TESTING=true`).

## CI

- **GitHub** (Push/PR auf `main,develop`): `backend-lint` + `frontend-lint` + `backend-test` (MariaDB 11 + `alembic upgrade head` + pytest) + `frontend-test` (build_runner + `flutter test`) → `docker-build` (4 Images).
- **GitLab**: Stages `lint → test → build`; `docker-build` nur auf `main` mit Push zur Registry.

Lokales Gate (wie CI): `ruff check .` + `ruff format --check .` + `pytest tests/ -x -q --tb=short` (aus `backend/`), `flutter analyze` + `flutter test` (aus `frontend/`).

## Siehe auch

- [USO.md](USO.md): tägliche Nutzung des Deployments
- [ADMINISTRACION.md](ADMINISTRACION.md): Betrieb und Wiederherstellung
- [SEGURIDAD.md](SEGURIDAD.md): Produktionskontrollen und -parameter
- [HERRAMIENTAS.md](HERRAMIENTAS.md): Build-/Test-Skripte und Befehle
