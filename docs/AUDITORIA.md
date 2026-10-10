# Auditoría de código — Clakettes (09/10/2026, ampl. multiplataforma 09/10/2026)

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
2. `main.py` RateLimitMiddleware: una sola instancia `RateLimiter` (dos buckets por prefijo `dav:`/`middleware:` en vez de dos conexiones SQLite).
3. `base_service.py`: `paginate` fija `page>=1`, `size` en `[1,100]`; nuevo `paginate_filtered()` para migrar los `get_all_paginated` clonados y los 17 endpoints con paginación en memoria.
4. `routers/dependencies.py`: `get_current_user_optional` reutiliza `validate_access_token` (elimina ~30 líneas duplicadas JWT+sesión); fix `__import__("datetime")` → import normal; nuevo `get_or_404()` para reemplazar ~100 `HTTPException(404)` inline.
5. `dav/auth.py`: documentada la relación con `app.auth._hash_token`.
6. `pyproject.toml`/`requirements.txt` sincronizados (reportlab).
7. `reusable_widgets.dart`: nuevo `showAppSnack()` para unificar ~113 `ScaffoldMessenger`.

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
   (piloto). Nota: los 21 `AlertDialog` restantes son diálogos de *formulario*
   (crear/editar), no de confirmación — no migran a `showConfirmDialog`
   (ya usado en `_deleteAward`); requerirían un `CreateEntityDialog` común.
9. CI: gate `ruff format --check` añadido (GH + GitLab) tras verificar
   `215 files already formatted` — desbloquea la propuesta de HERRAMIENTAS.md.
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
16. Chat: `chat_screen.dart` 1038 → 701 líneas; burbujas a
    `widgets/chat_bubble.dart` (`ChatBubble` + `ChatBubbleWidget` con imagen,
    ubicación, vCard, iCal) y barra a `widgets/chat_input_bar.dart`
    (`ChatInputBar`). 2 tests async nuevos en `crypto_utils_test`.
17. `locations_screen` 1144 → 665 líneas: tarjetas y formulario a
    `widgets/location_cards.dart` (`LocationCard`, `LegacyCard`,
    `LegacyLocation`, `LocationFormScreen`, `LocationFormResult`); borrado
    con `showConfirmDialog` + `showAppSnack` (un AlertDialog menos).
18. `festival_profile_screen` 1276 → 937 líneas: `RulebooksSection` y
    `FestivalLocationsSection` (+ mapa y fichas) a
    `widgets/festival_sections.dart`. La pantalla conserva estado,
    lectura, edición y callbacks.
19. `api_service.dart` 1134 → 512 líneas: 95 métodos movidos a `lib/services/api/`
    (`event_api` 31, `location_api` 25, `org_api` 17, `catalog_api` 13,
    resto a `user_api`). El núcleo conserva config, auth, transporte y
    admin/búsqueda. API pública intacta.
20. `user_profile_screen` 996 → 819 líneas: `SessionsCard` y `AliasesCard`
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
    CI), `docs/SEGURIDAD.md` (tokens, matriz de permisos, checklist prod).
    READMEs y `AGENTS.md` con cifras reales; `ADMIN_PASSWORD` real en
    `.env.example` (`setup`, no `Admin123!`).
Estado: 1366 tests backend + 313 frontend en verde, ruff + analyze limpios.

## 4. Mantenibilidad pendiente (no aplicado, orden sugerido)

1. Migrar routers a `get_or_404` y servicios a `paginate_filtered` (mecánico, por dominio).
2. Migrar `python-jose` → `PyJWT` (PR aislado con tests de expiración/tipo/rotación).
3. Trocear `festival_profile(1312L)`, `locations(1200L)`, `api_service(1132L)`, `chat(1038L)`.
4. Migrar 21 `AlertDialog` directos a `ConfirmDialog`; usar `showAppSnack` en los 113 sitios.
5. `ruff format .` + `ruff check --fix` (E501/W292); añadir `*.db`, `*.hive*`, `uploads/` a `.gitignore`.
