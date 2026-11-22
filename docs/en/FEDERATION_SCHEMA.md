# Clakettes Schema v1

[ES](../es/FEDERATION_SCHEMA.md) · [EN](FEDERATION_SCHEMA.md) · [FR](../fr/FEDERATION_SCHEMA.md) · [DE](../de/FEDERATION_SCHEMA.md) · [IT](../it/FEDERATION_SCHEMA.md) · [CA](../ca/FEDERATION_SCHEMA.md) · [EU](../eu/FEDERATION_SCHEMA.md) · [GL](../gl/FEDERATION_SCHEMA.md) · [OC](../oc/FEDERATION_SCHEMA.md)

Initial version of the federation schema. It defines the minimal entities exchangeable between nodes, versioned via `schema_version` in each node's manifest.

## Trust model (Phase 2)

A node's identity is the tuple **(domain, X.509 TLS certificate)**. Peering between nodes is done over mutual mTLS: each node validates the peer's certificate chain against its root CA, verifies that the certificate domain matches the declared one, and rejects self-signed certificates in production. Rotation and revocation are managed through certificate renewal.

## Entities

- `festival`: id, name, edition, created_at, owner_node
- `user`: id, uuid, did, handle, username, node_origin
- `message`: id, sender, recipient, body, created_at, node_origin
- `moderation_report`: id, reporter_node, target_node, target_user_ref, reason, status
- `identity_redirect`: old_ref, new_ref, target_domain, created_at
- `migration_audit`: entity_type, entity_id, action, source_domain, target_domain, details, created_at
- `chat_outbox`: message_id (unique), node_origin, subject, payload, signature, status, attempts, last_error, created_at
- `message_report`: reporter_id, message_id, reason, status
- `chat_mute`: user_id, channel_id, node_domain, until, reason

## Fields and constraints

- `uuid`: globally stable identifier (UUID v4).
- `did`: optional decentralized identifier.
- `handle`: `user@instance` resolvable via WebFinger.
- `schema_version`: schema version declared by the node in its manifest (current: `1`).

## Federation endpoints

### Identity and directory

- `GET /api/federation/manifest` — node manifest with `schema_version`, `node`, `version`, `capabilities`, `issued_at`, `expires_at`, `signature` and `certificate_chain`. RSA-SHA256 signature with the node's TLS certificate private key; the peer validates the PEM of the chain and the validity of `expires_at` (24 h).
- `GET /api/federation/directory` — list of trusted nodes (`trusted_nodes`) with `allowed = true`, including `cert_fingerprint_sha256` (PEM fingerprint), `capabilities`, `consent_required`, `minimize_data`.
- `GET/POST /api/federation/nodes` — node policies (allowlist/blocklist): `consent_required`, `minimize_data`, `import_only`, `disable_chat`, `disable_search`. Admin only; the last three are persisted and applied in the bridge and the event bus.

### Federated identity and tokens (Phase 3)

- `GET /api/federation/.well-known/jwks.json` — node's RSA public key in JWKS format to validate peer federation tokens.
- `POST /api/federation/token` — issues a signed federation JWT (RS256). Requires node identity verified via mTLS.
- `POST /api/federation/peers/verify` — validates a remote node's identity (domain + CN and certificate PEM + signed manifest).
- `POST /api/federation/peers/{domain}/revoke` — revokes a trusted node (admin).
- `GET /api/federation/whoami` — peer identity (`iss`, `sub`, node) only if its Bearer JWT validates against its JWKS; 401 otherwise.

### Users, reports and discovery

- `GET /api/federation/users/{ref}` — resolves user by `uuid`, `did` or `handle`. Requires verified peer mTLS.
- `GET /api/federation/.well-known/webfinger` — resolves `acct:user@domain`. Requires verified peer mTLS.
- `POST/GET/PATCH /api/federation/reports` — moderation report between nodes.

### Portability (Phase 7)

