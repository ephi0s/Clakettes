# Amministrazione — Clakettes

[ES](../es/ADMINISTRACION.md) · [EN](../en/ADMINISTRACION.md) · [FR](../fr/ADMINISTRACION.md) · [DE](../de/ADMINISTRACION.md) · [IT](ADMINISTRACION.md) · [CA](../ca/ADMINISTRACION.md) · [EU](../eu/ADMINISTRACION.md) · [GL](../gl/ADMINISTRACION.md) · [OC](../oc/ADMINISTRACION.md)

Guida per chi gestisce un deployment. Infrastruttura in [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md), checklist di produzione in [SEGURIDAD.md](SEGURIDAD.md).

## Account iniziale

In non-prod (`APP_ENV != production`) all'avvio vengono creati `admin` / `setup` (`admin@clakettes.com`, ruolo admin) se non esistono; in prod **non vengono creati**. Cambia la password al primo accesso. L'accesso usa `POST /api/users/login` (JWT 30 min + refresh 30 d, elenco e revoca delle sessioni su `/api/auth/sessions`).

## Endpoint `/api/admin` (solo ruolo admin, 403 altrimenti)

| Metodo e rotta | Effetto |
|---|---|
| `GET /api/admin/stats` | Contatori: utenti, festival, corti, messaggi, attivi |
| `GET /api/admin/tables` | Tabelle (tranne `alembic_version`) con numero di righe |
| `GET /api/admin/audit-log` | Traccia di audit (filtri `action`, `actor_user_id`) |
| `POST /api/admin/reset` `{"confirm":"yes","password":"<actual>"}` | `drop_all + create_all`. 400 se `confirm` non è `yes`, 403 se la password non verifica; rate-limit proprio 3/300s (429, bypass con `TESTING=true`) |

## Segreti e rotazione

- `SECRET_KEY`: obbligatoria in prod (l'avvio fallisce con la chiave di esempio e indica `secrets.token_urlsafe(64)`). La rotazione invalida tutti i JWT e i refresh token: falla in una finestra di manutenzione e avvisa (tutti rifanno il login).
- `CORS_ORIGINS`: origini esplicite in prod; `*` + credenziali è vietato e blocca l'avvio.
- Dietro proxy: `uvicorn --proxy-headers` + `FORWARDED_ALLOW_IPS` + TLS frontale.

## Federazione

| Operazione | Endpoint / strumento | Effetto |
|---|---|---|
| Nodi e politiche | `GET/POST /api/federation/nodes` | Allowlist/blocklist con `consent_required`, `minimize_data`, `import_only`, `disable_chat`, `disable_search` (admin) |
| Identità del peer | `GET /api/federation/whoami` | Valida il JWT RS256 del peer contro il suo JWKS; 401 se non valido |
| Portabilità | `POST /api/federation/portability/bundles`, `/imports`, `/festivals/{id}/migrate`, `/users/{ref}/migrate`, `GET /redirects/{ref}` | Esporta/importa bundle firmati, migra proprietà e identità e risolve le vecchie ref (migrazioni, solo admin) |
| Chat e moderazione | `/api/federation/chat/bridge/{inbound,outbound,config}`, `GET /api/federation/chat/messages`, `/api/chat/moderation/*` | Bridge firmato, cronologia deduplicata, segnalazioni, mute, filtro e limite di 10 messaggi/60 s per nodo e utente |
| Eventi | `GET /api/federation/events/stream`, `POST /publish`, `GET /retry-queue` | SSE con `since` e battito, pubblicazione ai peer e ripetizioni (3 tentativi, 300 ms → 1,5 s → 5 s) |
| Resilienza | `GET /api/federation/resilience/{health,heartbeat,metrics,incident-plan}`, `POST /keys/revoke`, `GET /keys/revoked` | Health, heartbeat, metriche p50/p95, revoca immediata delle chiavi e piano incidente |
| Conformità | `python tools/federation_conformance.py <url> [--json]` | Verifica un nodo terzo; esce 1 in caso di errori critici/alti |

Il dettaglio del modello di fiducia e del trasporto è in [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md) e [FEDERATION_CHAT_BROKER.md](FEDERATION_CHAT_BROKER.md).

## Backup e migrazioni

- SQLite: copiare `*.db` a fermo (`-Kill` prima). MariaDB: `mariadb-dump` (volume `db-data`).
- Migrazioni: `alembic upgrade head` da `backend/` (prod **solo** Alembic, mai `create_all`). Le ultime migrazioni aggiungono `identity_redirects`, `migration_audits`, `chat_outbox`, `message_reports`, `chat_mutes`, l'unicità del posto (`uq_event_seat_location`) e `contest_type` nei corti con `festival_id` obbligatorio.
- Cambio motore: `python export_sqlite_to_mariadb.py` (dev→prod), `python import_mariadb_to_sqlite.py` (prod→dev); dettaglio in [DATABASE.md](DATABASE.md).

## Risoluzione problemi

| Sintomo | Causa probabile | Azione |
|---|---|---|
| Avvio interrotto per `SECRET_KEY` / CORS | default insicuro o `*` in prod | Definisci `SECRET_KEY` e `CORS_ORIGINS` espliciti |
| `401` su endpoint pubblici dei moduli | link generato male | Controlla il token del link; l'accesso anonimo non dà 401 da solo |
| `403` gestendo festival/canale/comitato | chiamante senza ruolo | Verifica appartenenza e ruolo (`GET …/members`); l'auto-join dà solo `attendee` |
| `409` all'unione | già membro | Usa `leave` o gestisci dai membri |
| `413` in upload | supera 10 MB corpo / 5 MB immagine / 100 MB video / 10 MB pdf | Comprimi o dividi il file |
| `429` generalizzato | rate limit 100/60s per IP (o 3/300s sul reset) | Attendi e riprova; controlla un `TESTING=true` residuo |
| WS non si connette | JWT senza `type=access` o sessione revocata/scaduta | Rifai il login; controlla `/api/auth/sessions` |
| App offline non sincronizza | coda con fallimenti esauriti (`failed`, 3 tentativi + backoff) | Controlla gli errori nel prompt di sync; `clear()` dopo conferma al logout |
| `403` importando un bundle | `origin_domain` non consentito nella politica del nodo | Controlla `/api/federation/nodes` e importa di nuovo |
| `429` nella chat federata | oltre 10 messaggi/60 s per nodo e utente | Attendi il `Retry-After`; nei test si disattiva con `TESTING=true` |
| Eventi SSE interrotti o senza dati | token non valido o `since` oltre il replay | Rifanno il login e ripartono con `since=0` (replay di 200 eventi) |
| Messaggi federati duplicati | reinvio del bridge | Scartati per `message_id` in `chat_outbox`; controlla `/api/federation/chat/messages` |

## Vedi anche

- [USO.md](USO.md): avvio e gestione del sistema
- [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md): deployment, porte e CI
- [SEGURIDAD.md](SEGURIDAD.md): checklist di hardening e politiche
- [../README.md](../../README.md): contesto globale del progetto
