# Auditoria de còde — Clakettes (09/10/2026, ampl. multiplataforma 09/10/2026, rev. 10/10/2026)

[ES](../es/AUDITORIA.md) · [EN](../en/AUDITORIA.md) · [FR](../fr/AUDITORIA.md) · [DE](../de/AUDITORIA.md) · [IT](../it/AUDITORIA.md) · [CA](../ca/AUDITORIA.md) · [EU](../eu/AUDITORIA.md) · [GL](../gl/AUDITORIA.md) · [OC](AUDITORIA.md)

> **Addendum 11/10/2026** (chifras verificadas): backend 1402 tèsts en 37 fichièrs;
> routers 36 fichièrs (33 amb `APIRouter`); services 36; models 34; schemas 33;
> Alembic 18 versions; `docs/es/API.md` 310 endpoints (operationIds unics).
> RGPD: privacitat per defaut, consentiment, escafament/exportacion, purga de
> sessions, auditoria append-only, sanitizat de metadonadas, TLS MariaDB en prod,
> DAV amb caducitat, CSP/HSTS. Fornidors de pagament mock/stripe/redsys.

## 0. Resumit executiu (10/10/2026, chifras verificadas)

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

Cossí tornar verificar: `cd backend; python -m ruff check .; python -m pytest tests/ -x -q --tb=short` e `cd frontend; flutter analyze; flutter test`.

## 1. Dependéncias extèrnas: çò que se pòt eliminar e çò que non

### Backend (`backend/requirements.txt` + `pyproject.toml`)

| Dep | Veredicto | Motivo |
| --- | --- | --- |
| fastapi, uvicorn[standard], sqlalchemy, pydantic(+settings), alembic | Mantener | Núcleo del stack |
| python-jose[cryptography] | Mantener por ahora, migrar a PyJWT en el futuro | Abandonado desde 2016, pero el cambio toca `app/auth.py` + `routers/dependencies.py` + tests; hacerlo en PR separado con tests de tokens |
| python-dotenv | Mantener | Requerido por `pydantic-settings>=2` y `uvicorn[standard]` (`--env-file`); solo 2 scripts lo importan directamente, pero quitarlo rompería la carga de `.env` |
| pymysql | Mantener como driver prod | Solo se usa con MariaDB; no cargarlo en dev no ahorra nada (import perezoso ya en SQLAlchemy) |
| python-multipart, email-validator, bcrypt | Mantener | Uploads, validación email, hash passwords |
| reportlab 5.0.1 | Mantener, pero con import perezoso (hecho) | Solo `export_service._build_pdf`; antes se importaba a nivel de módulo (~200 ms + memoria en cada worker). Ahora import dentro de la función. Además se sincronizó `pyproject.toml` (faltaba) y se pineó `==5.0.1` |

### Frontend (`frontend/pubspec.yaml`)

Totas las dependéncias son en usatge reau; cap se poguèt levar sens rompre foncionalitat:

- `archive`: utilizat en `crypto_utils.dart` (ZLib/GZip). `dart:io` non vai perque rompe web.
- `path_provider`: utilizat en `file_downloader_io.dart` (mobil/desktop).
- `web`: utilizat en `file_downloader_web.dart`.
- `pointycastle` + `crypto` + `uuid`: E2EE del chat (X25519/ECDH P-256 + AES-GCM).
- `flutter_map` + `cancellable_tile` + `latlong2` + `geolocator` + `url_launcher`: mapas.
- `table_calendar`, `flutter_local_notifications` + `timezone` + `flutter_timezone`, `image_picker` + `file_picker`: cada un amb 1-2 usatges, mas los levar trairiá foncionalitat.

## 2. Optimizacions aplicadas

