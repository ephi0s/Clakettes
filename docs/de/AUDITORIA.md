# Code-Audit — Clakettes (Rev. 10/10/2026, Multiplattform-Erweiterung 09/10/2026)

[ES](../es/AUDITORIA.md) · [EN](../en/AUDITORIA.md) · [FR](../fr/AUDITORIA.md) · [DE](AUDITORIA.md) · [IT](../it/AUDITORIA.md) · [CA](../ca/AUDITORIA.md) · [EU](../eu/AUDITORIA.md) · [GL](../gl/AUDITORIA.md) · [OC](../oc/AUDITORIA.md)

> **Addendum 11/10/2026** (verifizierte Zahlen): Backend 1439 `def test_` in 47 Dateien; Router 40 Dateien (38 mit `APIRouter`); Dienste 43; Modelle 40; Schemas 37; Alembic 36 Versionen; `docs/de/API.md` 339 Endpunkte in 38 Routern (einzigartige operationIds). DSGVO: Datenschutz nach Voreinstellung, Einwilligung, Löschung/Export, Sitzungsbereinigung, append-only Audit, Metadatenbereinigung, TLS MariaDB in Produktion, DAV-Ablauf, CSP/HSTS. Zahlungsanbieter Mock/Stripe/Redsys.

## 0. Executive Summary (10/10/2026, verifizierte Zahlen)

| Bereich | Status | Detail |
|---------|--------|--------|
| Backend-Tests | 1439 `def test_` in 47 Dateien | `Get-ChildItem backend/tests -Recurse -Filter "test_*.py" \| Select-String "def test_"` |
| Frontend-Tests | 75 Dateien `*_test.dart` | `Get-ChildItem frontend/test -Recurse -Filter "*_test.dart"` |
| Router/Dienste/Modelle/Schemas | 40/43/40/37 Dateien (38 Router mit `APIRouter`) | `dependencies.py`/`permissions.py` sind Helfer ohne Router; `base.py`/`__init__.py` sind keine Entitäten |
| Migrationen | 36 Versionen | `alembic/versions/` |
| Endpunkte | 339 in 38 Routern (`docs/de/API.md` via AST) | `python tools/gen_api.py` idempotent; einfacher Grep gibt ~290 (zählt `propfind/report/options/websocket` nicht) |
| Lint | `ruff check` + `ruff format --Check` sauber | `AGENTS.md` und CI (GH + GitLab) mit Format-Tor |
| Docs | Backend konsolidiert in `docs/` | `docs/de/BACKEND.md` + `docs/de/DATABASE.md`; Index in `docs/de/README.md` |
| Hauptschulden | `get_or_404` teilweise, `paginate_filtered` ohne Nutzung, `python-jose` nicht migriert, 24 `AlertDialog` / 115 `ScaffoldMessenger` verbleibend | Siehe §5 mit Zählungen und Verifizierung |

Wie man erneut verifiziert: `cd backend; python -m ruff check .; python -m pytest tests/ -x -q --tb=short` und `cd frontend; flutter analyze; flutter test`.

## 1. Externe Abhängigkeiten: was entfernt werden kann und was nicht

### Backend (`backend/requirements.txt` + `pyproject.toml`)

| Dep | Urteil | Grund |
|-----|--------|-------|
| fastapi, uvicorn[standard], sqlalchemy, pydantic(+settings), alembic | Behalten | Kerne des Stacks |
| python-jose[cryptography] | Für jetzt behalten, zu PyJWT migrieren in Zukunft | Verlassen seit 2016, aber die Änderung betrifft `app/auth.py` + `routers/dependencies.py` + Tests; in separater PR mit Token-Tests durchführen |
| python-dotenv | Behalten | Erforderlich durch `pydantic-settings>=2` und `uvicorn[standard]` (`--env-file`); nur 2 Skripte importieren es direkt, aber Entfernen würde `.env`-Laden brechen |
| pymysql | Behalten als Prod-Treiber | Wird nur mit MariaDB verwendet; nicht laden in Dev spart nichts (lazy Import bereits in SQLAlchemy) |
| python-multipart, email-validator, bcrypt | Behalten | Uploads, E-Mail-Validierung, Passwort-Hashing |
| reportlab 5.1.0 | Behalten, aber mit Lazy-Import (erledigt) | Nur `export_service._build_pdf`; zuvor auf Modulebene importiert (~200 ms + Speicher pro Worker). Jetzt innerhalb der Funktion importiert. Zudem `pyproject.toml` synchronisiert (fehlte) und `==5.1.0` gepinnt |

### Frontend (`frontend/pubspec.yaml`)

Alle Abhängigkeiten sind in echtem Einsatz; keine konnte ohne Funktionsverlust entfernt werden:

