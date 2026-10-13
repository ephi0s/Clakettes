# Infraestrutura — Clakettes

[ES](../es/INFRAESTRUCTURA.md) · [EN](../en/INFRAESTRUCTURA.md) · [FR](../fr/INFRAESTRUCTURA.md) · [DE](../de/INFRAESTRUCTURA.md) · [IT](../it/INFRAESTRUCTURA.md) · [CA](../ca/INFRAESTRUCTURA.md) · [EU](../eu/INFRAESTRUCTURA.md) · [GL](INFRAESTRUCTURA.md) · [OC](../oc/INFRAESTRUCTURA.md)

Perfís, portos, entorno e CI. Operativa diaria en [USO.md](USO.md), lista de endurecido en [SEGURIDAD.md](SEGURIDAD.md).

## Perfís Docker (`docker-compose.yml`)

| Perfil | Comando | Servicios |
|---|---|---|
| dev (sin perfil) | `docker compose up` | backend + frontend |
| db | `docker compose --profile db up` | + MariaDB 11 |
| prod | `docker compose --profile prod up -d` | backend-prod + frontend-prod + db |
| build | perfiles `[build]` en `frontend/docker/compose` | web, linux-x64, linux-appimage, android |
| windows / ci / dev | mismo compose | windows-x64+installer, test+analyze, dev web |

## Portos e volumes

| Puerto | Servicio | Variable |
|---|---|---|
| `8000` | backend y backend-prod | `PORT_BACKEND` |
| `3000` | frontend dev | `PORT_FRONTEND` |
| `80` | frontend-prod (nginx, build web estático) | `PORT_FRONTEND_PROD` |
| `3306` | MariaDB (interno) | `PORT_DB` |

Volúmenes: `./backend:/app` + `backend-data:/app/data`, `./frontend:/app`, `db-data:/var/lib/mysql`. Backups: SQLite = copiar `*.db`; MariaDB = `mariadb-dump` sobre `db-data`.

## Imaxes

- Backend `python:3.12-alpine`, EXPOSE 8000; dev con `uvicorn --reload`, prod como usuario non-root `appuser`.
- Frontend build `ubuntu:24.04 + Flutter 3.47.3` (ARG `BACKEND_URL`); dev `flutter run -d web-server` en 3000; prod `nginx:alpine` en 80 con `try_files $uri $uri/ /index.html` (SPA).

## Entorno (`backend/.env`, ver `.env.example`)

| Variable | Efecto |
|---|---|
| `APP_ENV` | `development` crea admin `admin/setup` + `create_all`; `production` exige Alembic y bloquea `SECRET_KEY` por defecto y CORS `*` |
| `SECRET_KEY` | Firma JWT (`HS256`); caduca access 30 min, refresh 30 d |
| `DATABASE_URL` | `sqlite:///./clakettes.db` (dev) o `mariadb+pymysql://…` (prod) |
| `CORS_ORIGINS` | Vacío = `*` sin credenciales (solo dev); prod exige orígenes explícitos |
| `PUBLIC_BASE_URL`, `FORWARDED_ALLOW_IPS` | URL pública y proxies de confianza (TLS frontal obligatorio en prod: los tokens DAV viajan en URL) |
| `BACKEND_URL` | `--dart-define` para la app Flutter (también cambiable en la pantalla de backend; persiste en SharedPreferences) |

## Saúde e observables

- `GET /health` → `{"status":"healthy"}`; `GET /` → versión (`0.3.0`). `ConnectivityMonitor` na app úsaos como sonda real.
- Logs: stdout de uvicorn (tokens DAV redactados); erros de API en SnackBar + `debugPrint`.
- Límites: corpo ≤10 MB (413), avatar/imaxe ≤5 MB (`jpeg/png/webp/gif` con magic-bytes), vídeo ≤100 MB (`mp4/webm/quicktime`), docs ≤10 MB (pdf); rate limit 100 req/60s por IP (429; `/dav*` 600/60s; bypass con `TESTING=true`).

## CI

- **GitHub** (push/PR a `main,develop`): `backend-lint` + `frontend-lint` + `backend-test` (MariaDB 11 + `alembic upgrade head` + pytest) + `frontend-test` (build_runner + `flutter test`) → `docker-build` (4 imaxes).
- **GitLab**: stages `lint → test → build`; `docker-build` só en `main` con push ao registry.

Porta local (mesma que CI): `ruff check .` + `ruff format --check .` + `pytest tests/ -x -q --tb=short` (desde `backend/`), `flutter analyze` + `flutter test` (desde `frontend/`).

## Ver tamén

- [USO.md](USO.md): uso diario do despregamento
- [ADMINISTRACION.md](ADMINISTRACION.md): operacións e recuperación
- [SEGURIDAD.md](SEGURIDAD.md): controis e parámetros de produción
- [HERRAMIENTAS.md](HERRAMIENTAS.md): scripts e comandos de build/test
