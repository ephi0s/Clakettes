---
name: flutter-fix-layout-issues
description: Fixes Flutter layout errors (overflows, unbounded constraints) using Dart and Flutter MCP tools. Use when addressing "RenderFlex overflowed", "Vertical viewport was given unbounded height", or similar layout issues.
metadata:
  model: models/gemini-3.1-pro-preview
  last_modified: Tue, 24 Nov 2026 00:00:00 GMT
---
# Errores de layout en Clakettes

Flutter 3.50.1 / Dart 3.14. UI desde `package:material_ui/material_ui.dart` y `package:cupertino_ui/cupertino_ui.dart`.

Regla base: «las restricciones bajan, los tamaños suben, el padre coloca». El error aparece cuando un hijo pide más espacio del que el padre puede dar.

## Diagnóstico y decisión de arreglo

- [ ] «RenderFlex overflowed» → `Expanded`/`Flexible` alrededor del hijo que desborda en `Row`/`Column`/`Flex`.
- [ ] «Vertical viewport was given unbounded height» → envolver `ListView`/`GridView` en `Expanded` o darle altura con `SizedBox`.
- [ ] «InputDecorator cannot have unbounded width» → `Expanded`/`Flexible` alrededor de `TextField`/`TextFormField`.
- [ ] «Incorrect use of ParentData widget» → `Expanded` hijo directo de `Row`/`Column`/`Flex`; `Positioned` hijo directo de `Stack`.
- [ ] «RenderBox was not laid out» → error en cascada; ignóralo y busca la violación de restricciones real más arriba en el stack.

Ejemplos mínimos:

```dart
// Altura no acotada: ListView dentro de Column
Column(children: [const Text('Header'), Expanded(child: ListView.builder(...))])

// Ancho no acotado: TextField dentro de Row
Row(children: [const Icon(Icons.search), Expanded(child: TextFormField())])
```

## Flujo de resolución

- [ ] Ejecuta en debug y captura el mensaje exacto en la consola.
- [ ] Identifica el error primario (ignora los «RenderBox was not laid out» en cascada).
- [ ] Aplica el arreglo condicional de la tabla anterior según el mensaje.
- [ ] Hot reload y comprueba que desaparecen la pantalla roja/gris y las franjas amarillas.
- [ ] Si aparece un error nuevo, repite el flujo desde el mensaje primario.

## Al reestructurar

- [ ] Conserva `Semantics`, `ExcludeSemantics`, `SemanticHeader` y tooltips; no los pierdas al envolver widgets.
- [ ] Extrae UI reutilizable a `frontend/lib/widgets/` (burbujas, tarjetas, barras, secciones) y mantén `frontend/lib/screens/` por debajo de 600 líneas.
- [ ] Formularios: `LayoutBuilder` con tope `maxWidth: 600`, `SingleChildScrollView` + `Column` con `SizedBox(height: ...)`.

## Verificación

- [ ] `flutter analyze` y `flutter test`.
- [ ] Puerta completa: `tools/check.ps1` / `tools/check.sh`.
