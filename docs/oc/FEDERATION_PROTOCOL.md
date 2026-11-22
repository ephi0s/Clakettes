# Protocòl de federacion Clakettes (fases 2 a 10)

[ES](../es/FEDERATION_PROTOCOL.md) · [EN](../en/FEDERATION_PROTOCOL.md) · [FR](../fr/FEDERATION_PROTOCOL.md) · [DE](../de/FEDERATION_PROTOCOL.md) · [IT](../it/FEDERATION_PROTOCOL.md) · [CA](../ca/FEDERATION_PROTOCOL.md) · [EU](../eu/FEDERATION_PROTOCOL.md) · [GL](../gl/FEDERATION_PROTOCOL.md) · [OC](FEDERATION_PROTOCOL.md)

Estapas per crear un servidor/client interoperable:

1. Implementar los endpoints `/api/federation/*` (vejatz `docs/es/FEDERATION_SCHEMA.md`).
2. Configurar TLS obligatòri entre noses amb mTLS mutu (Fasa 2): certificat emés per una CA de fisança, sens self-signed en produccion.
3. Enregistrar lo nose coma fisable a cada par amb lo qual farà peering (`trusted_nodes`: domeni, emprenta SHA-256 del PEM del certificat, CN del subjècte, capacitats, politicas). `POST /api/federation/nodes` serva `import_only`, `disable_chat` e `disable_search` amb `consent_required` e `minimize_data`.
4. Expausar lo manifest a `GET /api/federation/manifest` amb `schema_version`, `node`, `version`, `capabilities`, `issued_at`, `expires_at`, `signature` e `certificate_chain`. Lo manifest es signat en RSA-SHA256 (PKCS#1 v1.5) amb la clau privada del certificat TLS del nose; lo par valida la signatura amb lo PEM de `certificate_chain` e verifica `expires_at` (24 h).
5. Expausar la clau publica a `GET /api/federation/.well-known/jwks.json` per que los pares validen los tokens de federacion.
6. Validar los tokens dels pares via JWKS: un nose remote que apela un endpoint protegit deu presentar un Bearer JWT signat (RS256) que son `iss` siá son domeni e que sa signatura siá validada contra son JWKS. `GET /api/federation/whoami` torna l'identitat del par solament quand aqueste JWT valida (401 autrament).
7. Resòlver los usagis remots via `GET /api/federation/users/{ref}` e `GET /api/federation/.well-known/webfinger` (ambdos demandan un peer mTLS verificat sonque quand `MTLS_REQUIRED=true`; per defaut `False`).
8. Utilizar Clakettes Schema v1 per l'escambi de donadas.
9. Portar identitat e donadas amb `POST /api/federation/portability/bundles` e `/imports` (signatura HMAC-SHA256 e checksum), migrar amb `/festivals/{id}/migrate` e `/users/{ref}/migrate`, e resòlver las refs ancianas amb `GET /redirects/{ref}`.
10. Liurar lo chat pel bridge signat `/api/federation/chat/bridge/{inbound,outbound,config}`; l'istoric se consulta a `/api/federation/chat/messages`, amb deduplicacion per `message_id` e ordre per `timestamp` + `message_id`. La còda durabla `chat_outbox` permet un transpòrt intercambiable (detalh dins `docs/es/FEDERATION_CHAT_BROKER.md`).
11. Propagar los cambiaments pel bus d'eveniments: `GET /api/federation/events/stream` (SSE amb `since` e batement), `POST /publish` e `GET /retry-queue` (3 ensajos, backoff 300 ms → 1,5 s → 5 s).
12. Vigilar la santat del peering amb `/api/federation/resilience/{health,heartbeat,metrics,keys/revoke,keys/revoked,incident-plan}`; `metrics` expausa p50/p95, laténcia, fracasses e reensajos.
13. Verificar la conformitat d'un nose tèrç amb `python tools/federation_conformance.py <url> [--json]` (1 se i a de fracasses critics/ausats).

## Motivacion

Lo protocòl permet a de noses independents d'escambiar festivals, usagis e messatges sens perdre identitat ni traçabilitat.

## Ajustaments

- `consent_required`: demanda un consentiment explicit abans de federar las donadas d'un nose.
- `import_only`: federacion unidireccionala (solament importar, non exportar).
- `disable_chat`/`disable_search`: permission per foncion per nose.
- `minimize_data`: non partejar mai que lo necessari dins lo peering.

## Endpoints claus

| Endpoint | Metòde | Descripcion |
|---|---|---|
| `/api/federation/manifest` | GET | Manifest signat RSA-SHA256 amb `expires_at` e `certificate_chain` |
| `/api/federation/directory` | GET | Directòri dels noses fisables |
| `/api/federation/nodes` | GET/POST | Politicas d'allowlist/blocklist (`import_only`, `disable_chat`, `disable_search`) |
| `/api/federation/whoami` | GET | Identitat del par, en validant son JWT contra son JWKS |
| `/api/federation/.well-known/jwks.json` | GET | Clau publica JWKS del nose |
| `/api/federation/token` | POST | Emission de JWT de federacion (RS256) |
| `/api/federation/peers/verify` | POST | Verificacion d'identitat de nose remote (CN e PEM del certificat) |
| `/api/federation/peers/{domain}/revoke` | POST | Revocacion de nose fisable (admin) |
| `/api/federation/users/{ref}` | GET | Resolucion d'usagi remote (mTLS) |
| `/api/federation/.well-known/webfinger` | GET | WebFinger `acct:user@domain` (mTLS) |
| `/api/federation/reports` | POST/GET/PATCH | Rapòrts de moderacion entre noses |
| `/api/federation/portability/bundles`, `/imports` | POST | Exportacion e importacion de bundles signats |
| `/api/federation/portability/festivals/{id}/migrate`, `/users/{ref}/migrate` | POST | Migracion dels festivals e de l'identitat d'usagi (admin) |
| `/api/federation/portability/redirects/{ref}` | GET | Resolucion de la ref anciana aprèp la migracion |
| `/api/federation/chat/bridge/inbound`, `/outbound`, `/config` | POST/GET | Bridge de chat signat e sa configuracion |
| `/api/federation/chat/messages` | GET | Istoric federat, deduplicat e ordenat |
| `/api/chat/moderation/*` | POST/PATCH/GET | Rapòrts, silencis, filtre e limita de chat |
| `/api/federation/events/stream`, `/publish`, `/retry-queue` | GET/POST | SSE amb `since` e batement, publicacion e reensajos |
| `/api/federation/resilience/health`, `/heartbeat`, `/metrics` | GET | Santat, batement e metricas realas p50/p95 |
| `/api/federation/resilience/keys/revoke`, `/keys/revoked`, `/incident-plan` | POST/GET | Revocacion de claus e plan d'incident |
