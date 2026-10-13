# Auditoria de codi — Clakettes (09/10/2026, ampl. multiplataforma 09/10/2026, rev. 10/10/2026)

> **Addendum 11/10/2026** (xifres verificades): backend 1402 tests en 37 fitxers;
> routers 36 fitxers (33 amb `APIRouter`); services 36; models 34; schemas 33;
> Alembic 18 versions; `docs/API.md` 310 endpoints (operationIds únics).
> RGPD: privacitat per defecte, consentiment, esborrat/exportació, purga de
> sessions, auditoria append-only, sanititzat de metadades, TLS MariaDB en prod,
> DAV amb caducitat, CSP/HSTS. Proveïdors de pagament mock/stripe/redsys.

## 0. Resum executiu (10/10/2026, xifres verificades)

| Área | Estado | Detalle |
| --- | --- | --- |
| Backend tests | 1321 `def test_` en 33 archivos | `Get-ChildItem backend/tests -Recurse -Filter "test_*.py" \| Select-String "def test_"` |
| Frontend tests | 347 bloques en 69 archivos | `Get-ChildItem frontend/test -Recurse -Filter "*_test.dart" \| Select-String "testWidgets\(|test\("` |
| Routers/Services/Models/Schemas | 35/33/33/32 archivos (33 routers con `APIRouter`) | `permissions.py`/`dependencies.py` son helpers sin router; `base.py`/`__init__.py` no son entidades |
| Migraciones | 15 + `__init__.py` | `alembic/versions/` |
| Endpoints | 294 en 33 routers (`docs/API.md` por AST) | `python tools/gen_api.py` idempotente; grep simple da 272 (no cuenta `propfind/report/options/websocket`) |
| Lint | `ruff check` + `ruff format --check` limpios (216 archivos) | `AGENTS.md` y CI (GH + GitLab) con gate de formato |
| Docs | Backend consolidado en `docs/` | `docs/BACKEND.md` + `docs/DATABASE.md`; índice en `docs/README.md` |
| Deuda principal | `get_or_404` parcial, `paginate_filtered` sin usos, `python-jose` sin migrar, 24 `AlertDialog` / 115 `ScaffoldMessenger` restantes | Ver §5 con conteos y verificación |

Com re-verificar: `cd backend; python -m ruff check .; python -m pytest tests/ -x -q --tb=short` i `cd frontend; flutter analyze; flutter test`.

## 1. Dependències externes: què es pot eliminar i què no

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

Totes les dependències són en ús real; cap s'ha pogut eliminar sense trencar funcionalitat:

- `archive`: usat a `crypto_utils.dart` (ZLib/GZip). `dart:io` no val perquè trenca web.
- `path_provider`: usat a `file_downloader_io.dart` (mòbil/desktop).
- `web`: usat a `file_downloader_web.dart`.
- `pointycastle` + `crypto` + `uuid`: E2EE del xat (X25519/ECDH P-256 + AES-GCM).
- `flutter_map` + `cancellable_tile` + `latlong2` + `geolocator` + `url_launcher`: mapes.
- `table_calendar`, `flutter_local_notifications` + `timezone` + `flutter_timezone`, `image_picker` + `file_picker`: cadascun amb 1-2 usos, però eliminar-los trauria funcionalitat.

## 2. Optimitzacions aplicades

1. `export_service.py`: import reportlab peresós a `_build_pdf` + docstring.
2. `main.py` RateLimitMiddleware + `routers/admin.py` + `routers/auth.py`: 3 instàncies `RateLimiter` (buckets `middleware:`/`dav:` + limiters de `reset` 3/300s i `login`); no unificar sense perdre límits distints.
3. `base_service.py`: `paginate` fixa `page>=1`, `size` a `[1,100]`; nou `paginate_filtered()` definit amb 0 usos (pendent migrar els `get_all_paginated` clonats).
4. `routers/dependencies.py`: `get_current_user_optional` reutilitza `validate_access_token` (elimina ~30 línies duplicades JWT+sessió); fix `__import__("datetime")` → import normal; nou `get_or_404()` per reemplaçar ~100 `HTTPException(404)` inline.
5. `dav/auth.py`: documentada la relació amb `app.auth._hash_token`.
6. `pyproject.toml`/`requirements.txt` sincronitzats (reportlab).
7. `reusable_widgets.dart`: nou `showAppSnack()` (1 def + 8 usos; queden 115 `ScaffoldMessenger` directes).

