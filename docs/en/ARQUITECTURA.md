# Architecture — Clakettes

[ES](../es/ARQUITECTURA.md) · [EN](ARQUITECTURA.md) · [FR](../fr/ARQUITECTURA.md) · [DE](../de/ARQUITECTURA.md) · [IT](../it/ARQUITECTURA.md) · [CA](../ca/ARQUITECTURA.md) · [EU](../eu/ARQUITECTURA.md) · [GL](../gl/ARQUITECTURA.md) · [OC](../oc/ARQUITECTURA.md)

## Map

```
Flutter (web/desktop/Android/iOS) ──HTTPS──► FastAPI ──► SQLite (dev) / MariaDB (prod)
  offline-first (Hive)                    JWT 30 min + refresh 30 d
                                           rate limit 100/60s (?page=&size=)
```

Ports (Docker): backend `8000`, frontend `3000` (dev) / `80` (prod), MariaDB `3306`.

## Backend (`backend/`, detail in [BACKEND.md](BACKEND.md) and [DATABASE.md](DATABASE.md))

Layers: Routers → Services → Models, types via `app.enums`.

| Piece | Where | Rule |
|---|---|---|
| CRUD + `paginate` (size≤100) + `paginate_filtered` | `services/base_service.py` | Routers do not query; services do not raise 404 (except 3 inherited) |
| Uniform 404 | `routers/dependencies.py:get_or_404` | fetch → 404 in one line |
| Auth | `app/auth.py:validate_access_token` | Signature + `type=access` + active/not revoked/not expired session; `last_used_at` lazy (5 min) |
| Optional auth | `routers/dependencies.py:get_current_user_optional` | Public endpoints without 401 |
| Permissions | `routers/permissions.py` | `require_festival_admin`, `require_channel_admin/member`, `require_form_admin`, `can_manage_*` |
| Rate limit | `RateLimitMiddleware` + `RateLimiter` (SQLite, buckets `middleware:`/`dav:`; instances in `main`/`admin`/`auth`) | Disabled with `TESTING=true` |
| Realtime chat | `app/chat_backend/` (WebSocket) + REST in `routers/chat.py` | WS validates session via `validate_access_token` |
| Federated chat | `routers/federation_chat_bridge.py`, `services/message_queue_service.py` (`chat_outbox`), `chat_backend/durable_queue_backend.py` (`DurableQueueBackend`), `services/message_federation_service.py` | RS256-signed bridge, dedup by `message_id`, ordering by `timestamp`, interchangeable transport |
| Chat moderation | `routers/chat_moderation.py`, `services/chat_moderation_service.py`, `services/chat_rate_limit_service.py` | Reports, mutes, word filter, `disable_chat` and 10 messages/60 s per node and user (off with `TESTING=true`) |
| Event bus | `routers/federation_events.py`, `services/event_bus_service.py` | SSE with `since`, heartbeat and replay (200); signed publish and 3 retries (300 ms→5 s) |
| CalDAV | `app/dav/` + `routers/dav.py` (prefix `/dav`, own bucket 600/60s) | Bearer token in URL; TLS mandatory in prod |
| Export | `services/export_service.py` | CSV/ICS in stdlib; PDF with reportlab in lazy import |
| Migrations | `alembic/` (42 versions, head `c1d2e3f4a5b6`) | Prod only Alembic; dev also `create_all` |
| Federation | `routers/federation.py`, `services/jwks_service.py`, `services/node_policy_service.py`, `services/node_peering_service.py`, `services/federation_token_service.py`, `app/mtls.py` | RSA-SHA256 signed manifest, directory, nodes, reports, webfinger, users ref, JWKS, `whoami`, federated token, peers/verify, peers/revoke, mTLS by CN/PEM |
| Portability | `routers/federation_portability.py`, `services/portability_service.py`, models `identity_redirect`/`migration_audit` | Signed bundles, imports, festival/user migration and redirects |
| Resilience | `routers/federation_resilience.py`, `services/federation_metrics_service.py` | Health, heartbeat, p50/p95 metrics, key revocation and incident plan |
| Conformance | `tools/federation_conformance.py`, `services/federation_conformance_service.py` | CLI that verifies manifest, JWKS, token, directory, portability, bridge and SSE |

Generated API: `python tools/gen_api.py --all` produces 441 endpoints in 39 routers with prefix (see [API.md](API.md)).

## Frontend (`frontend/`)

Singleton services + `setState()` + Streams (no Provider). Startup in `main()`:
`DatabaseService` → `OfflineCache` → `SyncQueue` → `ConnectivityMonitor` → `LocaleService` → `NotificationService`.

| Piece | Where | Rule |
|---|---|---|
| API | `services/api_service.dart` (core) + `services/api/` (9 domains) | Base `BACKEND_URL` (saved > dart-define > platform default; Android emulator `10.0.2.2`) |
| Offline | `offline_cache_service.dart` (Hive) + `sync_queue_service.dart` (FIFO, retry 3 + backoff, anti-resend) | Cache tagged by node (`putWithOrigin`, `getOrigin`, `getEnvelope`, `listOrigins`, `clearOrigin`, `reconcile`); per-node health checks to degrade gracefully; on reconnect, sync with confirmation |
| Chat | `screens/chat_screen.dart` + `widgets/chat_bubble.dart` + `widgets/chat_input_bar.dart` | Live WS, REST for history and federated history; E2EE ECDH P-256 + AES-GCM in isolates |
| Notifications | `notification_service.dart` | Desktop: OS plugin; web: Notification API; mobile: no-op (see [PUSH.md](PUSH.md)) |
| Navigation | `main_scaffold.dart` | Rail >800px, Bar <800px, Drawer always; 10 cached screens |
| i18n | `l10n/` + `assets/l10n/` (9 locales) | `en.arb` is fallback; 0 missing keys (verified with script) |
| OS permissions | `AndroidManifest.xml` / `Info.plist` | Network, location, camera, photo library, exact alarms |

## Key flows

1. **Reservation**: festival → event → bulk seats (1 commit) → reservation → occupancy (pin in `tests/integration/test_flows.py`).
2. **Message**: channel → member → DM → read → delete (only sender/admin).
3. **Delegation**: create → list active → revoke (only delegator/admin).
4. **Public registration**: token link → form without auth → approval.
5. **Portability**: signed bundle → import with origin policy → festival/user migration → redirect of the old ref.
6. **Federated chat**: signed envelope → signature verification and dedup → persistence in `chat_outbox` → broadcast and ordering by `timestamp`.
7. **Events**: publish to the bus → SSE with `since` and heartbeat → retry with backoff if the peer fails.
