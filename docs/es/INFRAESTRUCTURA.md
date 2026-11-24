# Infraestructura — Clakettes

[ES](INFRAESTRUCTURA.md) · [EN](../en/INFRAESTRUCTURA.md) · [FR](../fr/INFRAESTRUCTURA.md) · [DE](../de/INFRAESTRUCTURA.md) · [IT](../it/INFRAESTRUCTURA.md) · [CA](../ca/INFRAESTRUCTURA.md) · [EU](../eu/INFRAESTRUCTURA.md) · [GL](../gl/INFRAESTRUCTURA.md) · [OC](../oc/INFRAESTRUCTURA.md)

Perfiles, puertos, entorno y CI. Operativa diaria en [USO.md](USO.md), checklist de endurecido en [SEGURIDAD.md](SEGURIDAD.md).

## Perfiles Docker (`docker-compose.yml`)

| Perfil | Comando | Servicios |
|---|---|---|
| dev (sin perfil) | `docker compose up` | backend + frontend |
| db | `docker compose --profile db up` | + MariaDB 11 |
| prod | `docker compose --profile prod up -d` | backend-prod + frontend-prod + db |
| build | perfiles `[build]` en `frontend/docker/compose` | web, linux-x64, linux-appimage, android |
| windows / ci / dev | mismo compose | windows-x64+installer, test+analyze, dev web |

## Puertos y volúmenes

| Puerto | Servicio | Variable |
|---|---|---|
| `8000` | backend y backend-prod | `PORT_BACKEND` |
| `3000` | frontend dev | `PORT_FRONTEND` |
| `80` | frontend-prod (nginx, build web estático) | `PORT_FRONTEND_PROD` |
| `3306` | MariaDB (interno) | `PORT_DB` |

Volúmenes: `./backend:/app` + `backend-data:/app/data`, `./frontend:/app`, `db-data:/var/lib/mysql`. Backups: SQLite = copiar `*.db`; MariaDB = `mariadb-dump` sobre `db-data`.

## Imágenes

- Backend `python:3.12-alpine`, EXPOSE 8000; dev con `uvicorn --reload`, prod como usuario no-root `appuser`.
- Frontend build `ubuntu:24.04 + Flutter 3.50.1` (ARG `BACKEND_URL`); dev `flutter run -d web-server` en 3000; prod `nginx:alpine` en 80 con `try_files $uri $uri/ /index.html` (SPA).

## Entorno (`backend/.env`, ver `.env.example`)

