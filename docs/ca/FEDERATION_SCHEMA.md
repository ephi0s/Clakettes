# Clakettes Schema v1

Versió inicial de l'esquema de federació. Defineix les entitats mínimes intercanviables entre nodes, versionades mitjançant `schema_version` al manifest de cada node.

## Model de confiança (Fase 2)

La identitat d'un node és la tupla **(domini, certificat TLS X.509)**. El peering entre nodes es fa sobre mTLS mutu: cada node valida la cadena de certificats del pare contra la seva CA arrel, verifica que el domini del certificat coincideixi amb el declarat, i rebutja certificats self-signed en producció. La rotació i revocació es gestionen per renovació de certificat.

## Entitats

- `festival`: id, name, edition, created_at, owner_node
- `user`: id, uuid, did, handle, username, node_origin
- `message`: id, sender, recipient, body, created_at, node_origin
- `moderation_report`: id, reporter_node, target_node, target_user_ref, reason, status
- `identity_redirect`: old_ref, new_ref, target_domain, created_at
- `migration_audit`: entity_type, entity_id, action, source_domain, target_domain, details, created_at
- `chat_outbox`: message_id (únic), node_origin, subject, payload, signature, status, attempts, last_error, created_at
- `message_report`: reporter_id, message_id, reason, status
- `chat_mute`: user_id, channel_id, node_domain, until, reason

## Camps i restriccions

- `uuid`: identificador estable global (UUID v4).
- `did`: identificador descentralitzat opcional.
- `handle`: `usuari@instancia` resoluble via WebFinger.
- `schema_version`: versió de l'esquema declarada pel node al seu manifest (actual: `1`).

## Endpoints de federació

### Identitat i directori

- `GET /api/federation/manifest` — manifest del node amb `schema_version`, `node`, `version`, `capabilities`, `issued_at`, `expires_at`, `signature` i `certificate_chain`. Signatura RSA-SHA256 amb la clau privada del certificat TLS del node; el pare valida el PEM de la cadena i la vigència de `expires_at` (24 h).
- `GET /api/federation/directory` — llista de nodes confiats (`trusted_nodes`) amb `allowed = true`, incloent `cert_fingerprint_sha256` (huella del PEM), `capabilities`, `consent_required`, `minimize_data`.
- `GET/POST /api/federation/nodes` — polítiques de node (allowlist/blocklist): `consent_required`, `minimize_data`, `import_only`, `disable_chat`, `disable_search`. Només admin; els tres últims es desaven i s'apliquen al bridge i al bus d'esdeveniments.

### Identitat federada i tokens (Fase 3)

- `GET /api/federation/.well-known/jwks.json` — clau pública RSA del node en format JWKS per validar tokens de federació de pares.
- `POST /api/federation/token` — emet un JWT de federació signat (RS256). Requereix identitat de node verificada via mTLS.
- `POST /api/federation/peers/verify` — valida la identitat d'un node remot (domini + CN i PEM del certificat + manifest signat).
- `POST /api/federation/peers/{domain}/revoke` — revoca un node confiat (admin).
- `GET /api/federation/whoami` — identitat del pare (`iss`, `sub`, node) només si el seu Bearer JWT valida contra el seu JWKS; 401 si no.

### Usuaris, reportes i descobriment

- `GET /api/federation/users/{ref}` — resol usuaris per `uuid`, `did` o `handle`. Requereix peer mTLS verificat.
- `GET /api/federation/.well-known/webfinger` — resol `acct:user@domain`. Requereix peer mTLS verificat.
- `POST/GET/PATCH /api/federation/reports` — reporte de moderació entre nodes.

### Portabilitat (Fase 7)

