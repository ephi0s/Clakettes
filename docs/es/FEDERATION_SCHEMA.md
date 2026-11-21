# Clakettes Schema v1

Versión inicial del schema de federación. Define las entidades mínimas intercambiables entre nodos, versionado mediante `schema_version` en el manifiesto de cada nodo.

## Modelo de confianza (Fase 2)

La identidad de un nodo es la tupla **(dominio, certificado TLS X.509)**. El peering entre nodos se realiza sobre mTLS mutuo: cada nodo valida la cadena de certificados del par contra su CA raíz, verifica que el dominio del cert coincida con el declarado, y rechaza certificados self-signed en producción. La rotación y revocación se gestionan por renovación de certificado.

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

## Campos y restricciones

- `uuid`: identificador estable global (UUID v4).
- `did`: identificador descentralizado opcional.
- `handle`: `usuario@instancia` resoluble vía WebFinger.
- `schema_version`: versión del schema declarada por el nodo en su manifiesto (actual: `1`).

## Endpoints de federación

### Identidad y directorio

- `GET /api/federation/manifest` — manifiesto del nodo con `schema_version`, `node`, `version`, `capabilities`, `issued_at`, `expires_at`, `signature` y `certificate_chain`. Firma RSA-SHA256 con la clave privada del certificado TLS del nodo; el par valida el PEM de la cadena y la vigencia de `expires_at` (24 h).
- `GET /api/federation/directory` — lista de nodos confiados (`trusted_nodes`) con `allowed = true`, incluyendo `cert_fingerprint_sha256` (huella del PEM), `capabilities`, `consent_required`, `minimize_data`.
- `GET/POST /api/federation/nodes` — políticas de nodo (allowlist/blocklist): `consent_required`, `minimize_data`, `import_only`, `disable_chat`, `disable_search`. Solo admin; los tres últimos se persisten y se aplican en el bridge y en el bus de eventos.

### Identidad federada y tokens (Fase 3)

- `GET /api/federation/.well-known/jwks.json` — clave pública RSA del nodo en formato JWKS para validar tokens de federación de pares.
- `POST /api/federation/token` — emite un JWT de federación firmado (RS256). Requiere identidad de nodo verificada vía mTLS.
- `POST /api/federation/peers/verify` — valida la identidad de un nodo remoto (dominio + CN y PEM del certificado + manifiesto firmado).
- `POST /api/federation/peers/{domain}/revoke` — revoca un nodo confiado (admin).
- `GET /api/federation/whoami` — identidad del par (`iss`, `sub`, nodo) solo si su Bearer JWT valida contra su JWKS; 401 si no.

### Usuarios, reportes y descubrimento

- `GET /api/federation/users/{ref}` — resuelve usuario por `uuid`, `did` o `handle`. Requiere peer mTLS verificado.
- `GET /api/federation/.well-known/webfinger` — resuelve `acct:user@domain`. Requiere peer mTLS verificado.
- `POST/GET/PATCH /api/federation/reports` — reporte de moderación entre nodos.

### Portabilidad (Fase 7)

- `POST /api/federation/portability/bundles` — genera un bundle del usuario con `bundle_version`, `origin_domain`, `payload`, `signature` (HMAC-SHA256 con `SECRET_KEY`) y `checksum` (SHA-256 del payload canónico).
- `POST /api/federation/portability/imports` — valida firma y checksum, comprueba la política de origen (403 si no está permitido), aplica `minimize_data` y registra lo importado (usuario, cortos, festivales, mensajes).
- `POST /api/federation/portability/festivals/{festival_id}/migrate` — transfiere la propiedad del festival y sus cortos a `new_owner_id` de `target_domain` con verificación de checksum; solo admin.
- `POST /api/federation/portability/users/{user_ref}/migrate` — reescribe `handle` y `did` al dominio de destino y crea la redirección; solo admin.
- `GET /api/federation/portability/redirects/{old_ref}` — resuelve la ref antigua (`old_ref`, `new_ref`, `target_domain`, `created_at`).

### Chat federado, moderación y eventos (Fases 8 y 9)

- `POST /api/federation/chat/bridge/inbound` — acepta un sobre firmado (`message_id`, `node_origin`, `content`, `timestamp`, `signature`), verifica la firma RS256 contra la clave pública del par, descarta duplicados por `message_id`, persiste el mensaje y lo difunde; `403` si el nodo no está permitido o la firma es inválida.
- `POST /api/federation/chat/bridge/outbound` — firma el sobre, lo encola en `chat_outbox` con sujeto `clakettes.chat.node.{target_node}` y publica por el transporte configurado (`DurableQueueBackend`); `config` devuelve transporte, stream, algoritmo y subject mapping.
- `GET /api/federation/chat/messages` — historial federado deduplicado por `message_id` y ordenado por `timestamp` + `message_id` (filtro opcional `node`).
- `POST /api/chat/moderation/messages/{message_id}/report`, `PATCH /moderate`, `GET /reports`, `POST/GET /mutes`, `GET /limits` — reportes, ocultar/borrar, mutes por usuario/canal/nodo, filtro de palabras bloqueadas, `disable_chat` por nodo y rate limit de 10 mensajes/60 s por nodo y usuario (desactivado con `TESTING=true`).
- `GET /api/federation/events/stream` — SSE con `since`, `token`, `limit` opcional, replay de los últimos 200 eventos y latido `: ping` cada 15 s.
- `POST /api/federation/events/publish` — publica en un tema derivado de `node`/`entity` (o `topic` explícito), firma el envío a pares con HMAC (`X-Clakettes-Signature`) y omite los nodos con `disable_chat`/`disable_search`; solo admin.
- `GET /api/federation/events/retry-queue` — reintentos pendientes; 3 intentos con backoff 300 ms → 1,5 s → 5 s.

### Resiliencia (Fase 10)

- `GET /api/federation/resilience/health` — estado del nodo, base de datos, número de nodos y latencia.
- `GET /api/federation/resilience/heartbeat` — actualiza `last_seen_at` del par y registra la latencia en métricas.
- `GET /api/federation/resilience/metrics` — peticiones, aciertos, fallos, reintentos y latencias p50/p95 globales y por nodo.
- `POST /api/federation/resilience/keys/revoke`, `GET /keys/revoked` — revocación inmediata de claves por dominio con motivo, y listado de revocaciones; solo admin para revocar.
- `GET /api/federation/resilience/incident-plan` — plan de recuperación ante compromiso de nodo (8 pasos).

### Health y utilidades

- `GET /api/federation/health`, `/ping`, `/status`, `/info`, `/version`, `/capabilities`, `/keys`, `/events`, `/peers`, `/links`, `/stats`, `/config`, `/heartbeat`, `/aggregate-nodes`, `/ok`, `/yes`, `/no`, `/maybe`, `/always`, `/never` — endpoints de sondeo y diagnóstico.

## Ajustabilidad

- El schema es versionado; los nodos declaran `schema_version` en el manifest.
- Campos opcionales (`did`, `handle`) pueden omitirse si el nodo no los soporta.
- La minimización de datos (`minimize_data`) permite omitir campos sensibles en peering.
