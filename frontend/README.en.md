# Clakettes — Frontend

[ES](README.md) · [EN](README.en.md) · [FR](README.fr.md) · [DE](README.de.md) · [IT](README.it.md) · [CA](README.ca.md) · [EU](README.eu.md) · [GL](README.gl.md) · [OC](README.oc.md)

Multi-platform Flutter frontend for the film festival management platform.

## Tech stack

- **Framework**: Flutter (Material 3, dynamic color, dark mode)
- **State**: Singletons + `setState()` + Streams (NO Provider, NO flutter_it, NO riverpod)
- **Local storage**: Hive, SharedPreferences
- **i18n**: the languages in `assets/l10n/` (en, es, fr, de, it, ca, eu, gl, oc) — manual `AppLocalizations` (no gen-l10n)
- **Accessibility**: Semantics widgets, TalkBack/VoiceOver support, WCAG 2.1 AA
- **Architecture**: Services / Managers / Views (Pragmatic Flutter Architecture)

## Quick start

```bash
cd frontend
flutter pub get
flutter run -d web-server --web-port 3000
```

## Scripts

See `../start.ps1` for launchers with `--dev`, `--final`, `--web` flags.

## Architecture

```
lib/
├── screens/           # UI screens
│   ├── auth/          # Login
│   ├── festivals/     # List, profile, create festival
│   ├── users/         # Profile, directory, create user, roles
│   ├── shortfilms/    # List, profile, upload short film
│   ├── chat/          # Chat, channels, create channel
│   ├── events/        # Event management and detail, seats/bookings
│   ├── awards/        # Palmarés
│   ├── notifications/ # Notification center
│   ├── locations/     # Map, location detail
│   ├── forms/         # Registration forms, page editor, responses, public forms
│   ├── admin/         # Admin panel
│   ├── committees/    # Committees
│   └── settings/      # Backend config, directory member, dashboard
├── services/          # services + api/ + chat_backend
│   ├── api_service.dart              # Facade + core (auth, transport, admin, search)
│   ├── api/                          # Domain methods (part of api_service.dart)
│   │   ├── user_api.dart, festival_api.dart, channel_api.dart, form_api.dart
│   │   ├── calendar_api.dart, catalog_api.dart, org_api.dart
│   │   ├── event_api.dart, location_api.dart
│   ├── auth_service.dart             # JWT, session persistence
│   ├── backend_config.dart           # Backend URL (saved > dart-define > platform default)
│   ├── channel_service.dart          # Chat channels + E2EE keys
│   ├── connectivity_monitor.dart     # Online/offline detection
│   ├── crypto_utils.dart             # E2EE (ECDH P-256, AES-GCM) + compression, with async isolates
│   ├── database_service.dart         # Hive init + type adapters
│   ├── file_downloader.dart          # Native download (web/io conditional)
│   ├── locale_service.dart           # Locale persistence (SharedPreferences)
│   ├── notification_service.dart     # Reminders: plugin on desktop, Notification API on web, no-op on mobile
│   ├── notification_platform.dart    # Conditional web/stub export (no Firebase)
│   ├── offline_cache_service.dart    # Hive boxes (festivals, users, shortfilms, messages)
│   ├── sync_queue_service.dart       # Offline queue with retry + backoff (max 3 attempts)
│   └── chat_backend/                 # Chat WS + REST abstraction
│       ├── abstract_chat_backend.dart
│       ├── chat_service.dart         # WS/REST/E2EE facade
│       ├── rest_chat_backend.dart    # History/sync via REST (used as a fake in tests)
│       └── websocket_chat_backend.dart  # Realtime via WebSocket
├── models/            # Dart models (manual fromJson/toJson + Hive codegen)
├── widgets/           # accessible reusable widgets
│   ├── reusable_widgets.dart     # ProfileAvatar, InfoRow, StatusIndicator, ListItemCard, SemanticHeader, SemanticTextField + showAppSnack
│   ├── agenda_calendar_widget.dart
│   ├── chat_bubble.dart          # Message bubble + rich content
│   ├── chat_input_bar.dart       # Chat input bar
│   ├── confirm_dialog.dart       # Accessible confirmation dialog
│   ├── dav_subscription_section.dart
│   ├── emoji_picker.dart         # Emoji picker in bottom sheet
│   ├── empty_state_widget.dart   # Accessible empty state
│   ├── error_state_widget.dart   # Error state with retry
│   ├── event_visibility_picker.dart
│   ├── festival_sections.dart    # Festival rules and locations sections
│   ├── film_location_card.dart   # Shooting location card
│   ├── language_picker.dart
│   ├── list_item_animation.dart  # Row entrance animation
│   ├── loading_skeleton.dart     # Loading skeleton (shimmer)
│   ├── location_badge_chip.dart  # Location chip
│   ├── location_cards.dart       # LocationCard, LegacyCard, LocationFormScreen
│   ├── location_selector.dart    # Location picker
│   ├── location_tag_editor.dart  # Location tag editor
│   ├── login_prompt_sheet.dart
│   ├── map_picker.dart           # Point picker map
│   ├── open_in_maps_action.dart
│   ├── seat_map_widget.dart      # Interactive seat map
│   └── user_profile_cards.dart   # SessionsCard, AliasesCard
├── l10n/              # AppLocalizations + all ARBs
├── main.dart          # Entry point, Material 3 theme, service init order
├── main_scaffold.dart # NavigationRail (>800px) / NavigationBar (<800px) + Drawer
└── auth_wrapper.dart  # Auth gate (splash → login / home)
```

