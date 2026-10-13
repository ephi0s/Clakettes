# Infrastruttura — Clakettes

Profili, porte, ambiente e CI. Operatività quotidiana in [USO.it.md](USO.it.md), checklist di hardening in [SEGURIDAD.it.md](SEGURIDAD.it.md).

## Profili Docker (`docker-compose.yml`)

| Perfil | Comando | Servicios |
|---|---|---|
| dev (sin perfil) | `docker compose up` | backend + frontend |
| db | `docker compose --profile db up` | + MariaDB 11 |
| prod | `docker compose --profile prod up -d` | backend-prod + frontend-prod + db |
| build | perfiles `[build]` en `frontend/docker/compose` | web, linux-x64, linux-appimage, android |
| windows / ci / dev | mismo compose | windows-x64+installer, test+analyze, dev web |

## Porte e volumi

| Puerto | Servicio | Variable |
|---|---|---|
| `8000` | backend y backend-prod | `PORT_BACKEND` |
| `3000` | frontend dev | `PORT_FRONTEND` |
| `80` | frontend-prod (nginx, build web estático) | `PORT_FRONTEND_PROD` |
| `3306` | MariaDB (interno) | `PORT_DB` |

Volumi: `./backend:/app` + `backend-data:/app/data`, `./frontend:/app`, `db-data:/var/lib/mysql`. Backup: SQLite = copiare `*.db`; MariaDB = `mariadb-dump` su `db-data`.

## Immagini

- Backend `python:3.12-alpine`, EXPOSE 8000; dev con `uvicorn --reload`, prod come utente non-root `appuser`.
- Frontend build `ubuntu:24.04 + Flutter 3.47.3` (ARG `BACKEND_URL`); dev `flutter run -d web-server` su 3000; prod `nginx:alpine` su 80 con `try_files $uri $uri/ /index.html` (SPA).

## Ambiente (`backend/.env`, vedi `.env.example`)

| Variable | Efecto |
|---|---|
| `APP_ENV` | `development` crea admin `admin/setup` + `create_all`; `production` exige Alembic y bloquea `SECRET_KEY` por defecto y CORS `*` |
| `SECRET_KEY` | Firma JWT (`HS256`); caduca access 30 min, refresh 30 d |
| `DATABASE_URL` | `sqlite:///./clakettes.db` (dev) o `mariadb+pymysql://…` (prod) |
| `CORS_ORIGINS` | Vacío = `*` sin credenciales (solo dev); prod exige orígenes explícitos |
| `PUBLIC_BASE_URL`, `FORWARDED_ALLOW_IPS` | URL pública y proxies de confianza (TLS frontal obligatorio en prod: los tokens DAV viajan en URL) |
| `BACKEND_URL` | `--dart-define` para la app Flutter (también cambiable en la pantalla de backend; persiste en SharedPreferences) |

## Salute e osservabili

- `GET /health` → `{"status":"healthy"}`; `GET /` → versione (`0.3.0`). `ConnectivityMonitor` nell'app li usa come sonda reale.
- Log: stdout di uvicorn (token DAV redatti); errori di API in SnackBar + `debugPrint`.
- Limiti: corpo ≤10 MB (413), avatar/immagine ≤5 MB (`jpeg/png/webp/gif` con magic-bytes), video ≤100 MB (`mp4/webm/quicktime`), docs ≤10 MB (pdf); rate limit 100 req/60s per IP (429; `/dav*` 600/60s; bypass con `TESTING=true`).

## CI

- **GitHub** (push/PR a `main,develop`): `backend-lint` + `frontend-lint` + `backend-test` (MariaDB 11 + `alembic upgrade head` + pytest) + `frontend-test` (build_runner + `flutter test`) → `docker-build` (4 immagini).
- **GitLab**: stages `lint → test → build`; `docker-build` solo in `main` con push al registry.

Porta locale (stessa del CI): `ruff check .` + `ruff format --check .` + `pytest tests/ -x -q --tb=short` (da `backend/`), `flutter analyze` + `flutter test` (da `frontend/`).

## Vedi anche

- [USO.it.md](USO.it.md): uso quotidiano del deployment
- [ADMINISTRACION.it.md](ADMINISTRACION.it.md): operazioni e ripristino
- [SEGURIDAD.it.md](SEGURIDAD.it.md): controlli e parametri di produzione
- [HERRAMIENTAS.it.md](HERRAMIENTAS.it.md): script e comandi di build/test
