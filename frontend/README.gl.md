# Clakettes — Frontend

[ES](README.md) · [EN](README.en.md) · [FR](README.fr.md) · [DE](README.de.md) · [IT](README.it.md) · [CA](README.ca.md) · [EU](README.eu.md) · [GL](README.gl.md) · [OC](README.oc.md)

Frontend Flutter multiplataforma para a plataforma de xestión de festivais de cine.

## Stack tecnolóxico

- **Framework**: Flutter (Material 3, cor dinámica, modo escuro)
- **Estado**: Singletons + `setState()` + Streams (NO Provider, NO flutter_it, NO riverpod)
- **Almacenamento local**: Hive, SharedPreferences
- **i18n**: todos os idiomas (en, es, fr, de, it, ca, eu, gl, oc) — `AppLocalizations` manual (sen gen-l10n)
- **Accesibilidade**: Semantics, soporte TalkBack/VoiceOver, WCAG 2.1 AA
- **Arquitectura**: Services / Managers / Views (Arquitectura Flutter Pragmática)

## Inicio rápido

```bash
cd frontend
flutter pub get
flutter run -d web-server --web-port 3000
```

## Scripts

Consulta `../start.ps1` para os lanzadores con flags `--dev`, `--final`, `--web`.

## Arquitectura

```
lib/
├── screens/           # pantallas UI
│   ├── auth/          # Login
│   ├── festivals/     # Lista, perfil, crear festival
│   ├── users/         # Perfil, directorio, crear usuario, roles
│   ├── shortfilms/    # Lista, perfil, crear curtametraxe
│   ├── chat/          # Chat, canais, crear canal
│   ├── events/        # Xestión e detalle de eventos, asentos/reservas
│   ├── awards/        # Palmarés
│   ├── notifications/ # Centro de notificacións
│   ├── locations/     # Mapa, detalle de localización
│   ├── forms/         # Formularios de rexistro, editor de páxinas, respostas, formularios públicos
│   ├── admin/         # Panel de administración
│   ├── committees/    # Comités
│   └── settings/      # Configuración do backend, membro do directorio, panel
├── services/          # servizos + api/ + chat_backend
│   ├── api_service.dart              # Fachada + núcleo (auth, transporte, admin, busca)
│   ├── api/                          # Métodos por dominio (part of api_service.dart)
│   │   ├── user_api.dart, festival_api.dart, channel_api.dart, form_api.dart
│   │   ├── calendar_api.dart, catalog_api.dart, org_api.dart
│   │   ├── event_api.dart, location_api.dart
│   ├── auth_service.dart             # JWT, persistencia de sesión
│   ├── backend_config.dart           # URL do backend (gardada > dart-define > predeterminado por plataforma)
│   ├── channel_service.dart          # Canais de chat + claves E2EE
│   ├── connectivity_monitor.dart     # Detección en liña/fóra de liña
│   ├── crypto_utils.dart             # E2EE (ECDH P-256, AES-GCM) + compresión, con isolates async
│   ├── database_service.dart         # Inicialización de Hive + adaptadores de tipos
│   ├── file_downloader.dart          # Descarga nativa (condicional web/io)
│   ├── locale_service.dart           # Persistencia do idioma (SharedPreferences)
│   ├── notification_service.dart     # Recordatorios: plugin no escritorio, Notification API na web, no-op no móbil
│   ├── notification_platform.dart    # Exportación condicional web/stub (sen Firebase)
│   ├── offline_cache_service.dart    # Caixas Hive (festivals, users, shortfilms, messages)
│   ├── sync_queue_service.dart       # Cola offline con retry + backoff (máx. 3 intentos)
│   └── chat_backend/                 # Abstracción WS + REST do chat
│       ├── abstract_chat_backend.dart
│       ├── chat_service.dart         # Fachada WS/REST/E2EE
│       ├── rest_chat_backend.dart    # Historial/sync vía REST (usado como fake en probas)
│       └── websocket_chat_backend.dart  # Tempo real vía WebSocket
├── models/            # modelos Dart (manuais fromJson/toJson + Hive codegen)
├── widgets/           # widgets reutilizables accesibles
│   ├── reusable_widgets.dart     # ProfileAvatar, InfoRow, StatusIndicator, ListItemCard, SemanticHeader, SemanticTextField + showAppSnack
│   ├── agenda_calendar_widget.dart
│   ├── chat_bubble.dart          # Burbulla de mensaxe + contido enriquecido
│   ├── chat_input_bar.dart       # Barra de entrada do chat
│   ├── confirm_dialog.dart       # Diálogo de confirmación accesible
│   ├── dav_subscription_section.dart
│   ├── emoji_picker.dart         # Selector de emojis na folla inferior
│   ├── empty_state_widget.dart   # Estado baleiro accesible
│   ├── error_state_widget.dart   # Estado de error con reintento
│   ├── event_visibility_picker.dart
│   ├── festival_sections.dart    # Seccións de bases e localizacións do festival
│   ├── film_location_card.dart   # Tarxeta de rodaxe en localización
│   ├── language_picker.dart
│   ├── list_item_animation.dart  # Animación de entrada de filas
│   ├── loading_skeleton.dart     # Skeleton de carga (shimmer)
│   ├── location_badge_chip.dart  # Chip con localización
│   ├── location_cards.dart       # LocationCard, LegacyCard, LocationFormScreen
│   ├── location_selector.dart    # Selector de localizacións
│   ├── location_tag_editor.dart  # Editor de etiquetas de localización
│   ├── login_prompt_sheet.dart
│   ├── map_picker.dart           # Mapa de selección de punto
│   ├── open_in_maps_action.dart
│   ├── seat_map_widget.dart      # Mapa de asentos interactivo
│   └── user_profile_cards.dart   # SessionsCard, AliasesCard
├── l10n/              # AppLocalizations + ARB
├── main.dart          # Punto de entrada, tema Material 3, orde de init de servizos
├── main_scaffold.dart # NavigationRail (>800px) / NavigationBar (<800px) + Drawer
└── auth_wrapper.dart  # Porta de autenticación (splash → login / home)
```

