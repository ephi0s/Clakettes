---
name: flutter-build-responsive-layout
description: Use `LayoutBuilder`, `MediaQuery`, or `Expanded/Flexible` to create a layout that adapts to different screen sizes. Use when you need the UI to look good on both mobile and tablet/desktop form factors.
metadata:
  model: models/gemini-3.1-pro-preview
  last_modified: Tue, 24 Nov 2026 00:00:00 GMT
---
# Layouts adaptativos en Clakettes

Flutter 3.50.1 / Dart 3.14. UI desde `package:material_ui/material_ui.dart` y `package:cupertino_ui/cupertino_ui.dart`.

## Decisión: medir el espacio disponible

- [ ] Usa `LayoutBuilder` y decide con `constraints.maxWidth`, no con el tipo de dispositivo.
- [ ] Usa `MediaQuery.sizeOf(context)` solo si necesitas el tamaño de toda la ventana.
- [ ] No uses `MediaQuery.orientationOf`/`OrientationBuilder` ni bloquees la orientación: la app corre en ventanas redimensionables.
- [ ] Regla base: «las restricciones bajan, los tamaños suben, el padre coloca».

## Decisión: patrón de navegación (`frontend/lib/main_scaffold.dart`)

- [ ] Envuelve el scaffold en `LayoutBuilder` y evalúa `constraints.maxWidth > 800`.
- [ ] Si es ancho: `NavigationRail` + `Drawer`; si no: `NavigationBar`.
- [ ] Mantén las pantallas lazy: `_screens[index] ??= ...` (no las construyas todas al arrancar).
- [ ] Sin `Expanded` fuera de `Row`/`Column`/`Flex`; sin `Positioned` fuera de `Stack`.

## Decisión: distribuir y limitar espacio

- [ ] `Expanded` ocupa todo el espacio restante; `Flexible` permite encoger hasta un límite.
- [ ] Listas grandes o desconocidas: siempre `ListView.builder`/`GridView.builder`.
- [ ] Evita estiramientos en pantallas grandes con `ConstrainedBox(maxWidth: ...)` dentro de un `Center`.
- [ ] Formularios: `LayoutBuilder` con tope `maxWidth: 600`, `SingleChildScrollView` + `Column` con `SizedBox(height: ...)` entre campos.

## Decisión: tamaño de pantalla y extracción

- [ ] Pantallas en `frontend/lib/screens/` por debajo de 600 líneas.
- [ ] Si una pantalla crece, extrae UI reutilizable a `frontend/lib/widgets/`: burbujas, tarjetas, barras, secciones.
- [ ] No rompas accesibilidad al reestructurar: conserva `Semantics`, `ExcludeSemantics`, `SemanticHeader` y tooltips.

## Verificación

- [ ] `flutter analyze` y `flutter test`.
- [ ] Puerta completa: `tools/check.ps1` / `tools/check.sh`.
- [ ] Redimensiona la ventana y revisa la transición de NavigationBar a NavigationRail/Drawer y posibles overflows.
