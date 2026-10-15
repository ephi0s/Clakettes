# Ús — Clakettes

[ES](../es/USO.md) · [EN](../en/USO.md) · [FR](../fr/USO.md) · [DE](../de/USO.md) · [IT](../it/USO.md) · [CA](../ca/USO.md) · [EU](../eu/USO.md) · [GL](../gl/USO.md) · [OC](USO.md)

## Aviada rapida

| Quiero | Comando |
|---|---|
| Todo en local | `.\start.ps1` o `./start.sh` (Docker si hay, local si no) |
| Solo backend / frontend | `-NoFrontend` / `-NoBackend` |
| Probar en navegador | `-Web` (modo local) |
| Producción local | `-Final` (build web + serve) |
| Tests | `-TestBackend` / `-TestFrontend` |
| Migraciones / con MariaDB | `-Migrate` / `-MariaDB` / `-TestMigration` |
| Parar todo | `-Kill` |
| Instalar dependencias que falten | `-InstallMissing` (Windows: winget + git clone; Linux/macOS: gestor del SO + git clone) |
| Revisar el entorno sin arrancar | `-Check` (doctor: Docker, Python, Flutter, .venv, puertos; sale 1 si falta algo) |
| Builds distribuibles | `-BuildAll` (`tools/build-all.ps1` → `builds/`) |

Sens Docker, lo lançaire crea un environa bare-metal locau: detecta Python 3.12+ e Flutter, mòstra cossí los installar segon ton SO e prepausa de los installar amb `-InstallMissing` (demanda abans levat que vajas amb lo flag).

URLs dev: backend `http://localhost:8000` (Swagger en `/docs`), frontend `http://localhost:3000`.
Se lo pòrt es ocupat se reassigna sol (aguacha `[PUERTO]` dins la sortida).
Admin iniciau (sonque non-prod): `admin` / `setup` — cambiar en intrar.

## Configuracion

| Variable / flag | Dónde | Efecto |
|---|---|---|
| `BACKEND_URL` | `--dart-define` o pantalla de backend en la app | URL del API (persiste en SharedPreferences) |
| `DATABASE_URL` | `backend/.env` | `sqlite:///./clakettes.db` (dev; en Docker `./data/clakettes.db`) o `mariadb+pymysql://…?ssl_ca=…` (prod, TLS obligatorio) |
| `SECRET_KEY` | env (obligatoria en `APP_ENV=production`) | Firma JWT; default inseguro bloquea el arranque en prod |
| `CORS_ORIGINS` | env | Orígenes explícitos en prod (`*` prohibido con credenciales) |
| `APP_ENV` | env | `development` crea admin + `create_all`; `production` exige Alembic |

## Operacion

- **Migrar**: `alembic upgrade head` dempuèi `backend/` (Docker: `-Migrate`).
- **SQLite → MariaDB**: `export_sqlite_to_mariadb.py`; tornada amb `import_mariadb_to_sqlite.py` (detalh en [DATABASE.md](DATABASE.md)).
- **Salvagardas**: SQLite = copiar `*.db`; MariaDB = `mariadb-dump` (volum `db-data` en Docker).
- **Jornaus**: uvicorn stdout (tokens DAV ja redactats); errors d'API en SnackBar + `debugPrint`.
- **Limits**: còrses ≤10 MB (413 se màger); rate limit amb 429 + tornada d'ensajar.

- **Migracion automatica** : l’app migra sola la DB a l’aviada e sagèla las DB nòvas amb la revision actuala ; `SKIP_AUTO_MIGRATE=1` per l’ometre.
## Ròtles d'utilizaire

`admin` (tot) → `organizer` (son festivau: eveniments, formularis, comitats) → `attendee`/`juror`/etc. (assignats per organizers; l'auto-join sonque dona `attendee`). Canaus: `admin`/`moderator`/`member`; comitats amb comptatge de membres en lista.

## Foncions en desvolopament actiu

🚧 Las foncions seguentas son en desvolopament actiu e pòdon cambiar:

- **Profils socials** : murs de publicacions (microblogging amb Markdown e incrustats de vidèo e podcast) suls profils d'utilizaire e de festenal, amb fils de responsas opcionals per publicacion e moderacion per ròtles (admins, gestion del festenal, moderators). Pas de reaccions, pegatinas ni GIF per ara.
- **Personalizacion dels profils** : portada, tagline e ligams socials suls utilizaires e festenals.
- **Badges** : desactivats per defaut ; sonque l'equipa admin pòt los activar (`PUT /api/badges/settings`). Los badges de plataforma son autrejats pels admins ; los de merit de festenal (veteran, popular, ròtle, prèmi especial) per sa gestion. Cada badge pòrta una imatge (SVG preferit).

## Veire tanben

- [README.oc.md](../../README.oc.md): descripcion generala del projècte e accès rapid
- [HERRAMIENTAS.md](HERRAMIENTAS.md): scripts e comandas d'execucion
- [ADMINISTRACION.md](ADMINISTRACION.md): administracion del desplegament e rotacion de secrets
- [SEGURIDAD.md](SEGURIDAD.md): checklist e bonas practicas de produccion
