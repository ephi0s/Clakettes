# Uso — Clakettes

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
| Builds distribuibles | `-BuildAll` (`tools/build-all.ps1` → `builds/`) |

URLs dev: backend `http://localhost:8000` (Swagger en `/docs`), frontend `http://localhost:3000`.
Admin inicial (solo no-prod): `admin` / `setup` — cambiar al entrar.

## Configuración

| Variable / flag | Dónde | Efecto |
|---|---|---|
| `BACKEND_URL` | `--dart-define` o pantalla de backend en la app | URL del API (persiste en SharedPreferences) |
| `DATABASE_URL` | `backend/.env` | `sqlite:///./clakettes.db` (dev) o `mariadb+pymysql://…` (prod) |
| `SECRET_KEY` | env (obligatoria en `APP_ENV=production`) | Firma JWT; default inseguro bloquea el arranque en prod |
| `CORS_ORIGINS` | env | Orígenes explícitos en prod (`*` prohibido con credenciales) |
| `APP_ENV` | env | `development` crea admin + `create_all`; `production` exige Alembic |

## Operación

- **Migrar**: `alembic upgrade head` desde `backend/` (Docker: `-Migrate`).
- **SQLite → MariaDB**: `export_sqlite_to_mariadb.py`; vuelta con `import_mariadb_to_sqlite.py` (detalle en `DATABASE.md`).
- **Backups**: SQLite = copiar `*.db`; MariaDB = `mariadb-dump` (volumen `db-data` en Docker).
- **Logs**: uvicorn stdout (tokens DAV ya redactados); errores de API en SnackBar + `debugPrint`.
- **Límites**: cuerpos ≤10 MB (413 si mayor); rate limit con 429 + reintento.

## Roles de usuario

`admin` (todo) → `organizer` (su festival: eventos, formularios, comités) → `attendee`/`juror`/etc. (asignados por organizers; el auto-join solo da `attendee`). Canales: `admin`/`moderator`/`member`; comités con conteo de miembros en lista.
