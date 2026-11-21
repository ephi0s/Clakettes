# Arquitectura — Clakettes

[ES](ARQUITECTURA.md) · [EN](../en/ARQUITECTURA.md) · [FR](../fr/ARQUITECTURA.md) · [DE](../de/ARQUITECTURA.md) · [IT](../it/ARQUITECTURA.md) · [CA](../ca/ARQUITECTURA.md) · [EU](../eu/ARQUITECTURA.md) · [GL](../gl/ARQUITECTURA.md) · [OC](../oc/ARQUITECTURA.md)

## Mapa

```
Flutter (web/escritorio/Android/iOS) ──HTTPS──► FastAPI ──► SQLite (dev) / MariaDB (prod)
  offline-first (Hive)                    JWT 30 min + refresh 30 d
                                          rate limit 100/60s (?page=&size=)
```

Puertos (Docker): backend `8000`, frontend `3000` (dev) / `80` (prod), MariaDB `3306`.

## Backend (`backend/`, detalle en [BACKEND.md](BACKEND.md) y [DATABASE.md](DATABASE.md))

Capas: Routers → Services → Models, tipos vía `app.enums`.

| Pieza | Dónde | Regla |
|---|---|---|
| CRUD + `paginate` (size≤100) + `paginate_filtered` | `services/base_service.py` | Los routers no consultan; los servicios no lanzan 404 (salvo 3 heredados) |
| 404 uniforme | `routers/dependencies.py:get_or_404` | fetch → 404 en una línea |
| Auth | `app/auth.py:validate_access_token` | Firma + `type=access` + sesión activa/no revocada/no expirada; `last_used_at` lazy (5 min) |
| Auth opcional | `routers/dependencies.py:get_current_user_optional` | Endpoints públicos sin 401 |
| Permisos | `routers/permissions.py` | `require_festival_admin`, `require_channel_admin/member`, `require_form_admin`, `can_manage_*` |
| Rate limit | `RateLimitMiddleware` + `RateLimiter` (SQLite, buckets `middleware:`/`dav:`; instancias en `main`/`admin`/`auth`) | Desactivado con `TESTING=true` |
| Chat realtime | `app/chat_backend/` (WebSocket) + REST en `routers/chat.py` | WS valida sesión vía `validate_access_token` |
| Chat federado | `routers/federation_chat_bridge.py`, `services/message_queue_service.py` (`chat_outbox`), `chat_backend/durable_queue_backend.py` (`DurableQueueBackend`), `services/message_federation_service.py` | Bridge firmado RS256, dedup por `message_id`, orden por `timestamp`, transporte intercambiable |
| Moderación de chat | `routers/chat_moderation.py`, `services/chat_moderation_service.py`, `services/chat_rate_limit_service.py` | Reportes, mutes, filtro de palabras, `disable_chat` y 10 mensajes/60 s por nodo y usuario (off con `TESTING=true`) |
| Bus de eventos | `routers/federation_events.py`, `services/event_bus_service.py` | SSE con `since`, latido y replay (200); publicación firmada y reintentos 3 (300 ms→5 s) |
| CalDAV | `app/dav/` + `routers/dav.py` (prefijo `/dav`, bucket propio 600/60s) | Token bearer en URL; TLS obligatorio en prod |
| Export | `services/export_service.py` | CSV/ICS en stdlib; PDF con reportlab en import perezoso |
| Migraciones | `alembic/` (42 versiones, head `c1d2e3f4a5b6`) | Prod solo Alembic; dev además `create_all` |
| Federación | `routers/federation.py`, `services/jwks_service.py`, `services/node_policy_service.py`, `services/node_peering_service.py`, `services/federation_token_service.py`, `app/mtls.py` | manifest firmado RSA-SHA256, directorio, nodos, reportes, webfinger, users ref, JWKS, `whoami`, token federado, peers/verify, peers/revoke, mTLS por CN/PEM |
| Portabilidad | `routers/federation_portability.py`, `services/portability_service.py`, modelos `identity_redirect`/`migration_audit` | Bundles firmados, imports, migración de festivales/usuarios y redirects |
| Resiliencia | `routers/federation_resilience.py`, `services/federation_metrics_service.py` | Health, heartbeat, métricas p50/p95, revocación de claves y plan de incidente |
| Conformidad | `tools/federation_conformance.py`, `services/federation_conformance_service.py` | CLI que verifica manifiesto, JWKS, token, directorio, portabilidad, bridge y SSE |

API generada: `python tools/gen_api.py --all` produce 441 endpoints en 39 routers con prefijo (ver [API.md](API.md)).

## Frontend (`frontend/`)

Servicios singleton + `setState()` + Streams (sin Provider). Arranque en `main()`:
`DatabaseService` → `OfflineCache` → `SyncQueue` → `ConnectivityMonitor` → `LocaleService` → `NotificationService`.

| Pieza | Dónde | Regla |
|---|---|---|
| API | `services/api_service.dart` (núcleo) + `services/api/` (9 dominios) | Base `BACKEND_URL` (guardada > dart-define > default por plataforma; Android emulador `10.0.2.2`) |
| Offline | `offline_cache_service.dart` (Hive) + `sync_queue_service.dart` (FIFO, retry 3 + backoff, anti-reenvío) | Caché con etiqueta de nodo (`putWithOrigin`, `getOrigin`, `getEnvelope`, `listOrigins`, `clearOrigin`, `reconcile`); health checks por nodo para degradar con elegancia; al reconectar, sync con confirmación |
| Chat | `screens/chat_screen.dart` + `widgets/chat_bubble.dart` + `widgets/chat_input_bar.dart` | WS en vivo, REST para historial e historial federado; E2EE ECDH P-256 + AES-GCM en isolates |
| Avisos | `notification_service.dart` | Escritorio: plugin SO; web: Notification API; móvil: no-op (ver [PUSH.md](PUSH.md)) |
| Navegación | `main_scaffold.dart` | Rail >800px, Bar <800px, Drawer siempre; 10 pantallas cacheadas |
| i18n | `l10n/` + `assets/l10n/` (9 locales) | `en.arb` es fallback; 0 claves ausentes (verificado con script) |
| Permisos SO | `AndroidManifest.xml` / `Info.plist` | Red, ubicación, cámara, fototeca, alarmas exactas |

## Flujos clave

1. **Reserva**: festival → evento → asientos bulk (1 commit) → reserva → ocupación (pin en `tests/integration/test_flows.py`).
2. **Mensaje**: canal → miembro → DM → lectura → borrado (solo emisor/admin).
3. **Delegación**: crear → listar activas → revocar (solo delegador/admin).
4. **Registro público**: enlace con token → formulario sin auth → aprobación.
5. **Portabilidad**: bundle firmado → import con política de origen → migración de festival/usuario → redirect de la ref antigua.
6. **Chat federado**: sobre firmado → verificación de firma y dedup → persistencia en `chat_outbox` → difusión y orden por `timestamp`.
7. **Eventos**: publicación en el bus → SSE con `since` y latido → reintento con backoff si el par falla.