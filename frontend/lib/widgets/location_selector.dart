import 'dart:async';

import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../models/location_model.dart';
import '../services/api_service.dart';
import 'location_badge_chip.dart';

/// Selector de ubicaciones en bottom sheet con búsqueda, paginación y solo resultados activos.
///
/// Úsalo cuando el usuario deba elegir una ubicación existente. Obtiene las ubicaciones
/// activas de la API con búsqueda con retardo e infinito scroll, excluyendo [excludeId]
/// (p. ej. la ubicación que se está editando). Invoca [onSelected] cuando se elige una.
class LocationSelector extends StatefulWidget {
  final ValueChanged<Location> onSelected;
  final int? excludeId;

  const LocationSelector({
    super.key,
    required this.onSelected,
    this.excludeId,
  });

  /// Abre [LocationSelector] en un bottom sheet modal con desplazamiento.
  static Future<void> show(
    BuildContext context, {
    required ValueChanged<Location> onSelected,
    int? excludeId,
  }) {
    return showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      useSafeArea: true,
      builder: (_) => LocationSelector(
        onSelected: onSelected,
        excludeId: excludeId,
      ),
    );
  }

  @override
  State<LocationSelector> createState() => _LocationSelectorState();
}

class _LocationSelectorState extends State<LocationSelector> {
  final ApiService _api = ApiService();
  final TextEditingController _searchCtrl = TextEditingController();
  List<Location> _locations = [];
  bool _isLoading = true;
  bool _hasError = false;
  bool _isSearching = false;
  int _currentPage = 1;
  bool _hasMore = true;
  Timer? _searchDebounce;

  @override
  void initState() {
    super.initState();
    _loadLocations();
  }

  @override
  void dispose() {
    _searchDebounce?.cancel();
    _searchCtrl.dispose();
    super.dispose();
  }

  /// Carga una página de ubicaciones activas, opcionalmente filtrada por [search].
  Future<void> _loadLocations({String? search}) async {
    setState(() {
      _isLoading = _currentPage == 1;
      _isSearching = search != null && search.isNotEmpty;
    });

    try {
      final result = await _api.getLocations(
        page: _currentPage,
        size: 20,
        search: search,
        isActive: true,
      );
      setState(() {
        _locations = result.items.where((l) => l.id != widget.excludeId).toList();
        _hasMore = _currentPage < result.pages;
        _isLoading = false;
        _hasError = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
        _hasError = true;
      });
    }
  }

  /// Manejador de búsqueda con retardo que reinicia la paginación antes de consultar.
  void _onSearchChanged(String query) {
    _searchDebounce?.cancel();
    _searchDebounce = Timer(const Duration(milliseconds: 400), () {
      _currentPage = 1;
      _loadLocations(search: query.trim().isEmpty ? null : query.trim());
    });
  }

