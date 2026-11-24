# Clakettes — Frontend

[ES](README.md) · [EN](README.en.md) · [FR](README.fr.md) · [DE](README.de.md) · [IT](README.it.md) · [CA](README.ca.md) · [EU](README.eu.md) · [GL](README.gl.md) · [OC](README.oc.md)

Frontend Flutter multiplataforma per a la plataforma de gestió de festivals de cinema.

## Stack tecnològic

- **Framework**: Flutter (Material 3, color dinàmic, mode fosc)
- **Estat**: Singletons + `setState()` + Streams (NO Provider, NO flutter_it, NO riverpod)
- **Emmagatzematge local**: Hive, SharedPreferences
- **i18n**: tots els idiomes (en, es, fr, de, it, ca, eu, gl, oc) — `AppLocalizations` manual (sense gen-l10n)
- **Accessibilitat**: widgets Semantics, suport TalkBack/VoiceOver, WCAG 2.1 AA
- **Arquitectura**: Services / Managers / Views (Arquitectura Flutter Pragmàtica)

## Inici ràpid

```bash
cd frontend
flutter pub get
flutter run -d web-server --web-port 3000
```

## Scripts

Consulta `../start.ps1` per als llançadors amb flags `--dev`, `--final`, `--web`.

## Arquitectura

```
lib/
├── screens/           # pantalles UI
│   ├── auth/          # Login
│   ├── festivals/     # Llista, perfil, crear festival
│   ├── users/         # Perfil, directori, crear usuari, rols
│   ├── shortfilms/    # Llista, perfil, crear curtmetratge
│   ├── chat/          # Xat, canals, crear canal
│   ├── events/        # Gestió i detall d'esdeveniments, seients/reserves
│   ├── awards/        # Palmarés
│   ├── notifications/ # Centre de notificacions
│   ├── locations/     # Mapa, detall de localització
│   ├── forms/         # Formularis de registre, editor de pàgines, respostes, formularis públics
│   ├── admin/         # Panell d'administració
│   ├── committees/    # Comitès
│   └── settings/      # Configuració del backend, membre del directori, tauler
├── services/          # serveis + api/ + chat_backend
│   ├── api_service.dart              # Fachada + nucli (auth, transport, admin, cerca)
│   ├── api/                          # Mètodes per domini (part of api_service.dart)
│   │   ├── user_api.dart, festival_api.dart, channel_api.dart, form_api.dart
│   │   ├── calendar_api.dart, catalog_api.dart, org_api.dart
│   │   ├── event_api.dart, location_api.dart
│   ├── auth_service.dart             # JWT, persistència de sessió
│   ├── backend_config.dart           # URL del backend (desada > dart-define > predeterminat per plataforma)
│   ├── channel_service.dart          # Canals de xat + claus E2EE
│   ├── connectivity_monitor.dart     # Detecció en línia/fora de línia
│   ├── crypto_utils.dart             # E2EE (ECDH P-256, AES-GCM) + compressió, amb isolates async
│   ├── database_service.dart         # Inicialització de Hive + adaptadors de tipus
│   ├── file_downloader.dart          # Descàrrega nativa (condicional web/io)
│   ├── locale_service.dart           # Persistència d'idioma (SharedPreferences)
│   ├── notification_service.dart     # Recordatoris: plugin a l'escriptori, Notification API al web, no-op al mòbil
│   ├── notification_platform.dart    # Export condicional web/stub (sense Firebase)
│   ├── offline_cache_service.dart    # Caixes Hive (festivals, users, shortfilms, messages)
│   ├── sync_queue_service.dart       # Cua offline amb retry + backoff (màx. 3 intents)
│   └── chat_backend/                 # Abstracció WS + REST del xat
│       ├── abstract_chat_backend.dart
│       ├── chat_service.dart         # Fachada WS/REST/E2EE
│       ├── rest_chat_backend.dart    # Historial/sync via REST (fet servir com a fake en tests)
│       └── websocket_chat_backend.dart  # Temps real via WebSocket
├── models/            # Models Dart (fromJson/toJson manuals + codegen Hive)
├── widgets/           # widgets reutilitzables accessibles
│   ├── reusable_widgets.dart     # ProfileAvatar, InfoRow, StatusIndicator, ListItemCard, SemanticHeader, SemanticTextField + showAppSnack
│   ├── agenda_calendar_widget.dart
│   ├── chat_bubble.dart          # Bombolla de missatge + contingut enriquit
│   ├── chat_input_bar.dart       # Barra d'entrada del xat
│   ├── confirm_dialog.dart       # Diàleg de confirmació accessible
│   ├── dav_subscription_section.dart
│   ├── emoji_picker.dart         # Selector d'emojis en bottom sheet
│   ├── empty_state_widget.dart   # Estat buit accessible
│   ├── error_state_widget.dart   # Estat d'error amb reintent
│   ├── event_visibility_picker.dart
│   ├── festival_sections.dart    # Seccions de bases i localitzacions del festival
│   ├── film_location_card.dart   # Targeta de rodatge en localització
│   ├── language_picker.dart
│   ├── list_item_animation.dart  # Animació d'entrada de files
│   ├── loading_skeleton.dart     # Skeleton de càrrega (shimmer)
│   ├── location_badge_chip.dart  # Xip amb localització
│   ├── location_cards.dart       # LocationCard, LegacyCard, LocationFormScreen
│   ├── location_selector.dart    # Selector de localitzacions
│   ├── location_tag_editor.dart  # Editor d'etiquetes de localització
│   ├── login_prompt_sheet.dart
│   ├── map_picker.dart           # Mapa de selecció de punt
│   ├── open_in_maps_action.dart
│   ├── seat_map_widget.dart      # Mapa de seients interactiu
│   └── user_profile_cards.dart   # SessionsCard, AliasesCard
├── l10n/              # AppLocalizations + ARB
├── main.dart          # Punt d'entrada, tema Material 3, ordre d'init de serveis
├── main_scaffold.dart # NavigationRail (>800px) / NavigationBar (<800px) + Drawer
└── auth_wrapper.dart  # Porta d'autenticació (splash → login / home)
```

