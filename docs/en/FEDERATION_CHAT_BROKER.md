# Broker evaluation for chat and events: MQTT 5 vs NATS JetStream

[EN](FEDERATION_CHAT_BROKER.md)

This document closes the pending evaluation on which transport to use for chat and event propagation between Clakettes nodes. The decision is binding for Phase 8 (chat as a federated queue) and coexists with the current WebSocket backend described in `docs/es/ARQUITECTURA.md`.

## Weighted criteria

Weights out of 100, score from 1 (poor) to 5 (optimal). The contribution is weight × score / 100.

| Criterion | Weight | MQTT 5 | Contrib. | NATS JetStream | Contrib. |
|---|---:|---:|---:|---:|---:|
| Persistence | 15 | 2 | 0,30 | 5 | 0,75 |
| Ordering | 12 | 3 | 0,36 | 5 | 0,60 |
| Deduplication | 12 | 2 | 0,24 | 5 | 0,60 |
| mTLS | 10 | 4 | 0,40 | 5 | 0,50 |
| Message signing | 8 | 3 | 0,24 | 4 | 0,32 |
| Federated bridges | 18 | 2 | 0,36 | 5 | 0,90 |
| Operational footprint | 10 | 3 | 0,30 | 5 | 0,50 |
| FastAPI/SQLite compatibility | 8 | 3 | 0,24 | 4 | 0,32 |
| Deployment cost | 7 | 3 | 0,21 | 5 | 0,35 |
| **Total** | **100** | | **2,65** | | **4,84** |

### Why these numbers

- **Persistence**: MQTT 5 offers durable sessions and retained messages, but the real history ends up in an external database; JetStream provides streams with configurable retention, replay and durable consumers in the binary itself.
- **Ordering**: MQTT preserves order per topic while the session lives; on reconnect or across a bridge, order degrades. JetStream provides a sequence number per subject within the stream.
- **Deduplication**: MQTT QoS 1 duplicates after reconnection and QoS 2 is costly to operate; JetStream brings publication deduplication via the `Nats-Msg-Id` header within a configurable window (2 min by default).
- **mTLS**: both support it. MQTT delegates it to the broker in use; NATS integrates it with mutual TLS and, in addition, NKeys/JWT identities.
- **Message signing**: both require signing at the application level with the node's TLS key; NATS fits better because headers travel untransformed end to end.
- **Federated bridges**: the highest-weighted criterion. MQTT is hub-and-spoke and each vendor defines its own bridge; NATS brings leaf nodes and gateways as first-class primitives, with subject mapping.
- **Operational footprint and cost**: a single `nats-server` binary (Apache-2.0, JetStream included) versus an MQTT broker that usually drags along a database for persistence and session affinity rules.
- **FastAPI/SQLite**: the `nats-py` client is asynchronous and fits the `async` methods of `ChatBackend`; signature verification reuses `cryptography`, already present in `backend/requirements.txt`.

## Decision

**NATS JetStream wins** (4,84 versus 2,65). It is not a tie: the most heavily weighted criterion, federated bridges, is where the difference is greatest and where this project has a hard requirement.

Concrete reasons for Clakettes:

1. **The existing trust model fits without inventing anything new**: `docs/es/FEDERATION_SECURITY.md` defines node identity as domain + X.509 certificate, mTLS against a CA and `trusted_nodes` with SHA-256 fingerprint. NATS leaf nodes authenticate with that same mTLS, so the bridge between nodes inherits the already documented rotation and revocation (set `allowed = false` and the handshake fails).
2. **Ordering + deduplication + persistence come from the same place**: the entity exchange in `docs/es/FEDERATION_SCHEMA.md` includes `message` with `node_origin` and `created_at`. A stream per subject with a sequence number and deduplication via `Nats-Msg-Id` (using the persisted `message_id` as the idempotency key) avoids rewriting that logic in every consumer.
3. **One binary for two needs**: the same `nats-server` serves the ephemeral event bus (Core NATS, wiring of hubs and room events) and the durable bus (JetStream, messaging and reports). It fits the current Docker deployment (backend 8000, frontend 3000, MariaDB 3306) without adding another service with its own database.
4. **The client is asynchronous by nature**: `nats-py` integrates into FastAPI's `lifespan` alongside the initialization of Hive and the registry, with no extra threads or bridges.

Mitigated drawbacks:

