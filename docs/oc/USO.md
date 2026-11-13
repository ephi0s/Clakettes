# Uso — Clakettes

[ES](../es/USO.md) · [EN](../en/USO.md) · [FR](../fr/USO.md) · [DE](../de/USO.md) · [IT](../it/USO.md) · [CA](../ca/USO.md) · [EU](../eu/USO.md) · [GL](../gl/USO.md) · [OC](USO.md)

## Arrancada rapida

| Volgo | Comanda |
|-------|---------|
| Tot en local | `.\start.ps1` o `./start.sh` (Docker si aich, local se non) |
| Solo backend / frontend | `-NoFrontend` / `-NoBackend` |
| Probar en navegador | `-Web` (modo local) |
| Productiu local | `-Final` (build web + serve) |
| Tests | `-TestBackend` / `-TestFrontend` |
| Migracions / amb MariaDB | `-Migrate` / `-MariaDB` / `-TestMigration` |
| Parar tot | `-Kill` |
| Installar dependencias que faltan | `-InstallMissing` (Windows: winget + git clone; Linux/macOS: gestionari de SO + git clone) |
| Revisar l'entorn sens arrancar | `-Check` (doctor: Docker, Python, Flutter, .venv, ports; sale 1 si manca algo) |
| Builds distribuibles | `-BuildAll` (`tools/build-all.ps1` → `builds/`) |

Sens Docker, lo lanzador crea un entorno bare-metal local: detecta Python 3.12+ e Flutter, mostra coma instalalos segont lo vòstre SO e offre instalalos amb `-InstallMissing` (preguissa abans se non anatz amb lo flag).

URLs dev: backend `http://localhost:8000` (Swagger en `/docs`), frontend `http://localhost:3000`.
Se lo port es ocupat se reassigna sens (mira `[PUERTO]` en la sortida).
Admin initial (solo no-prod): `admin` / `setup` — cambiar al entrar.

## Configuracion

| Variable / flag | On | Efecte |
|-----------------|----|--------|
| `BACKEND_URL` | `--dart-define` o pantalla de backend en l'app | URL de l'API (persiste en SharedPreferences) |
| `DATABASE_URL` | `backend/.env` | `sqlite:///./clakettes.db` (dev; en Docker `./data/clakettes.db`) o `mariadb+pymysql://…?ssl_ca=…` (prod, TLS obligatari) |
| `SECRET_KEY` | env (obligatari en `APP_ENV=production`) | Firma JWT; default insegur bloqueja l'arrancada en prod |
| `CORS_ORIGINS` | env | Origenes explicitas en prod (`*` prohibit amb credencials) |
| `APP_ENV` | env | `development` crea admin + `create_all`; `production` exige Alembic |

## Operacion

- **Migrar**: `alembic upgrade head` des de `backend/` (Docker: `-Migrate`).
- **Migracion automatica**: l'app migra sens la DB al arrancar e sella las DB novas amb la revisión actual; `SKIP_AUTO_MIGRATE=1` per omitir-lo (DBs gestionades externament).
- **SQLite → MariaDB**: `export_sqlite_to_mariadb.py`; tornada amb `import_mariadb_to_sqlite.py` (detalle en [DATABASE.md](DATABASE.md)).
- **Backups**: SQLite = copiar `*.db`; MariaDB = `mariadb-dump` (volum `db-data` en Docker).
- **Logs**: stdout de uvicorn (tokens DAV ja redactats); errors de l'API en SnackBar + `debugPrint`.
- **Limites**: corpos ≤10 MB (413 se mai gran); rate limit amb 429 + reedicio.

## Rolis d'usagi

`admin` (tot) → `organizer` (son festival: eventos, formularis, comitots) → `attendee`/`juror`/etc. (assignats pels organizers; l'auto-join dota solament `attendee`). Canals: `admin`/`moderator`/`member`; comitots amb conte de membres en la llista.

## Funcions en desvelupament activ

🚧 Las segundas funcions estan en desvelupament activ e poden cambiar:

- **Profils socials**: murs de publications (microblogging amb Markdown e incrustats de vídeo e podcast) en profils d'usagi e festival, amb fils de resposta opcionals per publicació e moderacion per rols (administradors, gestió del festival, moderadors). Sens reaccions, stickers nin GIF per ara.
- **Personalizacion de profils**: portada, tagline e enlaços socials en usagis e festivals.
- **Insignias**: desactivadas per defecte; solament l'equip administratiu pot activarlas (`PUT /api/badges/settings`). Las insignias de la plataforma li otorganpels administradors; las insignias de merito de festival (veterà, popular, ròle, premi especial), lor gestion. Cada insignia porta una imatge (SVG preferit).
- **Votacion del jurat**: puntuacion per obra, agregacio e anonimitat opcional (fasa 5 del roadmap).

## Veire ancaus

- [README.md](../../README.oc.md): descricio general del projècte e acces rapid
- [HERRAMIENTAS.md](HERRAMIENTAS.md): scripts e comandes d'execucio
- [ADMINISTRACION.md](ADMINISTRACION.md): administratzia del desplegament e rotacion de secrets
- [SEGURIDAD.md](SEGURIDAD.md): checklist e boas practicas de productiu