# Clakettes — Frontend-a

[ES](README.md) · [EN](README.en.md) · [FR](README.fr.md) · [DE](README.de.md) · [IT](README.it.md) · [CA](README.ca.md) · [EU](README.eu.md) · [GL](README.gl.md) · [OC](README.oc.md)

Zine-jaialdien kudeaketa plataformarako Flutter frontend multiplataforma.

## Pila teknologikoa

- **Framework-a**: Flutter (Material 3, kolore dinamikoa, modu iluna)
- **Egoera**: Singleton-ak + `setState()` + Stream-ak (EZ Provider, EZ flutter_it, EZ riverpod)
- **Tokiko biltegiratzea**: Hive, SharedPreferences
- **i18n**: 9 hizkuntza (en, es, fr, de, it, ca, eu, gl, oc) — `AppLocalizations` manuala (gen-l10n gabe)
- **Irisgarritasuna**: Semantics widget, TalkBack/VoiceOver euskarria, WCAG 2.1 AA
- **Arkitektura**: Services / Managers / Views (Flutter Arkitektura Pragmatikoa)

## Hasiera azkarra

```bash
cd frontend
flutter pub get
flutter run -d web-server --web-port 3000
```

## Script-ak

Kontsultatu `../start.ps1` abiarazleetarako `--dev`, `--final`, `--web` flag-ekin.

## Arkitektura

