# Mejoras propuestas — Clakettes

Informe derivado del análisis completo del proyecto (backend `backend/` ~11.7k líneas, frontend `frontend/` ~24k líneas). Cada mejora incluye cómo abordarla. No desarrolladas.

---

## CRÍTICO — Seguridad (backend)

### 1. Cerrar ~25 endpoints sin autorización por rol
**Dónde**: `user_roles.py:43,66,78,106` (escalada de privilegios: cualquier autenticado asigna roles/tags), `user_festival.py:17,24` (acepta `role` arbitrario del cliente), `channels.py:59-111`, `committees.py:43-131`, `delegations.py:29-63`, `locations.py:39,61`, `location_images.py:23,40`, `location_relations.py:32`, `shortfilm_locations.py:29,37`, `roles.py:93-127`, `participant_tags.py:86`, `form_definitions.py:39-287`, `registration_forms.py:38-177`, `events.py:55-390`.

**Cómo abordarlo**: centralizar permisos en `app/routers/permissions.py` con dependencias reutilizables (`require_festival_admin`, `require_owner`, `require_channel_admin`). En `user_roles.py`/`user_festival.py`, restringir la asignación de roles a `admin` (y scope del festival), y en `join_festival` aceptar solo un rol de lista blanca (p.ej. `attendee`). En `channels.py`, verificar que el caller es miembro con rol admin del canal. En `form_definitions`/`registration_forms`, que approve/reject exijan ser el creador o admin del festival. Añadir tests que validen 403 para usuarios sin permiso (hoy `test_events.py`/`test_channels.py` congelan la conducta insegura como esperada).

### 2. `GET /api/users/` y `/users/{id}` filtran email sin auth
**Dónde**: `routers/users.py:15-18,40-45`.

**Cómo abordarlo**: exigir `get_current_user` en ambos, y/o crear `PublicUserResponse` sin email/phone para endpoints públicos (p.ej. perfiles en directorios). Elegir un criterio único (privacidad por defecto) y reflejarlo en tests.

### 3. Chat sin ownership: DMs ajenos legibles/borrables
**Dónde**: `routers/chat.py:33-37` (list_messages), `:66-77` (mark_message_read), `:79-85` (delete_message).

**Cómo abordarlo**: en el servicio de mensajes, filtrar siempre por el par `(min(user_id, other_id), max(...))` y exigir que el caller sea uno de los dos participantes; `delete_message` solo permite al remitente (o admin global). Mismo criterio en la lectura de DMs del canal. Tests de acceso cruzado entre dos usuarios.

### 4. Bug auth opcional: formularios públicos siempre 401
**Dónde**: `form_definitions.py:215` (`submit_public_response`), `registration_forms.py:98` (`register_via_public_link`).

**Cómo abordarlo**: reemplazar `Depends(get_current_user)` por una dependencia opcional (`get_current_user_optional`) que devuelva `None` en vez de lanzar 401 cuando no hay token. Alinear el mismo helper en `chat.py` si aplica.

### 5. WebSocket valida JWT pero no sesión activa; `type` nunca se valida
**Dónde**: `auth.py:40,86` (payload `type: access` sin validar), `chat.py:156-164` (`_get_user_from_token`).

**Cómo abordarlo**: en `get_current_user` (y en el WS), comprobar `payload["type"] == "access"` y que la sesión existe y no está revocada, reutilizando la lógica de `auth_session_service` en lugar de solo decodificar.

### 6. Admin automático "setup" y SECRET_KEY insegura por defecto; CORS `*` + credentials
**Dónde**: `config.py:20`, `main.py:63-64,107-118,168-182`.

**Cómo abordarlo**: en `main.py`, bloquear arranque (o generar clave aleatoria con warning) si `SECRET_KEY` no se define por env en modo producción (`APP_ENV=production`); el admin por defecto solo debe crearse en dev (`APP_ENV != "production"`) y con password forzado a cambiar. CORS: rechazar la combinación `["*"]` + `allow_credentials=True` y exigir orígenes explícitos vía env (ver §7 de rendimiento para el `TrustedHostMiddleware`).

