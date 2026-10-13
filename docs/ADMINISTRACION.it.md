# Amministrazione — Clakettes

Guida per chi gestisce un deployment. Infrastruttura in [INFRAESTRUCTURA.it.md](INFRAESTRUCTURA.it.md), checklist di produzione in [SEGURIDAD.it.md](SEGURIDAD.it.md).

## Account iniziale

In non-prod (`APP_ENV != production`) l'avvio crea `admin` / `setup` (`admin@clakettes.com`, ruolo admin) se non esiste; in prod **non viene creato**. Cambia la password al primo accesso. Il login usa `POST /api/users/login` (JWT 30 min + refresh 30 g, elenco e revoca delle sessioni in `/api/auth/sessions`).

## Endpoint `/api/admin` (solo ruolo admin, 403 negli altri casi)

| Metodo e rotta | Effetto |
|---|---|
| `GET /api/admin/stats` | Conteggi: utenti, festival, corti, messaggi, attivi |
| `GET /api/admin/tables` | Tabelle (meno `alembic_version`) con n. di righe |
| `POST /api/admin/reset` `{"confirm":"yes","password":"<actual>"}` | `drop_all + create_all`. 400 se `confirm` non è `yes`, 403 se la password non verifica; rate-limit proprio 3/300s (429, bypass con `TESTING=true`) |

## Segreti e rotazione

- `SECRET_KEY`: obbligatoria in prod (l'avvio fallisce con quella di esempio e indica `secrets.token_urlsafe(64)`). Ruotarla invalida tutti i JWT e i refresh token: farlo in una finestra di manutenzione e avvisare (tutti devono rieffettuare il login).
- `CORS_ORIGINS`: origini esplicite in prod; `*` + credenziali è vietato e blocca l'avvio.
- Dietro proxy: `uvicorn --proxy-headers` + `FORWARDED_ALLOW_IPS` + TLS frontale.

## Backup e migrazioni

- SQLite: copiare `*.db` a caldo fermo (`-Kill` prima). MariaDB: `mariadb-dump` (volume `db-data`).
- Migrazioni: `alembic upgrade head` da `backend/` (18 versioni; in prod **solo** Alembic, mai `create_all`).
- Cambio di motore: `python export_sqlite_to_mariadb.py` (dev→prod), `python import_mariadb_to_sqlite.py` (prod→dev); dettaglio in [DATABASE.it.md](DATABASE.it.md).

## Troubleshooting

| Sintomo | Causa probabile | Azione |
|---|---|---|
| Avvio interrotto per `SECRET_KEY` / CORS | default insicuro o `*` in prod | Definisci `SECRET_KEY` e `CORS_ORIGINS` espliciti |
| `401` negli endpoint pubblici dei form | link generato male | Controlla il token del link; l'accesso anonimo non dà 401 di per sé |
| `403` gestendo festival/canale/comitato | caller senza ruolo | Verifica appartenenza e ruolo (`GET …/members`); l'auto-join dà solo `attendee` |
| `409` unendosi | è già membro | Usa `leave` o gestisci dai membri |
| `413` caricando | supera 10 MB corpo / 5 MB immagine / 100 MB video / 10 MB pdf | Comprimi o dividi il file |
| `429` generalizzato | rate limit 100/60s per IP (o 3/300s nel reset) | Attendi e riprova; controlla `TESTING=true` residuo |
| WS non si connette | JWT senza `type=access` o sessione revocata/scaduta | Re-login; controlla `/api/auth/sessions` |
| App offline non sincronizza | coda con errori esauriti (`failed`, 3 tentativi + backoff) | Controlla gli errori nel prompt di sync; `clear()` dopo conferma nel logout |

## Vedi anche

- [USO.it.md](USO.it.md): avvio e gestione del sistema
- [INFRAESTRUCTURA.it.md](INFRAESTRUCTURA.it.md): deployment, porte e CI
- [SEGURIDAD.it.md](SEGURIDAD.it.md): checklist di hardening e policy
- [../README.it.md](../README.it.md): contesto globale del progetto
