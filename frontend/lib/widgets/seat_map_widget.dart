import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../models/event_model.dart';

/// Mapa de asientos interactivo que renderiza los asientos por sección con colores de estado y leyenda.
///
/// Úsalo para mostrar y seleccionar asientos de un evento. Los asientos se disponen
/// en una cuadrícula con escala por sección; los asientos disponibles y asignados son
/// pulsables mediante [onSeatTap], y [selectedSeatIds] resalta la selección del usuario.
/// Muestra un mensaje de vacío cuando no hay asientos.
class SeatMapWidget extends StatelessWidget {
  final List<EventSeat> seats;
  final Set<int> selectedSeatIds;
  final void Function(EventSeat seat)? onSeatTap;

  const SeatMapWidget({
    super.key,
    required this.seats,
    this.selectedSeatIds = const {},
    this.onSeatTap,
  });

  /// Devuelve el color usado para renderizar un asiento según el estado dado.
  Color _statusColor(String status, ColorScheme cs) {
    switch (status) {
      case 'available':
        return cs.tertiary;
      case 'reserved':
      case 'sold':
        return cs.error;
      case 'assigned':
        return cs.secondary;
      case 'blocked':
      default:
        return cs.surfaceContainerHighest;
    }
  }

  Color _statusTextColor(String status, ColorScheme cs) {
    switch (status) {
      case 'available':
        return cs.onTertiary;
      case 'reserved':
      case 'sold':
        return cs.onError;
      case 'assigned':
        return cs.onSecondary;
      case 'blocked':
      default:
        return cs.onSurfaceVariant;
    }
  }

  /// Devuelve la etiqueta localizada para el estado de asiento dado.
  String _statusLabel(String status, AppLocalizations l10n) {
    switch (status) {
      case 'available':
        return l10n.seatAvailable;
      case 'reserved':
        return l10n.seatReserved;
      case 'sold':
        return l10n.seatSold;
      case 'assigned':
        return l10n.seatAssigned;
      case 'blocked':
        return l10n.seatBlocked;
      default:
        return status;
    }
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final l10n = AppLocalizations.of(context)!;
    if (seats.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.event_seat_outlined, size: 64, color: cs.onSurfaceVariant.withAlpha(80)),
              const SizedBox(height: 16),
              Text(l10n.noSeatsConfigured, style: TextStyle(color: cs.onSurfaceVariant)),
            ],
          ),
        ),
      );
    }

    final sections = seats.map((s) => s.section).toSet().toList()..sort();

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          for (final section in sections) ...[
            if (sections.length > 1)
              Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Text(section, style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600, color: cs.primary)),
              ),
            LayoutBuilder(
              builder: (context, constraints) {
                final sectionSeats = seats.where((s) => s.section == section && s.x != null && s.y != null).toList();
                if (sectionSeats.isEmpty) return const SizedBox.shrink();
                final xs = sectionSeats.map((s) => s.x ?? 0).toList();
                final ys = sectionSeats.map((s) => s.y ?? 0).toList();
                if (xs.isEmpty || ys.isEmpty) return const SizedBox.shrink();
                final sMinX = xs.reduce((a, b) => a < b ? a : b);
                final sMaxX = xs.reduce((a, b) => a > b ? a : b);
                final sMinY = ys.reduce((a, b) => a < b ? a : b);
                final sMaxY = ys.reduce((a, b) => a > b ? a : b);
                final rangeX = sMaxX - sMinX;
                final rangeY = sMaxY - sMinY;
                const seatSize = 32.0;
                const gap = 4.0;
                final gridW = (rangeX + 1) * (seatSize + gap);
                final gridH = (rangeY + 1) * (seatSize + gap);
                final scale = constraints.maxWidth / gridW;
                final effectiveScale = scale < 1 ? scale : 1.0;

                return SizedBox(
                  width: constraints.maxWidth,
                  height: gridH * effectiveScale,
                  child: Stack(
                    children: [
                      for (final seat in sectionSeats)
                        Positioned(
                          left: ((seat.x ?? sMinX) - sMinX) * (seatSize + gap) * effectiveScale + gap,
                          top: ((seat.y ?? sMinY) - sMinY) * (seatSize + gap) * effectiveScale + gap,
                          child: Semantics(
                            label: '${l10n.seat} ${seat.rowLabel ?? ''} ${seat.number ?? ''} ${_statusLabel(seat.status, l10n)}',
                            child: GestureDetector(
                              onTap: seat.status == 'available' || seat.status == 'assigned'
                                  ? () => onSeatTap?.call(seat)
                                  : null,
                              child: Container(
                                width: seatSize * effectiveScale,
                                height: seatSize * effectiveScale,
                                decoration: BoxDecoration(
                                  color: selectedSeatIds.contains(seat.id)
                                      ? cs.primary
                                      : _statusColor(seat.status, cs),
                                  borderRadius: BorderRadius.circular(4),
                                  border: Border.all(
                                    color: selectedSeatIds.contains(seat.id)
                                        ? cs.primaryContainer
                                        : cs.outline.withAlpha(60),
                                    width: 1,
                                  ),
                                ),
                                alignment: Alignment.center,
                                child: Text(
                                  '${seat.rowLabel ?? ''}${seat.number ?? ''}',
                                  style: TextStyle(
                                    fontSize: 8 * effectiveScale,
                                    color: selectedSeatIds.contains(seat.id)
                                        ? cs.onPrimary
                                        : _statusTextColor(seat.status, cs),
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ),
                            ),
                          ),
                        ),
                    ],
                  ),
                );
              },
            ),
            const SizedBox(height: 16),
          ],
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: cs.surfaceContainerHighest.withAlpha(80),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Wrap(
              spacing: 16,
              runSpacing: 8,
              children: [
                _legendItem(context, cs.tertiary, l10n.seatAvailable),
                _legendItem(context, cs.error, l10n.seatReservedOrSold),
                _legendItem(context, cs.secondary, l10n.seatAssigned),
                _legendItem(context, cs.surfaceContainerHighest, l10n.seatBlocked),
                if (selectedSeatIds.isNotEmpty)
                  _legendItem(context, cs.primary, l10n.seatSelected),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// Construye una fila individual de la leyenda de colores de estado.
  Widget _legendItem(BuildContext context, Color color, String label) {
    final cs = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 14,
          height: 14,
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(3),
            border: Border.all(color: cs.outline.withAlpha(60)),
          ),
        ),
        const SizedBox(width: 6),
        Text(label, style: textTheme.labelMedium?.copyWith(color: cs.onSurfaceVariant)),
      ],
    );
  }
}