  void _loadMore() {
    if (_hasMore && !_isLoading) {
      _currentPage++;
      _loadLocations(search: _searchCtrl.text.trim().isEmpty ? null : _searchCtrl.text.trim());
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final l10n = AppLocalizations.of(context)!;

    return DraggableScrollableSheet(
      initialChildSize: 0.7,
      minChildSize: 0.4,
      maxChildSize: 0.9,
      expand: false,
      builder: (context, scrollController) {
        return Column(
          children: [
            Container(
              margin: const EdgeInsets.only(top: 8),
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: colorScheme.outlineVariant,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
              child: Row(
                children: [
                  Expanded(
                    child: Semantics(
                      label: l10n.searchLocations,
                      child: TextField(
                        controller: _searchCtrl,
                        autofocus: true,
                        decoration: InputDecoration(
                          hintText: l10n.searchLocations,
                          prefixIcon: const Icon(Icons.search_rounded, size: 20),
                          suffixIcon: _searchCtrl.text.isNotEmpty
                              ? IconButton(
                                  icon: const Icon(Icons.clear_rounded, size: 18),
                                  onPressed: () {
                                    _searchCtrl.clear();
                                    _onSearchChanged('');
                                  },
                                )
                              : null,
                          isDense: true,
                          contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                        ),
                        textInputAction: TextInputAction.search,
                        onChanged: _onSearchChanged,
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  TextButton(
                    onPressed: () => Navigator.pop(context),
                    child: Text(l10n.close),
                  ),
                ],
              ),
            ),
            const Divider(height: 1),
            Expanded(
              child: _buildContent(context, scrollController),
            ),
          ],
        );
      },
    );
  }

  Widget _buildContent(BuildContext context, ScrollController scrollController) {
    final l10n = AppLocalizations.of(context)!;

    if (_isLoading && _locations.isEmpty) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_hasError) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.error_outline_rounded, size: 40, color: Theme.of(context).colorScheme.error),
            const SizedBox(height: 12),
            Text(l10n.loadError),
            const SizedBox(height: 12),
            FilledButton.tonal(
              onPressed: () => _loadLocations(search: _searchCtrl.text.trim().isEmpty ? null : _searchCtrl.text.trim()),
              child: Text(l10n.retry),
            ),
          ],
        ),
      );
    }

    if (_locations.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.location_off_rounded, size: 40, color: Theme.of(context).colorScheme.onSurfaceVariant.withAlpha(100)),
            const SizedBox(height: 12),
            Text(l10n.noLocations),
            if (_isSearching) ...[
              const SizedBox(height: 4),
              Text(l10n.tryDifferentSearch, style: Theme.of(context).textTheme.bodySmall),
            ],
          ],
        ),
      );
    }

    return NotificationListener<ScrollNotification>(
      onNotification: (notification) {
        if (notification is ScrollEndNotification &&
            notification.metrics.pixels >= notification.metrics.maxScrollExtent - 100) {
          _loadMore();
        }
        return false;
      },
      child: ListView.builder(
        controller: scrollController,
        padding: const EdgeInsets.symmetric(vertical: 4),
        itemCount: _locations.length + (_hasMore ? 1 : 0),
        itemBuilder: (context, index) {
          if (index == _locations.length) {
            return const Center(
              child: Padding(
                padding: EdgeInsets.all(16),
                child: CircularProgressIndicator(strokeWidth: 2),
              ),
            );
          }
          return _LocationPreviewTile(
            location: _locations[index],
            onTap: () {
              widget.onSelected(_locations[index]);
              Navigator.pop(context);
            },
          );
        },
      ),
    );
  }
}

/// Tile de lista que previsualiza una ubicación con miniatura, insignia y etiquetas.
class _LocationPreviewTile extends StatelessWidget {
  final Location location;
  final VoidCallback onTap;

  const _LocationPreviewTile({
    required this.location,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Semantics(
      label: location.name,
      button: true,
      child: ListTile(
        leading: Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            color: colorScheme.surfaceContainerHighest.withAlpha(80),
            borderRadius: BorderRadius.circular(10),
          ),
          clipBehavior: Clip.antiAlias,
          child: location.locationImages.isNotEmpty
              ? Image.network(
                  location.locationImages.first.url,
                  width: 44,
                  height: 44,
                  cacheWidth: (44 * MediaQuery.devicePixelRatioOf(context)).round(),
                  cacheHeight: (44 * MediaQuery.devicePixelRatioOf(context)).round(),
                  fit: BoxFit.cover,
                  errorBuilder: (_, __, ___) => _buildIcon(context),
                )
              : _buildIcon(context),
        ),
        title: Text(
          location.name,
          style: TextStyle(fontWeight: FontWeight.w600, color: colorScheme.onSurface),
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        subtitle: Row(
          children: [
            if (location.badge != null && location.badge!.isNotEmpty) ...[
              LocationBadgeChip(badge: location.badge, small: true),
              const SizedBox(width: 6),
            ],
            if (location.tags.isNotEmpty) ...[
              Icon(Icons.label_rounded, size: 12, color: colorScheme.onSurfaceVariant.withAlpha(150)),
              const SizedBox(width: 3),
              Text(
                location.tags.take(3).join(', '),
                style: TextStyle(
                  fontSize: 12,
                  color: colorScheme.onSurfaceVariant,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ],
        ),
        trailing: Icon(Icons.chevron_right_rounded, color: colorScheme.onSurfaceVariant.withAlpha(120), size: 20),
        onTap: onTap,
      ),
    );
  }

  Widget _buildIcon(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return Center(
      child: Icon(Icons.location_on_rounded, size: 22, color: colorScheme.onSurfaceVariant.withAlpha(150)),
    );
  }
}
