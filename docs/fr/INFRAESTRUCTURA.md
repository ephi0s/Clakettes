# Infrastructure — Clakettes

[ES](../es/INFRAESTRUCTURA.md) · [EN](../en/INFRAESTRUCTURA.md) · [FR](INFRAESTRUCTURA.md) · [DE](../de/INFRAESTRUCTURA.md) · [IT](../it/INFRAESTRUCTURA.md) · [CA](../ca/INFRAESTRUCTURA.md) · [EU](../eu/INFRAESTRUCTURA.md) · [GL](../gl/INFRAESTRUCTURA.md) · [OC](../oc/INFRAESTRUCTURA.md)

Profils, ports, environnement et CI. Opération quotidienne dans [USO.md](USO.md), checklist d'endurcissement dans [SEGURIDAD.md](SEGURIDAD.md).

## Profils Docker (`docker-compose.yml`)

| Profil | Commande | Services |
|---|---|---|
| dev (sans profil) | `docker compose up` | backend + frontend |
| db | `docker compose --profile db up` | + MariaDB 11 |
| prod | `docker compose --profile prod up -d` | backend-prod + frontend-prod + db |
| build | profils `[build]` dans `frontend/docker/compose` | web, linux-x64, linux-appimage, android |
| windows / ci / dev | même compose | windows-x64+installer, test+analyze, dev web |

## Ports et volumes

| Port | Service | Variable |
|---|---|---|
| `8000` | backend et backend-prod | `PORT_BACKEND` |
| `3000` | frontend dev | `PORT_FRONTEND` |
| `80` | frontend-prod (nginx, build web statique) | `PORT_FRONTEND_PROD` |
| `3306` | MariaDB (interne) | `PORT_DB` |

Volumes : `./backend:/app` + `backend-data:/app/data`, `./frontend:/app`, `db-data:/var/lib/mysql`. Sauvegardes : SQLite = copier `*.db` ; MariaDB = `mariadb-dump` sur `db-data`.

## Images

- Backend `python:3.12-alpine`, EXPOSE 8000 ; dev avec `uvicorn --reload`, prod comme utilisateur non-root `appuser`.
- Frontend build `ubuntu:24.04 + Flutter 3.47.3` (ARG `BACKEND_URL`) ; dev `flutter run -d web-server` sur 3000 ; prod `nginx:alpine` sur 80 avec `try_files $uri $uri/ /index.html` (SPA).

## Environnement (`backend/.env`, voir `.env.example`)

| Variable | Effet |
|---|---|
| `APP_ENV` | `development` crée admin `admin/setup` + `create_all` ; `production` exige Alembic et bloque `SECRET_KEY` par défaut et CORS `*` |
| `SECRET_KEY` | Signe JWT (`HS256`) ; access expire 30 min, refresh 30 j |
| `DATABASE_URL` | `sqlite:///./clakettes.db` (dev) ou `mariadb+pymysql://…` (prod) |
| `CORS_ORIGINS` | Vide = `*` sans credentials (dev uniquement) ; prod exige origines explicites |
| `PUBLIC_BASE_URL`, `FORWARDED_ALLOW_IPS` | URL publique et proxies de confiance (TLS frontal obligatoire en prod : les tokens DAV voyagent dans l'URL) |
| `BACKEND_URL` | `--dart-define` pour l'app Flutter (modifiable aussi sur l'écran backend ; persiste dans SharedPreferences) |

## Santé et observables

- `GET /health` → `{"status":"healthy"}` ; `GET /` → version (`0.3.0`). `ConnectivityMonitor` dans l'app les utilise comme sonde réelle.
- Logs : stdout uvicorn (tokens DAV redactés) ; erreurs API dans SnackBar + `debugPrint`.
- Limites : corps ≤10 Mo (413), avatar/image ≤5 Mo (`jpeg/png/webp/gif` avec magic-bytes), vidéo ≤100 Mo (`mp4/webm/quicktime`), docs ≤10 Mo (pdf) ; rate limit 100 req/60s par IP (429 ; `/dav*` 600/60s ; contournement avec `TESTING=true`).

## CI

- **GitHub** (push/PR sur `main,develop`) : `backend-lint` + `frontend-lint` + `backend-test` (MariaDB 11 + `alembic upgrade head` + pytest) + `frontend-test` (build_runner + `flutter test`) → `docker-build` (4 images).
- **GitLab** : stages `lint → test → build` ; `docker-build` seulement sur `main` avec push au registry.

Porte locale (même que CI) : `ruff check .` + `ruff format --check .` + `pytest tests/ -x -q --tb=short` (depuis `backend/`), `flutter analyze` + `flutter test` (depuis `frontend/`).

## Voir aussi

- [USO.md](USO.md) : utilisation quotidienne du déploiement
- [ADMINISTRACION.md](ADMINISTRACION.md) : opérations et récupération
- [SEGURIDAD.md](SEGURIDAD.md) : contrôles et paramètres de production
- [HERRAMIENTAS.md](HERRAMIENTAS.md) : scripts et commandes de build/test