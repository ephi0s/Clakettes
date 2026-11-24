# Utilizacion — Clakettes

[ES](../es/USO.md) · [EN](../en/USO.md) · [FR](../fr/USO.md) · [DE](../de/USO.md) · [IT](../it/USO.md) · [CA](../ca/USO.md) · [EU](../eu/USO.md) · [GL](../gl/USO.md) · [OC](USO.md)

## Arranjada rapida

| Vòli | Comanda |
|---|---|
| Tot en local | `.\start.ps1` o `./start.sh` (Docker se i a, local autrament) |
| Solament backend / frontend | `-NoFrontend` / `-NoBackend` |
| Ensajar dins un navegador de desvolopament | per defaut / `-Dev` (o `-Web` per forçar lo mode local) |
| Produccion locala | `-Final` (build web + serve) |
| Tèsts | `-TestBackend` / `-TestFrontend` |
| Migracions / amb MariaDB | `-Migrate` / `-MariaDB` / `-TestMigration` |
| Arrestar tot | `-Kill` |
| Installar las dependéncias que mancan | `-InstallMissing` (Windows: winget + git clone; Linux/macOS: gestor del SO + git clone) |
| Revisar l'environament sens arrancar | `-Check` (doctor: Docker, Python, Flutter, .venv, pòrts; sòrt 1 se quicòm manca) |
| Builds distribuibles | `-BuildAll` (`tools/build-all.ps1` → `builds/`) |

Sens Docker, lo lançaire crea un environament bare-metal local: detecta Python 3.12+ e Flutter, mostra còm los installar segon vòstre SO e ofrís de los installar amb `-InstallMissing` (demanda abans levat se anatz amb lo flag).

URLs dev: backend `http://localhost:8000` (Swagger a `/docs`), frontend `http://localhost:3000`.
Se lo pòrt es ocupat se torna atribuir sol (gardatz `[PUERTO]` dins la sortida).
Admin inicial (solament non-prod): `admin` / `setup` — cambiar en intrant.

## Configuracion

