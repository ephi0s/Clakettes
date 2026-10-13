# Arkitektura — Clakettes

[ES](../es/ARQUITECTURA.md) · [EN](../en/ARQUITECTURA.md) · [FR](../fr/ARQUITECTURA.md) · [DE](../de/ARQUITECTURA.md) · [IT](../it/ARQUITECTURA.md) · [CA](../ca/ARQUITECTURA.md) · [EU](ARQUITECTURA.md) · [GL](../gl/ARQUITECTURA.md) · [OC](../oc/ARQUITECTURA.md)

## Mapa

```
Flutter (web/escritorio/Android/iOS) ──HTTPS──► FastAPI ──► SQLite (dev) / MariaDB (prod)
  offline-first (Hive)                    JWT 30 min + refresh 30 d
                                          rate limit 100/60s (?page=&size=)
```

Portuak (Docker): backend `8000`, frontend `3000` (dev) / `80` (prod), MariaDB `3306`.

## Backend-a (`backend/`, xehetasuna [BACKEND.md](BACKEND.md)-n eta [DATABASE.md](DATABASE.md)-n)

Geruzak: Routers (36) → Services (36) → Models (34), motak `app.enums` bidez.

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

## Frontend-a (`frontend/`)

Zerbitzu singleton-ak + `setState()` + Streams (Provider gabe). Abiaraztea `main()`-en:
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

## Funtsezko fluxuak

1. **Erreserba**: jaialdia → ekitaldia → eserlekuak bulk-ean (commit 1) → erreserba → okupazioa (pin `tests/integration/test_flows.py`-n).
2. **Mezua**: kanala → kidea → DM → irakurketa → ezabaketa (igoleak/adminak soilik).
3. **Delegetza**: sortu → aktiboak zerrendatu → ezeztatu (delegatzaileak/adminak soilik).
4. **Erregistro publikoa**: token-dun esteka → inprimakia auth gabe → onarpena.
