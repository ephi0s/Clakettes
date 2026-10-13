# Auditoría de código — Clakettes (09/10/2026, ampl. multiplataforma 09/10/2026, rev. 10/10/2026)

> **Addendum 11/10/2026** (cifras verificadas): backend 1402 tests en 37 archivos;
> routers 36 ficheros (33 con `APIRouter`); services 36; models 34; schemas 33;
> Alembic 18 versiones; `docs/API.md` 310 endpoints (operationIds únicos).
> RGPD: privacidad por defecto, consentimiento, borrado/exportación, purga de
> sesiones, auditoría append-only, sanitizado de metadatos, TLS MariaDB en prod,
> DAV con caducidad, CSP/HSTS. Proveedores de pago mock/stripe/redsys.

## 0. Resumen ejecutivo (10/10/2026, cifras verificadas)

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

Cómo re-verificar: `cd backend; python -m ruff check .; python -m pytest tests/ -x -q --tb=short` y `cd frontend; flutter analyze; flutter test`.

## 1. Dependencias externas: qué se puede eliminar y qué no

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

Todas las dependencias están en uso real; ninguna se pudo eliminar sin romper funcionalidad:

- `archive`: usado en `crypto_utils.dart` (ZLib/GZip). `dart:io` no vale porque rompe web.
- `path_provider`: usado en `file_downloader_io.dart` (móvil/desktop).
- `web`: usado en `file_downloader_web.dart`.
- `pointycastle` + `crypto` + `uuid`: E2EE del chat (X25519/ECDH P-256 + AES-GCM).
- `flutter_map` + `cancellable_tile` + `latlong2` + `geolocator` + `url_launcher`: mapas.
- `table_calendar`, `flutter_local_notifications` + `timezone` + `flutter_timezone`, `image_picker` + `file_picker`: cada uno con 1-2 usos, pero eliminarlos quitaría funcionalidad.

## 2. Optimizaciones aplicadas

1. `export_service.py`: import reportlab perezoso en `_build_pdf` + docstring.
2. `main.py` RateLimitMiddleware + `routers/admin.py` + `routers/auth.py`: 3 instancias `RateLimiter` (buckets `middleware:`/`dav:` + limiters de `reset` 3/300s y `login`); no unificar sin perder límites distintos.
3. `base_service.py`: `paginate` fija `page>=1`, `size` en `[1,100]`; nuevo `paginate_filtered()` definido con 0 usos (pendiente migrar los `get_all_paginated` clonados).
4. `routers/dependencies.py`: `get_current_user_optional` reutiliza `validate_access_token` (elimina ~30 líneas duplicadas JWT+sesión); fix `__import__("datetime")` → import normal; nuevo `get_or_404()` para reemplazar ~100 `HTTPException(404)` inline.
5. `dav/auth.py`: documentada la relación con `app.auth._hash_token`.
6. `pyproject.toml`/`requirements.txt` sincronizados (reportlab).
7. `reusable_widgets.dart`: nuevo `showAppSnack()` (1 def + 8 usos; quedan 115 `ScaffoldMessenger` directos).

## 3. Mejoras multiplataforma aplicadas (escritorio + web + Android + iOS/iPad)

1. `BackendConfig`: default por plataforma — emulador Android usa `10.0.2.2:8000`
   (localhost del emulador es el propio virtual, no el host); resto `localhost:8000`.
   Prioridad: URL guardada > `--dart-define=BACKEND_URL` > default por plataforma.
   `ApiService` usa el mismo default en constructor y getters.
2. `NotificationService`: en web (`kIsWeb`) `init` no toca plugin ni timezone
   (sin notificaciones locales en navegador) y `scheduleReminder` no hace nada;
   documentado en el docstring. Sin ramas por plataforma en las pantallas.
3. `file_downloader.dart`: verificado el import condicional
   (`web` por defecto, `io` si `dart.library.io`) — cubre navegador, escritorio,
   Android e iOS sin cambios.
4. `main_scaffold.dart`: añadido Cortos a la navegación (existía la pantalla
   `screenIndex 3` pero sin item — inaccesible). Rail >800px (escritorio/web),
   Bar <800px (móvil), Drawer en todos.
5. `AndroidManifest.xml`: añadidos INTERNET, ACCESS_NETWORK_STATE, ubicación
   (FINE+COARSE), CAMERA, READ_MEDIA_IMAGES/VIDEO, SCHEDULE/USE_EXACT_ALARM.
   Sin INTERNET explícito los builds release no tienen red.
6. `ios/Runner/Info.plist`: añadidos NSLocationWhenInUse, NSCamera,
   NSPhotoLibrary (+Add). Sin estos el sistema deniega o la App Store rechaza.