1. `export_service.py`: import reportlab peresós en `_build_pdf` + docstring.
2. `main.py` RateLimitMiddleware + `routers/admin.py` + `routers/auth.py`: 3 instàncias `RateLimiter` (buckets `middleware:`/`dav:` + limiters de `reset` 3/300s e `login`); non unificar sens pèrdre limits distints.
3. `base_service.py`: `paginate` fixa `page>=1`, `size` en `[1,100]`; nòu `paginate_filtered()` definit amb 0 usatges (pendent migrar los `get_all_paginated` clonats).
4. `routers/dependencies.py`: `get_current_user_optional` reutiliza `validate_access_token` (elimina ~30 linhas duplicadas JWT+session); fix `__import__("datetime")` → import normau; nòu `get_or_404()` per remplaçar ~100 `HTTPException(404)` inline.
5. `dav/auth.py`: documentada la relacion amb `app.auth._hash_token`.
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
    (2) e 5 routers de localizacions (12). Sens cambiaments d'esquèma: i a pas
    migracion Alembic pendenta per aqueste lòt.
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
24. Documentacion: `docs/es/API.md` (294 endpoints en 33 routers, generada per
    AST amb `tools/gen_api.py` — regenerabla), `docs/oc/ARQUITECTURA.md`
    (capas, fluxes, decisions multiplataforma), `docs/oc/USO.md` (aviada,
    env, operacion, ròtles), `docs/oc/DESARROLLO.md` (convencions + pòrtas
    CI), `docs/oc/SEGURIDAD.md` (tokens, matritz de permissions, checklist prod),
    `docs/oc/BACKEND.md` + `docs/oc/DATABASE.md` (mogudas dempuèi `backend/` lo 10/10/2026).
    READMEs e `AGENTS.md` amb chifras realas; admin dev `admin`/`setup`
    (sens `ADMIN_PASSWORD` en `.env.example`; seed sonque non-prod en `app/main.py:257`).
Estat: 1321 tèsts backend (33 fichièrs) + 347 frontend (69 fichièrs) en verd, ruff + analyze netes.

## 4. Revision 10/10/2026 (correccions a §2–§3)

1. Docs backend consolidadas: `backend/BACKEND.md` + `backend/DATABASE.md` → `docs/oc/BACKEND.md` + `docs/oc/DATABASE.md`; ligams actualizats en `README.oc.md`, `AGENTS.md`, `docs/oc/README.md`, `ARQUITECTURA.md`, `USO.md`, `ADMINISTRACION.md`.
2. Compte reau: routers 35 fichièrs (33 amb `APIRouter`; `permissions.py`/`dependencies.py` son helpers), services 33 moduls (+`__init__`), models 33 entitats (+`base.py`+`__init__`), schemas 32, Alembic 15, `API.md` 294 endpoints/33 routers (AST compta `propfind/report/options/websocket`; grep simple dona 272).
3. Tèsts: backend 1321 `def test_` en 33 fichièrs (non 1366/38); frontend 347 blòcs en 69 fichièrs (non 313/70). Widgets 24 OK. Ecrans: `festival_profile` 956L, `locations` 680L, `chat` 767L, `api_service` 511L, `user_profile` 803L.
4. Correccions a §2: `RateLimiter` son 3 instàncias (`main.py`, `admin.py`, `auth.py`), non 1; `ADMIN_PASSWORD` existís pas en `backend/.env.example` (sonque comentari `admin/setup`); `ruff format` cubrís 216 fichièrs (non 215).
5. `tools/gen_api.py` regenera `API.md` idempotent mas amb rota absoluda hardcodeada e sens shebang (non portable).

## 5. Mantenença pendenta (òrdre suggerit, amb verificacion)

| # | Tarea | Estado 10/10/2026 | Cómo verificar |
| --- | --- | --- | --- |
| 1 | Migrar routers a `get_or_404` y servicios a `paginate_filtered` | `get_or_404` en 13 routers (110 usos), 186 `404` inline restantes; `paginate_filtered` con 0 usos | `Select-String "get_or_404\(" backend/app/routers; Select-String "404" backend/app/routers; Select-String "paginate_filtered" backend/app/services` |
| 2 | Migrar `python-jose` → `PyJWT` (PR aislado con tests de expiración/tipo/rotación) | Sin migrar (`app/auth.py` usa `jose`) | `Select-String "from jose\|import jose" backend/app; Select-String "import jwt" backend/app` |
| 3 | Troceo de pantallas grandes | Hecho: `festival_profile` 956L, `locations` 680L, `api_service` 511L, `chat` 767L, `user_profile` 803L (widgets extraídos en `lib/widgets/`) | `(Get-Content frontend/lib/screens/<pantalla>).Count` |
| 4 | Migrar `AlertDialog` → `ConfirmDialog` y `ScaffoldMessenger` → `showAppSnack` | 24 `AlertDialog` vs 19 usos `showConfirmDialog`; 115 `ScaffoldMessenger` vs 8 usos `showAppSnack` (los `AlertDialog` restantes son formularios: requieren `CreateEntityDialog` común) | `Select-String "AlertDialog|showConfirmDialog|ScaffoldMessenger|showAppSnack" frontend/lib` |
| 5 | Higiene formato + `.gitignore` | `ruff format --check` + `ruff check` limpios y con gate en CI (GH + GitLab); `.gitignore` cubre `*.db*`, `*.hive`, `*.lock`, `uploads/` (no el glob `*.hive*`) | `ruff format --check .; ruff check .; Get-Content .gitignore` |
