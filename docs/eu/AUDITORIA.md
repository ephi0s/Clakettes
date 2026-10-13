# Kode-auditoria — Clakettes (09/10/2026, plataforma-aniztasun zabalkuntza 09/10/2026, berrik. 10/10/2026)

[ES](../es/AUDITORIA.md) · [EN](../en/AUDITORIA.md) · [FR](../fr/AUDITORIA.md) · [DE](../de/AUDITORIA.md) · [IT](../it/AUDITORIA.md) · [CA](../ca/AUDITORIA.md) · [EU](AUDITORIA.md) · [GL](../gl/AUDITORIA.md) · [OC](../oc/AUDITORIA.md)

> **11/10/2026ko gehigarria** (zifra egiaztatuak): backend-ean 1402 test 37 fitxategitan;
> router-ak 36 fitxategi (33 `APIRouter`-dun); services 36; models 34; schemas 33;
> Alembic 18 bertsio; `docs/es/API.md` 310 endpoint (operationId bakarrak).
> RGPD: pribatutasuna lehenetsita, adostasuna, ezabaketa/esportazioa, saioen
> purgaketa, append-only auditoria, metadatuen sanotizazioa, TLS MariaDB prod-ean,
> DAV iraungitzearekin, CSP/HSTS. Ordainketa-hornitzaileak mock/stripe/redsys.

## 0. Laburpen exekutiboa (10/10/2026, zifra egiaztatuak)

| Área | Estado | Detalle |
| --- | --- | --- |
| Backend tests | 1321 `def test_` en 33 archivos | `Get-ChildItem backend/tests -Recurse -Filter "test_*.py" \| Select-String "def test_"` |
| Frontend tests | 347 bloques en 69 archivos | `Get-ChildItem frontend/test -Recurse -Filter "*_test.dart" \| Select-String "testWidgets\(|test\("` |
| Routers/Services/Models/Schemas | 35/33/33/32 archivos (33 routers con `APIRouter`) | `permissions.py`/`dependencies.py` son helpers sin router; `base.py`/`__init__.py` no son entidades |
| Migraciones | 15 + `__init__.py` | `alembic/versions/` |
| Endpoints | 294 en 33 routers (`docs/es/API.md` por AST) | `python tools/gen_api.py` idempotente; grep simple da 272 (no cuenta `propfind/report/options/websocket`) |
| Lint | `ruff check` + `ruff format --check` limpios (216 archivos) | `AGENTS.md` y CI (GH + GitLab) con gate de formato |
| Docs | Backend consolidado en `docs/` | `docs/es/BACKEND.md` + `docs/es/DATABASE.md`; índice en `docs/es/README.md` |
| Deuda principal | `get_or_404` parcial, `paginate_filtered` sin usos, `python-jose` sin migrar, 24 `AlertDialog` / 115 `ScaffoldMessenger` restantes | Ver §5 con conteos y verificación |

Nola berre-egiaztatu: `cd backend; python -m ruff check .; python -m pytest tests/ -x -q --tb=short` eta `cd frontend; flutter analyze; flutter test`.

## 1. Kanpo-mendekotasunak: zer kendu daiteke eta zer ez

### Backend-a (`backend/requirements.txt` + `pyproject.toml`)

| Dep | Veredicto | Motivo |
| --- | --- | --- |
| fastapi, uvicorn[standard], sqlalchemy, pydantic(+settings), alembic | Mantener | Núcleo del stack |
| python-jose[cryptography] | Mantener por ahora, migrar a PyJWT en el futuro | Abandonado desde 2016, pero el cambio toca `app/auth.py` + `routers/dependencies.py` + tests; hacerlo en PR separado con tests de tokens |
| python-dotenv | Mantener | Requerido por `pydantic-settings>=2` y `uvicorn[standard]` (`--env-file`); solo 2 scripts lo importan directamente, pero quitarlo rompería la carga de `.env` |
| pymysql | Mantener como driver prod | Solo se usa con MariaDB; no cargarlo en dev no ahorra nada (import perezoso ya en SQLAlchemy) |
| python-multipart, email-validator, bcrypt | Mantener | Uploads, validación email, hash passwords |
| reportlab 5.0.1 | Mantener, pero con import perezoso (hecho) | Solo `export_service._build_pdf`; antes se importaba a nivel de módulo (~200 ms + memoria en cada worker). Ahora import dentro de la función. Además se sincronizó `pyproject.toml` (faltaba) y se pineó `==5.0.1` |

