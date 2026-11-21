# Utilizzo — Clakettes

[ES](../es/USO.md) · [EN](../en/USO.md) · [FR](../fr/USO.md) · [DE](../de/USO.md) · [IT](USO.md) · [CA](../ca/USO.md) · [EU](../eu/USO.md) · [GL](../gl/USO.md) · [OC](../oc/USO.md)

## Avvio rapido

| Voglio | Comando |
|---|---|
| Tutto in locale | `.\start.ps1` o `./start.sh` (Docker se disponibile, locale altrimenti) |
| Solo backend / frontend | `-NoFrontend` / `-NoBackend` |
| Provare nel browser | `-Web` (modalità locale) |
| Produzione locale | `-Final` (build web + serve) |
| Test | `-TestBackend` / `-TestFrontend` |
| Migrazioni / con MariaDB | `-Migrate` / `-MariaDB` / `-TestMigration` |
| Fermare tutto | `-Kill` |
| Installare le dipendenze mancanti | `-InstallMissing` (Windows: winget + git clone; Linux/macOS: gestore del SO + git clone) |
| Controllare l'ambiente senza avviare | `-Check` (doctor: Docker, Python, Flutter, .venv, porte; esce 1 se manca qualcosa) |
| Build distribuibili | `-BuildAll` (`tools/build-all.ps1` → `builds/`) |

Senza Docker, il launcher crea un ambiente locale bare-metal: rileva Python 3.12+ e Flutter, mostra come installarli in base al SO e offre di installarli con `-InstallMissing` (chiede prima salvo che tu passi il flag).

URL dev: backend `http://localhost:8000` (Swagger su `/docs`), frontend `http://localhost:3000`.
Se la porta è occupata viene riassegnata automaticamente (vedi `[PUERTO]` nell'output).
Admin iniziale (solo non-prod): `admin` / `setup` — da cambiare al primo accesso.

## Configurazione

| Variabile / flag | Dove | Effetto |
|---|---|---|
| `BACKEND_URL` | `--dart-define` o schermata backend nell'app | URL dell'API (persistita in SharedPreferences) |
| `DATABASE_URL` | `backend/.env` | `sqlite:///./clakettes.db` (dev; in Docker `./data/clakettes.db`) o `mariadb+pymysql://…?ssl_ca=…` (prod, TLS obbligatorio) |
| `SECRET_KEY` | env (obbligatoria in `APP_ENV=production`) | Firma JWT; default insicuro blocca l'avvio in prod |
| `CORS_ORIGINS` | env | Origini esplicite in prod (`*` vietato con credenziali) |
| `APP_ENV` | env | `development` crea admin + `create_all`; `production` richiede Alembic |
| `PUBLIC_BASE_URL` | `backend/.env` | Dominio pubblico del nodo; appare nel manifesto e nei bundle di portabilità |
| `MTLS_REQUIRED` | env | Impone peer mTLS verificato nella federazione (CN e PEM del certificato) |
| `MTLS_CLIENT_CERT_PATH`, `MTLS_CLIENT_KEY_PATH` | env | PEM del certificato e chiave privata che firmano il manifesto (RSA-SHA256) |

## Gestione

- **Migrare**: `alembic upgrade head` da `backend/` (Docker: `-Migrate`).
- **Migrazione automatica**: l'app migra da sola il DB all'avvio e sigilla i nuovi DB con la revisione corrente; `SKIP_AUTO_MIGRATE=1` per ometterla (DB gestiti esternamente).
- **SQLite → MariaDB**: `export_sqlite_to_mariadb.py`; ritorno con `import_mariadb_to_sqlite.py` (dettaglio in [DATABASE.md](DATABASE.md)).
- **Backup**: SQLite = copiare `*.db`; MariaDB = `mariadb-dump` (volume `db-data` in Docker).
- **Log**: stdout di uvicorn (token DAV redatti); errori API in SnackBar + `debugPrint`.
- **Limiti**: corpi ≤10 MB (413 se maggiore); rate limit con 429 + ripetizione (federation 60/60 s per IP; chat 10/60 s per nodo e utente, disattivato con `TESTING=true`).
- **Federazione**: verifica un nodo terzo con `python tools/federation_conformance.py <url> [--json]`; la salute del peering è su `/api/federation/resilience/health` e le metriche p50/p95 su `/metrics`.
- **Portabilità**: esporta/importa bundle da `/api/federation/portability/{bundles,imports}` e consulta i redirect di identità su `/redirects/{ref}`.

## Ruoli utente

`admin` (tutto) → `organizer` (il proprio festival: eventi, moduli, comitati) → `attendee`/`juror`/ecc. (assegnati dagli organizer; l'auto-join dà solo `attendee`). Canali: `admin`/`moderator`/`member`; comitati con conteggio membri in lista.

## Funzioni in sviluppo attivo

🚧 Le seguenti funzioni sono in sviluppo attivo e possono cambiare:

- **Profili sociali**: muri di pubblicazioni (microblogging con Markdown e incorporamenti di video e podcast) sui profili utente e festival, con thread di risposte opzionali per pubblicazione e moderazione per ruoli (amministratori, gestione del festival, moderatori). Per ora niente reazioni, sticker o GIF.
- **Personalizzazione dei profili**: copertina, tagline e link sociali su utenti e festival.
- **Distintivi**: disattivati di default; solo il team amministrativo può attivarli (`PUT /api/badges/settings`). I distintivi della piattaforma sono assegnati dagli amministratori; quelli di merito del festival (veterano, popolare, ruolo, premio speciale), loro gestione. Ogni distintivo ha un'immagine (SVG preferito).
- **Votazione della giuria**: punteggio per opera, aggregazione e anonimato opzionale (fase 5 della roadmap).

## Vedi anche

- [README.md](../../README.md): descrizione generale del progetto e accesso rapido
- [HERRAMIENTAS.md](HERRAMIENTAS.md): script e comandi di esecuzione
- [ADMINISTRACION.md](ADMINISTRACION.md): amministrazione del deployment e rotazione dei segreti
- [SEGURIDAD.md](SEGURIDAD.md): checklist e best practice di produzione
