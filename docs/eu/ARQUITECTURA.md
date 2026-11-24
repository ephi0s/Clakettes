# Arkitektura — Clakettes

[ES](../es/ARQUITECTURA.md) · [EN](../en/ARQUITECTURA.md) · [FR](../fr/ARQUITECTURA.md) · [DE](../de/ARQUITECTURA.md) · [IT](../it/ARQUITECTURA.md) · [CA](../ca/ARQUITECTURA.md) · [EU](ARQUITECTURA.md) · [GL](../gl/ARQUITECTURA.md) · [OC](../oc/ARQUITECTURA.md)

## Mapa

```
Flutter (web/mahaigaina/Android/iOS) ──HTTPS──► FastAPI ──► SQLite (dev) / MariaDB (prod)
  offline-first (Hive)                    JWT 30 min + refresh 30 d
                                           rate limit 100/60s (?page=&size=)
```

Atak (Docker): backend `8000`, frontend `3000` (dev) / `80` (prod), MariaDB `3306`.

## Backend (`backend/`, xehetasuna [BACKEND.md](BACKEND.md) eta [DATABASE.md](DATABASE.md) fitxategietan)

Geruzak: Routers → Services → Models, motak `app.enums` bidez.

| Zatia | Non | Araua |
|---|---|---|
| CRUD + `paginate` (size≤100) + `paginate_filtered` | `services/base_service.py` | Router-ek ez dute kontsultatzen; zerbitzuek ez dute 404-ik jaurtitzen (3 heredatutako izan ezik) |
| 404 uniformea | `routers/dependencies.py:get_or_404` | fetch → 404 lerro bakarrean |
| Auth | `app/auth.py:validate_access_token` | Sinadura + `type=access` + saio aktiboa/errebokatu gabea/iraungi gabea; `hash_token()`, `is_expired()` (naive = UTC), `get_user_with_roles()` eta `touch_session()` laguntzaileak (`last_used_at` aldekoa, 5 min) |
| Aukerako auth | `routers/dependencies.py:get_current_user_optional` | Endpoint publikoak 401 gabe |
| Baimenak | `routers/permissions.py` | `require_admin(user, db)` bateratua (legatuzko `admin` rola edo `UserRole` `ACTIVE`/`APPROVED`), `require_festival_admin`, `require_channel_admin/member`, `require_form_admin`, `can_manage_*`, `require_self_or_admin` (alias-ak) eta `require_owner_or_admin` (blokeoak) |
| Rate limit | `RateLimitMiddleware` + `RateLimiter` (SQLite, `middleware:`/`dav:` deposituekin; instantziak `main`/`admin`/`auth`/`auth_sessions`/`federation`-en) | 100/60 s globala, 600/60 s `/dav`-n, 5/300 s login, 20/60 s refresh, 3/300 s reset, federazioa 60/60 s; saihesbidea `app.config.is_testing()`-en zentralizatuta (`1/true/yes/on`) |
| Denbora errealeko txata | `app/chat_backend/` (WebSocket) + REST `routers/chat.py`-n | WS-ak saioa `validate_access_token` bidez balioztatzen du |
| Txat federatua | `routers/federation_chat_bridge.py`, `services/message_queue_service.py` (`chat_outbox`), `chat_backend/durable_queue_backend.py` (`DurableQueueBackend`), `services/message_federation_service.py` | RS256 sinatutako bridge-a, `message_id` bidez dedup-a, `timestamp` bidez ordena, garraio trukagarria |
| Txat-moderazioa | `routers/chat_moderation.py`, `services/chat_moderation_service.py`, `services/chat_rate_limit_service.py` | Txostenak, isiltzeak, hitz-iragazkia, `disable_chat` eta 10 mezu/60 s nodo eta erabiltzaile bakoitzeko (`TESTING` ∈ {1,true,yes,on} bidez off) |
| Gertaera-busa | `routers/federation_events.py`, `services/event_bus_service.py` | SSE `since`, bihotz-taupada eta replay-arekin (200); sinatutako argitalpena eta 3 birsaio (300 ms → 1,5 s → 5 s) |
| CalDAV | `app/dav/` + `routers/dav.py` (`/dav` aurrizkia, depositua 600/60s) | Bearer token URLan; TLS nahitaezkoa prod-en |
| Export | `services/export_service.py` | CSV/ICS stdlib-en; PDF reportlab-ekin inportazio aldegarri batean |
| Migrazioak | `alembic/` | Prod-en soilik Alembic; dev-en baita `create_all` |
| Federazioa | `routers/federation.py`, `services/jwks_service.py`, `services/node_policy_service.py`, `services/node_peering_service.py`, `services/federation_token_service.py`, `app/mtls.py` | RSA-SHA256 sinatutako manifestua, direktorioa, nodoak, txostenak, webfinger, erabiltzaile-erref., JWKS, `whoami`, federazio-tokena, peers/verify, peers/revoke, mTLS CN/PEM bidez |
| Portabilitatea | `routers/federation_portability.py`, `services/portability_service.py`, `identity_redirect`/`migration_audit` modeloak | Sinatutako bundle-ak, inportazioak, jaialdi/erabiltzaile migrazioa eta birbideratzeak |
| Erresilientzia | `routers/federation_resilience.py`, `services/federation_metrics_service.py` | Osasuna, taupada, p50/p95 metrikak, gakoen errebokazioa eta intzidente-plana |
| Betetzea | `tools/federation_conformance.py`, `services/federation_conformance_service.py` | CLIak manifestua, JWKS, tokena, direktorioa, portabilitatea, bridge-a eta SSE egiaztatzen ditu |