### Frontend-a (`frontend/pubspec.yaml`)

Mendekotasun guztiak benetako erabileran daude; bat ere ezin izan da kendu funtzionaltasuna hautsi gabe:

- `archive`: `crypto_utils.dart`-en erabilia (ZLib/GZip). `dart:io` ez du balio web-a hausten duelako.
- `path_provider`: `file_downloader_io.dart`-en erabilia (mugikorra/escritorioa).
- `web`: `file_downloader_web.dart`-en erabilia.
- `pointycastle` + `crypto` + `uuid`: txataren E2EE (X25519/ECDH P-256 + AES-GCM).
- `flutter_map` + `cancellable_tile` + `latlong2` + `geolocator` + `url_launcher`: mapak.
- `table_calendar`, `flutter_local_notifications` + `timezone` + `flutter_timezone`, `image_picker` + `file_picker`: bakoitza erabilera 1-2rekin, baina kentzeak funtzionaltasuna kenduko luke.

## 2. Aplikatutako optimizazioak

1. `export_service.py`: reportlab inportazio nagia `_build_pdf`-n + docstring.
2. `main.py` RateLimitMiddleware + `routers/admin.py` + `routers/auth.py`: 3 `RateLimiter` instantzia (`middleware:`/`dav:` bucket-ak + `reset` 3/300s eta `login` limiter-ak); ez bateratu muga desberdinak galdu gabe.
3. `base_service.py`: `paginate`-k `page>=1`, `size` `[1,100]`-en finkatzen du; `paginate_filtered()` berria 0 erabilerarekin (klonatutako `get_all_paginated`-ak migratzeko daude).
4. `routers/dependencies.py`: `get_current_user_optional`-ek `validate_access_token` berrerabiltzen du (JWT+saio ~30 lerro bikoiztu kenduta); `__import__("datetime")` konponketa → inportazio normala; `get_or_404()` berria ~100 `HTTPException(404)` inline ordezkatzeko.
5. `dav/auth.py`: `app.auth._hash_token`-rekiko erlazioa dokumentatuta.
6. `pyproject.toml`/`requirements.txt` sinkronizatuta (reportlab).
7. `reusable_widgets.dart`: `showAppSnack()` berria (def 1 + 8 erabilera; 115 `ScaffoldMessenger` zuzen geratzen dira).

## 3. Aplikatutako plataforma-aniztasun hobekuntzak (escritorioa + web-a + Android + iOS/iPad)

1. `BackendConfig`: plataformaren araberako lehenetsia — Android emuladoreak `10.0.2.2:8000` erabiltzen du
   (emuladorearen localhost-a birtual propioa da, ez host-a); gainerakoak `localhost:8000`.
   Lehentasuna: gordetako URL > `--dart-define=BACKEND_URL` > plataformaren araberako lehenetsia.
   `ApiService`-ek lehenetsi bera erabiltzen du eraikitzailean eta getter-etan.
2. `NotificationService`: web-ean (`kIsWeb`) `init`-ek ez du plugina ez timezone ukitzen
   (tokiko jakinarazpenik ez nabigatzailean) eta `scheduleReminder`-ek ez du ezer egiten;
   docstring-ean dokumentatuta. Plataformaren araberako adarrik ez pantailetan.
