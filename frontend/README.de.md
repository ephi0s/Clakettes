# Clakettes — Frontend

[ES](README.md) · [EN](README.en.md) · [FR](README.fr.md) · [DE](README.de.md) · [IT](README.it.md) · [CA](README.ca.md) · [EU](README.eu.md) · [GL](README.gl.md) · [OC](README.oc.md)

Flutter-Frontend (multiplattform) für die Filmfestival-Management-Plattform.

## Technologie-Stack

- **Framework**: Flutter (Material 3, color dinámico, modo oscuro)
- **Estado**: Singletons + `setState()` + Streams (NO Provider, NO flutter_it, NO riverpod)
- **Almacenamiento local**: Hive, SharedPreferences
- **i18n**: 9 idiomas (en, es, fr, de, it, ca, eu, gl, oc) — `AppLocalizations` manual (sin gen-l10n)
- **Accesibilidad**: widgets Semantics, soporte TalkBack/VoiceOver, WCAG 2.1 AA
- **Arquitectura**: Services / Managers / Views (Arquitectura Flutter Pragmática)

## Schnellstart

```bash
cd frontend
flutter pub get
flutter run -d web-server --web-port 3000
```

## Skripte

Consulta `../start.ps1` für die Launcher mit Flags `--dev`, `--final`, `--web`.

## Architektur

```
lib/
├── screens/           # UI-Bildschirme
│   ├── auth/          # Login
│   ├── festivals/     # Liste, Profil, Festival erstellen
│   ├── users/         # Profil, Verzeichnis, Benutzer erstellen, Rollen
│   ├── shortfilms/    # Liste, Profil, Kurzfilm erstellen
│   ├── chat/          # Chat, Kanäle, Kanal erstellen
│   ├── events/        # Event-Verwaltung und -Detail, Sitze/Buchungen
│   ├── awards/        # Palmarés
│   ├── notifications/ # Benachrichtigungszentrale
│   ├── locations/     # Karte, Standortdetail
│   ├── forms/         # Anmeldeformulare, Seiten-Editor, Antworten, öffentliche Formulare
│   ├── admin/         # Admin-Bereich
│   ├── committees/    # Komitees
│   └── settings/      # Backend-Konfiguration, Verzeichnismitglied, Dashboard
├── services/          # Dienste + api/ (Domänen) + chat_backend (Klassen)
│   ├── api_service.dart              # Fassade + Kern (Auth, Transport, Admin, Suche)
│   ├── api/                          # Methoden pro Domäne (part of api_service.dart)
│   │   ├── user_api.dart, festival_api.dart, channel_api.dart, form_api.dart
│   │   ├── calendar_api.dart, catalog_api.dart, org_api.dart
│   │   ├── event_api.dart, location_api.dart
│   ├── auth_service.dart             # JWT, Sitzungspersistenz
│   ├── backend_config.dart           # Backend-URL (gespeichert > dart-define > Plattform-Standard)
│   ├── channel_service.dart          # Chat-Kanäle + E2EE-Schlüssel
│   ├── connectivity_monitor.dart     # Online/Offline-Erkennung
│   ├── crypto_utils.dart             # E2EE (ECDH P-256, AES-GCM) + Kompression, mit async Isolates
│   ├── database_service.dart         # Hive-Initialisierung + Typadapter
│   ├── file_downloader.dart          # Nativer Download (web/io-bedingt)
│   ├── locale_service.dart           # Sprachpersistenz (SharedPreferences)
│   ├── notification_service.dart     # Erinnerungen: Plugin auf Desktop, Notification API im Web, No-op auf Mobil
│   ├── notification_platform.dart    # Bedingter web/stub-Export (ohne Firebase)
│   ├── offline_cache_service.dart    # Hive-Boxen (festivals, users, shortfilms, messages)
│   ├── sync_queue_service.dart       # Offline-Queue mit Retry + Backoff (max. 3 Versuche)
│   └── chat_backend/                 # Chat-WS + REST-Abstraktion
│       ├── abstract_chat_backend.dart
│       ├── chat_service.dart         # WS/REST/E2EE-Fassade
│       ├── rest_chat_backend.dart    # Historie/Sync via REST (in Tests als Fake genutzt)
│       └── websocket_chat_backend.dart  # Echtzeit via WebSocket
├── models/            # Dart-Modelle (manuelles fromJson/toJson + Hive-Codegen)
├── widgets/           # barrierefreie wiederverwendbare Widgets
│   ├── reusable_widgets.dart     # ProfileAvatar, InfoRow, StatusIndicator, ListItemCard, SemanticHeader, SemanticTextField + showAppSnack
│   ├── agenda_calendar_widget.dart
│   ├── chat_bubble.dart          # Nachrichtenblase + Rich Content
│   ├── chat_input_bar.dart       # Chat-Eingabeleiste
│   ├── confirm_dialog.dart       # Barrierefreier Bestätigungsdialog
│   ├── dav_subscription_section.dart
│   ├── emoji_picker.dart         # Emoji-Auswahl im Bottom Sheet
│   ├── empty_state_widget.dart   # Barrierefreier Leerzustand
│   ├── error_state_widget.dart   # Fehlerzustand mit Wiederholung
│   ├── event_visibility_picker.dart
│   ├── festival_sections.dart    # Festival-Regeln und -Standorte Abschnitte
│   ├── film_location_card.dart   # Drehort-Karte
│   ├── language_picker.dart
│   ├── list_item_animation.dart  # Zeilen-Eingangsanimation
│   ├── loading_skeleton.dart     # Lade-Skeleton (Shimmer)
│   ├── location_badge_chip.dart  # Standort-Chip
│   ├── location_cards.dart       # LocationCard, LegacyCard, LocationFormScreen
│   ├── location_selector.dart    # Standortauswahl
│   ├── location_tag_editor.dart  # Standort-Tag-Editor
│   ├── login_prompt_sheet.dart
│   ├── map_picker.dart           # Punktauswahl-Karte
│   ├── open_in_maps_action.dart
│   ├── seat_map_widget.dart      # Interaktiver Sitzplan
│   └── user_profile_cards.dart   # SessionsCard, AliasesCard
├── l10n/              # AppLocalizations + 9 ARB
├── main.dart          # Einstiegspunkt, Material-3-Theme, Reihenfolge der Dienst-Initialisierung
├── main_scaffold.dart # NavigationRail (>800px) / NavigationBar (<800px) + Drawer
└── auth_wrapper.dart  # Auth-Gate (Splash → Login / Home)
```

