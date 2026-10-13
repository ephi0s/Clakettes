# Infraestructura — Clakettes

Perfils, pòrts, environa e CI. Operativa vidanta en [USO.oc.md](USO.oc.md), checklist de durciment en [SEGURIDAD.oc.md](SEGURIDAD.oc.md).

## Perfils Docker (`docker-compose.yml`)

| Perfil | Comando | Servicios |
|---|---|---|
| dev (sin perfil) | `docker compose up` | backend + frontend |
| db | `docker compose --profile db up` | + MariaDB 11 |
| prod | `docker compose --profile prod up -d` | backend-prod + frontend-prod + db |
| build | perfiles `[build]` en `frontend/docker/compose` | web, linux-x64, linux-appimage, android |
| windows / ci / dev | mismo compose | windows-x64+installer, test+analyze, dev web |

## Pòrts e volums

| Puerto | Servicio | Variable |
|---|---|---|
| `8000` | backend y backend-prod | `PORT_BACKEND` |
| `3000` | frontend dev | `PORT_FRONTEND` |
| `80` | frontend-prod (nginx, build web estático) | `PORT_FRONTEND_PROD` |
| `3306` | MariaDB (interno) | `PORT_DB` |

Volums: `./backend:/app` + `backend-data:/app/data`, `./frontend:/app`, `db-data:/var/lib/mysql`. Salvagardas: SQLite = copiar `*.db`; MariaDB = `mariadb-dump` sus `db-data`.

## Imatges

- Backend `python:3.12-alpine`, EXPOSE 8000; dev amb `uvicorn --reload`, prod coma utilizaire non-root `appuser`.
- Frontend build `ubuntu:24.04 + Flutter 3.47.3` (ARG `BACKEND_URL`); dev `flutter run -d web-server` en 3000; prod `nginx:alpine` en 80 amb `try_files $uri $uri/ /index.html` (SPA).

## Environa (`backend/.env`, veire `.env.example`)

| Variable | Efecto |
|---|---|
| `APP_ENV` | `development` crea admin `admin/setup` + `create_all`; `production` exige Alembic y bloquea `SECRET_KEY` por defecto y CORS `*` |
| `SECRET_KEY` | Firma JWT (`HS256`); caduca access 30 min, refresh 30 d |
| `DATABASE_URL` | `sqlite:///./clakettes.db` (dev) o `mariadb+pymysql://…` (prod) |
| `CORS_ORIGINS` | Vacío = `*` sin credenciales (solo dev); prod exige orígenes explícitos |
| `PUBLIC_BASE_URL`, `FORWARDED_ALLOW_IPS` | URL pública y proxies de confianza (TLS frontal obligatorio en prod: los tokens DAV viajan en URL) |
| `BACKEND_URL` | `--dart-define` para la app Flutter (también cambiable en la pantalla de backend; persiste en SharedPreferences) |

## Santat e observables

- `GET /health` → `{"status":"healthy"}`; `GET /` → version (`0.3.0`). `ConnectivityMonitor` dins l'app los utiliza coma sonda reala.
- Jornaus: stdout d'uvicorn (tokens DAV redactats); errors d'API en SnackBar + `debugPrint`.
- Limits: còrs ≤10 MB (413), avatar/imatge ≤5 MB (`jpeg/png/webp/gif` amb magic-bytes), vidèo ≤100 MB (`mp4/webm/quicktime`), docs ≤10 MB (pdf); rate limit 100 req/60s per IP (429; `/dav*` 600/60s; bypass amb `TESTING=true`).

## CI

- **GitHub** (push/PR cap a `main,develop`): `backend-lint` + `frontend-lint` + `backend-test` (MariaDB 11 + `alembic upgrade head` + pytest) + `frontend-test` (build_runner + `flutter test`) → `docker-build` (4 imatges).
- **GitLab**: stages `lint → test → build`; `docker-build` sonque en `main` amb push al registry.

Pòrta locala (meteissa que CI): `ruff check .` + `ruff format --check .` + `pytest tests/ -x -q --tb=short` (dempuèi `backend/`), `flutter analyze` + `flutter test` (dempuèi `frontend/`).

## Veire tanben

- [USO.oc.md](USO.oc.md): usatge vidant del desplegament
- [ADMINISTRACION.oc.md](ADMINISTRACION.oc.md): operacions e recuperacion
- [SEGURIDAD.oc.md](SEGURIDAD.oc.md): contraròtles e paramètres de produccion
- [HERRAMIENTAS.oc.md](HERRAMIENTAS.oc.md): scripts e comandas de build/test