- `POST /api/federation/portability/bundles` — generates a user bundle with `bundle_version`, `origin_domain`, `payload`, `signature` (HMAC-SHA256 with `SECRET_KEY`) and `checksum` (SHA-256 of the canonical payload).
- `POST /api/federation/portability/imports` — validates signature and checksum, checks the origin policy (403 if not allowed), applies `minimize_data` and records what was imported (user, shorts, festivals, messages). Bundles include `contest_type` in each short: `MediaUrl` is validated/sanitized (invalid URL → `null`), `contest_type` is normalized to `official_section` if invalid and the festival checksum includes it.
- `POST /api/federation/portability/festivals/{festival_id}/migrate` — transfers festival ownership and its shorts to `new_owner_id` of `target_domain` with checksum verification; admin only.
- `POST /api/federation/portability/users/{user_ref}/migrate` — rewrites `handle` and `did` to the target domain and creates the redirect; admin only.
- `GET /api/federation/portability/redirects/{old_ref}` — resolves the old ref (`old_ref`, `new_ref`, `target_domain`, `created_at`).

### Federated chat, moderation and events (Phases 8 and 9)

- `POST /api/federation/chat/bridge/inbound` — accepts a signed envelope (`message_id`, `node_origin`, `content`, `timestamp`, `signature`), verifies the signature RS256 against the peer's public key, discards duplicates by `message_id`, persists the message and broadcasts it; `403` if the node is not allowed or the signature is invalid.
- `POST /api/federation/chat/bridge/outbound` — signs the envelope, queues it in `chat_outbox` with subject `clakettes.chat.node.{target_node}` and publishes through the configured transport (`DurableQueueBackend`); `config` returns transport, stream, algorithm and subject mapping.
- `GET /api/federation/chat/messages` — federated history deduplicated by `message_id` and ordered by `timestamp` + `message_id` (optional `node` filter).
- `POST /api/chat/moderation/messages/{message_id}/report`, `PATCH /moderate`, `GET /reports`, `POST/GET /mutes`, `GET /limits` — reports, hide/delete, mutes by user/channel/node, blocked-word filter, `disable_chat` per node and rate limit of 10 messages/60 s per node and user (disabled with `TESTING=true`).
- `GET /api/federation/events/stream` — SSE with mandatory `token` in query (optional `since` and `limit`), replay of the last 200 events and heartbeat `: ping` every 15 s.
- `POST /api/federation/events/publish` — publishes to a topic derived from `node`/`entity` (or explicit `topic`), signs the delivery to peers with HMAC (`X-Clakettes-Signature`) and skips nodes with `disable_chat`/`disable_search`; admin only.
- `GET /api/federation/events/retry-queue` — pending retries; 3 attempts with backoff 300 ms → 1.5 s → 5 s.

### Resilience (Phase 10)

- `GET /api/federation/resilience/health` — node status, database, number of nodes and latency.
- `GET /api/federation/resilience/heartbeat` — updates the peer's `last_seen_at` and records latency in metrics.
- `GET /api/federation/resilience/metrics` — requests, successes, failures, retries and global and per-node p50/p95 latencies.
- `POST /api/federation/resilience/keys/revoke`, `GET /keys/revoked` — immediate key revocation by domain with reason, and listing of revocations; admin only to revoke.
- `GET /api/federation/resilience/incident-plan` — recovery plan for node compromise (8 steps).

### Health and utilities

- `GET /api/federation/health`, `/ping`, `/status`, `/info`, `/version`, `/capabilities`, `/keys`, `/events`, `/peers`, `/links`, `/stats`, `/config`, `/heartbeat`, `/aggregate-nodes`, `/ok`, `/yes`, `/no`, `/maybe`, `/always`, `/never` — placeholders with static responses that do not reflect the real state; they are not operational probing or diagnostic endpoints.

> **Note:** they return fixed responses and can give a false sense of security; for real diagnostics, use the resilience endpoints described above.

## Adjustability

- The schema is versioned; nodes declare `schema_version` in the manifest.
- Optional fields (`did`, `handle`) can be omitted if the node does not support them.
- Data minimization (`minimize_data`) allows omitting sensitive fields in peering.
