import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:url_launcher/url_launcher.dart';
import '../l10n/app_localizations.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import '../widgets/reusable_widgets.dart';
import '../widgets/empty_state_widget.dart';
import '../widgets/error_state_widget.dart';
import '../widgets/location_cards.dart';
import '../widgets/confirm_dialog.dart';
import '../models/location_model.dart';
import 'festival_profile_screen.dart';
import 'user_profile_screen.dart';
import 'location_detail_screen.dart';

/// Pantalla que lista todas las localizaciones con búsqueda, filtro por
/// insignia y alternancia lista/mapa. Los administradores pueden añadir y
/// eliminar localizaciones.
class LocationsScreen extends StatefulWidget {
  const LocationsScreen({super.key});

  @override
  State<LocationsScreen> createState() => _LocationsScreenState();
}

/// Estado de [LocationsScreen]. Carga las localizaciones activas y las
/// coordenadas heredadas de festivales/usuarios en el primer build y mantiene
/// los valores de búsqueda y filtro por insignia.
class _LocationsScreenState extends State<LocationsScreen> {
  List<Location> _locations = [];
  List<LegacyLocation> _legacyLocations = [];
  bool _isLoading = true;
  bool _hasError = false;
  bool _isAdmin = false;
  bool _showList = true;
  bool _initialized = false;
  late AppLocalizations l10n;
  final TextEditingController _searchCtrl = TextEditingController();
  String _searchQuery = '';
  String? _selectedBadge;

  static const double _defaultLat = 40.4168;
  static const double _defaultLng = -3.7038;

  static const List<String?> _badgeFilters = [null, 'Sugerido', 'Obligatorio', 'Destacado'];

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    l10n = AppLocalizations.of(context)!;
    if (!_initialized) {
      _initialized = true;
      _loadLocations();
    }
  }

