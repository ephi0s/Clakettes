# Infraestructura — Clakettes

[ES](../es/INFRAESTRUCTURA.md) · [EN](../en/INFRAESTRUCTURA.md) · [FR](../fr/INFRAESTRUCTURA.md) · [DE](../de/INFRAESTRUCTURA.md) · [IT](../it/INFRAESTRUCTURA.md) · [CA](../ca/INFRAESTRUCTURA.md) · [EU](../eu/INFRAESTRUCTURA.md) · [GL](../gl/INFRAESTRUCTURA.md) · [OC](INFRAESTRUCTURA.md)

Perfils, pòrts, environament e CI. Operativa quotidiana dins [USO.md](USO.md), lista de contraròtle de renforçament dins [SEGURIDAD.md](SEGURIDAD.md).

## Perfils Docker (`docker-compose.yml`)

| Perfil | Comanda | Servicis |
|---|---|---|
| dev (sens perfil) | `docker compose up` | backend + frontend |
| db | `docker compose --profile db up` | + MariaDB 11 |
| prod | `docker compose --profile prod up -d` | backend-prod + frontend-prod + db |
| build | perfils `[build]` dins `frontend/docker/compose` | web, linux-x64, linux-appimage, android |
| windows / ci / dev | meteis compose | windows-x64+installer, test+analyze, dev web |

## Pòrts e volums

| Pòrt | Servici | Variabla |
|---|---|---|
| `8000` | backend e backend-prod | `PORT_BACKEND` |
| `3000` | frontend dev | `PORT_FRONTEND` |
| `80` | frontend-prod (nginx, build web estatic) | `PORT_FRONTEND_PROD` |
| `3306` | MariaDB (interne) | `PORT_DB` |

Volums: `./backend:/app` + `backend-data:/app/data`, `./frontend:/app`, `db-data:/var/lib/mysql`. Còpias de seguretat: SQLite = copiar `*.db`; MariaDB = `mariadb-dump` sus `db-data`.

## Imatges

- Backend `python:3.12-alpine`, EXPOSE 8000; dev amb `uvicorn --reload`, prod coma usuari non-root `appuser`.
- Frontend build `ubuntu:24.04 + Flutter 3.47.3` (ARG `BACKEND_URL`); dev `flutter run -d web-server` sus 3000; prod `nginx:alpine` sus 80 amb `try_files $uri $uri/ /index.html` (SPA).

## Environament (`backend/.env`, vejatz `.env.example`)

