# Infrastruktur — Clakettes

[ES](../es/INFRAESTRUCTURA.md) · [EN](../en/INFRAESTRUCTURA.md) · [FR](../fr/INFRAESTRUCTURA.md) · [DE](INFRAESTRUCTURA.md) · [IT](../it/INFRAESTRUCTURA.md) · [CA](../ca/INFRAESTRUCTURA.md) · [EU](../eu/INFRAESTRUCTURA.md) · [GL](../gl/INFRAESTRUCTURA.md) · [OC](../oc/INFRAESTRUCTURA.md)

Profile, Ports, Umgebung und CI. Täglicher Betrieb in [USO.md](USO.md), Härtungs-Checkliste in [SEGURIDAD.md](SEGURIDAD.md).

## Docker-Profile (`docker-compose.yml`)

| Profil | Befehl | Dienste |
|---|---|---|
| dev (ohne Profil) | `docker compose up` | Backend + Frontend |
| db | `docker compose --profile db up` | + MariaDB 11 |
| prod | `docker compose --profile prod up -d` | backend-prod + frontend-prod + db |
| build | `[build]`-Profile in `frontend/docker/compose` | web, linux-x64, linux-appimage, android |
| windows / ci / dev | gleiches Compose | windows-x64+installer, test+analyze, dev web |

## Ports und Volumes

| Port | Dienst | Variable |
|---|---|---|
| `8000` | Backend und backend-prod | `PORT_BACKEND` |
| `3000` | Frontend dev | `PORT_FRONTEND` |
| `80` | frontend-prod (nginx, statischer Web-Build) | `PORT_FRONTEND_PROD` |
| `3306` | MariaDB (intern) | `PORT_DB` |

Volumes: `./backend:/app` + `backend-data:/app/data`, `./frontend:/app`, `db-data:/var/lib/mysql`. Backups: SQLite = `*.db` kopieren; MariaDB = `mariadb-dump` auf `db-data`.

## Images

- Backend `python:3.12-alpine`, EXPOSE 8000; dev mit `uvicorn --reload`, prod als Non-Root-Benutzer `appuser`.
- Frontend-Build `ubuntu:24.04 + Flutter 3.47.3` (ARG `BACKEND_URL`); dev `flutter run -d web-server` auf 3000; prod `nginx:alpine` auf 80 mit `try_files $uri $uri/ /index.html` (SPA).

## Umgebung (`backend/.env`, siehe `.env.example`)

