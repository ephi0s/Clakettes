# Auditoría de código — Clakettes (09/10/2026, ampl. multiplataforma 09/10/2026, rev. 10/10/2026)

[ES](../es/AUDITORIA.md) · [EN](../en/AUDITORIA.md) · [FR](../fr/AUDITORIA.md) · [DE](../de/AUDITORIA.md) · [IT](../it/AUDITORIA.md) · [CA](../ca/AUDITORIA.md) · [EU](../eu/AUDITORIA.md) · [GL](AUDITORIA.md) · [OC](../oc/AUDITORIA.md)

> **Addendum 11/10/2026** (cifras verificadas): backend 1402 tests en 37 arquivos;
> routers 36 ficheiros (33 con `APIRouter`); services 36; models 34; schemas 33;
> Alembic 18 versións; `docs/es/API.md` 310 endpoints (operationIds únicos).
> RXPD: privacidade por defecto, consentimento, borrado/exportación, purga de
> sesións, auditoría append-only, sanitizado de metadatos, TLS MariaDB en prod,
> DAV con caducidade, CSP/HSTS. Provedores de pago mock/stripe/redsys.

## 0. Resumo executivo (10/10/2026, cifras verificadas)

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

Como re-verificar: `cd backend; python -m ruff check .; python -m pytest tests/ -x -q --tb=short` e `cd frontend; flutter analyze; flutter test`.

## 1. Dependencias externas: que se pode eliminar e que non

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

Todas as dependencias están en uso real; ningunha se puido eliminar sen romper funcionalidade:

- `archive`: usado en `crypto_utils.dart` (ZLib/GZip). `dart:io` non vale porque rompe web.
- `path_provider`: usado en `file_downloader_io.dart` (móbil/desktop).
- `web`: usado en `file_downloader_web.dart`.
- `pointycastle` + `crypto` + `uuid`: E2EE do chat (X25519/ECDH P-256 + AES-GCM).
- `flutter_map` + `cancellable_tile` + `latlong2` + `geolocator` + `url_launcher`: mapas.
- `table_calendar`, `flutter_local_notifications` + `timezone` + `flutter_timezone`, `image_picker` + `file_picker`: cada un con 1-2 usos, pero eliminalos quitaría funcionalidade.

## 2. Optimizacións aplicadas

1. `export_service.py`: import reportlab preguiceiro en `_build_pdf` + docstring.
2. `main.py` RateLimitMiddleware + `routers/admin.py` + `routers/auth.py`: 3 instancias `RateLimiter` (buckets `middleware:`/`dav:` + limiters de `reset` 3/300s e `login`); non unificar sen perder límites distintos.
3. `base_service.py`: `paginate` fixa `page>=1`, `size` en `[1,100]`; novo `paginate_filtered()` definido con 0 usos (pendente migrar os `get_all_paginated` clonados).
4. `routers/dependencies.py`: `get_current_user_optional` reutiliza `validate_access_token` (elimina ~30 liñas duplicadas JWT+sesión); fix `__import__("datetime")` → import normal; novo `get_or_404()` para substituír ~100 `HTTPException(404)` inline.
5. `dav/auth.py`: documentada a relación con `app.auth._hash_token`.
6. `pyproject.toml`/`requirements.txt` sincronizados (reportlab).
7. `reusable_widgets.dart`: novo `showAppSnack()` (1 def + 8 usos; quedan 115 `ScaffoldMessenger` directos).

## 3. Melloras multiplataforma aplicadas (escritorio + web + Android + iOS/iPad)

1. `BackendConfig`: default por plataforma — emulador Android usa `10.0.2.2:8000`
   (localhost do emulador é o propio virtual, non o host); resto `localhost:8000`.
   Prioridade: URL gardada > `--dart-define=BACKEND_URL` > default por plataforma.
   `ApiService` usa o mesmo default en construtor e getters.
2. `NotificationService`: en web (`kIsWeb`) `init` non toca plugin nin timezone
   (sen notificacións locais en navegador) e `scheduleReminder` non fai nada;
   documentado no docstring. Sen ramas por plataforma nas pantallas.
3. `file_downloader.dart`: verificado o import condicional
   (`web` por defecto, `io` se `dart.library.io`) — cobre navegador, escritorio,
   Android e iOS sen cambios.
4. `main_scaffold.dart`: engadido Curtas á navegación (existía a pantalla
   `screenIndex 3` pero sen item — inaccesible). Rail >800px (escritorio/web),
   Bar <800px (móbil), Drawer en todos.
5. `AndroidManifest.xml`: engadidos INTERNET, ACCESS_NETWORK_STATE, localización
   (FINE+COARSE), CAMERA, READ_MEDIA_IMAGES/VIDEO, SCHEDULE/USE_EXACT_ALARM.
   Sen INTERNET explícito os builds release non teñen rede.
