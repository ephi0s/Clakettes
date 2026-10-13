# Clakettes — Frontend

[ES](README.md) · [EN](README.en.md) · [FR](README.fr.md) · [DE](README.de.md) · [IT](README.it.md) · [CA](README.ca.md) · [EU](README.eu.md) · [GL](README.gl.md) · [OC](README.oc.md)

Frontend Flutter multiplataforma per a la plataforma de gestió de festivals de cinema.

## Stack tecnològic

- **Framework**: Flutter (Material 3, color dinàmic, mode fosc)
- **Estat**: Singletons + `setState()` + Streams (NO Provider, NO flutter_it, NO riverpod)
- **Emmagatzematge local**: Hive, SharedPreferences
- **i18n**: 9 idiomes (en, es, fr, de, it, ca, eu, gl, oc) — `AppLocalizations` manual (sense gen-l10n)
- **Accessibilitat**: 94+ widgets Semantics, suport TalkBack/VoiceOver, WCAG 2.1 AA
- **Arquitectura**: Services / Managers / Views (Arquitectura Flutter Pragmàtica)

## Inici ràpid

```bash
cd frontend
flutter pub get
flutter run -d web-server --web-port 3000
```

## Scripts

Consulta `../start.bat` / `../start.ps1` per als llançadors amb flags `--dev`, `--final`, `--web`.

## Arquitectura

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

## Ordre d'inicialització de serveis (main.dart)

```dart
await DatabaseService.init();           // Cajas Hive
await OfflineCacheService.init();       // Cargar datos en caché
await SyncQueueService.init();          // Mutaciones pendientes
await ConnectivityMonitor.start();      // Empezar a escuchar la red
await LocaleService.load();             // Cargar idioma guardado
// Después runApp()
```

## Patró de gestió d'estat

**Singletons + setState + Streams** — Sense Provider, sense flutter_it, sense Bloc.

- Els serveis són singletons (inicialitzats peresosament a `main.dart`)
- La UI utilitza `StatefulWidget` + `setState()` per a l'estat local
- Els serveis exposen Streams per a actualitzacions reactives (connectivitat, auth, sync)
- `ChangeNotifier` s'utilitza puntualment (AuthService, LocaleService) per a widgets `Consumer`

## Servei d'API

`ApiService` (singleton) — URL base via `--dart-define=BACKEND_URL=http://localhost:8000/api`

