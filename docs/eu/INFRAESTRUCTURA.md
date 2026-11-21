# Azpiegitura — Clakettes

[ES](../es/INFRAESTRUCTURA.md) · [EN](../en/INFRAESTRUCTURA.md) · [FR](../fr/INFRAESTRUCTURA.md) · [DE](../de/INFRAESTRUCTURA.md) · [IT](../it/INFRAESTRUCTURA.md) · [CA](../ca/INFRAESTRUCTURA.md) · [EU](INFRAESTRUCTURA.md) · [GL](../gl/INFRAESTRUCTURA.md) · [OC](../oc/INFRAESTRUCTURA.md)

Profilak, atak, ingurunea eta CI. Eguneroko operazioa [USO.md](USO.md) fitxategian, gogortze-kontrol zerrenda [SEGURIDAD.md](SEGURIDAD.md) fitxategian.

## Docker profilak (`docker-compose.yml`)

| Profila | Komandoa | Zerbitzuak |
|---|---|---|
| dev (profilik gabe) | `docker compose up` | backend + frontend |
| db | `docker compose --profile db up` | + MariaDB 11 |
| prod | `docker compose --profile prod up -d` | backend-prod + frontend-prod + db |
| build | `[build]` profilak `frontend/docker/compose`-n | web, linux-x64, linux-appimage, android |
| windows / ci / dev | compose bera | windows-x64+installer, test+analyze, dev web |

## Atak eta bolumenak

| Ataka | Zerbitzua | Aldagaia |
|---|---|---|
| `8000` | backend eta backend-prod | `PORT_BACKEND` |
| `3000` | frontend dev | `PORT_FRONTEND` |
| `80` | frontend-prod (nginx, web build estatikoa) | `PORT_FRONTEND_PROD` |
| `3306` | MariaDB (barnekoa) | `PORT_DB` |

Bolumenak: `./backend:/app` + `backend-data:/app/data`, `./frontend:/app`, `db-data:/var/lib/mysql`. Babeskopiak: SQLite = `*.db` kopiatu; MariaDB = `mariadb-dump` `db-data`-n gainean.

## Irudiak

- Backend `python:3.12-alpine`, EXPOSE 8000; dev `uvicorn --reload`-ekin, prod `appuser` erabiltzaile ez-root gisa.
- Frontend build `ubuntu:24.04 + Flutter 3.47.3` (ARG `BACKEND_URL`); dev `flutter run -d web-server` 3000-n; prod `nginx:alpine` 80-n `try_files $uri $uri/ /index.html` (SPA) erabiliz.

## Ingurunea (`backend/.env`, ikusi `.env.example`)

| Aldagaia | Eragina |
|---|---|
| `APP_ENV` | `development`-ek `admin/setup` admin + `create_all` sortzen ditu; `production`-ek Alembic eskatzen du eta lehenetsitako `SECRET_KEY` eta CORS `*` blokeatzen ditu |
| `SECRET_KEY` | JWT sinadura (`HS256`); access-a 30 min eta refresh-a 30 d iraungitzen dira |
| `DATABASE_URL` | `sqlite:///./clakettes.db` (dev) edo `mariadb+pymysql://…` (prod) |
| `CORS_ORIGINS` | Hutsa = `*` kredentzialik gabe (soilik dev); prod-ek jatorri esplizituak eskatzen ditu |
| `PUBLIC_BASE_URL`, `FORWARDED_ALLOW_IPS` | Nodoaren URL publikoa (manifestua eta bundle-ak) eta proxy fidagarriak (aurreko TLS nahitaezkoa prod-en: DAV tokenak URLan bidaiatzen dira) |
| `MTLS_REQUIRED`, `MTLS_CLIENT_CERT_PATH`, `MTLS_CLIENT_KEY_PATH` | Federazio-mTLSa (ziurtagiriaren CNa eta PEMa) eta RSA-SHA256 manifestua sinatzen duten PEMa/gakoa |
| `BACKEND_URL` | Flutter app-erako `--dart-define` (backend-pantailan ere alda daiteke; SharedPreferences-en irauten du) |

## Osasuna eta behatzekoak

- `GET /health` → `{"status":"healthy"}`; `GET /` → bertsioa (`0.3.0`). App-eko `ConnectivityMonitor`-ek benetako zunda gisa erabiltzen ditu, nodo bakoitzeko osasun-egiaztapenekin Hive cache-a dotoreki degradatzeko.
- Federazioa: `GET /api/federation/resilience/health` eta `/metrics` (p50/p95, latentzia, hutsegiteak eta birsaioak); `GET /api/federation/events/stream`-ek SSEa mantentzen du 15 s an bihotz-taupadarekin; `python tools/federation_conformance.py <url> [--json]` bidez hirugarren nodoak egiaztatzen dira.
- Logak: uvicorn stdout (DAV tokenak ezkutatuta); API erroreak SnackBar + `debugPrint` bidez.
- Mugak: gorputza ≤10 MB (413), avatar/irudia ≤5 MB (`jpeg/png/webp/gif` magic-bytes-ekin), bideoa ≤100 MB (`mp4/webm/quicktime`), dokumentuak ≤10 MB (pdf); rate limit 100 req/60s IP bakoitzeko (429; `/dav*` 600/60s; `TESTING=true` bidez saihestuta).

## CI

- **GitHub** (push/PR `main,develop`-era): `backend-lint` + `frontend-lint` + `backend-test` (MariaDB 11 + `alembic upgrade head` + pytest) + `frontend-test` (build_runner + `flutter test`) → `docker-build` (4 irudi).
- **GitLab**: `lint → test → build` etapak; `docker-build` soilik `main`-en registry-ra push eginez.

## Ikus ere

- [USO.md](USO.md): inplementazioaren eguneroko erabilera
- [ADMINISTRACION.md](ADMINISTRACION.md): operazioak eta berreskurapena
- [SEGURIDAD.md](SEGURIDAD.md): ekoizpeneko kontrolak eta parametroak
- [HERRAMIENTAS.md](HERRAMIENTAS.md): build/test script-ak eta komandoak
