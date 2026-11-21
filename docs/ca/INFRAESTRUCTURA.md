# Infraestructura — Clakettes

[ES](../es/INFRAESTRUCTURA.md) · [EN](../en/INFRAESTRUCTURA.md) · [FR](../fr/INFRAESTRUCTURA.md) · [DE](../de/INFRAESTRUCTURA.md) · [IT](../it/INFRAESTRUCTURA.md) · [CA](INFRAESTRUCTURA.md) · [EU](../eu/INFRAESTRUCTURA.md) · [GL](../gl/INFRAESTRUCTURA.md) · [OC](../oc/INFRAESTRUCTURA.md)

Perfils, ports, entorn i CI. Operativa diària a [USO.md](USO.md), llista de comprovació d'enduriment a [SEGURIDAD.md](SEGURIDAD.md).

## Perfils Docker (`docker-compose.yml`)

| Perfil | Comando | Serveis |
|---|---|---|
| dev (sense perfil) | `docker compose up` | backend + frontend |
| db | `docker compose --profile db up` | + MariaDB 11 |
| prod | `docker compose --profile prod up -d` | backend-prod + frontend-prod + db |
| build | perfils `[build]` a `frontend/docker/compose` | web, linux-x64, linux-appimage, android |
| windows / ci / dev | mateix compose | windows-x64+installer, test+analyze, dev web |

## Ports i volums

| Port | Servei | Variable |
|---|---|---|
| `8000` | backend i backend-prod | `PORT_BACKEND` |
| `3000` | frontend dev | `PORT_FRONTEND` |
| `80` | frontend-prod (nginx, build web estátic) | `PORT_FRONTEND_PROD` |
| `3306` | MariaDB (intern) | `PORT_DB` |

Volums: `./backend:/app` + `backend-data:/app/data`, `./frontend:/app`, `db-data:/var/lib/mysql`. Còpies de seguretat: SQLite = copiar `*.db`; MariaDB = `mariadb-dump` sobre `db-data`.

## Imatges

- Backend `python:3.12-alpine`, EXPOSE 8000; dev amb `uvicorn --reload`, prod com a usuari no-root `appuser`.
- Frontend build `ubuntu:24.04 + Flutter 3.47.3` (ARG `BACKEND_URL`); dev `flutter run -d web-server` a 3000; prod `nginx:alpine` a 80 amb `try_files $uri $uri/ /index.html` (SPA).

## Entorn (`backend/.env`, vegeu `.env.example`)

| Variable | Efecte |
|---|---|
| `APP_ENV` | `development` crea admin `admin/setup` + `create_all`; `production` exigeix Alembic i bloqueja `SECRET_KEY` per defecte i CORS `*` |
| `SECRET_KEY` | Signatura JWT (`HS256`); caduca access 30 min, refresh 30 d |
| `DATABASE_URL` | `sqlite:///./clakettes.db` (dev) o `mariadb+pymysql://…` (prod) |
| `CORS_ORIGINS` | Buit = `*` sense credencials (només dev); prod exigeix orígens explícits |
| `PUBLIC_BASE_URL`, `FORWARDED_ALLOW_IPS` | URL pública del node (manifest i bundles) i proxies de confiança (TLS frontal obligatori en prod: els tokens DAV viatgen a l'URL) |
| `MTLS_REQUIRED`, `MTLS_CLIENT_CERT_PATH`, `MTLS_CLIENT_KEY_PATH` | mTLS federat (CN i PEM del certificat) i PEM/clau que signen el manifest RSA-SHA256 |
| `BACKEND_URL` | `--dart-define` per a l'app Flutter (també canviable a la pantalla de backend; persisteix a SharedPreferences) |

## Salut i observables

- `GET /health` → `{"status":"healthy"}`; `GET /` → versió (`0.3.0`). El `ConnectivityMonitor` de l'app els fa servir com a sonda real, amb health checks per node per degradar la caché Hive amb elegància.
- Federació: `GET /api/federation/resilience/health` i `/metrics` (p50/p95, latència, fallades i reintents); `GET /api/federation/events/stream` manté l'SSE amb un batec cada 15 s; `python tools/federation_conformance.py <url> [--json]` verifica nodes tercers.
- Logs: stdout d'uvicorn (tokens DAV redactats); errors d'API en SnackBar + `debugPrint`.
- Límits: cos ≤10 MB (413), avatar/imatge ≤5 MB (`jpeg/png/webp/gif` amb magic-bytes), vídeo ≤100 MB (`mp4/webm/quicktime`), docs ≤10 MB (pdf); rate limit 100 req/60s per IP (429; `/dav*` 600/60s; bypass amb `TESTING=true`).

## CI

- **GitHub** (push/PR a `main,develop`): `backend-lint` + `frontend-lint` + `backend-test` (MariaDB 11 + `alembic upgrade head` + pytest) + `frontend-test` (build_runner + `flutter test`) → `docker-build` (4 imatges).
- **GitLab**: stages `lint → test → build`; `docker-build` només a `main` amb push al registry.

## Vegeu també

- [USO.md](USO.md): ús diari del desplegament
- [ADMINISTRACION.md](ADMINISTRACION.md): operacions i recuperació
- [SEGURIDAD.md](SEGURIDAD.md): controls i paràmetres de producció
- [HERRAMIENTAS.md](HERRAMIENTAS.md): scripts i comandos de build/test