6. `ios/Runner/Info.plist`: engadidos NSLocationWhenInUse, NSCamera,
   NSPhotoLibrary (+Add). Sen estes o sistema denega ou a App Store rexeita.
7. Backend `routers/festivals.py`: piloto `get_or_404(db, Festival/Location, ...)`
   — 9 bloques `if not → 404` eliminados; estendido a `shortfilms.py` (3) e
   `users.py` (4). Patrón a estender ao resto de routers.
8. Frontend `awards_screen.dart`: erro SnackBar migrado a `showAppSnack()`
   (piloto). Nota: os 24 `AlertDialog` restantes son diálogos de *formulario*
   (crear/editar), non de confirmación — non migran a `showConfirmDialog`
   (19 usos en 18 pantallas); requirirían un `CreateEntityDialog` común.
9. CI: gate `ruff format --check` engadido (GH + GitLab) tras verificar
   `216 files already formatted`.
10. Seguridade (piloto `channels.py`, bloque seguridade): novo
    `require_channel_member`/`is_channel_member` en `permissions.py` e uso en
    `channels.py` + `chat.py` (elimina 3 bloques inline con imports diferidos);
    `channels.py` migrado a `get_or_404` (7 bloques menos); whitelist de rol
    `Literal[admin,moderator,member]` en schemas (antes: string libre → 500
    por CheckConstraint; agora: 422); 4 tests 403/422 novos en
    `TestChannelAuthorization`.
11. Seguridade: `POST /delegations/{id}/revoke` esixía só auth — calquera
    revogaba delegacións alleas. Agora verifica delegador ou admin + test 403.
    Verificados xa OK (sen cambios): `user_roles`/`user_festival` (whitelist
    attendee), DMs (ownership), formularios públicos (auth opcional), WS
    (valida sesión), `bulk_create` (single commit), SyncQueue (retry+backoff),
    i18n (0 claves ausentes), `locations` (didChangeDependencies con garda).
12. `get_or_404` estendido a `committees.py` (10), `events.py` (58, vía script
    con revisión + 17 existencias sen asignar para evitar F841), `delegations`
    (2) e 5 routers de localizacións (12). Sen cambios de esquema: non hai
    migración Alembic pendente por este lote.
13. Rendemento: filtro `venue` de programacion baixado a SQL (antes filtraba
    a páxina en Python e rompía `total`/`pages`).
14. Frontend: gardas anti-dobre-envío en crear festival/usuario/curta +
    3 SnackBars migrados a `showAppSnack`.
15. Chat: E2EE fóra do UI thread — `_prepareContent`/`_unpackContent` usan
   `encryptAsync`/`decryptAsync` (isolates); novos `encryptSenderKeyAsync`/
    `decryptSenderKeyAsync` usados en difusión e recepción de sender keys.
    `RestChatBackend` consérvase: úsao `chat_service_test` como fake
    (non era código morto).
16. Chat: `chat_screen.dart` 1038 → 767 liñas; burbullas a
    `widgets/chat_bubble.dart` (`ChatBubble` + `ChatBubbleWidget` con imaxe,
    localización, vCard, iCal) e barra a `widgets/chat_input_bar.dart`
    (`ChatInputBar`). 2 tests async novos en `crypto_utils_test`.
17. `locations_screen` 1144 → 680 liñas: tarxetas e formulario a
    `widgets/location_cards.dart` (`LocationCard`, `LegacyCard`,
    `LegacyLocation`, `LocationFormScreen`, `LocationFormResult`); borrado
    con `showConfirmDialog` + `showAppSnack` (un AlertDialog menos).
18. `festival_profile_screen` 1276 → 956 liñas: `RulebooksSection` e
    `FestivalLocationsSection` (+ mapa e fichas) a
    `widgets/festival_sections.dart`. A pantalla conserva estado,
    lectura, edición e callbacks.
19. `api_service.dart` 1134 → 511 liñas: 95 métodos movidos a `lib/services/api/`
    (`event_api` 31, `location_api` 25, `org_api` 17, `catalog_api` 13,
    resto a `user_api` + `calendar/channel/festival/form`). O núcleo conserva config, auth, transporte e
    admin/búsqueda. API pública intacta.
20. `user_profile_screen` 996 → 803 liñas: `SessionsCard` e `AliasesCard`
    a `widgets/user_profile_cards.dart`. Corrixidos 4 `if` sen chaves
    herdados en `catalog_api`.
21. Tests de fluxo (`tests/integration/test_flows.py`): reserva completa
    (festival → evento → asentos → reserva → ocupación), mensaxería
    (canle → membro → DM → lectura → borrado) e delegación (crear →
    listar → revogar).
22. Widget tests dos widgets extraídos (13): `chat_bubble`,
    `chat_input_bar`, `user_profile_cards`, `location_cards`. Nota: os
    widgets baixo `wrapWithLocalization` necesitan un `pump()` extra
    (o Builder de localización resolve no segundo frame).
