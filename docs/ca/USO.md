# Ús — Clakettes

[ES](../es/USO.md) · [EN](../en/USO.md) · [FR](../fr/USO.md) · [DE](../de/USO.md) · [IT](../it/USO.md) · [CA](USO.md) · [EU](../eu/USO.md) · [GL](../gl/USO.md) · [OC](../oc/USO.md)

## Arrancada rápida

| Vull | Comanda |
|------|---------|
| Tot en local | `.\start.ps1` o `./start.sh` (Docker si n'hi ha, local si no) |
| Només backend / frontend | `-NoFrontend` / `-NoBackend` |
| Provar al navegador | `-Web` (mode local) |
| Producció local | `-Final` (build web + serve) |
| Proves | `-TestBackend` / `-TestFrontend` |
| Migracions / amb MariaDB | `-Migrate` / `-MariaDB` / `-TestMigration` |
| Aturar tot | `-Kill` |
| Instal·lar dependències que falten | `-InstallMissing` (Windows: winget + git clone; Linux/macOS: gestor del SO + git clone) |
| Revisar l'entorn sense arrancar | `-Check` (doctor: Docker, Python, Flutter, .venv, ports; surt 1 si falta algo) |
| Builds distribuïbles | `-BuildAll` (`tools/build-all.ps1` → `builds/`) |

Sense Docker, el llançador crea un entorn bare-metal local: detecta Python 3.12+ i Flutter, mostra com instal·lar-los segons el SO i ofereix instal·lar-los amb `-InstallMissing` (pregunta abans malgrat que vagi amb el flag).

URLs dev: backend `http://localhost:8000` (Swagger a `/docs`), frontend `http://localhost:3000`.
Si el port està ocupat, es reassigna sol (veure `[PUERTO]` a la sortida).
Admin inicial (només no-producció): `admin` / `setup` — canviar-hi al entrar.

## Configuració

| Variable / flag | On | Efecte |
|-----------------|----|--------|
| `BACKEND_URL` | `--dart-define` o pantalla de backend a l'app | URL de l'API (persisteix a SharedPreferences) |
| `DATABASE_URL` | `backend/.env` | `sqlite:///./clakettes.db` (dev; a Docker `./data/clakettes.db`) o `mariadb+pymysql://…?ssl_ca=…` (prod, TLS obligatori) |
| `SECRET_KEY` | env (obligatori a `APP_ENV=production`) | Firma JWT; default insegur bloqueja l'arrancada a prod |
| `CORS_ORIGINS` | env | Orígens explícits a prod (`*` prohibit amb credencials) |
| `APP_ENV` | env | `development` crea admin + `create_all`; `production` exige Alembic |

## Operació

- **Migrar**: `alembic upgrade head` des de `backend/` (Docker: `-Migrate`).
- **Migració automàtica**: l'app migra la DB sol al arrancar i sella les DB noves amb la revisió actual; `SKIP_AUTO_MIGRATE=1` per omitre'l (DB gestionades externament).
- **SQLite → MariaDB**: `export_sqlite_to_mariadb.py`; tornada amb `import_mariadb_to_sqlite.py` (detall a [DATABASE.md](DATABASE.md)).
- **Còpies de seguretat**: SQLite = copiar `*.db`; MariaDB = `mariadb-dump` (volum `db-data` a Docker).
- **Logs**: stdout d'uvicorn (tokens DAV ja redactats); errors de l'API a SnackBar + `debugPrint`.
- **Límits**: cosos ≤10 MB (413 si més gran); rate limit amb 429 + reintenta.

## Funcions d'usuari

`admin` (tots) → `organizer` (el seu festival: esdeveniments, formularis, comitats) → `attendee`/`juror`/etc. (assignats per organizers; l'auto-join només dona `attendee`). Canals: `admin`/`moderator`/`member`; comitats amb recompte de membres a la llista.

## Funcions en desenvolupament actiu

🚧 Les següents funcions estan en desenvolupament actiu i poden canviar:

- **Perfils socials**: murs de publicacions (microblogging amb Markdown i incrustats de vídeo i podcast) en perfils d'usuari i festival, amb fils de respostes opcionals per publicació i moderació per funcions (administradors, gestió del festival, moderadors). Sense reaccions, stickers ni GIF per ara.
- **Personalització de perfils**: portada, tagline i enllaços socials en usuaris i festivals.
- **Insígnies**: desactivades per defecte; només l'equip administratiu pot activar-les (`PUT /api/badges/settings`). Les insígnies de plataforma les otorgan els administradors; les insígnies de mèrit de festival (veterà, popular, rol, premi especial), la seva gestió. Cada insígnia porta una imatge (SVG preferit).
- **Vot del jurat**: puntuació per obra, agregació i anonimiat opcional (fase 5 del roadmap).

## Vegeu també

- [README.md](../../README.ca.md): descripció general del projecte i accés ràpid
- [HERRAMIENTAS.md](HERRAMIENTAS.md): scripts i comandes d'execució
- [ADMINISTRACION.md](ADMINISTRACION.md): administració del desplegament i rotació de secrets
- [SEGURIDAD.md](SEGURIDAD.md): llista de comprovació i bones pràctiques de producció