- `POST /api/federation/portability/bundles` — genera un bundle de l'usuari amb `bundle_version`, `origin_domain`, `payload`, `signature` (HMAC-SHA256 amb `SECRET_KEY`) i `checksum` (SHA-256 del payload canònic).
- `POST /api/federation/portability/imports` — valida signatura i checksum, comprova la política d'origen (403 si no està permès), aplica `minimize_data` i registra l'importat (usuari, curts, festivals, missatges).
- `POST /api/federation/portability/festivals/{festival_id}/migrate` — transfereix la propietat del festival i els seus curts a `new_owner_id` de `target_domain` amb verificació de checksum; només admin.
- `POST /api/federation/portability/users/{user_ref}/migrate` — reescriu `handle` i `did` al domini de destinació i crea la redirecció; només admin.
- `GET /api/federation/portability/redirects/{old_ref}` — resol la ref antiga (`old_ref`, `new_ref`, `target_domain`, `created_at`).

### Xat federat, moderació i esdeveniments (Fases 8 i 9)

- `POST /api/federation/chat/bridge/inbound` — accepta un sobre signat (`message_id`, `node_origin`, `content`, `timestamp`, `signature`), verifica la signatura RS256 contra la clau pública del pare, descarta duplicats per `message_id`, desa el missatge i el difon; `403` si el node no està permès o la signatura és invàlida.
- `POST /api/federation/chat/bridge/outbound` — signa el sobre, l'encua a `chat_outbox` amb subjecte `clakettes.chat.node.{target_node}` i publica pel transport configurat (`DurableQueueBackend`); `config` retorna transport, stream, algorisme i subject mapping.
- `GET /api/federation/chat/messages` — historial federat deduplicat per `message_id` i ordenat per `timestamp` + `message_id` (filtre opcional `node`).
- `POST /api/chat/moderation/messages/{message_id}/report`, `PATCH /moderate`, `GET /reports`, `POST/GET /mutes`, `GET /limits` — reportes, amagar/borrar, silenciaments per usuari/canal/node, filtre de paraules bloquejades, `disable_chat` per node i rate limit de 10 missatges/60 s per node i usuari (desactivat amb `TESTING=true`).
- `GET /api/federation/events/stream` — SSE amb `since`, `token`, `limit` opcional, replay dels últims 200 esdeveniments i batec `: ping` cada 15 s.
- `POST /api/federation/events/publish` — publica en un tema derivat de `node`/`entity` (o `topic` explícit), signa l'enviament a pares amb HMAC (`X-Clakettes-Signature`) i omet els nodes amb `disable_chat`/`disable_search`; només admin.
- `GET /api/federation/events/retry-queue` — reintents pendents; 3 intents amb backoff 300 ms → 1,5 s → 5 s.

### Resiliència (Fase 10)

- `GET /api/federation/resilience/health` — estat del node, base de dades, nombre de nodes i latència.
- `GET /api/federation/resilience/heartbeat` — actualitza `last_seen_at` del pare i registra la latència a les mètriques.
- `GET /api/federation/resilience/metrics` — peticions, encerts, fallades, reintents i latències p50/p95 globals i per node.
- `POST /api/federation/resilience/keys/revoke`, `GET /keys/revoked` — revocació immediata de claus per domini amb motiu, i llistat de revocacions; només admin per revocar.
- `GET /api/federation/resilience/incident-plan` — pla de recuperació davant compromís de node (8 passos).

### Health i utilitats

- `GET /api/federation/health`, `/ping`, `/status`, `/info`, `/version`, `/capabilities`, `/keys`, `/events`, `/peers`, `/links`, `/stats`, `/config`, `/heartbeat`, `/aggregate-nodes`, `/ok`, `/yes`, `/no`, `/maybe`, `/always`, `/never` — endpoints de sondeig i diagnòstic.

## Ajustabilitat

- L'esquema és versionat; els nodes declaren `schema_version` al manifest.
- Els camps opcionals (`did`, `handle`) poden omitir-se si el node no els suporta.
- La minimització de dades (`minimize_data`) permet ometre camps sensibles en el peering.
