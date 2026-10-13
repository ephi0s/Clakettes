# Code audit — Clakettes (09/10/2026, multi-platform ext. 09/10/2026, rev. 10/10/2026)

[ES](AUDITORIA.md) · [EN](AUDITORIA.en.md) · [FR](AUDITORIA.fr.md) · [DE](AUDITORIA.de.md) · [IT](AUDITORIA.it.md) · [CA](AUDITORIA.ca.md) · [EU](AUDITORIA.eu.md) · [GL](AUDITORIA.gl.md) · [OC](AUDITORIA.oc.md)

> **Addendum 11/10/2026** (verified figures): backend 1402 tests in 37 files;
> routers 36 files (33 with `APIRouter`); services 36; models 34; schemas 33;
> Alembic 18 versions; `docs/API.md` 310 endpoints (unique operationIds).
> GDPR: privacy by default, consent, erasure/export, session purge,
> append-only audit, metadata sanitizing, TLS for MariaDB in prod,
> DAV with expiry, CSP/HSTS. Mock/stripe/redsys payment providers.

## 0. Executive summary (10/10/2026, verified figures)

| Area | Status | Detail |
| --- | --- | --- |
| Backend tests | 1321 `def test_` in 33 files | `Get-ChildItem backend/tests -Recurse -Filter "test_*.py" \| Select-String "def test_"` |
| Frontend tests | 347 blocks in 69 files | `Get-ChildItem frontend/test -Recurse -Filter "*_test.dart" \| Select-String "testWidgets\(|test\("` |
| Routers/Services/Models/Schemas | 35/33/33/32 files (33 routers with `APIRouter`) | `permissions.py`/`dependencies.py` are helpers without a router; `base.py`/`__init__.py` are not entities |
| Migrations | 15 + `__init__.py` | `alembic/versions/` |
| Endpoints | 294 in 33 routers (`docs/API.md` via AST) | `python tools/gen_api.py` idempotent; plain grep gives 272 (does not count `propfind/report/options/websocket`) |
| Lint | `ruff check` + `ruff format --check` clean (216 files) | `AGENTS.md` and CI (GH + GitLab) with format gate |
| Docs | Backend consolidated in `docs/` | `docs/BACKEND.md` + `docs/DATABASE.md`; index in `docs/README.md` |
| Main debt | partial `get_or_404`, `paginate_filtered` unused, `python-jose` not migrated, 24 `AlertDialog` / 115 `ScaffoldMessenger` remaining | See §5 with counts and verification |

How to re-verify: `cd backend; python -m ruff check .; python -m pytest tests/ -x -q --tb=short` and `cd frontend; flutter analyze; flutter test`.

## 1. External dependencies: what can be removed and what cannot

### Backend (`backend/requirements.txt` + `pyproject.toml`)

| Dep | Verdict | Reason |
| --- | --- | --- |
| fastapi, uvicorn[standard], sqlalchemy, pydantic(+settings), alembic | Keep | Core of the stack |
| python-jose[cryptography] | Keep for now, migrate to PyJWT later | Abandoned since 2016, but the change touches `app/auth.py` + `routers/dependencies.py` + tests; do it in a separate PR with token tests |
| python-dotenv | Keep | Required by `pydantic-settings>=2` and `uvicorn[standard]` (`--env-file`); only 2 scripts import it directly, but removing it would break `.env` loading |
| pymysql | Keep as prod driver | Only used with MariaDB; not loading it in dev saves nothing (already lazy import in SQLAlchemy) |
| python-multipart, email-validator, bcrypt | Keep | Uploads, email validation, password hashing |
| reportlab 5.0.1 | Keep, but with lazy import (done) | Only `export_service._build_pdf`; previously imported at module level (~200 ms + memory per worker). Now imported inside the function. Also synced `pyproject.toml` (missing) and pinned `==5.0.1` |

### Frontend (`frontend/pubspec.yaml`)

All dependencies are in real use; none could be removed without breaking functionality:

