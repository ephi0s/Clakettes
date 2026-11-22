# Auditoría de código — Clakettes (09/10/2026, ampl. multiplataforma 09/10/2026, rev. 10/10/2026)

[ES](../es/AUDITORIA.md) · [EN](../en/AUDITORIA.md) · [FR](../fr/AUDITORIA.md) · [DE](../de/AUDITORIA.md) · [IT](../it/AUDITORIA.md) · [CA](../ca/AUDITORIA.md) · [EU](../eu/AUDITORIA.md) · [GL](AUDITORIA.md) · [OC](../oc/AUDITORIA.md)

## 0. Resumo executivo

Revisión das dependencias, optimizacións aplicadas e débeda técnica pendente do proxecto Clakettes.

## 1. Dependencias externas: que se pode eliminar e que non

### Backend (`backend/requirements.txt` + `pyproject.toml`)

| Dep | Veredicto | Motivo |
| --- | --- | --- |
| fastapi, uvicorn[standard], sqlalchemy, pydantic(+settings), alembic | Manter | Núcleo da pila |
| PyJWT==2.15.1 | Migración rematada | `python-jose` eliminado; `app/auth.py` e `routers/dependencies.py` usan PyJWT (bump 2.10.1 → 2.15.0 → 2.15.1) |
| python-dotenv | Non incluída | Non figura en `pyproject.toml`/`requirements*.txt` nin se importa en `backend/`; `pydantic-settings` carga `.env` directamente |
| pymysql | Manter como controlador prod | Só se usa con MariaDB; non cargalo en dev non aforra nada (import preguiceiro xa en SQLAlchemy) |
| python-multipart, email-validator, bcrypt | Manter | Subidas, validación de correo, hash de contrasinais |
| reportlab 5.1.0 | Manter, pero con import preguiceiro (feito) | Só `export_service._build_pdf`; antes importábase a nivel de módulo (~200 ms + memoria en cada worker). Agora importase dentro da función. Ademais sincronizouse `pyproject.toml` (faltaba) e fixouse `==5.1.0` |

**Versións fixadas en `backend/pyproject.toml` / `requirements*.txt`:** `fastapi==0.163.1`, `uvicorn[standard]==0.54.0`, `sqlalchemy==2.1.9`, `pydantic==2.14.3`, `pydantic-settings==2.16.3`, `email-validator==2.4.0`, `pymysql==1.2.4`, `python-multipart==0.0.34`, `PyJWT==2.15.1`, `cryptography==50.0.2`, `bcrypt>=4.3.0`, `alembic==1.20.1`, `reportlab==5.1.0`, `Pillow==13.0.0`, `mutagen==1.48.1`, `pypdf==7.1.0` (major desde 6.21.x); desenvolvemento: `pytest>=9.2.0`, `ruff==0.17.5`, `httpx==0.28.1`, `caldav==3.7.0`, `icalendar==7.3.0`.

### Frontend (`frontend/pubspec.yaml`)

Todas as dependencias están en uso real; ningunha se puido eliminar sen romper funcionalidade:

- `archive`: usado en `crypto_utils.dart` (ZLib/GZip). `dart:io` non vale porque rompe web.
- `path_provider`: usado en `file_downloader_io.dart` (móbil/desktop).
- `web`: usado en `file_downloader_web.dart`.
- `pointycastle` + `crypto`: E2EE do chat (ECDH P-256 + AES-GCM; o nome `X25519` aparece só nun campo herdado).
- `flutter_map` + `latlong2` + `geolocator` + `url_launcher`: mapas.
- `table_calendar`, `flutter_local_notifications` + `timezone` + `flutter_timezone`, `image_picker` + `file_picker`: cada un con 1-2 usos, pero eliminalos quitaría funcionalidade.

## 2. Optimizacións aplicadas

1. `export_service.py`: import reportlab preguiceiro en `_build_pdf` + docstring.
2. `main.py` RateLimitMiddleware + `routers/admin.py` + `routers/auth.py` + `routers/auth_sessions.py` + `routers/federation.py`: 5 instancias `RateLimiter` (buckets `middleware:`/`dav:` + limiters de `reset` 3/300 s, `login` 5/300 s, `refresh` 20/60 s e federación 60/60 s); non unificar sen perder límites distintos. O bypass pasa por `app.config.is_testing()` (`1/true/yes/on`).
3. `base_service.py`: `paginate` fixa `page>=1`, `size` en `[1,100]`; novo `paginate_filtered()` definido con 0 usos (pendente migrar os `get_all_paginated` clonados).
4. `routers/dependencies.py`: `get_current_user_optional` reutiliza `validate_access_token` (elimina ~30 liñas duplicadas JWT+sesión); fix `__import__("datetime")` → import normal; novo `get_or_404()` para substituír ~100 `HTTPException(404)` inline.
5. `dav/auth.py`: documentada a relación con `app.auth.hash_token` (antes `_hash_token`; consérvase o alias por compatibilidade).
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
    (2) e 5 routers de localizacións (12). Este lote non introduciu migración;
    revisións posteriores si engadiron `a8b9c0d1e2f3` (unicidade de asento) e
    `b9c0d1e2f3a4` (`contest_type` en curtos), ambas xa aplicadas no head
    `b9c0d1e2f3a4`.
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
24. Documentación: `docs/es/API.md` (446 endpoints en 43 routers, xerada por
    AST con `tools/gen_api.py` — rexenerable), `docs/es/ARQUITECTURA.md`
    (capas, fluxos, decisións multiplataforma), `docs/es/USO.md` (arranque,
    env, operación, roles), `docs/es/DESARROLLO.md` (convencións + portas
    CI), `docs/es/SEGURIDAD.md` (tokens, matriz de permisos, checklist prod),
    `docs/es/BACKEND.md` + `docs/es/DATABASE.md` (movidas desde `backend/` o 10/10/2026).
    READMEs e `AGENTS.md` con cifras reais; admin dev `admin`/`setup`
    (sen `ADMIN_PASSWORD` en `.env.example`; seed só non-prod en `app/main.py:257`).
Estado: 1544 tests backend (54 arquivos) + frontend en 77 arquivos en verde, ruff + analyze limpos.
