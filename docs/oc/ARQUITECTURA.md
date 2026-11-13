# Arquitectura — Clakettes

[ES](../es/ARQUITECTURA.md) · [EN](../en/ARQUITECTURA.md) · [FR](../fr/ARQUITECTURA.md) · [DE](../de/ARQUITECTURA.md) · [IT](../it/ARQUITECTURA.md) · [CA](../ca/ARQUITECTURA.md) · [EU](../eu/ARQUITECTURA.md) · [GL](../gl/ARQUITECTURA.md) · [OC](ARQUITECTURA.md)

## Mapa

```
Flutter (web/escritor/Android/iOS) ──HTTPS──► FastAPI ──► SQLite (dev) / MariaDB (prod)
  offline-first (Hive)                    JWT 30 min + refresh 30 d
                                          rate limit 100/60s (?page=&size=)
```

Ports (Docker): backend `8000`, frontend `3000` (dev) / `80` (prod), MariaDB `3306`.

## Backend (`backend/`, detalle en [BACKEND.md](BACKEND.md) e [DATABASE.md](DATABASE.md))

Capas: Routers → Services → Models, tipos vía `app.enums`.

| Peça | On | Regla |
|------|-----|-------|
| CRUD + `paginate` (size≤100) + `paginate_filtered` | `services/base_service.py` | Los routers non consultan; los servizos non lancan 404 (salvo 3 heredats) |
| 404 uniforme | `routers/dependencies.py:get_or_404` | fetch → 404 en una linea |
| Auth | `app/auth.py:validate_access_token` | Firma + `type=access` + sesion activa/no revocata/no expirada; `last_used_at` lazy (5 min) |
| Auth optional | `routers/dependencies.py:get_current_user_optional` | Endpoints publicos sens 401 |
| Permisos | `routers/permissions.py` | `require_festival_admin`, `require_channel_admin/member`, `require_form_admin`, `can_manage_*` |
| Rate limit | `RateLimitMiddleware` + `RateLimiter` (SQLite, cubs `middleware:`/`dav:`; instancias en `main`/`admin`/`auth`) | Desactivat amb `TESTING=true` |
| Chate en temps real | `app/chat_backend/` (WebSocket) + REST en `routers/chat.py` | WS valida sesion vía `validate_access_token` |
| CalDAV | `app/dav/` + `routers/dav.py` (prefixe `/dav`, cub propi 600/60s) | Token bearer en URL; TLS obligatari en prod |
| Export | `services/export_service.py` | CSV/ICS en stdlib; PDF con reportlab en import preguisat |
| Migracions | `alembic/` (36 versiones) | Prod solament Alembic; dev ademas `create_all` |
| Federacio | `routers/federation.py`, `services/jwks_service.py`, `services/node_policy_service.py` | manifest, directori, nods, informes, webfinger, ref usagis |

Comptes reals (verificats en disc):

| Component | Fitxers | Nota |
|-----------|---------|------|
| Routers | 40 (38 amb `APIRouter`) | `dependencies.py` e `permissions.py` son auxiliars sens router |
| Servizos | 43 | + `__init__.py` |
| Models d'entitat | 40 | + `base.py` e `__init__.py` |
| Esquemes | 37 | |
| Migracions Alembic | 36 | + `__init__.py` |
| Fitxers de prova | 47 | `test_*.py` |
| Linies `def test_` | 1439 | |

## Frontend (`frontend/`)

Servizos singleton + `setState()` + Streams (sens Provider). Arrancada en `main()`:
`DatabaseService` → `OfflineCache` → `SyncQueue` → `ConnectivityMonitor` → `LocaleService` → `NotificationService`.

| Peça | On | Regla |
|------|-----|-------|
| API | `services/api_service.dart` (núcleo) + `services/api/` (9 dominis) | Base `BACKEND_URL` (desada > dart-define > default per plataforma; emulador Android `10.0.2.2`) |
| Offline | `offline_cache_service.dart` (Hive) + `sync_queue_service.dart` (FIFO, retry 3 + backoff, anti-rereig) | Al reconectar, sincronizacion amb confirmacion |
| Chat | `screens/chat_screen.dart` + `widgets/chat_bubble.dart` + `widgets/chat_input_bar.dart` | WS en viu, REST per historial; E2EE ECDH P-256 + AES-GCM en isolats |
| Avisos | `notification_service.dart` | Escritori: plugin SO; web: Notification API; mobil: no-op (veire [PUSH.md](PUSH.md)) |
| Navegacion | `main_scaffold.dart` | Rail >800px, Bar <800px, Drawer sempre; 10 pantallas emmagatzemades |
| i18n | `l10n/` + `assets/l10n/` (9 locales) | `en.arb` es fallback; 0 claus absents (verificat amb script) |
| Permisos SO | `AndroidManifest.xml` / `Info.plist` | Xarxa, ubicacio, camera, fototeca, alarmas exactas |

Comptes reals (verificats en disc):

| Component | Fitxers | Nota |
|-----------|---------|------|
| Widgets reutilizables | 32 | en `lib/widgets/` |
| Pantallas | 36 | en `lib/screens/` |
| Fitxers de prova | 75 | `*_test.dart` en `test/` e subpastas |

## Fluxos claus

1. **Reserva**: festival → evento → asientos bulk (1 commit) → reserva → ocupacion (pin en `tests/integration/test_flows.py`).
2. **Mensaje**: canal → membre → DM → lectura → borrat (solament l'empresor/admin).
3. **Delegacion**: crear → llistar actives → revocar (solament el delegat/admin).
4. **Registro public**: enllac amb token → formularis sens auth → aprobat.