# Clakettes — Frontend

[ES](README.md) · [EN](README.en.md) · [FR](README.fr.md) · [DE](README.de.md) · [IT](README.it.md) · [CA](README.ca.md) · [EU](README.eu.md) · [GL](README.gl.md) · [OC](README.oc.md)

Frontend Flutter multipiattaforma per la piattaforma di gestione dei festival cinematografici.

## Stack tecnologico

- **Framework**: Flutter (Material 3, color dinámico, modo oscuro)
- **Estado**: Singletons + `setState()` + Streams (NO Provider, NO flutter_it, NO riverpod)
- **Almacenamiento local**: Hive, SharedPreferences
- **i18n**: 9 idiomas (en, es, fr, de, it, ca, eu, gl, oc) — `AppLocalizations` manual (sin gen-l10n)
- **Accesibilidad**: widgets Semantics, soporte TalkBack/VoiceOver, WCAG 2.1 AA
- **Arquitectura**: Services / Managers / Views (Arquitectura Flutter Pragmática)

## Avvio rapido

```bash
cd frontend
flutter pub get
flutter run -d web-server --web-port 3000
```

## Script

Consulta `../start.ps1` para los lanzadores con flags `--dev`, `--final`, `--web`.

## Architettura

```
lib/
├── screens/           # schermate UI
│   ├── auth/          # Login
│   ├── festivals/     # Elenco, profilo, crea festival
│   ├── users/         # Profilo, directory, crea utente, ruoli
│   ├── shortfilms/    # Elenco, profilo, crea cortometraggio
│   ├── chat/          # Chat, canali, crea canale
│   ├── events/        # Gestione e dettaglio eventi, posti/prenotazioni
│   ├── awards/        # Palmarés
│   ├── notifications/ # Centro notifiche
│   ├── locations/     # Mappa, dettaglio località
│   ├── forms/         # Form di registrazione, editor di pagine, risposte, form pubblici
│   ├── admin/         # Pannello di amministrazione
│   ├── committees/    # Comitati
│   └── settings/      # Configurazione backend, membro della directory, dashboard
├── services/          # servizi + api/ + chat_backend
│   ├── api_service.dart              # Facciata + nucleo (auth, trasporto, admin, ricerca)
│   ├── api/                          # Metodi per dominio (part of api_service.dart)
│   │   ├── user_api.dart, festival_api.dart, channel_api.dart, form_api.dart
│   │   ├── calendar_api.dart, catalog_api.dart, org_api.dart
│   │   ├── event_api.dart, location_api.dart
│   ├── auth_service.dart             # JWT, persistenza della sessione
│   ├── backend_config.dart           # URL del backend (salvata > dart-define > predefinito per piattaforma)
│   ├── channel_service.dart          # Canali chat + chiavi E2EE
│   ├── connectivity_monitor.dart     # Rilevamento online/offline
│   ├── crypto_utils.dart             # E2EE (ECDH P-256, AES-GCM) + compressione, con isolate async
│   ├── database_service.dart         # Inizializzazione Hive + adattatori di tipo
│   ├── file_downloader.dart          # Download nativo (condizionale web/io)
│   ├── locale_service.dart           # Persistenza della lingua (SharedPreferences)
│   ├── notification_service.dart     # Promemoria: plugin su desktop, Notification API sul web, no-op su mobile
│   ├── notification_platform.dart    # Export condizionale web/stub (senza Firebase)
│   ├── offline_cache_service.dart    # Box Hive (festivals, users, shortfilms, messages)
│   ├── sync_queue_service.dart       # Coda offline con retry + backoff (max 3 tentativi)
│   └── chat_backend/                 # Astrazione WS + REST della chat
│       ├── abstract_chat_backend.dart
│       ├── chat_service.dart         # Facciata WS/REST/E2EE
│       ├── rest_chat_backend.dart    # Cronologia/sync via REST (usato come fake nei test)
│       └── websocket_chat_backend.dart  # Tempo reale via WebSocket
├── models/            # Modelli Dart (fromJson/toJson manuale + codegen Hive)
├── widgets/           # widget riutilizzabili accessibili
│   ├── reusable_widgets.dart     # ProfileAvatar, InfoRow, StatusIndicator, ListItemCard, SemanticHeader, SemanticTextField + showAppSnack
│   ├── agenda_calendar_widget.dart
│   ├── chat_bubble.dart          # Bolla messaggio + contenuto ricco
│   ├── chat_input_bar.dart       # Barra di input della chat
│   ├── confirm_dialog.dart       # Dialogo di conferma accessibile
│   ├── dav_subscription_section.dart
│   ├── emoji_picker.dart         # Selettore emoji nel bottom sheet
│   ├── empty_state_widget.dart   # Stato vuoto accessibile
│   ├── error_state_widget.dart   # Stato di errore con ripetizione
│   ├── event_visibility_picker.dart
│   ├── festival_sections.dart    # Sezioni regolamenti e località del festival
│   ├── film_location_card.dart   # Carta della location di ripresa
│   ├── language_picker.dart
│   ├── list_item_animation.dart  # Animazione di ingresso delle righe
│   ├── loading_skeleton.dart     # Skeleton di caricamento (shimmer)
│   ├── location_badge_chip.dart  # Chip con località
│   ├── location_cards.dart       # LocationCard, LegacyCard, LocationFormScreen
│   ├── location_selector.dart    # Selettore di località
│   ├── location_tag_editor.dart  # Editor di tag della località
│   ├── login_prompt_sheet.dart
│   ├── map_picker.dart           # Mappa di selezione punto
│   ├── open_in_maps_action.dart
│   ├── seat_map_widget.dart      # Mappa posti interattiva
│   └── user_profile_cards.dart   # SessionsCard, AliasesCard
├── l10n/              # AppLocalizations + 9 ARB
├── main.dart          # Punto d'ingresso, tema Material 3, ordine di init dei servizi
├── main_scaffold.dart # NavigationRail (>800px) / NavigationBar (<800px) + Drawer
└── auth_wrapper.dart  # Gate di autenticazione (splash → login / home)
```

