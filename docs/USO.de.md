# Nutzung — Clakettes

[ES](USO.md) · [EN](USO.en.md) · [FR](USO.fr.md) · [DE](USO.de.md) · [IT](USO.it.md) · [CA](USO.ca.md) · [EU](USO.eu.md) · [GL](USO.gl.md) · [OC](USO.oc.md)

## Schnellstart

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

Ohne Docker erstellt der Launcher eine lokale Bare-Metal-Umgebung: erkennt Python 3.12+ und Flutter, zeigt die installweise je nach OS und bietet Installation mit `-InstallMissing` an (fragt vorher, außer mit dem Flag).

Dev-URLs: Backend `http://localhost:8000` (Swagger unter `/docs`), Frontend `http://localhost:3000`.
Wenn der Port belegt ist, wird er automatisch neu zugewiesen (siehe `[PUERTO]` in der Ausgabe).
Initialer Admin (nur Nicht-Prod): `admin` / `setup` — nach dem Login ändern.

## Konfiguration

| Variable / flag | Dónde | Efecto |
|---|---|---|
| `BACKEND_URL` | `--dart-define` o pantalla de backend en la app | URL del API (persiste en SharedPreferences) |
| `DATABASE_URL` | `backend/.env` | `sqlite:///./clakettes.db` (dev; en Docker `./data/clakettes.db`) o `mariadb+pymysql://…?ssl_ca=…` (prod, TLS obligatorio) |
| `SECRET_KEY` | env (obligatoria en `APP_ENV=production`) | Firma JWT; default inseguro bloquea el arranque en prod |
| `CORS_ORIGINS` | env | Orígenes explícitos en prod (`*` prohibido con credenciales) |
| `APP_ENV` | env | `development` crea admin + `create_all`; `production` exige Alembic |

## Betrieb

- **Migrieren**: `alembic upgrade head` aus `backend/` (Docker: `-Migrate`).
- **SQLite → MariaDB**: `export_sqlite_to_mariadb.py`; zurück mit `import_mariadb_to_sqlite.py` (Details in [DATABASE.de.md](DATABASE.de.md)).
- **Backups**: SQLite = `*.db` kopieren; MariaDB = `mariadb-dump` (Volume `db-data` in Docker).
- **Logs**: Uvicorn-Stdout (DAV-Tokens bereits redigiert); API-Fehler in SnackBar + `debugPrint`.
- **Limits**: Bodys ≤10 MB (413 wenn größer); Rate-Limit mit 429 + Retry.

## Nutzerrollen

`admin` (alles) → `organizer` (sein Festival: Events, Formulare, Komitees) → `attendee`/`juror`/etc. (von Organizern vergeben; Auto-Join gibt nur `attendee`). Kanäle: `admin`/`moderator`/`member`; Komitees mit Mitgliederzählung in der Liste.

## Siehe auch

- [README.de.md](../README.de.md): allgemeine Projektbeschreibung und Schnellzugriff
- [HERRAMIENTAS.de.md](HERRAMIENTAS.de.md): Skripte und Ausführungsbefehle
- [ADMINISTRACION.de.md](ADMINISTRACION.de.md): Deployment-Verwaltung und Secret-Rotation
- [SEGURIDAD.de.md](SEGURIDAD.de.md): Checkliste und Produktions-Best-Practices