## Orde de inicialización de servizos (main.dart)

```dart
await DatabaseService.init();           // Caixas Hive
await OfflineCacheService.init();       // Cargar datos na caché
await SyncQueueService.init();          // Mutacións pendentes
await NodeService.init();               // Nodos de federación
await ConnectivityMonitor.start();      // Comezar a escoitar a rede
await LocaleService.load();             // Cargar o idioma gardado
// Despois runApp()
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
5. **Procedencia**: a caché Hive etiqueta cada entrada co nodo de orixe (`putWithOrigin`, `getOrigin`, `getEnvelope`, `listOrigins`, `clearOrigin`, `reconcile`); os nodos sen resposta amósanse en `DegradedNodesBanner` e as rutas `/uploads/...` resólvense co nodo activo mediante `resolveMediaUrl()`
6. **Resolución de conflitos**: gaña o servidor (last-write-wins con timestamp)

## Internacionalización (i18n)

- **todos os locales**: en, es, fr, de, it, ca, eu, gl, oc (paridade verificada con `test/l10n/arb_parity_test.dart`)
- **Implementación manual**: `lib/l10n/app_localizations.dart` (sen gen-l10n)
- **Arquivos ARB**: `assets/l10n/app_<locale>.arb`
- **Auto-detección**: `LocaleService` le o idioma do sistema, con fallback a `en`, e persiste o locale resuelto
- **Delegado**: `AppLocalizations.of(context)` (delegate manual, sen gen-l10n)

### Engadir traducións

1. Engade a clave a `assets/l10n/app_en.arb`
2. Replícaa nos demais `.arb`
3. Úsaa en Dart: `AppLocalizations.of(context)!.yourKey`

### Claves aniñadas (roles, validación)

```json
"roles": { "admin": "Administrador", "organizer": "Organizador" }
```
```dart
AppLocalizations.of(context)!.roles['admin']
```

## Accesibilidade (WCAG 2.1 AA)

| Patrón | Utilización |
|---------|-------|
| `Semantics` | instancias para os lectores de pantalla |
| `SemanticHeader` | Cabeceiras de sección (`header: true`) |
| `SemanticTextField` | Campos de formulario con semántica de validación |
| `ExcludeSemantics` | iconas decorativas |
| `Tooltip` | elementos interactivos |
| `SnackBarBehavior.floating` | snackbars |
| `autovalidateMode: onUserInteraction` | Formularios |
| `TextInputAction.next/done` + `onSubmitted` | Navegación polo teclado |

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
- **Temas de compoñentes**: Card, AppBar, NavigationBar/Rail, InputDecoration, FilledButton, ElevatedButton, TextButton, SnackBar, Dialog, BottomSheet, Chip, ListTile, Drawer, PopupMenu, Scrollbar, Slider, Divider, FAB
- **Transicións de páxina Cupertino** en iOS/macOS
- **Imports de UI**: desde Flutter 3.50+ as imports de UI viven en `package:material_ui/material_ui.dart` e `package:cupertino_ui/cupertino_ui.dart`; os delegates de localización tómanse de `GlobalMaterialLocalizations.delegates` (sen `flutter_localizations`). Non se usa `package:flutter/material.dart` agás a ponte puntual de `table_calendar` en `lib/widgets/agenda_calendar_widget.dart`.

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

# Sobremesa
flutter build windows
flutter build linux
flutter build macos

# Móbil
flutter build apk        # APK Android
flutter build appbundle  # AAB Android (Play Store)
flutter build ios        # iOS (require macOS + Xcode)
```

