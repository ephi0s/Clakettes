# Clakettes federation protocol (phases 2 to 10)

[ES](../es/FEDERATION_PROTOCOL.md) · [EN](FEDERATION_PROTOCOL.md) · [FR](../fr/FEDERATION_PROTOCOL.md) · [DE](../de/FEDERATION_PROTOCOL.md) · [IT](../it/FEDERATION_PROTOCOL.md) · [CA](../ca/FEDERATION_PROTOCOL.md) · [EU](../eu/FEDERATION_PROTOCOL.md) · [GL](../gl/FEDERATION_PROTOCOL.md) · [OC](../oc/FEDERATION_PROTOCOL.md)

Steps to create an interoperable server/client:

1. Implement the `/api/federation/*` endpoints (see `docs/es/FEDERATION_SCHEMA.md`).
2. Configure mandatory TLS between nodes with mutual mTLS (Phase 2): certificate issued by a trusted CA, no self-signed in production.
3. Register the node as trusted in each peer it will peer with (`trusted_nodes`: domain, SHA-256 fingerprint of the certificate PEM, subject CN, capabilities, policies). `POST /api/federation/nodes` persists `import_only`, `disable_chat` and `disable_search` along with `consent_required` and `minimize_data`.
4. Expose the manifest at `GET /api/federation/manifest` with `schema_version`, `node`, `version`, `capabilities`, `issued_at`, `expires_at`, `signature` and `certificate_chain`. The manifest is signed in RSA-SHA256 (PKCS#1 v1.5) with the node's TLS certificate private key; the peer validates the signature with the PEM of `certificate_chain` and checks `expires_at` (24 h).
5. Expose the public key at `GET /api/federation/.well-known/jwks.json` so peers can validate federation tokens.
6. Validate peer tokens via JWKS: a remote node calling a protected endpoint must present a signed Bearer JWT (RS256) whose `iss` is its domain and whose signature validates against its JWKS. `GET /api/federation/whoami` returns the peer's identity only when that JWT validates (401 otherwise).
7. Resolve remote users via `GET /api/federation/users/{ref}` and `GET /api/federation/.well-known/webfinger` (both require verified peer mTLS only when `MTLS_REQUIRED=true`; default `False`).
8. Use Clakettes Schema v1 for data exchange.
9. Port identity and data with `POST /api/federation/portability/bundles` and `/imports`, migrate with `/festivals/{id}/migrate` and `/users/{ref}/migrate`, and resolve old refs with `GET /redirects/{ref}`.
10. Deliver chat through the signed bridge `/api/federation/chat/bridge/{inbound,outbound,config}`; history is queried at `/api/federation/chat/messages`, with deduplication by `message_id` and ordering by `timestamp` + `message_id`. The durable queue `chat_outbox` allows interchangeable transport (detail in `docs/es/FEDERATION_CHAT_BROKER.md`).
11. Propagate changes through the event bus: `GET /api/federation/events/stream` (SSE with `since` and heartbeat), `POST /publish` and `GET /retry-queue` (3 attempts, backoff 300 ms → 1.5 s → 5 s).
12. Monitor peering health with `/api/federation/resilience/{health,heartbeat,metrics,keys/revoke,keys/revoked,incident-plan}`; `metrics` exposes p50/p95, latency, failures and retries.
13. Verify a third-party node's conformance with `python tools/federation_conformance.py <url> [--json]` (1 if there are critical/high failures).

## Motivation

The protocol allows independent nodes to exchange festivals, users and messages without losing identity or traceability.

## Adjustments

- `consent_required`: requires explicit consent before federating a node's data.
- `import_only`: unidirectional federation (import only, no export).
- `disable_chat`/`disable_search`: per-function permissions per node.
- `minimize_data`: do not share more than necessary in peering.

## Key endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/federation/manifest` | GET | RSA-SHA256 signed manifest with `expires_at` and `certificate_chain` |
| `/api/federation/directory` | GET | Directory of trusted nodes |
| `/api/federation/nodes` | GET/POST | Allowlist/blocklist policies (`import_only`, `disable_chat`, `disable_search`) |
| `/api/federation/whoami` | GET | Peer identity, validating its JWT against its JWKS |
| `/api/federation/.well-known/jwks.json` | GET | Node's JWKS public key |
| `/api/federation/token` | POST | Issuance of federation JWT (RS256) |
| `/api/federation/peers/verify` | POST | Verification of remote node identity (CN and certificate PEM) |
| `/api/federation/peers/{domain}/revoke` | POST | Revocation of trusted node (admin) |
| `/api/federation/users/{ref}` | GET | Remote user resolution (mTLS) |
| `/api/federation/.well-known/webfinger` | GET | WebFinger `acct:user@domain` (mTLS) |
| `/api/federation/reports` | POST/GET/PATCH | Moderation reports between nodes |
| `/api/federation/portability/bundles`, `/imports` | POST | Export and import of signed bundles |
| `/api/federation/portability/festivals/{id}/migrate`, `/users/{ref}/migrate` | POST | Migration of festivals and user identity (admin) |
| `/api/federation/portability/redirects/{ref}` | GET | Resolution of old ref after migration |
| `/api/federation/chat/bridge/inbound`, `/outbound`, `/config` | POST/GET | Signed chat bridge and its configuration |
| `/api/federation/chat/messages` | GET | Federated history, deduplicated and ordered |
| `/api/chat/moderation/*` | POST/PATCH/GET | Reports, mutes, word filter and chat limit |
| `/api/federation/events/stream`, `/publish`, `/retry-queue` | GET/POST | SSE with `since` and heartbeat, publish and retries |
| `/api/federation/resilience/health`, `/heartbeat`, `/metrics` | GET | Health, heartbeat and real p50/p95 metrics |
| `/api/federation/resilience/keys/revoke`, `/keys/revoked`, `/incident-plan` | POST/GET | Key revocation and incident plan |
