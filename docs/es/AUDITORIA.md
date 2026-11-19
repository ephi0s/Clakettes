# Auditoría de código — Clakettes (rev. 10/10/2026, ampl. multiplataforma 09/10/2026)

[ES](AUDITORIA.md) · [EN](../en/AUDITORIA.md) · [FR](../fr/AUDITORIA.md) · [DE](../de/AUDITORIA.md) · [IT](../it/AUDITORIA.md) · [CA](../ca/AUDITORIA.md) · [EU](../eu/AUDITORIA.md) · [GL](../gl/AUDITORIA.md) · [OC](../oc/AUDITORIA.md)

## 0. Resumen ejecutivo

Revisión de dependencias, optimizaciones aplicadas y deuda técnica pendiente del proyecto Clakettes.

## 1. Dependencias externas: qué se puede eliminar y qué no

### Backend (`backend/requirements.txt` + `pyproject.toml`)

| Dep | Veredicto | Motivo |
| --- | --- | --- |
| fastapi, uvicorn[standard], sqlalchemy, pydantic(+settings), alembic | Mantener | Núcleo del stack |
| python-jose[cryptography] | Mantener por ahora, migrar a PyJWT en el futuro | Abandonado desde 2016, pero el cambio toca `app/auth.py` + `routers/dependencies.py` + tests; hacerlo en PR separado con tests de tokens |
| python-dotenv | Mantener | Requerido por `pydantic-settings>=2` y `uvicorn[standard]` (`--env-file`); solo 2 scripts lo importan directamente, pero quitarlo rompería la carga de `.env` |
| pymysql | Mantener como driver prod | Solo se usa con MariaDB; no cargarlo en dev no ahorra nada (import perezoso ya en SQLAlchemy) |
| python-multipart, email-validator, bcrypt | Mantener | Uploads, validación email, hash passwords |
| reportlab 5.1.0 | Mantener, pero con import perezoso (hecho) | Solo `export_service._build_pdf`; antes se importaba a nivel de módulo (~200 ms + memoria en cada worker). Ahora import dentro de la función. Además se sincronizó `pyproject.toml` (faltaba) y se pineó `==5.1.0` |

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
4. `routers/dependencies.py`: `get_current_user_optional` reutiliza `validate_access_token` (elimina líneas duplicadas JWT+sesión); fix `__import__("datetime")` → import normal; nuevo `get_or_404()` para reemplazar `HTTPException(404)` inline.
5. `dav/auth.py`: documentada la relación con `app.auth._hash_token`.
6. `pyproject.toml`/`requirements.txt` sincronizados (reportlab).
7. `reusable_widgets.dart`: nuevo `showAppSnack()` para centralizar snackbars.

## 3. Mejoras multiplataforma aplicadas (escritorio + web + Android + iOS/iPad)

