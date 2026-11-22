# Auditoria de còde — Clakettes (09/10/2026, ampl. multiplataforma 09/10/2026, rev. 10/10/2026)

[ES](../es/AUDITORIA.md) · [EN](../en/AUDITORIA.md) · [FR](../fr/AUDITORIA.md) · [DE](../de/AUDITORIA.md) · [IT](../it/AUDITORIA.md) · [CA](../ca/AUDITORIA.md) · [EU](../eu/AUDITORIA.md) · [GL](../gl/AUDITORIA.md) · [OC](AUDITORIA.md)

## 0. Resumit executiu

Revista de las dependéncias, de las optimizacions aplicadas e de la dèta tecnica en espèra del projècte Clakettes.

## 1. Dependéncias extèrnas: çò que se pòt eliminar e çò que non

### Backend (`backend/requirements.txt` + `pyproject.toml`)

| Dep | Veredicto | Motivo |
| --- | --- | --- |
| fastapi, uvicorn[standard], sqlalchemy, pydantic(+settings), alembic | Manténer | Nucli de la pila |
| PyJWT==2.15.1 | Migracion acabada | `python-jose` eliminat; `app/auth.py` e `routers/dependencies.py` utilizan PyJWT (bump 2.10.1 → 2.15.0 → 2.15.1) |
| python-dotenv | Non inclusa | Figura pas dins `pyproject.toml`/`requirements*.txt` ni es importa dins `backend/`; `pydantic-settings` carga `.env` dirèctament |
| pymysql | Manténer coma pilòt prod | Utilizat sonque amb MariaDB; lo cargar pas en dev non estalvia res (import peresós ja dins SQLAlchemy) |
| python-multipart, email-validator, bcrypt | Manténer | Mandadís, validacion de l'email, hash dels senhals |
| reportlab 5.1.0 | Manténer, mas amb import peresós (fait) | Sonque `export_service._build_pdf`; abans importat al nivèl del modul (~200 ms + memòria per cada worker). Ara importat dedins la foncion. En mai `pyproject.toml` foguèt sincronizat (manquava) e fixat `==5.1.0` |

**Versiones fixadas dins `backend/pyproject.toml` / `requirements*.txt`:** `fastapi==0.163.1`, `uvicorn[standard]==0.54.0`, `sqlalchemy==2.1.9`, `pydantic==2.14.3`, `pydantic-settings==2.16.3`, `email-validator==2.4.0`, `pymysql==1.2.4`, `python-multipart==0.0.34`, `PyJWT==2.15.1`, `cryptography==50.0.2`, `bcrypt>=4.3.0`, `alembic==1.20.1`, `reportlab==5.1.0`, `Pillow==13.0.0`, `mutagen==1.48.1`, `pypdf==7.1.0` (major dempuèi 6.21.x); desvolopament: `pytest>=9.2.0`, `ruff==0.17.5`, `httpx==0.28.1`, `caldav==3.7.0`, `icalendar==7.3.0`.

### Frontend (`frontend/pubspec.yaml`)

Totas las dependéncias son en usatge reau; cap se poguèt levar sens rompre foncionalitat:

- `archive`: utilizat en `crypto_utils.dart` (ZLib/GZip). `dart:io` non vai perque rompe web.
- `path_provider`: utilizat en `file_downloader_io.dart` (mobil/desktop).
- `web`: utilizat en `file_downloader_web.dart`.
- `pointycastle` + `crypto`: E2EE del chat (ECDH P-256 + AES-GCM; lo nom `X25519` apareis sonque dins un camp eretat).
- `flutter_map` + `latlong2` + `geolocator` + `url_launcher`: mapas.
- `table_calendar`, `flutter_local_notifications` + `timezone` + `flutter_timezone`, `image_picker` + `file_picker`: cada un amb 1-2 usatges, mas los levar trairiá foncionalitat.

## 2. Optimizacions aplicadas