/// Obtiene las localizaciones activas y construye puntos heredados a partir
/// de festivales y usuarios públicos que tienen coordenadas.
  Future<void> _loadLocations() async {
    setState(() {
      _isLoading = true;
      _hasError = false;
    });

    try {
      final user = await AuthService().getCurrentUser();
      _isAdmin = user?.role?.toLowerCase() == 'admin';

      final locationResult = await ApiService().getLocations(size: 100, isActive: true);

      final legacy = <LegacyLocation>[];

      try {
        final festivalResult = await ApiService().getFestivals(size: 100);
        for (final f in festivalResult.items) {
          if (f.latitude != null && f.longitude != null) {
            legacy.add(LegacyLocation(
              name: f.name,
              latitude: f.latitude!,
              longitude: f.longitude!,
              type: 'Festival',
              subtitle: f.location,
              sourceId: f.id?.toString(),
            ));
          }
        }
      } catch (e) {
        debugPrint('Error: $e');
      }

      try {
        final userResult = await ApiService().getUsers(size: 100);
        for (final u in userResult.items) {
          if (u.latitude != null && u.longitude != null && u.isPublic) {
            legacy.add(LegacyLocation(
              name: u.fullName ?? u.username,
              latitude: u.latitude!,
              longitude: u.longitude!,
              type: 'User',
              subtitle: u.role,
              sourceId: u.id?.toString(),
            ));
          }
        }
      } catch (e) {
        debugPrint('Error: $e');
      }

      if (mounted) {
        setState(() {
          _locations = locationResult.items;
          _legacyLocations = legacy;
          _isLoading = false;
        });
      }
    } catch (e) {
      debugPrint('Error: $e');
      if (mounted) {
        setState(() {
          _isLoading = false;
          _hasError = true;
        });
      }
    }
  }

  /// Localizaciones filtradas por la insignia seleccionada y la búsqueda.
  List<Location> get _filteredLocations {
    var result = _locations;
    if (_selectedBadge != null) {
      result = result.where((l) => l.badge == _selectedBadge).toList();
    }
    if (_searchQuery.isEmpty) return result;
    final q = _searchQuery.toLowerCase();
    return result.where((l) {
      return l.name.toLowerCase().contains(q) ||
          (l.description?.toLowerCase().contains(q) ?? false) ||
          (l.address?.toLowerCase().contains(q) ?? false) ||
          l.tags.any((t) => t.toLowerCase().contains(q));
    }).toList();
  }

  /// Puntos heredados de festivales/usuarios filtrados por la búsqueda.
  List<LegacyLocation> get _filteredLegacy {
    if (_searchQuery.isEmpty) return _legacyLocations;
    final q = _searchQuery.toLowerCase();
    return _legacyLocations.where((l) {
      return l.name.toLowerCase().contains(q) ||
          (l.subtitle?.toLowerCase().contains(q) ?? false) ||
          l.type.toLowerCase().contains(q);
    }).toList();
  }

  /// Media de todas las coordenadas visibles, usada como centro inicial del mapa.
  LatLng _mapCenter() {
    final all = <LatLng>[
      ..._locations.map((l) => LatLng(l.latitude, l.longitude)),
      ..._legacyLocations.map((l) => LatLng(l.latitude, l.longitude)),
    ];
    if (all.isEmpty) return const LatLng(_defaultLat, _defaultLng);
    final avgLat = all.map((p) => p.latitude).reduce((a, b) => a + b) / all.length;
    final avgLng = all.map((p) => p.longitude).reduce((a, b) => a + b) / all.length;
    return LatLng(avgLat, avgLng);
  }

  /// Abre el formulario de localización y la crea cuando devuelve un resultado.
  Future<void> _addLocation() async {
    final result = await Navigator.push<LocationFormResult>(
      context,
      MaterialPageRoute(
        builder: (_) => const LocationFormScreen(),
      ),
    );

    if (result != null) {
      try {
        await ApiService().createLocation(Location(
          name: result.name,
          description: result.description,
          address: result.address,
          latitude: result.latitude,
          longitude: result.longitude,
          tags: result.tags,
        ));
        _loadLocations();
      } catch (e) {
        if (mounted) showAppSnack(context, '${l10n.error}: $e');
      }
    }
  }

  /// Pide confirmación y elimina la localización indicada.
  Future<void> _deleteLocation(Location location) async {
    if (location.id == null) return;
    final confirmed = await showConfirmDialog(
      context,
      title: l10n.confirmDelete,
      message: '${l10n.delete} "${location.name}"?',
    );
    if (confirmed == true) {
      try {
        await ApiService().deleteLocation(location.id!);
        _loadLocations();
      } catch (e) {
        if (mounted) showAppSnack(context, '${l10n.error}: $e');
      }
    }
  }