---

## ALTO — Rendimiento (backend)

### 7. 17 endpoints con paginación en memoria
**Dónde**: `events.py:51,98,138,200,259,364,400`, `participant_tags.py:30,75`, `registration_forms.py:34,150`, `roles.py:32`, `user_roles.py:35,98`, `validation_rules.py:28,68`, `user_aliases.py:28`.

**Cómo abordarlo**: migrarlos a `BaseService.paginate` (ya existente, `base_service.py:55`) con filtros en SQL; en casos complejos (perfiles públicos con joins), construir la query con `joinedload`/subqueries antes de paginar. Verificar que los tests existentes pasan sin cambios de contrato (mismo formato `PageBase`).

### 8. Commit por request en auth
**Dónde**: `auth.py:105-106` (`last_used_at` + commit en cada request autenticado).

**Cómo abordarlo**: solo persistir si `last_used_at` es anterior a X minutos (p.ej. 5), o usar un update sin commit inmediato delegando en el commit del request. Medir con un endpoint bajo carga.

### 9. N+1 queries
**Dónde**: `events.py:431-461` (`get_public_profile_by_token`: 4+ queries por festival), `events.py:504-505` (2× `role_service.get` por rol), `committees.py:39-40` (get_member_count por comité), `permissions.py:149` (`is_admin` con `user.user_roles` lazy).

**Cómo abordarlo**: usar `joinedload`/`selectinload` en las queries raíz para festivales/roles/tags; calcular counts con subquery o `func.count` agrupado en una sola query; en `is_admin`, cargar `user_roles` con eager loading o cachear por request.

### 10. Faltan índices en tablas calientes
**Dónde**: `models/message.py:25-27` (sender/receiver/group_id), `Festival.name/description/location`, `User.username/full_name` (búsquedas `ilike %q%` en `search_service.py:16-31`).

**Cómo abordarlo**: añadir `index=True` en los models y una migración Alembic; para `ilike %...%` considerar FTS (SQLite FTS5 / MariaDB FULLTEXT) o al menos índice en los campos exactos usados en filtros.

### 11. Bucles con commit por fila
**Dónde**: `event_service.py:86-91` (`bulk_create` asientos), `registration_service.py:37-54` (`create_with_sections`), `form_service.py:30-52` (`create_with_pages`).

**Cómo abordarlo**: ejecutar inserts en un único `bulk_save_objects`/`add_all` y un solo commit al final; precomputar los ids de asientos existentes con una query en vez de una por asiento.

---

## ALTO — Bugs (frontend)

### 12. `LateInitializationError` en `_rootUrl`
**Dónde**: `api_service.dart:44,66-69` (`late final` reasignado por `setBaseUrl()`, llamado desde `backend_setup_screen.dart:55,72`).

**Cómo abordarlo**: cambiar a `String? _rootUrl` con getter que haga fallback a `BackendConfig`, y que `setBaseUrl` notifique vía stream (o que `AuthService`/llamadas lean la URL en cada request).

### 13. SyncQueue: retry roto, sin concurrencia y fuga entre usuarios
**Dónde**: `sync_queue_service.dart:130-146` (ops fallidas nunca se reintentan ni se limpian; `removeWhere` solo limpia `syncing`; `pendingCount` no cuenta failed), `:66` (factory ignora el parámetro), `main_scaffold.dart:493-494` (logout no limpia la cola), `create_festival_screen.dart:116-131` y `chat_screen.dart:470-490` (enqueue duplicado sin comprobar).

**Cómo abordarlo**: en `syncAll`, reintentar hasta N intentos con backoff y marcar `failed` solo tras agotarlos (o dejar `pending` para el siguiente ciclo); guard con un flag `_syncing` para evitar doble ejecución; en logout, `queue.clear()` tras confirmar; en los screens, comprobar `queue.contains(id)` antes de encolar y tratar la respuesta del `create` para actualizar el id local.

