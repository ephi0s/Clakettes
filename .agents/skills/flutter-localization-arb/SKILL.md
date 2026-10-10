---
name: flutter-localization-arb
description: Expert guidance for Clakettes manual i18n system. Covers 9 locales (en,es,fr,de,it,ca,eu,gl,oc), ARB JSON files loaded at runtime via rootBundle, AppLocalizations class (manual, no gen-l10n, ~413 lines), nested JSON keys for roles/validation, parameter interpolation ({param}), LocaleService singleton with SharedPreferences persistence, auto-detection from OS. Use when adding translations, creating new ARB keys, or modifying i18n logic.
metadata:
  model: models/gemini-3.1-pro-preview
  last_modified: Tue, 23 Jun 2026 01:45:00 GMT
---
# Flutter Localization (i18n)

## Architecture

Manual ARB-based — no `flutter gen-l10n`, no code generation.

1. **ARB files**: `assets/l10n/app_{lang}.arb` — 9 locales, ~300 keys each
2. **AppLocalizations**: `lib/l10n/app_localizations.dart` — loads ARB JSON at runtime via `rootBundle.loadString()`
3. **LocaleService**: `lib/services/locale_service.dart` — singleton, persists locale in SharedPreferences, broadcasts via `Stream<Locale>`
4. **MaterialApp**: configured with `localizationsDelegates` and `supportedLocales`

## Supported Locales

`en`, `es`, `fr`, `de`, `it`, `ca`, `eu`, `gl`, `oc`

## Key Patterns

### Loading
```dart
jsonString = await rootBundle.loadString('assets/l10n/app_${locale.languageCode}.arb');
// Fallback to English if file not found
```

### Access
```dart
AppLocalizations.of(context)!.someString
```

### Parameter interpolation
```dart
// ARB: "timeMinutesAgo": "{count} minutes ago"
// Dart: translate('timeMinutesAgo', args: {'count': count.toString()})
```

### Nested keys
- Roles: `getRoleTranslation('admin')` reads `_localizedStrings['roles']['admin']`
- Validation: `getValidationMessage('required')` reads `_localizedStrings['validation']['required']`

## AppLocalizations Class

`lib/l10n/app_localizations.dart` (~413 lines):
- `translate(key, {args})` — core lookup with optional interpolation
- Flat getters: `String get dashboard => translate('dashboard');`
- Parameterized: `String timeMinutesAgo(int count) => translate('timeMinutesAgo', args: {...});`
- `getRoleTranslation(String role)` — nested roles map
- `getValidationMessage(String key)` — nested validation map
- `_AppLocalizationsDelegate` — `isSupported` checks locale code, `load` calls `localizations.load()`

## LocaleService

`lib/services/locale_service.dart`:
- Lazy singleton via `get instance`
- `load()` — reads from SharedPreferences
- `setLocale(Locale)` — persists + broadcasts on stream
- `onLocaleChanged` stream — used by `ClakettesApp` to `setState()`
- `supportedLocales` — 9 Locale objects
- `localeNames` — maps codes to display names
- No UI language selector (auto-detects OS locale; setLocale exists for future use)

## Adding a New String

1. Add key to all 9 ARB files
2. Add getter in `AppLocalizations` (flat or parameterized)
3. Use: `AppLocalizations.of(context)!.newKey`
