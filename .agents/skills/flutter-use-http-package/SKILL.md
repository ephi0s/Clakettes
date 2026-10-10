---
name: flutter-use-http-package
description: Clakettes networking via the ApiService singleton (http + JWT Bearer + paginated envelope + offline SyncQueue fallback). Never raw http calls in screens. Use when adding or changing backend calls.
metadata:
  model: models/gemini-3.1-pro-preview
  last_modified: Sat, 10 Oct 2026 00:00:00 GMT
---
# Clakettes Networking via ApiService

## Contents
- [Rules](#rules)
- [Workflow: New Endpoint](#workflow-new-endpoint)
- [Examples](#examples)

## Rules

- **Singleton only**: `ApiService()` (factory, `http.Client` inside). Never instantiate `http.Client` or call `http.get/post` in screens/widgets. Test seam: `setClient()` / `reset()`.
- **Base URL**: `BackendConfig.compileTimeUrl` (`--dart-define=BACKEND_URL=...`) falling back to `BackendConfig.platformDefaultUrl`; runtime override via `setBaseUrl()` from `backend_setup_screen.dart`. Build paths as `$baseUrl/api/...`.
- **Auth**: `AuthService` token injected as `Authorization: Bearer <jwt>` on every request. On 401 the service refreshes the token once (`refreshToken()`); if refresh fails the session is cleared.
- **Envelope**: lists return `PaginatedResult<T>` (`items`, `total`, `pages`) with `?page=1&size=20`. Respect real pagination in screens; no `size: 100` dumps.
- **Status codes**: `200` GET/PUT/DELETE, `201` POST. Throw on anything else; screens catch and show `showAppSnack`.
- **Offline fallback**: on catch, guard `SyncQueueService.instance.contains(entityType:, operation:, payload:)` then `enqueue(...)`. Never enqueue duplicates.
- **Health**: `ApiService.healthCheck()` is the real connectivity probe used by `ConnectivityMonitor` — use it, not just `connectivity_plus`.

## Workflow: New Endpoint

- [ ] Add the method to the matching `part` file in `lib/services/api/` (`festival_api.dart`, `user_api.dart`, `channel_api.dart`, `form_api.dart`, `calendar_api.dart`, `catalog_api.dart`, `org_api.dart`, `event_api.dart`, `location_api.dart`).
- [ ] Parse with the model `fromJson`; wrap lists in `PaginatedResult`.
- [ ] In the screen: try API → catch → `contains`/`enqueue` → snackbar (`loadError` or `syncPending`).
- [ ] Run `flutter analyze`.

## Examples

### Domain API Method

```dart
Future<PaginatedResult<Festival>> getFestivals({int page = 1, int size = 20}) async {
  final headers = await _authHeaders;
  final res = await client.get(
    Uri.parse('$baseUrl/festivals?page=$page&size=$size'),
    headers: headers,
  );
  if (res.statusCode != 200) throw Exception('Failed: ${res.statusCode}');
  final body = jsonDecode(res.body) as Map<String, dynamic>;
  final items = (body['items'] as List).cast<Map<String, dynamic>>();
  return PaginatedResult(
    items: items.map(Festival.fromJson).toList(),
    total: body['total'] as int,
    pages: body['pages'] as int,
  );
}
```

### Screen With Offline Fallback

```dart
try {
  await ApiService().createFestival(festival);
  if (mounted) showAppSnack(context, l10n.success);
} catch (e) {
  final queue = SyncQueueService.instance;
  final payload = festival.toJson();
  if (!queue.contains(entityType: 'festival', operation: 'create', payload: payload)) {
    await queue.enqueue(entityType: 'festival', operation: 'create', payload: payload);
  }
}
```