- `archive`: verwendet in `crypto_utils.dart` (ZLib/GZip). `dart:io` taugt nicht, weil es Web bricht.
- `path_provider`: verwendet in `file_downloader_io.dart` (Mobil/Desktop).
- `web`: verwendet in `file_downloader_web.dart`.
- `pointycastle` + `crypto` + `uuid`: E2EE des Chats (X25519/ECDH P-256 + AES-GCM).
- `flutter_map` + `cancellable_tile` + `latlong2` + `geolocator` + `url_launcher`: Karten.
- `table_calendar`, `flutter_local_notifications` + `timezone` + `flutter_timezone`, `image_picker` + `file_picker`: jedes mit 1-2 Verwendungen, aber Entfernen würde Funktionalität entfernen.

## 2. Angewandte Optimierungen

1. `export_service.py`: Lazy-reportlab-Import in `_build_pdf` + Docstring.
2. `main.py` RateLimitMiddleware + `routers/admin.py` + `routers/auth.py`: 3 `RateLimiter`-Instanzen (Eimer `middleware:`/`dav:` + Limiter für `reset` 3/300s und `login`); nicht vereinheitlichen ohne unterschiedliche Limits zu verlieren.
3. `base_service.py`: `paginate` setzt `page>=1`, `size` in `[1,100]`; neues `paginate_filtered()` mit 0 Nutzungen definiert (ausstehende Migration der geklonten `get_all_paginated`).
4. `routers/dependencies.py`: `get_current_user_optional` nutzt wieder `validate_access_token` (entfernt ~30 duplizierte JWT+Session-Zeilen); Fix `__import__("datetime")` → normaler Import; neuer `get_or_404()` zur Ersetzung von ~100 inline `HTTPException(404)`.
5. `dav/auth.py`: Beziehung zu `app.auth._hash_token` dokumentiert.
6. `pyproject.toml`/`requirements.txt` synchronisiert (reportlab).
7. `reusable_widgets.dart`: neues `showAppSnack()` (1 Definition + 8 Nutzungen; 115 `ScaffoldMessenger` direkt verbleiben).

## 3. Angewandte Multiplattform-Verbesserungen (Desktop + Web + Android + iOS/iPad)

