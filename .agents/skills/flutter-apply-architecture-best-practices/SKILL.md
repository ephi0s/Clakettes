---
name: flutter-apply-architecture-best-practices
description: Clakettes architecture for Flutter. Singletons (AuthService, ApiService, ConnectivityMonitor, OfflineCacheService, SyncQueueService, LocaleService) + StatefulWidget setState() + Streams — NOT MVVM, NOT Provider, NOT get_it. Covers layers, service init order, auth flow, offline sync and navigation. Use when structuring features or refactoring in this project.
metadata:
  model: models/gemini-3.1-pro-preview
  last_modified: Tue, 24 Nov 2026 00:00:00 GMT
---
# Clakettes Flutter Architecture

## Layers

Singletons in `lib/services/` own data and connectivity. Screens in `lib/screens/` own UI state via `setState()`. Shared UI lives in `lib/widgets/`, i18n in `lib/l10n/`, plain models with `fromJson`/`toJson` in `lib/models/`.

Never introduce ViewModels, `ChangeNotifier`, repositories, use cases, `freezed`/`built_value`, or DI containers (`provider`, `get_it`). Inject nothing: call singletons directly (`ApiService()`, `SyncQueueService.instance`).

## Singleton Services

| Service | Access | Init pattern |
|---------|--------|-------------|
| `AuthService` | `AuthService()` (factory) | `static final ... = ..._internal()` |
| `ApiService` | `ApiService()` (factory) | `static final ... = ..._internal()` |
| `ConnectivityMonitor` | `ConnectivityMonitor.instance` | `static final instance = ..._internal()` |
| `OfflineCacheService` | `OfflineCacheService.instance` | `static final instance = ..._internal()` |
| `SyncQueueService` | `SyncQueueService.instance` | `static final instance = ..._internal()` |
| `LocaleService` | `LocaleService.instance` | lazy singleton `get instance` |

## Startup Order

In `main()` (`lib/main.dart`):
1. `WidgetsFlutterBinding.ensureInitialized()`
2. `DatabaseService.init()` — registra los adaptadores Hive y abre las boxes
3. `OfflineCacheService.instance.init()` — opens Hive cache boxes, loads/generates HMAC secret
4. `SyncQueueService.instance.init()` — opens Hive sync queue box
5. `ConnectivityMonitor.instance.start()` — listens to `connectivity_plus` changes, pings `/health`
6. `LocaleService.instance.load()` — reads locale from SharedPreferences
7. `runApp(ClakettesApp())`

## Auth Flow

- `AuthService()` — stores JWT, refresh token and user in SharedPreferences
- Login: `ApiService().login()` → saves token + refresh token + user → `MainScaffold` setState
- Logout: clears AuthService + OfflineCacheService → resets to login screen
- Token refresh: `ApiService.refreshToken()` — transparent retry on 401, clears session if refresh fails
- Session management: list/revoke sessions in UI

## Connectivity & Offline

- `ConnectivityMonitor` wraps `connectivity_plus`, broadcasts via `Stream<bool>`
- Verifies connectivity with backend health check (not just local link)
- `MainScaffold` subscribes in `initState()`, shows offline banner
- `OfflineCacheService` — HMAC-SHA256 signed Hive entries, schema validation per entity type
- `SyncQueueService` — FIFO queue in Hive, replayed on reconnect via `syncAll()`
- On reconnect: sync prompt shown if `pendingCount > 0`

## UI State & Navigation

StatefulWidget + `setState()` in `MainScaffold`:

```dart
int _selectedIndex = 0;
User? _currentUser;
int _unreadNotificationCount = 0;
bool _isOffline = false;
```

- `LayoutBuilder` checks `constraints.maxWidth > 800`
- Wide: `NavigationRail` (left sidebar) + `Drawer`
- Narrow: `NavigationBar` (bottom tabs)
- Screens lazy-initialized (`_screens[0] ??= ...`)
- Locale changes: `ClakettesApp` subscribes to `LocaleService.onLocaleChanged` stream → `setState()`

## Project Structure

```text
lib/
├── main.dart              # init order, ClakettesApp
├── main_scaffold.dart     # NavigationRail (>800px) / NavigationBar + Drawer
├── auth_wrapper.dart      # root widget
├── screens/               # one StatefulWidget per screen, _loadData + loading/error
├── services/              # singletons: api, auth, database, offline_cache, sync_queue,
│   └── api/               # connectivity_monitor, locale_service, notification_service
├── models/                # plain classes, Hive adapters via build_runner
├── widgets/               # reusable_widgets, confirm_dialog, open_in_maps_action...
└── l10n/                  # app_localizations.dart manual + ARB via rootBundle
```

## Workflow: Adding a Feature

- [ ] **Step 1: Model.** Add/update plain model in `lib/models/` with `fromJson`/`toJson`. If offline persistence is needed, add Hive `TypeAdapter` and regenerate (`flutter pub run build_runner build --delete-conflicting-outputs`).
- [ ] **Step 2: API.** Add method to the matching `part` file in `lib/services/api/` (never raw `http` calls in screens). Return `PaginatedResult<T>` for lists (`?page&size`).
- [ ] **Step 3: Offline.** On catch, `queue.contains(...)` then `enqueue(...)` (see flutter-offline-sync-hive). Never block the UI on sync.
- [ ] **Step 4: Screen.** `StatefulWidget` with `_isLoading`/`_error`, `setState()` updates, `LayoutBuilder` maxWidth 600 for forms. Reuse `ConfirmDialog`, `LoginPromptSheet`, `openInMaps()` instead of duplicating.
- [ ] **Step 5: i18n.** New strings go to all ARB files; `translate()` logs missing keys in debug.
- [ ] **Step 6: Validate.** `flutter analyze`, then `flutter test`.

## Example: Screen With Service Singleton

```dart
class FestivalsScreen extends StatefulWidget {
  const FestivalsScreen({super.key});
  @override
  State<FestivalsScreen> createState() => _FestivalsScreenState();
}

class _FestivalsScreenState extends State<FestivalsScreen> {
  List<Festival> _items = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      final page = await ApiService().getFestivals(page: 1, size: 20);
      if (mounted) setState(() => _items = page.items);
    } catch (e) {
      debugPrint('Error: $e');
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }
}
```