## 3. Millores multiplataforma aplicades (escriptori + web + Android + iOS/iPad)

1. `BackendConfig`: default per plataforma — emulador Android utilitza `10.0.2.2:8000`
   (localhost de l'emulador és el propi virtual, no l'host); resta `localhost:8000`.
   Prioritat: URL desada > `--dart-define=BACKEND_URL` > default per plataforma.
   `ApiService` utilitza el mateix default en constructor i getters.
2. `NotificationService`: en web (`kIsWeb`) `init` no toca plugin ni timezone
   (sense notificacions locals al navegador) i `scheduleReminder` no fa res;
   documentat al docstring. Sense branques per plataforma a les pantalles.
3. `file_downloader.dart`: verificat l'import condicional
   (`web` per defecte, `io` si `dart.library.io`) — cobreix navegador, escriptori,
   Android i iOS sense canvis.
4. `main_scaffold.dart`: afegit Cortos a la navegació (existia la pantalla
   `screenIndex 3` però sense item — inaccessible). Rail >800px (escriptori/web),
   Bar <800px (mòbil), Drawer a tots.
5. `AndroidManifest.xml`: afegits INTERNET, ACCESS_NETWORK_STATE, ubicació
   (FINE+COARSE), CAMERA, READ_MEDIA_IMAGES/VIDEO, SCHEDULE/USE_EXACT_ALARM.
   Sense INTERNET explícit els builds release no tenen xarxa.
6. `ios/Runner/Info.plist`: afegits NSLocationWhenInUse, NSCamera,
   NSPhotoLibrary (+Add). Sense aquests el sistema denega o l'App Store rebutja.
7. Backend `routers/festivals.py`: pilot `get_or_404(db, Festival/Location, ...)`
   — 9 blocs `if not → 404` eliminats; estès a `shortfilms.py` (3) i
   `users.py` (4). Patró a estendre a la resta de routers.
8. Frontend `awards_screen.dart`: error SnackBar migrat a `showAppSnack()`
   (pilot). Nota: els 24 `AlertDialog` restants són diàlegs de *formulari*
   (crear/editar), no de confirmació — no migren a `showConfirmDialog`
   (19 usos en 18 pantalles); requeririen un `CreateEntityDialog` comú.
9. CI: gate `ruff format --check` afegit (GH + GitLab) després de verificar
   `216 files already formatted`.
10. Seguretat (pilot `channels.py`, bloc seguretat): nou
    `require_channel_member`/`is_channel_member` a `permissions.py` i ús a
    `channels.py` + `chat.py` (elimina 3 blocs inline amb imports diferits);
    `channels.py` migrat a `get_or_404` (7 blocs menys); whitelist de rol
    `Literal[admin,moderator,member]` en schemas (abans: string lliure → 500
    per CheckConstraint; ara: 422); 4 tests 403/422 nous a
    `TestChannelAuthorization`.
11. Seguretat: `POST /delegations/{id}/revoke` exigia només auth — qualsevol
    revocava delegacions alienes. Ara verifica delegador o admin + test 403.
    Verificats ja OK (sense canvis): `user_roles`/`user_festival` (whitelist
    attendee), DMs (ownership), formularis públics (auth opcional), WS
    (valida sessió), `bulk_create` (single commit), SyncQueue (retry+backoff),
    i18n (0 claus absents), `locations` (didChangeDependencies amb guarda).
