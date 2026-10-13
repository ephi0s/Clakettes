# Clakettes — Frontend-a

Zine-jaialdien kudeaketa plataformarako Flutter frontend multiplataforma.

## Pila teknologikoa

- **Framework-a**: Flutter (Material 3, kolore dinamikoa, modu iluna)
- **Egoera**: Singleton-ak + `setState()` + Stream-ak (EZ Provider, EZ flutter_it, EZ riverpod)
- **Tokiko biltegiratzea**: Hive, SharedPreferences
- **i18n**: 9 hizkuntza (en, es, fr, de, it, ca, eu, gl, oc) — `AppLocalizations` manuala (gen-l10n gabe)
- **Irisgarritasuna**: 94+ Semantics widget, TalkBack/VoiceOver euskarria, WCAG 2.1 AA
- **Arkitektura**: Services / Managers / Views (Flutter Arkitektura Pragmatikoa)

## Hasiera azkarra

```bash
cd frontend
flutter pub get
flutter run -d web-server --web-port 3000
```

## Script-ak

Kontsultatu `../start.bat` / `../start.ps1` abiarazleetarako `--dev`, `--final`, `--web` flag-ekin.

## Arkitektura

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

## Zerbitzuen hasieratze-ordena (main.dart)

```dart
await DatabaseService.init();           // Cajas Hive
await OfflineCacheService.init();       // Cargar datos en caché
await SyncQueueService.init();          // Mutaciones pendientes
await ConnectivityMonitor.start();      // Empezar a escuchar la red
await LocaleService.load();             // Cargar idioma guardado
// Después runApp()
```

## Egoera-kudeaketako eredua

**Singleton-ak + setState + Stream-ak** — Provider gabe, flutter_it gabe, Bloc gabe.

- Zerbitzuak singleton-ak dira (`main.dart`-en alfer hasieratuta)
- UI-k `StatefulWidget` + `setState()` erabiltzen du egoera lokalerako
- Zerbitzuek Stream-ak erakusten dituzte eguneratze erreaktiboetarako (konektibitatea, auth, sync)
- `ChangeNotifier` puntualki erabiltzen da (AuthService, LocaleService) `Consumer` widget-etarako

## API zerbitzua

`ApiService` (singleton) — oinarrizko URL `--dart-define=BACKEND_URL=http://localhost:8000/api` bidez

- JWT automatikoki eransten du (AuthService-tik)
- Token-refresh automatikoa 401-ean
- Offline ilararekin integrazioa (SyncQueueService)
- Metodoak: `get`, `post`, `put`, `patch`, `delete`, `upload`

```dart
final api = ApiService();
final festivals = await api.get('/festivals/', query: {'page': '1', 'size': '20'});
```

## Offline-first arkitektura

1. **Hive kutxak**: `festivals`, `users`, `shortfilms`, `messages` (+ ekitaldiak, sariak, etab. ereduaren arabera)
2. **Irakurketa**: UI-k Hive-tik irakurtzen du lehenik eta API-tik sinkronizatzen du bigarren planoan
3. **Idazketa**: mutazioak `SyncQueueService`-n ilaratzen dira (HMAC-ekin sinatuta)
4. **Sync**: konektibitatea berreskuratzean, `SyncQueueService`-k ilara sekuentzialki erreproduzitzen du
5. **Gatazken ebazpena**: zerbitzariak irabazten du (last-write-wins timestamp-arekin)

## Internazionalizazioa (i18n)

- **9 locale**: en, es, fr, de, it, ca, eu, gl, oc
- **Eskuzko inplementazioa**: `lib/l10n/app_localizations.dart` (gen-l10n gabe)
- **ARB fitxategiak**: `assets/l10n/app_<locale>.arb`
- **Auto-detekzioa**: `LocaleService`-k sistemaren hizkuntza irakurtzen du, fallback `en`-era
- **Delegatua**: `AppLocalizations.of(context)` (delegatu manuala, gen-l10n gabe)

### Itzulpenak gehitzea

1. Gehitu giltza `assets/l10n/app_en.arb`-ra
2. Erreplikatu beste 8 `.arb`-etan
3. Erabili Dart-en: `AppLocalizations.of(context)!.yourKey`

### Giltza habiaratuak (rolak, balidazioa)

```json
"roles": { "admin": "Administrador", "organizer": "Organizador" }
```
```dart
AppLocalizations.of(context)!.roles['admin']
```