1. `BackendConfig`: Plattform-Standard — Android-Emulator nutzt `10.0.2.2:8000` (Emulator-Localhost ist der virtuelle selbst, nicht der Host); Rest `localhost:8000`. Priorität: gespeicherte URL > `--dart-define=BACKEND_URL` > Plattform-Standard. `ApiService` nutzt denselben Standard im Konstruktor und in Gettern.
2. `NotificationService`: auf Web (`kIsWeb`) berührt `init` kein Plugin oder Zeitzone (keine lokalen Benachrichtigungen im Browser) und `scheduleReminder` tut nichts; in Docstring dokumentiert. Keine Plattformzweige auf den Bildschirmen.
3. `file_downloader.dart`: bedingter Import verifiziert (`web` standardmäßig, `io` wenn `dart.library.io`) — deckt Browser, Desktop, Android und iOS ohne Änderungen ab.
4. `main_scaffold.dart`: Kurzfilme zur Navigation hinzugefügt (Bildschirm `screenIndex 3` existierte aber ohne Eintrag — unzugänglich). Rail >800px (Desktop/Web), Bar <800px (Mobil), Drawer auf allen.
5. `AndroidManifest.xml`: INTERNET, ACCESS_NETWORK_STATE, Standort (FINE+COARSE), CAMERA, READ_MEDIA_IMAGES/VIDEO, SCHEDULE/USE_EXACT_ALARM hinzugefügt. Ohne explizites INTERNET haben Release-Builds kein Netzwerk.
6. `ios/Runner/Info.plist`: NSLocationWhenInUse, NSCamera, NSPhotoLibrary (+Add) hinzugefügt. Ohne diese verweigert das System oder der App Store lehnt ab.
7. Backend `routers/festivals.py`: Pilot `get_or_404(db, Festival/Location, ...)` — 9 `if not → 404`-Blöcke entfernt; erweitert auf `shortfilms.py` (3) und `users.py` (4). Muster zum Erweitern auf den Rest der Router.
8. Frontend `awards_screen.dart`: Fehler-SnackBar auf `showAppSnack()` migriert (Pilot). Hinweis: Die 24 verbleibenden `AlertDialog`s sind *Formular*-Dialogs (erstellen/bearbeiten), keine Bestätigungsdialogs — sie migrieren nicht zu `showConfirmDialog` (19 Nutzungen in 18 Bildschirmen); erfordern einen gemeinsamen `CreateEntityDialog`.
9. CI: Tor `ruff format --check` hinzugefügt (GH + GitLab) nach Verifizierung von `216 files already formatted`.
10. Sicherheit (Pilot `channels.py`, Sicherheitsblock): Neues `require_channel_member`/`is_channel_member` in `permissions.py` und Nutzung in `channels.py` + `chat.py` (entfernt 3 inline-Blöcke mit verzögerten Imports); `channels.py` auf `get_or_404` migriert (7 Blöcke weniger); Rollen-Whitelist `Literal[admin,moderator,member]` in Schemas (zuvor: freie String → 500 durch CheckConstraint; jetzt: 422); 4 neue 403/422-Tests in `TestChannelAuthorization`.
11. Sicherheit: `POST /delegations/{id}/revoke` erforderte nur Auth — jeder konnte fremde Delegationen widerrufen. Jetzt prüft Delegierender oder Admin + 403-Test. Verifiziert OK (ohne Änderungen): `user_roles`/`user_festival` (attendee-Whitelist), DMs (Eigentum), öffentliche Formulare (optionale Auth), WS (validiert Sitzung), `bulk_create` (ein Commit), SyncQueue (Retry+Backoff), i18n (0 fehlende Schlüssel), `locations` (didChangeDependencies mit Guard).
12. `get_or_404` erweitert auf `committees.py` (10), `events.py` (58, via Skript mit Überprüfung + 17 unzuweiset zur Vermeidung von F841), `delegations` (2) und 5 Standort-Router (12). Keine Schemaänderung: keine Alembic-Migration ausstehend für dieses Paket.
13. Leistung: `venue`-Filter der Programmierung auf SQL heruntergezogen (zuvor gefilterte die Seite in Python und brach `total`/`pages`).
14. Frontend: Anti-Doppel-Send-Guards beim Erstellen von Festival/Nutzer/Kurzfilm + 3 SnackBars auf `showAppSnack` migriert.
15. Chat: E2EE außerhalb des UI-Threads — `_prepareContent`/`_unpackContent` nutzen `encryptAsync`/`decryptAsync` (Isolates); neue `encryptSenderKeyAsync`/`decryptSenderKeyAsync` verwendet in Sender-Key-Verbreitung und -Empfang. `RestChatBackend` wird beibehalten: wird von `chat_service_test` als Fake verwendet (war kein toter Code).
16. Chat: `chat_screen.dart` 1038 → 709 Zeilen; Blasen nach `widgets/chat_bubble.dart` (`ChatBubble` + `ChatBubbleWidget` mit Bild, Standort, vCard, iCal) und Leiste nach `widgets/chat_input_bar.dart` (`ChatInputBar`). 2 neue Async-Tests in `crypto_utils_test`.
17. `locations_screen` 1144 → 645 Zeilen: Karten und Formular nach `widgets/location_cards.dart` (`LocationCard`, `LegacyCard`, `LegacyLocation`, `LocationFormScreen`, `LocationFormResult`); Löschung mit `showConfirmDialog` + `showAppSnack` (ein `AlertDialog` weniger).
18. `festival_profile_screen` 1276 → 1173 Zeilen: `RulebooksSection` und `FestivalLocationsSection` (+ Karte und Karten) nach `widgets/festival_sections.dart`. Der Bildschirm behält Zustand, Lesen, Bearbeiten und Callbacks bei.
19. `api_service.dart` 1134 → 464 Zeilen: 95 Methoden nach `lib/services/api/` verschoben (`event_api` 31, `location_api` 25, `org_api` 17, `catalog_api` 13, Rest nach `user_api` + `calendar/channel/festival/form`). Der Kern behält Konfiguration, Auth, Transport und Admin/Suche bei. Öffentliche API intakt.
20. `user_profile_screen` 996 → 1391 Zeilen: `SessionsCard` und `AliasesCard` nach `widgets/user_profile_cards.dart`. 4 `if` ohne geschweifte Klammern korrigiert, geerbt in `catalog_api`.
21. Flow-Tests (`tests/integration/test_flows.py`): vollständige Reservierung (Festival → Event → Sitze → Reservierung → Belegung), Messaging (Kanal → Mitglied → DM → Lesen → Löschen) und Delegation (erstellen → auflisten → widerrufen).
22. Widget-Tests der extrahierten Widgets (13): `chat_bubble`, `chat_input_bar`, `user_profile_cards`, `location_cards`. Hinweis: Widgets unter `wrapWithLocalization` benötigen ein zusätzliches `pump()` (der Localization-Builder löst im zweiten Frame auf).
23. Nativer Push ohne Firebase (`docs/de/PUSH.md`): Browser-Notification-API auf Web (`notification_web.dart` + Stub mit bedingtem Export, keine neuen Deps), `flutter_local_notifications` auf Desktop + macOS-Berechtigung beim Start, Mobil als expliziter No-op (`_supported`). `flutter build web` verifiziert.
24. Dokumentation: `docs/de/API.md` (339 Endpunkte in 38 Routern, generiert durch AST mit `tools/gen_api.py` — regenerierbar), `docs/de/ARQUITECTURA.md` (Ebenen, Flows, Multiplattform-Entscheidungen), `docs/de/USO.md` (Start, Umgebung, Betrieb, Rollen), `docs/de/DESARROLLO.md` (Konventionen + CI-Tore), `docs/de/SEGURIDAD.md` (Tokens, Berechtigungsmatrix, Produktions-Checkliste), `docs/de/BACKEND.md` + `docs/de/DATABASE.md` (verschoben von `backend/` am 10/10/2026). READMEs und `AGENTS.md` mit realen Zahlen; Dev-Admin `admin`/`setup` (kein `ADMIN_PASSWORD` in `backend/.env.example`; Seed nur Nicht-Produktion in `app/main.py:257`).
Status: 1439 Backend-Tests (47 Dateien) + 75 Frontend (75 Dateien) grün, ruff + analyze sauber.