Sortutako APIa: `python tools/gen_api.py --all`-ek `main.py`-n eta `APIRouter` bakoitzaren aurrizkia konbinatuz endpoint-en erreferentzia sortzen du (ikusi [API.md](API.md)).

## Frontend (`frontend/`)

Singleton zerbitzuak + `setState()` + Streams (Provider gabe). Abiaraztea `main()`-en:
`DatabaseService` → `OfflineCache` → `SyncQueue` → `NodeService` → `ConnectivityMonitor` → `LocaleService` → `NotificationService`.

| Zatia | Non | Araua |
|---|---|---|
| API | `services/api_service.dart` (nukleoa) + `services/api/` (domeinuen split-a ezarria, ikusi bere README-n) | Oinarria `BACKEND_URL` (gordeta > dart-define > plataformaren araberako lehenetsia; Android emulatzailea `10.0.2.2`); `resolveMediaUrl()`-ek nodo aktiboa jartzen du `/uploads/...`-ren aurrean; `uploadFile()`-ek luzapenaren bidezko MIME-a, Bearer-a, 401/refresh birsaioa eta nodoen arteko fallback-a erabiltzen ditu; txataren WS-ak bere URLa `rootUrl` beretik eratorritzen du |
| Offline | `offline_cache_service.dart` (Hive) + `sync_queue_service.dart` (FIFO, 3 birsaio + atzerapena, birbidaltzearen aurkakoa) | Nodo-etiketadun cache-a (`putWithOrigin`, `getOrigin`, `getEnvelope`, `listOrigins`, `clearOrigin`, `reconcile`); `ConnectivityMonitor`-ek `NodeHealth`, `nodeHealth`, `offlineNodeCount`, `isDegraded` eta `ApiService.testNode()` zundaketak erakusten ditu; berriro konektatzean, sinkronizazioa berrespenarekin |
| Txata | `screens/chat_screen.dart` + `widgets/chat_bubble.dart` + `widgets/chat_input_bar.dart` | WS zuzenean, REST historia eta federazio-historiarako; E2EE ECDH P-256 + AES-GCM isolate-etan; `ChatPresenceBackend`-ek idazketa, latentzia eta irakurketa-berrespenak eskaintzen ditu; bilaketa lokala, dedup-a eta `(created_at,id)` bidezko ordena; offline mezuak modu iraunkorrean ilaratzen dira `message_id` berarekin |
| Jakinarazpenak | `notification_service.dart` | Mahaigaina: SO plugina; web-a: Notification API; mugikorra: no-op (ikusi [PUSH.md](PUSH.md)) |
| Nabigazioa | `main_scaffold.dart` | Rail >800px, Bar <800px, Drawer beti; pantailak cache-etan; `DegradedNodesBanner`-ek erantzun gabeko nodoen berri ematen du kopurua eta birsaioarekin (`checkNow()`) |
| i18n | `l10n/` + `assets/l10n/` (`assets/l10n/`-eko locale guztiak) | `app_en.arb` da fallback-a; gakoen eta placeholder-en paritatea `test/l10n/arb_parity_test.dart`-en (erreferentzia `es`); `LocaleService.load()`-ek SOaren locale-a detektatzen du eta ebatzitakoa gordetzen du |
| SO baimenak | `AndroidManifest.xml` / `Info.plist` | Sarea, kokapena, kamera, argazki-liburutegia, alarma zehatzak |

## Fluxu giltzarriak

1. **Erreserba**: jaialdia → gertaera → eserleku bulk (commit 1) → erreserba → okupazioa (pin-a `tests/integration/test_flows.py`-n).
2. **Mezua**: kanala → kidea → DM → irakurketa → ezabaketa (igortzailea/admin soilik).
3. **Ordezkaritza**: sortu → aktiboak zerrendatu → errebokatu (ordezkatzailea/admin soilik).
4. **Erregistro publikoa**: token-dun esteka → auth gabe formularioa → onarpena.
5. **Portabilitatea**: sinatutako bundle-a → jatorri-politikarekin inportatu → jaialdi/erabiltzaile migrazioa → erreferentzia zaharraren birbideratzea.
6. **Txat federatua**: sinatutako gutun-azala → sinadura eta dedup egiaztapena → `chat_outbox`-en iraunaraztea → hedapena eta `timestamp` bidezko ordena.
7. **Gertaerak**: busean argitaratu → SSE `since` eta bihotz-taupadarekin → atzerapeneko birsaioa pareak huts egiten badu.
8. **Jaialdiko laburrak**: `/api/festivals/{id}/shortfilms`-en alta `contest_type` erabiliz (`official_section` lehenespenez edo `contest`) → `FestivalDetailResponse` kopuru eta laburpenarekin → app-eko iragazkia → proiekzioak jaialdi bereko laburrekin soilik.
9. **Mediak**: multipart igoera → `/uploads/...` bide erlatiboa (magic bytes bidezko MIME-a, metadatu garbiak) → `resolveMediaUrl()`-ek nodo aktiboaren aurka ebazten du → Hive cache-a nodo bakoitzeko.
