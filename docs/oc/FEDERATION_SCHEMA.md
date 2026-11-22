# Clakettes Schema v1

[ES](../es/FEDERATION_SCHEMA.md) · [EN](../en/FEDERATION_SCHEMA.md) · [FR](../fr/FEDERATION_SCHEMA.md) · [DE](../de/FEDERATION_SCHEMA.md) · [IT](../it/FEDERATION_SCHEMA.md) · [CA](../ca/FEDERATION_SCHEMA.md) · [EU](../eu/FEDERATION_SCHEMA.md) · [GL](../gl/FEDERATION_SCHEMA.md) · [OC](FEDERATION_SCHEMA.md)

Version iniciala de l'esquèma de federacion. Defineix las entitats minimalas intercambiablas entre noses, versionadas amb `schema_version` dins lo manifest de cada nose.

## Modèl de fisança (Fasa 2)

L'identitat d'un nose es la tupa **(domeni, certificat TLS X.509)**. Lo peering entre noses se fa sus mTLS mutu: cada nose valida la cadena de certificats del par contra sa CA racina, verifica que lo domeni del certificat corresponda al declarat, e rebuta los certificats self-signed en produccion. La rotacion e la revocacion se gestionan per renovacion del certificat.

## Entitats

- `festival`: id, name, edition, created_at, owner_node
- `user`: id, uuid, did, handle, username, node_origin
- `message`: id, sender, recipient, body, created_at, node_origin
- `moderation_report`: id, reporter_node, target_node, target_user_ref, reason, status
- `identity_redirect`: old_ref, new_ref, target_domain, created_at
- `migration_audit`: entity_type, entity_id, action, source_domain, target_domain, details, created_at
- `chat_outbox`: message_id (unic), node_origin, subject, payload, signature, status, attempts, last_error, created_at
- `message_report`: reporter_id, message_id, reason, status
- `chat_mute`: user_id, channel_id, node_domain, until, reason

## Camps e restriccions

- `uuid`: identificador estable global (UUID v4).
- `did`: identificador descentralizat opcional.
- `handle`: `usagi@instància` resoluble via WebFinger.
- `schema_version`: version de l'esquèma declarada pel nose dins son manifest (actuala: `1`).

## Endpoints de federacion

### Identitat e directòri

- `GET /api/federation/manifest` — manifest del nose amb `schema_version`, `node`, `version`, `capabilities`, `issued_at`, `expires_at`, `signature` e `certificate_chain`. Signatura RSA-SHA256 amb la clau privada del certificat TLS del nose; lo par valida lo PEM de la cadena e la validitat de `expires_at` (24 h).
- `GET /api/federation/directory` — lista dels noses fisables (`trusted_nodes`) amb `allowed = true`, compres `cert_fingerprint_sha256` (emprenta del PEM), `capabilities`, `consent_required`, `minimize_data`.
- `GET/POST /api/federation/nodes` — politicas de nose (allowlist/blocklist): `consent_required`, `minimize_data`, `import_only`, `disable_chat`, `disable_search`. Solament admin; los tres darrièrs son servats e aplicats al bridge e al bus d'eveniments.

### Identitat federada e tokens (Fasa 3)

- `GET /api/federation/.well-known/jwks.json` — clau publica RSA del nose en format JWKS per validar los tokens de federacion dels pares.
- `POST /api/federation/token` — emet un JWT de federacion signat (RS256). Demanda una identitat de nose verificada via mTLS.
- `POST /api/federation/peers/verify` — valida l'identitat d'un nose remote (domeni + CN e PEM del certificat + manifest signat).
- `POST /api/federation/peers/{domain}/revoke` — revoca un nose fisable (admin).
- `GET /api/federation/whoami` — identitat del par (`iss`, `sub`, nose) solament se son Bearer JWT valida contra son JWKS; 401 autrament.

### Usagis, rapòrts e descobèrta

- `GET /api/federation/users/{ref}` — resòlv usagi per `uuid`, `did` o `handle`. Demanda un peer mTLS verificat.
- `GET /api/federation/.well-known/webfinger` — resòlv `acct:user@domain`. Demanda un peer mTLS verificat.
- `POST/GET/PATCH /api/federation/reports` — rapòrt de moderacion entre noses.

### Portabilitat (Fasa 7)