1. **No exactly-once like MQTT's QoS 2**: JetStream is at-least-once. Mitigation: publication deduplication via `Nats-Msg-Id` plus idempotent consumers that use `message_id` as the idempotency key; SQLite remains the source of truth and the message state is written before publishing.
2. **The browser does not natively speak the NATS protocol**: the frontend uses `web_socket_channel` (see `frontend/pubspec.yaml`). Mitigation: the edge WebSocket stays alive; the backend subscribes a JetStream consumer and forwards to the existing `ConnectionManager`. The change is internal and the API Flutter sees is untouched.
3. **The MQTT listener of `nats-server` only understands MQTT 3.1.1** (it rejects MQTT 5 CONNECT): if a device requiring MQTT 5 appears in the future, a dedicated edge MQTT broker will be set up that publishes to the same stream. This is out of the current scope: there are no MQTT devices in the `frontend/pubspec.yaml` inventory.

## Implementation consequences

### Abstract backend

The `ChatBackend` interface already exists in `backend/app/chat_backend/base.py` with `start()`, `stop()` and `send_message(...)`, and `backend/app/chat_backend/registry.py` allows the implementation to be replaced by registering it once at startup. Neither the interface nor the routers need to be touched: a new implementation is added, `NatsJetStreamChatBackend`, which in `start()` connects to `NATS_URL`, declares the stream `CLAKETTES_EVENTS` over the subject `clakettes.events.>` and creates the durable edge consumer; in `stop()` it does a `drain` and closes the connection; in `send_message(...)` it publishes the same payload that `WebSocketChatBackend` builds today, plus headers with `schema_version`, `node_origin`, `message_id`, `event_id` (UUID v4) and `signature`. The signature is RS256 over the canonical representation of the message with the private key of the node's TLS certificate, the same one that signs the manifest (`docs/es/FEDERATION_PROTOCOL.md`). The peer validates it against its JWKS or against the manifest certificate before applying the event.

### Single-node fallback

It is kept as is: `WebSocketChatBackend` remains the backend registered by default in development and with `TESTING=true`. SQLite keeps the messages table as the source of truth; the frontend continues with Hive (`OfflineCacheService`) and the FIFO queue (`SyncQueueService`) for offline mode. If the broker is unavailable, `send_message` enqueues the event in the sync queue with the same `message_id`/`event_id` and it is replayed on reconnect, without duplicates. The edge WebSocket continues delivering to the authenticated connections currently managed by `ConnectionManager`.

### Bridge between nodes

Each node starts its `nats-server` with JetStream and declares a leaf node (or a gateway between clusters) towards the hub node. The leaf authenticates with mTLS using the federated CA; the peer certificate is validated against `trusted_nodes.cert_fingerprint_sha256`. Subject mapping separates events by `node_origin`, by channel and by type, so that the existing policies `disable_chat`, `minimize_data`, `import_only`, `consent_required` and `disable_search` are applied at the inbound consumer before persisting. Revocation of a peer remains immediate: by setting `allowed = false`, the leaf's next mTLS handshake fails and its events stop coming in.

## 4-step migration plan

1. **Prepare**: add `nats-py` to `backend/requirements.txt` and the variables `NATS_URL`, `NATS_STREAM`, `NATS_TLS_CERT`, `NATS_TLS_KEY`, `NATS_CA` to `.env.example`. Implement `NatsJetStreamChatBackend` behind the `CHAT_BACKEND=nats` flag. The registry keeps registering WebSocket by default: no existing test changes.
2. **Shadow**: also publish to NATS with no one consuming for delivery; a validation consumer checks sequence, deduplication and signature between two nodes in staging. Real delivery still goes through WebSocket.
3. **Cut-over**: register the NATS backend in production and turn the WebSocket endpoint into a bridge: its JetStream consumer feeds `ConnectionManager.broadcast()`. Add point tests of the bridge with the transport double and `TESTING=true`, without starting a real broker in the suite. Parallel delivery: WS stays active during the change.
4. **Close**: remove the in-process broadcast for messaging between nodes, activate mTLS leaf nodes between two real nodes and leave single-node mode as a documented fallback. Update in the same change the API (`python tools/gen_api.py --all`), the figures and the README roadmap, and replicate this doc to the eight sister languages per the `AGENTS.md` rule.

## Status

**Decision adopted on 2026-11-20: NATS JetStream as the chat and event broker**, with WebSocket as the edge and single-node fallback, and MQTT 5 discarded for the federated core.

It unblocks the item «Evaluate broker (MQTT vs NATS JetStream) for chat and events» itself and, by direct dependency, the work on federated chat between nodes, event propagation between instances and the mTLS bridge with message signing. It does not unblock or replace the trust model or the federation endpoints already documented: it reuses them as is.
