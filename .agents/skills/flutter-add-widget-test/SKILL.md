---
name: flutter-add-widget-test
description: Implement a component-level test using `WidgetTester` to verify UI rendering and user interactions (tapping, scrolling, entering text). Use when validating that a specific widget displays correct data and responds to events as expected.
metadata:
  model: models/gemini-3.1-pro-preview
  last_modified: Tue, 21 Apr 2026 21:15:41 GMT
---
# Widget tests — Clakettes (`frontend/`)

Tests de componentes en `frontend/test/widgets/`; tests de pantallas en `frontend/test/screens/`.
UI con `package:material_ui/material_ui.dart` (y `cupertino_ui`), nunca `package:flutter/material.dart`.
Package: `clakettes`. Estado del repo: singletons + `setState()` + Streams; `ApiService()` devuelve `PaginatedResult<T>`.

## Envoltorio según el widget

- Sin i18n (p. ej. `SemanticHeader`, `StatusIndicator`): `MaterialApp(home: Scaffold(body: widget))` directo, como en `test/widgets/semantic_header_test.dart`.
- Con i18n o pantallas: `wrapWithLocalization()` de `test/screens/test_helper.dart`. Envuelve en `MaterialApp` con `TestLocalizationsDelegate`, `FlutterQuillLocalizations.delegate` y `GlobalMaterialLocalizations.delegates`, fijando `Locale('en')`.
- **Tras `pumpWidget` haz un `pump()` extra**: el delegate resuelve en el primer frame. Con `MockClient`/async pueden hacer falta 2-3 pumps:
  ```dart
  await tester.pumpWidget(wrapWithLocalization(const CalendarScreen()));
  await tester.pump();
  await tester.pump();
  ```
- Estado global: `setupApiTest()` limpia SharedPreferences/AuthService; inyecta con `ApiService().client = MockClient(...)` y envelope paginado `{"items": [], "total": 0, "pages": 0}`.
- Idioma: los tests fijan `en`; los cambios de locale reales los gestiona `LocaleService`.

## Checklist

- [ ] **Definir y construir**
  - [ ] Archivo `<nombre>_test.dart` en `test/widgets/` (o `test/screens/`); imports `material_ui`, `flutter_test` y `package:clakettes/widgets/...`.
  - [ ] `testWidgets('describe…', (tester) async { ... })` y `pumpWidget` con el envoltorio correcto.
  - [ ] `await tester.pump();` extra (y los que hagan falta para i18n/async).
- [ ] **Localizar y verificar**
  - [ ] Finders: `find.text('Festivals')`, `find.byType(SemanticHeader)`, `find.byIcon(Icons.check_circle_rounded)`, `find.byWidgetPredicate(...)`.
  - [ ] Matchers: `findsOneWidget`, `findsWidgets`, `findsNothing`, `findsNWidgets(n)`.
  - [ ] Accesibilidad: comprueba `Semantics`/`ExcludeSemantics` y tooltips de los widgets reutilizables.
- [ ] **Interactuar**
  - [ ] `tester.tap(finder)` → `pump()` para estado simple (`setState`); `pumpAndSettle()` para animaciones/streams.
  - [ ] `tester.enterText(...)` con `TextInputAction` cuando aplique; `scrollUntilVisible` para listas largas.
- [ ] **Verificar y feedback loop**
  - [ ] `expect()` tras cada interacción; si el finder falla, revisa envoltorio y número de pumps.
  - [ ] Corre `flutter test test/widgets/<nombre>_test.dart`; luego `flutter analyze` y `tools/check.ps1` / `tools/check.sh`.
  - [ ] Fallo → ajusta matcher/envoltorio/estado → vuelve a correr hasta pasar.
