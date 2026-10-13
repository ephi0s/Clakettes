# Uso — Clakettes

[ES](../es/USO.md) · [EN](../en/USO.md) · [FR](../fr/USO.md) · [DE](../de/USO.md) · [IT](../it/USO.md) · [CA](../ca/USO.md) · [EU](../eu/USO.md) · [GL](USO.md) · [OC](../oc/USO.md)

## Arranque rápido

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

Sen Docker, o lanzador crea un entorno bare-metal local: detecta Python 3.12+ e Flutter, mostra como instalalos segundo o teu SO e ofrece instalalos con `-InstallMissing` (pregunta antes salvo que vaias co flag).

URLs dev: backend `http://localhost:8000` (Swagger en `/docs`), frontend `http://localhost:3000`.
Se o porto está ocupado reasígnase só (mira `[PUERTO]` na saída).
Admin inicial (só non-prod): `admin` / `setup` — cambiar ao entrar.

## Configuración

| Variable / flag | Dónde | Efecto |
|---|---|---|
| `BACKEND_URL` | `--dart-define` o pantalla de backend en la app | URL del API (persiste en SharedPreferences) |
| `DATABASE_URL` | `backend/.env` | `sqlite:///./clakettes.db` (dev; en Docker `./data/clakettes.db`) o `mariadb+pymysql://…?ssl_ca=…` (prod, TLS obligatorio) |
| `SECRET_KEY` | env (obligatoria en `APP_ENV=production`) | Firma JWT; default inseguro bloquea el arranque en prod |
| `CORS_ORIGINS` | env | Orígenes explícitos en prod (`*` prohibido con credenciales) |
| `APP_ENV` | env | `development` crea admin + `create_all`; `production` exige Alembic |

## Operación

- **Migrar**: `alembic upgrade head` desde `backend/` (Docker: `-Migrate`).
- **SQLite → MariaDB**: `export_sqlite_to_mariadb.py`; volta con `import_mariadb_to_sqlite.py` (detalle en [DATABASE.md](DATABASE.md)).
- **Backups**: SQLite = copiar `*.db`; MariaDB = `mariadb-dump` (volume `db-data` en Docker).
- **Logs**: uvicorn stdout (tokens DAV xa redactados); erros de API en SnackBar + `debugPrint`.
- **Límites**: corpos ≤10 MB (413 se maior); rate limit con 429 + reintento.

## Roles de usuario

`admin` (todo) → `organizer` (o seu festival: eventos, formularios, comités) → `attendee`/`juror`/etc. (asignados por organizers; o auto-join só dá `attendee`). Canles: `admin`/`moderator`/`member`; comités con conteo de membros en lista.

## Ver tamén

- [README.md](../../README.gl.md): descricion xeral do proxecto e acceso rápido
- [HERRAMIENTAS.md](HERRAMIENTAS.md): scripts e comandos de execucion
- [ADMINISTRACION.md](ADMINISTRACION.md): administración do despregamento e rotacion de segredos
- [SEGURIDAD.md](SEGURIDAD.md): checklist e boas practicas de producion