```
lib/
├── screens/           # UI pantailak
│   ├── auth/          # Login
│   ├── festivals/     # Zerrenda, profila, sortu jaialdia
│   ├── users/         # Profila, direktorioa, sortu erabiltzailea, rolak
│   ├── shortfilms/    # Zerrenda, profila, sortu laburmetraia
│   ├── chat/          # Txata, kanalak, sortu kanala
│   ├── events/        # Ekitaldien kudeaketa eta xehetasuna, eserlekuak/erreserbak
│   ├── awards/        # Palmarés
│   ├── notifications/ # Jakinarazpen-zentroa
│   ├── locations/     # Mapa, kokapenaren xehetasuna
│   ├── forms/         # Izen-emate formularioak, orri-editorea, erantzunak, formulario publikoak
│   ├── admin/         # Administrazio-panela
│   ├── committees/    # Batzordeak
│   └── settings/      # Backendaren konfigurazioa, direktorioko kidea, panela
├── services/          # 17 zerbitzu + api/ (13 domeinu) + chat_backend (4 klase)
│   ├── api_service.dart              # Fatxada + nukleoa (auth, garraioa, admin, bilaketa)
│   ├── api/                          # Domeinuko metodoak (api_service.dart-en partea)
│   │   ├── user_api.dart, festival_api.dart, channel_api.dart, form_api.dart
│   │   ├── calendar_api.dart, catalog_api.dart, org_api.dart
│   │   ├── event_api.dart, location_api.dart
│   ├── auth_service.dart             # JWT, saioaren iraunkortasuna
│   ├── backend_config.dart           # Backendaren URLa (gordeta > dart-define > plataformaren lehenetsia)
│   ├── channel_service.dart          # Txat-kanalak + E2EE giltzak
│   ├── connectivity_monitor.dart     # Online/offline detekzioa
│   ├── crypto_utils.dart             # E2EE (ECDH P-256, AES-GCM) + konpresioa, isolate asynkoekin
│   ├── database_service.dart         # Hive-aren hasieratzea + mota-egokitzaileak
│   ├── file_downloader.dart          # Deskarga natiboa (web/io baldintzatuta)
│   ├── locale_service.dart           # Hizkuntzaren iraunkortasuna (SharedPreferences)
│   ├── notification_service.dart     # Gogorarazleak: plugin mahaigainean, Notification API webean, no-op mugikorrean
│   ├── notification_platform.dart    # Web/stub esportazio baldintzatua (Firebase gabe)
│   ├── offline_cache_service.dart    # Hive kutxak (festivals, users, shortfilms, messages)
│   ├── sync_queue_service.dart       # Linea offline retry + backoff-ekin (gehienez 3 saiakera)
│   └── chat_backend/                 # Txataren WS + REST abstrakzioa
│       ├── abstract_chat_backend.dart
│       ├── chat_service.dart         # WS/REST/E2EE fatxada
│       ├── rest_chat_backend.dart    # Historia/sync REST bidez (testetan fake gisa erabilia)
│       └── websocket_chat_backend.dart  # Denbora erreala WebSocket bidez
├── models/            # 24 Dart ereduak (eskuzko fromJson/toJson + Hive codegen)
├── widgets/           # 33 widget berrerabilgarri irisgarriak
│   ├── reusable_widgets.dart     # ProfileAvatar, InfoRow, StatusIndicator, ListItemCard, SemanticHeader, SemanticTextField + showAppSnack
│   ├── agenda_calendar_widget.dart
│   ├── chat_bubble.dart          # Mezu-burbuila + eduki aberatsa
│   ├── chat_input_bar.dart       # Txataren sarrera-barra
│   ├── confirm_dialog.dart       # Berrespen-elkarrizketa irisgarria
│   ├── dav_subscription_section.dart
│   ├── emoji_picker.dart         # Emoji-hautatzailea bottom sheet-ean
│   ├── empty_state_widget.dart   # Egoera hutsa irisgarria
│   ├── error_state_widget.dart   # Errore-egoera birsaioarekin
│   ├── event_visibility_picker.dart
│   ├── festival_sections.dart    # Jaialdiaren arau eta kokapen atalak
│   ├── film_location_card.dart   # Errodaje-kokapenaren txartela
│   ├── language_picker.dart
│   ├── list_item_animation.dart  # Lerroen sarrera-animazioa
│   ├── loading_skeleton.dart     # Karga-skeletona (shimmer)
│   ├── location_badge_chip.dart  # Kokapen-txipa
│   ├── location_cards.dart       # LocationCard, LegacyCard, LocationFormScreen
│   ├── location_selector.dart    # Kokapen-hautatzailea
│   ├── location_tag_editor.dart  # Kokapen-etiketen editorea
│   ├── login_prompt_sheet.dart
│   ├── map_picker.dart           # Puntu-hautapeko mapa
│   ├── open_in_maps_action.dart
│   ├── seat_map_widget.dart      # Eserleku-mapa interaktiboa
│   └── user_profile_cards.dart   # SessionsCard, AliasesCard
├── l10n/              # AppLocalizations + 9 ARB
├── main.dart          # Sarrera-puntua, Material 3 gaia, zerbitzuen hasieratze-ordena
├── main_scaffold.dart # NavigationRail (>800px) / NavigationBar (<800px) + Drawer
└── auth_wrapper.dart  # Autentifikazio-atea (splash → login / home)
```

## Zerbitzuen hasieratze-ordena (main.dart)

```dart
await DatabaseService.init();           // Hive kutxak
await OfflineCacheService.init();       // Kargatu cacheko datuak
await SyncQueueService.init();          // Zain dauden mutazioak
await NodeService().load();             // Nodo federatuen zerrenda kargatu
await ConnectivityMonitor.start();      // Sarea entuten hasi
await LocaleService.load();             // Gordetako hizkuntza kargatu
// Ondoren runApp()
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
6. **Nodo-jatorria**: Hive cache-ak nodo bakoitzaren jatorria gordetzen du; `reconcile`-k berriro konektatzean batzen du eta `clearOrigin`-ek nodo bat baztertzen du. Nodo batzuek erantzuten ez badute baina nagusiak bai, `DegradedNodesBanner` agertzen da kopuruarekin eta birkargatzeko botoiarekin.

## Internazionalizazioa (i18n)

- **9 locale**: en, es, fr, de, it, ca, eu, gl, oc (823 gako hizkuntzako, paritatea `test/l10n/arb_parity_test.dart`-ekin egiaztatuta)
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

| Eredua | Erabilera |
|---------|-------|
| `Semantics` | pantaila-irakurgailuentzako instantziak |
| `SemanticHeader` | Atal-buruak (`header: true`) |
| `SemanticTextField` | Balioztatze-semantikadun formulario-eremuak |
| `ExcludeSemantics` | ikono dekoratiboak |
| `Tooltip` | elementu interaktiboak |
| `SnackBarBehavior.floating` | snackbars |
| `autovalidateMode: onUserInteraction` | Formularioak |
| `TextInputAction.next/done` + `onSubmitted` | Teklatuzko nabigazioa |

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

# Mahaigaina
flutter build windows
flutter build linux
flutter build macos

# Mugikorra
flutter build apk        # APK Android
flutter build appbundle  # AAB Android (Play Store)
flutter build ios        # iOS (macOS + Xcode behar ditu)
```