## Ordre d'inicialització de serveis (main.dart)

```dart
await DatabaseService.init();           // Caixes Hive
await OfflineCacheService.init();       // Carrega dades en caché
await SyncQueueService.init();          // Mutacions pendents
await NodeService.init();               // Configuració del node
await ConnectivityMonitor.start();      // Comença a escoltar la xarxa
await LocaleService.load();             // Carrega el locale desat
// Després runApp()
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
- Nucli més `services/api/`; `resolveMediaUrl()` anteposa el node actiu a les rutes `/uploads/...`; `uploadFile()` fa servir MIME per extensió, Bearer, reintent 401/refresh i fallback entre nodes; el WS del xat deriva la seva URL del mateix `rootUrl`
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
6. **Procedència de node**: la caché Hive etiqueta cada entrada per node (`putWithOrigin`, `getOrigin`, `getEnvelope`, `listOrigins`, `clearOrigin`, `reconcile`); `ConnectivityMonitor` exposa `NodeHealth`, `offlineNodeCount` i `isDegraded`, i `DegradedNodesBanner` mostra els nodes sense resposta amb recompte i reintent (`checkNow()`)

## Internacionalització (i18n)

- **tots els locals**: en, es, fr, de, it, ca, eu, gl, oc (paritat verificada amb `test/l10n/arb_parity_test.dart`)
- **Implementació manual**: `lib/l10n/app_localizations.dart` (sense gen-l10n)
- **Fitxers ARB**: `assets/l10n/app_<locale>.arb`
- **Auto-detecció**: `LocaleService.load()` llegeix el locale del sistema, amb fallback a `en` i desa el resolt
- **Delegat**: `AppLocalizations.of(context)` (delegate manual, sense gen-l10n)

### Afegir traduccions

1. Afegeix la clau a `assets/l10n/app_en.arb`
2. Replica-la a tots els altres `.arb`
3. Utilitza-la en Dart: `AppLocalizations.of(context)!.yourKey`

### Claus niades (rols, validació)

```json
"roles": { "admin": "Administrador", "organizer": "Organizador" }
```
```dart
AppLocalizations.of(context)!.roles['admin']
```

## Accessibilitat (WCAG 2.1 AA)

| Patró | Ús |
|---------|-------|
| `Semantics` | Instàncies per a lectors de pantalla |
| `SemanticHeader` | Capçaleres de secció (`header: true`) |
| `SemanticTextField` | Camps de formulari amb semàntica de validació |
| `ExcludeSemantics` | Icones decoratives |
| `Tooltip` | Elements interactius |
| `SnackBarBehavior.floating` | Snackbars |
| `autovalidateMode: onUserInteraction` | Formularis |
| `TextInputAction.next/done` + `onSubmitted` | Navegació per teclat |

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
- **Temes de componentes**: Card, AppBar, NavigationBar/Rail, InputDecoration, FilledButton, ElevatedButton, TextButton, SnackBar, Dialog, BottomSheet, Chip, ListTile, Drawer, PopupMenu, Scrollbar, Slider, Divider, FAB
- **Transicions de pàgina Cupertino** en iOS/macOS
- **Imports d'UI**: des de Flutter 3.50+ els imports d'UI viuen a `package:material_ui/material_ui.dart` i `package:cupertino_ui/cupertino_ui.dart`; els delegats de localització provenen de `GlobalMaterialLocalizations.delegates` (sense `flutter_localizations`). No s'usa `package:flutter/material.dart` excepte el pont puntual de `table_calendar` a `lib/widgets/agenda_calendar_widget.dart`.

## Xat (E2EE)

- **Backend dual**: WebSocket (temps real) + REST (historial/sync)
- **E2EE**: intercanvi de claus X25519 (pointycastle), xifrat de missatges AES-GCM
- **Emmagatzematge de claus**: model `UserKey` (clau pública en backend, privada en Hive)
- **Servei**: `ChatService` abstrau WS/REST/E2EE
- **Presència**: `ChatPresenceBackend` aporta escriptura, latència i confirmacions de lectura; cerca local, dedup i ordre per `(created_at,id)`, amb missatges offline encuats de forma duradera amb el mateix `message_id`

## Mapes i localització

- `flutter_map` + `latlong2` + `geolocator`
- Tesel·les d'OpenStreetMap (proveïdor de tesel·les cancel·lable)
- `url_launcher` per a apps de mapes natives (Google Maps, Apple Maps, Maps.me)

## Build

```bash
# Web
flutter build web --dart-define=BACKEND_URL=https://api.clakettes.com/api

