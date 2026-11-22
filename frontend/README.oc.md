# Clakettes — Frontend

[ES](README.md) · [EN](README.en.md) · [FR](README.fr.md) · [DE](README.de.md) · [IT](README.it.md) · [CA](README.ca.md) · [EU](README.eu.md) · [GL](README.gl.md) · [OC](README.oc.md)

Frontend Flutter multiplataforma per la plataforma de gestion de festivals de cinèma.

## Pila tecnologica

- **Framework**: Flutter (Material 3, color dinámico, modo oscuro)
- **Estado**: Singletons + `setState()` + Streams (NO Provider, NO flutter_it, NO riverpod)
- **Almacenamiento local**: Hive, SharedPreferences
- **i18n**: 9 idiomas (en, es, fr, de, it, ca, eu, gl, oc) — `AppLocalizations` manual (sin gen-l10n)
- **Accesibilidad**: widgets Semantics, soporte TalkBack/VoiceOver, WCAG 2.1 AA
- **Arquitectura**: Services / Managers / Views (Arquitectura Flutter Pragmática)

## Aviada rapida

```bash
cd frontend
flutter pub get
flutter run -d web-server --web-port 3000
```

## Scripts

Consulta `../start.ps1` per los lançaïres amb flags `--dev`, `--final`, `--web`.

## Arquitectura

```
lib/
├── screens/           # ecrans UI
│   ├── auth/          # Login
│   ├── festivals/     # Lista, perfil, crear festival
│   ├── users/         # Perfil, repertòri, crear utilizaire, ròtles
│   ├── shortfilms/    # Lista, perfil, crear cortmetratge
│   ├── chat/          # Chat, canaus, crear canau
│   ├── events/        # Gestion e detalh dels eveniments, sètis/reservacions
│   ├── awards/        # Palmarés
│   ├── notifications/ # Centre de notificacions
│   ├── locations/     # Mapa, detalh de localizacion
│   ├── forms/         # Formularis d'inscripcion, editor de paginas, responsas, formularis publics
│   ├── admin/         # Panèl d'administracion
│   ├── committees/    # Comitats
│   └── settings/      # Configuracion del backend, membre del repertòri, panèl
├── services/          # servicis + api/ (domenis) + chat_backend (classas)
│   ├── api_service.dart              # Fachada + nuclèu (auth, transpòrt, admin, recèrca)
│   ├── api/                          # Metòdes per domeni (part of api_service.dart)
│   │   ├── user_api.dart, festival_api.dart, channel_api.dart, form_api.dart
│   │   ├── calendar_api.dart, catalog_api.dart, org_api.dart
│   │   ├── event_api.dart, location_api.dart
│   ├── auth_service.dart             # JWT, persisténcia de session
│   ├── backend_config.dart           # URL del backend (gardada > dart-define > defaut per plataforma)
│   ├── channel_service.dart          # Canaus de chat + claus E2EE
│   ├── connectivity_monitor.dart     # Deteccion en linha/fòra de linha
│   ├── crypto_utils.dart             # E2EE (ECDH P-256, AES-GCM) + compression, amb isolates async
│   ├── database_service.dart         # Inicializacion de Hive + adaptators de tipe
│   ├── file_downloader.dart          # Telecargament natiu (condicional web/io)
│   ├── locale_service.dart           # Persisténcia de la lenga (SharedPreferences)
│   ├── notification_service.dart     # Rapèls: plugin sus escritorio, Notification API sul web, no-op sus mobil
│   ├── notification_platform.dart    # Export condicional web/stub (sens Firebase)
│   ├── offline_cache_service.dart    # Caissas Hive (festivals, users, shortfilms, messages)
│   ├── sync_queue_service.dart       # Coa offline amb retry + backoff (max 3 ensajs)
│   └── chat_backend/                 # Abstraccion WS + REST del chat
│       ├── abstract_chat_backend.dart
│       ├── chat_service.dart         # Fachada WS/REST/E2EE
│       ├── rest_chat_backend.dart    # Istoric/sync via REST (utilizat coma fals dins los tèsts)
│       └── websocket_chat_backend.dart  # Temps reau via WebSocket
├── models/            # modèls Dart (manuals fromJson/toJson + codegen Hive)
├── widgets/           # widgets reutilizables accessibles
│   ├── reusable_widgets.dart     # ProfileAvatar, InfoRow, StatusIndicator, ListItemCard, SemanticHeader, SemanticTextField + showAppSnack
│   ├── agenda_calendar_widget.dart
│   ├── chat_bubble.dart          # Bola de messatge + contengut ric
│   ├── chat_input_bar.dart       # Barra d'entrada del chat
│   ├── confirm_dialog.dart       # Dialòg de confirmacion accessible
│   ├── dav_subscription_section.dart
│   ├── emoji_picker.dart         # Selector d'emojis dins un bottom sheet
│   ├── empty_state_widget.dart   # Estat vuege accessible
│   ├── error_state_widget.dart   # Estat d'error amb reensaj
│   ├── event_visibility_picker.dart
│   ├── festival_sections.dart    # Seccions de règulas e localizacions del festivau
│   ├── film_location_card.dart   # Carta de rodatge en localizacion
│   ├── language_picker.dart
│   ├── list_item_animation.dart  # Animacion d'entrada de las
│   ├── loading_skeleton.dart     # Skeleton de cargament (shimmer)
│   ├── location_badge_chip.dart  # Chip amb localizacion
│   ├── location_cards.dart       # LocationCard, LegacyCard, LocationFormScreen
│   ├── location_selector.dart    # Selector de localizacions
│   ├── location_tag_editor.dart  # Editor d'etiquetas de localizacion
│   ├── login_prompt_sheet.dart
│   ├── map_picker.dart           # Mapa de seleccion de punt
│   ├── open_in_maps_action.dart
│   ├── seat_map_widget.dart      # Mapa de sètis interactiu
│   └── user_profile_cards.dart   # SessionsCard, AliasesCard
├── l10n/              # AppLocalizations + ARB
├── main.dart          # Punt d'entrada, tèma Material 3, òrdre d'inicializacion de servicis
├── main_scaffold.dart # NavigationRail (>800px) / NavigationBar (<800px) + Drawer
└── auth_wrapper.dart  # Pòrta d'autentificacion (splash → login / home)
```