## Service initialization order (main.dart)

```dart
await DatabaseService.init();           // Hive boxes
await OfflineCacheService.init();       // Load cached data
await SyncQueueService.init();          // Pending mutations
await NodeService.init();               // Node configuration
await ConnectivityMonitor.start();      // Start listening to the network
await LocaleService.load();             // Load saved locale
// Then runApp()
```

## State management pattern

**Singletons + setState + Streams** — No Provider, no flutter_it, no Bloc.

- Services are singletons (lazily initialized in `main.dart`)
- The UI uses `StatefulWidget` + `setState()` for local state
- Services expose Streams for reactive updates (connectivity, auth, sync)
- `ChangeNotifier` is used sparingly (AuthService, LocaleService) for `Consumer` widgets

## API service

`ApiService` (singleton) — base URL via `--dart-define=BACKEND_URL=http://localhost:8000/api`

- Attaches the JWT automatically (from AuthService)
- Automatic token refresh on 401
- Offline queue integration (SyncQueueService)
- Core plus `services/api/` (separated domains); `resolveMediaUrl()` prefixes `/uploads/...` paths with the active node; `uploadFile()` uses MIME by extension, Bearer, 401/refresh retry and fallback between nodes; the chat WS derives its URL from the same `rootUrl`
- Methods: `get`, `post`, `put`, `patch`, `delete`, `upload`

```dart
final api = ApiService();
final festivals = await api.get('/festivals/', query: {'page': '1', 'size': '20'});
```

## Offline-first architecture

1. **Hive boxes**: `festivals`, `users`, `shortfilms`, `messages` (+ events, awards, etc. per model)
2. **Read**: the UI reads from Hive first and syncs from the API in the background
3. **Write**: mutations are queued in `SyncQueueService` (HMAC-signed)
4. **Sync**: on reconnect, `SyncQueueService` replays the queue sequentially
5. **Conflict resolution**: server wins (last-write-wins with timestamp)
6. **Node provenance**: the Hive cache tags each entry by node (`putWithOrigin`, `getOrigin`, `getEnvelope`, `listOrigins`, `clearOrigin`, `reconcile`); `ConnectivityMonitor` exposes `NodeHealth`, `offlineNodeCount` and `isDegraded`, and `DegradedNodesBanner` shows unresponsive nodes with a count and retry (`checkNow()`)

## Internationalization (i18n)

- **Locales**: en, es, fr, de, it, ca, eu, gl, oc (key parity verified with `test/l10n/arb_parity_test.dart`)
- **Manual implementation**: `lib/l10n/app_localizations.dart` (no gen-l10n)
- **ARB files**: `assets/l10n/app_<locale>.arb`
- **Auto-detection**: `LocaleService.load()` reads the system locale, falls back to `en` and persists the resolved one
- **Delegate**: `AppLocalizations.of(context)` (manual delegate, no gen-l10n)

### Adding translations

1. Add the key to `assets/l10n/app_en.arb`
2. Replicate it in the rest of the `.arb` files
3. Use it in Dart: `AppLocalizations.of(context)!.yourKey`

### Nested keys (roles, validation)

```json
"roles": { "admin": "Administrador", "organizer": "Organizador" }
```
```dart
AppLocalizations.of(context)!.roles['admin']
```

## Accessibility (WCAG 2.1 AA)

| Pattern | Use |
|---------|-------|
| `Semantics` | instances for screen readers |
| `SemanticHeader` | Section headings (`header: true`) |
| `SemanticTextField` | Form fields with validation semantics |
| `ExcludeSemantics` | decorative icons |
| `Tooltip` | interactive elements |
| `SnackBarBehavior.floating` | snackbars |
| `autovalidateMode: onUserInteraction` | Forms |
| `TextInputAction.next/done` + `onSubmitted` | Keyboard navigation |

### Reusable accessible widgets

```dart
// lib/widgets/reusable_widgets.dart
ProfileAvatar(avatarUrl, name, radius: 24)
InfoRow(label: 'Email', value: email, icon: Icons.email)
StatusIndicator(isActive: true, label: 'Activo')
ListItemCard(title: 'Festival', subtitle: 'Madrid', onTap: () {})
SemanticHeader('Festivales', level: 1)
SemanticTextField(label: 'Email', validator: emailValidator)
```

## Responsive navigation

- **>800px wide**: `NavigationRail` (side bar)
- **≤800px wide**: `NavigationBar` (bottom bar)
- Implemented in `MainScaffold` with `LayoutBuilder` + Drawer at all sizes