3. `file_downloader.dart`: inportazio baldintzatua egiaztatuta
   (`web` lehenetsiz, `io` `dart.library.io` badago) — nabigatzailea, escritorioa,
   Android eta iOS estaltzen ditu aldaketarik gabe.
4. `main_scaffold.dart`: Laburrak nabigazioan gehituta (bazegoen `screenIndex 3`
   pantaila baina item gabe — eskuraezina). Rail >800px (escritorioa/web-a),
   Bar <800px (mugikorra), Drawer denetan.
5. `AndroidManifest.xml`: INTERNET, ACCESS_NETWORK_STATE, kokapena
   (FINE+COARSE), CAMERA, READ_MEDIA_IMAGES/VIDEO, SCHEDULE/USE_EXACT_ALARM gehituta.
   INTERNET esplizitu gabe release build-ek ez dute sarerik.
6. `ios/Runner/Info.plist`: NSLocationWhenInUse, NSCamera,
   NSPhotoLibrary (+Add) gehituta. Hauek gabe sistemak ukatu edo App Store-k ezezkoa ematen du.
7. Backend `routers/festivals.py`: `get_or_404(db, Festival/Location, ...)` pilotua
   — 9 `if not → 404` bloke kenduta; `shortfilms.py`-ra (3) eta
   `users.py`-ra (4) hedatuta. Gainerako router-etara hedatzeko eredua.
8. Frontend `awards_screen.dart`: errore-SnackBar `showAppSnack()`-era migratuta
   (pilotua). Oharra: gainerako 24 `AlertDialog`-ak *inprimaki*-elkarrizketak dira
   (sortu/editatu), ez berrespenekoak — ez dira `showConfirmDialog`-era migratzen
   (19 erabilera 18 pantailatan); `CreateEntityDialog` komun bat beharko lukete.
9. CI: `ruff format --check` gate-a gehituta (GH + GitLab) egiaztatu ondoren
   `216 files already formatted`.
10. Segurtasuna (`channels.py` pilotua, segurtasun blokea): `require_channel_member`/`is_channel_member`
    berria `permissions.py`-n eta erabilera `channels.py` + `chat.py`-n (inportazio geroratuzko 3 inline bloke kentzen ditu);
    `channels.py` `get_or_404`-era migratuta (7 bloke gutxiago); rol-whitelist-a
    `Literal[admin,moderator,member]` schema-etan (lehen: string librea → 500
    CheckConstraint-engatik; orain: 422); 4 test 403/422 berri
    `TestChannelAuthorization`-en.
11. Segurtasuna: `POST /delegations/{id}/revoke`-k auth soilik eskatzen zuen — edonork
    ezeztatzen zituen besteren delegazioak. Orain delegatzailea edo admin egiaztatzen du + 403 test-a.
    Jada OK egiaztatuta (aldaketarik gabe): `user_roles`/`user_festival` (whitelist
    attendee), DM-ak (ownership), inprimaki publikoak (auth aukerakoa), WS
    (saioa balioztatzen du), `bulk_create` (commit bakarra), SyncQueue (retry+backoff),
    i18n (0 giltza falta), `locations` (didChangeDependencies guard-arekin).
12. `get_or_404` `committees.py`-ra (10), `events.py`-ra (58, script bidez
    berrikuspenarekin + esleitu gabeko 17 existentzia F841 saihesteko), `delegations`-era
    (2) eta kokapenen 5 router-etara (12) hedatuta. Eskema-aldaketarik gabe: ez dago
    Alembic migrazio pendiente-rik sorta honengatik.
13. Errendimendua: programazioaren `venue` iragazkia SQL-ra jaitsita (lehen orria
    Python-en iragazten zuen eta `total`/`pages` hausten zituen).
14. Frontend: bidalketa bikoitzaren aurkako guard-ak jaialdia/erabiltzailea/laburra sortzean +
    3 SnackBar `showAppSnack`-era migratuta.