## Ordine di inizializzazione dei servizi (main.dart)

```dart
await DatabaseService.init();           // Box Hive
await OfflineCacheService.init();       // Carica i dati in cache
await SyncQueueService.init();          // Mutazioni in attesa
await ConnectivityMonitor.start();      // Inizia ad ascoltare la rete
await LocaleService.load();             // Carica la lingua salvata
// Poi runApp()
```

## Pattern di gestione dello stato

**Singleton + setState + Streams** — Senza Provider, senza flutter_it, senza Bloc.

- I servizi sono singleton (inizializzati pigramente in `main.dart`)
- La UI usa `StatefulWidget` + `setState()` per lo stato locale
- I servizi espongono Streams per aggiornamenti reattivi (connettività, auth, sync)
- `ChangeNotifier` si usa puntualmente (AuthService, LocaleService) per widget `Consumer`

## Servizio di API

`ApiService` (singleton) — URL base vía `--dart-define=BACKEND_URL=http://localhost:8000/api`

- Allega il JWT automaticamente (da AuthService)
- Refresh automatico del token in 401
- Integrazione con la coda offline (SyncQueueService)
- Metodi: `get`, `post`, `put`, `patch`, `delete`, `upload`

```dart
final api = ApiService();
final festivals = await api.get('/festivals/', query: {'page': '1', 'size': '20'});
```

## Architettura offline-first

1. **Cajas Hive**: `festivals`, `users`, `shortfilms`, `messages` (+ eventos, premios, etc. según modelo)
2. **Lettura**: la UI legge prima da Hive e sincronizza dall'API in secondo piano
3. **Scrittura**: le mutazioni si accodano in `SyncQueueService` (firmate con HMAC)
4. **Sync**: al recupero della connettività, `SyncQueueService` riproduce la coda in sequenza
5. **Risoluzione dei conflitti**: vince il server (last-write-wins con timestamp)

## Internazionalizzazione (i18n)

- **9 locali**: en, es, fr, de, it, ca, eu, gl, oc (823 chiavi per ARB, parità verificata con `test/l10n/arb_parity_test.dart`)
- **Implementazione manuale**: `lib/l10n/app_localizations.dart` (sin gen-l10n)
- **File ARB**: `assets/l10n/app_<locale>.arb`
- **Auto-rilevamento**: `LocaleService` legge la lingua del sistema, con fallback a `en`
- **Delegato**: `AppLocalizations.of(context)` (delegate manual, sin gen-l10n)

### Aggiungere traduzioni

1. Aggiungi la chiave a `assets/l10n/app_en.arb`
2. Replicala negli altri 8 `.arb`
3. Usala in Dart: `AppLocalizations.of(context)!.yourKey`

### Chiavi annidate (ruoli, validazione)

```json
"roles": { "admin": "Administrador", "organizer": "Organizador" }
```
```dart
AppLocalizations.of(context)!.roles['admin']
```

## Accessibilità (WCAG 2.1 AA)

| Pattern | Uso |
|---------|-------|
| `Semantics` | istanze per lettori di schermo |
| `SemanticHeader` | Intestazioni di sezione (`header: true`) |
| `SemanticTextField` | Campi di form con semantica di validazione |
| `ExcludeSemantics` | icone decorative |
| `Tooltip` | elementi interattivi |
| `SnackBarBehavior.floating` | snackbars |
| `autovalidateMode: onUserInteraction` | Form |
| `TextInputAction.next/done` + `onSubmitted` | Navigazione da tastiera |

### Widget riutilizzabili accessibili

```dart
// lib/widgets/reusable_widgets.dart
ProfileAvatar(avatarUrl, name, radius: 24)
InfoRow(label: 'Email', value: email, icon: Icons.email)
StatusIndicator(isActive: true, label: 'Activo')
ListItemCard(title: 'Festival', subtitle: 'Madrid', onTap: () {})
SemanticHeader('Festivales', level: 1)
SemanticTextField(label: 'Email', validator: emailValidator)
```