1. `export_service.py`: import reportlab peresós en `_build_pdf` + docstring.
2. `main.py` RateLimitMiddleware + `routers/admin.py` + `routers/auth.py` + `routers/auth_sessions.py` + `routers/federation.py`: 5 instàncias `RateLimiter` (buckets `middleware:`/`dav:` + limiters de `reset` 3/300 s, `login` 5/300 s, `refresh` 20/60 s e federacion 60/60 s); non unificar sens pèrdre limits distints. Lo bypass passa per `app.config.is_testing()` (`1/true/yes/on`).
3. `base_service.py`: `paginate` fixa `page>=1`, `size` en `[1,100]`; nòu `paginate_filtered()` definit amb 0 usatges (pendent migrar los `get_all_paginated` clonats).
4. `routers/dependencies.py`: `get_current_user_optional` reutiliza `validate_access_token` (elimina ~30 linhas duplicadas JWT+session); fix `__import__("datetime")` → import normau; nòu `get_or_404()` per remplaçar ~100 `HTTPException(404)` inline.
5. `dav/auth.py`: documentada la relacion amb `app.auth.hash_token` (abans `_hash_token`; se consèrva l'alias per compatibilitat).
6. `pyproject.toml`/`requirements.txt` sincronizats (reportlab).
7. `reusable_widgets.dart`: nòu `showAppSnack()` (1 def + 8 usatges; demòran 115 `ScaffoldMessenger` dirèctes).

## 3. Amelhoraments multiplataforma aplicats (escritòri + web + Android + iOS/iPad)

1. `BackendConfig`: defaut per plataforma — emulador Android utiliza `10.0.2.2:8000`
   (localhost de l'emulador es lo virtuau meteis, non l'òste); rèsta `localhost:8000`.
   Prioritat: URL gardada > `--dart-define=BACKEND_URL` > defaut per plataforma.
   `ApiService` utiliza lo meteis defaut en constructor e getters.
2. `NotificationService`: en web (`kIsWeb`) `init` non tòca plugin ni timezone
   (sens notificacions localas en navegador) e `scheduleReminder` fa pas res;
   documentat dins lo docstring. Sens brancas per plataforma dins los ecrans.
3. `file_downloader.dart`: verificat l'import condicionau
   (`web` per defaut, `io` se `dart.library.io`) — cubrís navegador, escritòri,
   Android e iOS sens cambiaments.
4. `main_scaffold.dart`: apondut Corts a la navegacion (existissiá l'ecran
   `screenIndex 3` mas sens item — inaccessible). Rail >800px (escritòri/web),
   Bar <800px (mobil), Drawer en totes.
5. `AndroidManifest.xml`: aponduts INTERNET, ACCESS_NETWORK_STATE, ubicacion
   (FINE+COARSE), CAMERA, READ_MEDIA_IMAGES/VIDEO, SCHEDULE/USE_EXACT_ALARM.
   Sens INTERNET explicite los builds release an pas de ret.
6. `ios/Runner/Info.plist`: aponduts NSLocationWhenInUse, NSCamera,
   NSPhotoLibrary (+Add). Sens aquò lo sistèma denèga o l'App Store refusa.
7. Backend `routers/festivals.py`: pilòt `get_or_404(db, Festival/Location, ...)`
   — 9 blòcs `if not → 404` eliminats; estendut a `shortfilms.py` (3) e
   `users.py` (4). Patron a estendre a la rèsta de routers.
8. Frontend `awards_screen.dart`: error SnackBar migrat cap a `showAppSnack()`
   (pilòt). Nòta: los 24 `AlertDialog` demorants son dialògs de *formulari*
   (crear/editar), non de confirmacion — migran pas cap a `showConfirmDialog`
   (19 usatges en 18 ecrans); requeririán un `CreateEntityDialog` comun.
9. CI: pòrta `ruff format --check` aponduda (GH + GitLab) aprèp verificar
   `216 files already formatted`.
10. Seguretat (pilòt `channels.py`, blòc seguretat): nòu
    `require_channel_member`/`is_channel_member` en `permissions.py` e usatge en
    `channels.py` + `chat.py` (elimina 3 blòcs inline amb imports diferits);
    `channels.py` migrat cap a `get_or_404` (7 blòcs mens); whitelist de ròtle
    `Literal[admin,moderator,member]` en schemas (abans: string liure → 500
    per CheckConstraint; ara: 422); 4 tèsts 403/422 nòus en
    `TestChannelAuthorization`.
11. Seguretat: `POST /delegations/{id}/revoke` exigissiá sonque auth — qual que siá
    revocava delegacions d'autrui. Ara verifica delegador o admin + tèst 403.
    Verificats ja OK (sens cambiaments): `user_roles`/`user_festival` (whitelist
    attendee), DMs (ownership), formularis publics (auth opcionau), WS
    (valida session), `bulk_create` (single commit), SyncQueue (retry+backoff),
    i18n (0 claus absentas), `locations` (didChangeDependencies amb garda).
12. `get_or_404` estendut a `committees.py` (10), `events.py` (58, via script
    amb revision + 17 existéncias sens assignar per evitar F841), `delegations`
    (2) e 5 routers de localizacions (12). Aqueste lòt introduís pas de migracion;
    de revisions posterioras apondèron `a8b9c0d1e2f3` (unicitat de sètge) e
    `b9c0d1e2f3a4` (`contest_type` dins los corts), ambedas ja aplicadas al head
    `b9c0d1e2f3a4`.
13. Rendiment: filtre `venue` de programacion davalat cap a SQL (abans filtrava
    la pagina en Python e rompiá `total`/`pages`).
14. Frontend: gardas anti-doble-mandadís en crear festivau/utilizaire/cort +
    3 SnackBars migrats cap a `showAppSnack`.
15. Chat: E2EE fòra del UI thread — `_prepareContent`/`_unpackContent` utilizan
    `encryptAsync`/`decryptAsync` (isolates); nòus `encryptSenderKeyAsync`/
    `decryptSenderKeyAsync` utilizats en difusion e recepcion de sender keys.
    `RestChatBackend` se consèrva: l'utiliza `chat_service_test` coma fake
    (non èra còde mòrt).
16. Chat: `chat_screen.dart` 1038 → 767 linhas; borbolhas cap a
    `widgets/chat_bubble.dart` (`ChatBubble` + `ChatBubbleWidget` amb imatge,
    ubicacion, vCard, iCal) e barra cap a `widgets/chat_input_bar.dart`
    (`ChatInputBar`). 2 tèsts async nòus en `crypto_utils_test`.
17. `locations_screen` 1144 → 680 linhas: cartas e formulari cap a
    `widgets/location_cards.dart` (`LocationCard`, `LegacyCard`,
    `LegacyLocation`, `LocationFormScreen`, `LocationFormResult`); escafament
    amb `showConfirmDialog` + `showAppSnack` (un AlertDialog mens).
18. `festival_profile_screen` 1276 → 956 linhas: `RulebooksSection` e
    `FestivalLocationsSection` (+ mapa e fichas) cap a
    `widgets/festival_sections.dart`. L'ecran consèrva estat,
    lectura, edicion e callbacks.
19. `api_service.dart` 1134 → 511 linhas: 95 metòdes moguts cap a `lib/services/api/`
    (`event_api` 31, `location_api` 25, `org_api` 17, `catalog_api` 13,
    rèsta cap a `user_api` + `calendar/channel/festival/form`). Lo nuclèu consèrva config, auth, transpòrt e
    admin/cèrca. API publica intacta.
20. `user_profile_screen` 996 → 803 linhas: `SessionsCard` e `AliasesCard`
    cap a `widgets/user_profile_cards.dart`. Corregits 4 `if` sens claus
    eiretats en `catalog_api`.
21. Tèsts de flux (`tests/integration/test_flows.py`): resèrva completa
    (festivau → eveniment → sèts → resèrva → ocupacion), messatjariá
    (canau → membre → DM → lectura → escafament) e delegacion (crear →
    listar → revocar).
22. Widget tests dels widgets extraches (13): `chat_bubble`,
    `chat_input_bar`, `user_profile_cards`, `location_cards`. Nòta: los
    widgets jos `wrapWithLocalization` an besonh d'un `pump()` extra
    (lo Builder de localizacion resòlv dins lo segond frame).
23. Push natiu sens Firebase (`docs/oc/PUSH.md`): Notification API del navegador
    en web (`notification_web.dart` + stub amb export condicionau, sens deps
    nòvas), `flutter_local_notifications` en escritòri + permission macOS a
    l'iniciar, mobil en no-op explicite (`_supported`). `flutter build web`
    verificat.
24. Documentacion: `docs/es/API.md`, `docs/oc/ARQUITECTURA.md`
    (capas, fluxes, decisions multiplataforma), `docs/oc/USO.md` (aviada,
    env, operacion, ròtles), `docs/oc/DESARROLLO.md` (convencions + pòrtas
    CI), `docs/oc/SEGURIDAD.md` (tokens, matritz de permissions, checklist prod),
    `docs/oc/BACKEND.md` + `docs/oc/DATABASE.md` (mogudas dempuèi `backend/` lo 10/10/2026).
    READMEs e `AGENTS.md` amb chifras realas; admin dev `admin`/`setup`
    (sens `ADMIN_PASSWORD` en `.env.example`; seed sonque non-prod en `app/main.py:257`).
