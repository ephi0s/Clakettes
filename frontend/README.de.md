# Clakettes — Frontend

Flutter-Frontend (multiplattform) für die Filmfestival-Management-Plattform.

## Technologie-Stack

- **Framework**: Flutter (Material 3, color dinámico, modo oscuro)
- **Estado**: Singletons + `setState()` + Streams (NO Provider, NO flutter_it, NO riverpod)
- **Almacenamiento local**: Hive, SharedPreferences
- **i18n**: 9 idiomas (en, es, fr, de, it, ca, eu, gl, oc) — `AppLocalizations` manual (sin gen-l10n)
- **Accesibilidad**: 94+ widgets Semantics, soporte TalkBack/VoiceOver, WCAG 2.1 AA
- **Arquitectura**: Services / Managers / Views (Arquitectura Flutter Pragmática)

## Schnellstart

```bash
cd frontend
flutter pub get
flutter run -d web-server --web-port 3000
```

## Skripte

Consulta `../start.bat` / `../start.ps1` für die Launcher mit Flags `--dev`, `--final`, `--web`.

## Architektur

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

## Dienst-Initialisierungsreihenfolge (main.dart)

```dart
await DatabaseService.init();           // Cajas Hive
await OfflineCacheService.init();       // Cargar datos en caché
await SyncQueueService.init();          // Mutaciones pendientes
await ConnectivityMonitor.start();      // Empezar a escuchar la red
await LocaleService.load();             // Cargar idioma guardado
// Después runApp()
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

## Internationalisierung (i18n)

- **9 Locales**: en, es, fr, de, it, ca, eu, gl, oc
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

| Patrón | Uso |
|---------|-------|
| `Semantics` | 94+ instancias para lectores de pantalla |
| `SemanticHeader` | Encabezados de sección (`header: true`) |
| `SemanticTextField` | Campos de formulario con semántica de validación |
| `ExcludeSemantics` | 8+ iconos decorativos |
| `Tooltip` | 26+ elementos interactivos |
| `SnackBarBehavior.floating` | 29+ snackbars |
| `autovalidateMode: onUserInteraction` | Formularios |
| `TextInputAction.next/done` + `onSubmitted` | Navegación por teclado |

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

# Escritorio
flutter build windows
flutter build linux
flutter build macos

# Móvil
flutter build apk        # APK Android
flutter build appbundle  # AAB Android (Play Store)
flutter build ios        # iOS (requiere macOS + Xcode)
```

## Schlüsselabhängigkeiten

| Paquete | Propósito |
|---------|-----------|
| `http` | Cliente REST API |
| `hive_flutter` | Caché offline |
| `shared_preferences` | Persistencia de locale y token de auth |
| `connectivity_plus` | Detección de red |
| `web_socket_channel` | Chat en tiempo real |
| `pointycastle` | E2EE X25519/AES-GCM |
| `flutter_map` + `latlong2` | Mapas |
| `geolocator` | GPS |
| `flutter_local_notifications` | Notificaciones locales |
| `url_launcher` | Enlaces externos (mapas, web) |
| `uuid` | IDs del lado del cliente |

## Codegenerierung (Hive)

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

Generiert `*_adapter.dart` für die mit `@HiveType` annotierten Modelle.

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

Multi-Stage-Dockerfile:
- **dev**: `flutter run -d web-server --web-port 3000`
- **prod**: `flutter build web` → statisch serviert mit nginx

## Umgebungsvariablen

| Variable | Descripción | Default |
|----------|-------------|---------|
| `BACKEND_URL` | URL base de la API (vía `--dart-define`) | `http://localhost:8000/api` |
| `CHROME_EXECUTABLE` | Navegador para `flutter run -d chrome` | Auto-detectado (Brave/Chrome) |

## Fehlerbehebung

| Problema | Solución |
|----------|----------|
| `flutter pub get` falla | Borra `.dart_tool`, `pubspec.lock` y repite |
| Conflictos de tipos Hive | `flutter pub run build_runner build --delete-conflicting-outputs` |
| Fallo de conexión WebSocket | Comprueba `BACKEND_URL`; asegúrate de que el backend expone `/ws/chat` |
| El idioma no persiste | Limpia `SharedPreferences`, comprueba `LocaleService.load()` |
| El modo oscuro no aplica | Asegúrate de `ThemeMode.system` o `ThemeMode.dark` explícito en `MaterialApp` |

## Beitragen

1. Folge den bestehenden Mustern (Singletons, `setState`, Streams)
2. Füge `Semantics` zu neuen interaktiven Widgets hinzu
3. Füge Übersetzungen zu den 9 ARB-Dateien hinzu
4. Führe `flutter analyze` und `flutter test` vor dem PR aus
5. Konventionelle Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`

## Lizenz

MIT — Siehe [LICENSE](../LICENSE) im Root.
