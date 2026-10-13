# Ús — Clakettes

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
- **SQLite → MariaDB**: `export_sqlite_to_mariadb.py`; tornada amb `import_mariadb_to_sqlite.py` (detalh en [DATABASE.oc.md](DATABASE.oc.md)).
- **Salvagardas**: SQLite = copiar `*.db`; MariaDB = `mariadb-dump` (volum `db-data` en Docker).
- **Jornaus**: uvicorn stdout (tokens DAV ja redactats); errors d'API en SnackBar + `debugPrint`.
- **Limits**: còrses ≤10 MB (413 se màger); rate limit amb 429 + tornada d'ensajar.

## Ròtles d'utilizaire

`admin` (tot) → `organizer` (son festivau: eveniments, formularis, comitats) → `attendee`/`juror`/etc. (assignats per organizers; l'auto-join sonque dona `attendee`). Canaus: `admin`/`moderator`/`member`; comitats amb comptatge de membres en lista.

## Veire tanben

- [README.oc.md](../README.oc.md): descripcion generala del projècte e accès rapid
- [HERRAMIENTAS.oc.md](HERRAMIENTAS.oc.md): scripts e comandas d'execucion
- [ADMINISTRACION.oc.md](ADMINISTRACION.oc.md): administracion del desplegament e rotacion de secrets
- [SEGURIDAD.oc.md](SEGURIDAD.oc.md): checklist e bonas practicas de produccion