## Dienst-Initialisierungsreihenfolge (main.dart)

```dart
await DatabaseService.init();           // Hive-Boxen
await OfflineCacheService.init();       // Zwischengespeicherte Daten laden
await SyncQueueService.init();          // Ausstehende Mutationen
await ConnectivityMonitor.start();      // Netzwerküberwachung starten
await LocaleService.load();             // Gespeicherte Sprache laden
// Danach runApp()
```

## State-Management-Muster

**Singletons + setState + Streams** — Ohne Provider, ohne flutter_it, ohne Bloc.

- Die Dienste sind Singletons (lazy in `main.dart` initialisiert)
- Die UI nutzt `StatefulWidget` + `setState()` für lokalen State
- Die Dienste exponieren Streams für reaktive Updates (Konnektivität, Auth, Sync)
- `ChangeNotifier` wird punktuell genutzt (AuthService, LocaleService) für `Consumer`-Widgets

## API-Dienst

`ApiService` (Singleton) — Basis-URL via `--dart-define=BACKEND_URL=http://localhost:8000/api`

- Hängt das JWT automatisch an (aus AuthService)
- Automatisches Token-Refresh bei 401
- Integration mit der Offline-Queue (SyncQueueService)
- Methoden: `get`, `post`, `put`, `patch`, `delete`, `upload`

```dart
final api = ApiService();
final festivals = await api.get('/festivals/', query: {'page': '1', 'size': '20'});
```

## Offline-first-Architektur