- `archive`: used in `crypto_utils.dart` (ZLib/GZip). `dart:io` is not valid because it breaks web.
- `path_provider`: used in `file_downloader_io.dart` (mobile/desktop).
- `web`: used in `file_downloader_web.dart`.
- `pointycastle` + `crypto` + `uuid`: chat E2EE (X25519/ECDH P-256 + AES-GCM).
- `flutter_map` + `cancellable_tile` + `latlong2` + `geolocator` + `url_launcher`: maps.
- `table_calendar`, `flutter_local_notifications` + `timezone` + `flutter_timezone`, `image_picker` + `file_picker`: each with 1–2 uses, but removing them would remove functionality.

## 2. Applied optimizations

1. `export_service.py`: lazy reportlab import in `_build_pdf` + docstring.
2. `main.py` RateLimitMiddleware + `routers/admin.py` + `routers/auth.py`: 3 `RateLimiter` instances (`middleware:`/`dav:` buckets + `reset` 3/300s and `login` limiters); do not unify without losing distinct limits.
3. `base_service.py`: `paginate` pins `page>=1`, `size` in `[1,100]`; new `paginate_filtered()` defined with 0 uses (pending migration of cloned `get_all_paginated`).
4. `routers/dependencies.py`: `get_current_user_optional` reuses `validate_access_token` (removes ~30 duplicated JWT+session lines); fix `__import__("datetime")` → normal import; new `get_or_404()` to replace ~100 inline `HTTPException(404)`.
5. `dav/auth.py`: documented the relation with `app.auth._hash_token`.
6. `pyproject.toml`/`requirements.txt` synced (reportlab).
7. `reusable_widgets.dart`: new `showAppSnack()` (1 def + 8 uses; 115 direct `ScaffoldMessenger` remaining).

## 3. Applied multi-platform improvements (desktop + web + Android + iOS/iPad)

1. `BackendConfig`: platform default — Android emulator uses `10.0.2.2:8000`
   (the emulator localhost is the virtual device itself, not the host); rest `localhost:8000`.
   Priority: saved URL > `--dart-define=BACKEND_URL` > platform default.
   `ApiService` uses the same default in constructor and getters.
2. `NotificationService`: on web (`kIsWeb`) `init` touches neither plugin nor timezone
   (no local notifications in the browser) and `scheduleReminder` does nothing;
   documented in the docstring. No per-platform branches in screens.
3. `file_downloader.dart`: verified conditional import
   (`web` by default, `io` if `dart.library.io`) — covers browser, desktop,
   Android and iOS without changes.
4. `main_scaffold.dart`: added Shorts to navigation (the
   `screenIndex 3` screen existed but had no item — unreachable). Rail >800px (desktop/web),
   Bar <800px (mobile), Drawer everywhere.
5. `AndroidManifest.xml`: added INTERNET, ACCESS_NETWORK_STATE, location
   (FINE+COARSE), CAMERA, READ_MEDIA_IMAGES/VIDEO, SCHEDULE/USE_EXACT_ALARM.
   Without explicit INTERNET, release builds have no network.
6. `ios/Runner/Info.plist`: added NSLocationWhenInUse, NSCamera,
   NSPhotoLibrary (+Add). Without these the system denies access or the App Store rejects the build.
7. Backend `routers/festivals.py`: `get_or_404(db, Festival/Location, ...)` pilot
   — 9 `if not → 404` blocks removed; extended to `shortfilms.py` (3) and
   `users.py` (4). Pattern to extend to the remaining routers.
8. Frontend `awards_screen.dart`: error SnackBar migrated to `showAppSnack()`
   (pilot). Note: the 24 remaining `AlertDialog` are *form* dialogs
   (create/edit), not confirmation dialogs — they do not migrate to `showConfirmDialog`
   (19 uses in 18 screens); they would require a common `CreateEntityDialog`.
9. CI: `ruff format --check` gate added (GH + GitLab) after verifying
   `216 files already formatted`.
