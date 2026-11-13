# Arquitectura — Clakettes

[ES](../es/ARQUITECTURA.md) · [EN](../en/ARQUITECTURA.md) · [FR](../fr/ARQUITECTURA.md) · [DE](../de/ARQUITECTURA.md) · [IT](../it/ARQUITECTURA.md) · [CA](ARQUITECTURA.md) · [EU](../eu/ARQUITECTURA.md) · [GL](../gl/ARQUITECTURA.md) · [OC](../oc/ARQUITECTURA.md)

## Mapa

```
Flutter (web/ordinador/Android/iOS) ──HTTPS──► FastAPI ──► SQLite (dev) / MariaDB (prod)
  offline-first (Hive)                    JWT 30 min + refresh 30 d
                                          rate limit 100/60s (?page=&size=)
```

Ports (Docker): backend `8000`, frontend `3000` (dev) / `80` (prod), MariaDB `3306`.

## Backend (`backend/`, detall a [BACKEND.md](BACKEND.md) i [DATABASE.md](DATABASE.md))

Capes: Routers → Services → Models, tipus via `app.enums`.

| Peu | On | Regla |
|-----|----|-------|
| CRUD + `paginate` (size≤100) + `paginate_filtered` | `services/base_service.py` | Els routers no consulten; els serveis no llançen 404 (salvo 3 heretats) |
| 404 uniform | `routers/dependencies.py:get_or_404` | fetch → 404 en una línia |
| Autenticació | `app/auth.py:validate_access_token` | Signatura + `type=access` + sessió activa/no revocada/no expirada; `last_used_at` lazy (5 min) |
| Autenticació opcional | `routers/dependencies.py:get_current_user_optional` | Endpoints públics sense 401 |
| Permisos | `routers/permissions.py` | `require_festival_admin`, `require_channel_admin/member`, `require_form_admin`, `can_manage_*` |
| Límit de peticions | `RateLimitMiddleware` + `RateLimiter` (SQLite, cubets `middleware:`/`dav:`; instàncies a `main`/`admin`/`auth`) | Desactivat amb `TESTING=true` |
| Xat en temps real | `app/chat_backend/` (WebSocket) + REST a `routers/chat.py` | WS valida sessió via `validate_access_token` |
| CalDAV | `app/dav/` + `routers/dav.py` (prefix `/dav`, cubet propi 600/60s) | Token bearer a l'URL; TLS obligatori a prod |
| Export | `services/export_service.py` | CSV/ICS en stdlib; PDF amb reportlab en import perezos |
| Migracions | `alembic/` (36 versions) | Prod només Alembic; dev també `create_all` |
| Federació | `routers/federation.py`, `services/jwks_service.py`, `services/node_policy_service.py` | manifest, directori, nodes, informes, webfinger, ref usuaris |

Comptes reals (verificats al disc):

| Component | Fitxers | Nota |
|-----------|---------|------|
| Routers | 40 (38 amb `APIRouter`) | `dependencies.py` i `permissions.py` són helpers sense router |
| Serveis | 43 | + `__init__.py` |
| Models d'entitat | 40 | + `base.py` i `__init__.py` |
| Esquemes | 37 | |
| Migracions Alembic | 36 | + `__init__.py` |
| Fitxers de prova | 47 | `test_*.py` |
| Linies `def test_` | 1439 | |

## Frontend (`frontend/`)

Serveis singleton + `setState()` + Streams (sense Provider). Arrancada a `main()`:
`DatabaseService` → `OfflineCache` → `SyncQueue` → `ConnectivityMonitor` → `LocaleService` → `NotificationService`.

| Peu | On | Regla |
|-----|----|-------|
| API | `services/api_service.dart` (núcleo) + `services/api/` (9 dominis) | Base `BACKEND_URL` (desada > dart-define > default per plataforma; emulador Android `10.0.2.2`) |
| Fóra de línia | `offline_cache_service.dart` (Hive) + `sync_queue_service.dart` (FIFO, retry 3 + backoff, anti-rereig) | A la reconnexió, sincronització amb confirmació |
| Xat | `screens/chat_screen.dart` + `widgets/chat_bubble.dart` + `widgets/chat_input_bar.dart` | WS en viu, REST per historial; E2EE ECDH P-256 + AES-GCM en isolats |
| Notificacions | `notification_service.dart` | Escriptori: plugin SO; web: Notification API; mòbil: no-op (veure [PUSH.md](PUSH.md)) |
| Navegació | `main_scaffold.dart` | Rail >800px, Bar <800px, Drawer sempre; 10 pantalles emmagatzemades |
| i18n | `l10n/` + `assets/l10n/` (9 locals) | `en.arb` és el fallback; 0 claus absents (verificat amb script) |
| Permisos SO | `AndroidManifest.xml` / `Info.plist` | Xarxa, ubicació, càmera, fototeca, alarmes exaetes |

Comptes reals (verificats al disc):

| Component | Fitxers | Nota |
|-----------|---------|------|
| Widgets reutilitzables | 32 | a `lib/widgets/` |
| Pantalles | 36 | a `lib/screens/` |
| Fitxers de prova | 75 | `*_test.dart` a `test/` i subcarpetes |

## Fluxos clau

1. **Reserva**: festival → esdeveniment → seies bulk (1 commit) → reserva → ocupació (pin a `tests/integration/test_flows.py`).
2. **Missatge**: canal → membre → DM → lectura → esborrat (només l'emprestor/admin).
3. **Delegació**: crear → llistar actives → revocar (només el delegat/admin).
4. **Registre públic**: enllaç amb token → formulari sense autenticació → aprovat.