1. **Hive-Boxen**: `festivals`, `users`, `shortfilms`, `messages` (+ Events, Preise usw. je Modell)
2. **Lesen**: die UI liest zuerst aus Hive und synchronisiert im Hintergrund aus der API
3. **Schreiben**: Mutationen werden in `SyncQueueService` eingereiht (HMAC-signiert)
4. **Sync**: bei wiederhergestellter Konnektivität spielt `SyncQueueService` die Queue sequenziell ab
5. **Konfliktlösung**: Server gewinnt (Last-Write-Wins mit Timestamp)
6. **Herkunft**: der Hive-Cache speichert die Herkunft jedes Knotens (`putWithOrigin`, `getOrigin`, `reconcile`, `clearOrigin`); nicht antwortende Knoten meldet `DegradedNodesBanner` mit Zähler und Neuladen-Schaltfläche

## Internationalisierung (i18n)

- **9 Locales**: en, es, fr, de, it, ca, eu, gl, oc (823 Schlüssel pro ARB, Parität geprüft mit `test/l10n/arb_parity_test.dart`)
- **Manuelle Implementierung**: `lib/l10n/app_localizations.dart` (ohne gen-l10n)
- **ARB-Dateien**: `assets/l10n/app_<locale>.arb`
- **Auto-Erkennung**: `LocaleService` liest die Systemsprache, mit Fallback auf `en`
- **Delegate**: `AppLocalizations.of(context)` (manueller Delegate, ohne gen-l10n)

### Übersetzungen hinzufügen

1. Füge den Key zu `assets/l10n/app_en.arb` hinzu
2. Repliziere ihn in die anderen 8 `.arb`
3. Nutze ihn in Dart: `AppLocalizations.of(context)!.yourKey`

### Verschachtelte Keys (Rollen, Validierung)

```json
"roles": { "admin": "Administrador", "organizer": "Organizador" }
```
```dart
AppLocalizations.of(context)!.roles['admin']
```

## Barrierefreiheit (WCAG 2.1 AA)

| Muster | Verwendung |
|---------|-------|
| `Semantics` | Instanzen für Screenreader |
| `SemanticHeader` | Abschnittsüberschriften (`header: true`) |
| `SemanticTextField` | Formularfelder mit Validierungssemantik |
| `ExcludeSemantics` | dekorative Icons |
| `Tooltip` | interaktive Elemente |
| `SnackBarBehavior.floating` | snackbars |
| `autovalidateMode: onUserInteraction` | Formulare |
| `TextInputAction.next/done` + `onSubmitted` | Tastaturnavigation |

### Wiederverwendbare barrierefreie Widgets

```dart
// lib/widgets/reusable_widgets.dart
ProfileAvatar(avatarUrl, name, radius: 24)
InfoRow(label: 'Email', value: email, icon: Icons.email)
StatusIndicator(isActive: true, label: 'Activo')
ListItemCard(title: 'Festival', subtitle: 'Madrid', onTap: () {})
SemanticHeader('Festivales', level: 1)
SemanticTextField(label: 'Email', validator: emailValidator)
```

## Responsive Navigation

- **>800px Breite**: `NavigationRail` (Seitenleiste)
- **≤800px Breite**: `NavigationBar` (untere Leiste)
- Implementiert in `MainScaffold` mit `LayoutBuilder` + Drawer in allen Größen

## Theme (Material 3)

- **Seed-Farbe**: `#B8956E` (goldener Sand)
- **Dark Mode**: volle Unterstützung via `_baseTheme(ColorScheme)`
- **18+ Komponententhemes**: Card, AppBar, NavigationBar/Rail, InputDecoration, FilledButton, ElevatedButton, TextButton, SnackBar, Dialog, BottomSheet, Chip, ListTile, Drawer, PopupMenu, Scrollbar, Slider, Divider, FAB
- **Cupertino-Seitenübergänge** auf iOS/macOS

## Chat (E2EE)

- **Duales Backend**: WebSocket (Echtzeit) + REST (Historie/Sync)
- **E2EE**: X25519-Schlüsselaustausch (pointycastle), Nachrichtenverschlüsselung AES-GCM
- **Schlüsselspeicherung**: Modell `UserKey` (öffentlicher Schlüssel im Backend, privater in Hive)
- **Dienst**: `ChatService` abstrahiert WS/REST/E2EE

## Karten und Lokalisierung

- `flutter_map` + `latlong2` + `geolocator`
- OpenStreetMap-Kacheln (cancelbarer Kachelprovider)
- `url_launcher` für native Kartenapps (Google Maps, Apple Maps, Maps.me)

## Build

