# Code-Audit — Clakettes (09/10/2026, erw. Multiplattform 09/10/2026, Rev. 10/10/2026)

[ES](AUDITORIA.md) · [EN](AUDITORIA.en.md) · [FR](AUDITORIA.fr.md) · [DE](AUDITORIA.de.md) · [IT](AUDITORIA.it.md) · [CA](AUDITORIA.ca.md) · [EU](AUDITORIA.eu.md) · [GL](AUDITORIA.gl.md) · [OC](AUDITORIA.oc.md)

> **Nachtrag 11/10/2026** (verifizierte Zahlen): Backend 1402 Tests in 37 Dateien;
> Router 36 Dateien (33 mit `APIRouter`); Services 36; Models 34; Schemas 33;
> Alembic 18 Versionen; `docs/API.md` 310 Endpunkte (eindeutige operationIds).
> DSGVO: Privacy by Default, Einwilligung, Löschung/Export, Sitzungs-Purge,
> Append-only-Audit, Metadaten-Bereinigung, TLS für MariaDB in Prod,
> DAV mit Ablauf, CSP/HSTS. Zahlungsanbieter mock/stripe/redsys.

## 0. Zusammenfassung (10/10/2026, verifizierte Zahlen)

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

So re-verifizieren: `cd backend; python -m ruff check .; python -m pytest tests/ -x -q --tb=short` und `cd frontend; flutter analyze; flutter test`.

## 1. Externe Abhängigkeiten: was entfernbar ist und was nicht

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

Alle Abhängigkeiten werden tatsächlich verwendet; keine konnte ohne Funktionsverlust entfernt werden:

- `archive`: verwendet in `crypto_utils.dart` (ZLib/GZip). `dart:io` genügt nicht, da es Web bricht.
- `path_provider`: verwendet in `file_downloader_io.dart` (mobil/desktop).
- `web`: verwendet in `file_downloader_web.dart`.
- `pointycastle` + `crypto` + `uuid`: E2EE des Chats (X25519/ECDH P-256 + AES-GCM).
- `flutter_map` + `cancellable_tile` + `latlong2` + `geolocator` + `url_launcher`: Karten.
- `table_calendar`, `flutter_local_notifications` + `timezone` + `flutter_timezone`, `image_picker` + `file_picker`: je mit 1–2 Verwendungen, doch Entfernen würde Funktionalität streichen.

## 2. Angewandte Optimierungen

1. `export_service.py`: Lazy-Import von reportlab in `_build_pdf` + Docstring.
2. `main.py` RateLimitMiddleware + `routers/admin.py` + `routers/auth.py`: 3 `RateLimiter`-Instanzen (Buckets `middleware:`/`dav:` + Limiter für `reset` 3/300s und `login`); nicht vereinen ohne unterschiedliche Limits zu verlieren.
3. `base_service.py`: `paginate` fixiert `page>=1`, `size` in `[1,100]`; neues `paginate_filtered()` definiert mit 0 Verwendungen (Migration der geklonten `get_all_paginated` ausstehend).
4. `routers/dependencies.py`: `get_current_user_optional` nutzt `validate_access_token` wieder (entfernt ~30 doppelte JWT+Sitzungs-Zeilen); Fix `__import__("datetime")` → normaler Import; neues `get_or_404()` zum Ersetzen von ~100 inline-`HTTPException(404)`.
5. `dav/auth.py`: Beziehung zu `app.auth._hash_token` dokumentiert.
6. `pyproject.toml`/`requirements.txt` synchronisiert (reportlab).
7. `reusable_widgets.dart`: neues `showAppSnack()` (1 Def + 8 Verwendungen; 115 direkte `ScaffoldMessenger` verbleiben).

## 3. Angewandte Multiplattform-Verbesserungen (Desktop + Web + Android + iOS/iPad)

