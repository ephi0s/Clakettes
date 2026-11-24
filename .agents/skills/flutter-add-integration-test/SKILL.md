---
name: flutter-add-integration-test
description: Configures Flutter Driver for app interaction and converts MCP actions into permanent integration tests. Use when adding integration testing to a project, exploring UI components via MCP, or automating user flows with the integration_test package.
metadata:
  model: models/gemini-3.1-pro-preview
  last_modified: Tue, 21 Apr 2026 18:29:20 GMT
---
# Integration tests — Clakettes (`frontend/`)

E2E con el paquete `integration_test`: tests en `frontend/integration_test/app_test.dart` y
driver en `frontend/test_driver/integration_test.dart`. No uses `flutter_driver`,
`enableFlutterDriverExtension()` ni entry points de demo: el binding lo resuelve todo.

## Layout real

- `frontend/integration_test/app_test.dart`: `IntegrationTestWidgetsFlutterBinding.ensureInitialized()` + `testWidgets`.
- `frontend/test_driver/integration_test.dart`: `Future<void> main() => integrationDriver();`.
- `frontend/lib/main.dart`: `ClakettesApp`, el widget raíz que se bombea.
- Imports de UI: `package:material_ui/material_ui.dart` / `package:cupertino_ui/cupertino_ui.dart`.

## Checklist

- [ ] **Setup**
  - [ ] `integration_test` y `flutter_test` ya están en `dev_dependencies` de `frontend/pubspec.yaml`; no los reañadas.
  - [ ] En `setUpAll` desactiva el chequeo de backend e inicializa los singletons en orden:
    ```dart
    MainScaffold.skipBackendCheck = true;
    await DatabaseService.init();
    await OfflineCacheService.instance.init();
    await SyncQueueService.instance.init();
    ConnectivityMonitor.instance.start();
    await LocaleService.instance.load();
    ```
- [ ] **Exploración vía MCP (antes de escribir el test)**
  - [ ] `launch_app` sobre `frontend/lib/main.dart` para obtener el DTD URI.
  - [ ] `get_widget_tree` para descubrir `Text`, claves y tipos reales (`NavigationBar`/`NavigationRail`, `Icons.search_rounded`).
  - [ ] `tap`, `enter_text`, `scroll` validan el flujo; `waitFor`/`get_health` tras navegación o animaciones.
  - [ ] Si el widget no aparece, está sin montar en un `ListView`/`SliverList`: `scroll`/`scrollIntoView` primero.
- [ ] **Autoría**
  - [ ] Nombra archivos `<nombre>_test.dart`; usa `testWidgets` con `WidgetTester`.
  - [ ] `await tester.pumpWidget(const ClakettesApp()); await tester.pump();` (y otro `pump()` tras cada interacción).
  - [ ] Afirma con `find.text('Festivals')`, `find.byIcon(Icons.search_rounded)` o `find.byWidgetPredicate(...)`.
  - [ ] Elementos fuera de pantalla: `await tester.scrollUntilVisible(itemFinder, 500.0, scrollable: listFinder)`.
- [ ] **Ejecución y feedback loop**
  - [ ] `flutter drive --driver=test_driver/integration_test.dart --target=integration_test/app_test.dart` (o `flutter test integration_test/app_test.dart`).
  - [ ] Chrome: usa `CHROME_EXECUTABLE` detectado; si hace falta `chromedriver --port=4444` y `-d chrome`. Headless web: `-d web-server`.
  - [ ] Fallo → `PumpAndSettleTimedOutException` = animación infinita; widget no encontrado = `pump()` extra o `scrollUntilVisible` → vuelve a correr.
  - [ ] Cierre: `flutter analyze` y `tools/check.ps1` / `tools/check.sh`.
