# Clakettes — Frontend

[ES](README.md) · [EN](README.en.md) · [FR](README.fr.md) · [DE](README.de.md) · [IT](README.it.md) · [CA](README.ca.md) · [EU](README.eu.md) · [GL](README.gl.md) · [OC](README.oc.md)

Multi-platform Flutter frontend for the film festival management platform.

## Tech stack

- **Framework**: Flutter (Material 3, dynamic color, dark mode)
- **State**: Singletons + `setState()` + Streams (NO Provider, NO flutter_it, NO riverpod)
- **Local storage**: Hive, SharedPreferences
- **i18n**: 9 languages (en, es, fr, de, it, ca, eu, gl, oc) — manual `AppLocalizations` (no gen-l10n)
- **Accessibility**: 94+ Semantics widgets, TalkBack/VoiceOver support, WCAG 2.1 AA
- **Architecture**: Services / Managers / Views (Pragmatic Flutter Architecture)

## Quick start

```bash
cd frontend
flutter pub get
flutter run -d web-server --web-port 3000
```

## Scripts

See `../start.bat` / `../start.ps1` for launchers with `--dev`, `--final`, `--web` flags.

## Architecture

```
lib/
├── screens/           # 36 pantallas UI
│   ├── auth/          # Login
│   ├── festivals/     # Lista, perfil, crear festival
│   ├── users/         # Perfil, directorio, crear usuario, roles
│   ├── shortfilms/    # Lista, perfil, crear cortometraje
│   ├── chat/          # Chat, canales, crear canal
│   ├── events/        # Gestión y detalle de eventos, asientos/reservas
│   ├── awards/        # Palmarés
│   ├── notifications/ # Centro de notificaciones
│   ├── locations/     # Mapa, detalle de localización
│   ├── forms/         # Formularios de registro, editor de páginas, respuestas, formularios públicos
│   ├── admin/         # Panel de administración
│   ├── committees/    # Comités
│   └── settings/      # Configuración del backend, miembro del directorio, dashboard
├── services/          # 17 servicios + api/ (9 dominios) + chat_backend (4 clases)
│   ├── api_service.dart              # Fachada + núcleo (auth, transporte, admin, búsqueda)
│   ├── api/                          # Métodos por dominio (part of api_service.dart)
│   │   ├── user_api.dart, festival_api.dart, channel_api.dart, form_api.dart
│   │   ├── calendar_api.dart, catalog_api.dart, org_api.dart
│   │   ├── event_api.dart, location_api.dart
│   ├── auth_service.dart             # JWT, persistencia de sesión
│   ├── backend_config.dart           # URL del backend (guardada > dart-define > default por plataforma)
│   ├── channel_service.dart          # Canales de chat + claves E2EE
│   ├── connectivity_monitor.dart     # Detección online/offline
│   ├── crypto_utils.dart             # E2EE (ECDH P-256, AES-GCM) + compresión, con isolates async
│   ├── database_service.dart         # Inicialización de Hive + adaptadores de tipos
│   ├── file_downloader.dart          # Descarga nativa (condicional web/io)
│   ├── locale_service.dart           # Persistencia de idioma (SharedPreferences)
│   ├── notification_service.dart     # Recordatorios: plugin en escritorio, Notification API en web, no-op en móvil
│   ├── notification_platform.dart    # Export condicional web/stub (sin Firebase)
│   ├── offline_cache_service.dart    # Cajas Hive (festivals, users, shortfilms, messages)
│   ├── sync_queue_service.dart       # Cola offline con retry + backoff (max 3 intentos)
│   └── chat_backend/                 # Abstracción WS + REST del chat
│       ├── abstract_chat_backend.dart
│       ├── chat_service.dart         # Fachada WS/REST/E2EE
│       ├── rest_chat_backend.dart    # Historial/sync vía REST (usado como fake en tests)
│       └── websocket_chat_backend.dart  # Tiempo real vía WebSocket
├── models/            # 24 modelos Dart (manuales fromJson/toJson + Hive codegen)
├── widgets/           # 24 widgets reutilizables accesibles
│   ├── reusable_widgets.dart     # ProfileAvatar, InfoRow, StatusIndicator, ListItemCard, SemanticHeader, SemanticTextField + showAppSnack
│   ├── agenda_calendar_widget.dart
│   ├── chat_bubble.dart          # Burbuja de mensaje + contenido enriquecido
│   ├── chat_input_bar.dart       # Barra de entrada del chat
│   ├── confirm_dialog.dart       # Diálogo de confirmación accesible
│   ├── dav_subscription_section.dart
│   ├── emoji_picker.dart         # Selector de emojis en bottom sheet
│   ├── empty_state_widget.dart   # Estado vacío accesible
│   ├── error_state_widget.dart   # Estado de error con reintento
│   ├── event_visibility_picker.dart
│   ├── festival_sections.dart    # Secciones de bases y localizaciones del festival
│   ├── film_location_card.dart   # Tarjeta de rodaje en localización
│   ├── language_picker.dart
│   ├── list_item_animation.dart  # Animación de entrada de filas
│   ├── loading_skeleton.dart     # Skeleton de carga (shimmer)
│   ├── location_badge_chip.dart  # Chip con localización
│   ├── location_cards.dart       # LocationCard, LegacyCard, LocationFormScreen
│   ├── location_selector.dart    # Selector de localizaciones
│   ├── location_tag_editor.dart  # Editor de etiquetas de localización
│   ├── login_prompt_sheet.dart
│   ├── map_picker.dart           # Mapa de selección de punto
│   ├── open_in_maps_action.dart
│   ├── seat_map_widget.dart      # Mapa de asientos interactivo
│   └── user_profile_cards.dart   # SessionsCard, AliasesCard
├── l10n/              # AppLocalizations + 9 ARB
├── main.dart          # Entry point, tema Material 3, orden de init de servicios
├── main_scaffold.dart # NavigationRail (>800px) / NavigationBar (<800px) + Drawer
└── auth_wrapper.dart  # Gate de autenticación (splash → login / home)
```

