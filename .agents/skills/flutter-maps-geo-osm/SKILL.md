---
name: flutter-maps-geo-osm
description: Expert guidance for Clakettes maps and geo. Covers flutter_map with OSM tiles, MapPickerScreen with Nominatim search, shared openInMaps() action, and geolocator permissions. Use when working with locations, maps, or coordinates.
metadata:
  model: models/gemini-3.1-pro-preview
  last_modified: Sat, 10 Oct 2026 00:00:00 GMT
---
# Clakettes Maps and Geo (OSM)

## Dependencies (`frontend/pubspec.yaml`)

`flutter_map: ^7.0.2`, `latlong2: ^0.9.1`, `geolocator: ^11.0.0`, `url_launcher: ^6.2.1`.

## Tile Layer (single canonical form)

Every map uses OpenStreetMap tiles with the app user agent:

```dart
TileLayer(
  urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
  userAgentPackageName: 'com.clakettes.app',
)
```

Variants in use: full interactive maps (`locations_screen.dart`), non-interactive previews (`InteractiveFlag.none`, zoom 13, in `location_cards.dart`), mini detail maps (`h: 180`, zoom 13, `location_detail_screen.dart`), centroid maps (avg lat/lng, zoom 12, `h: 200`, `festival_sections.dart`).

## Shared Actions (never duplicate)

- `openInMaps(lat, lng, {label})` (`lib/widgets/open_in_maps_action.dart`): tries `geo:0,0?q=lat,lng(label)` via `canLaunchUrl`/`launchUrl`, falls back to `https://www.openstreetmap.org/?mlat=&mlon=` (`kIsWeb ? _blank : externalApplication`). Screens keep only a one-line `_openInMaps` wrapper delegating to it.
- `MapPickerScreen(initialLocation)` (`lib/widgets/map_picker.dart`): default center `LatLng(40.4168, -3.7038)`, `FlutterMap` + `MapController` + `onTap`, red `Icons.place` marker (size 44), Nominatim search (`https://nominatim.openstreetmap.org/search?q=&format=json&limit=5`, header `User-Agent: Clakettes/1.0`), `move(latLng, 15)`, returns `LatLng` via `Navigator.pop`.

Creating screens read coordinates as `LatLng? _selectedLatLng` via `MapPickerScreen` (see `create_festival_screen.dart`).

## Geolocation

Today only `chat_screen.dart` calls `Geolocator.getCurrentPosition()` to send `lat,lng` with 6 decimals — without `check/requestPermission` or `isLocationServiceEnabled`. New callers must add the permission flow first.

Permissions already declared: `ACCESS_FINE/COARSE_LOCATION` in `AndroidManifest.xml`, `NSLocationWhenInUseUsageDescription` in `ios/Runner/Info.plist` (no `Always`).
