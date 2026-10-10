---
name: flutter-offline-sync-hive
description: Expert guidance for Clakettes offline-first data. Covers DatabaseService.init() with 36 Hive adapters, OfflineCacheService HMAC-signed cache with schema validation, SyncQueueService FIFO replay (contains/enqueue/syncAll, maxAttempts 3, backoff), and ConnectivityMonitor health-probed status. Use when working with offline cache, sync queue, or connectivity.
metadata:
  model: models/gemini-3.1-pro-preview
  last_modified: Sat, 10 Oct 2026 00:00:00 GMT
---
# Clakettes Offline-First Data

## Startup Order (`lib/main.dart`)

1. `WidgetsFlutterBinding.ensureInitialized()`
2. `await DatabaseService.init()` — `Hive.initFlutter()` + 36 `registerAdapter(...)` calls
3. `await OfflineCacheService.instance.init()` — opens `offline_cache` + `cache_meta` boxes, loads/generates 32B HMAC secret in SharedPreferences
4. `await SyncQueueService.instance.init()` — opens `sync_queue` box
5. `ConnectivityMonitor.instance.start()` — `connectivity_plus` listener + `ApiService.healthCheck()` probe
6. `await LocaleService.instance.load()`
7. `await NotificationService.instance.init(l10n)` then `runApp(ClakettesApp())`

## OfflineCacheService

HMAC-SHA256 (base64Url) signed entries (`_CacheEntry{data, signature, timestamp}`). `get()` deletes the entry when HMAC or schema validation fails — fail closed, never serve tampered data.

| Method | Signature |
|--------|-----------|
| init | `Future<void> init()` |
| put | `Future<void> put(String entityType, dynamic data)` |
| get | `dynamic get(String entityType)` |
| remove | `Future<void> remove(String entityType)` |
| clear | `Future<void> clear()` |
| has | `bool has(String entityType)` |
| timestamp | `int? getTimestamp(String entityType)` |

Schema contract (`_validateEntitySchema`): rejects `id < 0`; requires `festival.name: String`, `user.username/email: String` + role in `{admin, organizer, user, jury, moderator}`, `shortfilm.title: String` + `user_id: int`, `message.content: String` + `sender_id: int`. Extend it when adding required fields.

## SyncQueueService

FIFO replay of mutations in Hive (`sync_queue` box, `operations` key). Non-reentrant (`_syncing` guard returns `{'synced': 0, 'failed': 0, 'errors': []}` while running).

| Member | Value |
|--------|-------|
| `maxAttempts` | `3` |
| backoff | `300 * (1 << (attempts - 1))` ms, capped at 5000, only when `attempts > 0` |
| `pendingCount` | pending + failed with `attempts < maxAttempts` |
| `syncAll()` | returns `{synced, failed, errors}`; keeps exhausted ops as `failed` for inspection |
| `_pluralize` | `festival→festivals`, `user→users`, `shortfilm→shortfilms`, `message→chat/messages` |

Always guard before enqueue to avoid duplicates:

```dart
final queue = SyncQueueService.instance;
if (!queue.contains(entityType: 'festival', operation: 'create', payload: payload)) {
  await queue.enqueue(entityType: 'festival', operation: 'create', payload: payload);
}
```

On reconnect `MainScaffold` prompts when `pendingCount > 0`; on logout `queue.clear()`.

## ConnectivityMonitor

`connectivity_plus.onConnectivityChanged` is only the trigger — `ApiService.healthCheck()` is the real probe. Exposes `isOnline` + broadcast `onStatusChanged`; `MainScaffold` shows the offline banner from it.