1. `BackendConfig`: default por plataforma — emulador Android usa `10.0.2.2:8000` (localhost del emulador es el propio virtual, no el host); resto `localhost:8000`. Prioridad: URL guardada > `--dart-define=BACKEND_URL` > default por plataforma. `ApiService` usa el mismo default en constructor y getters.
2. `NotificationService`: en web (`kIsWeb`) `init` no toca plugin ni timezone (sin notificaciones locales en navegador) y `scheduleReminder` no hace nada; documentado en el docstring. Sin ramas por plataforma en las pantallas.
3. `file_downloader.dart`: verificado el import condicional (`web` por defecto, `io` si `dart.library.io`) — cubre navegador, escritorio, Android e iOS sin cambios.
4. `main_scaffold.dart`: añadido Cortos a la navegación (existía la pantalla `screenIndex 3` pero sin item — inaccesible). Rail >800px (escritorio/web), Bar <800px (móvil), Drawer en todos.
5. `AndroidManifest.xml`: añadidos INTERNET, ACCESS_NETWORK_STATE, ubicación (FINE+COARSE), CAMERA, READ_MEDIA_IMAGES/VIDEO, SCHEDULE/USE_EXACT_ALARM. Sin INTERNET explícito los builds release no tienen red.
6. `ios/Runner/Info.plist`: añadidos NSLocationWhenInUse, NSCamera, NSPhotoLibrary (+Add). Sin estos el sistema deniega o la App Store rechaza.
7. Backend `routers/festivals.py`: piloto `get_or_404(db, Festival/Location, ...)`; extendido a `shortfilms.py` y `users.py`. Patrón a extender al resto de routers.
8. Frontend `awards_screen.dart`: error SnackBar migrado a `showAppSnack()` (piloto). Los `AlertDialog` restantes son diálogos de formulario (crear/editar), no de confirmación; requerirían un `CreateEntityDialog` común.
9. CI: gate `ruff format --check` añadido (GH + GitLab).
10. Seguridad (piloto `channels.py`): nuevo `require_channel_member`/`is_channel_member` en `permissions.py` y uso en `channels.py` + `chat.py`; `channels.py` migrado a `get_or_404`; whitelist de rol `Literal[admin,moderator,member]` en schemas (antes: string libre → 500 por CheckConstraint; ahora: 422).
11. Seguridad: `POST /delegations/{id}/revoke` exigía solo auth — cualquiera revocaba delegaciones ajenas. Ahora verifica delegador o admin + test 403.
12. `get_or_404` extendido a `committees.py`, `events.py`, `delegations` y 5 routers de localizaciones. Sin cambios de esquema: no hay migración Alembic pendiente por este lote.
13. Rendimiento: filtro `venue` de programación bajado a SQL (antes filtraba la página en Python y rompía `total`/`pages`).
14. Frontend: guardas anti-doble-envío en crear festival/usuario/corto + SnackBars migrados a `showAppSnack`.
15. Chat: E2EE fuera del UI thread — `_prepareContent`/`_unpackContent` usan `encryptAsync`/`decryptAsync` (isolates); nuevos `encryptSenderKeyAsync`/`decryptSenderKeyAsync` en difusión y recepción de sender keys. `RestChatBackend` se conserva: lo usa `chat_service_test` como fake.
16. Chat: `chat_screen.dart` reestructurado; burbujas a `widgets/chat_bubble.dart` y barra a `widgets/chat_input_bar.dart`. Tests async nuevos en `crypto_utils_test`.
17. `locations_screen` reestructurado: tarjetas y formulario a `widgets/location_cards.dart`; borrado con `showConfirmDialog` + `showAppSnack`.
18. `festival_profile_screen` reestructurado: `RulebooksSection` y `FestivalLocationsSection` (+ mapa y fichas) a `widgets/festival_sections.dart`.
19. `api_service.dart` reestructurado: métodos movidos a `lib/services/api/` (`event_api`, `location_api`, `org_api`, `catalog_api`, resto a `user_api` + `calendar/channel/festival/form`). El núcleo conserva config, auth, transporte y admin/búsqueda. API pública intacta.
20. `user_profile_screen` reestructurado: `SessionsCard` y `AliasesCard` a `widgets/user_profile_cards.dart`. Corregidos `if` sin llaves heredados en `catalog_api`.
21. Tests de flujo (`tests/integration/test_flows.py`): reserva completa (festival → evento → asientos → reserva → ocupación), mensajería (canal → miembro → DM → lectura → borrado) y delegación (crear → listar → revocar).
22. Widget tests de los widgets extraídos: `chat_bubble`, `chat_input_bar`, `user_profile_cards`, `location_cards`. Nota: los widgets bajo `wrapWithLocalization` necesitan un `pump()` extra.
23. Push nativo sin Firebase (`docs/es/PUSH.md`): Notification API del navegador en web, `flutter_local_notifications` en escritorio + permiso macOS al iniciar, móvil en no-op explícito. `flutter build web` verificado.
24. Documentación: `docs/es/API.md`, `docs/es/ARQUITECTURA.md`, `docs/es/USO.md`, `docs/es/DESARROLLO.md`, `docs/es/SEGURIDAD.md`, `docs/es/BACKEND.md` + `docs/es/DATABASE.md` (movidas desde `backend/` el 10/10/2026).