| Variabla | Efecte |
|---|---|
| `APP_ENV` | `development` crea admin `admin/setup` + `create_all`; `production` exegís Alembic e bloca `SECRET_KEY` per defaut e CORS `*` |
| `SECRET_KEY` | Signatura JWT (`HS256`); access expira 30 min, refresh 30 d |
| `DATABASE_URL` | `sqlite:///./clakettes.db` (dev) o `mariadb+pymysql://…` (prod) |
| `CORS_ORIGINS` | Vuèja = `*` sens credencials (solament dev); prod exegís d'origines explicitas |
| `PUBLIC_BASE_URL`, `FORWARDED_ALLOW_IPS` | URL publica del nose (manifest e bundles) e proxies fisables (TLS frontal obligatòri en prod: los tokens DAV viatjan dins l'URL) |
| `MTLS_REQUIRED`, `MTLS_CA_BUNDLE_PATH`, `MTLS_CLIENT_CERT_PATH`, `MTLS_CLIENT_KEY_PATH` | mTLS federat (CN e PEM del certificat), CA raíç per validar los pares e PEM/clau que signan lo manifest RSA-SHA256 |
| `TESTING` | `1/true/yes/on` (case-insensitive, `app.config.is_testing()`): desactiva totes los rate limits (global 100/60 s, `/dav` 600/60 s, login 5/300 s, refresh 20/60 s, reset 3/300 s, federacion 60/60 s) e l'auto-migracion |
| `SKIP_AUTO_MIGRATE` | `1/true/yes/on`: omet `alembic upgrade head` dins lo lifespan (DB gestionada exteriorament) |
| `RATE_LIMITS_DB_PATH` | Rota de la BD SQLite del limitador de taxas (per defaut `backend/rate_limits.db`) |
| `JWT_ISSUER`, `JWT_AUDIENCE`, `ACCESS_TOKEN_EXPIRE_MINUTES` | Claims validats e TTL del token d'accès (`clakettes`, `clakettes-api`, 30 min) |
| `PAYMENTS_PROVIDER`, `MOCK_WEBHOOK_SECRET`, `MOCK_PAYMENTS_FORCE_FAIL` | Fornisseire (`mock` per defaut) e secret del webhook simulat |
| `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `REDSYS_MERCHANT_CODE`, `REDSYS_TERMINAL`, `REDSYS_SECRET_KEY`, `REDSYS_SANDBOX`, `REDSYS_CURRENCY` | Credencialas Stripe/Redsys (sandbox per defaut, moneda `978`) |
| `BACKEND_URL` | `--dart-define` per l'app Flutter (tanben cambiabile dins l'ecran de backend; persistís dins SharedPreferences) |

## Santat e observables

- `GET /health` → `{"status":"healthy","db_revision":…}`; `GET /` → version (`0.3.0`, constanta `APP_VERSION`). Lo `ConnectivityMonitor` de l'app los utiliza coma sonda reala: `NodeHealth` per nose (`testNode()`, laténcia, `offlineNodeCount`, `isDegraded`) degrada la cach Hive amb elegància e mòstra `DegradedNodesBanner` amb recompte e boton de reensaj.
- Federacion: `GET /api/federation/resilience/health` e `/metrics` (p50/p95, laténcia, fracasses e reensajos); `GET /api/federation/events/stream` mantén lo SSE amb un batement cada 15 s; `python tools/federation_conformance.py <url> [--json]` verifica de noses tèrces.
- Jornals: stdout d'uvicorn (tokens DAV escafats); errors d'API dins SnackBar + `debugPrint`.
- Limites: còs ≤10 MB (413), avatar/imatge ≤5 MB (`jpeg/png/webp/gif` amb magic-bytes), vidèo ≤100 MB (`mp4/webm/quicktime`), documents ≤10 MB (pdf); rate limit 100 req/60s per IP (429; `/dav*` 600/60s; bypass amb `TESTING` ∈ {1,true,yes,on}).

## CI

- **GitHub** (push/PR a `main,develop`): `backend-lint` + `frontend-lint` + `backend-test` (SQLite, `TESTING=true`, pytest amb `-m "not interop"`) + `backend-migration` (MariaDB 11 + `alembic upgrade head`) + `frontend-test` (build_runner + `flutter test`) → `docker-build` (4 imatges).
- **GitLab**: etapas `lint → test → build`; `docker-build` solament sus `main` amb push al registry.

### Actualizacion de dependéncias

- `.github/dependabot.yml`: pip en `/backend` e pub en `/frontend`, setmanals (diluns), gropes `backend-deps`/`frontend-deps`, fins a 10 PRs dobèrts, etiquetas `backend`/`frontend` + `dependencies`, assignee `ephi0s` e prefixes `build(backend):`/`build(frontend):`. Se ignoran las actualizacions `version-update:semver-major`.
- `.github/workflows/dependabot-automerge.yml`: `pull_request_target`, solament per `dependabot[bot]`; utiliza `dependabot/fetch-metadata@v2` e activa `gh pr merge --auto --squash` sonque en patch/minor. Las majoras demoran a revision manuala e lo merge efectiu exigís CI verda.
- `.github/workflows/dependabot-rebase.yml`: diluns 04:17 UTC (`17 4 * * 1`) e `workflow_dispatch`; actualiza las brancas dels PRs dobèrts de Dependabot via `PUT /repos/{repo}/pulls/{n}/update-branch`.

## Vejatz tanben

- [USO.md](USO.md): utilizacion quotidiana del desplegament
- [ADMINISTRACION.md](ADMINISTRACION.md): operacions e recuperacion
- [SEGURIDAD.md](SEGURIDAD.md): contròls e parametres de produccion
- [HERRAMIENTAS.md](HERRAMIENTAS.md): scripts e comandas de build/test
