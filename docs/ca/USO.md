# Ús — Clakettes

[ES](../es/USO.md) · [EN](../en/USO.md) · [FR](../fr/USO.md) · [DE](../de/USO.md) · [IT](../it/USO.md) · [CA](USO.md) · [EU](../eu/USO.md) · [GL](../gl/USO.md) · [OC](../oc/USO.md)

## Arrencada ràpida

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

Sense Docker, el llançador crea un entorn bare-metal local: detecta Python 3.12+ i Flutter, mostra com instal·lar-los segons el teu SO i ofereix instal·lar-los amb `-InstallMissing` (pregunta abans llevat que vagis amb el flag).

URLs dev: backend `http://localhost:8000` (Swagger a `/docs`), frontend `http://localhost:3000`.
Si el port és ocupat es reassigna sol (mira `[PUERTO]` a la sortida).
Admin inicial (només no-prod): `admin` / `setup` — canviar en entrar.

## Configuració

| Variable / flag | Dónde | Efecto |
|---|---|---|
| `BACKEND_URL` | `--dart-define` o pantalla de backend en la app | URL del API (persiste en SharedPreferences) |
| `DATABASE_URL` | `backend/.env` | `sqlite:///./clakettes.db` (dev; en Docker `./data/clakettes.db`) o `mariadb+pymysql://…?ssl_ca=…` (prod, TLS obligatorio) |
| `SECRET_KEY` | env (obligatoria en `APP_ENV=production`) | Firma JWT; default inseguro bloquea el arranque en prod |
| `CORS_ORIGINS` | env | Orígenes explícitos en prod (`*` prohibido con credenciales) |
| `APP_ENV` | env | `development` crea admin + `create_all`; `production` exige Alembic |

## Operació

- **Migrar**: `alembic upgrade head` des de `backend/` (Docker: `-Migrate`).
- **SQLite → MariaDB**: `export_sqlite_to_mariadb.py`; tornada amb `import_mariadb_to_sqlite.py` (detall a [DATABASE.md](DATABASE.md)).
- **Backups**: SQLite = copiar `*.db`; MariaDB = `mariadb-dump` (volum `db-data` en Docker).
- **Logs**: uvicorn stdout (tokens DAV ja redactats); errors d'API en SnackBar + `debugPrint`.
- **Límits**: cossos ≤10 MB (413 si major); rate limit amb 429 + reintent.

- **Migració automàtica**: l’app migra sola la DB en arrencar i segella les DB noves amb la revisió actual; `SKIP_AUTO_MIGRATE=1` per ometre-ho.
## Rols d'usuari

`admin` (tot) → `organizer` (el seu festival: esdeveniments, formularis, comitès) → `attendee`/`juror`/etc. (assignats per organizers; l'auto-join només dóna `attendee`). Canals: `admin`/`moderator`/`member`; comitès amb comptatge de membres en llista.

## Funcions en desenvolupament actiu

🚧 Les funcions següents estan en desenvolupament actiu i poden canviar:

- **Perfils socials**: murs de publicacions (microblogging amb Markdown i incrustats de vídeo i pòdcast) en perfils d'usuari i festival, amb fils de respostes opcionals per publicació i moderació per rols (administradors, gestió del festival, moderadors). Sense reaccions, adhesius ni GIF per ara.
- **Personalització de perfils**: portada, tagline i enllaços socials en usuaris i festivals.
- **Insígnies**: desactivades per defecte; només l'equip administratiu pot activar-les (`PUT /api/badges/settings`). Les insígnies de plataforma les atorguen els administradors; les de mèrit de festival (veterà, popular, rol, premi especial), la seva gestió. Cada insígnia porta una imatge (SVG preferit).

## Vegeu també

- [README.ca.md](../../README.ca.md): descripció general del projecte i accés ràpid
- [HERRAMIENTAS.md](HERRAMIENTAS.md): scripts i ordres d'execució
- [ADMINISTRACION.md](ADMINISTRACION.md): administració del desplegament i rotació de secrets
- [SEGURIDAD.md](SEGURIDAD.md): checklist i bones pràctiques de producció
