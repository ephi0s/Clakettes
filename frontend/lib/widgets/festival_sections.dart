import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../l10n/app_localizations.dart';
import '../models/festival_rulebook_model.dart';
import '../models/location_model.dart';
import '../services/api_service.dart';
import 'reusable_widgets.dart';

/// Vista previa de las bases del festival con enlace a la lista completa.
class RulebooksSection extends StatelessWidget {
  final AppLocalizations l10n;
  final List<FestivalRulebook> rulebooks;
  final bool loading;
  final VoidCallback onOpenList;
  final Future<void> Function(String url) onOpenUrl;

  const RulebooksSection({
    super.key,
    required this.l10n,
    required this.rulebooks,
    required this.loading,
    required this.onOpenList,
    required this.onOpenUrl,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    if (loading) {
      return Container(
        width: double.infinity,
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: colorScheme.surfaceContainerLow,
          borderRadius: BorderRadius.circular(12),
        ),
        child: const Center(
          child: Padding(
            padding: EdgeInsets.all(8),
            child: CircularProgressIndicator(strokeWidth: 2),
          ),
        ),
      );
    }
    if (rulebooks.isEmpty) return const SizedBox.shrink();
    final preview = rulebooks.take(3).toList();
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainerLow,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: SemanticHeader(
                  text: l10n.rulebooks,
                  style: theme.textTheme.titleSmall?.copyWith(
                    color: colorScheme.primary,
                  ),
                ),
              ),
              TextButton(
                onPressed: onOpenList,
                child: Text(l10n.viewAll),
              ),
            ],
          ),
          const SizedBox(height: 8),
          ...preview.map((r) {
            final url = r.documentUrl;
            final resolved = url.startsWith('http://') || url.startsWith('https://')
                ? url
                : '${ApiService().rootUrl}$url';
            return Semantics(
              label: r.title,
              button: r.hasDocument,
              child: InkWell(
                borderRadius: BorderRadius.circular(10),
                onTap: r.hasDocument ? () => onOpenUrl(resolved) : null,
                child: Padding(
                  padding: const EdgeInsets.symmetric(vertical: 8),
                  child: Row(
                    children: [
                      Icon(
                        r.fileUrl != null ? Icons.picture_as_pdf_outlined : Icons.link,
                        size: 20,
                        color: colorScheme.primary,
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              r.title,
                              style: theme.textTheme.bodyMedium?.copyWith(
                                fontWeight: FontWeight.w600,
                              ),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                            Text(
                              l10n.getRulebookCategory(r.category),
                              style: theme.textTheme.bodySmall?.copyWith(
                                color: colorScheme.onSurfaceVariant,
                              ),
                            ),
                          ],
                        ),
                      ),
                      if (r.hasDocument)
                        Icon(
                          Icons.open_in_new,
                          size: 18,
                          color: colorScheme.onSurfaceVariant,
                        ),
                    ],
                  ),
                ),
              ),
            );
          }),
        ],
      ),
    );
  }
}

/// Sección de localizaciones del festival con mini mapa y fichas.
class FestivalLocationsSection extends StatelessWidget {
  final AppLocalizations l10n;
  final List<Location> locations;
  final bool loading;
  final bool isLoggedIn;
  final VoidCallback onAdd;
  final Future<void> Function(Location location) onRemove;
  final void Function(Location location) onOpen;

