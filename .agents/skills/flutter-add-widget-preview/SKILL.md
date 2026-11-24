---
name: flutter-add-widget-preview
description: Adds interactive widget previews to the project using the previews.dart system. Use when creating new UI components or updating existing screens to ensure consistent design and interactive testing.
metadata:
  model: models/gemini-3.1-pro-preview
  last_modified: Tue, 21 Apr 2026 20:05:23 GMT
---
# Widget previews — Clakettes (`frontend/`)

Flutter 3.50.1 / Dart 3.14. El repo usa el sistema de previews de Flutter
(`package:flutter/widget_previews.dart`) y se arranca con `flutter widget-preview start`
desde `frontend/`. Las imports de UI son `package:material_ui/material_ui.dart` y
`package:cupertino_ui/cupertino_ui.dart` (no `package:flutter/material.dart`).

## Targets válidos

Widgets reales de `frontend/lib/widgets/reusable_widgets.dart`: `ProfileAvatar`, `InfoRow`,
`StatusIndicator`, `ListItemCard`, `SemanticHeader`, `SemanticTextField`. Aplica `@Preview`
a funciones top-level, métodos estáticos o constructores públicos sin argumentos requeridos
que devuelvan `Widget`/`WidgetBuilder`. Como `SemanticHeader` exige `text`, usa una función:

```dart
import 'package:flutter/widget_previews.dart';
import 'package:material_ui/material_ui.dart';
import 'package:clakettes/widgets/reusable_widgets.dart';

@Preview(name: 'SemanticHeader', group: 'Typography')
Widget semanticHeaderPreview() => const SemanticHeader(text: 'Festivals');
```

## Checklist

- [ ] **Crear el preview**
  - [ ] Importa `package:flutter/widget_previews.dart` junto con `material_ui`/`cupertino_ui`.
  - [ ] Elige un target válido (arriba) y configura `@Preview(name:, group:, size:, brightness:)`.
  - [ ] Varios `@Preview` en el mismo target = varias instancias; extrae una subclase de `Preview` o `MultiPreview` si la configuración se repite.
  - [ ] Usa `size:` si el widget no tiene restricciones (el previewer lo limita al ~50% del viewport).
  - [ ] Para nombres/valores dinámicos usa `transform()` en una `Preview`/`MultiPreview` propia (un `const` no permite interpolación).
- [ ] **Limitaciones del previewer (web)**
  - [ ] Sin `dart:io`/`dart:ffi` ni plugins nativos: los singletons de Clakettes (Hive, SharedPreferences, connectivity) pueden fallar; aísla el widget o usa imports condicionales/mocks.
  - [ ] Assets con prefijo de paquete: `packages/clakettes/assets/...`.
  - [ ] Callbacks pasados a las anotaciones deben ser públicos y `const`.
  - [ ] Si el widget depende de `Theme.of(context)`, envuélvelo con el Material 3 del repo (seed `#B8956E`, dark mode).
- [ ] **Interacción y feedback loop**
  - [ ] IDE: abre el tab "Flutter Widget Preview"; CLI: `flutter widget-preview start` (abre Chrome).
  - [ ] Edita y observa el refresco automático; hot restart global para estado estático, individual para estado local del widget.
  - [ ] Revisa errores en consola IDE/CLI → corregir → repetir.
  - [ ] Cierre: `flutter analyze` y `tools/check.ps1` / `tools/check.sh`.
