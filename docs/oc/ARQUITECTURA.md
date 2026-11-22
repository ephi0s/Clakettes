# Arquitectura — Clakettes

[ES](../es/ARQUITECTURA.md) · [EN](../en/ARQUITECTURA.md) · [FR](../fr/ARQUITECTURA.md) · [DE](../de/ARQUITECTURA.md) · [IT](../it/ARQUITECTURA.md) · [CA](../ca/ARQUITECTURA.md) · [EU](../eu/ARQUITECTURA.md) · [GL](../gl/ARQUITECTURA.md) · [OC](ARQUITECTURA.md)

## Mapa

```
Flutter (web/ordinaire/Android/iOS) ──HTTPS──► FastAPI ──► SQLite (dev) / MariaDB (prod)
  offline-first (Hive)                    JWT 30 min + refresh 30 d
                                           rate limit 100/60s (?page=&size=)
```

Pòrts (Docker): backend `8000`, frontend `3000` (dev) / `80` (prod), MariaDB `3306`.

## Backend (`backend/`, detalh dins [BACKEND.md](BACKEND.md) e [DATABASE.md](DATABASE.md))

Cachas: Routers → Services → Models, tipes via `app.enums`.

| Pèça | Ont | Regla |
|---|---|---|
| CRUD + `paginate` (size≤100) + `paginate_filtered` | `services/base_service.py` | Los routers non consultan; los servicis non lançan 404 (levat 3 eretats) |
| 404 uniforma | `routers/dependencies.py:get_or_404` | fetch → 404 en una linha |
| Auth | `app/auth.py:validate_access_token` | Signatura + `type=access` + session activa/non revocada/non expirada; helpers `hash_token()`, `is_expired()` (naive = UTC), `get_user_with_roles()` e `touch_session()` (`last_used_at` lazy, 5 min) |
| Auth opcionala | `routers/dependencies.py:get_current_user_optional` | Endpoints publics sens 401 |
| Permissions | `routers/permissions.py` | `require_admin(user, db)` unificat (ròtle legacy `admin` o `UserRole` `ACTIVE`/`APPROVED`), `require_festival_admin`, `require_channel_admin/member`, `require_form_admin`, `can_manage_*`, `require_self_or_admin` (alias) e `require_owner_or_admin` (blocatges) |
| Rate limit | `RateLimitMiddleware` + `RateLimiter` (SQLite, cubèls `middleware:`/`dav:`; instàncias dins `main`/`admin`/`auth`/`auth_sessions`/`federation`) | 100/60 s global, 600/60 s `/dav`, 5/300 s login, 20/60 s refresh, 3/300 s reset, federacion 60/60 s; bypass centralizat en `app.config.is_testing()` (`1/true/yes/on`) |
| Chat en temps real | `app/chat_backend/` (WebSocket) + REST dins `routers/chat.py` | WS valida la session via `validate_access_token` |
| Chat federat | `routers/federation_chat_bridge.py`, `services/message_queue_service.py` (`chat_outbox`), `chat_backend/durable_queue_backend.py` (`DurableQueueBackend`), `services/message_federation_service.py` | Bridge signat RS256, dedup per `message_id`, ordre per `timestamp`, transpòrt intercambiable |
| Moderacion del chat | `routers/chat_moderation.py`, `services/chat_moderation_service.py`, `services/chat_rate_limit_service.py` | Rapòrts, silencis, filtre de mots, `disable_chat` e 10 messatges/60 s per nose e usagi (off amb `TESTING` ∈ {1,true,yes,on}) |
| Bus d'eveniments | `routers/federation_events.py`, `services/event_bus_service.py` | SSE amb `since`, batement e replay (200); publicacion signada e 3 reensajos (300 ms → 1,5 s → 5 s) |
| CalDAV | `app/dav/` + `routers/dav.py` (prefix `/dav`, cubèl proper 600/60s) | Token bearer dins l'URL; TLS obligatòri en prod |
| Export | `services/export_service.py` | CSV/ICS en stdlib; PDF amb reportlab en import perezós |
| Migracions | `alembic/` (45 versions, head `d1e2f3a4b5c6`) | Prod solament Alembic; dev tanben `create_all` |
| Federacion | `routers/federation.py`, `services/jwks_service.py`, `services/node_policy_service.py`, `services/node_peering_service.py`, `services/federation_token_service.py`, `app/mtls.py` | manifest signat RSA-SHA256, directòri, noses, rapòrts, webfinger, ref usagis, JWKS, `whoami`, token federat, peers/verify, peers/revoke, mTLS per CN/PEM |
| Portabilitat | `routers/federation_portability.py`, `services/portability_service.py`, modèls `identity_redirect`/`migration_audit` | Bundles signats, imports, migracion de festivals/usagis e redireccions |
| Resiliéncia | `routers/federation_resilience.py`, `services/federation_metrics_service.py` | Santat, batement, metricas p50/p95, revocacion de claus e plan d'incident |
| Conformitat | `tools/federation_conformance.py`, `services/federation_conformance_service.py` | CLI que verifica manifest, JWKS, token, directòri, portabilitat, bridge e SSE |

