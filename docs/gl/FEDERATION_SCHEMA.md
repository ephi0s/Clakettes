# Clakettes Schema v1

[ES](../es/FEDERATION_SCHEMA.md) · [EN](../en/FEDERATION_SCHEMA.md) · [FR](../fr/FEDERATION_SCHEMA.md) · [DE](../de/FEDERATION_SCHEMA.md) · [IT](../it/FEDERATION_SCHEMA.md) · [CA](../ca/FEDERATION_SCHEMA.md) · [EU](../eu/FEDERATION_SCHEMA.md) · [GL](FEDERATION_SCHEMA.md) · [OC](../oc/FEDERATION_SCHEMA.md)

Versión inicial do schema de federación. Define as entidades mínimas intercambiables entre nodos, versionadas mediante `schema_version` no manifesto de cada nodo.

## Modelo de confianza (Fase 2)

A identidade dun nodo é a tupla **(dominio, certificado TLS X.509)**. O peering entre nodos realízase sobre mTLS mutuo: cada nodo valida a cadea de certificados do par contra a súa CA raíz, verifica que o dominio do certificado coincida co declarado, e rexeita certificados self-signed en produción. A rotación e revogación xestiónanse por renovación de certificado.

## Entidades

- `festival`: id, name, edition, created_at, owner_node
- `user`: id, uuid, did, handle, username, node_origin
- `message`: id, sender, recipient, body, created_at, node_origin
- `moderation_report`: id, reporter_node, target_node, target_user_ref, reason, status
- `identity_redirect`: old_ref, new_ref, target_domain, created_at
- `migration_audit`: entity_type, entity_id, action, source_domain, target_domain, details, created_at
- `chat_outbox`: message_id (único), node_origin, subject, payload, signature, status, attempts, last_error, created_at
- `message_report`: reporter_id, message_id, reason, status
- `chat_mute`: user_id, channel_id, node_domain, until, reason

## Campos e restricións

- `uuid`: identificador estable global (UUID v4).
- `did`: identificador descentralizado opcional.
- `handle`: `usuario@instancia` resoluble vía WebFinger.
- `schema_version`: versión do schema declarada polo nodo no seu manifesto (actual: `1`).

## Endpoints de federación

### Identidade e directorio

- `GET /api/federation/manifest` — manifesto do nodo con `schema_version`, `node`, `version`, `capabilities`, `issued_at`, `expires_at`, `signature` e `certificate_chain`. Sinatura RSA-SHA256 coa clave privada do certificado TLS do nodo; o par valida o PEM da cadea e a vixencia de `expires_at` (24 h).
- `GET /api/federation/directory` — lista de nodos confiados (`trusted_nodes`) con `allowed = true`, incluíndo `cert_fingerprint_sha256` (pegada do PEM), `capabilities`, `consent_required`, `minimize_data`.
- `GET/POST /api/federation/nodes` — políticas de nodo (allowlist/blocklist): `consent_required`, `minimize_data`, `import_only`, `disable_chat`, `disable_search`. Só admin; os tres últimos persisten e aplícanse no bridge e no bus de eventos.

### Identidade federada e tokens (Fase 3)

- `GET /api/federation/.well-known/jwks.json` — clave pública RSA do nodo en formato JWKS para validar tokens de federación de pares.
- `POST /api/federation/token` — emite un JWT de federación asinado (RS256). Require identidade de nodo verificada vía mTLS.
- `POST /api/federation/peers/verify` — valida a identidade dun nodo remoto (dominio + CN e PEM do certificado + manifesto asinado).
- `POST /api/federation/peers/{domain}/revoke` — revoga un nodo confiado (admin).
- `GET /api/federation/whoami` — identidade do par (`iss`, `sub`, nodo) só se o seu Bearer JWT valida contra o seu JWKS; 401 se non.

### Usuarios, informes e descubrimento

- `GET /api/federation/users/{ref}` — resolve usuario por `uuid`, `did` ou `handle`. Require peer mTLS verificado.
- `GET /api/federation/.well-known/webfinger` — resolve `acct:user@domain`. Require peer mTLS verificado.
- `POST/GET/PATCH /api/federation/reports` — informe de moderación entre nodos.

### Portabilidade (Fase 7)

