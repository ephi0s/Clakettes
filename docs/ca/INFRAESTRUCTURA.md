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
| `MTLS_REQUIRED`, `MTLS_CA_BUNDLE_PATH`, `MTLS_CLIENT_CERT_PATH`, `MTLS_CLIENT_KEY_PATH` | mTLS federat (CN i PEM del certificat), CA arrel per validar els pars i PEM/clau que signen el manifest RSA-SHA256 |
| `TESTING` | `1/true/yes/on` (case-insensitive, `app.config.is_testing()`): desactiva tots els rate limits (global 100/60 s, `/dav` 600/60 s, login 5/300 s, refresh 20/60 s, reset 3/300 s, federació 60/60 s) i l'auto-migració |
| `SKIP_AUTO_MIGRATE` | `1/true/yes/on`: omiteix `alembic upgrade head` al lifespan (BD gestionada externament) |
| `RATE_LIMITS_DB_PATH` | Ruta de la BD SQLite del rate limiter (per defecte `backend/rate_limits.db`) |
| `JWT_ISSUER`, `JWT_AUDIENCE`, `ACCESS_TOKEN_EXPIRE_MINUTES` | Claims validats i TTL del token d'accés (`clakettes`, `clakettes-api`, 30 min) |
| `PAYMENTS_PROVIDER`, `MOCK_WEBHOOK_SECRET`, `MOCK_PAYMENTS_FORCE_FAIL` | Proveïdor (`mock` per defecte) i secret del webhook simulat |
| `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `REDSYS_MERCHANT_CODE`, `REDSYS_TERMINAL`, `REDSYS_SECRET_KEY`, `REDSYS_SANDBOX`, `REDSYS_CURRENCY` | Credencials Stripe/Redsys (sandbox per defecte, moneda `978`) |
| `BACKEND_URL` | `--dart-define` per a l'app Flutter (també canviable a la pantalla de backend; persisteix a SharedPreferences) |

## Salut i observables

- `GET /health` → `{"status":"healthy","db_revision":…}`; `GET /` → versió (`0.3.0`, constant `APP_VERSION`). El `ConnectivityMonitor` de l'app els fa servir com a sonda real: `NodeHealth` per node (`testNode()`, latència, `offlineNodeCount`, `isDegraded`) degrada la caché Hive amb elegància i mostra `DegradedNodesBanner` amb recompte i botó de reintent.
- Federació: `GET /api/federation/resilience/health` i `/metrics` (p50/p95, latència, fallades i reintents); `GET /api/federation/events/stream` manté l'SSE amb un batec cada 15 s; `python tools/federation_conformance.py <url> [--json]` verifica nodes tercers.
- Logs: stdout d'uvicorn (tokens DAV redactats); errors d'API en SnackBar + `debugPrint`.
- Límits: cos ≤10 MB (413), avatar/imatge ≤5 MB (`jpeg/png/webp/gif` amb magic-bytes), vídeo ≤100 MB (`mp4/webm/quicktime`), docs ≤10 MB (pdf); rate limit 100 req/60s per IP (429; `/dav*` 600/60s; bypass amb `TESTING` ∈ {1,true,yes,on}).

## CI

- **GitHub** (push/PR a `main,develop`): `backend-lint` + `frontend-lint` + `backend-test` (SQLite, `TESTING=true`, pytest amb `-m "not interop"`) + `backend-migration` (MariaDB 11 + `alembic upgrade head`) + `frontend-test` (build_runner + `flutter test`) → `docker-build` (4 imatges).
- **GitLab**: stages `lint → test → build`; `docker-build` només a `main` amb push al registry.

### Actualització de dependències

- `.github/dependabot.yml`: pip a `/backend` i pub a `/frontend`, setmanals (dilluns), grups `backend-deps`/`frontend-deps`, fins a 10 PRs oberts, etiquetes `backend`/`frontend` + `dependencies`, assignee `ephi0s` i prefixos `build(backend):`/`build(frontend):`. S'ignoren actualitzacions `version-update:semver-major`.
- `.github/workflows/dependabot-automerge.yml`: `pull_request_target`, només per a `dependabot[bot]`; fa servir `dependabot/fetch-metadata@v2` i activa `gh pr merge --auto --squash` només en patch/minor. Les majors queden a revisió manual i el merge efectiu exigeix CI verda.
- `.github/workflows/dependabot-rebase.yml`: dilluns 04:17 UTC (`17 4 * * 1`) i `workflow_dispatch`; actualitza les branques dels PRs oberts de Dependabot via `PUT /repos/{repo}/pulls/{n}/update-branch`.

## Vegeu també

- [USO.md](USO.md): ús diari del desplegament
- [ADMINISTRACION.md](ADMINISTRACION.md): operacions i recuperació
- [SEGURIDAD.md](SEGURIDAD.md): controls i paràmetres de producció
- [HERRAMIENTAS.md](HERRAMIENTAS.md): scripts i comandos de build/test