## 4. Überarbeitung 10/10/2026 (Korrekturen an §2–§3)

1. Backend-Docs konsolidiert: `backend/BACKEND.md` + `backend/DATABASE.md` → `docs/de/BACKEND.md` + `docs/de/DATABASE.md`; Links aktualisiert in `README.de.md`, `AGENTS.md`, `docs/de/README.md`, `ARQUITECTURA.md`, `USO.md`, `ADMINISTRACION.md`.
2. Reale Zählung: Router 40 Dateien (38 mit `APIRouter`; `permissions.py`/`dependencies.py` sind Helfer), Dienste 43 Module (+`__init__`), Modelle 40 Entitäten (+`base.py`+`__init__`), Schemas 37, Alembic 36, `API.md` 339 Endpunkte/38 Router (AST zählt `propfind/report/options/websocket`; einfacher Grep gibt ~290).
3. Tests: Backend 1439 `def test_` in 47 Dateien; Frontend 75 `*_test.dart`-Blöcke. Widgets 32 OK. Bildschirme: `festival_profile` 1173L, `locations` 645L, `chat` 709L, `api_service` 464L, `user_profile` 1391L.
4. Korrekturen zu §2: `RateLimiter` sind 3 Instanzen (`main.py`, `admin.py`, `auth.py`), nicht 1; `ADMIN_PASSWORD` existiert nicht in `backend/.env.example` (nur Kommentar `admin/setup`); `ruff format` umfasst 216 Dateien (nicht 215).
5. `tools/gen_api.py` regeneriert `API.md` idempotent, aber mit fest verdrahtetem absoluten Pfad und ohne Shebang (nicht portabel).

## 5. Ausstehende Wartbarkeit (vorgeschlagene Reihenfolge, mit Verifizierung)

| # | Aufgabe | Status 10/10/2026 | Wie verifizieren |
|---|---------|-------------------|------------------|
| 1 | Router auf `get_or_404` und Dienste auf `paginate_filtered` migrieren | `get_or_404` in 13 Routern (110 Nutzungen), 186 inline-`404` verbleibend; `paginate_filtered` mit 0 Nutzungen | `Select-String "get_or_404\(" backend/app/routers; Select-String "404" backend/app/routers; Select-String "paginate_filtered" backend/app/services` |
| 2 | `python-jose` → `PyJWT` migrieren (isolierte PR mit Ablauf/Typ/Rotation-Tests) | Nicht migriert (`app/auth.py` nutzt `jose`) | `Select-String "from jose\|import jose" backend/app; Select-String "import jwt" backend/app` |
| 3 | Große Bildschirme zerkleinern | Erledigt: `festival_profile` 1173L, `locations` 645L, `api_service` 464L, `chat` 709L, `user_profile` 1391L (Widget-Extraktionen in `lib/widgets/`) | `(Get-Content frontend/lib/screens/<Bildschirm>).Count` |
| 4 | `AlertDialog` → `ConfirmDialog` und `ScaffoldMessenger` → `showAppSnack` migrieren | 24 `AlertDialog` vs 19 `showConfirmDialog`-Nutzungen; 115 `ScaffoldMessenger` vs 8 `showAppSnack`-Nutzungen (verbleibende `AlertDialog`s sind Formulare: erfordern gemeinsamen `CreateEntityDialog`) | `Select-String "AlertDialog|showConfirmDialog|ScaffoldMessenger|showAppSnack" frontend/lib` |
| 5 | Format-Hygiene + `.gitignore` | `ruff format --Check` + `ruff check` sauber und mit Tor in CI (GH + GitLab); `.gitignore` deckt `*.db*`, `*.hive`, `*.lock`, `uploads/` ab (nicht das Glob `*.hive*`) | `ruff format --check .; ruff check .; Get-Content .gitignore` |