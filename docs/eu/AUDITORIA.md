# Kode-auditoria — Clakettes (09/10/2026, plataforma-aniztasun zabalkuntza 09/10/2026, berrik. 10/10/2026)

[ES](../es/AUDITORIA.md) · [EN](../en/AUDITORIA.md) · [FR](../fr/AUDITORIA.md) · [DE](../de/AUDITORIA.md) · [IT](../it/AUDITORIA.md) · [CA](../ca/AUDITORIA.md) · [EU](AUDITORIA.md) · [GL](../gl/AUDITORIA.md) · [OC](../oc/AUDITORIA.md)

## 0. Laburpen exekutiboa

Clakettes proiektuaren mendekotasunen, aplikatutako optimizazioen eta zain dagoen zor teknikoaren berrikuspena.

## 1. Kanpo-mendekotasunak: zer kendu daiteke eta zer ez

### Backend-a (`backend/requirements.txt` + `pyproject.toml`)

| Dep | Veredicto | Motivo |
| --- | --- | --- |
| fastapi, uvicorn[standard], sqlalchemy, pydantic(+settings), alembic | Mantendu | Stackaren muina |
| PyJWT==2.15.1 | Migrazioa osatuta | `python-jose` ezabatu da; `app/auth.py` eta `routers/dependencies.py`-ek PyJWT erabiltzen dute (2.10.1 → 2.15.0 → 2.15.1 bertsio-igoera) |
| python-dotenv | Ez sartuta | Ez da agertzen `pyproject.toml`/`requirements*.txt`-en, ezta `backend/`-en inportatzen ere; `pydantic-settings`-ek `.env` zuzenean kargatzen du |
| pymysql | Mantendu prod gidari gisa | MariaDB-rekin bakarrik erabiltzen da; dev-ean ez kargatzeak ez du ezer aurrezten (inportazio nagia dagoeneko SQLAlchemy-n) |
| python-multipart, email-validator, bcrypt | Mantendu | Kargak, helbide elektronikoaren baliozkotzea, pasahitz-hashak |
| reportlab 5.1.0 | Mantendu, baina inportazio nagiarekin (eginda) | Soilik `export_service._build_pdf`; lehen modulu-mailan inportatzen zen (~200 ms + memoria langile bakoitzeko). Orain funtzioaren barruan inportatzen da. Gainera `pyproject.toml` sinkronizatu zen (falta zen) eta `==5.1.0` finkatu zen |

**Bertsio finkatuak `backend/pyproject.toml` / `requirements*.txt`-en:** `fastapi==0.163.1`, `uvicorn[standard]==0.54.0`, `sqlalchemy==2.1.9`, `pydantic==2.14.3`, `pydantic-settings==2.16.3`, `email-validator==2.4.0`, `pymysql==1.2.4`, `python-multipart==0.0.34`, `PyJWT==2.15.1`, `cryptography==50.0.2`, `bcrypt>=4.3.0`, `alembic==1.20.1`, `reportlab==5.1.0`, `Pillow==13.0.0`, `mutagen==1.48.1`, `pypdf==7.1.0` (major 6.21.x-tik); garapena: `pytest>=9.2.0`, `ruff==0.17.5`, `httpx==0.28.1`, `caldav==3.7.0`, `icalendar==7.3.0`.

### Frontend-a (`frontend/pubspec.yaml`)

Mendekotasun guztiak benetako erabileran daude; bat ere ezin izan da kendu funtzionaltasuna hautsi gabe:

- `archive`: `crypto_utils.dart`-en erabilia (ZLib/GZip). `dart:io` ez du balio web-a hausten duelako.
- `path_provider`: `file_downloader_io.dart`-en erabilia (mugikorra/escritorioa).
- `web`: `file_downloader_web.dart`-en erabilia.
- `pointycastle` + `crypto`: txataren E2EE (ECDH P-256 + AES-GCM; `X25519` izena heredatutako eremu batean bakarrik agertzen da).
- `flutter_map` + `latlong2` + `geolocator` + `url_launcher`: mapak.
- `table_calendar`, `flutter_local_notifications` + `timezone` + `flutter_timezone`, `image_picker` + `file_picker`: bakoitza erabilera 1-2rekin, baina kentzeak funtzionaltasuna kenduko luke.

## 2. Aplikatutako optimizazioak

1. `export_service.py`: reportlab inportazio nagia `_build_pdf`-n + docstring.
2. `main.py` RateLimitMiddleware + `routers/admin.py` + `routers/auth.py` + `routers/auth_sessions.py` + `routers/federation.py`: 5 `RateLimiter` instantzia (`middleware:`/`dav:` bucket-ak + `reset` 3/300 s, `login` 5/300 s, `refresh` 20/60 s eta federazioa 60/60 s limiter-ak); ez bateratu muga desberdinak galdu gabe. Saihesbidea `app.config.is_testing()`-en bidez doa (`1/true/yes/on`).
3. `base_service.py`: `paginate`-k `page>=1`, `size` `[1,100]`-en finkatzen du; `paginate_filtered()` berria 0 erabilerarekin (klonatutako `get_all_paginated`-ak migratzeko daude).
4. `routers/dependencies.py`: `get_current_user_optional`-ek `validate_access_token` berrerabiltzen du (JWT+saio ~30 lerro bikoiztu kenduta); `__import__("datetime")` konponketa → inportazio normala; `get_or_404()` berria ~100 `HTTPException(404)` inline ordezkatzeko.
5. `dav/auth.py`: `app.auth.hash_token`-rekiko erlazioa dokumentatuta (lehen `_hash_token`; bateragarritasunerako aliasa gordetzen da).
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
    (2) eta kokapenen 5 router-etara (12) hedatuta. Sorta honek ez zuen migraziorik
    sartu; ondorengo berrikuspenek `a8b9c0d1e2f3` (eserlekuen bakartasuna) eta
    `b9c0d1e2f3a4` (`contest_type` laburretan) gehitu zituzten, biak head
    `b9c0d1e2f3a4`-ean jada aplikatuta.
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
Egoera: 1544 backend test (54 fitxategi) + frontend 77 fitxategitan berdean, ruff + analyze garbi.
