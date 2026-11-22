# Clakettes Schema v1

[ES](../es/FEDERATION_SCHEMA.md) · [EN](../en/FEDERATION_SCHEMA.md) · [FR](../fr/FEDERATION_SCHEMA.md) · [DE](../de/FEDERATION_SCHEMA.md) · [IT](FEDERATION_SCHEMA.md) · [CA](../ca/FEDERATION_SCHEMA.md) · [EU](../eu/FEDERATION_SCHEMA.md) · [GL](../gl/FEDERATION_SCHEMA.md) · [OC](../oc/FEDERATION_SCHEMA.md)

Versione iniziale dello schema di federazione. Definisce le entità minime scambiabili tra nodi, versionate tramite `schema_version` nel manifesto di ogni nodo.

## Modello di fiducia (Fase 2)

L'identità di un nodo è la tupla **(dominio, certificato TLS X.509)**. Il peering tra nodi avviene su mTLS reciproco: ogni nodo valida la catena di certificati del peer contro la propria CA radice, verifica che il dominio del certificato corrisponda a quello dichiarato e respinge i certificati self-signed in produzione. La rotazione e la revoca sono gestite tramite rinnovo del certificato.

## Entità

- `festival`: id, name, edition, created_at, owner_node
- `user`: id, uuid, did, handle, username, node_origin
- `message`: id, sender, recipient, body, created_at, node_origin
- `moderation_report`: id, reporter_node, target_node, target_user_ref, reason, status
- `identity_redirect`: old_ref, new_ref, target_domain, created_at
- `migration_audit`: entity_type, entity_id, action, source_domain, target_domain, details, created_at
- `chat_outbox`: message_id (unico), node_origin, subject, payload, signature, status, attempts, last_error, created_at
- `message_report`: reporter_id, message_id, reason, status
- `chat_mute`: user_id, channel_id, node_domain, until, reason

## Campi e vincoli

- `uuid`: identificatore stabile globale (UUID v4).
- `did`: identificatore decentralizzato opzionale.
- `handle`: `utente@istanza` risolvibile tramite WebFinger.
- `schema_version`: versione dello schema dichiarata dal nodo nel proprio manifesto (attuale: `1`).

## Endpoint di federazione

### Identità e directory

- `GET /api/federation/manifest` — manifesto del nodo con `schema_version`, `node`, `version`, `capabilities`, `issued_at`, `expires_at`, `signature` e `certificate_chain`. Firma RSA-SHA256 con la chiave privata del certificato TLS del nodo; il peer valida il PEM della catena e la validità di `expires_at` (24 h).
- `GET /api/federation/directory` — elenco dei nodi attendibili (`trusted_nodes`) con `allowed = true`, incluso `cert_fingerprint_sha256` (impronta del PEM), `capabilities`, `consent_required`, `minimize_data`.
- `GET/POST /api/federation/nodes` — politiche di nodo (allowlist/blocklist): `consent_required`, `minimize_data`, `import_only`, `disable_chat`, `disable_search`. Solo admin; le ultime tre vengono persistite e applicate nel bridge e nel bus degli eventi.

### Identità federata e token (Fase 3)

- `GET /api/federation/.well-known/jwks.json` — chiave pubblica RSA del nodo in formato JWKS per validare i token di federazione dei peer.
- `POST /api/federation/token` — emette un JWT di federazione firmato (RS256). Richiede identità del nodo verificata tramite mTLS.
- `POST /api/federation/peers/verify` — valida l'identità di un nodo remoto (dominio + CN e PEM del certificato + manifesto firmato).
- `POST /api/federation/peers/{domain}/revoke` — revoca un nodo attendibile (admin).
- `GET /api/federation/whoami` — identità del peer (`iss`, `sub`, nodo) solo se il suo Bearer JWT viene validato contro il suo JWKS; 401 altrimenti.

### Utenti, segnalazioni e scoperta

- `GET /api/federation/users/{ref}` — risolve l'utente per `uuid`, `did` o `handle`. Richiede peer mTLS verificato.
- `GET /api/federation/.well-known/webfinger` — risolve `acct:user@domain`. Richiede peer mTLS verificato.
- `POST/GET/PATCH /api/federation/reports` — segnalazione di moderazione tra nodi.

### Portabilità (Fase 7)