| Variabla / flag | Ont | Efecte |
|---|---|---|
| `BACKEND_URL` | `--dart-define` o ecran de backend dins l'app | URL de l'API (persistís dins SharedPreferences) |
| `DATABASE_URL` | `backend/.env` | `sqlite:///./clakettes.db` (dev; dins Docker `./data/clakettes.db`) o `mariadb+pymysql://…?ssl_ca=…` (prod, TLS obligatòri) |
| `SECRET_KEY` | env (obligatòria amb `APP_ENV=production`) | Signatura JWT; defaut pauc segur bloca l'arranjada en prod |
| `CORS_ORIGINS` | env | Origines explicitas en prod (`*` interdit amb credencials) |
| `APP_ENV` | env | `development` crea admin + `create_all`; `production` exegís Alembic |
| `PUBLIC_BASE_URL` | `backend/.env` | Domeni public del nose; apareis dins lo manifest e los bundles de portabilitat |
| `MTLS_REQUIRED` | env | Obliga a un peer mTLS verificat en federacion (CN e PEM del certificat) |
| `MTLS_CA_BUNDLE_PATH` | env | CA raíç per validar los certificats dels clients federats |
| `MTLS_CLIENT_CERT_PATH`, `MTLS_CLIENT_KEY_PATH` | env | PEM del certificat e clau privada que signan lo manifest (RSA-SHA256) |
| `TESTING`, `SKIP_AUTO_MIGRATE` | env | `1/true/yes/on`: `TESTING` desactiva los rate limits e l'auto-migracion; `SKIP_AUTO_MIGRATE` omet solament l'auto-migracion |
| `RATE_LIMITS_DB_PATH` | env | Rota de la BD SQLite de limits (per defaut `backend/rate_limits.db`) |
| `JWT_ISSUER`, `JWT_AUDIENCE`, `ACCESS_TOKEN_EXPIRE_MINUTES` | env | Claims e TTL del JWT d'accès |
| `PAYMENTS_PROVIDER`, `MOCK_WEBHOOK_SECRET`, `MOCK_PAYMENTS_FORCE_FAIL` | env | Passarelha (`mock` per defaut) e secrets del webhook simulat |
| `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `REDSYS_*` | env | Credencialas de pagament realas; detalh en [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) |

**Nota de pagaments**: `PAYMENTS_PROVIDER=mock` es lo valor per defaut (`backend/app/config.py`). Stripe e Redsys NO son operatius fins que los webhooks sián cablats (`POST /api/payments/webhook/{stripe,redsys}`); uei solament lo simulat fonciona. Lo `confirm` de Redsys torna sempre `"pending"`.
| `TESTING`, `SKIP_AUTO_MIGRATE` | env | `1/true/yes/on`: `TESTING` desactiva los rate limits e l'auto-migracion; `SKIP_AUTO_MIGRATE` omet solament l'auto-migracion |

## Operacion

- **Migrar**: `alembic upgrade head` dempuèi `backend/` (Docker: `-Migrate`).
- **Migracion automatica**: l'app migra sola la DB en arrancant e sella las DB novas amb la revision actuala; `SKIP_AUTO_MIGRATE=1` per ometre (DB gestionadas exteriorament).
- **SQLite → MariaDB**: `export_sqlite_to_mariadb.py`; retorn amb `import_mariadb_to_sqlite.py` (detalh dins [DATABASE.md](DATABASE.md)).
- **Còpias de seguretat**: SQLite = copiar `*.db`; MariaDB = `mariadb-dump` (volum `db-data` dins Docker).
- **Jornals**: stdout d'uvicorn (tokens DAV ja escafats); errors d'API dins SnackBar + `debugPrint`.
- **Limites**: còrs ≤10 MB (413 se pus grand); rate limit amb 429 + reensaji (global 100/60 s per IP, `/dav` 600/60 s, login 5/300 s, refresh 20/60 s, reset 3/300 s, federacion 60/60 s; chat 10/60 s per nose e usagi). `TESTING` ∈ {1,true,yes,on} desactiva totes los limits.
- **Sens connexion**: la cach Hive garda la provenança de cada nose; `reconcile` fusiona a la reconnexion e `clearOrigin` rebuta un nose. Se de noses non responon mas lo principal si, apareis `DegradedNodesBanner` amb lo recompte e un boton per recargar.
- **Mèdia**: las rotas `/uploads/...` que torna l'API se fan precedir del servidor actiu dins lo client (`resolveMediaUrl()`); las URLs `http(s)` s'utilizan tal qual.
- **Federacion**: verificatz un nose tèrç amb `python tools/federation_conformance.py <url> [--json]`; la santat del peering es a `/api/federation/resilience/health` e las metricas p50/p95 a `/metrics`.
- **Portabilitat**: exportatz/importatz de bundles dempuèi `/api/federation/portability/{bundles,imports}` e consultatz las redireccions d'identitat a `/redirects/{ref}`.

## Ròtles d'usagi

`admin` (tot) → `organizer` (son festival: eveniments, formularis, comitats) → `attendee`/`juror`/etc. (atribuits pels organizers; l'auto-join dona solament `attendee`). Canales: `admin`/`moderator`/`member`; comitats amb comptatge dels membres dins la lista.

## Fonctions en desvolopament actiu

🚧 Las fonctions seguentas son en desvolopament actiu e pòdon cambiar:

- **Perfils socials**: murs de publicacions (microblogging amb Markdown e d'integracions de vidèo e de podcast) suls perfils d'usagi e de festival, amb de fils de responsa opcionalas per publicacion e moderacion per ròtles (administrators, gestion del festival, moderators). Sens reaccions, autocolants ni GIF per ara.
- **Personalizacion dels perfils**: couvertura, tagline e ligams socials suls usagis e festivals.
- **Insignias**: desactivadas per defaut; solament l'equipa administrativa las pòt activar (`PUT /api/badges/settings`). Las insignias de plataforma las donan los administrators; las de meriti de festival (veteran, popular, ròtle, prèmi especial), sa gestion. Cada insignia pòrta una imatge (SVG de preferéncia).
- **Vot del jurat**: ja operatiu (notacion per òbra, agregacion e anonimat opcional); solament admet los corts del festival atribuit.

## Vejatz tanben

- [README.oc.md](../../README.oc.md): descripcion generala del projècte e accès rapid
- [HERRAMIENTAS.md](HERRAMIENTAS.md): scripts e comandas d'execucion
- [ADMINISTRACION.md](ADMINISTRACION.md): administracion del desplegament e rotacion dels secrets
- [SEGURIDAD.md](SEGURIDAD.md): lista de contraròtle e bonas practicas de produccion
