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
|------|------|-------|
| CRUD + `paginate` (size≤100) + `paginate_filtered` | `services/base_service.py` | Os routers non consultan; os servizos non lanzan 404 (salvo 3 herdados) |
| 404 uniforme | `routers/dependencies.py:get_or_404` | fetch → 404 nunha liña |
| Auth | `app/auth.py:validate_access_token` | Firma + `type=access` + sesión activa/não revocada/não expirada; `last_used_at` lazy (5 min) |
| Auth opcional | `routers/dependencies.py:get_current_user_optional` | Endpoints públicos sen 401 |
| Permisos | `routers/permissions.py` | `require_festival_admin`, `require_channel_admin/member`, `require_form_admin`, `can_manage_*` |
| Rate limit | `RateLimitMiddleware` + `RateLimiter` (SQLite, cubos `middleware:`/`dav:`; instancias en `main`/`admin`/`auth`) | Desactivado con `TESTING=true` |
| Chateo en tempo real | `app/chat_backend/` (WebSocket) + REST en `routers/chat.py` | WS valida sesión vía `validate_access_token` |
| CalDAV | `app/dav/` + `routers/dav.py` (prefixo `/dav`, cubo propio 600/60s) | Token bearer na URL; TLS obrigatorio en prod |
| Export | `services/export_service.py` | CSV/ICS en stdlib; PDF con reportlab en import preguizoso |
| Migracións | `alembic/` (36 versións) | Prod só Alembic; dev ademais `create_all` |
| Federación | `routers/federation.py`, `services/jwks_service.py`, `services/node_policy_service.py` | manifest, directorio, nodos, informes, webfinger, ref usuarios |

Contos reais (verificados no disco):

| Componente | Arquivos | Nota |
|------------|----------|------|
| Routers | 40 (38 con `APIRouter`) | `dependencies.py` e `permissions.py` son auxiliares sen router |
| Servizos | 43 | + `__init__.py` |
| Modelos de entidad | 40 | + `base.py` e `__init__.py` |
| Schemas | 37 | |
| Migracións Alembic | 36 | + `__init__.py` |
| Arquivos de teste | 47 | `test_*.py` |
| Liñas `def test_` | 1439 | |

## Frontend (`frontend/`)

Servizos singleton + `setState()` + Streams (sen Provider). Arranque en `main()`: `DatabaseService` → `OfflineCache` → `SyncQueue` → `ConnectivityMonitor` → `LocaleService` → `NotificationService`.

| Peza | Onde | Regra |
|------|------|-------|
| API | `services/api_service.dart` (núcleo) + `services/api/` (9 dominios) | Base `BACKEND_URL` (gardada > dart-define > defecto por plataforma; Android emulador `10.0.2.2`) |
| Offline | `offline_cache_service.dart` (Hive) + `sync_queue_service.dart` (FIFO, retry 3 + backoff, anti-reenvío) | Ao reconectar, sync con confirmación |
| Chat | `screens/chat_screen.dart` + `widgets/chat_bubble.dart` + `widgets/chat_input_bar.dart` | WS ao vivo, REST para historial; E2EE ECDH P-256 + AES-GCM en isolados |
| Avisos | `notification_service.dart` | Escritorio: plugin SO; web: Notification API; móbil: no-op (ver [PUSH.md](PUSH.md)) |
| Navegación | `main_scaffold.dart` | Rail >800px, Bar <800px, Drawer sempre; 10 pantallas cacheadas |
| i18n | `l10n/` + `assets/l10n/` (9 locales) | `en.arb` é fallback; 0 claves ausentes (verificado con script) |
| Permisos SO | `AndroidManifest.xml` / `Info.plist` | Rede, ubicación, cámara, fototeca, alarmas exactas |

Contos reais (verificados no disco):

| Componente | Arquivos | Nota |
|------------|----------|------|
| Widgets reutilizables | 32 | en `lib/widgets/` |
| Pantallas | 36 | en `lib/screens/` |
| Arquivos de teste | 75 | `*_test.dart` en `test/` e subpastas |

## Fluxos clave

1. **Reserva**: festival → evento → asientos bulk (1 commit) → reserva → ocupación (pin en `tests/integration/test_flows.py`).
2. **Mensaxe**: canal → membro → DM → lectura → borrado (solo emisor/admin).
3. **Delegación**: crear → listar activas → revocar (solo delegador/admin).
4. **Rexistro público**: enlace con token → formulario sen auth → aprobación.