1. `BackendConfig`: Default je Plattform — Android-Emulator nutzt `10.0.2.2:8000`
   (localhost des Emulators ist das Virtuelle selbst, nicht der Host); Rest `localhost:8000`.
   Priorität: gespeicherte URL > `--dart-define=BACKEND_URL` > Plattform-Default.
   `ApiService` nutzt denselben Default in Konstruktor und Gettern.
2. `NotificationService`: auf Web (`kIsWeb`) berührt `init` weder Plugin noch Timezone
   (keine lokalen Benachrichtigungen im Browser) und `scheduleReminder` tut nichts;
   im Docstring dokumentiert. Keine Plattformzweige in den Screens.
3. `file_downloader.dart`: konditionaler Import verifiziert
   (`web` per Default, `io` wenn `dart.library.io`) — deckt Browser, Desktop,
   Android und iOS ohne Änderungen ab.
4. `main_scaffold.dart`: Cortos zur Navigation hinzugefügt (Screen
   `screenIndex 3` existierte, aber ohne Item — unerreichbar). Rail >800px (Desktop/Web),
   Bar <800px (mobil), Drawer überall.
5. `AndroidManifest.xml`: INTERNET, ACCESS_NETWORK_STATE, Standort
   (FINE+COARSE), CAMERA, READ_MEDIA_IMAGES/VIDEO, SCHEDULE/USE_EXACT_ALARM hinzugefügt.
   Ohne explizites INTERNET haben Release-Builds kein Netz.
6. `ios/Runner/Info.plist`: NSLocationWhenInUse, NSCamera,
   NSPhotoLibrary (+Add) hinzugefügt. Ohne diese verweigert das System oder die App Store lehnt ab.
7. Backend `routers/festivals.py`: Pilot `get_or_404(db, Festival/Location, ...)`
   — 9 `if not → 404`-Blöcke entfernt; erweitert auf `shortfilms.py` (3) und
   `users.py` (4). Muster auf restliche Router zu erweitern.
8. Frontend `awards_screen.dart`: Fehler-SnackBar auf `showAppSnack()` migriert
   (Pilot). Hinweis: die 24 restlichen `AlertDialog` sind *Formular*-Dialoge
   (Erstellen/Bearbeiten), keine Bestätigung — sie migrieren nicht zu `showConfirmDialog`
   (19 Verwendungen in 18 Screens); sie bräuchten einen gemeinsamen `CreateEntityDialog`.
9. CI: Gate `ruff format --check` hinzugefügt (GH + GitLab) nach Verifikation
   `216 files already formatted`.
10. Sicherheit (Pilot `channels.py`, Sicherheitsblock): neues
    `require_channel_member`/`is_channel_member` in `permissions.py` und Verwendung in
    `channels.py` + `chat.py` (entfernt 3 Inline-Blöcke mit verzögerten Imports);
    `channels.py` auf `get_or_404` migriert (7 Blöcke weniger); Rollen-Whitelist
    `Literal[admin,moderator,member]` in Schemas (vorher: freier String → 500
    durch CheckConstraint; jetzt: 422); 4 neue 403/422-Tests in
    `TestChannelAuthorization`.
11. Sicherheit: `POST /delegations/{id}/revoke` verlangte nur Auth — jeder
    konnte fremde Delegierungen widerrufen. Jetzt prüft es Delegierer oder Admin + 403-Test.
    Bereits als OK verifiziert (ohne Änderungen): `user_roles`/`user_festival` (Whitelist
    attendee), DMs (Ownership), öffentliche Formulare (optionale Auth), WS
    (validiert Sitzung), `bulk_create` (single commit), SyncQueue (retry+backoff),
    i18n (0 fehlende Keys), `locations` (didChangeDependencies mit Guard).
12. `get_or_404` erweitert auf `committees.py` (10), `events.py` (58, per Skript
    mit Review + 17 unzugeordnete Existenzen zur Vermeidung von F841), `delegations`
    (2) und 5 Location-Router (12). Ohne Schemaänderung: keine offene
    Alembic-Migration durch dieses Paket.
13. Performance: `venue`-Filter der Programmplanung nach SQL verlagert (vorher filterte
    die Seite in Python und brach `total`/`pages`).