15. Txata: E2EE UI thread-etik kanpo — `_prepareContent`/`_unpackContent`-ek
    `encryptAsync`/`decryptAsync` (isolate-ak) erabiltzen dituzte; `encryptSenderKeyAsync`/
    `decryptSenderKeyAsync` berriak sender key-en difusioan eta harreran erabilita.
    `RestChatBackend` kontserbatzen da: `chat_service_test`-ek fake gisa erabiltzen du
    (ez zen kode hila).
16. Txata: `chat_screen.dart` 1038 → 767 lerro; burbuilak
    `widgets/chat_bubble.dart`-ra (`ChatBubble` + `ChatBubbleWidget` irudi,
    kokapen, vCard, iCal-ekin) eta barra `widgets/chat_input_bar.dart`-ra
    (`ChatInputBar`). 2 test async berri `crypto_utils_test`-en.
17. `locations_screen` 1144 → 680 lerro: txartelak eta inprimakia
    `widgets/location_cards.dart`-ra (`LocationCard`, `LegacyCard`,
    `LegacyLocation`, `LocationFormScreen`, `LocationFormResult`); ezabaketa
    `showConfirmDialog` + `showAppSnack`-ekin (AlertDialog bat gutxiago).
18. `festival_profile_screen` 1276 → 956 lerro: `RulebooksSection` eta
    `FestivalLocationsSection` (+ mapa eta fitxak)
    `widgets/festival_sections.dart`-ra. Pantailak egoera,
    irakurketa, edizioa eta callback-ak kontserbatzen ditu.
19. `api_service.dart` 1134 → 511 lerro: 95 metodo `lib/services/api/`-ra mugituta
    (`event_api` 31, `location_api` 25, `org_api` 17, `catalog_api` 13,
    gainerakoa `user_api` + `calendar/channel/festival/form`-era). Nukleoak config, auth, garraioa eta
    admin/bilaketa kontserbatzen ditu. API publikoa ukigabe.
20. `user_profile_screen` 996 → 803 lerro: `SessionsCard` eta `AliasesCard`
    `widgets/user_profile_cards.dart`-ra. Heredatutako giltzarik gabeko 4 `if`
    zuzenduta `catalog_api`-n.
21. Fluxu-test-ak (`tests/integration/test_flows.py`): erreserba osoa
    (jaialdia → ekitaldia → eserlekuak → erreserba → okupazioa), mezularitza
    (kanala → kidea → DM → irakurketa → ezabaketa) eta delegazioa (sortu →
    zerrendatu → ezeztatu).
22. Erauzitako widget-en widget test-ak (13): `chat_bubble`,
    `chat_input_bar`, `user_profile_cards`, `location_cards`. Oharra:
    `wrapWithLocalization` pean dauden widget-ek `pump()` gehigarri bat behar dute
    (lokalizazio-Builder-a bigarren frame-an ebazten da).
23. Push natiboa Firebase gabe (`docs/es/PUSH.md`): nabigatzailearen Notification API
    web-ean (`notification_web.dart` + stub esportazio baldintzatuarekin, mendekotasun
    berririk gabe), `flutter_local_notifications` escritorioan + macOS baimena
    hasieran, mugikorra esplizituki no-op (`_supported`). `flutter build web`
    egiaztatuta.
24. Dokumentazioa: `docs/es/API.md` (294 endpoint 33 router-etan, AST bidez sortua
    `tools/gen_api.py`-rekin — birsortgarria), `docs/es/ARQUITECTURA.md`
    (geruzak, fluxuak, plataforma-aniztasun erabakiak), `docs/es/USO.md` (abiaraztea,
    env, operazioa, rolak), `docs/es/DESARROLLO.md` (konbentzioak + CI ateak),
    `docs/es/SEGURIDAD.md` (token-ak, baimen-matrizea, prod checklist-a),
    `docs/es/BACKEND.md` + `docs/es/DATABASE.md` (`backend/`-tik mugituta 10/10/2026an).
    README-ak eta `AGENTS.md` zifra errelekin; admin dev `admin`/`setup`
    (`.env.example`-n `ADMIN_PASSWORD` gabe; seed prod-ez kanpo soilik `app/main.py:257`-n).