## Òrdre d'inicializacion de servicis (main.dart)

```dart
await DatabaseService.init();           // Caissas Hive
await OfflineCacheService.init();       // Cargar las donadas en cach
await SyncQueueService.init();          // Mutacions en espèra
await NodeService.init();               // Santat e estat dels noses
await ConnectivityMonitor.start();      // Començar a escotar la ret
await LocaleService.load();             // Cargar la lenga gardada
// Puèi runApp()
```

## Patron de gestion d'estat

**Singletons + setState + Streams** — Sens Provider, sens flutter_it, sens Bloc.

- Los servicis son singletons (inicializats peresosament en `main.dart`)
- L'UI utiliza `StatefulWidget` + `setState()` per l'estat locau
- Los servicis expausan Streams per actualizacions reactivas (connectivitat, auth, sync)
- `ChangeNotifier` s'utiliza puntualament (AuthService, LocaleService) per widgets `Consumer`

## Servici d'API

`ApiService` (singleton) — URL de basa via `--dart-define=BACKEND_URL=http://localhost:8000/api`

- Junta lo JWT automaticament (dempuèi AuthService)
- Refresh automatic de token en 401
- Integracion amb la coa offline (SyncQueueService)
- Metòdes: `get`, `post`, `put`, `patch`, `delete`, `upload`

```dart
final api = ApiService();
final festivals = await api.get('/festivals/', query: {'page': '1', 'size': '20'});
```

## Arquitectura offline-first

