# Code-Audit — Clakettes (Rev. 10/10/2026, Multiplattform-Erweiterung 09/10/2026)

[ES](../es/AUDITORIA.md) · [EN](../en/AUDITORIA.md) · [FR](../fr/AUDITORIA.md) · [DE](AUDITORIA.md) · [IT](../it/AUDITORIA.md) · [CA](../ca/AUDITORIA.md) · [EU](../eu/AUDITORIA.md) · [GL](../gl/AUDITORIA.md) · [OC](../oc/AUDITORIA.md)

## 0. Zusammenfassung

Überprüfung der Abhängigkeiten, angewandten Optimierungen und ausstehenden technischen Schulden des Clakettes-Projekts.

## 1. Externe Abhängigkeiten: was entfernt werden kann und was nicht

### Backend (`backend/requirements.txt` + `pyproject.toml`)

| Dep | Urteil | Grund |
|-----|--------|-------|
| fastapi, uvicorn[standard], sqlalchemy, pydantic(+settings), alembic | Behalten | Kerne des Stacks |
| PyJWT==2.15.1 | Migration abgeschlossen | `python-jose` entfernt; `app/auth.py` und `routers/dependencies.py` nutzen PyJWT (Bump 2.10.1 → 2.15.0 → 2.15.1) |
| python-dotenv | Nicht enthalten | Steht nicht in `pyproject.toml`/`requirements*.txt` und wird nicht in `backend/` importiert; `pydantic-settings` lädt `.env` direkt |
| pymysql | Behalten als Prod-Treiber | Wird nur mit MariaDB verwendet; nicht laden in Dev spart nichts (lazy Import bereits in SQLAlchemy) |
| python-multipart, email-validator, bcrypt | Behalten | Uploads, E-Mail-Validierung, Passwort-Hashing |
| reportlab 5.1.0 | Behalten, aber mit Lazy-Import (erledigt) | Nur `export_service._build_pdf`; zuvor auf Modulebene importiert (~200 ms + Speicher pro Worker). Jetzt innerhalb der Funktion importiert. Zudem `pyproject.toml` synchronisiert (fehlte) und `==5.1.0` gepinnt |

**In `backend/pyproject.toml` / `requirements*.txt` fixierte Versionen:** `fastapi==0.163.1`, `uvicorn[standard]==0.54.0`, `sqlalchemy==2.1.9`, `pydantic==2.14.3`, `pydantic-settings==2.16.3`, `email-validator==2.4.0`, `pymysql==1.2.4`, `python-multipart==0.0.34`, `PyJWT==2.15.1`, `cryptography==50.0.2`, `bcrypt>=4.3.0`, `alembic==1.20.1`, `reportlab==5.1.0`, `Pillow==13.0.0`, `mutagen==1.48.1`, `pypdf==7.1.0` (Major seit 6.21.x); Entwicklung: `pytest>=9.2.0`, `ruff==0.17.5`, `httpx==0.28.1`, `caldav==3.7.0`, `icalendar==7.3.0`.

### Frontend (`frontend/pubspec.yaml`)

Alle Abhängigkeiten sind in echtem Einsatz; keine konnte ohne Funktionsverlust entfernt werden:

- `archive`: verwendet in `crypto_utils.dart` (ZLib/GZip). `dart:io` taugt nicht, weil es Web bricht.
- `path_provider`: verwendet in `file_downloader_io.dart` (Mobil/Desktop).
- `web`: verwendet in `file_downloader_web.dart`.
- `pointycastle` + `crypto`: E2EE des Chats (ECDH P-256 + AES-GCM; der Name `X25519` erscheint nur in einem vererbten Feld).
- `flutter_map` + `latlong2` + `geolocator` + `url_launcher`: Karten.
- `table_calendar`, `flutter_local_notifications` + `timezone` + `flutter_timezone`, `image_picker` + `file_picker`: jedes mit 1-2 Verwendungen, aber Entfernen würde Funktionalität entfernen.

## 2. Angewandte Optimierungen

1. `export_service.py`: Lazy-reportlab-Import in `_build_pdf` + Docstring.
2. `main.py` RateLimitMiddleware + `routers/admin.py` + `routers/auth.py` + `routers/auth_sessions.py` + `routers/federation.py`: 5 `RateLimiter`-Instanzen (Eimer `middleware:`/`dav:` + Limiter für `reset` 3/300 s, `login` 5/300 s, `refresh` 20/60 s und Föderation 60/60 s); nicht vereinheitlichen ohne unterschiedliche Limits zu verlieren. Der Bypass läuft über `app.config.is_testing()` (`1/true/yes/on`).
3. `base_service.py`: `paginate` setzt `page>=1`, `size` in `[1,100]`; neues `paginate_filtered()` mit 0 Nutzungen definiert (ausstehende Migration der geklonten `get_all_paginated`).
4. `routers/dependencies.py`: `get_current_user_optional` nutzt wieder `validate_access_token` (entfernt ~30 duplizierte JWT+Session-Zeilen); Fix `__import__("datetime")` → normaler Import; neuer `get_or_404()` zur Ersetzung von ~100 inline `HTTPException(404)`.
5. `dav/auth.py`: Beziehung zu `app.auth.hash_token` dokumentiert (früher `_hash_token`; der Alias bleibt aus Kompatibilitätsgründen erhalten).
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
12. `get_or_404` erweitert auf `committees.py` (10), `events.py` (58, via Skript mit Überprüfung + 17 unzuweiset zur Vermeidung von F841), `delegations` (2) und 5 Standort-Router (12). Dieses Paket brachte keine Migration; spätere Revisionen fügten jedoch `a8b9c0d1e2f3` (Sitzplatz-Eindeutigkeit) und `b9c0d1e2f3a4` (`contest_type` in Kurzfilmen) hinzu, beide bereits im Head `b9c0d1e2f3a4` angewendet.
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
24. Dokumentation: `docs/de/API.md`, `docs/de/ARQUITECTURA.md`, `docs/de/USO.md`, `docs/de/DESARROLLO.md`, `docs/de/SEGURIDAD.md`, `docs/de/BACKEND.md` + `docs/de/DATABASE.md` (verschoben von `backend/` am 10/10/2026). READMEs und `AGENTS.md` mit realen Zahlen; Dev-Admin `admin`/`setup` (kein `ADMIN_PASSWORD` in `backend/.env.example`; Seed nur Nicht-Produktion in `app/main.py:257`).