API generada: `python tools/gen_api.py --all` produís 446 endpoints dins 43 routers (39 amb prefix dins `main.py`; lo generador combina tanben lo prefix de cada `APIRouter` e detecta las dependéncias d'auth, vejatz [API.md](API.md)).

## Frontend (`frontend/`)

Servicis singleton + `setState()` + Streams (sens Provider). Arranjada dins `main()`:
`DatabaseService` → `OfflineCache` → `SyncQueue` → `NodeService` → `ConnectivityMonitor` → `LocaleService` → `NotificationService`.

| Pèça | Ont | Regla |
|---|---|---|
| API | `services/api_service.dart` (nuclèu) + `services/api/` (13 domenis, division implementada, vejatz son README) | Base `BACKEND_URL` (gardada > dart-define > defaut per plataforma; emulator Android `10.0.2.2`); `resolveMediaUrl()` antepón lo nose actiu a `/uploads/...`; `uploadFile()` utiliza lo MIME per extension, Bearer, reensaj 401/refresh e fallback entre noses; lo WS del chat deriva son URL del meteis `rootUrl` |
| Offline | `offline_cache_service.dart` (Hive) + `sync_queue_service.dart` (FIFO, 3 reensajos + backoff, anti-reenviament) | Cach amb etiqueta de nose (`putWithOrigin`, `getOrigin`, `getEnvelope`, `listOrigins`, `clearOrigin`, `reconcile`); `ConnectivityMonitor` expausa `NodeHealth`, `nodeHealth`, `offlineNodeCount`, `isDegraded` e sondas `ApiService.testNode()`; a la reconnexion, sync amb confirmacion |
| Chat | `screens/chat_screen.dart` + `widgets/chat_bubble.dart` + `widgets/chat_input_bar.dart` | WS en directe, REST per istoric e istoric federat; E2EE ECDH P-256 + AES-GCM en isolats; `ChatPresenceBackend` apòrta escritura, laténcia e confirmacions de lectura; recèrca locala, dedup e ordre per `(created_at,id)`; messatges offline encolats de forma durabla amb lo meteis `message_id` |
| Avisos | `notification_service.dart` | Escritòri: plugin SO; web: Notification API; mobil: no-op (vejatz [PUSH.md](PUSH.md)) |
| Navigacion | `main_scaffold.dart` | Rail >800px, Bar <800px, Drawer totjorn; 11 ecrans en cach; `DegradedNodesBanner` avisa dels noses sens responsa amb recompte e reensaj (`checkNow()`) |
| i18n | `l10n/` + `assets/l10n/` (9 locales, 823 claus per ARB) | `app_en.arb` es lo fallback; paritat de claus e placeholders en `test/l10n/arb_parity_test.dart` (referéncia `es`); `LocaleService.load()` detecta lo locale del SO e persista lo resolt |
| Permissions SO | `AndroidManifest.xml` / `Info.plist` | Ret, localizacion, camèra, galariá, alarmas exactas |

## Fluxes claus

1. **Reserva**: festival → eveniment → sètis bulk (1 commit) → reserva → ocupacion (pin dins `tests/integration/test_flows.py`).
2. **Messatge**: canal → membre → DM → lectura → escafatge (solament emeteire/admin).
3. **Delegacion**: crear → listar activas → revocar (solament delegaire/admin).
4. **Registre public**: ligam amb token → formulari sens auth → aprobacion.
5. **Portabilitat**: bundle signat → import amb politica d'origina → migracion de festival/usagi → redireccion de la ref anciana.
6. **Chat federat**: envelopa signada → verificacion de signatura e dedup → persisténcia dins `chat_outbox` → difusion e ordre per `timestamp`.
7. **Eveniments**: publicacion sul bus → SSE amb `since` e batement → reensaji amb backoff se lo par fracassa.
8. **Corts en festival**: alta en `/api/festivals/{id}/shortfilms` amb `contest_type` (`official_section` per defaut o `contest`) → `FestivalDetailResponse` amb recompte e resumit → filtre dins l'app → projeccions solament amb corts del meteis festival.
9. **Mèdia**: pujada multipart → rota relativa `/uploads/...` (MIME per magic bytes, metadatas netejadas) → `resolveMediaUrl()` la resòlv contra lo nose actiu → cach Hive per nose.
