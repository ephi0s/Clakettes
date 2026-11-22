# Code audit — Clakettes (rev. 10/10/2026, multi-platform expansion 09/10/2026)

[ES](../es/AUDITORIA.md) · [EN](AUDITORIA.md) · [FR](../fr/AUDITORIA.md) · [DE](../de/AUDITORIA.md) · [IT](../it/AUDITORIA.md) · [CA](../ca/AUDITORIA.md) · [EU](../eu/AUDITORIA.md) · [GL](../gl/AUDITORIA.md) · [OC](../oc/AUDITORIA.md)

## 0. Executive summary

Review of dependencies, applied optimizations and pending technical debt of the Clakettes project.

## 1. External dependencies: what can be removed and what cannot

### Backend (`backend/requirements.txt` + `pyproject.toml`)

| Dep | Verdict | Reason |
| --- | --- | --- |
| fastapi, uvicorn[standard], sqlalchemy, pydantic(+settings), alembic | Keep | Core stack |
| PyJWT==2.15.1 | Migration completed | `python-jose` removed; `app/auth.py` and `routers/dependencies.py` use PyJWT (bump 2.10.1 → 2.15.0 → 2.15.1) |
| python-dotenv | Not included | Not listed in `pyproject.toml`/`requirements*.txt` nor imported in `backend/`; `pydantic-settings` loads `.env` directly |
| pymysql | Keep as prod driver | Only used with MariaDB; not loading it in dev saves nothing (lazy import already in SQLAlchemy) |
| python-multipart, email-validator, bcrypt | Keep | Uploads, email validation, password hashing |
| reportlab 5.1.0 | Keep, but with lazy import (done) | Only `export_service._build_pdf`; previously imported at module level (~200 ms + memory per worker). Now imported inside the function. Also `pyproject.toml` synchronized (was missing) and pinned `==5.1.0` |

**Versions pinned in `backend/pyproject.toml` / `requirements*.txt`:** `fastapi==0.163.1`, `uvicorn[standard]==0.54.0`, `sqlalchemy==2.1.9`, `pydantic==2.14.3`, `pydantic-settings==2.16.3`, `email-validator==2.4.0`, `pymysql==1.2.4`, `python-multipart==0.0.34`, `PyJWT==2.15.1`, `cryptography==50.0.2`, `bcrypt>=4.3.0`, `alembic==1.20.1`, `reportlab==5.1.0`, `Pillow==13.0.0`, `mutagen==1.48.1`, `pypdf==7.1.0` (major from 6.21.x); development: `pytest>=9.2.0`, `ruff==0.17.5`, `httpx==0.28.1`, `caldav==3.7.0`, `icalendar==7.3.0`.

### Frontend (`frontend/pubspec.yaml`)

All dependencies are in real use; none could be removed without breaking functionality:

- `archive`: used in `crypto_utils.dart` (ZLib/GZip). `dart:io` does not work because it breaks web.
- `path_provider`: used in `file_downloader_io.dart` (mobile/desktop).
- `web`: used in `file_downloader_web.dart`.
- `pointycastle` + `crypto`: chat E2EE (ECDH P-256 + AES-GCM; the name `X25519` appears only in a legacy field).
- `flutter_map` + `latlong2` + `geolocator` + `url_launcher`: maps.
- `table_calendar`, `flutter_local_notifications` + `timezone` + `flutter_timezone`, `image_picker` + `file_picker`: each with 1-2 uses, but removing them would remove functionality.

## 2. Applied optimizations

1. `export_service.py`: lazy reportlab import in `_build_pdf` + docstring.
2. `main.py` RateLimitMiddleware + `routers/admin.py` + `routers/auth.py` + `routers/auth_sessions.py` + `routers/federation.py`: 5 `RateLimiter` instances (buckets `middleware:`/`dav:` + limiters for `reset` 3/300 s, `login` 5/300 s, `refresh` 20/60 s and federation 60/60 s); do not unify without losing distinct limits. The bypass goes through `app.config.is_testing()` (`1/true/yes/on`).
3. `base_service.py`: `paginate` fixes `page>=1`, `size` in `[1,100]`; new `paginate_filtered()` defined with 0 uses (pending migration of cloned `get_all_paginated`).
4. `routers/dependencies.py`: `get_current_user_optional` reuses `validate_access_token` (removes ~30 duplicated JWT+session lines); fix `__import__("datetime")` → normal import; new `get_or_404()` to replace ~100 inline `HTTPException(404)`.
5. `dav/auth.py`: documented relationship with `app.auth.hash_token` (formerly `_hash_token`; the alias is kept for compatibility).
6. `pyproject.toml`/`requirements.txt` synchronized (reportlab).
7. `reusable_widgets.dart`: new `showAppSnack()` (1 def + 8 uses; 115 `ScaffoldMessenger` direct remain).

## 3. Multi-platform improvements applied (desktop + web + Android + iOS/iPad)

