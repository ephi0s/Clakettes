# Infraestructura — Clakettes

[ES](INFRAESTRUCTURA.md) · [EN](INFRAESTRUCTURA.en.md) · [FR](INFRAESTRUCTURA.fr.md) · [DE](INFRAESTRUCTURA.de.md) · [IT](INFRAESTRUCTURA.it.md) · [CA](INFRAESTRUCTURA.ca.md) · [EU](INFRAESTRUCTURA.eu.md) · [GL](INFRAESTRUCTURA.gl.md) · [OC](INFRAESTRUCTURA.oc.md)

Perfils, ports, entorn i CI. Operativa diària a [USO.ca.md](USO.ca.md), checklist d'endurit a [SEGURIDAD.ca.md](SEGURIDAD.ca.md).

## Perfils Docker (`docker-compose.yml`)

| Perfil | Comando | Servicios |
|---|---|---|
| dev (sin perfil) | `docker compose up` | backend + frontend |
| db | `docker compose --profile db up` | + MariaDB 11 |
| prod | `docker compose --profile prod up -d` | backend-prod + frontend-prod + db |
| build | perfiles `[build]` en `frontend/docker/compose` | web, linux-x64, linux-appimage, android |
| windows / ci / dev | mismo compose | windows-x64+installer, test+analyze, dev web |

## Ports i volums

| Puerto | Servicio | Variable |
|---|---|---|
| `8000` | backend y backend-prod | `PORT_BACKEND` |
| `3000` | frontend dev | `PORT_FRONTEND` |
| `80` | frontend-prod (nginx, build web estático) | `PORT_FRONTEND_PROD` |
| `3306` | MariaDB (interno) | `PORT_DB` |

Volums: `./backend:/app` + `backend-data:/app/data`, `./frontend:/app`, `db-data:/var/lib/mysql`. Backups: SQLite = copiar `*.db`; MariaDB = `mariadb-dump` sobre `db-data`.

## Imatges

- Backend `python:3.12-alpine`, EXPOSE 8000; dev amb `uvicorn --reload`, prod com a usuari no-root `appuser`.
- Frontend build `ubuntu:24.04 + Flutter 3.47.3` (ARG `BACKEND_URL`); dev `flutter run -d web-server` a 3000; prod `nginx:alpine` a 80 amb `try_files $uri $uri/ /index.html` (SPA).

## Entorn (`backend/.env`, vegeu `.env.example`)

| Variable | Efecto |
|---|---|
| `APP_ENV` | `development` crea admin `admin/setup` + `create_all`; `production` exige Alembic y bloquea `SECRET_KEY` por defecto y CORS `*` |
| `SECRET_KEY` | Firma JWT (`HS256`); caduca access 30 min, refresh 30 d |
| `DATABASE_URL` | `sqlite:///./clakettes.db` (dev) o `mariadb+pymysql://…` (prod) |
| `CORS_ORIGINS` | Vacío = `*` sin credenciales (solo dev); prod exige orígenes explícitos |
| `PUBLIC_BASE_URL`, `FORWARDED_ALLOW_IPS` | URL pública y proxies de confianza (TLS frontal obligatorio en prod: los tokens DAV viajan en URL) |
| `BACKEND_URL` | `--dart-define` para la app Flutter (también cambiable en la pantalla de backend; persiste en SharedPreferences) |

## Salut i observables

- `GET /health` → `{"status":"healthy"}`; `GET /` → versió (`0.3.0`). `ConnectivityMonitor` a l'app els utilitza com a sonda real.
- Logs: stdout d'uvicorn (tokens DAV redactats); errors d'API en SnackBar + `debugPrint`.
- Límits: cos ≤10 MB (413), avatar/imatge ≤5 MB (`jpeg/png/webp/gif` amb magic-bytes), vídeo ≤100 MB (`mp4/webm/quicktime`), docs ≤10 MB (pdf); rate limit 100 req/60s per IP (429; `/dav*` 600/60s; bypass amb `TESTING=true`).

## CI

- **GitHub** (push/PR a `main,develop`): `backend-lint` + `frontend-lint` + `backend-test` (MariaDB 11 + `alembic upgrade head` + pytest) + `frontend-test` (build_runner + `flutter test`) → `docker-build` (4 imatges).
- **GitLab**: stages `lint → test → build`; `docker-build` només a `main` amb push al registry.

Porta local (mateixa que CI): `ruff check .` + `ruff format --check .` + `pytest tests/ -x -q --tb=short` (des de `backend/`), `flutter analyze` + `flutter test` (des de `frontend/`).

## Vegeu també

- [USO.ca.md](USO.ca.md): ús diari del desplegament
- [ADMINISTRACION.ca.md](ADMINISTRACION.ca.md): operacions i recuperació
- [SEGURIDAD.ca.md](SEGURIDAD.ca.md): controls i paràmetres de producció
- [HERRAMIENTAS.ca.md](HERRAMIENTAS.ca.md): scripts i ordres de build/test
