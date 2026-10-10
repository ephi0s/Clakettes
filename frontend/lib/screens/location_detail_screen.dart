import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../l10n/app_localizations.dart';
import '../models/location_model.dart';
import '../models/location_tag_model.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import '../widgets/reusable_widgets.dart';
import '../widgets/location_badge_chip.dart';
import '../widgets/location_tag_editor.dart';
import '../widgets/open_in_maps_action.dart';

/// Muestra el detalle completo de una localización: cabecera, insignia,
/// descripción, etiquetas, galería de imágenes, mapa de coordenadas y
/// localizaciones relacionadas/de rodaje. Los administradores pueden
/// eliminar la localización.
class LocationDetailScreen extends StatefulWidget {
  final int locationId;

  const LocationDetailScreen({super.key, required this.locationId});

  @override
  State<LocationDetailScreen> createState() => _LocationDetailScreenState();
}

/// Estado de [LocationDetailScreen]. Carga la localización, sus etiquetas y
/// el rol del usuario actual en el primer build.
class _LocationDetailScreenState extends State<LocationDetailScreen> {
  Location? _location;
  List<LocationTag> _tags = [];
  bool _isLoading = true;
  bool _hasError = false;
  bool _isAdmin = false;
  bool _initialized = false;
  late AppLocalizations l10n;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    l10n = AppLocalizations.of(context)!;
    if (!_initialized) {
      _initialized = true;
      _loadData();
    }
  }

  /// Carga la localización, sus etiquetas y el rol de administrador del usuario actual.
  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
      _hasError = false;
    });

    try {
      final user = await AuthService().getCurrentUser();
      _isAdmin = user?.role?.toLowerCase() == 'admin';

      final location = await ApiService().getLocation(widget.locationId);
      final tags = await ApiService().getLocationTags(widget.locationId);

      if (mounted) {
        setState(() {
          _location = location;
          _tags = tags;
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

  /// Pide confirmación y elimina la localización, cerrando la pantalla con `true`.
  Future<void> _deleteLocation() async {
    if (_location?.id == null) return;
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(l10n.confirmDelete),
        content: Text('${l10n.delete} "${_location!.name}"?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: Text(l10n.cancel)),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: FilledButton.styleFrom(backgroundColor: Theme.of(ctx).colorScheme.error),
            child: Text(l10n.delete),
          ),
        ],
      ),
    );
    if (confirmed == true) {
      try {
        await ApiService().deleteLocation(_location!.id!);
        if (mounted) Navigator.pop(context, true);
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('${l10n.error}: $e')));
        }
      }
    }
  }

  /// Propone una nueva etiqueta para la localización y la añade a la lista en caso de éxito.
  Future<void> _proposeTag(String tag) async {
    if (_location?.id == null) return;
    try {
      final newTag = await ApiService().proposeLocationTag(_location!.id!, tag);
      if (mounted) {
        setState(() => _tags.add(newTag));
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('${l10n.error}: $e')));
      }
    }
  }

  /// Revoca una etiqueta existente y la elimina de la lista en caso de éxito.
  Future<void> _revokeTag(LocationTag tag) async {
    if (_location?.id == null || tag.id == null) return;
    try {
      await ApiService().revokeLocationTag(_location!.id!, tag.id!);
      if (mounted) {
        setState(() => _tags.removeWhere((t) => t.id == tag.id));
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('${l10n.error}: $e')));
      }
    }
  }

  Future<void> _openInMaps(double lat, double lng, String label) =>
      openInMaps(lat, lng, label: label);

  /// Muestra la imagen a pantalla completa en un diálogo con visor interactivo.
  void _showImagePreview(String imageUrl) {
    showDialog(
      context: context,
      builder: (_) => Dialog(
        backgroundColor: Colors.transparent,
        child: InteractiveViewer(
          child: ClipRRect(
            borderRadius: BorderRadius.circular(16),
            child: Image.network(imageUrl, fit: BoxFit.contain, gaplessPlayback: true, filterQuality: FilterQuality.medium, errorBuilder: (_, __, ___) => const Icon(Icons.broken_image, size: 48)),
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.locationDetail),
        actions: [
          if (_isAdmin && _location?.id != null)
            Semantics(
              label: l10n.delete,
              child: Tooltip(
                message: l10n.delete,
                child: IconButton(
                  icon: const Icon(Icons.delete_outline),
                  onPressed: _deleteLocation,
                ),
              ),
            ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _hasError
              ? Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.error_outline, size: 48, color: theme.colorScheme.error),
                      const SizedBox(height: 16),
                      Text(l10n.loadError),
                      const SizedBox(height: 16),
                      FilledButton.tonal(onPressed: _loadData, child: Text(l10n.retry)),
                    ],
                  ),
                )
              : _buildContent(theme),
    );
  }

  /// Construye el contenido completo de la pantalla de detalle.
  Widget _buildContent(ThemeData theme) {
    final location = _location!;
    final cs = theme.colorScheme;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 800),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
          _buildHeader(location, theme),
          const SizedBox(height: 16),
          _buildBadge(location, theme),
          const SizedBox(height: 16),
          if (location.description != null && location.description!.isNotEmpty) ...[
            _buildSection(l10n.description, theme),
            const SizedBox(height: 8),
            Semantics(
              label: '${l10n.description}: ${location.description}',
              child: Text(location.description!, style: theme.textTheme.bodyLarge),
            ),
            const SizedBox(height: 16),
          ],
          _buildSection(l10n.tags, theme),
          const SizedBox(height: 8),
          LocationTagEditor(
            tags: _tags,
            isAdmin: _isAdmin,
            onPropose: _proposeTag,
            onRevoke: _revokeTag,
          ),
          const SizedBox(height: 16),
          _buildSection(l10n.locationGallery, theme),
          const SizedBox(height: 8),
          _buildGallery(location, cs),
          const SizedBox(height: 16),
          _buildSection(l10n.coordinates, theme),
          const SizedBox(height: 8),
          _buildMiniMap(location, cs, theme),
          const SizedBox(height: 16),
          if (location.relatedLocationIds.isNotEmpty) ...[
            _buildSection(l10n.relatedLocations, theme),
            const SizedBox(height: 8),
            _buildRelatedLocations(location, cs, theme),
            const SizedBox(height: 16),
          ],
          if (location.filmLocations.isNotEmpty) ...[
            _buildSection(l10n.filmLocations, theme),
            const SizedBox(height: 8),
            _buildFilmedHere(location, cs, theme),
          ],
          ],
        ),
      ),
      ),
    );
  }

  /// Cabecera con el nombre, el autor y las coordenadas de la localización.
  Widget _buildHeader(Location location, ThemeData theme) {
    final cs = theme.colorScheme;
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: cs.primary.withAlpha(25),
            shape: BoxShape.circle,
          ),
          child: Icon(Icons.place, color: cs.primary, size: 24),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Semantics(
                header: true,
                child: Text(location.name, style: theme.textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold)),
              ),
              if (location.addedBy != null) ...[
                const SizedBox(height: 4),
                InfoRow(
                  icon: Icons.person_outline,
                  semanticLabel: '${l10n.addedBy}: ${location.addedBy}',
                  text: '${l10n.addedBy} #${location.addedBy}',
                ),
              ],
              const SizedBox(height: 4),
              InfoRow(
                icon: Icons.explore,
                semanticLabel: '${l10n.coordinates}: ${location.latitude.toStringAsFixed(6)}, ${location.longitude.toStringAsFixed(6)}',
                text: '${location.latitude.toStringAsFixed(6)}, ${location.longitude.toStringAsFixed(6)}',
              ),
            ],
          ),
        ),
      ],
    );
  }

  /// Muestra la insignia de la localización si existe.
  Widget _buildBadge(Location location, ThemeData theme) {
    if (location.badge == null || location.badge!.isEmpty) return const SizedBox.shrink();
    return Row(
      children: [
        LocationBadgeChip(badge: location.badge),
      ],
    );
  }

  /// Título de sección semántico dentro del detalle.
  Widget _buildSection(String title, ThemeData theme) {
    return Semantics(
      header: true,
      child: Text(title, style: theme.textTheme.titleSmall?.copyWith(color: theme.colorScheme.primary)),
    );
  }

  /// Galería horizontal de imágenes con vista previa a pantalla completa.
  Widget _buildGallery(Location location, ColorScheme cs) {
    final images = location.locationImages;
    if (images.isEmpty) {
      return Semantics(
        label: l10n.noImages,
        child: Container(
          height: 100,
          decoration: BoxDecoration(
            color: cs.surfaceContainerHighest.withAlpha(60),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Center(
            child: Text(l10n.noImages, style: TextStyle(color: cs.onSurfaceVariant)),
          ),
        ),
      );
    }

    return SizedBox(
      height: 120,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: images.length,
        separatorBuilder: (_, __) => const SizedBox(width: 8),
        itemBuilder: (_, i) {
          return ClipRRect(
            borderRadius: BorderRadius.circular(10),
            child: GestureDetector(
              onTap: () => _showImagePreview(images[i].url),
              child: Semantics(
                label: '${l10n.image} ${i + 1}',
                button: true,
                child: Image.network(
                  images[i].url,
                  width: 120,
                  height: 120,
                  cacheWidth: (120 * MediaQuery.devicePixelRatioOf(context)).round(),
                  cacheHeight: (120 * MediaQuery.devicePixelRatioOf(context)).round(),
                  fit: BoxFit.cover,
                  errorBuilder: (_, __, ___) => Container(
                    width: 120,
                    height: 120,
                    color: cs.surfaceContainerHighest,
                    child: Icon(Icons.broken_image, color: cs.onSurfaceVariant),
                  ),
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  /// Mapa de la localización con botón de navegación.
  Widget _buildMiniMap(Location location, ColorScheme cs, ThemeData theme) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(12),
      child: Stack(
        children: [
          SizedBox(
            height: 180,
            child: FlutterMap(
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
                      child: Icon(Icons.place, color: cs.primary, size: 40),
                    ),
                  ],
                ),
              ],
            ),
          ),
          Positioned(
            top: 8,
            right: 8,
            child: Material(
              color: cs.surfaceContainerHighest,
              borderRadius: BorderRadius.circular(24),
              elevation: 4,
              child: InkWell(
                borderRadius: BorderRadius.circular(24),
                onTap: () => _openInMaps(location.latitude, location.longitude, location.name),
                child: Padding(
                  padding: const EdgeInsets.all(10),
                  child: Icon(Icons.directions, color: cs.primary, size: 22),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// Chips con las localizaciones relacionadas por su id.
  Widget _buildRelatedLocations(Location location, ColorScheme cs, ThemeData theme) {
    if (location.relatedLocationIds.isEmpty) {
      return Semantics(
        label: l10n.noRelatedLocations,
        child: Text(l10n.noRelatedLocations, style: TextStyle(color: cs.onSurfaceVariant)),
      );
    }

    return Wrap(
      spacing: 8,
      runSpacing: 4,
      children: location.relatedLocationIds.map((id) {
        return ActionChip(
          avatar: Icon(Icons.place, size: 16, color: cs.primary),
          label: Text('#$id'),
          onPressed: () {
            Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => LocationDetailScreen(locationId: id)),
            );
          },
        );
      }).toList(),
    );
  }

  /// Tarjetas con los cortometrajes rodados en la localización.
  Widget _buildFilmedHere(Location location, ColorScheme cs, ThemeData theme) {
    if (location.filmLocations.isEmpty) {
      return Semantics(
        label: l10n.noFilmLocations,
        child: Text(l10n.noFilmLocations, style: TextStyle(color: cs.onSurfaceVariant)),
      );
    }

    return Column(
      children: location.filmLocations.map((fl) {
        return Card(
          margin: const EdgeInsets.only(bottom: 8),
          child: ListTile(
            leading: Icon(Icons.movie, color: cs.primary),
            title: Text('${l10n.shortFilms} #${fl.shortfilmId}'),
            subtitle: Text('${l10n.filmLocationRole}: ${fl.role}'),
            trailing: Icon(Icons.chevron_right, color: cs.onSurfaceVariant),
          ),
        );
      }).toList(),
    );
  }
}