## Irisgarritasuna (WCAG 2.1 AA)

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

### Widget berrerabilgarri irisgarriak

```dart
// lib/widgets/reusable_widgets.dart
ProfileAvatar(avatarUrl, name, radius: 24)
InfoRow(label: 'Email', value: email, icon: Icons.email)
StatusIndicator(isActive: true, label: 'Activo')
ListItemCard(title: 'Festival', subtitle: 'Madrid', onTap: () {})
SemanticHeader('Festivales', level: 1)
SemanticTextField(label: 'Email', validator: emailValidator)
```

## Nabigazio responsive-a

- **>800px zabalera**: `NavigationRail` (alboko barra)
- **≤800px zabalera**: `NavigationBar` (beheko barra)
- `MainScaffold`-en inplementatuta `LayoutBuilder` + Drawer-ekin tamaina guztietan

## Gaia (Material 3)

- **Hazi-kolorea**: `#B8956E` (harea doratua)
- **Modu iluna**: euskarri osoa `_baseTheme(ColorScheme)` bidez
- **18+ osagai-gai**: Card, AppBar, NavigationBar/Rail, InputDecoration, FilledButton, ElevatedButton, TextButton, SnackBar, Dialog, BottomSheet, Chip, ListTile, Drawer, PopupMenu, Scrollbar, Slider, Divider, FAB
- **Cupertino orri-trantsizioak** iOS/macOS-en

## Txata (E2EE)

- **Backend bikoitza**: WebSocket (denbora erreala) + REST (historiala/sync)
- **E2EE**: X25519 giltza-trukea (pointycastle), mezu-zifraketa AES-GCM
- **Giltza-biltegiratzea**: `UserKey` eredua (giltza publikoa backend-ean, pribatua Hive-n)
- **Zerbitzua**: `ChatService`-k WS/REST/E2EE abstrahitzen ditu

## Mapak eta kokapena

- `flutter_map` + `latlong2` + `geolocator`
- OpenStreetMap lauzak (lauza-hornitzaile ezeztagarria)
- `url_launcher` mapa-app natiboetarako (Google Maps, Apple Maps, Maps.me)

## Build-a

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

## Mendekotasunak (giltzarriak)

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

## Kode-sorkuntza (Hive)

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

` *_adapter.dart` sortzen du `@HiveType`-dun modeloetarako.

## Testing-a

```bash
# Tests unitarios + de widgets
flutter test

# Tests de integración (requiere dispositivo/emulador)
flutter test integration_test/
```

## Linting-a

```bash
flutter analyze
```

`flutter_lints` erabiltzen du (multzo gomendatua).

## Direktorio-egitura (zabalduta)

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

## Docker (Frontend-a)

```powershell
cd frontend/docker
.\build.ps1 -Target all      # Todas las plataformas
.\build.ps1 -Target web      # Solo web
```

Dockerfile multi-etapa:
- **dev**: `flutter run -d web-server --web-port 3000`
- **prod**: `flutter build web` → estático zerbitzatuta nginx-ekin

## Ingurune-aldagaiak

| Variable | Descripción | Default |
|----------|-------------|---------|
| `BACKEND_URL` | URL base de la API (vía `--dart-define`) | `http://localhost:8000/api` |
| `CHROME_EXECUTABLE` | Navegador para `flutter run -d chrome` | Auto-detectado (Brave/Chrome) |

## Arazoen konponbidea

| Problema | Solución |
|----------|----------|
| `flutter pub get` falla | Borra `.dart_tool`, `pubspec.lock` y repite |
| Conflictos de tipos Hive | `flutter pub run build_runner build --delete-conflicting-outputs` |
| Fallo de conexión WebSocket | Comprueba `BACKEND_URL`; asegúrate de que el backend expone `/ws/chat` |
| El idioma no persiste | Limpia `SharedPreferences`, comprueba `LocaleService.load()` |
| El modo oscuro no aplica | Asegúrate de `ThemeMode.system` o `ThemeMode.dark` explícito en `MaterialApp` |

## Laguntzea

1. Jarraitu existitzen diren ereduak (singleton-ak, `setState`, stream-ak)
2. Gehitu `Semantics` widget interaktibo berriei
3. Gehitu itzulpenak 9 ARB fitxategietara
4. Exekutatu `flutter analyze` eta `flutter test` PR aurretik
5. Commit konbentzionalak: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`

## Lizentzia

MIT — Kontsultatu [LICENSE](../LICENSE) erroan.
