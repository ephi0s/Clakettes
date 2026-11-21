# Sicurezza federata (fasi 2 a 10)

## Modello di fiducia

- Identità del nodo = dominio + certificato TLS X.509.
- Peering reciproco tramite mTLS con certificati di dominio (CA pubblica o privata): vengono validati il CN del subject e il PEM del certificato, non solo il dominio dichiarato.
- TLS obbligatorio tra nodi; validazione rigorosa dei certificati nel peering (nessun self-signed in prod).
- L'identità è memorizzata in `trusted_nodes` (dominio, impronta SHA-256 del PEM, CN del subject, CA emittente, validità, politiche).
- Ogni nodo espone un manifesto firmato in RSA-SHA256 con la chiave privata del proprio certificato TLS; i peer validano la firma contro il PEM di `certificate_chain` e verificano `expires_at` (24 h).

## Rotazione e revoca

- La rotazione è gestita tramite rinnovo del certificato: al rinnovo, l'impronta in `trusted_nodes` viene aggiornata senza rompere il peering (la radice di fiducia è la CA, non il singolo certificato).
- Un nodo compromesso viene revocato impostando `allowed = false` in `trusted_nodes` (`POST /api/federation/peers/{domain}/revoke`, solo admin) o invalidando il suo certificato nella CRL della CA.
- La revoca amministrativa è immediata: il successivo handshake mTLS fallisce.
- La revoca d'emergenza è gestita anche da `POST /api/federation/resilience/keys/revoke` (solo admin, con motivo) e consultata su `GET /keys/revoked`; `GET /incident-plan` descrive gli 8 passi di risposta a una compromissione.

## Controlli di accesso

- Rate limiting globale: 100 req/60s per IP (bucket `middleware:`); `/dav` ha 600/60s.
- Rate limiting per endpoint sensibile: login 5/300s per IP, refresh 20/60s per IP, federation 60/60s per IP; chat 10 messaggi/60 s per nodo e utente (disattivato con `TESTING=true`).
- Gli endpoint di federazione che espongono dati utente (`/users/{ref}`, `/.well-known/webfinger`) richiedono peer mTLS verificato.
- `GET /api/federation/whoami` richiede un Bearer JWT di federazione (RS256) validato contro il JWKS dell'emittente; senza token valido risponde 401.
- Gli endpoint di amministrazione dei nodi (`/nodes`, `/peers/{domain}/revoke`, migrazioni di portabilità, `events/publish`, `events/retry-queue`, `keys/revoke`) richiedono il ruolo admin; la moderazione di canale richiede admin o moderatore del canale.
- Lo stream SSE degli eventi richiede un token di accesso valido in `?token=`; l'evento si consulta con `since` e il replay è limitato agli ultimi 200 eventi.

## Integrità, chat ed eventi

- I bundle di portabilità recano una `signature` HMAC-SHA256 con `SECRET_KEY` e un `checksum` SHA-256 sul payload canonico; l'import respinge bundle invalidi (400) e origini non consentite (403) e applica `minimize_data` per omettere campi sensibili.
- Il bridge della chat firma in RS256 i campi canonici della busta (`message_id`, `node_origin`, `content`, `timestamp`, …); il ricevente scarica la chiave pubblica del peer e verifica la firma prima di persistere. La tabella `chat_outbox` impone l'unicità per `message_id`, così un reinvio viene risposto come `duplicate`; la cronologia è ordinata per `timestamp` + `message_id`.
- Il trasporto è intercambiabile tramite la coda durable (`DurableQueueBackend` su `chat_outbox`), con tentativo e backoff; la decisione sul broker (NATS JetStream, WebSocket di bordo e fallback mononodo) è in `docs/es/FEDERATION_CHAT_BROKER.md`.
- La moderazione copre segnalazioni, nascondere/cancellare messaggi, mute con validità e ambito per canale o nodo, filtro parole bloccate e `disable_chat` per nodo (`POST /api/chat/moderation/*`). Si completa con il limite di 10 messaggi/60 s per nodo e utente.
- Gli eventi verso i peer sono firmati con HMAC-SHA256 nell'header `X-Clakettes-Signature` e propagati solo ai nodi consentiti; gli errori entrano nella coda di ripetizione (3 tentativi, backoff 300 ms → 1,5 s → 5 s) visibile su `/api/federation/events/retry-queue`.
- Le politiche `disable_chat` e `disable_search` vengono valutate prima di applicare eventi o messaggi in entrata, e `import_only` limita l'export; `GET /api/federation/resilience/metrics` espone p50/p95, latenza, errori e tentativi per vigilare sul peering.

## Adeguatezze

- `allowlist`/`blocklist` per nodo (`node_policies` / `trusted_nodes`).
- Rate limiting e anti-flood al bordo della federazione.
- Propagazione delle segnalazioni di moderazione tra nodi.
- `consent_required`: richiede consenso esplicito prima di federare i dati di un nodo.
- `import_only`: federazione unidirezionale (solo import, nessun export).
- `disable_chat`/`disable_search`: permessi per funzione per nodo.
- `minimize_data`: condividere solo il necessario nel peering.

## Riferimenti

- `docs/es/MODELO_CONFIANZA_NODOS.md` — progettazione dettagliata del modello di fiducia e delle tabelle del database.
- `docs/es/FEDERATION_PROTOCOL.md` — passi di interoperabilità nodo-server/client (fasi 2 a 10).
- `docs/es/FEDERATION_SCHEMA.md` — Clakettes Schema v1, entità ed endpoint di federazione.
- `docs/es/FEDERATION_CHAT_BROKER.md` — decisione sul broker per chat ed eventi tra nodi.
- `docs/es/AMENAZAS_NODOS_FEDERACION.md` — minacce per nodo e rischi residui.