## Dependencias (clave)

| Paquete | Finalidade |
|---------|-----------|
| `http` | Cliente da API REST |
| `hive_flutter` | Caché sen liña |
| `shared_preferences` | Persistencia do locale e do token de auth |
| `connectivity_plus` | Detección de rede |
| `web_socket_channel` | Chat en tempo real |
| `pointycastle` | E2EE X25519/AES-GCM |
| `flutter_map` + `latlong2` | Mapas |
| `geolocator` | GPS |
| `flutter_local_notifications` | Notificacións locais |
| `url_launcher` | Ligazóns externas (mapas, web) |
| `uuid` | IDs do lado do cliente |

## Xeración de código (Hive)

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

Xera `*_adapter.dart` para os modelos anotados con `@HiveType`.

## Testing

```bash
# Probas unitarias + de widgets
flutter test

# Probas de integración (require dispositivo/emulador)
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
│   ├── l10n/                # arquivos ARB
│   └── images/              # Logos, placeholders
├── lib/
│   ├── l10n/                # app_localizations.dart (manual)
│   ├── models/              # modelos Dart (Hive + codegen)
│   ├── screens/             # pantallas
│   ├── widgets/             # widgets reutilizables
│   ├── services/            # servizos + api/ + chat_backend
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
.\build.ps1 -Target all      # Todas as plataformas
.\build.ps1 -Target web      # Só web
```

Dockerfile multi-etapa:
- **dev**: `flutter run -d web-server --web-port 3000`
- **prod**: `flutter build web` → servido estático con nginx

## Variables de entorno

| Variable | Descrición | Predeterminado |
|----------|-------------|---------|
| `BACKEND_URL` | URL base da API (vía `--dart-define`) | `http://localhost:8000/api` |
| `CHROME_EXECUTABLE` | Navegador para `flutter run -d chrome` | Detectado automaticamente (Brave/Chrome) |

## Solución de problemas

| Problema | Resolución |
|----------|----------|
| `flutter pub get` falla | Borra `.dart_tool`, `pubspec.lock` e repite |
| Conflitos de tipos Hive | `flutter pub run build_runner build --delete-conflicting-outputs` |
| Fallo de conexión WebSocket | Comproba `BACKEND_URL`; asegúrate de que o backend expón `/ws/chat` |
| O idioma non persiste | Limpa `SharedPreferences`, comproba `LocaleService.load()` |
| O modo escuro non se aplica | Asegúrate de `ThemeMode.system` ou `ThemeMode.dark` explícito en `MaterialApp` |

## Contribuír

1. Segue os patróns existentes (singletons, `setState`, streams)
2. Engade `Semantics` aos novos widgets interactivos
3. Engade traducións a todos os arquivos ARB
4. Executa `flutter analyze` e `flutter test` antes do PR
5. Commits convencionais: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`

## Licenza

MIT — Consulta [LICENSE](../LICENSE) na raíz.
