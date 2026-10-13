# Architektur — Clakettes

[ES](../es/ARQUITECTURA.md) · [EN](../en/ARQUITECTURA.md) · [FR](../fr/ARQUITECTURA.md) · [DE](ARQUITECTURA.md) · [IT](../it/ARQUITECTURA.md) · [CA](../ca/ARQUITECTURA.md) · [EU](../eu/ARQUITECTURA.md) · [GL](../gl/ARQUITECTURA.md) · [OC](../oc/ARQUITECTURA.md)

## Übersicht

```
Flutter (web/escritorio/Android/iOS) ──HTTPS──► FastAPI ──► SQLite (dev) / MariaDB (prod)
  offline-first (Hive)                    JWT 30 min + refresh 30 d
                                          rate limit 100/60s (?page=&size=)
```

Ports (Docker): Backend `8000`, Frontend `3000` (dev) / `80` (prod), MariaDB `3306`.

## Backend (`backend/`, Details in [BACKEND.md](BACKEND.md) und [DATABASE.md](DATABASE.md))

Schichten: Router (36) → Services (36) → Models (34), Typen über `app.enums`.

| Pieza | Dónde | Regla |
|---|---|---|
| CRUD + `paginate` (size≤100) + `paginate_filtered` | `services/base_service.py` | Los routers no consultan; los servicios no lanzan 404 (salvo 3 heredados) |
| 404 uniforme | `routers/dependencies.py:get_or_404` | fetch → 404 en una línea |
| Auth | `app/auth.py:validate_access_token` | Firma + `type=access` + sesión activa/no revocada/no expirada; `last_used_at` lazy (5 min) |
| Auth opcional | `routers/dependencies.py:get_current_user_optional` | Endpoints públicos sin 401 |
| Permisos | `routers/permissions.py` | `require_festival_admin`, `require_channel_admin/member`, `require_form_admin`, `can_manage_*` |
| Rate limit | `RateLimitMiddleware` + `RateLimiter` (SQLite, buckets `middleware:`/`dav:`; instancias en `main`/`admin`/`auth`) | Desactivado con `TESTING=true` |
| Chat realtime | `app/chat_backend/` (WebSocket) + REST en `routers/chat.py` | WS valida sesión vía `validate_access_token` |
| CalDAV | `app/dav/` + `routers/dav.py` (prefijo `/dav`, bucket propio 600/60s) | Token bearer en URL; TLS obligatorio en prod |
| Export | `services/export_service.py` | CSV/ICS en stdlib; PDF con reportlab en import perezoso |
| Migraciones | `alembic/` (18) | Prod solo Alembic; dev además `create_all` |

## Frontend (`frontend/`)

Singleton-Dienste + `setState()` + Streams (ohne Provider). Start in `main()`:
`DatabaseService` → `OfflineCache` → `SyncQueue` → `ConnectivityMonitor` → `LocaleService` → `NotificationService`.

| Pieza | Dónde | Regla |
|---|---|---|
| API | `services/api_service.dart` (núcleo) + `services/api/` (9 dominios) | Base `BACKEND_URL` (guardada > dart-define > default por plataforma; Android emulador `10.0.2.2`) |
| Offline | `offline_cache_service.dart` (Hive) + `sync_queue_service.dart` (FIFO, retry 3 + backoff, anti-reenvío) | Al reconectar, sync con confirmación |
| Chat | `screens/chat_screen.dart` + `widgets/chat_bubble.dart` + `widgets/chat_input_bar.dart` | WS en vivo, REST para historial; E2EE ECDH P-256 + AES-GCM en isolates |
| Avisos | `notification_service.dart` | Escritorio: plugin SO; web: Notification API; móvil: no-op (ver [PUSH.md](PUSH.md)) |
| Navegación | `main_scaffold.dart` | Rail >800px, Bar <800px, Drawer siempre; 10 pantallas cacheadas |
| i18n | `l10n/` + `assets/l10n/` (9 locales) | `en.arb` es fallback; 0 claves ausentes (verificado con script) |
| Permisos SO | `AndroidManifest.xml` / `Info.plist` | Red, ubicación, cámara, fototeca, alarmas exactas |

## Schlüsselabläufe

1. **Reserva**: festival → evento → asientos bulk (1 commit) → reserva → ocupación (pin en `tests/integration/test_flows.py`).
2. **Mensaje**: canal → miembro → DM → lectura → borrado (solo emisor/admin).
3. **Delegación**: crear → listar activas → revocar (solo delegador/admin).
4. **Registro público**: enlace con token → formulario sin auth → aprobación.
