# Uso — Clakettes

[ES](../es/USO.md) · [EN](../en/USO.md) · [FR](../fr/USO.md) · [DE](../de/USO.md) · [IT](USO.md) · [CA](../ca/USO.md) · [EU](../eu/USO.md) · [GL](../gl/USO.md) · [OC](../oc/USO.md)

## Avvio rapido

| Voglio | Comando |
|--------|---------|
| Tutto in locale | `.\start.ps1` o `./start.sh` (Docker se disponibile, locale altrimenti) |
| Solo backend / frontend | `-NoFrontend` / `-NoBackend` |
| Test nel browser | `-Web` (modo locale) |
| Produzione locale | `-Final` (build web + serve) |
| Test | `-TestBackend` / `-TestFrontend` |
| Migrazioni / con MariaDB | `-Migrate` / `-MariaDB` / `-TestMigration` |
| Fermare tutto | `-Kill` |
| Installare dipendenze mancanti | `-InstallMissing` (Windows: winget + git clone; Linux/macOS: gestore pacchetti OS + git clone) |
| Verificare ambiente senza avviare | `-Check` (doctor: Docker, Python, Flutter, .venv, porte; esce 1 se manca qualcosa) |
| Build distribuibili | `-BuildAll` (`tools/build-all.ps1` → `builds/`) |

Senza Docker, il launcher crea un ambiente bare-metal locale: rileva Python 3.12+ e Flutter, mostra come installarli secondo il tuo SO e offre di installarli con `-InstallMissing` (chiede prima a meno che non si passi il flag).

URL dev: backend `http://localhost:8000` (Swagger su `/docs`), frontend `http://localhost:3000`.
Se la porta è occupata viene riassegnata automaticamente (vedi `[PUERTO]` nell'output).
Admin iniziale (solo non-prod): `admin` / `setup` — cambiare al primo accesso.

## Configurazione

| Variabile / flag | Dove | Effetto |
|------------------|------|---------|
| `BACKEND_URL` | `--dart-define` o schermo backend nell'app | URL dell'API (persistito in SharedPreferences) |
| `DATABASE_URL` | `backend/.env` | `sqlite:///./clakettes.db` (dev; in Docker `./data/clakettes.db`) o `mariadb+pymysql://…?ssl_ca=…` (prod, TLS obbligatorio) |
| `SECRET_KEY` | env (obbligatoria in `APP_ENV=production`) | Firma JWT; default insicuro blocca l'avvio in prod |
| `CORS_ORIGINS` | env | Origini esplicite in prod (`*` proibito con credenziali) |
| `APP_ENV` | env | `development` crea admin + `create_all`; `production` richiede Alembic |

## Operazione

- **Migrare**: `alembic upgrade head` da `backend/` (Docker: `-Migrate`).
- **Migrazione automatica**: l'app migra il DB da sola all'avvio e sigilla i DB nuovi con la revisione corrente; `SKIP_AUTO_MIGRATE=1` per ometterlo (DB gestiti esternamente).
- **SQLite → MariaDB**: `export_sqlite_to_mariadb.py`; ritorno con `import_mariadb_to_sqlite.py` (dettaglio in [DATABASE.md](DATABASE.md)).
- **Backup**: SQLite = copia `*.db`; MariaDB = `mariadb-dump` (volume `db-data` in Docker).
- **Log**: stdout uvicorn (token DAV già redactati); errori API in SnackBar + `debugPrint`.
- **Limiti**: corpi ≤10 MB (413 se maggiore); rate limit con 429 + ripetizione.

## Ruoli utente

`admin` (tutto) → `organizer` (il suo festival: eventi, moduli, comitati) → `attendee`/`juror`/etc. (assegnati dagli organizer; auto-join dà solo `attendee`). Canali: `admin`/`moderator`/`member`; comitati con conteo membri nella lista.

## Funzioni in sviluppo attivo

🚧 Le seguenti funzioni sono in sviluppo attivo e possono cambiare:

- **Profili sociali**: muri di pubblicazione (microblogging con Markdown e inserimenti video/podcast) su profili utente e festival, con fili di risposte opzionali per pubblicazione e moderazione per ruoli (amministratori, gestione festival, moderatori). Nessuna reazione, sticker o GIF per ora.
- **Personalizzazione profili**: copertina, tagline e link social su utenti e festival.
- **Badge**: disattivati per default; solo il team amministrativo può attivarli (`PUT /api/badges/settings`). Badge della piattaforma concessi dagli amministratori; badge di merito del festival (veterano, popolare, ruolo, premio speciale), loro gestione. Ogni badge ha un'immagine (SVG preferito).
- **Voto giuria**: punteggio per opera, aggregazione e anonimato opzionale (fase 5 della roadmap).

## Vedi anche

- [README.md](../../README.it.md): descrizione generale del progetto e accesso rapido
- [HERRAMIENTAS.md](HERRAMIENTAS.md): script e comandi di esecuzione
- [ADMINISTRACION.md](ADMINISTRACION.md): amministrazione del deployment e rotazione segreti
- [SEGURIDAD.md](SEGURIDAD.md): checklist e best practice di produzione