1. `BackendConfig`: platform default — Android emulator uses `10.0.2.2:8000` (emulator localhost is the virtual itself, not the host); rest `localhost:8000`. Priority: saved URL > `--dart-define=BACKEND_URL` > platform default. `ApiService` uses the same default in constructor and getters.
2. `NotificationService`: on web (`kIsWeb`) `init` does not touch plugin or timezone (no local notifications in browser) and `scheduleReminder` does nothing; documented in docstring. No platform branches on screens.
3. `file_downloader.dart`: verified conditional import (`web` by default, `io` if `dart.library.io`) — covers browser, desktop, Android and iOS without changes.
4. `main_scaffold.dart`: added Shorts to navigation (screen `screenIndex 3` existed but without item — inaccessible). Rail >800px (desktop/web), Bar <800px (mobile), Drawer on all.
5. `AndroidManifest.xml`: added INTERNET, ACCESS_NETWORK_STATE, location (FINE+COARSE), CAMERA, READ_MEDIA_IMAGES/VIDEO, SCHEDULE/USE_EXACT_ALARM. Without explicit INTERNET, release builds have no network.
6. `ios/Runner/Info.plist`: added NSLocationWhenInUse, NSCamera, NSPhotoLibrary (+Add). Without these the system denies or the App Store rejects.
7. Backend `routers/festivals.py`: pilot `get_or_404(db, Festival/Location, ...)` — 9 `if not → 404` blocks removed; extended to `shortfilms.py` (3) and `users.py` (4). Pattern to extend to the rest of routers.
8. Frontend `awards_screen.dart`: error SnackBar migrated to `showAppSnack()` (pilot). Note: the 24 remaining `AlertDialog`s are *form* dialogs (create/edit), not confirmation dialogs — they do not migrate to `showConfirmDialog` (19 uses in 18 screens); would require a common `CreateEntityDialog`.
9. CI: `ruff format --check` gate added (GH + GitLab) after verifying `216 files already formatted`.
10. Security (pilot `channels.py`, security block): new `require_channel_member`/`is_channel_member` in `permissions.py` and use in `channels.py` + `chat.py` (removes 3 inline blocks with deferred imports); `channels.py` migrated to `get_or_404` (7 fewer blocks); role whitelist `Literal[admin,moderator,member]` in schemas (before: free string → 500 by CheckConstraint; now: 422); 4 new 403/422 tests in `TestChannelAuthorization`.
11. Security: `POST /delegations/{id}/revoke` required only auth — anyone could revoke others' delegations. Now verifies delegator or admin + 403 test. Verified OK (no changes): `user_roles`/`user_festival` (attendee whitelist), DMs (ownership), public forms (optional auth), WS (validates session), `bulk_create` (single commit), SyncQueue (retry+backoff), i18n (0 missing keys), `locations` (didChangeDependencies with guard).
12. `get_or_404` extended to `committees.py` (10), `events.py` (58, via script with review + 17 unassigned to avoid F841), `delegations` (2) and 5 location routers (12). This batch introduced no migration; later revisions did add `a8b9c0d1e2f3` (seat uniqueness) and `b9c0d1e2f3a4` (`contest_type` in shorts), both already applied at head `b9c0d1e2f3a4`.
13. Performance: `venue` filter on programming moved to SQL (before it filtered the page in Python and broke `total`/`pages`).
14. Frontend: anti-double-submit guards on creating festival/user/short + 3 SnackBars migrated to `showAppSnack`.
15. Chat: E2EE off UI thread — `_prepareContent`/`_unpackContent` use `encryptAsync`/`decryptAsync` (isolates); new `encryptSenderKeyAsync`/`decryptSenderKeyAsync` used in sender key distribution and reception. `RestChatBackend` is kept: used by `chat_service_test` as fake (was not dead code).
16. Chat: `chat_screen.dart` 1038 → 709 lines; bubbles to `widgets/chat_bubble.dart` (`ChatBubble` + `ChatBubbleWidget` with image, location, vCard, iCal) and bar to `widgets/chat_input_bar.dart` (`ChatInputBar`). 2 new async tests in `crypto_utils_test`.
17. `locations_screen` 1144 → 645 lines: cards and form to `widgets/location_cards.dart` (`LocationCard`, `LegacyCard`, `LegacyLocation`, `LocationFormScreen`, `LocationFormResult`); deletion with `showConfirmDialog` + `showAppSnack` (one AlertDialog less).
18. `festival_profile_screen` 1276 → 1173 lines: `RulebooksSection` and `FestivalLocationsSection` (+ map and cards) to `widgets/festival_sections.dart`. The screen keeps state, reading, editing and callbacks.
19. `api_service.dart` 1134 → 464 lines: 95 methods moved to `lib/services/api/` (`event_api` 31, `location_api` 25, `org_api` 17, `catalog_api` 13, rest to `user_api` + `calendar/channel/festival/form`). The core keeps config, auth, transport and admin/search. Public API intact.
20. `user_profile_screen` 996 → 1391 lines: `SessionsCard` and `AliasesCard` to `widgets/user_profile_cards.dart`. Fixed 4 `if` without braces inherited in `catalog_api`.
21. Flow tests (`tests/integration/test_flows.py`): complete reservation (festival → event → seats → reservation → occupancy), messaging (channel → member → DM → read → delete) and delegation (create → list → revoke).
22. Widget tests of extracted widgets (13): `chat_bubble`, `chat_input_bar`, `user_profile_cards`, `location_cards`. Note: widgets under `wrapWithLocalization` need an extra `pump()` (the localization Builder resolves in the second frame).
23. Native push without Firebase (`docs/en/PUSH.md`): browser Notification API on web (`notification_web.dart` + stub with conditional export, no new deps), `flutter_local_notifications` on desktop + macOS permission on start, mobile as explicit no-op (`_supported`). `flutter build web` verified.
24. Documentation: `docs/en/API.md`, `docs/en/ARQUITECTURA.md`, `docs/en/USO.md`, `docs/en/DESARROLLO.md`, `docs/en/SEGURIDAD.md`, `docs/en/BACKEND.md` + `docs/en/DATABASE.md` (moved from `backend/` on 10/10/2026). READMEs and `AGENTS.md` with real figures; dev admin `admin`/`setup` (no `ADMIN_PASSWORD` in `backend/.env.example`; seed only non-prod in `app/main.py:257`).