1. **Caissas Hive**: `festivals`, `users`, `shortfilms`, `messages` (+ eveniments, prèmis, etc. segon modèl)
2. **Lectura**: l'UI legís d'en primièr de Hive e sincroniza dempuèi l'API en segond plan
3. **Escritura**: las mutacions s'enquan en `SyncQueueService` (signadas amb HMAC)
4. **Sync**: en tornar trobar connectivitat, `SyncQueueService` reprodusís la coa sequencialament
5. **Resolucion de conflictes**: ganha lo servidor (last-write-wins amb timestamp)
6. **Provenança**: cada intrada de la cach garda son nose d'origina; `reconcile` fusiona a la reconnexion, `clearOrigin` rebuta un nose e `DegradedNodesBanner` avisa dels noses sens responsa amb recompte e boton de reensaj (`checkNow()`).

## Internacionalizacion (i18n)

- **9 locales**: en, es, fr, de, it, ca, eu, gl, oc (823 claus per ARB, paritat verificada amb `test/l10n/arb_parity_test.dart`)
- **Implementacion manuala**: `lib/l10n/app_localizations.dart` (sens gen-l10n)
- **Fichièrs ARB**: `assets/l10n/app_<locale>.arb`
- **Auto-deteccion**: `LocaleService.load()` legís la lenga del sistèma, amb fallback a `en`, e persista lo locale resolt
- **Delegat**: `AppLocalizations.of(context)` (delegate manual, sens gen-l10n)

### Apondre traduccions

1. Apond la clau a `assets/l10n/app_en.arb`
2. Replica-la dins los autres 8 `.arb`
3. Utiliza-la en Dart: `AppLocalizations.of(context)!.yourKey`

### Claus imbricadas (ròtles, validacion)

```json
"roles": { "admin": "Administrador", "organizer": "Organizador" }
```
```dart
AppLocalizations.of(context)!.roles['admin']
```

## Accessibilitat (WCAG 2.1 AA)

| Patron | Usatge |
|---------|-------|
| `Semantics` | instàncias per lectors d'ecran |
| `SemanticHeader` | Títols de seccion (`header: true`) |
| `SemanticTextField` | Camps de formulari amb semantica de validacion |
| `ExcludeSemantics` | icònas decorativas |
| `Tooltip` | elements interactius |
| `SnackBarBehavior.floating` | snackbars |
| `autovalidateMode: onUserInteraction` | Formularis |
| `TextInputAction.next/done` + `onSubmitted` | Navigacion per clavier |

### Widgets reutilizables accessibles

```dart
// lib/widgets/reusable_widgets.dart
ProfileAvatar(avatarUrl, name, radius: 24)
InfoRow(label: 'Email', value: email, icon: Icons.email)
StatusIndicator(isActive: true, label: 'Activo')
ListItemCard(title: 'Festival', subtitle: 'Madrid', onTap: () {})
SemanticHeader('Festivales', level: 1)
SemanticTextField(label: 'Email', validator: emailValidator)
```

## Navegacion responsiva

- **>800px de larg**: `NavigationRail` (barra laterala)
- **≤800px de larg**: `NavigationBar` (barra inferiora)
- Implementat en `MainScaffold` amb `LayoutBuilder` + Drawer en totas las talhas

## Tèma (Material 3)

- **Color grana**: `#B8956E` (arena daurada)
- **Mòde escur**: sosten complet via `_baseTheme(ColorScheme)`
- **tèmas de compausants**: Card, AppBar, NavigationBar/Rail, InputDecoration, FilledButton, ElevatedButton, TextButton, SnackBar, Dialog, BottomSheet, Chip, ListTile, Drawer, PopupMenu, Scrollbar, Slider, Divider, FAB
- **Transicions de pagina Cupertino** en iOS/macOS

## Chat (E2EE)

- **Backend duau**: WebSocket (temps reau) + REST (istoric/sync)
- **E2EE**: escambi de claus X25519 (pointycastle), chiframent de messatges AES-GCM
- **Estocatge de claus**: modèl `UserKey` (clau publica en backend, privada en Hive)
- **Servici**: `ChatService` abstrach WS/REST/E2EE
- **Preséncia**: `ChatPresenceBackend` apòrta escritura, laténcia e confirmacions de lectura; recèrca locala, dedup e ordre per `(created_at,id)`; messatges offline encolats de forma durabla amb lo meteis `message_id`

