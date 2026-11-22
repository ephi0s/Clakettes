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
| Auth | `app/auth.py:validate_access_token` | Signature + `type=access` + active/not revoked/not expired session; helpers `hash_token()`, `is_expired()` (naive = UTC), `get_user_with_roles()` and `touch_session()` (`last_used_at` lazy, 5 min) |
| Optional auth | `routers/dependencies.py:get_current_user_optional` | Public endpoints without 401 |
| Permissions | `routers/permissions.py` | unified `require_admin(user, db)` (legacy `admin` role or `UserRole` `ACTIVE`/`APPROVED`), `require_festival_admin`, `require_channel_admin/member`, `require_form_admin`, `can_manage_*`, `require_self_or_admin` (alias) and `require_owner_or_admin` (blocks) |
| Rate limit | `RateLimitMiddleware` + `RateLimiter` (SQLite, buckets `middleware:`/`dav:`; instances in `main`/`admin`/`auth`/`auth_sessions`/`federation`) | 100/60 s global, 600/60 s `/dav`, 5/300 s login, 20/60 s refresh, 3/300 s reset, 60/60 s federation; centralized bypass via `app.config.is_testing()` (`1/true/yes/on`) |
| Realtime chat | `app/chat_backend/` (WebSocket) + REST in `routers/chat.py` | WS validates session via `validate_access_token` |
| Federated chat | `routers/federation_chat_bridge.py`, `services/message_queue_service.py` (`chat_outbox`), `chat_backend/durable_queue_backend.py` (`DurableQueueBackend`), `services/message_federation_service.py` | RS256-signed bridge, dedup by `message_id`, ordering by `timestamp`, interchangeable transport |
| Chat moderation | `routers/chat_moderation.py`, `services/chat_moderation_service.py`, `services/chat_rate_limit_service.py` | Reports, mutes, word filter, `disable_chat` and 10 messages/60 s per node and user (off with `TESTING` ∈ {1,true,yes,on}) |
| Event bus | `routers/federation_events.py`, `services/event_bus_service.py` | SSE with `since`, heartbeat and replay (200); signed publish and 3 retries (300 ms → 1.5 s → 5 s) |
| CalDAV | `app/dav/` + `routers/dav.py` (prefix `/dav`, own bucket 600/60s) | Bearer token in URL; TLS mandatory in prod |
| Export | `services/export_service.py` | CSV/ICS in stdlib; PDF with reportlab in lazy import |
| Migrations | `alembic/` (45 versions, head `d1e2f3a4b5c6`) | Prod only Alembic; dev also `create_all` |
| Federation | `routers/federation.py`, `services/jwks_service.py`, `services/node_policy_service.py`, `services/node_peering_service.py`, `services/federation_token_service.py`, `app/mtls.py` | RSA-SHA256 signed manifest, directory, nodes, reports, webfinger, users ref, JWKS, `whoami`, federated token, peers/verify, peers/revoke, mTLS by CN/PEM |
| Portability | `routers/federation_portability.py`, `services/portability_service.py`, models `identity_redirect`/`migration_audit` | Signed bundles, imports, festival/user migration and redirects |
| Resilience | `routers/federation_resilience.py`, `services/federation_metrics_service.py` | Health, heartbeat, p50/p95 metrics, key revocation and incident plan |
| Conformance | `tools/federation_conformance.py`, `services/federation_conformance_service.py` | CLI that verifies manifest, JWKS, token, directory, portability, bridge and SSE |

Generated API: `python tools/gen_api.py --all` produces 446 endpoints in 43 routers (39 with prefix in `main.py`; the generator also combines each `APIRouter`'s prefix and detects auth dependencies, see [API.md](API.md)).

## Frontend (`frontend/`)

Singleton services + `setState()` + Streams (no Provider). Startup in `main()`:
`DatabaseService` → `OfflineCache` → `SyncQueue` → `NodeService` → `ConnectivityMonitor` → `LocaleService` → `NotificationService`.

| Piece | Where | Rule |
|---|---|---|
| API | `services/api_service.dart` (core) + `services/api/` (13 domains, split implemented, see its README) | Base `BACKEND_URL` (saved > dart-define > platform default; Android emulator `10.0.2.2`); `resolveMediaUrl()` prefixes the active node to `/uploads/...`; `uploadFile()` uses MIME by extension, Bearer, 401/refresh retry and fallback between nodes; the chat WS derives its URL from the same `rootUrl` |
| Offline | `offline_cache_service.dart` (Hive) + `sync_queue_service.dart` (FIFO, retry 3 + backoff, anti-resend) | Cache tagged by node (`putWithOrigin`, `getOrigin`, `getEnvelope`, `listOrigins`, `clearOrigin`, `reconcile`); `ConnectivityMonitor` exposes `NodeHealth`, `nodeHealth`, `offlineNodeCount`, `isDegraded` and `ApiService.testNode()` probes; on reconnect, sync with confirmation |
| Chat | `screens/chat_screen.dart` + `widgets/chat_bubble.dart` + `widgets/chat_input_bar.dart` | Live WS, REST for history and federated history; E2EE ECDH P-256 + AES-GCM in isolates; `ChatPresenceBackend` provides typing, latency and read receipts; local search, dedup and ordering by `(created_at,id)`; offline messages durably queued with the same `message_id` |
| Notifications | `notification_service.dart` | Desktop: OS plugin; web: Notification API; mobile: no-op (see [PUSH.md](PUSH.md)) |
| Navigation | `main_scaffold.dart` | Rail >800px, Bar <800px, Drawer always; 11 cached screens; `DegradedNodesBanner` warns about unresponsive nodes with a count and retry (`checkNow()`) |
| i18n | `l10n/` + `assets/l10n/` (9 locales, 823 keys per ARB) | `app_en.arb` is fallback; key and placeholder parity in `test/l10n/arb_parity_test.dart` (`es` reference); `LocaleService.load()` detects the OS locale and persists the resolved one |
| OS permissions | `AndroidManifest.xml` / `Info.plist` | Network, location, camera, photo library, exact alarms |

## Key flows

1. **Reservation**: festival → event → bulk seats (1 commit) → reservation → occupancy (pin in `tests/integration/test_flows.py`).
2. **Message**: channel → member → DM → read → delete (only sender/admin).
3. **Delegation**: create → list active → revoke (only delegator/admin).
4. **Public registration**: token link → form without auth → approval.
5. **Portability**: signed bundle → import with origin policy → festival/user migration → redirect of the old ref.
6. **Federated chat**: signed envelope → signature verification and dedup → persistence in `chat_outbox` → broadcast and ordering by `timestamp`.
7. **Events**: publish to the bus → SSE with `since` and heartbeat → retry with backoff if the peer fails.
8. **Shorts in festival**: creation at `/api/festivals/{id}/shortfilms` with `contest_type` (`official_section` by default or `contest`) → `FestivalDetailResponse` with count and summary → filter in the app → screenings only with shorts from the same festival.
9. **Media**: multipart upload → relative path `/uploads/...` (MIME by magic bytes, metadata cleaned) → `resolveMediaUrl()` resolves it against the active node → Hive cache per node.
