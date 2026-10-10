---
name: flutter-state-management-pattern
description: Expert guidance for Clakettes Flutter state management. Uses Singletons (AuthService, ApiService, ConnectivityMonitor, OfflineCacheService, SyncQueueService, LocaleService) + StatefulWidget setState() + Streams — NOT Provider, NOT flutter_it. Covers service initialization order in main(), AuthService session persistence via SharedPreferences, offline sync via SyncQueueService (HMAC-signed Hive cache), and connectivity monitoring. Use when working with state, services, or data flow.
metadata:
  model: models/gemini-3.1-pro-preview
  last_modified: Tue, 23 Jun 2026 01:45:00 GMT
---
# Flutter State Management Pattern

## Architecture

**Singletons + StatefulWidget setState() + Streams**. No Provider, no ChangeNotifier, no flutter_it.

### Singleton Patterns Used

| Service | Access | Init pattern |
|---------|--------|-------------|
| `AuthService` | `AuthService()` (factory) | `static final ... = ..._internal()` |
| `ApiService` | `ApiService()` (factory) | `static final ... = ..._internal()` |
| `ConnectivityMonitor` | `ConnectivityMonitor.instance` | `static final instance = ..._internal()` |
| `OfflineCacheService` | `OfflineCacheService.instance` | `static final instance = ..._internal()` |
| `SyncQueueService` | `SyncQueueService.instance` | `static final instance = ..._internal()` |
| `LocaleService` | `LocaleService.instance` | lazy singleton `get instance` |

## Startup Order

In `main()` (`lib/main.dart:12-19`):
1. `WidgetsFlutterBinding.ensureInitialized()`
2. `DatabaseService.init()` — registers Hive adapters, opens boxes (festivals, users, shortfilms, messages)
3. `OfflineCacheService.instance.init()` — opens Hive cache boxes, loads/generates HMAC secret
4. `SyncQueueService.instance.init()` — opens Hive sync queue box
5. `ConnectivityMonitor.instance.start()` — listens to `connectivity_plus` changes, pings `/health`
6. `LocaleService.instance.load()` — reads locale from SharedPreferences
7. `runApp(ClakettesApp())`

## Auth Flow

- `AuthService()` — stores JWT, refresh token, user in SharedPreferences
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

## UI State

StatefulWidget + `setState()` in `MainScaffold`:
```dart
int _selectedIndex = 0;
User? _currentUser;
int _unreadNotificationCount = 0;
bool _isOffline = false;
```

Navigation:
- `LayoutBuilder` checks `constraints.maxWidth > 800`
- Wide: `NavigationRail` (left sidebar) + `Drawer`
- Narrow: `NavigationBar` (bottom tabs)
- Screens lazy-initialized (`_screens[0] ??= ...`)

Locale changes: `ClakettesApp` subscribes to `LocaleService.onLocaleChanged` stream → `setState()`.
