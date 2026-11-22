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
| `MTLS_REQUIRED`, `MTLS_CA_BUNDLE_PATH`, `MTLS_CLIENT_CERT_PATH`, `MTLS_CLIENT_KEY_PATH` | Federazio-mTLSa (ziurtagiriaren CNa eta PEMa), pareak balioztatzeko CA erroa eta RSA-SHA256 manifestua sinatzen duten PEMa/gakoa |
| `TESTING` | `1/true/yes/on` (case-insensitive, `app.config.is_testing()`): rate limit guztiak (global 100/60 s, `/dav` 600/60 s, login 5/300 s, refresh 20/60 s, reset 3/300 s, federazioa 60/60 s) eta auto-migrazioa desaktibatzen ditu |
| `SKIP_AUTO_MIGRATE` | `1/true/yes/on`: `alembic upgrade head` saltzen du lifespan-ean (kanpoan kudeatutako DBa) |
| `RATE_LIMITS_DB_PATH` | Rate limiter-aren SQLite DBaren bidea (lehenetsiz `backend/rate_limits.db`) |
| `JWT_ISSUER`, `JWT_AUDIENCE`, `ACCESS_TOKEN_EXPIRE_MINUTES` | Balioztatutako claim-ak eta sarbide-tokenaren TTL-a (`clakettes`, `clakettes-api`, 30 min) |
| `PAYMENTS_PROVIDER`, `MOCK_WEBHOOK_SECRET`, `MOCK_PAYMENTS_FORCE_FAIL` | Hornitzailea (`mock` lehenetsiz) eta webhook simulatuaren sekretua |
| `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `REDSYS_MERCHANT_CODE`, `REDSYS_TERMINAL`, `REDSYS_SECRET_KEY`, `REDSYS_SANDBOX`, `REDSYS_CURRENCY` | Stripe/Redsys kredentzialak (sandbox lehenetsiz, txanpona `978`) |
| `BACKEND_URL` | Flutter app-erako `--dart-define` (backend-pantailan ere alda daiteke; SharedPreferences-en irauten du) |

## Osasuna eta behatzekoak

- `GET /health` → `{"status":"healthy","db_revision":…}`; `GET /` → bertsioa (`0.3.0`, `APP_VERSION` konstantea). App-eko `ConnectivityMonitor`-ek benetako zunda gisa erabiltzen ditu: nodo bakoitzeko `NodeHealth`-ek (`testNode()`, latentzia, `offlineNodeCount`, `isDegraded`) Hive cache-a dotoreki degradatzen du eta `DegradedNodesBanner` erakusten du kopuruarekin eta birsaio-botoiarekin.
- Federazioa: `GET /api/federation/resilience/health` eta `/metrics` (p50/p95, latentzia, hutsegiteak eta birsaioak); `GET /api/federation/events/stream`-ek SSEa mantentzen du 15 s an bihotz-taupadarekin; `python tools/federation_conformance.py <url> [--json]` bidez hirugarren nodoak egiaztatzen dira.
- Logak: uvicorn stdout (DAV tokenak ezkutatuta); API erroreak SnackBar + `debugPrint` bidez.
- Mugak: gorputza ≤10 MB (413), avatar/irudia ≤5 MB (`jpeg/png/webp/gif` magic-bytes-ekin), bideoa ≤100 MB (`mp4/webm/quicktime`), dokumentuak ≤10 MB (pdf); rate limit 100 req/60s IP bakoitzeko (429; `/dav*` 600/60s; `TESTING` ∈ {1,true,yes,on} bidez saihestuta).

## CI

- **GitHub** (push/PR `main,develop`-era): `backend-lint` + `frontend-lint` + `backend-test` (SQLite, `TESTING=true`, pytest `-m "not interop"` erabiliz) + `backend-migration` (MariaDB 11 + `alembic upgrade head`) + `frontend-test` (build_runner + `flutter test`) → `docker-build` (4 irudi).
- **GitLab**: `lint → test → build` etapak; `docker-build` soilik `main`-en registry-ra push eginez.

### Mendekotasunen eguneratzea

- `.github/dependabot.yml`: pip `/backend`-n eta pub `/frontend`-n, astero (astelehena), `backend-deps`/`frontend-deps` taldeak, gehienez 10 PR ireki, `backend`/`frontend` + `dependencies` etiketak, `ephi0s` esleitua eta `build(backend):`/`build(frontend):` aurrizkiak. `version-update:semver-major` eguneraketak baztertzen dira.
- `.github/workflows/dependabot-automerge.yml`: `pull_request_target`, `dependabot[bot]`-entzat soilik; `dependabot/fetch-metadata@v2` erabiltzen du eta `gh pr merge --auto --squash` patch/minor-ean soilik aktibatzen du. Major-ak eskuzko berrikuspenerako geratzen dira eta benetako merge-ak CI berdea eskatzen du.
- `.github/workflows/dependabot-rebase.yml`: astelehenetan 04:17 UTC (`17 4 * * 1`) eta `workflow_dispatch`; Dependabot-en PR irekien adarrak `PUT /repos/{repo}/pulls/{n}/update-branch` bidez eguneratzen ditu.

## Ikus ere

- [USO.md](USO.md): inplementazioaren eguneroko erabilera
- [ADMINISTRACION.md](ADMINISTRACION.md): operazioak eta berreskurapena
- [SEGURIDAD.md](SEGURIDAD.md): ekoizpeneko kontrolak eta parametroak
- [HERRAMIENTAS.md](HERRAMIENTAS.md): build/test script-ak eta komandoak