# Escriptori
flutter build windows
flutter build linux
flutter build macos

# Mòbil
flutter build apk        # APK Android
flutter build appbundle  # AAB Android (Play Store)
flutter build ios        # iOS (requereix macOS + Xcode)
```

## Dependències (clau)

| Paquet | Propòsit |
|---------|-----------|
| `http` | Client REST API |
| `hive_flutter` | Caché offline |
| `shared_preferences` | Persistència de locale i token d'auth |
| `connectivity_plus` | Detecció de xarxa |
| `web_socket_channel` | Xat en temps real |
| `pointycastle` | E2EE X25519/AES-GCM |
| `flutter_map` + `latlong2` | Mapes |
| `geolocator` | GPS |
| `flutter_local_notifications` | Notificacions locals |
| `url_launcher` | Enllaços externs (mapes, web) |
| `uuid` | IDs del costat del client |

## Generació de codi (Hive)

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

Genera `*_adapter.dart` per als models anotats amb `@HiveType`.

## Testing

```bash
# Tests unitaris + de widgets
flutter test

# Tests d'integració (requereix dispositiu/emulador)
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
│   ├── l10n/                # ARB
│   └── images/              # Logos, placeholders
├── lib/
│   ├── l10n/                # app_localizations.dart (manual)
│   ├── models/              # Models Dart (Hive + codegen)
│   ├── screens/             # pantalles
│   ├── widgets/             # widgets reutilitzables
│   ├── services/            # serveis + api/ + chat_backend
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
.\build.ps1 -Target all      # Totes les plataformes
.\build.ps1 -Target web      # Només web
```

Dockerfile multi-etapa:
- **dev**: `flutter run -d web-server --web-port 3000`
- **prod**: `flutter build web` → servit estàtic amb nginx

## Variables d'entorn

| Variable | Descripció | Default |
|----------|-------------|---------|
| `BACKEND_URL` | URL base de l'API (via `--dart-define`) | `http://localhost:8000/api` |
| `CHROME_EXECUTABLE` | Navegador per a `flutter run -d chrome` | Detectat automàticament (Brave/Chrome) |

## Solució de problemes

| Problema | Solució |
|----------|----------|
| `flutter pub get` falla | Esborra `.dart_tool`, `pubspec.lock` i repeteix |
| Conflictes de tipus Hive | `flutter pub run build_runner build --delete-conflicting-outputs` |
| Fallada de connexió WebSocket | Comprova `BACKEND_URL`; assegura't que el backend exposa `/ws/chat` |
| L'idioma no persisteix | Neteja `SharedPreferences`, comprova `LocaleService.load()` | |
| El mode fosc no s'aplica | Assegura't de `ThemeMode.system` o `ThemeMode.dark` explícit a `MaterialApp` | |

## Contribuir

1. Segueix els patrons existents (singletons, `setState`, streams)
2. Afegeix `Semantics` als nous widgets interactius
3. Afegeix traduccions als fitxers ARB
4. Executa `flutter analyze` i `flutter test` abans del PR
5. Commits convencionals: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`

## Llicència

MIT — Consulta [LICENSE](../LICENSE) en l'arrel.
