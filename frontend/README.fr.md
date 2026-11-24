# Clakettes — Frontend

[ES](README.md) · [EN](README.en.md) · [FR](README.fr.md) · [DE](README.de.md) · [IT](README.it.md) · [CA](README.ca.md) · [EU](README.eu.md) · [GL](README.gl.md) · [OC](README.oc.md)

Frontend Flutter multiplateforme pour la plateforme de gestion de festivals de cinéma.

## Stack technologique

- **Framework** : Flutter (Material 3, couleur dynamique, mode sombre)
- **État** : Singletons + `setState()` + Streams (NO Provider, NO flutter_it, NO riverpod)
- **Stockage local** : Hive, SharedPreferences
- **i18n** : les langues de `assets/l10n/` (en, es, fr, de, it, ca, eu, gl, oc) — `AppLocalizations` manuel (sans gen-l10n)
- **Accessibilité** : widgets Semantics, support TalkBack/VoiceOver, WCAG 2.1 AA
- **Architecture** : Services / Managers / Views (Architecture Flutter Pragmatique)

## Démarrage rapide

```bash
cd frontend
flutter pub get
flutter run -d web-server --web-port 3000
```

## Scripts

Consulte `../start.ps1` pour les lanceurs avec flags `--dev`, `--final`, `--web`.

## Architecture

```
lib/
├── screens/           # écrans UI
│   ├── auth/          # Login
│   ├── festivals/     # Liste, profil, créer un festival
│   ├── users/         # Profil, annuaire, créer un utilisateur, rôles
│   ├── shortfilms/    # Liste, profil, créer un court-métrage
│   ├── chat/          # Chat, canaux, créer un canal
│   ├── events/        # Gestion et détail des événements, sièges/réservations
│   ├── awards/        # Palmarés
│   ├── notifications/ # Centre de notifications
│   ├── locations/     # Carte, détail de localisation
│   ├── forms/         # Formulaires d'inscription, éditeur de pages, réponses, formulaires publics
│   ├── admin/         # Panneau d'administration
│   ├── committees/    # Comités
│   └── settings/      # Config du backend, membre de l'annuaire, tableau de bord
├── services/          # services + api/ + chat_backend
│   ├── api_service.dart              # Façade + noyau (auth, transport, admin, recherche)
│   ├── api/                          # Méthodes par domaine (part of api_service.dart)
│   │   ├── user_api.dart, festival_api.dart, channel_api.dart, form_api.dart
│   │   ├── calendar_api.dart, catalog_api.dart, org_api.dart
│   │   ├── event_api.dart, location_api.dart
│   ├── auth_service.dart             # JWT, persistance de session
│   ├── backend_config.dart           # URL du backend (enregistrée > dart-define > défaut par plateforme)
│   ├── channel_service.dart          # Canaux de chat + clés E2EE
│   ├── connectivity_monitor.dart     # Détection en ligne/hors ligne
│   ├── crypto_utils.dart             # E2EE (ECDH P-256, AES-GCM) + compression, avec isolates async
│   ├── database_service.dart         # Init Hive + adaptateurs de types
│   ├── file_downloader.dart          # Téléchargement natif (conditionnel web/io)
│   ├── locale_service.dart           # Persistance de langue (SharedPreferences)
│   ├── notification_service.dart     # Rappels : plugin sur bureau, Notification API sur web, no-op sur mobile
│   ├── notification_platform.dart    # Export conditionnel web/stub (sans Firebase)
│   ├── offline_cache_service.dart    # Boîtes Hive (festivals, users, shortfilms, messages)
│   ├── sync_queue_service.dart       # File offline avec retry + backoff (max 3 tentatives)
│   └── chat_backend/                 # Abstraction WS + REST du chat
│       ├── abstract_chat_backend.dart
│       ├── chat_service.dart         # Façade WS/REST/E2EE
│       ├── rest_chat_backend.dart    # Historique/sync via REST (utilisé comme fake dans les tests)
│       └── websocket_chat_backend.dart  # Temps réel via WebSocket
├── models/            # Modèles Dart (fromJson/toJson manuel + codegen Hive)
├── widgets/           # widgets réutilisables accessibles
│   ├── reusable_widgets.dart     # ProfileAvatar, InfoRow, StatusIndicator, ListItemCard, SemanticHeader, SemanticTextField + showAppSnack
│   ├── agenda_calendar_widget.dart
│   ├── chat_bubble.dart          # Bulle de message + contenu riche
│   ├── chat_input_bar.dart       # Barre de saisie du chat
│   ├── confirm_dialog.dart       # Dialogue de confirmation accessible
│   ├── dav_subscription_section.dart
│   ├── emoji_picker.dart         # Sélecteur d'emoji dans une bottom sheet
│   ├── empty_state_widget.dart   # État vide accessible
│   ├── error_state_widget.dart   # État d'erreur avec réessai
│   ├── event_visibility_picker.dart
│   ├── festival_sections.dart    # Sections règlements et lieux du festival
│   ├── film_location_card.dart   # Carte de lieu de tournage
│   ├── language_picker.dart
│   ├── list_item_animation.dart  # Animation d'entrée des lignes
│   ├── loading_skeleton.dart     # Skeleton de chargement (shimmer)
│   ├── location_badge_chip.dart  # Chip de localisation
│   ├── location_cards.dart       # LocationCard, LegacyCard, LocationFormScreen
│   ├── location_selector.dart    # Sélecteur de localisation
│   ├── location_tag_editor.dart  # Éditeur d'étiquettes de localisation
│   ├── login_prompt_sheet.dart
│   ├── map_picker.dart           # Carte de sélection de point
│   ├── open_in_maps_action.dart
│   ├── seat_map_widget.dart      # Plan de sièges interactif
│   └── user_profile_cards.dart   # SessionsCard, AliasesCard
├── l10n/              # AppLocalizations + tous les ARB
├── main.dart          # Point d'entrée, thème Material 3, ordre d'init des services
├── main_scaffold.dart # NavigationRail (>800px) / NavigationBar (<800px) + Drawer
└── auth_wrapper.dart  # Porte d'authentification (splash → login / home)
```