- Adjunta el JWT automàticament (des d'AuthService)
- Refresh automàtic de token en 401
- Integració amb la cua offline (SyncQueueService)
- Mètodes: `get`, `post`, `put`, `patch`, `delete`, `upload`

```dart
final api = ApiService();
final festivals = await api.get('/festivals/', query: {'page': '1', 'size': '20'});
```

## Arquitectura offline-first

1. **Caixes Hive**: `festivals`, `users`, `shortfilms`, `messages` (+ esdeveniments, premis, etc. segons model)
2. **Lectura**: la UI llegeix primer d'Hive i sincronitza des de l'API en segon pla
3. **Escriptura**: les mutacions s'encuen a `SyncQueueService` (signades amb HMAC)
4. **Sync**: en recuperar connectivitat, `SyncQueueService` reprodueix la cua seqüencialment
5. **Resolució de conflictes**: guanya el servidor (last-write-wins amb timestamp)

## Internacionalització (i18n)

- **9 locales**: en, es, fr, de, it, ca, eu, gl, oc
- **Implementació manual**: `lib/l10n/app_localizations.dart` (sense gen-l10n)
- **Fitxers ARB**: `assets/l10n/app_<locale>.arb`
- **Auto-detecció**: `LocaleService` llegeix l'idioma del sistema, amb fallback a `en`
- **Delegat**: `AppLocalizations.of(context)` (delegate manual, sense gen-l10n)

### Afegir traduccions

1. Afegeix la clau a `assets/l10n/app_en.arb`
2. Replica-la als altres 8 `.arb`
3. Utilitza-la en Dart: `AppLocalizations.of(context)!.yourKey`

### Claus niades (rols, validació)

```json
"roles": { "admin": "Administrador", "organizer": "Organizador" }
```
```dart
AppLocalizations.of(context)!.roles['admin']
```

## Accessibilitat (WCAG 2.1 AA)

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

### Widgets reutilitzables accessibles

```dart
// lib/widgets/reusable_widgets.dart
ProfileAvatar(avatarUrl, name, radius: 24)
InfoRow(label: 'Email', value: email, icon: Icons.email)
StatusIndicator(isActive: true, label: 'Activo')
ListItemCard(title: 'Festival', subtitle: 'Madrid', onTap: () {})
SemanticHeader('Festivales', level: 1)
SemanticTextField(label: 'Email', validator: emailValidator)
```

## Navegació responsive

- **>800px d'amplada**: `NavigationRail` (barra lateral)
- **≤800px d'amplada**: `NavigationBar` (barra inferior)
- Implementat a `MainScaffold` amb `LayoutBuilder` + Drawer en totes les mides

## Tema (Material 3)

- **Color llavor**: `#B8956E` (arena daurada)
- **Mode fosc**: suport complet via `_baseTheme(ColorScheme)`
- **18+ temes de components**: Card, AppBar, NavigationBar/Rail, InputDecoration, FilledButton, ElevatedButton, TextButton, SnackBar, Dialog, BottomSheet, Chip, ListTile, Drawer, PopupMenu, Scrollbar, Slider, Divider, FAB
- **Transicions de pàgina Cupertino** en iOS/macOS

## Xat (E2EE)

- **Backend dual**: WebSocket (temps real) + REST (historial/sync)
- **E2EE**: intercanvi de claus X25519 (pointycastle), xifrat de missatges AES-GCM
- **Emmagatzematge de claus**: model `UserKey` (clau pública en backend, privada en Hive)
- **Servei**: `ChatService` abstrau WS/REST/E2EE

## Mapes i localització

- `flutter_map` + `latlong2` + `geolocator`
- Tesel·les d'OpenStreetMap (proveïdor de tesel·les cancel·lable)
- `url_launcher` per a apps de mapes natives (Google Maps, Apple Maps, Maps.me)

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

## Dependències (clau)

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

## Generació de codi (Hive)

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

Genera `*_adapter.dart` per als models anotats amb `@HiveType`.

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

Utilitza `flutter_lints` (conjunt recomanat).

## Estructura del directori (ampliada)

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

Dockerfile multi-etapa:
- **dev**: `flutter run -d web-server --web-port 3000`
- **prod**: `flutter build web` → servit estàtic amb nginx

## Variables d'entorn

| Variable | Descripción | Default |
|----------|-------------|---------|
| `BACKEND_URL` | URL base de la API (vía `--dart-define`) | `http://localhost:8000/api` |
| `CHROME_EXECUTABLE` | Navegador para `flutter run -d chrome` | Auto-detectado (Brave/Chrome) |

## Solució de problemes

| Problema | Solución |
|----------|----------|
| `flutter pub get` falla | Borra `.dart_tool`, `pubspec.lock` y repite |
| Conflictos de tipos Hive | `flutter pub run build_runner build --delete-conflicting-outputs` |
| Fallo de conexión WebSocket | Comprueba `BACKEND_URL`; asegúrate de que el backend expone `/ws/chat` |
| El idioma no persiste | Limpia `SharedPreferences`, comprueba `LocaleService.load()` |
| El modo oscuro no aplica | Asegúrate de `ThemeMode.system` o `ThemeMode.dark` explícito en `MaterialApp` |

## Contribuir

1. Segueix els patrons existents (singletons, `setState`, streams)
2. Afegeix `Semantics` als nous widgets interactius
3. Afegeix traduccions als 9 fitxers ARB
4. Executa `flutter analyze` i `flutter test` abans del PR
5. Commits convencionals: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`

## Llicència

MIT — Consulta [LICENSE](../LICENSE) en l'arrel.