```bash
# Web
flutter build web --dart-define=BACKEND_URL=https://api.clakettes.com/api

# Desktop
flutter build windows
flutter build linux
flutter build macos

# Mobil
flutter build apk        # APK Android
flutter build appbundle  # AAB Android (Play Store)
flutter build ios        # iOS (benötigt macOS + Xcode)
```

## Schlüsselabhängigkeiten

| Paket | Zweck |
|---------|-----------|
| `http` | REST-API-Client |
| `hive_flutter` | Offline-Cache |
| `shared_preferences` | Persistenz von Locale und Auth-Token |
| `connectivity_plus` | Netzwerkerkennung |
| `web_socket_channel` | Echtzeit-Chat |
| `pointycastle` | E2EE X25519/AES-GCM |
| `flutter_map` + `latlong2` | Karten |
| `geolocator` | GPS |
| `flutter_local_notifications` | Lokale Benachrichtigungen |
| `url_launcher` | Externe Links (Karten, Web) |
| `uuid` | Client-seitige IDs |

## Codegenerierung (Hive)

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

Generiert `*_adapter.dart` für die mit `@HiveType` annotierten Modelle.

## Testing

```bash
# Unit- + Widget-Tests
flutter test

# Integrationstests (benötigt Gerät/Emulator)
flutter test integration_test/
```

## Linting

```bash
flutter analyze
```

Nutzt `flutter_lints` (empfohlenes Set).

## Verzeichnisstruktur (erweitert)

```
frontend/
├── android/                 # Config Android
├── ios/                     # Config iOS
├── linux/                   # Config Linux
├── macos/                   # Config macOS
├── windows/                 # Config Windows
├── web/                     # Config web (index.html, manifest.json)
├── assets/
│   ├── l10n/                # 9 ARB-Dateien
│   └── images/              # Logos, placeholders
├── lib/
│   ├── l10n/                # app_localizations.dart (manual)
│   ├── models/              # Dart-Modelle (Hive + Codegen)
│   ├── screens/             # Bildschirme
│   ├── widgets/             # wiederverwendbare Widgets
│   ├── services/            # Dienste + api/ + chat_backend
│   ├── main.dart
│   ├── main_scaffold.dart
│   └── auth_wrapper.dart
├── test/                    # Tests Flutter
├── docker/                  # Dockerfile, build.ps1, nginx.conf
├── pubspec.yaml
└── README.md
```

## Docker (Frontend)

```powershell
cd frontend/docker
.\build.ps1 -Target all      # Alle Plattformen
.\build.ps1 -Target web      # Nur Web
```

Multi-Stage-Dockerfile:
- **dev**: `flutter run -d web-server --web-port 3000`
- **prod**: `flutter build web` → statisch serviert mit nginx

## Umgebungsvariablen

| Variable | Beschreibung | Standard |
|----------|-------------|---------|
| `BACKEND_URL` | API-Basis-URL (via `--dart-define`) | `http://localhost:8000/api` |
| `CHROME_EXECUTABLE` | Browser für `flutter run -d chrome` | Automatisch erkannt (Brave/Chrome) |

## Fehlerbehebung

| Problem | Lösung |
|----------|----------|
| `flutter pub get` schlägt fehl | `.dart_tool`, `pubspec.lock` löschen und erneut versuchen |
| Hive-Typkonflikte | `flutter pub run build_runner build --delete-conflicting-outputs` |
| WebSocket-Verbindungsfehler | Prüfe `BACKEND_URL`; stelle sicher, dass das Backend `/ws/chat` bereitstellt |
| Sprache bleibt nicht erhalten | `SharedPreferences` löschen, `LocaleService.load()` prüfen |
| Dark Mode wird nicht angewendet | Explizites `ThemeMode.system` oder `ThemeMode.dark` in `MaterialApp` sicherstellen |

## Beitragen

1. Folge den bestehenden Mustern (Singletons, `setState`, Streams)
2. Füge `Semantics` zu neuen interaktiven Widgets hinzu
3. Füge Übersetzungen zu den 9 ARB-Dateien hinzu
4. Führe `flutter analyze` und `flutter test` vor dem PR aus
5. Konventionelle Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`

## Lizenz

MIT — Siehe [LICENSE](../LICENSE) im Root.