## Ordre d'initialisation des services (main.dart)

```dart
await DatabaseService.init();           // Boîtes Hive
await OfflineCacheService.init();       // Charger les données en cache
await SyncQueueService.init();          // Mutations en attente
await ConnectivityMonitor.start();      // Commencer à écouter le réseau
await LocaleService.load();             // Charger la langue enregistrée
// Puis runApp()
```

## Motif de gestion d'état

**Singletons + setState + Streams** — Sans Provider, sans flutter_it, sans Bloc.

- Les services sont singletons (initialisés paresseusement dans `main.dart`)
- L'UI utilise `StatefulWidget` + `setState()` pour l'état local
- Les services exposent Streams pour mises à jour réactives (connectivité, auth, sync)
- `ChangeNotifier` est utilisé ponctuellement (AuthService, LocaleService) pour widgets `Consumer`

## Service d'API

`ApiService` (singleton) — URL base via `--dart-define=BACKEND_URL=http://localhost:8000/api`

- Attache le JWT automatiquement (depuis AuthService)
- Refresh automatique de token en 401
- Intégration avec la file offline (SyncQueueService)
- Méthodes : `get`, `post`, `put`, `patch`, `delete`, `upload`

```dart
final api = ApiService();
final festivals = await api.get('/festivals/', query: {'page': '1', 'size': '20'});
```

## Architecture offline-first

1. **Boîtes Hive** : `festivals`, `users`, `shortfilms`, `messages` (+ événements, prix, etc. selon modèle)
2. **Lecture** : l'UI lit d'abord de Hive et synchronise depuis l'API en arrière-plan
3. **Écriture** : les mutations sont enfilées dans `SyncQueueService` (signées avec HMAC)
4. **Sync** : en récupérant connectivité, `SyncQueueService` rejoue la file séquentiellement
5. **Résolution de conflits** : gagne le serveur (last-write-wins avec timestamp)
6. **Provenance** : le cache Hive étiquette chaque nœud (`putWithOrigin`/`getOrigin`) ; `reconcile` fusionne à la reconnexion, `clearOrigin` écarte un nœud et `DegradedNodesBanner` signale les nœuds sans réponse