10. Security (`channels.py` pilot, security block): new
    `require_channel_member`/`is_channel_member` in `permissions.py` and use in
    `channels.py` + `chat.py` (removes 3 inline blocks with deferred imports);
    `channels.py` migrated to `get_or_404` (7 fewer blocks); role whitelist
    `Literal[admin,moderator,member]` in schemas (before: free string → 500
    on CheckConstraint; now: 422); 4 new 403/422 tests in
    `TestChannelAuthorization`.
11. Security: `POST /delegations/{id}/revoke` required only auth — anyone
    could revoke чужой delegations. Now verifies delegator or admin + 403 test.
    Already verified OK (no changes): `user_roles`/`user_festival` (attendee whitelist), DMs (ownership), public forms (optional auth), WS
    (validates session), `bulk_create` (single commit), SyncQueue (retry+backoff),
    i18n (0 missing keys), `locations` (didChangeDependencies with guard).
12. `get_or_404` extended to `committees.py` (10), `events.py` (58, via script
    with review + 17 unassigned exists to avoid F841), `delegations`
    (2) and 5 location routers (12). No schema changes: no pending
    Alembic migration from this batch.
13. Performance: programming `venue` filter lowered to SQL (previously filtered
    the page in Python and broke `total`/`pages`).
14. Frontend: anti-double-submit guards on create festival/user/short +
    3 SnackBars migrated to `showAppSnack`.
15. Chat: E2EE off the UI thread — `_prepareContent`/`_unpackContent` use
    `encryptAsync`/`decryptAsync` (isolates); new `encryptSenderKeyAsync`/
    `decryptSenderKeyAsync` used in sender-key broadcast and reception.
    `RestChatBackend` is kept: `chat_service_test` uses it as a fake
    (it was not dead code).
16. Chat: `chat_screen.dart` 1038 → 767 lines; bubbles to
    `widgets/chat_bubble.dart` (`ChatBubble` + `ChatBubbleWidget` with image,
    location, vCard, iCal) and bar to `widgets/chat_input_bar.dart`
    (`ChatInputBar`). 2 new async tests in `crypto_utils_test`.
17. `locations_screen` 1144 → 680 lines: cards and form to
    `widgets/location_cards.dart` (`LocationCard`, `LegacyCard`,
    `LegacyLocation`, `LocationFormScreen`, `LocationFormResult`); deletion
    with `showConfirmDialog` + `showAppSnack` (one less AlertDialog).
18. `festival_profile_screen` 1276 → 956 lines: `RulebooksSection` and
    `FestivalLocationsSection` (+ map and cards) to
    `widgets/festival_sections.dart`. The screen keeps state,
    reading, editing and callbacks.
19. `api_service.dart` 1134 → 511 lines: 95 methods moved to `lib/services/api/`
    (`event_api` 31, `location_api` 25, `org_api` 17, `catalog_api` 13,
    rest to `user_api` + `calendar/channel/festival/form`). The core keeps config, auth, transport and
    admin/search. Public API intact.
20. `user_profile_screen` 996 → 803 lines: `SessionsCard` and `AliasesCard`
    to `widgets/user_profile_cards.dart`. Fixed 4 braceless `if`
    inherited in `catalog_api`.
21. Flow tests (`tests/integration/test_flows.py`): full booking
    (festival → event → seats → reservation → occupancy), messaging
    (channel → member → DM → read → delete) and delegation (create →
    list → revoke).
22. Widget tests for the extracted widgets (13): `chat_bubble`,
    `chat_input_bar`, `user_profile_cards`, `location_cards`. Note:
    widgets under `wrapWithLocalization` need an extra `pump()`
    (the localization Builder resolves on the second frame).
23. Native push without Firebase (`docs/PUSH.md`): browser Notification API
    on web (`notification_web.dart` + stub with conditional export, no new
    deps), `flutter_local_notifications` on desktop + macOS permission at
    startup, mobile as explicit no-op (`_supported`). `flutter build web`
    verified.
