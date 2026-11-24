---
name: flutter-accessibility-wcag
description: Expert guidance for Clakettes WCAG 2.1 / ARIA accessibility. Covers Semantics widget patterns on the accessible widgets, ExcludeSemantics for decorative icons, SemanticHeader for screen reader headings, tooltips on interactive elements, SnackBarBehavior.floating, form validation with autovalidateMode, keyboard navigation with TextInputAction, and color contrast via Material 3 dark mode. Use when ensuring accessibility compliance or adding new accessible widgets.
metadata:
  model: models/gemini-3.1-pro-preview
  last_modified: Tue, 23 Jun 2026 01:45:00 GMT
---
# Flutter Accessibility (WCAG 2.1)

## Core Widgets

The reusable accessible widgets in `lib/widgets/reusable_widgets.dart`:

### ProfileAvatar
- `Semantics(label: semanticLabel)` wrapper on CircleAvatar
- `ExcludeSemantics` on initials text (decorative)
- Fallback to first letter of name

### InfoRow
- `Semantics(label: semanticLabel)` wrapper
- `ExcludeSemantics` on leading icon (decorative, in primaryContainer box)
- `InkWell` with `BorderRadius.circular(8)` when `onTap != null`

### StatusIndicator
- `Semantics` with `activeLabel`/`inactiveLabel` as label
- `ExcludeSemantics` on icon
- Optional `Chip` variant

### ListItemCard
- `Semantics(label: semanticLabel ?? title)` wrapper
- `Card` + `InkWell`, rounded 14
- Chevron trailing icon by default

### SemanticHeader
- `Semantics(header: true, label: text)` — marks as heading for screen readers
- Pure text display, accepts optional `style` and `textAlign`

### SemanticTextField
- `Semantics(label: semanticLabel)` wrapper on `TextFormField`
- Passes through: `validator`, `textInputAction`, `onFieldSubmitted`, `maxLength`, `obscureText`, `suffixIcon`, `prefixIcon`

## Patterns

- **Semantics widgets** on the accessible widgets and screens
- **Tooltips** on IconButtons and interactive elements
- **ExcludeSemantics** on decorative icons to avoid redundant announcements
- **SnackBarBehavior.floating** for better visibility
- **Keyboard navigation**: `TextInputAction.next`/`done` on forms, `onFieldSubmitted` callbacks
- **Form validation**: `autovalidateMode: AutovalidateMode.onUserInteraction`

## Location Distribution

- `lib/widgets/reusable_widgets.dart` — the accessible widgets (ProfileAvatar, InfoRow, StatusIndicator, ListItemCard, SemanticHeader, SemanticTextField)
- `lib/widgets/empty_state_widget.dart` — Semantics + ExcludeSemantics on decorative icon
- `lib/widgets/error_state_widget.dart` — Semantics on error messages
- All screens in `lib/screens/` — Semantics/ExcludeSemantics on the screens
- `lib/main_scaffold.dart` — NavigationRail/NavigationBar with Semantics labels, liveRegion on content area
