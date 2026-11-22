# Federated security (phases 2 to 10)

[ES](../es/FEDERATION_SECURITY.md) · [EN](FEDERATION_SECURITY.md) · [FR](../fr/FEDERATION_SECURITY.md) · [DE](../de/FEDERATION_SECURITY.md) · [IT](../it/FEDERATION_SECURITY.md) · [CA](../ca/FEDERATION_SECURITY.md) · [EU](../eu/FEDERATION_SECURITY.md) · [GL](../gl/FEDERATION_SECURITY.md) · [OC](../oc/FEDERATION_SECURITY.md)

## Trust model

- Node identity = domain + X.509 TLS certificate.
- Mutual peering via mTLS with domain certificates (public or private CA): the subject CN and certificate PEM are validated, not only the declared domain.
- Mandatory TLS between nodes; strict certificate validation in peering (no self-signed in prod).
- Identity is stored in `trusted_nodes` (domain, SHA-256 fingerprint of the PEM, subject CN, issuing CA, validity, policies).
- Each node exposes a manifest signed in RSA-SHA256 with the private key of its TLS certificate; peers validate the signature against the PEM of `certificate_chain` and check `expires_at` (24 h).

## Rotation and revocation

- Rotation is managed through certificate renewal: on renewal, the fingerprint in `trusted_nodes` is updated without breaking peering (the root of trust is the CA, not the individual certificate).
- A compromised node is revoked by marking `allowed = false` in `trusted_nodes` (`POST /api/federation/peers/{domain}/revoke`, admin only) or invalidating its certificate in the CA's CRL.
- Administrative revocation is immediate: the next mTLS handshake fails.
- Emergency revocation is also managed from `POST /api/federation/resilience/keys/revoke` (admin only, with reason) and queried at `GET /keys/revoked`; `GET /incident-plan` describes the 8 response steps for a compromise.

## Access controls

- Global rate limiting: 100 req/60s per IP (bucket `middleware:`); `/dav` has 600/60s.
- Per-sensitive-endpoint rate limiting: login 5/300s per IP, refresh 20/60s per IP, federation 60/60s per IP; chat 10 messages/60 s per node and user (disabled with `TESTING=true`).
- Federation endpoints exposing user data (`/users/{ref}`, `/.well-known/webfinger`) require verified peer mTLS.
- `GET /api/federation/whoami` requires a federation Bearer JWT (RS256) validated against the issuer's JWKS; without a valid token it responds 401.
- Node administration endpoints (`/nodes`, `/peers/{domain}/revoke`, portability migrations, `events/publish`, `events/retry-queue`, `keys/revoke`) require the admin role; channel moderation requires admin or channel moderator.
- The SSE event stream requires a valid access token in `?token=`; the event is queried with `since` and replay is limited to the last 200 events.

## Integrity, chat and events

- Portability bundles carry an HMAC-SHA256 `signature` with `SECRET_KEY` and a SHA-256 `checksum` over the canonical payload; import rejects invalid bundles (400) and disallowed origins (403), and applies `minimize_data` to omit sensitive fields.
- The chat bridge signs in RS256 the canonical fields of the envelope (`message_id`, `node_origin`, `content`, `timestamp`, …); the receiver downloads the peer's public key and verifies the signature before persisting. The `chat_outbox` table enforces uniqueness by `message_id`, so a resend is answered as `duplicate`; history is ordered by `timestamp` + `message_id`.
- Transport is interchangeable through the durable queue (`DurableQueueBackend` over `chat_outbox`), with retry and backoff; the broker decision (NATS JetStream, edge WebSocket and single-node fallback) is in `docs/es/FEDERATION_CHAT_BROKER.md`.
- Moderation covers reports, hide/delete messages, mutes with validity and scope by channel or node, blocked-word filter and `disable_chat` per node (`POST /api/chat/moderation/*`). It is complemented by the limit of 10 messages/60 s per node and user.
- Events to peers are signed with HMAC-SHA256 in the `X-Clakettes-Signature` header and propagated only to allowed nodes; failures enter the retry queue (3 attempts, backoff 300 ms → 1.5 s → 5 s) visible at `/api/federation/events/retry-queue`.
- The `disable_chat` and `disable_search` policies are evaluated before applying incoming events or messages, and `import_only` restricts export; `GET /api/federation/resilience/metrics` exposes p50/p95, latency, failures and retries to monitor peering.

## Adjustments

- `allowlist`/`blocklist` per node (`node_policies` / `trusted_nodes`).
- Rate limiting and anti-flood at the federation edge.
- Propagation of moderation reports between nodes.
- `consent_required`: requires explicit consent before federating a node's data.
- `import_only`: unidirectional federation (import only, no export).
- `disable_chat`/`disable_search`: per-function permissions per node.
- `minimize_data`: do not share more than necessary in peering.

## References

- `docs/es/MODELO_CONFIANZA_NODOS.md` — detailed design of the trust model and database tables.
- `docs/es/FEDERATION_PROTOCOL.md` — node-server/client interoperability steps (phases 2 to 10).
- `docs/es/FEDERATION_SCHEMA.md` — Clakettes Schema v1, entities and federation endpoints.
- `docs/es/FEDERATION_CHAT_BROKER.md` — broker decision for chat and events between nodes.
- `docs/es/AMENAZAS_NODOS_FEDERACION.md` — threats per node and residual risks.