23. Push nativo sen Firebase (`docs/es/PUSH.md`): Notification API do navegador
    en web (`notification_web.dart` + stub con export condicional, sen deps
    novas), `flutter_local_notifications` en escritorio + permiso macOS ao
    iniciar, móbil en no-op explícito (`_supported`). `flutter build web`
    verificado.
24. Documentación: `docs/es/API.md` (294 endpoints en 33 routers, xerada por
    AST con `tools/gen_api.py` — rexenerable), `docs/es/ARQUITECTURA.md`
    (capas, fluxos, decisións multiplataforma), `docs/es/USO.md` (arranque,
    env, operación, roles), `docs/es/DESARROLLO.md` (convencións + portas
    CI), `docs/es/SEGURIDAD.md` (tokens, matriz de permisos, checklist prod),
    `docs/es/BACKEND.md` + `docs/es/DATABASE.md` (movidas desde `backend/` o 10/10/2026).
    READMEs e `AGENTS.md` con cifras reais; admin dev `admin`/`setup`
    (sen `ADMIN_PASSWORD` en `.env.example`; seed só non-prod en `app/main.py:257`).
Estado: 1321 tests backend (33 arquivos) + 347 frontend (69 arquivos) en verde, ruff + analyze limpos.

## 4. Revisión 10/10/2026 (correccións a §2–§3)

1. Docs backend consolidadas: `backend/BACKEND.md` + `backend/DATABASE.md` → `docs/es/BACKEND.md` + `docs/es/DATABASE.md`; ligazóns actualizadas en `README.md`, `AGENTS.md`, `docs/es/README.md`, `ARQUITECTURA.md`, `USO.md`, `ADMINISTRACION.md`.
2. Conteo real: routers 35 arquivos (33 con `APIRouter`; `permissions.py`/`dependencies.py` son helpers), services 33 módulos (+`__init__`), models 33 entidades (+`base.py`+`__init__`), schemas 32, Alembic 15, `API.md` 294 endpoints/33 routers (AST conta `propfind/report/options/websocket`; grep simple da 272).
3. Tests: backend 1321 `def test_` en 33 arquivos (non 1366/38); frontend 347 bloques en 69 arquivos (non 313/70). Widgets 24 OK. Pantallas: `festival_profile` 956L, `locations` 680L, `chat` 767L, `api_service` 511L, `user_profile` 803L.
4. Correccións a §2: `RateLimiter` son 3 instancias (`main.py`, `admin.py`, `auth.py`), non 1; `ADMIN_PASSWORD` non existe en `backend/.env.example` (só comentario `admin/setup`); `ruff format` cobre 216 arquivos (non 215).
5. `tools/gen_api.py` rexenera `API.md` idempotente pero con ruta absoluta hardcodeada e sen shebang (non portable).

## 5. Mantibilidade pendente (orde suxerida, con verificación)

| # | Tarea | Estado 10/10/2026 | Cómo verificar |
| --- | --- | --- | --- |
| 1 | Migrar routers a `get_or_404` y servicios a `paginate_filtered` | `get_or_404` en 13 routers (110 usos), 186 `404` inline restantes; `paginate_filtered` con 0 usos | `Select-String "get_or_404\(" backend/app/routers; Select-String "404" backend/app/routers; Select-String "paginate_filtered" backend/app/services` |
| 2 | Migrar `python-jose` → `PyJWT` (PR aislado con tests de expiración/tipo/rotación) | Sin migrar (`app/auth.py` usa `jose`) | `Select-String "from jose\|import jose" backend/app; Select-String "import jwt" backend/app` |
| 3 | Troceo de pantallas grandes | Hecho: `festival_profile` 956L, `locations` 680L, `api_service` 511L, `chat` 767L, `user_profile` 803L (widgets extraídos en `lib/widgets/`) | `(Get-Content frontend/lib/screens/<pantalla>).Count` |
| 4 | Migrar `AlertDialog` → `ConfirmDialog` y `ScaffoldMessenger` → `showAppSnack` | 24 `AlertDialog` vs 19 usos `showConfirmDialog`; 115 `ScaffoldMessenger` vs 8 usos `showAppSnack` (los `AlertDialog` restantes son formularios: requieren `CreateEntityDialog` común) | `Select-String "AlertDialog|showConfirmDialog|ScaffoldMessenger|showAppSnack" frontend/lib` |
| 5 | Higiene formato + `.gitignore` | `ruff format --check` + `ruff check` limpios y con gate en CI (GH + GitLab); `.gitignore` cubre `*.db*`, `*.hive`, `*.lock`, `uploads/` (no el glob `*.hive*`) | `ruff format --check .; ruff check .; Get-Content .gitignore` |
