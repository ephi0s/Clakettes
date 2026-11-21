# Infrastruttura — Clakettes

[ES](../es/INFRAESTRUCTURA.md) · [EN](../en/INFRAESTRUCTURA.md) · [FR](../fr/INFRAESTRUCTURA.md) · [DE](../de/INFRAESTRUCTURA.md) · [IT](INFRAESTRUCTURA.md) · [CA](../ca/INFRAESTRUCTURA.md) · [EU](../eu/INFRAESTRUCTURA.md) · [GL](../gl/INFRAESTRUCTURA.md) · [OC](../oc/INFRAESTRUCTURA.md)

Profili, porte, ambiente e CI. Gestione quotidiana in [USO.md](USO.md), checklist di hardening in [SEGURIDAD.md](SEGURIDAD.md).

## Profili Docker (`docker-compose.yml`)

| Profilo | Comando | Servizi |
|---|---|---|
| dev (senza profilo) | `docker compose up` | backend + frontend |
| db | `docker compose --profile db up` | + MariaDB 11 |
| prod | `docker compose --profile prod up -d` | backend-prod + frontend-prod + db |
| build | profili `[build]` in `frontend/docker/compose` | web, linux-x64, linux-appimage, android |
| windows / ci / dev | stesso compose | windows-x64+installer, test+analyze, dev web |

## Porte e volumi

| Porta | Servizio | Variabile |
|---|---|---|
| `8000` | backend e backend-prod | `PORT_BACKEND` |
| `3000` | frontend dev | `PORT_FRONTEND` |
| `80` | frontend-prod (nginx, build web statico) | `PORT_FRONTEND_PROD` |
| `3306` | MariaDB (interno) | `PORT_DB` |

Volumi: `./backend:/app` + `backend-data:/app/data`, `./frontend:/app`, `db-data:/var/lib/mysql`. Backup: SQLite = copiare `*.db`; MariaDB = `mariadb-dump` su `db-data`.

## Immagini

- Backend `python:3.12-alpine`, EXPOSE 8000; dev con `uvicorn --reload`, prod come utente non-root `appuser`.
- Frontend build `ubuntu:24.04 + Flutter 3.47.3` (ARG `BACKEND_URL`); dev `flutter run -d web-server` su 3000; prod `nginx:alpine` su 80 con `try_files $uri $uri/ /index.html` (SPA).

## Ambiente (`backend/.env`, vedi `.env.example`)

| Variabile | Effetto |
|---|---|
| `APP_ENV` | `development` crea admin `admin/setup` + `create_all`; `production` richiede Alembic e blocca `SECRET_KEY` predefinita e CORS `*` |
| `SECRET_KEY` | Firma JWT (`HS256`); access scade a 30 min, refresh a 30 d |
| `DATABASE_URL` | `sqlite:///./clakettes.db` (dev) o `mariadb+pymysql://…` (prod) |
| `CORS_ORIGINS` | Vuoto = `*` senza credenziali (solo dev); prod richiede origini esplicite |
| `PUBLIC_BASE_URL`, `FORWARDED_ALLOW_IPS` | URL pubblico del nodo (manifesto e bundle) e proxy attendibili (TLS frontale obbligatorio in prod: i token DAV viaggiano nell'URL) |
| `MTLS_REQUIRED`, `MTLS_CLIENT_CERT_PATH`, `MTLS_CLIENT_KEY_PATH` | mTLS federato (CN e PEM del certificato) e PEM/chiave che firmano il manifesto RSA-SHA256 |
| `BACKEND_URL` | `--dart-define` per l'app Flutter (cambiabile anche nella schermata backend; persistita in SharedPreferences) |

## Salute e osservabili

- `GET /health` → `{"status":"healthy"}`; `GET /` → versione (`0.3.0`). Il `ConnectivityMonitor` nell'app li usa come sonda reale, con health check per nodo per degradare con eleganza la cache Hive.
- Federazione: `GET /api/federation/resilience/health` e `/metrics` (p50/p95, latenza, errori e ripetizioni); `GET /api/federation/events/stream` mantiene l'SSE con un battito ogni 15 s; `python tools/federation_conformance.py <url> [--json]` verifica nodi terzi.
- Log: stdout di uvicorn (token DAV redatti); errori API in SnackBar + `debugPrint`.
- Limiti: corpo ≤10 MB (413), avatar/immagine ≤5 MB (`jpeg/png/webp/gif` con magic-bytes), video ≤100 MB (`mp4/webm/quicktime`), docs ≤10 MB (pdf); rate limit 100 req/60s per IP (429; `/dav*` 600/60s; bypass con `TESTING=true`).

## CI

- **GitHub** (push/PR su `main,develop`): `backend-lint` + `frontend-lint` + `backend-test` (MariaDB 11 + `alembic upgrade head` + pytest) + `frontend-test` (build_runner + `flutter test`) → `docker-build` (4 immagini).
- **GitLab**: stage `lint → test → build`; `docker-build` solo su `main` con push al registry.

## Vedi anche

- [USO.md](USO.md): utilizzo quotidiano del deployment
- [ADMINISTRACION.md](ADMINISTRACION.md): operazioni e recupero
- [SEGURIDAD.md](SEGURIDAD.md): controlli e parametri di produzione
- [HERRAMIENTAS.md](HERRAMIENTAS.md): script e comandi di build/test
