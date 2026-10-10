import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';

/// Chip accesible que muestra una insignia de ubicación (Sugerido/Obligatorio/Destacado).
///
/// Se oculta por completo cuando [badge] es null o está vacío. Muestra un icono
/// y una etiqueta de color; hay una variante [small] para filas compactas.
class LocationBadgeChip extends StatelessWidget {
  final String? badge;
  final bool small;

  const LocationBadgeChip({
    super.key,
    this.badge,
    this.small = false,
  });

  static const Map<String, IconData> _badgeIcons = {
    'Sugerido': Icons.lightbulb_outline_rounded,
    'sugerido': Icons.lightbulb_outline_rounded,
    'Obligatorio': Icons.priority_high_rounded,
    'obligatorio': Icons.priority_high_rounded,
    'Destacado': Icons.star_rounded,
    'destacado': Icons.star_rounded,
  };

  Color _badgeColor(String badge, ColorScheme cs) {
    switch (badge.toLowerCase()) {
      case 'sugerido':
        return cs.primary;
      case 'obligatorio':
        return cs.error;
      case 'destacado':
        return cs.tertiary;
      default:
        return cs.outline;
    }
  }

  @override
  Widget build(BuildContext context) {
    if (badge == null || badge!.isEmpty) return const SizedBox.shrink();

    final cs = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;
    final color = _badgeColor(badge!, cs);
    final icon = _badgeIcons[badge!] ?? Icons.label_rounded;
    final label = AppLocalizations.of(context)?.getBadgeTranslation(badge!) ?? badge!;

    return Semantics(
      label: label,
      child: Chip(
        avatar: ExcludeSemantics(
          child: Icon(icon, size: small ? 12 : 16, color: color),
        ),
        label: Text(
          label,
          style: (small ? textTheme.labelSmall : textTheme.labelLarge)?.copyWith(
            fontWeight: FontWeight.w600,
            color: color,
          ),
        ),
        backgroundColor: color.withAlpha(20),
        side: BorderSide.none,
        padding: EdgeInsets.symmetric(horizontal: small ? 2 : 4),
        visualDensity: VisualDensity.compact,
        materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
      ),
    );
  }
}
