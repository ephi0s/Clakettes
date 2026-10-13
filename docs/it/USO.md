# Uso — Clakettes

[ES](../es/USO.md) · [EN](../en/USO.md) · [FR](../fr/USO.md) · [DE](../de/USO.md) · [IT](USO.md) · [CA](../ca/USO.md) · [EU](../eu/USO.md) · [GL](../gl/USO.md) · [OC](../oc/USO.md)

## Avvio rapido

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

Senza Docker, il launcher crea un ambiente bare-metal locale: rileva Python 3.12+ e Flutter, mostra come installarli secondo il tuo SO e offre di installarli con `-InstallMissing` (chiede prima salvo che tu vada con il flag).

URL dev: backend `http://localhost:8000` (Swagger in `/docs`), frontend `http://localhost:3000`.
Se la porta è occupata si riassegna da sola (guarda `[PUERTO]` nell'output).
Admin iniziale (solo non-prod): `admin` / `setup` — cambiare al primo accesso.

## Configurazione

| Variable / flag | Dónde | Efecto |
|---|---|---|
| `BACKEND_URL` | `--dart-define` o pantalla de backend en la app | URL del API (persiste en SharedPreferences) |
| `DATABASE_URL` | `backend/.env` | `sqlite:///./clakettes.db` (dev; en Docker `./data/clakettes.db`) o `mariadb+pymysql://…?ssl_ca=…` (prod, TLS obligatorio) |
| `SECRET_KEY` | env (obligatoria en `APP_ENV=production`) | Firma JWT; default inseguro bloquea el arranque en prod |
| `CORS_ORIGINS` | env | Orígenes explícitos en prod (`*` prohibido con credenciales) |
| `APP_ENV` | env | `development` crea admin + `create_all`; `production` exige Alembic |

## Operazione

- **Migrare**: `alembic upgrade head` da `backend/` (Docker: `-Migrate`).
- **SQLite → MariaDB**: `export_sqlite_to_mariadb.py`; ritorno con `import_mariadb_to_sqlite.py` (dettaglio in [DATABASE.md](DATABASE.md)).
- **Backup**: SQLite = copiare `*.db`; MariaDB = `mariadb-dump` (volume `db-data` in Docker).
- **Log**: uvicorn stdout (token DAV già redatti); errori di API in SnackBar + `debugPrint`.
- **Limiti**: corpi ≤10 MB (413 se maggiore); rate limit con 429 + nuovo tentativo.

## Ruoli utente

`admin` (tutto) → `organizer` (il suo festival: eventi, form, comitati) → `attendee`/`juror`/ecc. (assegnati dagli organizer; l'auto-join dà solo `attendee`). Canali: `admin`/`moderator`/`member`; comitati con conteggio membri in lista.

## Vedi anche

- [README.it.md](../../README.it.md): descrizione generale del progetto e accesso rapido
- [HERRAMIENTAS.md](HERRAMIENTAS.md): script e comandi di esecuzione
- [ADMINISTRACION.md](ADMINISTRACION.md): amministrazione del deployment e rotazione dei segreti
- [SEGURIDAD.md](SEGURIDAD.md): checklist e buone pratiche di produzione