12. `get_or_404` estès a `committees.py` (10), `events.py` (58, via script
    amb revisió + 17 existències sense assignar per evitar F841), `delegations`
    (2) i 5 routers de localitzacions (12). Sense canvis d'esquema: no hi ha
    migració Alembic pendent per aquest lot.
13. Rendiment: filtre `venue` de programació baixat a SQL (abans filtrava
    la pàgina en Python i trencava `total`/`pages`).
14. Frontend: guardes anti-doble-enviament en crear festival/usuari/curt +
    3 SnackBars migrats a `showAppSnack`.
15. Xat: E2EE fora del UI thread — `_prepareContent`/`_unpackContent` utilitzen
    `encryptAsync`/`decryptAsync` (isolates); nous `encryptSenderKeyAsync`/
    `decryptSenderKeyAsync` usats en difusió i recepció de sender keys.
    `RestChatBackend` es conserva: l'utilitza `chat_service_test` com a fake
    (no era codi mort).
16. Xat: `chat_screen.dart` 1038 → 767 línies; bombolles a
    `widgets/chat_bubble.dart` (`ChatBubble` + `ChatBubbleWidget` amb imatge,
    ubicació, vCard, iCal) i barra a `widgets/chat_input_bar.dart`
    (`ChatInputBar`). 2 tests async nous a `crypto_utils_test`.
17. `locations_screen` 1144 → 680 línies: targetes i formulari a
    `widgets/location_cards.dart` (`LocationCard`, `LegacyCard`,
    `LegacyLocation`, `LocationFormScreen`, `LocationFormResult`); esborrat
    amb `showConfirmDialog` + `showAppSnack` (un AlertDialog menys).
18. `festival_profile_screen` 1276 → 956 línies: `RulebooksSection` i
    `FestivalLocationsSection` (+ mapa i fitxes) a
    `widgets/festival_sections.dart`. La pantalla conserva estat,
    lectura, edició i callbacks.
19. `api_service.dart` 1134 → 511 línies: 95 mètodes moguts a `lib/services/api/`
    (`event_api` 31, `location_api` 25, `org_api` 17, `catalog_api` 13,
    resta a `user_api` + `calendar/channel/festival/form`). El nucli conserva config, auth, transport i
    admin/cerca. API pública intacta.
20. `user_profile_screen` 996 → 803 línies: `SessionsCard` i `AliasesCard`
    a `widgets/user_profile_cards.dart`. Corregits 4 `if` sense claus
    heretats a `catalog_api`.
21. Tests de flux (`tests/integration/test_flows.py`): reserva completa
    (festival → esdeveniment → seients → reserva → ocupació), missatgeria
    (canal → membre → DM → lectura → esborrat) i delegació (crear →
    llistar → revocar).
22. Widget tests dels widgets extrets (13): `chat_bubble`,
    `chat_input_bar`, `user_profile_cards`, `location_cards`. Nota: els
    widgets sota `wrapWithLocalization` necessiten un `pump()` extra
    (el Builder de localització resol en el segon frame).
23. Push natiu sense Firebase (`docs/PUSH.ca.md`): Notification API del navegador
    en web (`notification_web.dart` + stub amb export condicional, sense deps
    noves), `flutter_local_notifications` en escriptori + permís macOS en
    iniciar, mòbil en no-op explícit (`_supported`). `flutter build web`
    verificat.
24. Documentació: `docs/API.md` (294 endpoints en 33 routers, generada per
    AST amb `tools/gen_api.py` — regenerable), `docs/ARQUITECTURA.ca.md`
    (capes, fluxos, decisions multiplataforma), `docs/USO.ca.md` (arrencada,
    env, operació, rols), `docs/DESARROLLO.ca.md` (convencions + portes
    CI), `docs/SEGURIDAD.ca.md` (tokens, matriu de permisos, checklist prod),
    `docs/BACKEND.ca.md` + `docs/DATABASE.ca.md` (mogudes des de `backend/` el 10/10/2026).
    READMEs i `AGENTS.md` amb xifres reals; admin dev `admin`/`setup`
    (sense `ADMIN_PASSWORD` a `.env.example`; seed només no-prod a `app/main.py:257`).