14. Frontend: Guards gegen Doppelversand beim Erstellen von Festival/Nutzer/Kurzfilm +
    3 SnackBars auf `showAppSnack` migriert.
15. Chat: E2EE aus dem UI-Thread — `_prepareContent`/`_unpackContent` nutzen
    `encryptAsync`/`decryptAsync` (Isolates); neue `encryptSenderKeyAsync`/
    `decryptSenderKeyAsync` in Verbreitung und Empfang von Sender-Keys genutzt.
    `RestChatBackend` bleibt erhalten: es nutzt `chat_service_test` als Fake
    (war kein toter Code).
16. Chat: `chat_screen.dart` 1038 → 767 Zeilen; Bubbles nach
    `widgets/chat_bubble.dart` (`ChatBubble` + `ChatBubbleWidget` mit Bild,
    Standort, vCard, iCal) und Leiste nach `widgets/chat_input_bar.dart`
    (`ChatInputBar`). 2 neue Async-Tests in `crypto_utils_test`.
17. `locations_screen` 1144 → 680 Zeilen: Karten und Formular nach
    `widgets/location_cards.dart` (`LocationCard`, `LegacyCard`,
    `LegacyLocation`, `LocationFormScreen`, `LocationFormResult`); Löschen
    mit `showConfirmDialog` + `showAppSnack` (ein AlertDialog weniger).
18. `festival_profile_screen` 1276 → 956 Zeilen: `RulebooksSection` und
    `FestivalLocationsSection` (+ Karte und Karten) nach
    `widgets/festival_sections.dart`. Der Screen behält State,
    Lesen, Bearbeiten und Callbacks.
19. `api_service.dart` 1134 → 511 Zeilen: 95 Methoden nach `lib/services/api/` verschoben
    (`event_api` 31, `location_api` 25, `org_api` 17, `catalog_api` 13,
    Rest nach `user_api` + `calendar/channel/festival/form`). Der Kern behält Config, Auth, Transport und
    Admin/Suche. Öffentliche API intakt.
20. `user_profile_screen` 996 → 803 Zeilen: `SessionsCard` und `AliasesCard`
    nach `widgets/user_profile_cards.dart`. 4 geerbte `if` ohne Klammern
    in `catalog_api` korrigiert.
21. Flow-Tests (`tests/integration/test_flows.py`): komplette Reservierung
    (Festival → Event → Sitze → Reservierung → Belegung), Messaging
    (Kanal → Mitglied → DM → Lesen → Löschen) und Delegierung (erstellen →
    listen → widerrufen).
22. Widget-Tests der extrahierten Widgets (13): `chat_bubble`,
    `chat_input_bar`, `user_profile_cards`, `location_cards`. Hinweis: Widgets
    unter `wrapWithLocalization` brauchen ein extra `pump()`
    (der Lokalisierungs-Builder löst im zweiten Frame auf).
23. Nativer Push ohne Firebase (`docs/PUSH.de.md`): native Browser-Notification-API
    auf Web (`notification_web.dart` + Stub mit konditionalem Export, ohne neue
    Deps), `flutter_local_notifications` auf Desktop + macOS-Berechtigung beim
    Start, mobil als explizites No-op (`_supported`). `flutter build web`
    verifiziert.
24. Dokumentation: `docs/API.md` (294 Endpunkte in 33 Routern, per AST mit
    `tools/gen_api.py` erzeugt — regenerierbar), `docs/ARQUITECTURA.de.md`
    (Schichten, Abläufe, Multiplattform-Entscheidungen), `docs/USO.de.md` (Start,
    Env, Betrieb, Rollen), `docs/DESARROLLO.de.md` (Konventionen + CI-Gates),
    `docs/SEGURIDAD.de.md` (Tokens, Berechtigungsmatrix, Prod-Checkliste),
    `docs/BACKEND.de.md` + `docs/DATABASE.de.md` (verschoben aus `backend/` am 10/10/2026).
    READMEs und `AGENTS.md` mit realen Zahlen; Dev-Admin `admin`/`setup`
    (ohne `ADMIN_PASSWORD` in `.env.example`; Seed nur Nicht-Prod in `app/main.py:257`).