## Mendekotasunak (giltzarriak)

| Paketea | Helburua |
|---------|-----------|
| `http` | REST API bezeroa |
| `hive_flutter` | Cache offline |
| `shared_preferences` | Locale eta auth tokenaren iraunkortasuna |
| `connectivity_plus` | Sare-detekzioa |
| `web_socket_channel` | Denbora errealeko txata |
| `pointycastle` | E2EE X25519/AES-GCM |
| `flutter_map` + `latlong2` | Mapak |
| `geolocator` | GPS |
| `flutter_local_notifications` | Jakinarazpen lokalak |
| `url_launcher` | Kanpo-estekak (mapak, web) |
| `uuid` | Bezero-aldeko IDak |

## Kode-sorkuntza (Hive)

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

` *_adapter.dart` sortzen du `@HiveType`-dun modeloetarako.

## Testing-a

```bash
# Unit + widget testak
flutter test

# Integrazio-testak (gailua/emuladorea behar da)
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
│   ├── l10n/                # 9 ARB fitxategi
│   └── images/              # Logos, placeholders
├── lib/
│   ├── l10n/                # app_localizations.dart (manual)
│   ├── models/              # Dart ereduak (Hive + codegen)
│   ├── screens/             # pantailak
│   ├── widgets/             # widget berrerabilgarriak
│   ├── services/            # zerbitzuak + api/ + chat_backend
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
.\build.ps1 -Target all      # Plataforma guztiak
.\build.ps1 -Target web      # Web soilik
```

Dockerfile multi-etapa:
- **dev**: `flutter run -d web-server --web-port 3000`
- **prod**: `flutter build web` → estático zerbitzatuta nginx-ekin

## Ingurune-aldagaiak

| Aldagaia | Deskribapena | Lehenetsia |
|----------|-------------|---------|
| `BACKEND_URL` | APIaren oinarrizko URLa (`--dart-define` bidez) | `http://localhost:8000/api` |
| `CHROME_EXECUTABLE` | `flutter run -d chrome`-rako nabigatzailea | Automatikoki detektatuta (Brave/Chrome) |

## Arazoen konponbidea

| Arazoa | Irtenbidea |
|----------|----------|
| `flutter pub get` huts egiten du | Ezabatu `.dart_tool`, `pubspec.lock` eta saiatu berriro |
| Hive moten gatazkak | `flutter pub run build_runner build --delete-conflicting-outputs` |
| WebSocket konexio-errorea | Egiaztatu `BACKEND_URL`; ziurtatu backend-ek `/ws/chat` erakusten duela |
| Hizkuntzak ez du irauten | Garbitu `SharedPreferences`, egiaztatu `LocaleService.load()` |
| Modu iluna aplikatzen ez bada | Ziurtatu `ThemeMode.system` edo `ThemeMode.dark` esplizitua `MaterialApp`-en |

## Laguntzea

1. Jarraitu existitzen diren ereduak (singleton-ak, `setState`, stream-ak)
2. Gehitu `Semantics` widget interaktibo berriei
3. Gehitu itzulpenak 9 ARB fitxategietara
4. Exekutatu `flutter analyze` eta `flutter test` PR aurretik
5. Commit konbentzionalak: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`

## Lizentzia

MIT — Kontsultatu [LICENSE](../LICENSE) erroan.
