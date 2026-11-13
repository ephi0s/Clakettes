# Arkitektura — Clakettes

[ES](../es/ARQUITECTURA.md) · [EN](../en/ARQUITECTURA.md) · [FR](../fr/ARQUITECTURA.md) · [DE](../de/ARQUITECTURA.md) · [IT](../it/ARQUITECTURA.md) · [CA](../ca/ARQUITECTURA.md) · [EU](ARQUITECTURA.md) · [GL](../gl/ARQUITECTURA.md) · [OC](../oc/ARQUITECTURA.md)

## Mapa

```
Flutter (web/desktop/Android/iOS) ──HTTPS──► FastAPI ──► SQLite (dev) / MariaDB (prod)
  offline-first (Hive)                    JWT 30 min + refresh 30 d
                                          rate limit 100/60s (?page=&size=)
```

Portuak (Docker): backend `8000`, frontend `3000` (dev) / `80` (prod), MariaDB `3306`.

## Backend (`backend/`, informazio gehiago [BACKEND.md](BACKEND.md) eta [DATABASE.md](DATABASE.md) fitxategian)

Nazioak: Routers → Services → Models, motak `app.enums`-ekin.

| Piesa | Non | Egiazkotasuna |
|-------|-----|---------------|
| CRUD + `paginate` (size≤100) + `paginate_filtered` | `services/base_service.py` | Routers-ek erasotzat egin ez dute; zerbitzariak 404-ek ez (3 errorrek ada) |
| 404 batitzan | `routers/dependencies.py:get_or_404` | ezazu 404-ko emaitza laguntzat |
| Autentikazioa | `app/auth.py:validate_access_token` | Sinatura + `type=access` + sessioa guztitan/no idatzita/no kadu, `last_used_at` lazy (5 min) |
| Autentikatik gabe | `routers/dependencies.py:get_current_user_optional` | Endpoints publikoak 404-rik gabe |
| Baimendiak | `routers/permissions.py` | `require_festival_admin`, `require_channel_admin/member`, `require_form_admin`, `can_manage_*` |
| Rate-limit | `RateLimitMiddleware` + `RateLimiter` (SQLite, bucket `middleware:`/`dav:`; `main`/`admin`/`auth` instanzioak) | `TESTING=true` duzun erasoan desaktibatzea |
| Txat-egoitza | `app/chat_backend/` (WebSocket) + REST `routers/chat.py`-en | WS `validate_access_token`-ekin sessioa eskaintzen du |
| CalDAV | `app/dav/` + `routers/dav.py` (`/dav` prefixikoa, buket bakarra 600/60s) | Bearer token URL-an; TLS beharrezkoa produktu batean |
| Eskaintza | `services/export_service.py` | CSV/ICS stdlib-en; PDF reportlab-arekin eskaintza lazy bidez |
| Migrazioak | `alembic/` (36 bertsioa) | Produktuan Alembic-ak; dev-en `create_all` gehiago |
| Federazioa | `routers/federation.py`, `services/jwks_service.py`, `services/node_policy_service.py` | esku-menua, direktorioa, nodoak, taldeak, webfinger, erabiltzailea ref |

Egiten diren konbendak (diskoan egiaztatuta):

| Eskura | Fitxategi | Eskaera |
|--------|-----------|---------|
| Routers | 40 (38 `APIRouter`-ekin) | `dependencies.py` eta `permissions.py` helper-ak, routerek gabe |
| Zerbitzariak | 43 | + `__init__.py` |
| Entitate-ko modeloak | 40 | + `base.py` eta `__init__.py` |
| Eskaera | 37 | |
| Alembic-ko migrazioak | 36 | + `__init__.py` |
| Prove-fitxategiak | 47 | `test_*.py` |
| `def test_` errenkadak | 1439 | |

## Frontend (`frontend/`)

Zerbitziak erakusten daitezkeena + `setState()` + Streams (ez Provider). `main()`-ean:

`DatabaseService` → `OfflineCache` → `SyncQueue` → `ConnectivityMonitor` → `LocaleService` → `NotificationService`.

| Piesa | Non | Egiazkotasuna |
|-------|-----|---------------|
| API | `services/api_service.dart` (nohia) + `services/api/` (9 domeinuak) | `BACKEND_URL` oinarria (desberrituta > dart-define > plataforma Default; Android emulatzailea `10.0.2.2`) |
| Erasoarekin | `offline_cache_service.dart` (Hive) + `sync_queue_service.dart` (FIFO, retry 3 + backoff, anti-merkezera) | Eraso-biderris sustainablean aurkeztzea |
| Txat | `screens/chat_screen.dart` + `widgets/chat_bubble.dart` + `widgets/chat_input_bar.dart` | WS gorriz, REST erabiliz historiara; E2EE ECDH P-256 + AES-GCM isolatuetan |
| Jakinik gabe | `notification_service.dart` | Desktop: SO plugina; web: Notification API; mobea: no-op ([PUSH.md](PUSH.md)-en) |
| Navegatzea | `main_scaffold.dart` | Rail >800px, Bar <800px, Drawer бидеan; 10 pantalla-cacheatutakoak |
| i18n | `l10n/` + `assets/l10n/` (9 localak) | `en.arb` ezarrezkoa; 0 kladiak absentak (script-ak eskaintzen du) |
| SO-ko baimendiak | `AndroidManifest.xml` / `Info.plist` | Xarxa, ubikazioa, kamera, fototeka, alarmak |

Egiten diren konbendak (diskoan egiaztatuta):

| Eskura | Fitxategi | Eskaera |
|--------|-----------|---------|
| Atzeratutako widget-ak | 32 | `lib/widgets/` barruan |
| Pantailak | 36 | `lib/screens/` barruan |
| Prove-fitxategiak | 75 | `*_test.dart` `test/` barruan eta subcarpeten barruan |

## Bidaia garrantzitsuak

1. **Reserva**: festival → evento → sitting bulk (1 commit) → reserva -> ocupazioa (`tests/integration/test_flows.py`-en pin bat).
2. **Mezua**: kanala → kidea → DM -> irakurri -> ezabatu (emendatua bakarra/adminra).
3. **Delegazioa**: sortu -> zerrendatu -> ukatu (delegaduta/adminra).
4. **Publiko erregistroa**: token-link -> erregistro formulario autentikazio gabe -> onartze.