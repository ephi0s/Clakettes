# Infrastructure — Clakettes

[ES](../es/INFRAESTRUCTURA.md) · [EN](../en/INFRAESTRUCTURA.md) · [FR](INFRAESTRUCTURA.md) · [DE](../de/INFRAESTRUCTURA.md) · [IT](../it/INFRAESTRUCTURA.md) · [CA](../ca/INFRAESTRUCTURA.md) · [EU](../eu/INFRAESTRUCTURA.md) · [GL](../gl/INFRAESTRUCTURA.md) · [OC](../oc/INFRAESTRUCTURA.md)

Profils, ports, environnement et CI. Opérationnelle quotidienne dans [USO.md](USO.md), liste de contrôle de durcissement dans [SEGURIDAD.md](SEGURIDAD.md).

## Profils Docker (`docker-compose.yml`)

| Perfil | Comando | Servicios |
|---|---|---|
| dev (sin perfil) | `docker compose up` | backend + frontend |
| db | `docker compose --profile db up` | + MariaDB 11 |
| prod | `docker compose --profile prod up -d` | backend-prod + frontend-prod + db |
| build | perfiles `[build]` en `frontend/docker/compose` | web, linux-x64, linux-appimage, android |
| windows / ci / dev | mismo compose | windows-x64+installer, test+analyze, dev web |

## Ports et volumes

| Puerto | Servicio | Variable |
|---|---|---|
| `8000` | backend y backend-prod | `PORT_BACKEND` |
| `3000` | frontend dev | `PORT_FRONTEND` |
| `80` | frontend-prod (nginx, build web estático) | `PORT_FRONTEND_PROD` |
| `3306` | MariaDB (interno) | `PORT_DB` |

Volumes : `./backend:/app` + `backend-data:/app/data`, `./frontend:/app`, `db-data:/var/lib/mysql`. Sauvegardes : SQLite = copier `*.db` ; MariaDB = `mariadb-dump` sur `db-data`.

## Images

- Backend `python:3.12-alpine`, EXPOSE 8000 ; dev avec `uvicorn --reload`, prod comme utilisateur non-root `appuser`.
- Frontend build `ubuntu:24.04 + Flutter 3.47.3` (ARG `BACKEND_URL`) ; dev `flutter run -d web-server` sur 3000 ; prod `nginx:alpine` sur 80 avec `try_files $uri $uri/ /index.html` (SPA).

## Environnement (`backend/.env`, voir `.env.example`)

| Variable | Efecto |
|---|---|
| `APP_ENV` | `development` crea admin `admin/setup` + `create_all`; `production` exige Alembic y bloquea `SECRET_KEY` por defecto y CORS `*` |
| `SECRET_KEY` | Firma JWT (`HS256`); caduca access 30 min, refresh 30 d |
| `DATABASE_URL` | `sqlite:///./clakettes.db` (dev) o `mariadb+pymysql://…` (prod) |
| `CORS_ORIGINS` | Vacío = `*` sin credenciales (solo dev); prod exige orígenes explícitos |
| `PUBLIC_BASE_URL`, `FORWARDED_ALLOW_IPS` | URL pública y proxies de confianza (TLS frontal obligatorio en prod: los tokens DAV viajan en URL) |
| `BACKEND_URL` | `--dart-define` para la app Flutter (también cambiable en la pantalla de backend; persiste en SharedPreferences) |

## Santé et observables

- `GET /health` → `{"status":"healthy"}` ; `GET /` → version (`0.3.0`). `ConnectivityMonitor` dans l'app les utilise comme sonde réelle.
- Logs : stdout d'uvicorn (tokens DAV caviardés) ; erreurs d'API en SnackBar + `debugPrint`.
- Limites : corps ≤10 MB (413), avatar/image ≤5 MB (`jpeg/png/webp/gif` avec magic-bytes), vidéo ≤100 MB (`mp4/webm/quicktime`), docs ≤10 MB (pdf) ; rate limit 100 req/60s par IP (429 ; `/dav*` 600/60s ; bypass avec `TESTING=true`).

## CI

- **GitHub** (push/PR vers `main,develop`) : `backend-lint` + `frontend-lint` + `backend-test` (MariaDB 11 + `alembic upgrade head` + pytest) + `frontend-test` (build_runner + `flutter test`) → `docker-build` (4 images).
- **GitLab** : stages `lint → test → build` ; `docker-build` seulement sur `main` avec push au registry.

Porte locale (même que CI) : `ruff check .` + `ruff format --check .` + `pytest tests/ -x -q --tb=short` (depuis `backend/`), `flutter analyze` + `flutter test` (depuis `frontend/`).

## Voir aussi

- [USO.md](USO.md) : usage quotidien du déploiement
- [ADMINISTRACION.md](ADMINISTRACION.md) : opérations et récupération
- [SEGURIDAD.md](SEGURIDAD.md) : contrôles et paramètres de production
- [HERRAMIENTAS.md](HERRAMIENTAS.md) : scripts et commandes de build/test