## Service initialization order (main.dart)

```dart
await DatabaseService.init();           // Cajas Hive
await OfflineCacheService.init();       // Cargar datos en caché
await SyncQueueService.init();          // Mutaciones pendientes
await ConnectivityMonitor.start();      // Empezar a escuchar la red
await LocaleService.load();             // Cargar idioma guardado
// Después runApp()
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

## Internationalization (i18n)

- **9 locales**: en, es, fr, de, it, ca, eu, gl, oc
- **Manual implementation**: `lib/l10n/app_localizations.dart` (no gen-l10n)
- **ARB files**: `assets/l10n/app_<locale>.arb`
- **Auto-detection**: `LocaleService` reads the system language, falling back to `en`
- **Delegate**: `AppLocalizations.of(context)` (manual delegate, no gen-l10n)

### Adding translations

1. Add the key to `assets/l10n/app_en.arb`
2. Replicate it in the other 8 `.arb` files
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
| `Semantics` | 94+ instances for screen readers |
| `SemanticHeader` | Section headings (`header: true`) |
| `SemanticTextField` | Form fields with validation semantics |
| `ExcludeSemantics` | 8+ decorative icons |
| `Tooltip` | 26+ interactive elements |
| `SnackBarBehavior.floating` | 29+ snackbars |
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
- **18+ component themes**: Card, AppBar, NavigationBar/Rail, InputDecoration, FilledButton, ElevatedButton, TextButton, SnackBar, Dialog, BottomSheet, Chip, ListTile, Drawer, PopupMenu, Scrollbar, Slider, Divider, FAB
- **Cupertino page transitions** on iOS/macOS

## Chat (E2EE)

- **Dual backend**: WebSocket (realtime) + REST (history/sync)
- **E2EE**: X25519 key exchange (pointycastle), AES-GCM message encryption
- **Key storage**: `UserKey` model (public key on backend, private key in Hive)
- **Service**: `ChatService` abstracts WS/REST/E2EE

## Maps and geolocation

- `flutter_map` + `latlong2` + `geolocator`
- OpenStreetMap tiles (cancellable tile provider)
- `url_launcher` for native maps apps (Google Maps, Apple Maps, Maps.me)

## Build

```bash
# Web
flutter build web --dart-define=BACKEND_URL=https://api.clakettes.com/api

# Escritorio
flutter build windows
flutter build linux
flutter build macos

# Móvil
flutter build apk        # APK Android
flutter build appbundle  # AAB Android (Play Store)
flutter build ios        # iOS (requiere macOS + Xcode)
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
# Tests unitarios + de widgets
flutter test

# Tests de integración (requiere dispositivo/emulador)
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
│   ├── l10n/                # 9 archivos ARB
│   └── images/              # Logos, placeholders
├── lib/
│   ├── l10n/                # app_localizations.dart (manual)
│   ├── models/              # 44 modelos Dart (Hive + codegen)
│   ├── screens/             # 36 pantallas
│   ├── widgets/             # 24 widgets reutilizables
│   ├── services/            # 17 servicios + api/ (9) + chat_backend (4)
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
.\build.ps1 -Target all      # Todas las plataformas
.\build.ps1 -Target web      # Solo web
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
3. Add translations to all 9 ARB files
4. Run `flutter analyze` and `flutter test` before the PR
5. Conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`

## License

MIT — See [LICENSE](../LICENSE) at the root.
