---
name: flutter-implement-json-serialization
description: Clakettes model serialization. Plain classes with fromJson/toJson plus Hive TypeAdapters via build_runner where offline persistence applies. Use when adding or changing lib/models/.
metadata:
  model: models/gemini-3.1-pro-preview
  last_modified: Sat, 10 Oct 2026 00:00:00 GMT
---
# Clakettes JSON Serialization

## Contents
- [Core Guidelines](#core-guidelines)
- [Workflow: Model Change](#workflow-model-change)
- [Examples](#examples)

## Core Guidelines

- **Plain models first**: `factory Model.fromJson(Map<String, dynamic> json)` + `Map<String, dynamic> toJson()`, `final` properties, explicit casts. Pattern-match syntax is used in this codebase.
- **Hive when offline**: models persisted by `DatabaseService` (`festivals`, `users`, `shortfilms`, `messages` boxes) or cached by `OfflineCacheService` need a Hive `TypeAdapter` with a unique `typeId`. Register it in `DatabaseService.init()` alongside the existing 36 adapters.
- **Regenerate, never hand-write adapters**: `flutter pub run build_runner build --delete-conflicting-outputs`.
- **SyncQueue payloads**: `SyncOperation.toJson()` uses `entity_type`/`entity_id`/`created_at`/`status`/`attempts` keys; keep them stable — the queue replays them against the backend.
- **Schema contract**: `OfflineCacheService._validateEntitySchema` requires `festival.name: String`, `user.username/email: String` + `role` in `{admin, organizer, user, jury, moderator}`, `shortfilm.title: String` + `user_id: int`, `message.content: String` + `sender_id: int`. New required fields must be added there too.
- **Large payloads**: `compute()` for crypto/parse off the UI thread (see `crypto_utils.dart`); small payloads parse synchronously.
- **Tests**: unit-test `fromJson`/`toJson` round-trip for every model change.

## Workflow: Model Change

- [ ] Update the plain class + `fromJson`/`toJson`.
- [ ] If persisted/cached: add/update the `TypeAdapter` (unique `typeId`), register in `DatabaseService.init()`, run build_runner.
- [ ] If the entity is cached: extend `_validateEntitySchema` for new required fields.
- [ ] Run `flutter analyze` + model tests.

## Examples

### Model With Pattern-Match fromJson

```dart
class ShortFilm {
  final int? id;
  final String title;
  final int userId;

  const ShortFilm({this.id, required this.title, required this.userId});

  factory ShortFilm.fromJson(Map<String, dynamic> json) {
    return switch (json) {
      {'id': int? id, 'title': String title, 'user_id': int userId} =>
        ShortFilm(id: id, title: title, userId: userId),
      _ => throw const FormatException('Failed to load ShortFilm.'),
    };
  }

  Map<String, dynamic> toJson() {
    return {'id': id, 'title': title, 'user_id': userId};
  }
}
```

### Hive Adapter Registration

```dart
await Hive.initFlutter();
Hive.registerAdapter(ShortFilmAdapter());
await DatabaseService.init();
```