| Variable | Efecto |
|---|---|
| `APP_ENV` | `development` crea admin `admin/setup` + `create_all`; `production` exige Alembic y bloquea `SECRET_KEY` por defecto y CORS `*` |
| `SECRET_KEY` | Firma JWT (`HS256`); caduca access 30 min, refresh 30 d |
| `DATABASE_URL` | `sqlite:///./clakettes.db` (dev) o `mariadb+pymysql://…` (prod) |
| `CORS_ORIGINS` | Vacío = `*` sin credenciales (solo dev); prod exige orígenes explícitos |
| `PUBLIC_BASE_URL`, `FORWARDED_ALLOW_IPS` | URL pública del nodo (manifiesto y bundles) y proxies de confianza (TLS frontal obligatorio en prod: los tokens DAV viajan en URL) |
| `MTLS_REQUIRED`, `MTLS_CA_BUNDLE_PATH`, `MTLS_CLIENT_CERT_PATH`, `MTLS_CLIENT_KEY_PATH` | mTLS federado (CN y PEM del certificado), CA raíz para validar a los pares y PEM/clave que firman el manifiesto RSA-SHA256 |
| `TESTING` | `1/true/yes/on` (case-insensitive, `app.config.is_testing()`): desactiva todos los rate limits (global 100/60 s, `/dav` 600/60 s, login 5/300 s, refresh 20/60 s, reset 3/300 s, federación 60/60 s) y la auto-migración |
| `SKIP_AUTO_MIGRATE` | `1/true/yes/on`: omite `alembic upgrade head` en el lifespan (DB gestionada externamente) |
| `RATE_LIMITS_DB_PATH` | Ruta de la BD SQLite del rate limiter (por defecto `backend/rate_limits.db`) |
| `JWT_ISSUER`, `JWT_AUDIENCE`, `ACCESS_TOKEN_EXPIRE_MINUTES` | Claims validados y TTL del access token (`clakettes`, `clakettes-api`, 30 min) |
| `PAYMENTS_PROVIDER`, `MOCK_WEBHOOK_SECRET`, `MOCK_PAYMENTS_FORCE_FAIL` | Proveedor (`mock` por defecto) y secreto del webhook simulado |
| `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `REDSYS_MERCHANT_CODE`, `REDSYS_TERMINAL`, `REDSYS_SECRET_KEY`, `REDSYS_SANDBOX`, `REDSYS_CURRENCY` | Credenciales de Stripe/Redsys (sandbox por defecto, moneda `978`) |
| `BACKEND_URL` | `--dart-define` para la app Flutter (también cambiable en la pantalla de backend; persiste en SharedPreferences) |

## Salud y observables

- `GET /health` → `{"status":"healthy","db_revision":…}`; `GET /` → la versión devuelta por `APP_VERSION`. `ConnectivityMonitor` en la app los usa como sonda real: `NodeHealth` por nodo (`testNode()`, latencia, `offlineNodeCount`, `isDegraded`) degrada la caché Hive con elegancia y muestra `DegradedNodesBanner` con recuento y botón de reintento.
- Federación: `GET /api/federation/resilience/health` y `/metrics` (p50/p95, latencia, fallos y reintentos); `GET /api/federation/events/stream` mantiene el SSE con un latido cada 15 s; `python tools/federation_conformance.py <url> [--json]` verifica nodos terceros.
- Logs: stdout de uvicorn (tokens DAV redactados); errores de API en SnackBar + `debugPrint`.
- Límites: cuerpo ≤10 MB (413), avatar/imagen ≤5 MB (`jpeg/png/webp/gif` con magic-bytes), vídeo ≤100 MB (`mp4/webm/quicktime`), docs ≤10 MB (pdf); rate limit 100 req/60s por IP (429; `/dav*` 600/60s; bypass con `TESTING` ∈ {1,true,yes,on}).

## CI

- **GitHub** (push/PR a `main,develop`): `backend-lint` + `frontend-lint` + `docs-api` (verifica que `API.md` esté regenerada) + `backend-test` (SQLite, `TESTING=true`, pytest con `-m "not interop"`) + `backend-migration` (MariaDB 11 + `alembic upgrade head`) + `frontend-test` (build_runner + `flutter test`) → `docker-build` (las imágenes de backend y frontend, dev y prod).
- **GitLab**: stages `lint → test → build`; los jobs de lint incluyen `docs-api` (verifica que `API.md` esté regenerada); `docker-build` solo en `main` con push al registry.

### Actualización de dependencias

- `.github/dependabot.yml`: pip en `/backend` y pub en `/frontend`, semanales (lunes), grupos `backend-deps`/`frontend-deps`, hasta 10 PRs abiertos, etiquetas `backend`/`frontend` + `dependencies`, assignee `ephi0s` y prefijos `build(backend):`/`build(frontend):`. Se ignoran actualizaciones `version-update:semver-major`.
- `.github/workflows/dependabot-automerge.yml`: `pull_request_target`, solo para `dependabot[bot]`; usa `dependabot/fetch-metadata@v2` y activa `gh pr merge --auto --squash` únicamente en patch/minor. Las mayores quedan a revisión manual y el merge efectivo exige CI verde.
- `.github/workflows/dependabot-rebase.yml`: lunes 04:17 UTC (`17 4 * * 1`) y `workflow_dispatch`; actualiza las ramas de los PRs abiertos de Dependabot vía `PUT /repos/{repo}/pulls/{n}/update-branch`.

## Ver también

- [USO.md](USO.md): uso diario del despliegue
- [ADMINISTRACION.md](ADMINISTRACION.md): operaciones y recuperación
- [SEGURIDAD.md](SEGURIDAD.md): controles y parámetros de producción
- [HERRAMIENTAS.md](HERRAMIENTAS.md): scripts y comandos de build/test