## Internationalisation (i18n)

- **Locales** : en, es, fr, de, it, ca, eu, gl, oc (parité des clés vérifiée avec `test/l10n/arb_parity_test.dart`)
- **Implémentation manuelle** : `lib/l10n/app_localizations.dart` (sans gen-l10n)
- **Fichiers ARB** : `assets/l10n/app_<locale>.arb`
- **Auto-détection** : `LocaleService` lit la langue du système, avec fallback à `en`
- **Délégué** : `AppLocalizations.of(context)` (delegate manuel, sans gen-l10n)

### Ajouter traductions

1. Ajoute la clé à `assets/l10n/app_en.arb`
2. Réplique-la dans le reste des `.arb`
3. Utilise-la en Dart : `AppLocalizations.of(context)!.yourKey`

### Clés imbriquées (rôles, validation)

```json
"roles": { "admin": "Administrador", "organizer": "Organizador" }
```
```dart
AppLocalizations.of(context)!.roles['admin']
```

## Accessibilité (WCAG 2.1 AA)

| Motif | Usage |
|---------|-------|
| `Semantics` | instances pour lecteurs d'écran |
| `SemanticHeader` | En-têtes de section (`header: true`) |
| `SemanticTextField` | Champs de formulaire avec sémantique de validation |
| `ExcludeSemantics` | icônes décoratives |
| `Tooltip` | éléments interactifs |
| `SnackBarBehavior.floating` | snackbars |
| `autovalidateMode: onUserInteraction` | Formulaires |
| `TextInputAction.next/done` + `onSubmitted` | Navigation au clavier |

### Widgets réutilisables accessibles

```dart
// lib/widgets/reusable_widgets.dart
ProfileAvatar(avatarUrl, name, radius: 24)
InfoRow(label: 'Email', value: email, icon: Icons.email)
StatusIndicator(isActive: true, label: 'Activo')
ListItemCard(title: 'Festival', subtitle: 'Madrid', onTap: () {})
SemanticHeader('Festivales', level: 1)
SemanticTextField(label: 'Email', validator: emailValidator)
```

## Navigation responsive

- **>800px de large** : `NavigationRail` (barre latérale)
- **≤800px de large** : `NavigationBar` (barre inférieure)
- Implémenté dans `MainScaffold` avec `LayoutBuilder` + Drawer dans toutes les tailles

## Thème (Material 3)

- **Couleur graine** : `#B8956E` (sable doré)
- **Mode sombre** : support complet via `_baseTheme(ColorScheme)`
- **Thèmes de composants** : Card, AppBar, NavigationBar/Rail, InputDecoration, FilledButton, ElevatedButton, TextButton, SnackBar, Dialog, BottomSheet, Chip, ListTile, Drawer, PopupMenu, Scrollbar, Slider, Divider, FAB
- **Transitions de page Cupertino** sur iOS/macOS
- **Imports d'UI** : depuis Flutter 3.50+, les imports d'UI se trouvent dans `package:material_ui/material_ui.dart` et `package:cupertino_ui/cupertino_ui.dart` ; les délégués de localisation proviennent de `GlobalMaterialLocalizations.delegates` (sans `flutter_localizations`). `package:flutter/material.dart` n'est pas utilisé sauf le pont ponctuel de `table_calendar` dans `lib/widgets/agenda_calendar_widget.dart`.

## Chat (E2EE)

- **Backend dual** : WebSocket (temps réel) + REST (historique/sync)
- **E2EE** : échange de clés X25519 (pointycastle), chiffrement de messages AES-GCM
- **Stockage de clés** : modèle `UserKey` (clé publique en backend, privée en Hive)
- **Service** : `ChatService` abstrait WS/REST/E2EE

