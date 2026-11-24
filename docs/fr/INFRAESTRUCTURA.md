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
- Frontend build `ubuntu:24.04 + Flutter 3.50.1` (ARG `BACKEND_URL`) ; dev `flutter run -d web-server` sur 3000 ; prod `nginx:alpine` sur 80 avec `try_files $uri $uri/ /index.html` (SPA).

## Environnement (`backend/.env`, voir `.env.example`)

| Variable | Effet |
|---|---|
| `APP_ENV` | `development` crée l'admin `admin/setup` + `create_all` ; `production` exige Alembic et bloque le `SECRET_KEY` par défaut et CORS `*` |
| `SECRET_KEY` | Signature JWT (`HS256`) ; access expire 30 min, refresh 30 d |
| `DATABASE_URL` | `sqlite:///./clakettes.db` (dev) ou `mariadb+pymysql://…` (prod) |
| `CORS_ORIGINS` | Vide = `*` sans identifiants (dev seulement) ; prod exige des origines explicites |
| `PUBLIC_BASE_URL`, `FORWARDED_ALLOW_IPS` | URL publique du nœud (manifeste et bundles) et proxys de confiance (TLS frontal obligatoire en prod : les tokens DAV voyagent dans l'URL) |
| `MTLS_REQUIRED`, `MTLS_CA_BUNDLE_PATH`, `MTLS_CLIENT_CERT_PATH`, `MTLS_CLIENT_KEY_PATH` | mTLS fédéré (CN et PEM du certificat), CA racine pour valider les pairs et PEM/clé qui signent le manifeste RSA-SHA256 |
| `TESTING` | `1/true/yes/on` (insensible à la casse, `app.config.is_testing()`) : désactive tous les rate limits (global 100/60 s, `/dav` 600/60 s, login 5/300 s, refresh 20/60 s, reset 3/300 s, federation 60/60 s) et l'auto-migration |
| `SKIP_AUTO_MIGRATE` | `1/true/yes/on` : omet `alembic upgrade head` dans le lifespan (DB gérée extérieurement) |
| `RATE_LIMITS_DB_PATH` | Chemin de la BD SQLite du rate limiter (par défaut `backend/rate_limits.db`) |
| `JWT_ISSUER`, `JWT_AUDIENCE`, `ACCESS_TOKEN_EXPIRE_MINUTES` | Claims validés et durée de vie du token d'accès (`clakettes`, `clakettes-api`, 30 min) |
| `PAYMENTS_PROVIDER`, `MOCK_WEBHOOK_SECRET`, `MOCK_PAYMENTS_FORCE_FAIL` | Fournisseur (`mock` par défaut) et secret du webhook simulé |
| `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `REDSYS_MERCHANT_CODE`, `REDSYS_TERMINAL`, `REDSYS_SECRET_KEY`, `REDSYS_SANDBOX`, `REDSYS_CURRENCY` | Identifiants Stripe/Redsys (sandbox par défaut, devise `978`) |
| `BACKEND_URL` | `--dart-define` pour l'app Flutter (aussi modifiable sur l'écran backend ; persisté dans SharedPreferences) |

## Santé et observables

- `GET /health` → `{"status":"healthy","db_revision":…}` ; `GET /` → la version renvoyée par `APP_VERSION`. Le `ConnectivityMonitor` de l'app les utilise comme sonde réelle : `NodeHealth` par nœud (`testNode()`, latence, `offlineNodeCount`, `isDegraded`) dégrade le cache Hive avec élégance et affiche `DegradedNodesBanner` avec le décompte et un bouton de relance.
- Fédération : `GET /api/federation/resilience/health` et `/metrics` (p50/p95, latence, échecs et relances) ; `GET /api/federation/events/stream` maintient le SSE avec un battement toutes les 15 s ; `python tools/federation_conformance.py <url> [--json]` vérifie les nœuds tiers.
- Logs : stdout d'uvicorn (tokens DAV expurgés) ; erreurs d'API dans SnackBar + `debugPrint`.
- Limites : corps ≤10 MB (413), avatar/image ≤5 MB (`jpeg/png/webp/gif` avec magic-bytes), vidéo ≤100 MB (`mp4/webm/quicktime`), docs ≤10 MB (pdf) ; rate limit 100 req/60s par IP (429 ; `/dav*` 600/60s ; contournement avec `TESTING` ∈ {1,true,yes,on}).

## CI

- **GitHub** (push/PR vers `main,develop`) : `backend-lint` + `frontend-lint` + `docs-api` (vérifie que `API.md` est régénérée) + `backend-test` (SQLite, `TESTING=true`, pytest avec `-m "not interop"`) + `backend-migration` (MariaDB 11 + `alembic upgrade head`) + `frontend-test` (build_runner + `flutter test`) → `docker-build` (les images de backend et frontend, dev et prod).
- **GitLab** : stages `lint → test → build` ; les jobs de lint incluent `docs-api` (vérifie que `API.md` est régénérée) ; `docker-build` seulement sur `main` avec push vers le registry.

### Mise à jour des dépendances

- `.github/dependabot.yml` : pip dans `/backend` et pub dans `/frontend`, hebdomadaires (lundi), groupes `backend-deps`/`frontend-deps`, jusqu'à 10 PR ouvertes, étiquettes `backend`/`frontend` + `dependencies`, assignee `ephi0s` et préfixes `build(backend):`/`build(frontend):`. Les mises à jour `version-update:semver-major` sont ignorées.
- `.github/workflows/dependabot-automerge.yml` : `pull_request_target`, uniquement pour `dependabot[bot]` ; utilise `dependabot/fetch-metadata@v2` et active `gh pr merge --auto --squash` seulement sur patch/minor. Les majeures restent à revue manuelle et le merge effectif exige une CI verte.
- `.github/workflows/dependabot-rebase.yml` : lundi 04:17 UTC (`17 4 * * 1`) et `workflow_dispatch` ; rebase les branches des PR Dependabot ouvertes via `PUT /repos/{repo}/pulls/{n}/update-branch`.

## Voir aussi

- [USO.md](USO.md) : utilisation quotidienne du déploiement
- [ADMINISTRACION.md](ADMINISTRACION.md) : opérations et récupération
- [SEGURIDAD.md](SEGURIDAD.md) : contrôles et paramètres de production
- [HERRAMIENTAS.md](HERRAMIENTAS.md) : scripts et commandes de build/test
