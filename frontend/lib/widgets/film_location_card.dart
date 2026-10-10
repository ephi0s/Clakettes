import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../models/film_location_model.dart';
import '../models/location_model.dart';

/// Tarjeta accesible que muestra una ubicación asignada a una película con su rol y rango horario.
///
/// Úsala en listas de ubicaciones vinculadas a una película. Muestra una miniatura,
/// el nombre de la ubicación, una insignia de rol, un rango horario opcional y una
/// acción de eliminar cuando se proporcionan [showActions] y [onRemove].
class FilmLocationCard extends StatelessWidget {
  final FilmLocation filmLocation;
  final Location? location;
  final VoidCallback? onTap;
  final VoidCallback? onRemove;
  final bool showActions;

  const FilmLocationCard({
    super.key,
    required this.filmLocation,
    this.location,
    this.onTap,
    this.onRemove,
    this.showActions = true,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final l10n = AppLocalizations.of(context)!;

    return Semantics(
      label: location?.name ?? l10n.location,
      child: Card(
        margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 5),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(14),
          side: BorderSide(color: colorScheme.outlineVariant.withAlpha(30)),
        ),
        child: InkWell(
          borderRadius: BorderRadius.circular(14),
          onTap: onTap,
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Row(
              children: [
                _buildThumbnail(context),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        location?.name ?? l10n.location,
                        style: theme.textTheme.titleSmall?.copyWith(
                          fontWeight: FontWeight.w600,
                          color: colorScheme.onSurface,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          _RoleBadge(role: filmLocation.role),
                          if (filmLocation.startTime != null || filmLocation.endTime != null) ...[
                            const SizedBox(width: 8),
                            _TimeRange(
                              startTime: filmLocation.startTime,
                              endTime: filmLocation.endTime,
                            ),
                          ],
                        ],
                      ),
                    ],
                  ),
                ),
                if (showActions && onRemove != null) ...[
                  const SizedBox(width: 8),
                  Semantics(
                    label: l10n.delete,
                    button: true,
                    child: IconButton(
                      icon: Icon(Icons.close_rounded, size: 18, color: colorScheme.onSurfaceVariant),
                      onPressed: onRemove,
                      visualDensity: VisualDensity.compact,
                      padding: EdgeInsets.zero,
                      constraints: const BoxConstraints(minWidth: 32, minHeight: 32),
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }

  /// Renderiza una miniatura en caché de la primera imagen de la ubicación, con un icono de ubicación como respaldo.
  Widget _buildThumbnail(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final images = location?.locationImages ?? [];

    return Container(
      width: 48,
      height: 48,
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainerHighest.withAlpha(80),
        borderRadius: BorderRadius.circular(10),
      ),
      clipBehavior: Clip.antiAlias,
      child: images.isNotEmpty
          ? Image.network(
              images.first.url,
              width: 48,
              height: 48,
              cacheWidth: (48 * MediaQuery.devicePixelRatioOf(context)).round(),
              cacheHeight: (48 * MediaQuery.devicePixelRatioOf(context)).round(),
              fit: BoxFit.cover,
              errorBuilder: (_, __, ___) => _buildFallbackIcon(context),
            )
          : _buildFallbackIcon(context),
    );
  }

  Widget _buildFallbackIcon(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return Center(
      child: Icon(Icons.location_on_rounded, size: 22, color: colorScheme.onSurfaceVariant.withAlpha(150)),
    );
  }
}

/// Insignia de color compacta que muestra el rol de una ubicación en una película
/// (p. ej. primary, secondary, establishing) con un icono acorde.
class _RoleBadge extends StatelessWidget {
  final String role;

  const _RoleBadge({required this.role});

  static const Map<String, IconData> _roleIcons = {
    'primary': Icons.star_rounded,
    'secondary': Icons.star_outline_rounded,
    'background': Icons.panorama_rounded,
    'establishing': Icons.videocam_rounded,
  };

  Color _roleColor(String role, ColorScheme cs) {
    switch (role) {
      case 'primary':
        return cs.primary;
      case 'secondary':
        return cs.secondary;
      case 'background':
        return cs.tertiary;
      case 'establishing':
        return cs.error;
      default:
        return cs.outline;
    }
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;
    final color = _roleColor(role, cs);
    final icon = _roleIcons[role] ?? Icons.label_rounded;

    return Semantics(
      label: role,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
        decoration: BoxDecoration(
          color: color.withAlpha(20),
          borderRadius: BorderRadius.circular(6),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 12, color: color),
            const SizedBox(width: 3),
            Text(
              role[0].toUpperCase() + role.substring(1),
              style: textTheme.labelSmall?.copyWith(
                fontWeight: FontWeight.w600,
                color: color,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Fila compacta que muestra el rango horario inicio–fin de una ubicación de película, formateado desde segundos.
class _TimeRange extends StatelessWidget {
  final double? startTime;
  final double? endTime;

  const _TimeRange({this.startTime, this.endTime});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final l10n = AppLocalizations.of(context)!;

    final start = startTime != null ? _formatTime(startTime!) : '--:--';
    final end = endTime != null ? _formatTime(endTime!) : '--:--';

    return Semantics(
      label: l10n.timeRange(start, end),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.schedule_rounded, size: 12, color: colorScheme.onSurfaceVariant.withAlpha(150)),
          const SizedBox(width: 3),
          Text(
            '$start – $end',
            style: TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.w500,
              color: colorScheme.onSurfaceVariant.withAlpha(180),
            ),
          ),
        ],
      ),
    );
  }

  /// Formatea los segundos desde medianoche como `HH:MM:SS`, omitiendo las horas cuando son cero.
  String _formatTime(double seconds) {
    final total = seconds.toInt();
    final h = total ~/ 3600;
    final m = (total % 3600) ~/ 60;
    final s = total % 60;
    if (h > 0) return '${h.toString().padLeft(2, '0')}:${m.toString().padLeft(2, '0')}:${s.toString().padLeft(2, '0')}';
    return '${m.toString().padLeft(2, '0')}:${s.toString().padLeft(2, '0')}';
  }
}