Status: 1321 Backend-Tests (33 Dateien) + 347 Frontend (69 Dateien) grün, ruff + analyze sauber.

## 4. Review 10/10/2026 (Korrekturen zu §2–§3)

1. Backend-Docs konsolidiert: `backend/BACKEND.md` + `backend/DATABASE.md` → `docs/BACKEND.md` + `docs/DATABASE.md`; Links aktualisiert in `README.md`, `AGENTS.md`, `docs/README.md`, `ARQUITECTURA.md`, `USO.md`, `ADMINISTRACION.md`.
2. Reale Zählung: Router 35 Dateien (33 mit `APIRouter`; `permissions.py`/`dependencies.py` sind Helper), Services 33 Module (+`__init__`), Models 33 Entitäten (+`base.py`+`__init__`), Schemas 32, Alembic 15, `API.md` 294 Endpunkte/33 Router (AST zählt `propfind/report/options/websocket`; einfaches grep gibt 272).
3. Tests: Backend 1321 `def test_` in 33 Dateien (nicht 1366/38); Frontend 347 Blöcke in 69 Dateien (nicht 313/70). Widgets 24 OK. Screens: `festival_profile` 956L, `locations` 680L, `chat` 767L, `api_service` 511L, `user_profile` 803L.
4. Korrekturen zu §2: `RateLimiter` sind 3 Instanzen (`main.py`, `admin.py`, `auth.py`), nicht 1; `ADMIN_PASSWORD` existiert nicht in `backend/.env.example` (nur Kommentar `admin/setup`); `ruff format` deckt 216 Dateien ab (nicht 215).
5. `tools/gen_api.py` regeneriert `API.md` idempotent, aber mit hartcodiertem absolutem Pfad und ohne Shebang (nicht portabel).

## 5. Offene Wartbarkeit (vorgeschlagene Reihenfolge, mit Verifikation)

| # | Tarea | Estado 10/10/2026 | Cómo verificar |
| --- | --- | --- | --- |
| 1 | Migrar routers a `get_or_404` y servicios a `paginate_filtered` | `get_or_404` en 13 routers (110 usos), 186 `404` inline restantes; `paginate_filtered` con 0 usos | `Select-String "get_or_404\(" backend/app/routers; Select-String "404" backend/app/routers; Select-String "paginate_filtered" backend/app/services` |
| 2 | Migrar `python-jose` → `PyJWT` (PR aislado con tests de expiración/tipo/rotación) | Sin migrar (`app/auth.py` usa `jose`) | `Select-String "from jose\|import jose" backend/app; Select-String "import jwt" backend/app` |
| 3 | Troceo de pantallas grandes | Hecho: `festival_profile` 956L, `locations` 680L, `api_service` 511L, `chat` 767L, `user_profile` 803L (widgets extraídos en `lib/widgets/`) | `(Get-Content frontend/lib/screens/<pantalla>).Count` |
| 4 | Migrar `AlertDialog` → `ConfirmDialog` y `ScaffoldMessenger` → `showAppSnack` | 24 `AlertDialog` vs 19 usos `showConfirmDialog`; 115 `ScaffoldMessenger` vs 8 usos `showAppSnack` (los `AlertDialog` restantes son formularios: requieren `CreateEntityDialog` común) | `Select-String "AlertDialog|showConfirmDialog|ScaffoldMessenger|showAppSnack" frontend/lib` |
| 5 | Higiene formato + `.gitignore` | `ruff format --check` + `ruff check` limpios y con gate en CI (GH + GitLab); `.gitignore` cubre `*.db*`, `*.hive`, `*.lock`, `uploads/` (no el glob `*.hive*`) | `ruff format --check .; ruff check .; Get-Content .gitignore` |