### 14. ~60 claves i18n inexistentes y 32 claves de asientos sin traducir
**Dónde**: formularios (`form_detail_screen.dart:210-570`, `registration_forms_screen.dart`, `form_page_editor_screen.dart:99-439`, `form_definitions_screen.dart:65-210`, `form_response_detail_screen.dart:55-156`, `public_form_screen.dart:80-258`) y 7 locales sin `seatMap`, `seatAvailable`, etc.

**Cómo abordarlo**: script que compare `translate('...')`/`t('...')` usados en `lib/` contra las claves de los 9 ARB y liste las ausentes; añadir claves a `en.arb` (fuente de fallback) y traducir al resto; hacer que `translate()` loguee (debugPrint) cuando devuelva la clave cruda para detectar futuras fugas; mover strings hardcodeadas (`chat_screen.dart:280,917`, `location_badge_chip.dart:14-19`, `login_screen.dart:58`) a los ARB.

### 15. `didChangeDependencies` sin guardas
**Dónde**: `locations_screen.dart:44-51` (refetch + setState síncrono en cada cambio de dependencias).

**Cómo abordarlo**: mover la carga a `initState` + `postFrameCallback`, o guardar `if (!_initialized)` con reset solo cuando cambie el locale; eliminar el `setState` síncrono dentro del callback.

---

## MEDIO

### 16. MainScaffold contradice AGENTS.md: sin NavigationRail/NavigationBar
**Dónde**: `main_scaffold.dart` (solo AppBar + Drawer); `integration_test/app_test.dart:30` espera `NavigationBar` inexistente.

**Cómo abordarlo**: decidir entre (a) implementar `NavigationRail` >800px / `NavigationBar` <800px como indica AGENTS.md (con `LayoutBuilder`), o (b) actualizar AGENTS.md y el integration test a la realidad (Drawer). Recomendado (a) para la UX desktop, y en cualquier caso corregir el integration test.

### 17. Ruff: 249 violaciones; `create_all` vs Alembic; archivos de estado versionados
**Dónde**: 182× E501 y 67× W292; `main.py:124` (`Base.metadata.create_all` en lifespan); `clakettes.db`, `rate_limits.db`, `uploads/avatars/*.png`, `*.hive` en el repo.

**Cómo abordarlo**: `ruff check --fix` (E501/W292 son auto-corregibles en su mayoría; revisar manualmente las líneas >120); eliminar `create_all` del lifespan en favor de `alembic upgrade head` en dev (o mantener solo si hay flag explícito); añadir `*.db`, `*.hive*`, `uploads/` a `.gitignore` y borrar los artefactos del índice.

### 18. Deuda de tamaño y duplicación en frontend
**Dónde**: `api_service.dart` (1285 líneas), `locations_screen.dart` (1143), `chat_screen.dart` (1004); login-prompt duplicado ×3 (`main_scaffold.dart:241-285`, `festivals_screen.dart:46-94`, `festival_profile_screen.dart:76-124`); diálogo "crear entidad" ×5; confirm-delete en 2 estilos; `_openInMaps` ×4; FlutterMap+OSM ×8; `_loadData()`+loading/error en ~15 pantallas; `Message` reconstruido con 15 args ×2 (`chat_screen.dart:170-248`).

**Cómo abordarlo**: refactor incremental: (1) extraer widgets: `LoginPromptSheet`, `CreateEntityDialog`, `ConfirmDeleteDialog` unificado, `AppMapTileLayer` (con `flutter_map_cancellable_tile_provider`, ya en pubspec), `OpenInMapsAction`; (2) en `chat_screen.dart`, construir `Message` en un solo helper o con el backend; (3) dividir `api_service.dart` por dominio (`UserApi`, `FestivalApi`, `ChannelApi`...) manteniendo la firma pública; (4) plantilla `LoadDataMixin` para el patrón loading/error. Cada paso con tests existentes en verde.

