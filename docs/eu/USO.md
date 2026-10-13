# Erabilera — Clakettes

[ES](../es/USO.md) · [EN](../en/USO.md) · [FR](../fr/USO.md) · [DE](../de/USO.md) · [IT](../it/USO.md) · [CA](../ca/USO.md) · [EU](USO.md) · [GL](../gl/USO.md) · [OC](../oc/USO.md)

## Abiarazte azkarra

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

Docker gabe, abiarazleak tokiko bare-metal ingurune bat sortzen du: Python 3.12+ eta Flutter detektatzen ditu, zure SO-aren arabera nola instalatu erakusten du eta `-InstallMissing`-ekin instalatzea eskaintzen du (aurretik galdetzen du flag-arekin zoazenean izan ezik).

Dev URL-ak: backend `http://localhost:8000` (Swagger `/docs`-en), frontend `http://localhost:3000`.
Portua okupatuta badago bakarrik biresleitzen da (begiratu `[PUERTO]` irteeran).
Hasierako admin-a (ez-prod soilik): `admin` / `setup` — sartzean aldatu.

## Konfigurazioa

| Variable / flag | Dónde | Efecto |
|---|---|---|
| `BACKEND_URL` | `--dart-define` o pantalla de backend en la app | URL del API (persiste en SharedPreferences) |
| `DATABASE_URL` | `backend/.env` | `sqlite:///./clakettes.db` (dev; en Docker `./data/clakettes.db`) o `mariadb+pymysql://…?ssl_ca=…` (prod, TLS obligatorio) |
| `SECRET_KEY` | env (obligatoria en `APP_ENV=production`) | Firma JWT; default inseguro bloquea el arranque en prod |
| `CORS_ORIGINS` | env | Orígenes explícitos en prod (`*` prohibido con credenciales) |
| `APP_ENV` | env | `development` crea admin + `create_all`; `production` exige Alembic |

## Operazioa

- **Migratu**: `alembic upgrade head` `backend/`-tik (Docker: `-Migrate`).
- **SQLite → MariaDB**: `export_sqlite_to_mariadb.py`; itzulera `import_mariadb_to_sqlite.py`-rekin (xehetasuna [DATABASE.md](DATABASE.md)-n).
- **Backup-ak**: SQLite = `*.db` kopiatu; MariaDB = `mariadb-dump` (`db-data` bolumena Docker-en).
- **Log-ak**: uvicorn stdout (DAV token-ak jada redaktatuta); API erroreak SnackBar + `debugPrint`-en.
- **Mugak**: gorputzak ≤10 MB (413 handiagoa bada); rate limit 429 + saiakera-errepikapenarekin.

## Erabiltzaile-rolak

`admin` (dena) → `organizer` (bere jaialdia: ekitaldiak, inprimakiak, batzordeak) → `attendee`/`juror`/etab. (organizer-ek esleituta; auto-join-ek `attendee` soilik ematen du). Kanalak: `admin`/`moderator`/`member`; kide-zenbaketa duten batzordeak zerrendan.

## Ikusi halaber

- [README.md](../../README.eu.md): proiektuaren deskribapen orokorra eta sarbide azkarra
- [HERRAMIENTAS.md](HERRAMIENTAS.md): exekuzio script-ak eta komandoak
- [ADMINISTRACION.md](ADMINISTRACION.md): hedapenaren administrazioa eta sekretuen errotazioa
- [SEGURIDAD.md](SEGURIDAD.md): ekoizpeneko checklist-a eta jardunbide egokiak