7. Backend `routers/festivals.py`: piloto `get_or_404(db, Festival/Location, ...)`
   — 9 bloques `if not → 404` eliminados; extendido a `shortfilms.py` (3) y
   `users.py` (4). Patrón a extender al resto de routers.
8. Frontend `awards_screen.dart`: error SnackBar migrado a `showAppSnack()`
   (piloto). Nota: los 24 `AlertDialog` restantes son diálogos de *formulario*
   (crear/editar), no de confirmación — no migran a `showConfirmDialog`
   (19 usos en 18 pantallas); requerirían un `CreateEntityDialog` común.
9. CI: gate `ruff format --check` añadido (GH + GitLab) tras verificar
   `216 files already formatted`.
10. Seguridad (piloto `channels.py`, bloque seguridad): nuevo
    `require_channel_member`/`is_channel_member` en `permissions.py` y uso en
    `channels.py` + `chat.py` (elimina 3 bloques inline con imports diferidos);
    `channels.py` migrado a `get_or_404` (7 bloques menos); whitelist de rol
    `Literal[admin,moderator,member]` en schemas (antes: string libre → 500
    por CheckConstraint; ahora: 422); 4 tests 403/422 nuevos en
    `TestChannelAuthorization`.
11. Seguridad: `POST /delegations/{id}/revoke` exigía solo auth — cualquiera
    revocaba delegaciones ajenas. Ahora verifica delegador o admin + test 403.
    Verificados ya OK (sin cambios): `user_roles`/`user_festival` (whitelist
    attendee), DMs (ownership), formularios públicos (auth opcional), WS
    (valida sesión), `bulk_create` (single commit), SyncQueue (retry+backoff),
    i18n (0 claves ausentes), `locations` (didChangeDependencies con guarda).
12. `get_or_404` extendido a `committees.py` (10), `events.py` (58, vía script
    con revisión + 17 existencias sin asignar para evitar F841), `delegations`
    (2) y 5 routers de localizaciones (12). Sin cambios de esquema: no hay
    migración Alembic pendiente por este lote.
13. Rendimiento: filtro `venue` de programacion bajado a SQL (antes filtraba
    la página en Python y rompía `total`/`pages`).
14. Frontend: guardas anti-doble-envío en crear festival/usuario/corto +
    3 SnackBars migrados a `showAppSnack`.
15. Chat: E2EE fuera del UI thread — `_prepareContent`/`_unpackContent` usan
    `encryptAsync`/`decryptAsync` (isolates); nuevos `encryptSenderKeyAsync`/
    `decryptSenderKeyAsync` usados en difusión y recepción de sender keys.
    `RestChatBackend` se conserva: lo usa `chat_service_test` como fake
    (no era código muerto).
16. Chat: `chat_screen.dart` 1038 → 767 líneas; burbujas a
    `widgets/chat_bubble.dart` (`ChatBubble` + `ChatBubbleWidget` con imagen,
    ubicación, vCard, iCal) y barra a `widgets/chat_input_bar.dart`
    (`ChatInputBar`). 2 tests async nuevos en `crypto_utils_test`.
17. `locations_screen` 1144 → 680 líneas: tarjetas y formulario a
    `widgets/location_cards.dart` (`LocationCard`, `LegacyCard`,
    `LegacyLocation`, `LocationFormScreen`, `LocationFormResult`); borrado
    con `showConfirmDialog` + `showAppSnack` (un AlertDialog menos).
18. `festival_profile_screen` 1276 → 956 líneas: `RulebooksSection` y
    `FestivalLocationsSection` (+ mapa y fichas) a
    `widgets/festival_sections.dart`. La pantalla conserva estado,
    lectura, edición y callbacks.
19. `api_service.dart` 1134 → 511 líneas: 95 métodos movidos a `lib/services/api/`
    (`event_api` 31, `location_api` 25, `org_api` 17, `catalog_api` 13,
    resto a `user_api` + `calendar/channel/festival/form`). El núcleo conserva config, auth, transporte y
    admin/búsqueda. API pública intacta.
20. `user_profile_screen` 996 → 803 líneas: `SessionsCard` y `AliasesCard`
    a `widgets/user_profile_cards.dart`. Corregidos 4 `if` sin llaves
    heredados en `catalog_api`.
21. Tests de flujo (`tests/integration/test_flows.py`): reserva completa
    (festival → evento → asientos → reserva → ocupación), mensajería
    (canal → miembro → DM → lectura → borrado) y delegación (crear →
    listar → revocar).
22. Widget tests de los widgets extraídos (13): `chat_bubble`,
    `chat_input_bar`, `user_profile_cards`, `location_cards`. Nota: los
    widgets bajo `wrapWithLocalization` necesitan un `pump()` extra
    (el Builder de localización resuelve en el segundo frame).
