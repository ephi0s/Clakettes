# Azpiegitura — Clakettes

[ES](../es/INFRAESTRUCTURA.md) · [EN](../en/INFRAESTRUCTURA.md) · [FR](../fr/INFRAESTRUCTURA.md) · [DE](../de/INFRAESTRUCTURA.md) · [IT](../it/INFRAESTRUCTURA.md) · [CA](../ca/INFRAESTRUCTURA.md) · [EU](INFRAESTRUCTURA.md) · [GL](../gl/INFRAESTRUCTURA.md) · [OC](../oc/INFRAESTRUCTURA.md)

Profilak, portuak, ingurunea eta CI. Eguneroko operatiba [USO.md](USO.md)-n, gogortze-checklist-a [SEGURIDAD.md](SEGURIDAD.md)-n.

## Docker profilak (`docker-compose.yml`)

| Perfil | Comando | Servicios |
|---|---|---|
| dev (sin perfil) | `docker compose up` | backend + frontend |
| db | `docker compose --profile db up` | + MariaDB 11 |
| prod | `docker compose --profile prod up -d` | backend-prod + frontend-prod + db |
| build | perfiles `[build]` en `frontend/docker/compose` | web, linux-x64, linux-appimage, android |
| windows / ci / dev | mismo compose | windows-x64+installer, test+analyze, dev web |

## Portuak eta bolumenak

| Puerto | Servicio | Variable |
|---|---|---|
| `8000` | backend y backend-prod | `PORT_BACKEND` |
| `3000` | frontend dev | `PORT_FRONTEND` |
| `80` | frontend-prod (nginx, build web estático) | `PORT_FRONTEND_PROD` |
| `3306` | MariaDB (interno) | `PORT_DB` |

Bolumenak: `./backend:/app` + `backend-data:/app/data`, `./frontend:/app`, `db-data:/var/lib/mysql`. Backup-ak: SQLite = `*.db` kopiatu; MariaDB = `mariadb-dump` `db-data`-ren gainean.

## Irudiak

- Backend `python:3.12-alpine`, EXPOSE 8000; dev `uvicorn --reload`-ekin, prod `appuser` root-ez den erabiltzaile gisa.
- Frontend build `ubuntu:24.04 + Flutter 3.47.3` (ARG `BACKEND_URL`); dev `flutter run -d web-server` 3000-n; prod `nginx:alpine` 80-n `try_files $uri $uri/ /index.html`-ekin (SPA).

## Ingurunea (`backend/.env`, ikusi `.env.example`)

| Variable | Efecto |
|---|---|
| `APP_ENV` | `development` crea admin `admin/setup` + `create_all`; `production` exige Alembic y bloquea `SECRET_KEY` por defecto y CORS `*` |
| `SECRET_KEY` | Firma JWT (`HS256`); caduca access 30 min, refresh 30 d |
| `DATABASE_URL` | `sqlite:///./clakettes.db` (dev) o `mariadb+pymysql://…` (prod) |
| `CORS_ORIGINS` | Vacío = `*` sin credenciales (solo dev); prod exige orígenes explícitos |
| `PUBLIC_BASE_URL`, `FORWARDED_ALLOW_IPS` | URL pública y proxies de confianza (TLS frontal obligatorio en prod: los tokens DAV viajan en URL) |
| `BACKEND_URL` | `--dart-define` para la app Flutter (también cambiable en la pantalla de backend; persiste en SharedPreferences) |

## Osasuna eta behatgarriak

- `GET /health` → `{"status":"healthy"}`; `GET /` → bertsioa (`0.3.0`). App-ko `ConnectivityMonitor`-ek benetako zunda gisa erabiltzen ditu.
- Log-ak: uvicorn-en stdout (DAV token-ak redaktatuta); API erroreak SnackBar + `debugPrint`-en.
- Mugak: gorputza ≤10 MB (413), avatar/irudia ≤5 MB (`jpeg/png/webp/gif` magic-byte-ekin), bideoa ≤100 MB (`mp4/webm/quicktime`), doc-ak ≤10 MB (pdf); rate limit 100 req/60s IP-ko (429; `/dav*` 600/60s; bypass `TESTING=true`-rekin).

## CI

- **GitHub** (push/PR `main,develop`-ra): `backend-lint` + `frontend-lint` + `backend-test` (MariaDB 11 + `alembic upgrade head` + pytest) + `frontend-test` (build_runner + `flutter test`) → `docker-build` (4 irudi).
- **GitLab**: stage-ak `lint → test → build`; `docker-build` `main`-en soilik registry-ra push-arekin.

Ate lokala (CI-aren berdina): `ruff check .` + `ruff format --check .` + `pytest tests/ -x -q --tb=short` (`backend/`-tik), `flutter analyze` + `flutter test` (`frontend/`-tik).

## Ikusi halaber

- [USO.md](USO.md): hedapenaren eguneroko erabilera
- [ADMINISTRACION.md](ADMINISTRACION.md): operazioak eta berreskurapena
- [SEGURIDAD.md](SEGURIDAD.md): ekoizpeneko kontrolak eta parametroak
- [HERRAMIENTAS.md](HERRAMIENTAS.md): build/test script-ak eta komandoak