## Mapas e localizacion

- `flutter_map` + `latlong2` + `geolocator`
- Teulas d'OpenStreetMap (fornidor de teulas anulable)
- `url_launcher` per apps de mapas nativas (Google Maps, Apple Maps, Maps.me)

## Build

```bash
# Web
flutter build web --dart-define=BACKEND_URL=https://api.clakettes.com/api

# Buro
flutter build windows
flutter build linux
flutter build macos

# Mobil
flutter build apk        # APK Android
flutter build appbundle  # AAB Android (Play Store)
flutter build ios        # iOS (demanda macOS + Xcode)
```

## Dependéncias (clau)

| Paquet | Propòsit |
|---------|-----------|
| `http` | Client REST API |
| `hive_flutter` | Cach offline |
| `shared_preferences` | Persisténcia del locale e del token d'autentificacion |
| `connectivity_plus` | Deteccion de la ret |
| `web_socket_channel` | Chat en temps reau |
| `pointycastle` | E2EE X25519/AES-GCM |
| `flutter_map` + `latlong2` | Mapas |
| `geolocator` | GPS |
| `flutter_local_notifications` | Notificacions localas |
| `url_launcher` | Ligams extèrnes (mapas, web) |
| `uuid` | IDs del costat client |

## Generacion de còde (Hive)

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

Genera `*_adapter.dart` per los modèls anotats amb `@HiveType`.

## Testing

```bash
# Tèsts unitaris + de widgets
flutter test

# Tèsts d'integracion (demanda aparelh/emulator)
flutter test integration_test/
```

## Linting

```bash
flutter analyze
```

Utiliza `flutter_lints` (jòc recomandat).

## Estructura del directòri (ampliada)

```
frontend/
├── android/                 # Config Android
├── ios/                     # Config iOS
├── linux/                   # Config Linux
├── macos/                   # Config macOS
├── windows/                 # Config Windows
├── web/                     # Config web (index.html, manifest.json)
├── assets/
│   ├── l10n/                # fichièrs ARB
│   └── images/              # Logos, placeholders
├── lib/
│   ├── l10n/                # app_localizations.dart (manual)
│   ├── models/              # modèls Dart (Hive + codegen)
│   ├── screens/             # ecrans
│   ├── widgets/             # widgets reutilizables
│   ├── services/            # servicis + api/ + chat_backend
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
.\build.ps1 -Target all      # Totas las plataformas
.\build.ps1 -Target web      # Sonque web
```

Dockerfile multi-etapa:
- **dev**: `flutter run -d web-server --web-port 3000`
- **prod**: `flutter build web` → servit estatic amb nginx

## Variablas d'environa

| Variabla | Descripcion | Defaut |
|----------|-------------|---------|
| `BACKEND_URL` | URL de basa de l'API (via `--dart-define`) | `http://localhost:8000/api` |
| `CHROME_EXECUTABLE` | Navegador per `flutter run -d chrome` | Detectat automaticament (Brave/Chrome) |

## Solucion de problèmas

| Problema | Solucion |
|----------|----------|
| `flutter pub get` fracassa | Escafa `.dart_tool`, `pubspec.lock` e tornatz ensajar |
| Conflictis de tipes Hive | `flutter pub run build_runner build --delete-conflicting-outputs` |
| Fracàs de connexion WebSocket | Verifica `BACKEND_URL`; assegura't que lo backend expausa `/ws/chat` |
| La lenga persista pas | Escafa `SharedPreferences`, verifica `LocaleService.load()` |
| Lo mòde escur s'aplica pas | Assegura-te de `ThemeMode.system` o `ThemeMode.dark` explicit dins `MaterialApp` |

## Contribuir

1. Seguís los patrons existents (singletons, `setState`, streams)
2. Apond `Semantics` als nòus widgets interactius
3. Apond traduccions als 9 fichièrs ARB
4. Executa `flutter analyze` e `flutter test` abans del PR
5. Commits convencionaus: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`

## Licéncia

MIT — Consulta [LICENSE](../LICENSE) en la raiç.
