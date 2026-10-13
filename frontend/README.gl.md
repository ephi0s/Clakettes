# Clakettes — Frontend

Frontend Flutter multiplataforma para a plataforma de xestión de festivais de cine.

## Stack tecnolóxico

- **Framework**: Flutter (Material 3, cor dinámica, modo escuro)
- **Estado**: Singletons + `setState()` + Streams (NO Provider, NO flutter_it, NO riverpod)
- **Almacenamento local**: Hive, SharedPreferences
- **i18n**: 9 idiomas (en, es, fr, de, it, ca, eu, gl, oc) — `AppLocalizations` manual (sen gen-l10n)
- **Accesibilidade**: 94+ widgets Semantics, soporte TalkBack/VoiceOver, WCAG 2.1 AA
- **Arquitectura**: Services / Managers / Views (Arquitectura Flutter Pragmática)

## Inicio rápido

```bash
cd frontend
flutter pub get
flutter run -d web-server --web-port 3000
```

## Scripts

Consulta `../start.bat` / `../start.ps1` para os lanzadores con flags `--dev`, `--final`, `--web`.

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

## Orde de inicialización de servizos (main.dart)

```dart
await DatabaseService.init();           // Cajas Hive
await OfflineCacheService.init();       // Cargar datos en caché
await SyncQueueService.init();          // Mutaciones pendientes
await ConnectivityMonitor.start();      // Empezar a escuchar la red
await LocaleService.load();             // Cargar idioma guardado
// Después runApp()
```

## Patrón de xestión de estado

**Singletons + setState + Streams** — Sen Provider, sen flutter_it, sen Bloc.

- Os servizos son singletons (inicializados preguiceiramente en `main.dart`)
- A UI usa `StatefulWidget` + `setState()` para o estado local
- Os servizos expoñen Streams para actualizacións reactivas (conectividade, auth, sync)
- `ChangeNotifier` úsase puntualmente (AuthService, LocaleService) para widgets `Consumer`

## Servizo de API

`ApiService` (singleton) — URL base vía `--dart-define=BACKEND_URL=http://localhost:8000/api`

- Adxunta o JWT automaticamente (desde AuthService)
- Refresh automático de token en 401
- Integración coa cola offline (SyncQueueService)
- Métodos: `get`, `post`, `put`, `patch`, `delete`, `upload`

```dart
final api = ApiService();
final festivals = await api.get('/festivals/', query: {'page': '1', 'size': '20'});
```

## Arquitectura offline-first

1. **Caixas Hive**: `festivals`, `users`, `shortfilms`, `messages` (+ eventos, premios, etc. segundo modelo)
2. **Lectura**: a UI le primeiro de Hive e sincroniza desde a API en segundo plano
3. **Escritura**: as mutacións encólanse en `SyncQueueService` (firmadas con HMAC)
4. **Sync**: ao recuperar conectividade, `SyncQueueService` reproduce a cola secuencialmente
5. **Resolución de conflitos**: gaña o servidor (last-write-wins con timestamp)

## Internacionalización (i18n)

- **9 locales**: en, es, fr, de, it, ca, eu, gl, oc
- **Implementación manual**: `lib/l10n/app_localizations.dart` (sen gen-l10n)
- **Arquivos ARB**: `assets/l10n/app_<locale>.arb`
- **Auto-detección**: `LocaleService` le o idioma do sistema, con fallback a `en`
- **Delegado**: `AppLocalizations.of(context)` (delegate manual, sen gen-l10n)

### Engadir traducións

1. Engade a clave a `assets/l10n/app_en.arb`
2. Replícaa nos outros 8 `.arb`
3. Úsaa en Dart: `AppLocalizations.of(context)!.yourKey`

### Claves aniñadas (roles, validación)

```json
"roles": { "admin": "Administrador", "organizer": "Organizador" }
```
```dart
AppLocalizations.of(context)!.roles['admin']
```

## Accesibilidade (WCAG 2.1 AA)

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

### Widgets reutilizables accesibles

```dart
// lib/widgets/reusable_widgets.dart
ProfileAvatar(avatarUrl, name, radius: 24)
InfoRow(label: 'Email', value: email, icon: Icons.email)
StatusIndicator(isActive: true, label: 'Activo')
ListItemCard(title: 'Festival', subtitle: 'Madrid', onTap: () {})
SemanticHeader('Festivales', level: 1)
SemanticTextField(label: 'Email', validator: emailValidator)
```

## Navegación responsive

- **>800px de ancho**: `NavigationRail` (barra lateral)
- **≤800px de ancho**: `NavigationBar` (barra inferior)
- Implementado en `MainScaffold` con `LayoutBuilder` + Drawer en todos os tamaños

## Tema (Material 3)

- **Cor semente**: `#B8956E` (area dourada)
- **Modo escuro**: soporte completo vía `_baseTheme(ColorScheme)`
- **18+ temas de compoñentes**: Card, AppBar, NavigationBar/Rail, InputDecoration, FilledButton, ElevatedButton, TextButton, SnackBar, Dialog, BottomSheet, Chip, ListTile, Drawer, PopupMenu, Scrollbar, Slider, Divider, FAB
- **Transicións de páxina Cupertino** en iOS/macOS

## Chat (E2EE)

- **Backend dual**: WebSocket (tempo real) + REST (historial/sync)
- **E2EE**: intercambio de claves X25519 (pointycastle), cifrado de mensaxes AES-GCM
- **Almacenamento de claves**: modelo `UserKey` (clave pública en backend, privada en Hive)
- **Servizo**: `ChatService` abstrae WS/REST/E2EE

## Mapas e localización

- `flutter_map` + `latlong2` + `geolocator`
- Teselas de OpenStreetMap (provedor de teselas cancelable)
- `url_launcher` para apps de mapas nativas (Google Maps, Apple Maps, Maps.me)

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

## Dependencias (clave)

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

## Xeración de código (Hive)

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

Xera `*_adapter.dart` para os modelos anotados con `@HiveType`.

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

Usa `flutter_lints` (conxunto recomendado).

## Estrutura do directorio (ampliada)

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
- **prod**: `flutter build web` → servido estático con nginx

## Variables de entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `BACKEND_URL` | URL base de la API (vía `--dart-define`) | `http://localhost:8000/api` |
| `CHROME_EXECUTABLE` | Navegador para `flutter run -d chrome` | Auto-detectado (Brave/Chrome) |

## Solución de problemas

| Problema | Solución |
|----------|----------|
| `flutter pub get` falla | Borra `.dart_tool`, `pubspec.lock` y repite |
| Conflictos de tipos Hive | `flutter pub run build_runner build --delete-conflicting-outputs` |
| Fallo de conexión WebSocket | Comprueba `BACKEND_URL`; asegúrate de que el backend expone `/ws/chat` |
| El idioma no persiste | Limpia `SharedPreferences`, comprueba `LocaleService.load()` |
| El modo oscuro no aplica | Asegúrate de `ThemeMode.system` o `ThemeMode.dark` explícito en `MaterialApp` |

## Contribuír

1. Segue os patróns existentes (singletons, `setState`, streams)
2. Engade `Semantics` aos novos widgets interactivos
3. Engade traducións aos 9 arquivos ARB
4. Executa `flutter analyze` e `flutter test` antes do PR
5. Commits convencionais: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`

## Licenza

MIT — Consulta [LICENSE](../LICENSE) na raíz.