## Theme (Material 3)

- **Seed color**: `#B8956E` (golden sand)
- **Dark mode**: full support via `_baseTheme(ColorScheme)`
- **Component themes**: Card, AppBar, NavigationBar/Rail, InputDecoration, FilledButton, ElevatedButton, TextButton, SnackBar, Dialog, BottomSheet, Chip, ListTile, Drawer, PopupMenu, Scrollbar, Slider, Divider, FAB
- **Cupertino page transitions** on iOS/macOS
- **UI imports**: since Flutter 3.50+ UI imports live in `package:material_ui/material_ui.dart` and `package:cupertino_ui/cupertino_ui.dart`; localization delegates come from `GlobalMaterialLocalizations.delegates` (no `flutter_localizations`). `package:flutter/material.dart` is not used except for the one-off `table_calendar` bridge in `lib/widgets/agenda_calendar_widget.dart`.

## Chat (E2EE)

- **Dual backend**: WebSocket (realtime) + REST (history/sync)
- **E2EE**: X25519 key exchange (pointycastle), AES-GCM message encryption
- **Key storage**: `UserKey` model (public key on backend, private key in Hive)
- **Service**: `ChatService` abstracts WS/REST/E2EE
- **Presence**: `ChatPresenceBackend` provides typing, latency and read receipts; local search, dedup and ordering by `(created_at,id)`, with offline messages durably queued under the same `message_id`

## Maps and geolocation

- `flutter_map` + `latlong2` + `geolocator`
- OpenStreetMap tiles (cancellable tile provider)
- `url_launcher` for native maps apps (Google Maps, Apple Maps, Maps.me)

## Build

```bash
# Web
flutter build web --dart-define=BACKEND_URL=https://api.clakettes.com/api

# Desktop
flutter build windows
flutter build linux
flutter build macos

# Mobile
flutter build apk        # APK Android
flutter build appbundle  # AAB Android (Play Store)
flutter build ios        # iOS (requires macOS + Xcode)
```

## Key dependencies

| Package | Purpose |
|---------|-----------|
| `http` | REST API client |
| `hive_flutter` | Offline cache |
| `shared_preferences` | Locale and auth token persistence |
| `connectivity_plus` | Network detection |
| `web_socket_channel` | Realtime chat |
| `pointycastle` | E2EE X25519/AES-GCM |
| `flutter_map` + `latlong2` | Maps |
| `geolocator` | GPS |
| `flutter_local_notifications` | Local notifications |
| `url_launcher` | External links (maps, web) |
| `uuid` | Client-side IDs |

## Code generation (Hive)

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

Generates `*_adapter.dart` for models annotated with `@HiveType`.

## Testing

```bash
# Unit + widget tests
flutter test

# Integration tests (requires device/emulator)
flutter test integration_test/
```

## Linting

```bash
flutter analyze
```

Uses `flutter_lints` (recommended set).

## Expanded directory structure

```
frontend/
├── android/                 # Config Android
├── ios/                     # Config iOS
├── linux/                   # Config Linux
├── macos/                   # Config macOS
├── windows/                 # Config Windows
├── web/                     # Config web (index.html, manifest.json)
├── assets/
│   ├── l10n/                # all ARBs
│   └── images/              # Logos, placeholders
├── lib/
│   ├── l10n/                # app_localizations.dart (manual)
│   ├── models/              # Dart models (Hive + codegen)
│   ├── screens/             # screens
│   ├── widgets/             # reusable widgets
│   ├── services/            # services + api/ + chat_backend
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
.\build.ps1 -Target all      # All platforms
.\build.ps1 -Target web      # Web only
```

Multi-stage Dockerfile:
- **dev**: `flutter run -d web-server --web-port 3000`
- **prod**: `flutter build web` → static served with nginx

## Environment variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BACKEND_URL` | API base URL (via `--dart-define`) | `http://localhost:8000/api` |
| `CHROME_EXECUTABLE` | Browser for `flutter run -d chrome` | Auto-detected (Brave/Chrome) |

## Troubleshooting

| Issue | Solution |
|----------|----------|
| `flutter pub get` fails | Delete `.dart_tool`, `pubspec.lock` and retry |
| Hive type conflicts | `flutter pub run build_runner build --delete-conflicting-outputs` |
| WebSocket connection failure | Check `BACKEND_URL`; ensure the backend exposes `/ws/chat` |
| Language does not persist | Clear `SharedPreferences`, check `LocaleService.load()` |
| Dark mode does not apply | Ensure explicit `ThemeMode.system` or `ThemeMode.dark` in `MaterialApp` |

## Contributing

1. Follow existing patterns (singletons, `setState`, streams)
2. Add `Semantics` to new interactive widgets
3. Add translations to all ARBs
4. Run `flutter analyze` and `flutter test` before the PR
5. Conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`

## License

MIT — See [LICENSE](../LICENSE) at the root.