23. Push nativo sin Firebase (`docs/PUSH.md`): Notification API del navegador
    en web (`notification_web.dart` + stub con export condicional, sin deps
    nuevas), `flutter_local_notifications` en escritorio + permiso macOS al
    iniciar, móvil en no-op explícito (`_supported`). `flutter build web`
    verificado.
24. Documentación: `docs/API.md` (294 endpoints en 33 routers, generada por
    AST con `tools/gen_api.py` — regenerable), `docs/ARQUITECTURA.md`
    (capas, flujos, decisiones multiplataforma), `docs/USO.md` (arranque,
    env, operación, roles), `docs/DESARROLLO.md` (convenciones + puertas
    CI), `docs/SEGURIDAD.md` (tokens, matriz de permisos, checklist prod),
    `docs/BACKEND.md` + `docs/DATABASE.md` (movidas desde `backend/` el 10/10/2026).
    READMEs y `AGENTS.md` con cifras reales; admin dev `admin`/`setup`
    (sin `ADMIN_PASSWORD` en `.env.example`; seed solo no-prod en `app/main.py:257`).
Estado: 1321 tests backend (33 archivos) + 347 frontend (69 archivos) en verde, ruff + analyze limpios.

## 4. Revisión 10/10/2026 (correcciones a §2–§3)

1. Docs backend consolidadas: `backend/BACKEND.md` + `backend/DATABASE.md` → `docs/BACKEND.md` + `docs/DATABASE.md`; enlaces actualizados en `README.md`, `AGENTS.md`, `docs/README.md`, `ARQUITECTURA.md`, `USO.md`, `ADMINISTRACION.md`.
2. Conteo real: routers 35 archivos (33 con `APIRouter`; `permissions.py`/`dependencies.py` son helpers), services 33 módulos (+`__init__`), models 33 entidades (+`base.py`+`__init__`), schemas 32, Alembic 15, `API.md` 294 endpoints/33 routers (AST cuenta `propfind/report/options/websocket`; grep simple da 272).
3. Tests: backend 1321 `def test_` en 33 archivos (no 1366/38); frontend 347 bloques en 69 archivos (no 313/70). Widgets 24 OK. Pantallas: `festival_profile` 956L, `locations` 680L, `chat` 767L, `api_service` 511L, `user_profile` 803L.
4. Correcciones a §2: `RateLimiter` son 3 instancias (`main.py`, `admin.py`, `auth.py`), no 1; `ADMIN_PASSWORD` no existe en `backend/.env.example` (solo comentario `admin/setup`); `ruff format` cubre 216 archivos (no 215).
5. `tools/gen_api.py` regenera `API.md` idempotente pero con ruta absoluta hardcodeada y sin shebang (no portable).

## 5. Mantenibilidad pendiente (orden sugerido, con verificación)

| # | Tarea | Estado 10/10/2026 | Cómo verificar |
| --- | --- | --- | --- |
| 1 | Migrar routers a `get_or_404` y servicios a `paginate_filtered` | `get_or_404` en 13 routers (110 usos), 186 `404` inline restantes; `paginate_filtered` con 0 usos | `Select-String "get_or_404\(" backend/app/routers; Select-String "404" backend/app/routers; Select-String "paginate_filtered" backend/app/services` |
| 2 | Migrar `python-jose` → `PyJWT` (PR aislado con tests de expiración/tipo/rotación) | Sin migrar (`app/auth.py` usa `jose`) | `Select-String "from jose\|import jose" backend/app; Select-String "import jwt" backend/app` |
| 3 | Troceo de pantallas grandes | Hecho: `festival_profile` 956L, `locations` 680L, `api_service` 511L, `chat` 767L, `user_profile` 803L (widgets extraídos en `lib/widgets/`) | `(Get-Content frontend/lib/screens/<pantalla>).Count` |
| 4 | Migrar `AlertDialog` → `ConfirmDialog` y `ScaffoldMessenger` → `showAppSnack` | 24 `AlertDialog` vs 19 usos `showConfirmDialog`; 115 `ScaffoldMessenger` vs 8 usos `showAppSnack` (los `AlertDialog` restantes son formularios: requieren `CreateEntityDialog` común) | `Select-String "AlertDialog|showConfirmDialog|ScaffoldMessenger|showAppSnack" frontend/lib` |
| 5 | Higiene formato + `.gitignore` | `ruff format --check` + `ruff check` limpios y con gate en CI (GH + GitLab); `.gitignore` cubre `*.db*`, `*.hive`, `*.lock`, `uploads/` (no el glob `*.hive*`) | `ruff format --check .; ruff check .; Get-Content .gitignore` |
