# Arquitectura — Clakettes

[ES](../es/ARQUITECTURA.md) · [EN](../en/ARQUITECTURA.md) · [FR](../fr/ARQUITECTURA.md) · [DE](../de/ARQUITECTURA.md) · [IT](../it/ARQUITECTURA.md) · [CA](ARQUITECTURA.md) · [EU](../eu/ARQUITECTURA.md) · [GL](../gl/ARQUITECTURA.md) · [OC](../oc/ARQUITECTURA.md)

## Mapa

```
Flutter (web/escriptori/Android/iOS) ──HTTPS──► FastAPI ──► SQLite (dev) / MariaDB (prod)
  offline-first (Hive)                    JWT 30 min + refresh 30 d
                                           rate limit 100/60s (?page=&size=)
```

Ports (Docker): backend `8000`, frontend `3000` (dev) / `80` (prod), MariaDB `3306`.

## Backend (`backend/`, detall a [BACKEND.md](BACKEND.md) i [DATABASE.md](DATABASE.md))

Capes: Routers → Services → Models, tipus via `app.enums`.

| Peça | On | Regla |
|---|---|---|
| CRUD + `paginate` (size≤100) + `paginate_filtered` | `services/base_service.py` | Els routers no consulten; els serveis no llancen 404 (excepte 3 heretats) |
| 404 uniforme | `routers/dependencies.py:get_or_404` | fetch → 404 en una línia |
| Auth | `app/auth.py:validate_access_token` | Signatura + `type=access` + sessió activa/no revocada/no expirada; `last_used_at` lazy (5 min) |
| Auth opcional | `routers/dependencies.py:get_current_user_optional` | Endpoints públics sense 401 |
| Permisos | `routers/permissions.py` | `require_festival_admin`, `require_channel_admin/member`, `require_form_admin`, `can_manage_*` |
| Rate limit | `RateLimitMiddleware` + `RateLimiter` (SQLite, cubets `middleware:`/`dav:`; instàncies a `main`/`admin`/`auth`) | Desactivat amb `TESTING=true` |
| Xat en temps real | `app/chat_backend/` (WebSocket) + REST a `routers/chat.py` | WS valida sessió via `validate_access_token` |
| Xat federat | `routers/federation_chat_bridge.py`, `services/message_queue_service.py` (`chat_outbox`), `chat_backend/durable_queue_backend.py` (`DurableQueueBackend`), `services/message_federation_service.py` | Bridge signat RS256, dedup per `message_id`, ordre per `timestamp`, transport intercambiable |
| Moderació de xat | `routers/chat_moderation.py`, `services/chat_moderation_service.py`, `services/chat_rate_limit_service.py` | Reportes, silenciaments, filtre de paraules, `disable_chat` i 10 missatges/60 s per node i usuari (off amb `TESTING=true`) |
| Bus d'esdeveniments | `routers/federation_events.py`, `services/event_bus_service.py` | SSE amb `since`, batec i replay (200); publicació signada i reintents 3 (300 ms→5 s) |
| CalDAV | `app/dav/` + `routers/dav.py` (prefix `/dav`, cubet propi 600/60s) | Token bearer a l'URL; TLS obligatori en prod |
| Export | `services/export_service.py` | CSV/ICS en stdlib; PDF amb reportlab en import perezós |
| Migracions | `alembic/` (42 versions, head `c1d2e3f4a5b6`) | Prod només Alembic; dev a més `create_all` |
| Federació | `routers/federation.py`, `services/jwks_service.py`, `services/node_policy_service.py`, `services/node_peering_service.py`, `services/federation_token_service.py`, `app/mtls.py` | manifest signat RSA-SHA256, directori, nodes, reportes, webfinger, ref usuaris, JWKS, `whoami`, token federat, peers/verify, peers/revoke, mTLS per CN/PEM |
| Portabilitat | `routers/federation_portability.py`, `services/portability_service.py`, models `identity_redirect`/`migration_audit` | Bundles signats, imports, migració de festivals/usuaris i redirects |
| Resiliència | `routers/federation_resilience.py`, `services/federation_metrics_service.py` | Health, heartbeat, mètriques p50/p95, revocació de claus i pla d'incident |
| Conformitat | `tools/federation_conformance.py`, `services/federation_conformance_service.py` | CLI que verifica manifest, JWKS, token, directori, portabilitat, bridge i SSE |

API generada: `python tools/gen_api.py --all` produeix 446 endpoints en 39 routers amb prefix (vegeu [API.md](API.md)).

## Frontend (`frontend/`)

Serveis singleton + `setState()` + Streams (sense Provider). Arrancada a `main()`:
`DatabaseService` → `OfflineCache` → `SyncQueue` → `ConnectivityMonitor` → `LocaleService` → `NotificationService`.

| Peça | On | Regla |
|---|---|---|
| API | `services/api_service.dart` (nucli) + `services/api/` (9 dominis) | Base `BACKEND_URL` (desada > dart-define > default per plataforma; emulador Android `10.0.2.2`) |
| Offline | `offline_cache_service.dart` (Hive) + `sync_queue_service.dart` (FIFO, retry 3 + backoff, anti-reenviament) | Caché amb etiqueta de node (`putWithOrigin`, `getOrigin`, `getEnvelope`, `listOrigins`, `clearOrigin`, `reconcile`); health checks per node per degradar amb elegància; en reconnectar, sync amb confirmació |
| Xat | `screens/chat_screen.dart` + `widgets/chat_bubble.dart` + `widgets/chat_input_bar.dart` | WS en viu, REST per historial i historial federat; E2EE ECDH P-256 + AES-GCM en isolates |
| Avisos | `notification_service.dart` | Escriptori: plugin SO; web: Notification API; mòbil: no-op (vegeu [PUSH.md](PUSH.md)) |
| Navegació | `main_scaffold.dart` | Rail >800px, Bar <800px, Drawer sempre; 10 pantalles emmagatzemades |
| i18n | `l10n/` + `assets/l10n/` (9 locals) | `en.arb` és el fallback; 0 claus absents (verificat amb script) |
| Permisos SO | `AndroidManifest.xml` / `Info.plist` | Xarxa, ubicació, càmera, fototeca, alarmes exactes |

## Fluxos clau

1. **Reserva**: festival → esdeveniment → seients bulk (1 commit) → reserva → ocupació (pin a `tests/integration/test_flows.py`).
2. **Missatge**: canal → membre → DM → lectura → esborrat (només emissor/admin).
3. **Delegació**: crear → llistar actives → revocar (només delegador/admin).
4. **Registre públic**: enllaç amb token → formulari sense auth → aprovació.
5. **Portabilitat**: bundle signat → import amb política d'origen → migració de festival/usuari → redirect de la ref antiga.
6. **Xat federat**: sobre signat → verificació de signatura i dedup → persistència a `chat_outbox` → difusió i ordre per `timestamp`.
7. **Esdeveniments**: publicació al bus → SSE amb `since` i batec → reintent amb backoff si el pare falla.
