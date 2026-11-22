# Protocollo di federazione Clakettes (fasi 2 a 10)

[ES](../es/FEDERATION_PROTOCOL.md) · [EN](../en/FEDERATION_PROTOCOL.md) · [FR](../fr/FEDERATION_PROTOCOL.md) · [DE](../de/FEDERATION_PROTOCOL.md) · [IT](FEDERATION_PROTOCOL.md) · [CA](../ca/FEDERATION_PROTOCOL.md) · [EU](../eu/FEDERATION_PROTOCOL.md) · [GL](../gl/FEDERATION_PROTOCOL.md) · [OC](../oc/FEDERATION_PROTOCOL.md)

Passi per creare un server/client interoperabile:

1. Implementare gli endpoint `/api/federation/*` (vedi `docs/es/FEDERATION_SCHEMA.md`).
2. Configurare TLS obbligatorio tra nodi con mTLS reciproco (Fase 2): certificato emesso da una CA attendibile, nessun self-signed in produzione.
3. Registrare il nodo come attendibile presso ogni peer con cui farà peering (`trusted_nodes`: dominio, impronta SHA-256 del PEM del certificato, CN del subject, capacità, politiche). `POST /api/federation/nodes` persiste `import_only`, `disable_chat` e `disable_search` insieme a `consent_required` e `minimize_data`.
4. Esporre il manifesto su `GET /api/federation/manifest` con `schema_version`, `node`, `version`, `capabilities`, `issued_at`, `expires_at`, `signature` e `certificate_chain`. Il manifesto è firmato in RSA-SHA256 (PKCS#1 v1.5) con la chiave privata del certificato TLS del nodo; il peer valida la firma con il PEM di `certificate_chain` e verifica `expires_at` (24 h).
5. Esporre la chiave pubblica su `GET /api/federation/.well-known/jwks.json` affinché i peer validino i token di federazione.
6. Validare i token dei peer tramite JWKS: un nodo remoto che chiama un endpoint protetto deve presentare un Bearer JWT firmato (RS256) il cui `iss` sia il suo dominio e la cui firma sia validata contro il suo JWKS. `GET /api/federation/whoami` restituisce l'identità del peer solo quando tale JWT viene validato (401 altrimenti).
7. Risolvere gli utenti remoti tramite `GET /api/federation/users/{ref}` e `GET /api/federation/.well-known/webfinger` (entrambi richiedono peer mTLS verificato solo quando `MTLS_REQUIRED=true`; per impostazione predefinita `False`).
8. Usare Clakettes Schema v1 per lo scambio dati.
9. Portare identità e dati con `POST /api/federation/portability/bundles` e `/imports`, migrare con `/festivals/{id}/migrate` e `/users/{ref}/migrate`, e risolvere le vecchie ref con `GET /redirects/{ref}`.
10. Consegnare la chat tramite il bridge firmato `/api/federation/chat/bridge/{inbound,outbound,config}`; la cronologia si consulta su `/api/federation/chat/messages`, con deduplicazione per `message_id` e ordinamento per `timestamp` + `message_id`. La coda durable `chat_outbox` consente un trasporto intercambiabile (dettaglio in `docs/es/FEDERATION_CHAT_BROKER.md`).
11. Propagare le modifiche tramite il bus degli eventi: `GET /api/federation/events/stream` (SSE con `since` e battito), `POST /publish` e `GET /retry-queue` (3 tentativi, backoff 300 ms → 1,5 s → 5 s).
12. Vigilare sulla salute del peering con `/api/federation/resilience/{health,heartbeat,metrics,keys/revoke,keys/revoked,incident-plan}`; `metrics` espone p50/p95, latenza, errori e tentativi.
13. Verificare la conformità di un nodo terzo con `python tools/federation_conformance.py <url> [--json]` (1 in caso di errori critici/alti).

## Motivazione

Il protocollo permette a nodi indipendenti di scambiare festival, utenti e messaggi senza perdere identità o tracciabilità.

## Adeguatezze

- `consent_required`: richiede consenso esplicito prima di federare i dati di un nodo.
- `import_only`: federazione unidirezionale (solo import, nessun export).
- `disable_chat`/`disable_search`: permessi per funzione per nodo.
- `minimize_data`: condividere solo il necessario nel peering.

## Endpoint chiave

| Endpoint | Metodo | Descrizione |
|---|---|---|
| `/api/federation/manifest` | GET | Manifesto firmato RSA-SHA256 con `expires_at` e `certificate_chain` |
| `/api/federation/directory` | GET | Directory dei nodi attendibili |
| `/api/federation/nodes` | GET/POST | Politiche allowlist/blocklist (`import_only`, `disable_chat`, `disable_search`) |
| `/api/federation/whoami` | GET | Identità del peer, con validazione del suo JWT contro il suo JWKS |
| `/api/federation/.well-known/jwks.json` | GET | Chiave pubblica JWKS del nodo |
| `/api/federation/token` | POST | Emissione di JWT di federazione (RS256) |
| `/api/federation/peers/verify` | POST | Verifica dell'identità di un nodo remoto (CN e PEM del certificato) |
| `/api/federation/peers/{domain}/revoke` | POST | Revoca di un nodo attendibile (admin) |
| `/api/federation/users/{ref}` | GET | Risoluzione di utente remoto (mTLS) |
| `/api/federation/.well-known/webfinger` | GET | WebFinger `acct:user@domain` (mTLS) |
| `/api/federation/reports` | POST/GET/PATCH | Segnalazioni di moderazione tra nodi |
| `/api/federation/portability/bundles`, `/imports` | POST | Esportazione e importazione di bundle firmati |
| `/api/federation/portability/festivals/{id}/migrate`, `/users/{ref}/migrate` | POST | Migrazione di festival e identità utente (admin) |
| `/api/federation/portability/redirects/{ref}` | GET | Risoluzione della vecchia ref dopo la migrazione |
| `/api/federation/chat/bridge/inbound`, `/outbound`, `/config` | POST/GET | Bridge della chat firmato e sua configurazione |
| `/api/federation/chat/messages` | GET | Cronologia federata, deduplicata e ordinata |
| `/api/chat/moderation/*` | POST/PATCH/GET | Segnalazioni, mute, filtro e limite della chat |
| `/api/federation/events/stream`, `/publish`, `/retry-queue` | GET/POST | SSE con `since` e battito, pubblicazione e tentativi |
| `/api/federation/resilience/health`, `/heartbeat`, `/metrics` | GET | Salute, battito e metriche reali p50/p95 |
| `/api/federation/resilience/keys/revoke`, `/keys/revoked`, `/incident-plan` | POST/GET | Revoca chiavi e piano incidente |