Egoera: 1321 backend test (33 fitxategi) + 347 frontend (69 fitxategi) berdean, ruff + analyze garbi.

## 4. 10/10/2026ko berrikuspena (§2–§3 zuzenketak)

1. Backend doc-ak bateratuta: `backend/BACKEND.md` + `backend/DATABASE.md` → `docs/es/BACKEND.md` + `docs/es/DATABASE.md`; estekak eguneratuta `README.md`, `AGENTS.md`, `docs/es/README.md`, `ARQUITECTURA.md`, `USO.md`, `ADMINISTRACION.md`-n.
2. Benetako kontaketa: router-ak 35 fitxategi (33 `APIRouter`-dun; `permissions.py`/`dependencies.py` helper-ak dira), services 33 modulu (+`__init__`), models 33 entitate (+`base.py`+`__init__`), schemas 32, Alembic 15, `API.md` 294 endpoint/33 router (AST-k `propfind/report/options/websocket` zenbatzen ditu; grep soilak 272 ematen du).
3. Test-ak: backend 1321 `def test_` 33 fitxategitan (ez 1366/38); frontend 347 bloke 69 fitxategitan (ez 313/70). Widget-ak 24 OK. Pantailak: `festival_profile` 956L, `locations` 680L, `chat` 767L, `api_service` 511L, `user_profile` 803L.
4. §2 zuzenketak: `RateLimiter` 3 instantzia dira (`main.py`, `admin.py`, `auth.py`), ez 1; `ADMIN_PASSWORD` ez dago `backend/.env.example`-n (iruzkin soilik `admin/setup`); `ruff format`-ek 216 fitxategi estaltzen ditu (ez 215).
5. `tools/gen_api.py`-k `API.md` idempotente birsortzen du baina bide absolutu hardkodeatuarekin eta shebang gabe (ez eramangarria).

## 5. Mantentze-pendienteak (iradokitako ordena, egiaztapenarekin)

| # | Tarea | Estado 10/10/2026 | Cómo verificar |
| --- | --- | --- | --- |
| 1 | Migrar routers a `get_or_404` y servicios a `paginate_filtered` | `get_or_404` en 13 routers (110 usos), 186 `404` inline restantes; `paginate_filtered` con 0 usos | `Select-String "get_or_404\(" backend/app/routers; Select-String "404" backend/app/routers; Select-String "paginate_filtered" backend/app/services` |
| 2 | Migrar `python-jose` → `PyJWT` (PR aislado con tests de expiración/tipo/rotación) | Sin migrar (`app/auth.py` usa `jose`) | `Select-String "from jose\|import jose" backend/app; Select-String "import jwt" backend/app` |
| 3 | Troceo de pantallas grandes | Hecho: `festival_profile` 956L, `locations` 680L, `api_service` 511L, `chat` 767L, `user_profile` 803L (widgets extraídos en `lib/widgets/`) | `(Get-Content frontend/lib/screens/<pantalla>).Count` |
| 4 | Migrar `AlertDialog` → `ConfirmDialog` y `ScaffoldMessenger` → `showAppSnack` | 24 `AlertDialog` vs 19 usos `showConfirmDialog`; 115 `ScaffoldMessenger` vs 8 usos `showAppSnack` (los `AlertDialog` restantes son formularios: requieren `CreateEntityDialog` común) | `Select-String "AlertDialog|showConfirmDialog|ScaffoldMessenger|showAppSnack" frontend/lib` |
| 5 | Higiene formato + `.gitignore` | `ruff format --check` + `ruff check` limpios y con gate en CI (GH + GitLab); `.gitignore` cubre `*.db*`, `*.hive`, `*.lock`, `uploads/` (no el glob `*.hive*`) | `ruff format --check .; ruff check .; Get-Content .gitignore` |