- `POST /api/federation/portability/bundles` — xera un bundle do usuario con `bundle_version`, `origin_domain`, `payload`, `signature` (HMAC-SHA256 con `SECRET_KEY`) e `checksum` (SHA-256 do payload canónico).
- `POST /api/federation/portability/imports` — valida sinatura e checksum, comproba a política de orixe (403 se non está permitido), aplica `minimize_data` e rexistra o importado (usuario, curtos, festivais, mensaxes). Os bundles incorporan `contest_type` en cada curto: validase/sanéase `MediaUrl` (URL inválida → `null`), normalízase `contest_type` a `official_section` se non é válido e o checksum do festival inclúeo.
- `POST /api/federation/portability/festivals/{festival_id}/migrate` — transfire a propiedade do festival e os seus curtos a `new_owner_id` de `target_domain` con verificación de checksum; só admin.
- `POST /api/federation/portability/users/{user_ref}/migrate` — reescribe `handle` e `did` ao dominio de destino e crea a redirección; só admin.
- `GET /api/federation/portability/redirects/{old_ref}` — resolve a ref antiga (`old_ref`, `new_ref`, `target_domain`, `created_at`).

### Chat federado, moderación e eventos (Fases 8 e 9)

- `POST /api/federation/chat/bridge/inbound` — acepta un sobre asinado (`message_id`, `node_origin`, `content`, `timestamp`, `signature`), verifica a sinatura RS256 contra a clave pública do par, descarta duplicados por `message_id`, persiste a mensaxe e difúndea; `403` se o nodo non está permitido ou a sinatura é inválida.
- `POST /api/federation/chat/bridge/outbound` — asina o sobre, encólao en `chat_outbox` con suxeito `clakettes.chat.node.{target_node}` e publica polo transporte configurado (`DurableQueueBackend`); `config` devolve transporte, stream, algoritmo e subject mapping.
- `GET /api/federation/chat/messages` — histórico federado deduplicado por `message_id` e ordenado por `timestamp` + `message_id` (filtro opcional `node`).
- `POST /api/chat/moderation/messages/{message_id}/report`, `PATCH /moderate`, `GET /reports`, `POST/GET /mutes`, `GET /limits` — informes, ocultar/borrar, silenciamentos por usuario/canal/nodo, filtro de palabras bloqueadas, `disable_chat` por nodo e rate limit de 10 mensaxes/60 s por nodo e usuario (desactivado con `TESTING=true`).
- `GET /api/federation/events/stream` — SSE con `token` obrigatorio na query (`since` e `limit` opcionais), replay dos últimos 200 eventos e latido `: ping` cada 15 s.
- `POST /api/federation/events/publish` — publica nun tema derivado de `node`/`entity` (ou `topic` explícito), asina o envío a pares con HMAC (`X-Clakettes-Signature`) e omite os nodos con `disable_chat`/`disable_search`; só admin.
- `GET /api/federation/events/retry-queue` — reintentos pendentes; 3 intentos con backoff 300 ms → 1,5 s → 5 s.

### Resiliencia (Fase 10)

- `GET /api/federation/resilience/health` — estado do nodo, base de datos, número de nodos e latencia.
- `GET /api/federation/resilience/heartbeat` — actualiza `last_seen_at` do par e rexistra a latencia nas métricas.
- `GET /api/federation/resilience/metrics` — peticións, acertos, fallos, reintentos e latencias p50/p95 globais e por nodo.
- `POST /api/federation/resilience/keys/revoke`, `GET /keys/revoked` — revogación inmediata de claves por dominio con motivo, e listado de revogacións; só admin para revogar.
- `GET /api/federation/resilience/incident-plan` — plan de recuperación ante compromiso de nodo (8 pasos).

### Health e utilidades

- `GET /api/federation/health`, `/ping`, `/status`, `/info`, `/version`, `/capabilities`, `/keys`, `/events`, `/peers`, `/links`, `/stats`, `/config`, `/heartbeat`, `/aggregate-nodes`, `/ok`, `/yes`, `/no`, `/maybe`, `/always`, `/never` — marcadores de posición (placeholders) con respostas estáticas que non reflicten o estado real; non son endpoints de sondaxe nin diagnóstico operativos.

> **Aviso:** devolven respostas fixas e poden dar unha falsa sensación de seguridade; para un diagnóstico real, utilicen os endpoints de resiliencia descritos arriba.

## Axustabilidade

- O schema é versionado; os nodos declaran `schema_version` no manifesto.
- Os campos opcionais (`did`, `handle`) poden omitirse se o nodo non os soporta.
- A minimización de datos (`minimize_data`) permite omitir campos sensibles no peering.