24. Documentation: `docs/API.md` (294 endpoints in 33 routers, AST-generated
    with `tools/gen_api.py` — regenerable), `docs/ARQUITECTURA.md`
    (layers, flows, multi-platform decisions), `docs/USO.md` (startup,
    env, operation, roles), `docs/DESARROLLO.md` (conventions + CI
    gates), `docs/SEGURIDAD.md` (tokens, permission matrix, prod checklist),
    `docs/BACKEND.md` + `docs/DATABASE.md` (moved from `backend/` on 10/10/2026).
    READMEs and `AGENTS.md` with real figures; dev admin `admin`/`setup`
    (no `ADMIN_PASSWORD` in `.env.example`; non-prod-only seed in `app/main.py:257`).
Status: 1321 backend tests (33 files) + 347 frontend (69 files) green, ruff + analyze clean.

## 4. Review 10/10/2026 (corrections to §2–§3)

1. Consolidated backend docs: `backend/BACKEND.md` + `backend/DATABASE.md` → `docs/BACKEND.md` + `docs/DATABASE.md`; links updated in `README.md`, `AGENTS.md`, `docs/README.md`, `ARQUITECTURA.md`, `USO.md`, `ADMINISTRACION.md`.
2. Real count: routers 35 files (33 with `APIRouter`; `permissions.py`/`dependencies.py` are helpers), services 33 modules (+`__init__`), models 33 entities (+`base.py`+`__init__`), schemas 32, Alembic 15, `API.md` 294 endpoints/33 routers (AST counts `propfind/report/options/websocket`; plain grep gives 272).
3. Tests: backend 1321 `def test_` in 33 files (not 1366/38); frontend 347 blocks in 69 files (not 313/70). Widgets 24 OK. Screens: `festival_profile` 956L, `locations` 680L, `chat` 767L, `api_service` 511L, `user_profile` 803L.
4. Corrections to §2: `RateLimiter` are 3 instances (`main.py`, `admin.py`, `auth.py`), not 1; `ADMIN_PASSWORD` does not exist in `backend/.env.example` (only `admin/setup` comment); `ruff format` covers 216 files (not 215).
5. `tools/gen_api.py` regenerates `API.md` idempotently but with a hardcoded absolute path and no shebang (not portable).

## 5. Maintainability backlog (suggested order, with verification)

| # | Task | Status 10/10/2026 | How to verify |
| --- | --- | --- | --- |
| 1 | Migrate routers to `get_or_404` and services to `paginate_filtered` | `get_or_404` in 13 routers (110 uses), 186 remaining inline `404`; `paginate_filtered` with 0 uses | `Select-String "get_or_404\(" backend/app/routers; Select-String "404" backend/app/routers; Select-String "paginate_filtered" backend/app/services` |
| 2 | Migrate `python-jose` → `PyJWT` (isolated PR with expiry/type/rotation tests) | Not migrated (`app/auth.py` uses `jose`) | `Select-String "from jose\|import jose" backend/app; Select-String "import jwt" backend/app` |
| 3 | Split large screens | Done: `festival_profile` 956L, `locations` 680L, `api_service` 511L, `chat` 767L, `user_profile` 803L (widgets extracted in `lib/widgets/`) | `(Get-Content frontend/lib/screens/<screen>).Count` |
| 4 | Migrate `AlertDialog` → `ConfirmDialog` and `ScaffoldMessenger` → `showAppSnack` | 24 `AlertDialog` vs 19 `showConfirmDialog` uses; 115 `ScaffoldMessenger` vs 8 `showAppSnack` uses (remaining `AlertDialog` are forms: require a common `CreateEntityDialog`) | `Select-String "AlertDialog|showConfirmDialog|ScaffoldMessenger|showAppSnack" frontend/lib` |
| 5 | Format hygiene + `.gitignore` | `ruff format --check` + `ruff check` clean and gated in CI (GH + GitLab); `.gitignore` covers `*.db*`, `*.hive`, `*.lock`, `uploads/` (not the `*.hive*` glob) | `ruff format --check .; ruff check .; Get-Content .gitignore` |