## Navigazione responsive

- **>800px di larghezza**: `NavigationRail` (barra laterale)
- **≤800px di larghezza**: `NavigationBar` (barra inferiore)
- Implementato in `MainScaffold` con `LayoutBuilder` + Drawer in tutte le dimensioni

## Tema (Material 3)

- **Colore seme**: `#B8956E` (arena dorada)
- **Modalità scura**: supporto completo vía `_baseTheme(ColorScheme)`
- **temi di componenti**: Card, AppBar, NavigationBar/Rail, InputDecoration, FilledButton, ElevatedButton, TextButton, SnackBar, Dialog, BottomSheet, Chip, ListTile, Drawer, PopupMenu, Scrollbar, Slider, Divider, FAB
- **Transizioni di pagina Cupertino** in iOS/macOS

## Chat (E2EE)

- **Backend duale**: WebSocket (tempo reale) + REST (historial/sync)
- **E2EE**: scambio di chiavi X25519 (pointycastle), cifratura dei messaggi AES-GCM
- **Memorizzazione delle chiavi**: modello `UserKey` (chiave pubblica nel backend, privata in Hive)
- **Servizio**: `ChatService` astrae WS/REST/E2EE

## Mappe e localizzazione

- `flutter_map` + `latlong2` + `geolocator`
- Tessere di OpenStreetMap (provider di tessere cancellabile)
- `url_launcher` per app di mappe native (Google Maps, Apple Maps, Maps.me)

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
flutter build ios        # iOS (richiede macOS + Xcode)
```

## Dipendenze (chiave)

| Pacchetto | Scopo |
|---------|-----------|
| `http` | Client REST API |
| `hive_flutter` | Cache offline |
| `shared_preferences` | Persistenza di locale e token di auth |
| `connectivity_plus` | Rilevamento rete |
| `web_socket_channel` | Chat in tempo reale |
| `pointycastle` | E2EE X25519/AES-GCM |
| `flutter_map` + `latlong2` | Mappe |
| `geolocator` | GPS |
| `flutter_local_notifications` | Notifiche locali |
| `url_launcher` | Link esterni (mappe, web) |
| `uuid` | ID lato client |

## Generazione di codice (Hive)

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

Genera `*_adapter.dart` per i modelli annotati con `@HiveType`.

## Testing

```bash
# Test unitari + dei widget
flutter test

# Test di integrazione (richiede dispositivo/emulatore)
flutter test integration_test/
```

## Linting

```bash
flutter analyze
```

Usa `flutter_lints` (insieme raccomandato).

## Struttura della directory (ampliata)

```
frontend/
├── android/                 # Config Android
├── ios/                     # Config iOS
├── linux/                   # Config Linux
├── macos/                   # Config macOS
├── windows/                 # Config Windows
├── web/                     # Config web (index.html, manifest.json)
├── assets/
│   ├── l10n/                # file ARB
│   └── images/              # Logos, placeholders
├── lib/
│   ├── l10n/                # app_localizations.dart (manual)
│   ├── models/              # Modelli Dart (Hive + codegen)
│   ├── screens/             # schermate
│   ├── widgets/             # widget riutilizzabili
│   ├── services/            # servizi + api/ + chat_backend
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
.\build.ps1 -Target all      # Tutte le piattaforme
.\build.ps1 -Target web      # Solo web
```

Dockerfile multi-stadio:
- **dev**: `flutter run -d web-server --web-port 3000`
- **prod**: `flutter build web` → servito statico con nginx

## Variabili di ambiente

| Variabile | Descrizione | Predefinito |
|----------|-------------|---------|
| `BACKEND_URL` | URL di base dell'API (via `--dart-define`) | `http://localhost:8000/api` |
| `CHROME_EXECUTABLE` | Browser per `flutter run -d chrome` | Rilevato automaticamente (Brave/Chrome) |

## Risoluzione dei problemi

| Problema | Soluzione |
|----------|----------|
| `flutter pub get` fallisce | Elimina `.dart_tool`, `pubspec.lock` e riprova |
| Conflitti di tipi Hive | `flutter pub run build_runner build --delete-conflicting-outputs` |
| Errore di connessione WebSocket | Controlla `BACKEND_URL`; assicurati che il backend esponga `/ws/chat` |
| La lingua non persiste | Cancella `SharedPreferences`, controlla `LocaleService.load()` |
| La modalità scura non si applica | Assicurati di `ThemeMode.system` o `ThemeMode.dark` esplicito in `MaterialApp` |

## Contribuire

1. Segui i pattern esistenti (singleton, `setState`, streams)
2. Aggiungi `Semantics` ai nuovi widget interattivi
3. Aggiungi traduzioni ai 9 file ARB
4. Esegui `flutter analyze` e `flutter test` prima della PR
5. Commit convenzionali: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`

## Licenza

MIT — Consulta [LICENSE](../LICENSE) en la raíz.
