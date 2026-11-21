# Arquitectura — Clakettes

[ES](../es/ARQUITECTURA.md) · [EN](../en/ARQUITECTURA.md) · [FR](../fr/ARQUITECTURA.md) · [DE](../de/ARQUITECTURA.md) · [IT](../it/ARQUITECTURA.md) · [CA](../ca/ARQUITECTURA.md) · [EU](../eu/ARQUITECTURA.md) · [GL](ARQUITECTURA.md) · [OC](../oc/ARQUITECTURA.md)

## Mapa

```
Flutter (web/escritorio/Android/iOS) ──HTTPS──► FastAPI ──► SQLite (dev) / MariaDB (prod)
  offline-first (Hive)                    JWT 30 min + refresh 30 d
                                           rate limit 100/60s (?page=&size=)
```

Portos (Docker): backend `8000`, frontend `3000` (dev) / `80` (prod), MariaDB `3306`.

## Backend (`backend/`, detalle en [BACKEND.md](BACKEND.md) e [DATABASE.md](DATABASE.md))

Capas: Routers → Services → Models, tipos vía `app.enums`.

| Peza | Onde | Regra |
|---|---|---|
| CRUD + `paginate` (size≤100) + `paginate_filtered` | `services/base_service.py` | Os routers non consultan; os servizos non lanzan 404 (salvo 3 herdados) |
| 404 uniforme | `routers/dependencies.py:get_or_404` | fetch → 404 nunha liña |
| Auth | `app/auth.py:validate_access_token` | Sinatura + `type=access` + sesión activa/non revogada/non expirada; `last_used_at` lazy (5 min) |
| Auth opcional | `routers/dependencies.py:get_current_user_optional` | Endpoints públicos sen 401 |
| Permisos | `routers/permissions.py` | `require_festival_admin`, `require_channel_admin/member`, `require_form_admin`, `can_manage_*` |
| Rate limit | `RateLimitMiddleware` + `RateLimiter` (SQLite, buckets `middleware:`/`dav:`; instancias en `main`/`admin`/`auth`) | Desactivado con `TESTING=true` |
| Chat en tempo real | `app/chat_backend/` (WebSocket) + REST en `routers/chat.py` | WS valida sesión vía `validate_access_token` |
| Chat federado | `routers/federation_chat_bridge.py`, `services/message_queue_service.py` (`chat_outbox`), `chat_backend/durable_queue_backend.py` (`DurableQueueBackend`), `services/message_federation_service.py` | Bridge asinado RS256, dedup por `message_id`, orde por `timestamp`, transporte intercambiable |
| Moderación de chat | `routers/chat_moderation.py`, `services/chat_moderation_service.py`, `services/chat_rate_limit_service.py` | Informes, silenciamentos, filtro de palabras, `disable_chat` e 10 mensaxes/60 s por nodo e usuario (off con `TESTING=true`) |
| Bus de eventos | `routers/federation_events.py`, `services/event_bus_service.py` | SSE con `since`, latido e replay (200); publicación asinada e reintentos 3 (300 ms→5 s) |
| CalDAV | `app/dav/` + `routers/dav.py` (prefixo `/dav`, bucket propio 600/60s) | Token bearer na URL; TLS obrigatorio en prod |
| Export | `services/export_service.py` | CSV/ICS en stdlib; PDF con reportlab en import perezoso |
| Migracións | `alembic/` (42 versións, head `c1d2e3f4a5b6`) | Prod só Alembic; dev ademais `create_all` |
| Federación | `routers/federation.py`, `services/jwks_service.py`, `services/node_policy_service.py`, `services/node_peering_service.py`, `services/federation_token_service.py`, `app/mtls.py` | manifesto asinado RSA-SHA256, directorio, nodos, informes, webfinger, ref de usuarios, JWKS, `whoami`, token federado, peers/verify, peers/revoke, mTLS por CN/PEM |
| Portabilidade | `routers/federation_portability.py`, `services/portability_service.py`, modelos `identity_redirect`/`migration_audit` | Bundles asinados, imports, migración de festivais/usuarios e redirects |
| Resiliencia | `routers/federation_resilience.py`, `services/federation_metrics_service.py` | Health, heartbeat, métricas p50/p95, revogación de claves e plan de incidente |
| Conformidade | `tools/federation_conformance.py`, `services/federation_conformance_service.py` | CLI que verifica manifesto, JWKS, token, directorio, portabilidade, bridge e SSE |

API xerada: `python tools/gen_api.py --all` produce 441 endpoints en 39 routers con prefixo (ver [API.md](API.md)).

## Frontend (`frontend/`)

Servizos singleton + `setState()` + Streams (sen Provider). Arranque en `main()`:
`DatabaseService` → `OfflineCache` → `SyncQueue` → `ConnectivityMonitor` → `LocaleService` → `NotificationService`.

| Peza | Onde | Regra |
|---|---|---|
| API | `services/api_service.dart` (núcleo) + `services/api/` (9 dominios) | Base `BACKEND_URL` (guardada > dart-define > default por plataforma; emulador Android `10.0.2.2`) |
| Offline | `offline_cache_service.dart` (Hive) + `sync_queue_service.dart` (FIFO, retry 3 + backoff, anti-reenvío) | Caché con etiqueta de nodo (`putWithOrigin`, `getOrigin`, `getEnvelope`, `listOrigins`, `clearOrigin`, `reconcile`); health checks por nodo para degradar con elegancia; ao reconectar, sync con confirmación |
| Chat | `screens/chat_screen.dart` + `widgets/chat_bubble.dart` + `widgets/chat_input_bar.dart` | WS en vivo, REST para histórico e histórico federado; E2EE ECDH P-256 + AES-GCM en isolates |
| Avisos | `notification_service.dart` | Escritorio: plugin SO; web: Notification API; móbil: no-op (ver [PUSH.md](PUSH.md)) |
| Navegación | `main_scaffold.dart` | Rail >800px, Bar <800px, Drawer sempre; 10 pantallas cacheadas |
| i18n | `l10n/` + `assets/l10n/` (9 locales) | `en.arb` é o fallback; 0 claves ausentes (verificado con script) |
| Permisos SO | `AndroidManifest.xml` / `Info.plist` | Rede, localización, cámara, fototeca, alarmas exactas |

## Fluxos clave

1. **Reserva**: festival → evento → asentos bulk (1 commit) → reserva → ocupación (pin en `tests/integration/test_flows.py`).
2. **Mensaxe**: canal → membro → DM → lectura → borrado (só emisor/admin).
3. **Delegación**: crear → listar activas → revogar (só delegador/admin).
4. **Rexistro público**: ligazón con token → formulario sen auth → aprobación.
5. **Portabilidade**: bundle asinado → import con política de orixe → migración de festival/usuario → redirect da ref antiga.
6. **Chat federado**: sobre asinado → verificación de sinatura e dedup → persistencia en `chat_outbox` → difusión e orde por `timestamp`.
7. **Eventos**: publicación no bus → SSE con `since` e latido → reintento con backoff se o par falla.