- `POST /api/federation/portability/bundles` — genera un bundle dell'utente con `bundle_version`, `origin_domain`, `payload`, `signature` (HMAC-SHA256 con `SECRET_KEY`) e `checksum` (SHA-256 del payload canonico).
- `POST /api/federation/portability/imports` — valida firma e checksum, controlla la politica di origine (403 se non consentito), applica `minimize_data` e registra ciò che è stato importato (utente, corti, festival, messaggi). I bundle includono `contest_type` in ogni corto: si valida/sanea `MediaUrl` (URL non valido → `null`), si normalizza `contest_type` a `official_section` se non è valido e il checksum del festival lo include.
- `POST /api/federation/portability/festivals/{festival_id}/migrate` — trasferisce la proprietà del festival e i suoi corti a `new_owner_id` di `target_domain` con verifica del checksum; solo admin.
- `POST /api/federation/portability/users/{user_ref}/migrate` — riscrive `handle` e `did` sul dominio di destinazione e crea il redirect; solo admin.
- `GET /api/federation/portability/redirects/{old_ref}` — risolve la vecchia ref (`old_ref`, `new_ref`, `target_domain`, `created_at`).

### Chat federata, moderazione ed eventi (Fasi 8 e 9)

- `POST /api/federation/chat/bridge/inbound` — accetta una busta firmata (`message_id`, `node_origin`, `content`, `timestamp`, `signature`), verifica la firma RS256 contro la chiave pubblica del peer, scarta i duplicati per `message_id`, persiste il messaggio e lo diffonde; `403` se il nodo non è consentito o la firma è invalida.
- `POST /api/federation/chat/bridge/outbound` — firma la busta, la accoda in `chat_outbox` con soggetto `clakettes.chat.node.{target_node}` e pubblica tramite il trasporto configurato (`DurableQueueBackend`); `config` restituisce trasporto, stream, algoritmo e subject mapping.
- `GET /api/federation/chat/messages` — cronologia federata deduplicata per `message_id` e ordinata per `timestamp` + `message_id` (filtro `node` opzionale).
- `POST /api/chat/moderation/messages/{message_id}/report`, `PATCH /moderate`, `GET /reports`, `POST/GET /mutes`, `GET /limits` — segnalazioni, nascondi/cancella, mute per utente/canale/nodo, filtro parole bloccate, `disable_chat` per nodo e rate limit di 10 messaggi/60 s per nodo e utente (disattivato con `TESTING=true`).
- `GET /api/federation/events/stream` — SSE con `token` obbligatorio in query (`since` e `limit` opzionali), replay degli ultimi 200 eventi e battito `: ping` ogni 15 s.
- `POST /api/federation/events/publish` — pubblica su un tema derivato da `node`/`entity` (o `topic` esplicito), firma l'invio ai peer con HMAC (`X-Clakettes-Signature`) e omette i nodi con `disable_chat`/`disable_search`; solo admin.
- `GET /api/federation/events/retry-queue` — tentativi in attesa; 3 tentativi con backoff 300 ms → 1,5 s → 5 s.

### Resilienza (Fase 10)

- `GET /api/federation/resilience/health` — stato del nodo, database, numero di nodi e latenza.
- `GET /api/federation/resilience/heartbeat` — aggiorna `last_seen_at` del peer e registra la latenza nelle metriche.
- `GET /api/federation/resilience/metrics` — richieste, successi, errori, tentativi e latenze p50/p95 globali e per nodo.
- `POST /api/federation/resilience/keys/revoke`, `GET /keys/revoked` — revoca immediata delle chiavi per dominio con motivo ed elenco delle revoche; solo admin per revocare.
- `GET /api/federation/resilience/incident-plan` — piano di recupero in caso di compromissione del nodo (8 passi).

### Health e utilità

- `GET /api/federation/health`, `/ping`, `/status`, `/info`, `/version`, `/capabilities`, `/keys`, `/events`, `/peers`, `/links`, `/stats`, `/config`, `/heartbeat`, `/aggregate-nodes`, `/ok`, `/yes`, `/no`, `/maybe`, `/always`, `/never` — placeholder con risposte statiche che non riflettono lo stato reale; non sono endpoint di sondaggio o diagnostica operativi.

> **Avviso:** restituiscono risposte fisse e possono dare una falsa sensazione di sicurezza; per una diagnostica reale, usare gli endpoint di resilienza descritti sopra.

## Regolabilità

- Lo schema è versionato; i nodi dichiarano `schema_version` nel manifesto.
- I campi opzionali (`did`, `handle`) possono essere omessi se il nodo non li supporta.
- La minimizzazione dei dati (`minimize_data`) consente di omettere campi sensibili nel peering.