- `POST /api/federation/portability/bundles` — genèra un bundle de l'usagi amb `bundle_version`, `origin_domain`, `payload`, `signature` (HMAC-SHA256 amb `SECRET_KEY`) e `checksum` (SHA-256 del payload canonic).
- `POST /api/federation/portability/imports` — valida signatura e checksum, verifica la politica d'origina (403 se non es autorizat), aplica `minimize_data` e enregistra l'importat (usagi, corts, festivals, messatges). Los bundles incorporan `contest_type` dins cada cort: se valida/sanea `MediaUrl` (URL invalida → `null`), se normaliza `contest_type` a `official_section` se non es valid e lo checksum del festival l'inclutz.
- `POST /api/federation/portability/festivals/{festival_id}/migrate` — transferís la proprietat del festival e sos corts a `new_owner_id` de `target_domain` amb verificacion de checksum; solament admin.
- `POST /api/federation/portability/users/{user_ref}/migrate` — reescriu `handle` e `did` al domeni de destinacion e crea la redireccion; solament admin.
- `GET /api/federation/portability/redirects/{old_ref}` — resòlv la ref anciana (`old_ref`, `new_ref`, `target_domain`, `created_at`).

### Chat federat, moderacion e eveniments (Fasas 8 e 9)

- `POST /api/federation/chat/bridge/inbound` — accepta una envelopa signada (`message_id`, `node_origin`, `content`, `timestamp`, `signature`), verifica la signatura RS256 contra la clau publica del par, escarta los doblons per `message_id`, serva lo messatge e lo difusa; `403` se lo nose non es autorizat o la signatura es invalida.
- `POST /api/federation/chat/bridge/outbound` — signa l'envelopa, la met en còda dins `chat_outbox` amb subjècte `clakettes.chat.node.{target_node}` e publica pel transpòrt configurat (`DurableQueueBackend`); `config` torna transpòrt, stream, algoritme e correspodendas de subjèctes.
- `GET /api/federation/chat/messages` — istoric federat deduplicat per `message_id` e ordenat per `timestamp` + `message_id` (filtre opcional `node`).
- `POST /api/chat/moderation/messages/{message_id}/report`, `PATCH /moderate`, `GET /reports`, `POST/GET /mutes`, `GET /limits` — rapòrts, amagar/escafar, silencis per usagi/canal/nose, filtre de mots blocats, `disable_chat` per nose e limita de 10 messatges/60 s per nose e usagi (desactivat amb `TESTING=true`).
- `GET /api/federation/events/stream` — SSE amb `token` obligatòri en query (`since` e `limit` opcionalas), replay dels darrièrs 200 eveniments e batement `: ping` cada 15 s.
- `POST /api/federation/events/publish` — publica sus un tèma derivat de `node`/`entity` (o `topic` explicit), signa l'enviament als pares amb HMAC (`X-Clakettes-Signature`) e omet los noses amb `disable_chat`/`disable_search`; solament admin.
- `GET /api/federation/events/retry-queue` — reensajos en espèra; 3 ensajos amb backoff 300 ms → 1,5 s → 5 s.

### Resiliéncia (Fasa 10)

- `GET /api/federation/resilience/health` — estat del nose, basa de donadas, nombre de noses e laténcia.
- `GET /api/federation/resilience/heartbeat` — actualiza `last_seen_at` del par e enregistra la laténcia dins las metricas.
- `GET /api/federation/resilience/metrics` — demandas, succèsses, fracasses, reensajos e laténcias p50/p95 globalas e per nose.
- `POST /api/federation/resilience/keys/revoke`, `GET /keys/revoked` — revocacion immediata de claus per domeni amb motiv, e lista de las revocacions; solament admin per revocar.
- `GET /api/federation/resilience/incident-plan` — plan de recuperacion en cas de compromission d'un nose (8 estapas).

### Santat e utilitats

- `GET /api/federation/health`, `/ping`, `/status`, `/info`, `/version`, `/capabilities`, `/keys`, `/events`, `/peers`, `/links`, `/stats`, `/config`, `/heartbeat`, `/aggregate-nodes`, `/ok`, `/yes`, `/no`, `/maybe`, `/always`, `/never` — marcaires de posicion (placeholders) amb responsas estaticas que non reflètan l'estat real ; non son endpoints de sonda ni diagnostic operatius.

> **Avertiment :** retornan responsas fixas e pòdon donar una falsa impression de seguretat ; per un diagnostic real, utilizatz los endpoints de resilientia descrits mai naut.

## Ajustabilitat

- L'esquèma es versionat; los noses declaran `schema_version` dins lo manifest.
- Los camps opcionals (`did`, `handle`) pòdon èsser omeses se lo nose non los supòrta.
- La minimizacion de las donadas (`minimize_data`) permet d'ometre de camps sensibles dins lo peering.
