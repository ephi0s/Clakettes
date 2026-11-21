# Infrastructure — Clakettes

[ES](../es/INFRAESTRUCTURA.md) · [EN](../en/INFRAESTRUCTURA.md) · [FR](INFRAESTRUCTURA.md) · [DE](../de/INFRAESTRUCTURA.md) · [IT](../it/INFRAESTRUCTURA.md) · [CA](../ca/INFRAESTRUCTURA.md) · [EU](../eu/INFRAESTRUCTURA.md) · [GL](../gl/INFRAESTRUCTURA.md) · [OC](../oc/INFRAESTRUCTURA.md)

Profils, ports, environnement et CI. Exploitation quotidienne dans [USO.md](USO.md), checklist de durcissement dans [SEGURIDAD.md](SEGURIDAD.md).

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

- Backend `python:3.12-alpine`, EXPOSE 8000 ; dev avec `uvicorn --reload`, prod en utilisateur non-root `appuser`.
- Frontend build `ubuntu:24.04 + Flutter 3.47.3` (ARG `BACKEND_URL`) ; dev `flutter run -d web-server` sur 3000 ; prod `nginx:alpine` sur 80 avec `try_files $uri $uri/ /index.html` (SPA).

## Environnement (`backend/.env`, voir `.env.example`)

| Variable | Effet |
|---|---|
| `APP_ENV` | `development` crée l'admin `admin/setup` + `create_all` ; `production` exige Alembic et bloque le `SECRET_KEY` par défaut et CORS `*` |
| `SECRET_KEY` | Signature JWT (`HS256`) ; access expire 30 min, refresh 30 d |
| `DATABASE_URL` | `sqlite:///./clakettes.db` (dev) ou `mariadb+pymysql://…` (prod) |
| `CORS_ORIGINS` | Vide = `*` sans identifiants (dev seulement) ; prod exige des origines explicites |
| `PUBLIC_BASE_URL`, `FORWARDED_ALLOW_IPS` | URL publique du nœud (manifeste et bundles) et proxys de confiance (TLS frontal obligatoire en prod : les tokens DAV voyagent dans l'URL) |
| `MTLS_REQUIRED`, `MTLS_CLIENT_CERT_PATH`, `MTLS_CLIENT_KEY_PATH` | mTLS fédéré (CN et PEM du certificat) et PEM/clé qui signent le manifeste RSA-SHA256 |
| `BACKEND_URL` | `--dart-define` pour l'app Flutter (aussi modifiable sur l'écran backend ; persisté dans SharedPreferences) |

## Santé et observables

- `GET /health` → `{"status":"healthy"}` ; `GET /` → version (`0.3.0`). Le `ConnectivityMonitor` de l'app les utilise comme sonde réelle, avec des health checks par nœud pour dégrader le cache Hive avec élégance.
- Fédération : `GET /api/federation/resilience/health` et `/metrics` (p50/p95, latence, échecs et relances) ; `GET /api/federation/events/stream` maintient le SSE avec un battement toutes les 15 s ; `python tools/federation_conformance.py <url> [--json]` vérifie les nœuds tiers.
- Logs : stdout d'uvicorn (tokens DAV expurgés) ; erreurs d'API dans SnackBar + `debugPrint`.
- Limites : corps ≤10 MB (413), avatar/image ≤5 MB (`jpeg/png/webp/gif` avec magic-bytes), vidéo ≤100 MB (`mp4/webm/quicktime`), docs ≤10 MB (pdf) ; rate limit 100 req/60s par IP (429 ; `/dav*` 600/60s ; contournement avec `TESTING=true`).

## CI

- **GitHub** (push/PR vers `main,develop`) : `backend-lint` + `frontend-lint` + `backend-test` (MariaDB 11 + `alembic upgrade head` + pytest) + `frontend-test` (build_runner + `flutter test`) → `docker-build` (4 images).
- **GitLab** : stages `lint → test → build` ; `docker-build` seulement sur `main` avec push vers le registry.

## Voir aussi

- [USO.md](USO.md) : utilisation quotidienne du déploiement
- [ADMINISTRACION.md](ADMINISTRACION.md) : opérations et récupération
- [SEGURIDAD.md](SEGURIDAD.md) : contrôles et paramètres de production
- [HERRAMIENTAS.md](HERRAMIENTAS.md) : scripts et commandes de build/test