## Cartes et localisation

- `flutter_map` + `latlong2` + `geolocator`
- Tuiles OpenStreetMap (fournisseur de tuiles annulable)
- `url_launcher` pour apps de cartes natives (Google Maps, Apple Maps, Maps.me)

## Build

```bash
# Web
flutter build web --dart-define=BACKEND_URL=https://api.clakettes.com/api

# Bureau
flutter build windows
flutter build linux
flutter build macos

# Mobile
flutter build apk        # APK Android
flutter build appbundle  # AAB Android (Play Store)
flutter build ios        # iOS (nécessite macOS + Xcode)
```

## Dépendances (clé)

| Paquet | Rôle |
|---------|-----------|
| `http` | Client REST API |
| `hive_flutter` | Cache hors ligne |
| `shared_preferences` | Persistance de la locale et du token d'auth |
| `connectivity_plus` | Détection réseau |
| `web_socket_channel` | Chat en temps réel |
| `pointycastle` | E2EE X25519/AES-GCM |
| `flutter_map` + `latlong2` | Cartes |
| `geolocator` | GPS |
| `flutter_local_notifications` | Notifications locales |
| `url_launcher` | Liens externes (cartes, web) |
| `uuid` | IDs côté client |

## Génération de code (Hive)

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

Génère `*_adapter.dart` pour les modèles annotés avec `@HiveType`.

## Testing

```bash
# Tests unitaires + de widgets
flutter test

# Tests d'intégration (nécessite un appareil/émulateur)
flutter test integration_test/
```

## Linting

```bash
flutter analyze
```

Utilise `flutter_lints` (ensemble recommandé).

## Structure du répertoire (étendue)

```
frontend/
├── android/                 # Config Android
├── ios/                     # Config iOS
├── linux/                   # Config Linux
├── macos/                   # Config macOS
├── windows/                 # Config Windows
├── web/                     # Config web (index.html, manifest.json)
├── assets/
│   ├── l10n/                # fichiers ARB
│   └── images/              # Logos, placeholders
├── lib/
│   ├── l10n/                # app_localizations.dart (manual)
│   ├── models/              # Modèles Dart (Hive + codegen)
│   ├── screens/             # écrans
│   ├── widgets/             # widgets réutilisables
│   ├── services/            # services + api/ + chat_backend
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
.\build.ps1 -Target all      # Toutes les plateformes
.\build.ps1 -Target web      # Web uniquement
```

Dockerfile multi-étape :
- **dev** : `flutter run -d web-server --web-port 3000`
- **prod** : `flutter build web` → servi statique avec nginx

## Variables d'environnement

| Variable | Description | Défaut |
|----------|-------------|---------|
| `BACKEND_URL` | URL de base de l'API (via `--dart-define`) | `http://localhost:8000/api` |
| `CHROME_EXECUTABLE` | Navigateur pour `flutter run -d chrome` | Détecté automatiquement (Brave/Chrome) |

## Solution de problèmes

| Problème | Solution |
|----------|----------|
| `flutter pub get` échoue | Supprime `.dart_tool`, `pubspec.lock` et réessaie |
| Conflits de types Hive | `flutter pub run build_runner build --delete-conflicting-outputs` |
| Échec de connexion WebSocket | Vérifie `BACKEND_URL` ; assure-toi que le backend expose `/ws/chat` |
| La langue ne persiste pas | Efface `SharedPreferences`, vérifie `LocaleService.load()` |
| Le mode sombre ne s'applique pas | Assure-toi de `ThemeMode.system` ou `ThemeMode.dark` explicite dans `MaterialApp` |

## Contribuer

1. Suis les motifs existants (singletons, `setState`, streams)
2. Ajoute `Semantics` aux nouveaux widgets interactifs
3. Ajoute des traductions à tous les ARB
4. Exécute `flutter analyze` et `flutter test` avant la PR
5. Commits conventionnels : `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`

## Licence

MIT — Consulte [LICENSE](../LICENSE) à la racine.
