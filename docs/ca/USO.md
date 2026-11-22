# Ús — Clakettes

[ES](../es/USO.md) · [EN](../en/USO.md) · [FR](../fr/USO.md) · [DE](../de/USO.md) · [IT](../it/USO.md) · [CA](USO.md) · [EU](../eu/USO.md) · [GL](../gl/USO.md) · [OC](../oc/USO.md)

## Arrencada ràpida

| Vull | Comando |
|---|---|
| Tot en local | `.\start.ps1` o `./start.sh` (Docker si n'hi ha, local si no) |
| Només backend / frontend | `-NoFrontend` / `-NoBackend` |
| Provar en navegador | `-Web` (mode local) |
| Producció local | `-Final` (build web + serve) |
| Tests | `-TestBackend` / `-TestFrontend` |
| Migracions / amb MariaDB | `-Migrate` / `-MariaDB` / `-TestMigration` |
| Parar-ho tot | `-Kill` |
| Instal·lar dependències que falten | `-InstallMissing` (Windows: winget + git clone; Linux/macOS: gestor del SO + git clone) |
| Revisar l'entorn sense arrancar | `-Check` (doctor: Docker, Python, Flutter, .venv, ports; surt 1 si falta alguna cosa) |
| Builds distribuïbles | `-BuildAll` (`tools/build-all.ps1` → `builds/`) |

Sense Docker, el llançador crea un entorn bare-metal local: detecta Python 3.12+ i Flutter, mostra com instal·lar-los segons el teu SO i ofereix instal·lar-los amb `-InstallMissing` (pregunta abans llevat que hi vagis amb el flag).

URLs dev: backend `http://localhost:8000` (Swagger a `/docs`), frontend `http://localhost:3000`.
Si el port està ocupat es reassigna sol (mira `[PUERTO]` a la sortida).
Admin inicial (només no-prod): `admin` / `setup` — canviar en entrar.

## Configuració

| Variable / flag | On | Efecte |
|---|---|---|
| `BACKEND_URL` | `--dart-define` o pantalla de backend a l'app | URL de l'API (persisteix a SharedPreferences) |
| `DATABASE_URL` | `backend/.env` | `sqlite:///./clakettes.db` (dev; a Docker `./data/clakettes.db`) o `mariadb+pymysql://…?ssl_ca=…` (prod, TLS obligatori) |
| `SECRET_KEY` | env (obligatòria a `APP_ENV=production`) | Signatura JWT; default insegur bloqueja l'arrencada en prod |
| `CORS_ORIGINS` | env | Orígens explícits en prod (`*` prohibit amb credencials) |
| `APP_ENV` | env | `development` crea admin + `create_all`; `production` exigeix Alembic |
| `PUBLIC_BASE_URL` | `backend/.env` | Domini públic del node; apareix al manifest i als bundles de portabilitat |
| `MTLS_REQUIRED` | env | Obliga a peer mTLS verificat en federació (CN i PEM del certificat) |
| `MTLS_CA_BUNDLE_PATH` | env | CA arrel per validar certificats de clients federats |
| `MTLS_CLIENT_CERT_PATH`, `MTLS_CLIENT_KEY_PATH` | env | PEM del certificat i clau privada que signen el manifest (RSA-SHA256) |
| `TESTING`, `SKIP_AUTO_MIGRATE` | env | `1/true/yes/on`: `TESTING` desactiva els rate limits i l'auto-migració; `SKIP_AUTO_MIGRATE` omet només l'auto-migració |
| `RATE_LIMITS_DB_PATH` | env | Ruta de la BD SQLite de límits (per defecte `backend/rate_limits.db`) |
| `JWT_ISSUER`, `JWT_AUDIENCE`, `ACCESS_TOKEN_EXPIRE_MINUTES` | env | Claims i TTL del JWT d'accés |
| `PAYMENTS_PROVIDER`, `MOCK_WEBHOOK_SECRET`, `MOCK_PAYMENTS_FORCE_FAIL` | env | Passarel·la (`mock` per defecte) i secrets del webhook simulat |
| `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `REDSYS_*` | env | Credencials de pagament reals; detall a [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) |

**Nota de pagaments**: `PAYMENTS_PROVIDER=mock` és el valor per defecte (`backend/app/config.py`). Stripe i Redsys NO estan operatius fins que es cablegin els seus webhooks (`POST /api/payments/webhook/{stripe,redsys}`); avui només funciona el simulat. El `confirm` de Redsys retorna sempre `"pending"`.
| `TESTING`, `SKIP_AUTO_MIGRATE` | env | `1/true/yes/on`: `TESTING` desactiva rate limits i auto-migració; `SKIP_AUTO_MIGRATE` omiteix només l'auto-migració |

## Operació

- **Migrar**: `alembic upgrade head` des de `backend/` (Docker: `-Migrate`).
- **Migració automàtica**: l'app migra sola la DB en arrencar i segella les DB noves amb la revisió actual; `SKIP_AUTO_MIGRATE=1` per omitir-ho (DB gestionades externament).
- **SQLite → MariaDB**: `export_sqlite_to_mariadb.py`; tornada amb `import_mariadb_to_sqlite.py` (detall a [DATABASE.md](DATABASE.md)).
- **Còpies de seguretat**: SQLite = copiar `*.db`; MariaDB = `mariadb-dump` (volum `db-data` a Docker).
- **Logs**: stdout d'uvicorn (tokens DAV ja redactats); errors d'API en SnackBar + `debugPrint`.
- **Límits**: cossos ≤10 MB (413 si més gran); rate limit amb 429 + reintent (global 100/60 s per IP, `/dav` 600/60 s, login 5/300 s, refresh 20/60 s, reset 3/300 s, federació 60/60 s; xat 10/60 s per node i usuari). `TESTING` ∈ {1,true,yes,on} desactiva tots els límits.
- **Sense connexió**: la caché Hive guarda la procedència de cada node; `reconcile` fusiona en reconnectar i `clearOrigin` descarta un node. Si alguns nodes no responen però el principal sí, apareix `DegradedNodesBanner` amb el recompte i un botó per recarregar.
- **Mitjans**: les rutes `/uploads/...` que retorna l'API s'anteposen al servidor actiu al client (`resolveMediaUrl()`); les URLs `http(s)` s'usen tal qual.
- **Federació**: comprova un node tercer amb `python tools/federation_conformance.py <url> [--json]`; la salut del peering està a `/api/federation/resilience/health` i les mètriques p50/p95 a `/metrics`.
- **Portabilitat**: exporta/importa bundles des de `/api/federation/portability/{bundles,imports}` i consulta les redireccions d'identitat a `/redirects/{ref}`.

## Rols d'usuari

`admin` (tot) → `organizer` (el seu festival: esdeveniments, formularis, comitès) → `attendee`/`juror`/etc. (assignats pels organizers; l'auto-join només dona `attendee`). Canals: `admin`/`moderator`/`member`; comitès amb comptatge de membres a la llista.

## Funcions en desenvolupament actiu

🚧 Les següents funcions estan en desenvolupament actiu i poden canviar:

- **Perfils socials**: murs de publicacions (microblogging amb Markdown i incrustacions de vídeo i pòdcast) en perfils d'usuari i festival, amb fils de respostes opcionals per publicació i moderació per rols (administradors, gestió del festival, moderadors). Sense reaccions, stickers ni GIF per ara.
- **Personalització de perfils**: portada, tagline i enllaços socials en usuaris i festivals.
- **Insígnies**: desactivades per defecte; només l'equip administratiu pot activar-les (`PUT /api/badges/settings`). Les insígnies de plataforma les atorguen els administradors; les de mèrit de festival (veterà, popular, rol, premi especial), la seva gestió. Cada insígnia porta una imatge (SVG preferit).
- **Votació del jurat**: ja operativa (puntuació per obra, agregació i anonimat opcional); només admet curts del festival assignat.

## Vegeu també

- [README.ca.md](../../README.ca.md): descripció general del projecte i accés ràpid
- [HERRAMIENTAS.md](HERRAMIENTAS.md): scripts i comandos d'execució
- [ADMINISTRACION.md](ADMINISTRACION.md): administració del desplegament i rotació de secrets
- [SEGURIDAD.md](SEGURIDAD.md): llista de comprovació i bones pràctiques de producció
