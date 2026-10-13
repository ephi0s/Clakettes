import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:http/http.dart' as http;
import 'package:latlong2/latlong.dart';
import '../l10n/app_localizations.dart';

/// Selector de mapa a pantalla completa para elegir las coordenadas de una ubicación.
///
/// Úsalo cuando una ubicación necesite coordenadas. Muestra un mapa de teselas
/// OpenStreetMap con un cuadro de búsqueda respaldado por Nominatim; al tocar el mapa
/// o un resultado de búsqueda se selecciona un punto. Se cierra con el [LatLng] elegido
/// (o null) al guardar.
class MapPickerScreen extends StatefulWidget {
  final AppLocalizations l10n;
  final LatLng? initialLocation;

  const MapPickerScreen({
    super.key,
    required this.l10n,
    this.initialLocation,
  });

  @override
  State<MapPickerScreen> createState() => _MapPickerScreenState();
}

class _MapPickerScreenState extends State<MapPickerScreen> {
  final MapController _mapController = MapController();
  final TextEditingController _searchCtrl = TextEditingController();

  LatLng? _selectedLatLng;
  bool _isSearching = false;
  List<Map<String, dynamic>> _searchResults = [];
  late LatLng _center;

  @override
  void initState() {
    super.initState();
    _selectedLatLng = widget.initialLocation;
    _center = widget.initialLocation ?? const LatLng(40.4168, -3.7038);
  }

  @override
  void dispose() {
    _mapController.dispose();
    _searchCtrl.dispose();
    super.dispose();
  }

  /// Geocodifica [query] mediante Nominatim y guarda hasta 5 resultados candidatos.
  Future<void> _searchLocation(String query) async {
    if (query.trim().isEmpty) return;
    setState(() => _isSearching = true);
    try {
      final uri = Uri.parse(
        'https://nominatim.openstreetmap.org/search?q=${Uri.encodeComponent(query)}&format=json&limit=5',
      );
      final response = await http.get(uri, headers: {
        'User-Agent': 'Clakettes/1.0',
      });
      if (response.statusCode == 200 && mounted) {
        final data = json.decode(response.body) as List;
        setState(() {
          _searchResults = data.cast<Map<String, dynamic>>();
          _isSearching = false;
        });
      } else {
        if (mounted) setState(() => _isSearching = false);
      }
    } catch (e) {
      debugPrint('Error: $e');
      if (mounted) setState(() => _isSearching = false);
    }
  }

  /// Selecciona un resultado de Nominatim, centra el mapa en él y limpia la búsqueda.
  void _selectSearchResult(Map<String, dynamic> result) {
    final lat = double.parse(result['lat']);
    final lng = double.parse(result['lon']);
    final latLng = LatLng(lat, lng);
    setState(() {
      _selectedLatLng = latLng;
      _center = latLng;
      _searchResults = [];
      _searchCtrl.clear();
    });
    _mapController.move(latLng, 15);
  }

  @override
  Widget build(BuildContext context) {
    final l10n = widget.l10n;
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.addLocation),
        leading: IconButton(
          tooltip: MaterialLocalizations.of(context).closeButtonTooltip,
          icon: const Icon(Icons.close),
          onPressed: () => Navigator.pop(context),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, _selectedLatLng),
            child: Text(l10n.save),
          ),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(12, 8, 12, 0),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: _searchCtrl,
                  decoration: InputDecoration(
                    hintText: l10n.search,
                    prefixIcon: const Icon(Icons.search),
                    suffixIcon: _isSearching
                        ? const Padding(
                            padding: EdgeInsets.all(12),
                            child: SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            ),
                          )
                        : IconButton(
                            tooltip: l10n.clear,
                            icon: const Icon(Icons.clear),
                            onPressed: () {
                              _searchCtrl.clear();
                              setState(() => _searchResults = []);
                            },
                          ),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    contentPadding:
                        const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    filled: true,
                  ),
                  onSubmitted: _searchLocation,
                  textInputAction: TextInputAction.search,
                ),
                if (_searchResults.isNotEmpty)
                  ClipRRect(
                    borderRadius: const BorderRadius.vertical(
                        bottom: Radius.circular(12)),
                    child: Container(
                      constraints: const BoxConstraints(maxHeight: 200),
                      decoration: BoxDecoration(
                        color: theme.colorScheme.surfaceContainerHighest,
                      ),
                      child: ListView.builder(
                        shrinkWrap: true,
                        padding: EdgeInsets.zero,
                        itemCount: _searchResults.length,
                        itemBuilder: (_, i) {
                          final result = _searchResults[i];
                          final displayName =
                              result['display_name']?.toString() ?? '';
                          final parts = displayName.split(', ');
                          final shortName = parts.length > 3
                              ? '${parts.take(3).join(', ')}, …'
                              : displayName;
                          return ListTile(
                            leading: Icon(Icons.place,
                                color: theme.colorScheme.primary),
                            title: Text(shortName,
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis),
                            dense: true,
                            onTap: () => _selectSearchResult(result),
                          );
                        },
                      ),
                    ),
                  ),
              ],
            ),
          ),
          Expanded(
            child: Stack(
              children: [
                FlutterMap(
                  mapController: _mapController,
                  options: MapOptions(
                    initialCenter: _center,
                    initialZoom: _selectedLatLng != null ? 13 : 5,
                    onTap: (_, latLng) {
                      setState(() => _selectedLatLng = latLng);
                    },
                  ),
                  children: [
                    TileLayer(
                      urlTemplate:
                          'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                      userAgentPackageName: 'com.clakettes.app',
                    ),
                    if (_selectedLatLng != null)
                      MarkerLayer(
                        markers: [
                          Marker(
                            point: _selectedLatLng!,
                            width: 80,
                            height: 80,
                            child: const Column(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Icon(Icons.place, color: Colors.red, size: 44),
                              ],
                            ),
                          ),
                        ],
                      ),
                  ],
                ),
                if (_selectedLatLng != null)
                  Positioned(
                    left: 16,
                    right: 16,
                    bottom: 16,
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 12, vertical: 8),
                      decoration: BoxDecoration(
                        color: theme.colorScheme.surface.withAlpha(220),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.explore,
                              size: 14,
                              color: theme.colorScheme.onSurfaceVariant),
                          const SizedBox(width: 6),
                          Flexible(
                            child: Text(
                              '${_selectedLatLng!.latitude.toStringAsFixed(6)}, ${_selectedLatLng!.longitude.toStringAsFixed(6)}',
                              style: theme.textTheme.bodySmall?.copyWith(
                                fontFamily: 'monospace',
                                color: theme.colorScheme.onSurfaceVariant,
                              ),
                              textAlign: TextAlign.center,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