| Variable | Wirkung |
|---|---|
| `APP_ENV` | `development` erstellt Admin `admin/setup` + `create_all`; `production` erfordert Alembic und blockiert Standard-`SECRET_KEY` und CORS `*` |
| `SECRET_KEY` | Signiert JWT (`HS256`); Access läuft nach 30 min ab, Refresh nach 30 d |
| `DATABASE_URL` | `sqlite:///./clakettes.db` (dev) oder `mariadb+pymysql://…` (prod) |
| `CORS_ORIGINS` | Leer = `*` ohne Credentials (nur dev); prod erfordert explizite Origins |
| `PUBLIC_BASE_URL`, `FORWARDED_ALLOW_IPS` | Öffentliche URL des Knotens (Manifest und Bundles) und vertrauenswürdige Proxies (Frontend-TLS in Prod zwingend: DAV-Tokens reisen in der URL) |
| `MTLS_REQUIRED`, `MTLS_CA_BUNDLE_PATH`, `MTLS_CLIENT_CERT_PATH`, `MTLS_CLIENT_KEY_PATH` | Föderiertes mTLS (CN und PEM des Zertifikats), Root-CA zur Validierung der Peers und PEM/Schlüssel, der das RSA-SHA256-Manifest signiert |
| `TESTING` | `1/true/yes/on` (case-insensitive, `app.config.is_testing()`): deaktiviert alle Rate-Limits (global 100/60 s, `/dav` 600/60 s, Login 5/300 s, Refresh 20/60 s, Reset 3/300 s, Federation 60/60 s) und die Auto-Migration |
| `SKIP_AUTO_MIGRATE` | `1/true/yes/on`: überspringt `alembic upgrade head` im Lifespan (extern verwaltete DB) |
| `RATE_LIMITS_DB_PATH` | Pfad der SQLite-DB des Rate-Limiters (standardmäßig `backend/rate_limits.db`) |
| `JWT_ISSUER`, `JWT_AUDIENCE`, `ACCESS_TOKEN_EXPIRE_MINUTES` | Validierte Claims und TTL des Access-Tokens (`clakettes`, `clakettes-api`, 30 min) |
| `PAYMENTS_PROVIDER`, `MOCK_WEBHOOK_SECRET`, `MOCK_PAYMENTS_FORCE_FAIL` | Anbieter (`mock` als Standard) und Secret des simulierten Webhooks |
| `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `REDSYS_MERCHANT_CODE`, `REDSYS_TERMINAL`, `REDSYS_SECRET_KEY`, `REDSYS_SANDBOX`, `REDSYS_CURRENCY` | Stripe/Redsys-Zugangsdaten (Sandbox als Standard, Währung `978`) |
| `BACKEND_URL` | `--dart-define` für die Flutter-App (auch im Backend-Bildschirm änderbar; in SharedPreferences persistiert) |

## Gesundheit und Observables

- `GET /health` → `{"status":"healthy","db_revision":…}`; `GET /` → Version (`0.3.0`, Konstante `APP_VERSION`). Der `ConnectivityMonitor` in der App nutzt sie als echte Sonde: `NodeHealth` pro Knoten (`testNode()`, Latenz, `offlineNodeCount`, `isDegraded`) degradiert den Hive-Cache elegant und zeigt `DegradedNodesBanner` mit Zähler und Wiederholungsschaltfläche.
- Föderation: `GET /api/federation/resilience/health` und `/metrics` (p50/p95, Latenz, Fehler und Wiederholungen); `GET /api/federation/events/stream` hält das SSE mit einem Herzschlag alle 15 s aufrecht; `python tools/federation_conformance.py <url> [--json]` prüft Drittknoten.
- Logs: uvicorn-stdout (DAV-Tokens redigiert); API-Fehler in SnackBar + `debugPrint`.
- Limits: Body ≤10 MB (413), Avatar/Bild ≤5 MB (`jpeg/png/webp/gif` mit Magic-Bytes), Video ≤100 MB (`mp4/webm/quicktime`), Docs ≤10 MB (pdf); Rate-Limit 100 req/60s pro IP (429; `/dav*` 600/60s; Umgehung mit `TESTING` ∈ {1,true,yes,on}).

## CI

- **GitHub** (Push/PR auf `main,develop`): `backend-lint` + `frontend-lint` + `backend-test` (SQLite, `TESTING=true`, pytest mit `-m "not interop"`) + `backend-migration` (MariaDB 11 + `alembic upgrade head`) + `frontend-test` (build_runner + `flutter test`) → `docker-build` (4 Images).
- **GitLab**: Stages `lint → test → build`; `docker-build` nur auf `main` mit Push in die Registry.

### Aktualisierung von Abhängigkeiten

- `.github/dependabot.yml`: pip in `/backend` und pub in `/frontend`, wöchentlich (montags), Gruppen `backend-deps`/`frontend-deps`, bis zu 10 offene PRs, Labels `backend`/`frontend` + `dependencies`, Assignee `ephi0s` und Präfixe `build(backend):`/`build(frontend):`. Aktualisierungen vom Typ `version-update:semver-major` werden ignoriert.
- `.github/workflows/dependabot-automerge.yml`: `pull_request_target`, nur für `dependabot[bot]`; nutzt `dependabot/fetch-metadata@v2` und aktiviert `gh pr merge --auto --squash` nur bei Patch/Minor. Majors bleiben zur manuellen Prüfung und der tatsächliche Merge erfordert grünes CI.
- `.github/workflows/dependabot-rebase.yml`: montags 04:17 UTC (`17 4 * * 1`) und `workflow_dispatch`; aktualisiert die Branches offener Dependabot-PRs via `PUT /repos/{repo}/pulls/{n}/update-branch`.

## Siehe auch

- [USO.md](USO.md): tägliche Nutzung des Deployments
- [ADMINISTRACION.md](ADMINISTRACION.md): Operationen und Wiederherstellung
- [SEGURIDAD.md](SEGURIDAD.md): Kontrollen und Produktionsparameter
- [HERRAMIENTAS.md](HERRAMIENTAS.md): Skripte und Build/Test-Befehle