Estat: 1321 tests backend (33 fitxers) + 347 frontend (69 fitxers) en verd, ruff + analyze nets.

## 4. Revisió 10/10/2026 (correccions a §2–§3)

1. Docs backend consolidades: `backend/BACKEND.md` + `backend/DATABASE.md` → `docs/BACKEND.ca.md` + `docs/DATABASE.ca.md`; enllaços actualitzats a `README.ca.md`, `AGENTS.md`, `docs/README.ca.md`, `ARQUITECTURA.ca.md`, `USO.ca.md`, `ADMINISTRACION.ca.md`.
2. Compte real: routers 35 fitxers (33 amb `APIRouter`; `permissions.py`/`dependencies.py` són helpers), services 33 mòduls (+`__init__`), models 33 entitats (+`base.py`+`__init__`), schemas 32, Alembic 15, `API.md` 294 endpoints/33 routers (AST compta `propfind/report/options/websocket`; grep simple dóna 272).
3. Tests: backend 1321 `def test_` en 33 fitxers (no 1366/38); frontend 347 blocs en 69 fitxers (no 313/70). Widgets 24 OK. Pantalles: `festival_profile` 956L, `locations` 680L, `chat` 767L, `api_service` 511L, `user_profile` 803L.
4. Correccions a §2: `RateLimiter` són 3 instàncies (`main.py`, `admin.py`, `auth.py`), no 1; `ADMIN_PASSWORD` no existeix a `backend/.env.example` (només comentari `admin/setup`); `ruff format` cobreix 216 fitxers (no 215).
5. `tools/gen_api.py` regenera `API.md` idempotent però amb ruta absoluta hardcodejada i sense shebang (no portable).

## 5. Mantenibilitat pendent (ordre suggerit, amb verificació)

| # | Tarea | Estado 10/10/2026 | Cómo verificar |
| --- | --- | --- | --- |
| 1 | Migrar routers a `get_or_404` y servicios a `paginate_filtered` | `get_or_404` en 13 routers (110 usos), 186 `404` inline restantes; `paginate_filtered` con 0 usos | `Select-String "get_or_404\(" backend/app/routers; Select-String "404" backend/app/routers; Select-String "paginate_filtered" backend/app/services` |
| 2 | Migrar `python-jose` → `PyJWT` (PR aislado con tests de expiración/tipo/rotación) | Sin migrar (`app/auth.py` usa `jose`) | `Select-String "from jose\|import jose" backend/app; Select-String "import jwt" backend/app` |
| 3 | Troceo de pantallas grandes | Hecho: `festival_profile` 956L, `locations` 680L, `api_service` 511L, `chat` 767L, `user_profile` 803L (widgets extraídos en `lib/widgets/`) | `(Get-Content frontend/lib/screens/<pantalla>).Count` |
| 4 | Migrar `AlertDialog` → `ConfirmDialog` y `ScaffoldMessenger` → `showAppSnack` | 24 `AlertDialog` vs 19 usos `showConfirmDialog`; 115 `ScaffoldMessenger` vs 8 usos `showAppSnack` (los `AlertDialog` restantes son formularios: requieren `CreateEntityDialog` común) | `Select-String "AlertDialog|showConfirmDialog|ScaffoldMessenger|showAppSnack" frontend/lib` |
| 5 | Higiene formato + `.gitignore` | `ruff format --check` + `ruff check` limpios y con gate en CI (GH + GitLab); `.gitignore` cubre `*.db*`, `*.hive`, `*.lock`, `uploads/` (no el glob `*.hive*`) | `ruff format --check .; ruff check .; Get-Content .gitignore` |