  const FestivalLocationsSection({
    super.key,
    required this.l10n,
    required this.locations,
    required this.loading,
    required this.isLoggedIn,
    required this.onAdd,
    required this.onRemove,
    required this.onOpen,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    if (loading) {
      return Container(
        width: double.infinity,
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: colorScheme.surfaceContainerLow,
          borderRadius: BorderRadius.circular(12),
        ),
        child: const Center(
          child: Padding(
            padding: EdgeInsets.all(8),
            child: CircularProgressIndicator(strokeWidth: 2),
          ),
        ),
      );
    }
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainerLow,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: SemanticHeader(
                  text: l10n.locations,
                  style: theme.textTheme.titleSmall?.copyWith(
                    color: colorScheme.primary,
                  ),
                ),
              ),
              if (isLoggedIn)
                Semantics(
                  label: l10n.addLocation,
                  button: true,
                  child: Tooltip(
                    message: l10n.addLocation,
                    child: IconButton(
                      icon: const Icon(Icons.add_location_alt_outlined),
                      onPressed: onAdd,
                    ),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 12),
          if (locations.isEmpty)
            Semantics(
              label: l10n.noLocations,
              child: InkWell(
                onTap: isLoggedIn ? onAdd : null,
                borderRadius: BorderRadius.circular(8),
                child: Padding(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  child: Column(
                    children: [
                      Icon(
                        Icons.location_off_outlined,
                        size: 32,
                        color: colorScheme.onSurfaceVariant.withAlpha(140),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        l10n.noLocations,
                        style: theme.textTheme.bodyMedium?.copyWith(
                          color: colorScheme.onSurfaceVariant,
                        ),
                        textAlign: TextAlign.center,
                      ),
                      if (isLoggedIn) ...[
                        const SizedBox(height: 4),
                        Text(
                          l10n.addLocation,
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: colorScheme.primary,
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ),
            )
          else ...[
            _LocationsMap(l10n: l10n, locations: locations, onOpen: onOpen),
            const SizedBox(height: 8),
            ...locations.map(
              (loc) => _LocationTile(
                l10n: l10n,
                loc: loc,
                isLoggedIn: isLoggedIn,
                onOpen: onOpen,
                onRemove: onRemove,
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class _LocationsMap extends StatelessWidget {
  final AppLocalizations l10n;
  final List<Location> locations;
  final void Function(Location location) onOpen;

  const _LocationsMap({required this.l10n, required this.locations, required this.onOpen});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    if (locations.isEmpty) return const SizedBox.shrink();
    final centerLat =
        locations.map((l) => l.latitude).reduce((a, b) => a + b) /
            locations.length;
    final centerLng =
        locations.map((l) => l.longitude).reduce((a, b) => a + b) /
            locations.length;
    return SizedBox(
      height: 200,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(12),
        child: FlutterMap(
          options: MapOptions(
            initialCenter: LatLng(centerLat, centerLng),
            initialZoom: 12,
            interactionOptions: const InteractionOptions(
              flags: InteractiveFlag.all,
            ),
          ),
          children: [
            TileLayer(
              urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
              userAgentPackageName: 'com.clakettes.app',
            ),
            MarkerLayer(
              markers: locations.map((loc) {
                return Marker(
                  point: LatLng(loc.latitude, loc.longitude),
                  width: 140,
                  height: 90,
                  child: GestureDetector(
                    onTap: () => onOpen(loc),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          Icons.place,
                          color: colorScheme.primary,
                          size: 36,
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 8,
                            vertical: 2,
                          ),
                          decoration: BoxDecoration(
                            color: colorScheme.surfaceContainerHighest,
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Text(
                            loc.name,
                            style: theme.textTheme.bodySmall?.copyWith(
                              fontWeight: FontWeight.w600,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              }).toList(),
            ),
          ],
        ),
      ),
    );
  }
}

class _LocationTile extends StatelessWidget {
  final AppLocalizations l10n;
  final Location loc;
  final bool isLoggedIn;
  final void Function(Location location) onOpen;
  final Future<void> Function(Location location) onRemove;

  const _LocationTile({
    required this.l10n,
    required this.loc,
    required this.isLoggedIn,
    required this.onOpen,
    required this.onRemove,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    return Semantics(
      label: loc.name,
      button: true,
      child: InkWell(
        borderRadius: BorderRadius.circular(10),
        onTap: () => onOpen(loc),
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 8),
          child: Row(
            children: [
              Icon(
                Icons.location_on_outlined,
                size: 20,
                color: colorScheme.primary,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      loc.name,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    if (loc.description != null &&
                        loc.description!.isNotEmpty)
                      Text(
                        loc.description!,
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: colorScheme.onSurfaceVariant,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                  ],
                ),
              ),
              if (isLoggedIn)
                Semantics(
                  label: l10n.delete,
                  button: true,
                  child: Tooltip(
                    message: l10n.delete,
                    child: IconButton(
                      icon: Icon(
                        Icons.delete_outline,
                        size: 20,
                        color: colorScheme.onSurfaceVariant,
                      ),
                      onPressed: () => onRemove(loc),
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}
