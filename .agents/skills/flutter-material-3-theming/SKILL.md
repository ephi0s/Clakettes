---
name: flutter-material-3-theming
description: Expert guidance for Clakettes Material 3 theming. Covers custom ThemeData from seed color (#B8956E), light/dark theme via _baseTheme(ColorScheme), 18+ component themes (Card, AppBar, NavigationBar/Rail, InputDecoration, FilledButton, ElevatedButton, TextButton, SnackBar, Dialog, BottomSheet, Chip, ListTile, Drawer, PopupMenu, Scrollbar, Slider, Divider, FAB), Cupertino page transitions, and theme consistency. Use when modifying theme or adding themed widgets.
metadata:
  model: models/gemini-3.1-pro-preview
  last_modified: Tue, 23 Jun 2026 01:45:00 GMT
---
# Flutter Material 3 Theming

## Color Scheme

Defined in `lib/main.dart:48`:
```dart
static const Color _seedColor = Color(0xFFB8956E);
```
- Light: `ColorScheme.fromSeed(seedColor: _seedColor, brightness: Brightness.light, surface: Color(0xFFFDFBF9))`
- Dark: `ColorScheme.fromSeed(seedColor: _seedColor, brightness: Brightness.dark, surface: Color(0xFF121212))`
- `ThemeMode.system` — follows OS preference
- `visualDensity: VisualDensity.comfortable`, `useMaterial3: true`

## Component Themes

All in `_baseTheme(ColorScheme)` (`main.dart:87-284`):

| Component | Key details |
|-----------|-------------|
| Page transitions | `CupertinoPageTransitionsBuilder` for Android/iOS/Windows |
| Card | elevation 0, rounded 16, subtle outline |
| AppBar | `centerTitle: false`, scrolledUnderElevation 1, transparent bg |
| NavigationBar | indicatorColor: primaryContainer, rounded 12, height 68, icon 24/22 |
| NavigationRail | labelType: all, minExtendedWidth 220, groupAlignment 0.0 |
| FAB | elevation 2, rounded 16, extended padding |
| InputDecoration | filled (60% surfaceContainer), rounded 14, no border, contentPadding 16x16 |
| FilledButton | rounded 14, bold, letter-spacing 0.3 |
| ElevatedButton | rounded 14, elevation 0 |
| TextButton | rounded 10 |
| SnackBar | floating, rounded 14 |
| Dialog | rounded 20, bold title |
| BottomSheet | rounded top 24 |
| Divider | thickness 0.5, subtle |
| Chip | rounded 10, elevation 0 |
| ListTile | rounded 12, horizontal padding 16 |
| Drawer | rounded top-right/bottom-right 24 |
| PopupMenu | rounded 14 |
| Scrollbar | thickness 4, rounded 8 |
| Slider | primary/primaryContainer colors |

## Pattern

`_baseTheme(ColorScheme)` receives generated scheme. Both `_buildLightTheme()` and `_buildDarkTheme()` call it, ensuring consistent component themes across modes.