/// Abre la localización en la app de mapas del sistema, usando
/// OpenStreetMap cuando el esquema geo no está disponible.
  Future<void> _openInMaps(double lat, double lng, String label) async {
    final encodedLabel = Uri.encodeComponent(label);
    final geoUri = Uri.parse('geo:0,0?q=$lat,$lng($encodedLabel)');
    if (await canLaunchUrl(geoUri)) {
      await launchUrl(geoUri);
      return;
    }
    final osmUri = Uri.parse('https://www.openstreetmap.org/?mlat=$lat&mlon=$lng');
    if (await canLaunchUrl(osmUri)) {
      if (kIsWeb) {
        await launchUrl(osmUri, webOnlyWindowName: '_blank');
      } else {
        await launchUrl(osmUri, mode: LaunchMode.externalApplication);
      }
    }
  }

  /// Abre la pantalla de detalle de la localización y recarga la lista si cambió.
  void _openLocationDetail(Location location) async {
    if (location.id == null) return;
    final changed = await Navigator.push<bool>(
      context,
      MaterialPageRoute(builder: (_) => LocationDetailScreen(locationId: location.id!)),
    );
    if (changed == true && mounted) {
      _loadLocations();
    }
  }

  /// Muestra una hoja inferior con los detalles del punto heredado y un mini mapa.
  void _showLegacyDetails(LegacyLocation location) {
    showModalBottomSheet(
      context: context,
      builder: (ctx) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(16, 16, 16, 24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  _legacyIcon(location.type),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Semantics(
                      header: true,
                      child: Text(location.name, style: Theme.of(ctx).textTheme.titleLarge),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              InfoRow(icon: Icons.category, semanticLabel: '${l10n.location}: ${l10n.getLocationTypeTranslation(location.type)}', text: l10n.getLocationTypeTranslation(location.type)),
              const SizedBox(height: 8),
              SizedBox(
                height: 150,
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(12),
                  child: Stack(
                    children: [
                      FlutterMap(
                        options: MapOptions(
                          initialCenter: LatLng(location.latitude, location.longitude),
                          initialZoom: 13,
                          interactionOptions: const InteractionOptions(flags: InteractiveFlag.all),
                        ),
                        children: [
                          TileLayer(
                            urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                            userAgentPackageName: 'com.clakettes.app',
                          ),
                          MarkerLayer(
                            markers: [
                              Marker(
                                point: LatLng(location.latitude, location.longitude),
                                width: 80,
                                height: 80,
                                child: Icon(Icons.place, color: Theme.of(ctx).colorScheme.primary, size: 40),
                              ),
                            ],
                          ),
                        ],
                      ),
                      Positioned(
                        top: 8,
                        right: 8,
                        child: Material(
                          color: Theme.of(ctx).colorScheme.surfaceContainerHighest,
                          borderRadius: BorderRadius.circular(24),
                          elevation: 4,
                          child: InkWell(
                            borderRadius: BorderRadius.circular(24),
                            onTap: () {
                              Navigator.pop(ctx);
                              _openInMaps(location.latitude, location.longitude, location.name);
                            },
                            child: Padding(
                              padding: const EdgeInsets.all(10),
                              child: Icon(Icons.directions, color: Theme.of(ctx).colorScheme.primary, size: 22),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              if (location.subtitle != null) ...[
                const SizedBox(height: 8),
                InfoRow(icon: Icons.description, semanticLabel: '${l10n.description}: ${location.subtitle}', text: location.subtitle!),
              ],
            ],
          ),
        ),
      ),
    );
  }

  /// Color del marcador según el tipo de punto.
  Color _markerColor(String type) {
    final cs = Theme.of(context).colorScheme;
    switch (type) {
      case 'User':
        return cs.secondary;
      default:
        return cs.primary;
    }
  }

  /// Icono y color usados para un punto heredado según su tipo.
  Widget _legacyIcon(String type) {
    final cs = Theme.of(context).colorScheme;
    final color = type == 'User' ? cs.secondary : cs.primary;
    final icon = type == 'User' ? Icons.person : Icons.festival;
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(color: color.withAlpha(25), shape: BoxShape.circle),
      child: Icon(icon, color: color, size: 20),
    );
  }

  /// Abre el perfil del festival o usuario asociado a un punto heredado.
  Future<void> _onLegacyTap(LegacyLocation location) async {
    try {
      bool? changed = false;
      if (location.type == 'Festival' && location.sourceId != null) {
        final id = int.tryParse(location.sourceId!);
        if (id == null) return;
        final festival = await ApiService().getFestival(id);
        if (mounted) {
          changed = await Navigator.push<bool>(
            context,
            MaterialPageRoute(builder: (_) => FestivalProfileScreen(festival: festival)),
          );
        }
      } else if (location.type == 'User' && location.sourceId != null) {
        final id = int.tryParse(location.sourceId!);
        if (id == null) return;
        final user = await ApiService().getUser(id);
        if (mounted) {
          changed = await Navigator.push<bool>(
            context,
            MaterialPageRoute(builder: (_) => UserProfileScreen(user: user)),
          );
        }
      }
      if (changed == true && mounted) {
        _loadLocations();
      }
    } catch (e) {
      debugPrint('Error: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.locationFetchError)));
      }
    }
  }

  @override
  void dispose() {
    _searchCtrl.dispose();
    super.dispose();
  }

  double get _topInset =>
      Navigator.canPop(context) ? 0 : MediaQuery.of(context).padding.top;

  @override
  Widget build(BuildContext context) {
    l10n = AppLocalizations.of(context)!;
    final filtered = _filteredLocations;
    final theme = Theme.of(context);

    return Scaffold(
      appBar: Navigator.canPop(context)
          ? AppBar(title: Text(l10n.locations))
          : null,
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _hasError
              ? ErrorStateWidget(onRetry: _loadLocations)
              : Stack(
                  children: [
                    _showList ? _buildListView(filtered) : _buildMapView(),
                    Positioned(
                      top: _topInset + 8,
                      left: 16,
                      right: 16,
                      child: Container(
                        padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
                        decoration: BoxDecoration(
                          color: theme.colorScheme.surface.withAlpha(230),
                          borderRadius: BorderRadius.circular(12),
                          boxShadow: [
                            BoxShadow(color: Colors.black.withAlpha(30), blurRadius: 8, offset: const Offset(0, 2)),
                          ],
                        ),
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Row(
                              children: [
                                Icon(Icons.location_on, color: theme.colorScheme.primary),
                                const SizedBox(width: 8),
                                Text(l10n.locations, style: theme.textTheme.titleMedium),
                                const Spacer(),
                                _viewToggle(theme),
                              ],
                            ),
                            const SizedBox(height: 8),
                            Row(
                              children: [
                                Expanded(
                                  child: TextField(
                                    controller: _searchCtrl,
                                    decoration: InputDecoration(
                                      hintText: l10n.search,
                                      prefixIcon: const Icon(Icons.search, size: 20),
                                      isDense: true,
                                      contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                                      border: OutlineInputBorder(
                                        borderRadius: BorderRadius.circular(8),
                                        borderSide: BorderSide.none,
                                      ),
                                      filled: true,
                                      fillColor: theme.colorScheme.surfaceContainerHighest.withAlpha(180),
                                    ),
                                    onChanged: (v) => setState(() => _searchQuery = v),
                                  ),
                                ),
                                const SizedBox(width: 8),
                                _buildBadgeFilter(theme),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
      floatingActionButton: _isAdmin
          ? Semantics(
              label: l10n.addLocation,
              child: Tooltip(
                message: l10n.addLocation,
                child: FloatingActionButton(
                  onPressed: _addLocation,
                  child: const Icon(Icons.add_location),
                ),
              ),
            )
          : null,
    );
  }

  /// Selector desplegable para filtrar por insignia.
  Widget _buildBadgeFilter(ThemeData theme) {
    return Semantics(
      label: l10n.filterByBadge,
      child: DropdownButton<String?>(
        value: _selectedBadge,
        isDense: true,
        underline: const SizedBox.shrink(),
        icon: Icon(Icons.filter_list, size: 18, color: theme.colorScheme.onSurfaceVariant),
        items: [
          DropdownMenuItem<String?>(
            value: null,
            child: Text(l10n.all, style: const TextStyle(fontSize: 12)),
          ),
          ..._badgeFilters.where((b) => b != null).map((badge) {
            return DropdownMenuItem<String?>(
              value: badge,
              child: Text(l10n.getBadgeTranslation(badge!), style: const TextStyle(fontSize: 12)),
            );
          }),
        ],
        onChanged: (v) => setState(() => _selectedBadge = v),
      ),
    );
  }

  /// Alterna entre la vista de lista y la vista de mapa.
  Widget _viewToggle(ThemeData theme) {
    return Semantics(
      label: _showList ? l10n.mapView : l10n.listView,
      child: ToggleButtons(
        isSelected: [!_showList, _showList],
        onPressed: (i) => setState(() => _showList = i == 1),
        borderRadius: BorderRadius.circular(8),
        constraints: const BoxConstraints(minWidth: 36, minHeight: 32),
        children: [
          Tooltip(message: l10n.mapView, child: const Icon(Icons.map, size: 18)),
          Tooltip(message: l10n.listView, child: const Icon(Icons.list, size: 18)),
        ],
      ),
    );
  }

  /// Construye la vista de mapa con los marcadores de localizaciones.
  Widget _buildMapView() {
    return FlutterMap(
      options: MapOptions(
        initialCenter: _mapCenter(),
        initialZoom: 11,
        onTap: (_, __) {},
      ),
      children: [
        TileLayer(
          urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
          userAgentPackageName: 'com.clakettes.app',
        ),
        MarkerLayer(
          markers: [
            ..._filteredLocations.map((location) {
              return Marker(
                point: LatLng(location.latitude, location.longitude),
                width: 130,
                height: 80,
                child: GestureDetector(
                  onTap: () => _openLocationDetail(location),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: Theme.of(context).colorScheme.primary,
                          shape: BoxShape.circle,
                          border: Border.all(color: Colors.white, width: 2),
                          boxShadow: const [
                            BoxShadow(color: Colors.black26, blurRadius: 4, offset: Offset(0, 2)),
                          ],
                        ),
                        child: const Icon(Icons.place, color: Colors.white, size: 20),
                      ),
                      Container(
                        margin: const EdgeInsets.only(top: 2),
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: Colors.black87,
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(
                          location.name,
                          style: const TextStyle(color: Colors.white, fontSize: 10),
                          overflow: TextOverflow.ellipsis,
                          maxLines: 1,
                        ),
                      ),
                    ],
                  ),
                ),
              );
            }),
            ..._filteredLegacy.map((location) {
              final color = _markerColor(location.type);
              return Marker(
                point: LatLng(location.latitude, location.longitude),
                width: 130,
                height: 80,
                child: GestureDetector(
                  onTap: () => _onLegacyTap(location),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: color,
                          shape: BoxShape.circle,
                          border: Border.all(color: Colors.white, width: 2),
                          boxShadow: const [
                            BoxShadow(color: Colors.black26, blurRadius: 4, offset: Offset(0, 2)),
                          ],
                        ),
                        child: const Icon(Icons.place, color: Colors.white, size: 20),
                      ),
                      Container(
                        margin: const EdgeInsets.only(top: 2),
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: Colors.black87,
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(
                          location.name,
                          style: const TextStyle(color: Colors.white, fontSize: 10),
                          overflow: TextOverflow.ellipsis,
                          maxLines: 1,
                        ),
                      ),
                    ],
                  ),
                ),
              );
            }),
          ],
        ),
      ],
    );
  }

  /// Construye la vista de lista con las localizaciones filtradas.
  Widget _buildListView(List<Location> locations) {
    final allLegacy = _filteredLegacy;

    if (locations.isEmpty && allLegacy.isEmpty) {
      return Center(
        child: EmptyStateWidget(
          icon: Icons.location_off,
          title: _searchQuery.isNotEmpty || _selectedBadge != null ? l10n.noLocations : l10n.subtitle,
        ),
      );
    }

    return ListView(
      padding: EdgeInsets.only(
        top: _topInset + 120,
        bottom: 80,
      ),
      children: [
        if (locations.isNotEmpty) ...[
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 4),
            child: Semantics(
              header: true,
              child: Text(
                l10n.locations,
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                ),
              ),
            ),
          ),
          ...locations.map((loc) => LocationCard(
            location: loc,
            onTap: () => _openLocationDetail(loc),
            onDelete: _isAdmin && loc.id != null ? () => _deleteLocation(loc) : null,
          )),
        ],
        if (allLegacy.isNotEmpty) ...[
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 4),
            child: Semantics(
              header: true,
              child: Text(
                '${l10n.festivals} / ${l10n.users}',
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                ),
              ),
            ),
          ),
          ...allLegacy.map((loc) => LegacyCard(
            location: loc,
            onTap: () => _showLegacyDetails(loc),
            onNavigate: () => _onLegacyTap(loc),
          )),
        ],
      ],
    );
  }
}
