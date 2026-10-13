# Usage — Clakettes

## Démarrage rapide

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

Sans Docker, le lanceur crée un environnement bare-metal local : détecte Python 3.12+ et Flutter, montre comment les installer selon ton OS et offre de les installer avec `-InstallMissing` (demande avant sauf si tu vas avec le flag).

URLs dev : backend `http://localhost:8000` (Swagger sur `/docs`), frontend `http://localhost:3000`.
Si le port est occupé il est réassigné seul (regarde `[PUERTO]` dans la sortie).
Admin initial (seulement non-prod) : `admin` / `setup` — changer en entrant.

## Configuration

| Variable / flag | Dónde | Efecto |
|---|---|---|
| `BACKEND_URL` | `--dart-define` o pantalla de backend en la app | URL del API (persiste en SharedPreferences) |
| `DATABASE_URL` | `backend/.env` | `sqlite:///./clakettes.db` (dev; en Docker `./data/clakettes.db`) o `mariadb+pymysql://…?ssl_ca=…` (prod, TLS obligatorio) |
| `SECRET_KEY` | env (obligatoria en `APP_ENV=production`) | Firma JWT; default inseguro bloquea el arranque en prod |
| `CORS_ORIGINS` | env | Orígenes explícitos en prod (`*` prohibido con credenciales) |
| `APP_ENV` | env | `development` crea admin + `create_all`; `production` exige Alembic |

## Opération

- **Migrer** : `alembic upgrade head` depuis `backend/` (Docker : `-Migrate`).
- **SQLite → MariaDB** : `export_sqlite_to_mariadb.py` ; retour avec `import_mariadb_to_sqlite.py` (détail dans [DATABASE.fr.md](DATABASE.fr.md)).
- **Sauvegardes** : SQLite = copier `*.db` ; MariaDB = `mariadb-dump` (volume `db-data` en Docker).
- **Logs** : uvicorn stdout (tokens DAV déjà caviardés) ; erreurs d'API en SnackBar + `debugPrint`.
- **Limites** : corps ≤10 MB (413 si majeur) ; rate limit avec 429 + réessai.

## Rôles d'utilisateur

`admin` (tout) → `organizer` (son festival : événements, formulaires, comités) → `attendee`/`juror`/etc. (assignés par organizers ; l'auto-join donne seulement `attendee`). Canaux : `admin`/`moderator`/`member` ; comités avec comptage de membres en liste.

## Voir aussi

- [README.fr.md](../README.fr.md) : description générale du projet et accès rapide
- [HERRAMIENTAS.fr.md](HERRAMIENTAS.fr.md) : scripts et commandes d'exécution
- [ADMINISTRACION.fr.md](ADMINISTRACION.fr.md) : administration du déploiement et rotation de secrets
- [SEGURIDAD.fr.md](SEGURIDAD.fr.md) : liste de contrôle et bonnes pratiques de production
