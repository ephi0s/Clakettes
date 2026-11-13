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
| CalDAV | `app/dav/` + `routers/dav.py` (prefix `/dav`, own bucket 600/60s) | Bearer token in URL; TLS mandatory in prod |
| Export | `services/export_service.py` | CSV/ICS in stdlib; PDF with reportlab in lazy import |
| Migrations | `alembic/` (36 versions) | Prod only Alembic; dev also `create_all` |
| Federation | `routers/federation.py`, `services/jwks_service.py`, `services/node_policy_service.py` | manifest, directory, nodes, reports, webfinger, users ref |

Real counts (verified on disk):

| Component | Files | Note |
|---|---|---|
| Routers | 40 (38 with `APIRouter`) | `dependencies.py` and `permissions.py` are helpers without router |
| Services | 43 | + `__init__.py` |
| Entity models | 40 | + `base.py` and `__init__.py` |
| Schemas | 37 | |
| Alembic migrations | 36 | + `__init__.py` |
| Test files | 47 | `test_*.py` |
| `def test_` lines | 1439 | |

## Frontend (`frontend/`)

Singleton services + `setState()` + Streams (no Provider). Startup in `main()`:
`DatabaseService` → `OfflineCache` → `SyncQueue` → `ConnectivityMonitor` → `LocaleService` → `NotificationService`.

| Piece | Where | Rule |
|---|---|---|
| API | `services/api_service.dart` (core) + `services/api/` (9 domains) | Base `BACKEND_URL` (saved > dart-define > platform default; Android emulator `10.0.2.2`) |
| Offline | `offline_cache_service.dart` (Hive) + `sync_queue_service.dart` (FIFO, retry 3 + backoff, anti-resend) | On reconnect, sync with confirmation |
| Chat | `screens/chat_screen.dart` + `widgets/chat_bubble.dart` + `widgets/chat_input_bar.dart` | Live WS, REST for history; E2EE ECDH P-256 + AES-GCM in isolates |
| Notifications | `notification_service.dart` | Desktop: OS plugin; web: Notification API; mobile: no-op (see [PUSH.md](PUSH.md)) |
| Navigation | `main_scaffold.dart` | Rail >800px, Bar <800px, Drawer always; 10 cached screens |
| i18n | `l10n/` + `assets/l10n/` (9 locales) | `en.arb` is fallback; 0 missing keys (verified with script) |
| OS permissions | `AndroidManifest.xml` / `Info.plist` | Network, location, camera, photo library, exact alarms |

Real counts (verified on disk):

| Component | Files | Note |
|---|---|---|
| Reusable widgets | 32 | in `lib/widgets/` |
| Screens | 36 | in `lib/screens/` |
| Test files | 75 | `*_test.dart` in `test/` and subfolders |

## Key flows

1. **Reservation**: festival → event → bulk seats (1 commit) → reservation → occupancy (pin in `tests/integration/test_flows.py`).
2. **Message**: channel → member → DM → read → delete (only sender/admin).
3. **Delegation**: create → list active → revoke (only delegator/admin).
4. **Public registration**: token link → form without auth → approval.