### 19. Rendimiento de UI
**Dónde**: 0 usos de `itemExtent`/`prototypeItem`; 10 `Image.network` sin caché; refetch en cada filtro (`form_detail_screen.dart:530-538`, `form_definitions_screen.dart:158`); setState por keystroke (`locations_screen.dart:444`); `ChatCrypto` E2EE en UI thread (`crypto_utils.dart:292-375`); `size:100` sin paginación real.

**Cómo abordarlo**: `prototypeItem` en listas de mensajes/ítems de tamaño fijo; `cached_network_image` para las 10 imágenes; debounce (400ms) en búsquedas y mover filtros a nivel de datos (filtrar la lista en memoria sin refetch cuando el dataset está cargado); `compute()` para `encrypt/decrypt` de `ChatCrypto`; respetar el `PaginatedResult` con `page`/`size` reales en las pantallas principales.

### 20. Calidad de tests
**Dónde backend**: routers sin tests (`auth_sessions`, `committees`, `delegations`, `role_groups`, `shortfilm_locations`, `location_images`, `location_relations`, `location_tags`, uploads, search, user_festival, chat/WS); `conftest.py` duplicado entre `tests/` y `tests/services/`; `create_shortfilm` con ids hardcodeados (`tests/services/conftest.py:84-85`).

**Cómo abordarlo**: tests por router con factory helpers compartidos (extraer a `tests/factories.py`); parametrizar el conftest de servicios para reutilizar el engine; añadir tests de 403/401 en los endpoints del bloque 1 (serán red del cambio).

**Dónde frontend**: 29 tests de pantallas sin aserciones; sin tests de `syncAll`/retry/conflictos; `lib/main_test.dart` (entry point de test dentro de `lib/`); `test/widget_test.dart` bombea sin inicializar Hive; sin tests para widgets (`seat_map`, `map_picker`, `emoji_picker`, location_*, `film_location_card`, skeletons/states).

**Cómo abordarlo**: aserciones mínimas en smoke tests (widget visible, datos renderizados); tests unitarios de `syncAll` (éxito, fallo parcial, retry, doble llamada) con `FakeApiService`; mover `main_test.dart` a `test/`; fixture de Hive en `setUp`; tests de los widgets clave con `WidgetTester`.

### 21. Deuda menor y código muerto
**Dónde**: `dependencies.py:9` (`get_object_or_404` sin uso); `role_service.py:36`, `event_service.py:37`, `group_service.py:177`, `auth_session_service.py:11` (métodos solo usados por tests); `auth_wrapper.dart` completo; `RestChatBackend` y `ChatService.useBackend` (`rest_chat_backend.dart:12`); `import 'dart:io'` sin uso (`crypto_utils.dart:2`) que rompería web; 79 `debugPrint` con errores silenciados; enums duplicados entre `app/enums.py` y models; strings hardcodeadas en backend (`event_service.py:191,201`, `chat.py:131,139`); `oauth2_scheme` redefinido (`auth_sessions.py:19`); `UploadFormLinkCreate` usado como Update; DELETE con 200+message en vez de 204; `LocationTag` import sin uso en `locations.py`; `HTTPException` desde servicios (`group_service.py:3`, `channel_service.py:3`).

**Cómo abordarlo**: barrido en 2-3 pasadas: (1) eliminar muerto confirmado con `rg` (sin usos fuera de tests, revisar tests antes de borrar); (2) mover enums duplicados a `app/enums.py` y reexportar para no romper imports; (3) en servicios, sustituir `HTTPException` por excepciones de dominio (`NotFoundError`, `PermissionDeniedError`) traducidas en el router; unificar status codes (204 en DELETE/201 en creación); strings → enums/constants.

---

## Orden de ejecución sugerido

1. **Bloque CRÍTICO (1-6)** — seguridad: sin esto el resto es cosmético.
2. **Bugs frontend (12-15)** — `LateInitializationError`, sync, i18n: afectan a usuarios reales.
3. **Rendimiento backend (7-11)** — N+1, paginación, índices, commits.
4. **17-18** — higiene: ruff, gitignore, refactor incremental (riesgo bajo, sin cambiar API).
5. **19-21** — rendimiento UI, tests, deuda menor.
