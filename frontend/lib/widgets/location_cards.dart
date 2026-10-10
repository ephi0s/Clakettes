import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../l10n/app_localizations.dart';
import '../models/location_model.dart';
import 'reusable_widgets.dart';
import 'location_badge_chip.dart';
import 'map_picker.dart';

/// Tarjeta de lista para una localización con miniatura, insignia,
/// descripción, etiquetas y una acción de borrado opcional.
class LocationCard extends StatelessWidget {
  final Location location;
  final VoidCallback onTap;
  final VoidCallback? onDelete;

  const LocationCard({
    super.key,
    required this.location,
    required this.onTap,
    this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 5),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(14),
        side: BorderSide(color: theme.colorScheme.outlineVariant.withAlpha(30)),
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(14),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              ClipRRect(
                borderRadius: BorderRadius.circular(10),
                child: Container(
                  width: 64,
                  height: 64,
                  color: theme.colorScheme.primaryContainer.withAlpha(80),
                  child: location.images.isNotEmpty
                      ? Image.network(
                          location.images.first,
                          width: 64,
                          height: 64,
                          cacheWidth: (64 * MediaQuery.devicePixelRatioOf(context)).round(),
                          cacheHeight: (64 * MediaQuery.devicePixelRatioOf(context)).round(),
                          fit: BoxFit.cover,
                          errorBuilder: (_, __, ___) => Icon(Icons.place, color: theme.colorScheme.primary, size: 28),
                        )
                      : Icon(Icons.place, color: theme.colorScheme.primary, size: 28),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      location.name,
                      style: theme.textTheme.bodyLarge?.copyWith(fontWeight: FontWeight.w600),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    if (location.badge != null && location.badge!.isNotEmpty) ...[
                      const SizedBox(height: 2),
                      LocationBadgeChip(badge: location.badge, small: true),
                    ],
                    if (location.description != null && location.description!.isNotEmpty)
                      Padding(
                        padding: const EdgeInsets.only(top: 2),
                        child: Text(
                          location.description!,
                          style: theme.textTheme.bodySmall?.copyWith(color: theme.colorScheme.onSurfaceVariant),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    if (location.tags.isNotEmpty) ...[
                      const SizedBox(height: 4),
                      Wrap(
                        spacing: 4,
                        runSpacing: 2,
                        children: location.tags.take(3).map((tag) {
                          return Container(
                            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                            decoration: BoxDecoration(
                              color: theme.colorScheme.secondaryContainer.withAlpha(120),
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Text(
                              tag,
                              style: TextStyle(fontSize: 10, color: theme.colorScheme.onSecondaryContainer),
                            ),
                          );
                        }).toList(),
                      ),
                    ],
                  ],
                ),
              ),
              if (onDelete != null)
                IconButton(
                  icon: Icon(Icons.delete_outline, size: 18, color: theme.colorScheme.error),
                  onPressed: onDelete,
                  padding: EdgeInsets.zero,
                  constraints: const BoxConstraints(),
                ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Tarjeta de lista para una localización heredada de festival/usuario.
class LegacyCard extends StatelessWidget {
  final LegacyLocation location;
  final VoidCallback onTap;
  final VoidCallback onNavigate;

  const LegacyCard({
    super.key,
    required this.location,
    required this.onTap,
    required this.onNavigate,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;
    final color = location.type == 'User' ? cs.secondary : cs.primary;
    final icon = location.type == 'User' ? Icons.person : Icons.festival;

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 5),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(14),
        side: BorderSide(color: theme.colorScheme.outlineVariant.withAlpha(30)),
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(14),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            children: [
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: color.withAlpha(25),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(icon, color: color, size: 24),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(location.name, style: theme.textTheme.bodyLarge?.copyWith(fontWeight: FontWeight.w600)),
                    if (location.subtitle != null)
                      Text(location.subtitle!, style: theme.textTheme.bodySmall?.copyWith(color: theme.colorScheme.onSurfaceVariant)),
                    Text(AppLocalizations.of(context)!.getLocationTypeTranslation(location.type), style: TextStyle(fontSize: 10, color: color)),
                  ],
                ),
              ),
              IconButton(
                icon: Icon(Icons.open_in_new, size: 18, color: theme.colorScheme.primary),
                onPressed: onNavigate,
                padding: EdgeInsets.zero,
                constraints: const BoxConstraints(),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Punto de mapa inmutable derivado de un festival o usuario con coordenadas.
class LegacyLocation {
  final String name;
  final double latitude;
  final double longitude;
  final String type;
  final String? subtitle;
  final String? sourceId;

  LegacyLocation({
    required this.name,
    required this.latitude,
    required this.longitude,
    required this.type,
    this.subtitle,
    this.sourceId,
  });
}

/// Datos devueltos por el formulario de creación de localización.
class LocationFormResult {
  final String name;
  final String? description;
  final String? address;
  final double latitude;
  final double longitude;
  final List<String> tags;

  LocationFormResult({
    required this.name,
    this.description,
    this.address,
    required this.latitude,
    required this.longitude,
    this.tags = const [],
  });
}

/// Formulario con estilo de diálogo para crear una localización con selector
/// de mapa y etiquetas.
class LocationFormScreen extends StatefulWidget {
  const LocationFormScreen({super.key});

  @override
  State<LocationFormScreen> createState() => LocationFormScreenState();
}

/// Estado de [LocationFormScreen]. Mantiene las coordenadas seleccionadas,
/// la lista de etiquetas y los controladores de campo hasta enviar el formulario.
class LocationFormScreenState extends State<LocationFormScreen> {
  final TextEditingController _nameCtrl = TextEditingController();
  final TextEditingController _descCtrl = TextEditingController();
  final TextEditingController _addrCtrl = TextEditingController();
  final TextEditingController _tagsCtrl = TextEditingController();

  LatLng? _selectedLatLng;
  final List<String> _tags = [];

  @override
  void dispose() {
    _nameCtrl.dispose();
    _descCtrl.dispose();
    _addrCtrl.dispose();
    _tagsCtrl.dispose();
    super.dispose();
  }

  /// Añade el texto de etiqueta actual a la lista si es nuevo y no vacío.
  void _addTag() {
    final tag = _tagsCtrl.text.trim();
    if (tag.isNotEmpty && !_tags.contains(tag)) {
      setState(() => _tags.add(tag));
      _tagsCtrl.clear();
    }
  }

  /// Elimina una etiqueta de la lista seleccionada.
  void _removeTag(String tag) {
    setState(() => _tags.remove(tag));
  }

  /// Abre el selector de mapa y guarda las coordenadas seleccionadas.
  Future<void> _pickLocation() async {
    final result = await Navigator.push<LatLng>(
      context,
      MaterialPageRoute(builder: (_) => MapPickerScreen(l10n: AppLocalizations.of(context)!)),
    );
    if (result != null) {
      setState(() => _selectedLatLng = result);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.addLocation),
        leading: IconButton(
          icon: const Icon(Icons.close),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView(
              padding: const EdgeInsets.all(12),
              children: [
                GestureDetector(
                  onTap: _pickLocation,
                  child: Container(
                    height: 200,
                    decoration: BoxDecoration(
                      color: theme.colorScheme.surfaceContainerHighest,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(
                        color: _selectedLatLng != null
                            ? theme.colorScheme.primary
                            : theme.colorScheme.outlineVariant,
                      ),
                    ),
                    child: _selectedLatLng != null
                        ? Stack(
                            children: [
                              ClipRRect(
                                borderRadius: BorderRadius.circular(12),
                                child: FlutterMap(
                                  options: MapOptions(
                                    initialCenter: _selectedLatLng!,
                                    initialZoom: 13,
                                    interactionOptions: const InteractionOptions(flags: InteractiveFlag.none),
                                  ),
                                  children: [
                                    TileLayer(
                                      urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                                      userAgentPackageName: 'com.clakettes.app',
                                    ),
                                    MarkerLayer(
                                      markers: [
                                        Marker(
                                          point: _selectedLatLng!,
                                          width: 80,
                                          height: 80,
                                          child: const Icon(Icons.place, color: Colors.red, size: 44),
                                        ),
                                      ],
                                    ),
                                  ],
                                ),
                              ),
                              Positioned(
                                top: 8,
                                right: 8,
                                child: FilledButton.tonal(
                                  onPressed: _pickLocation,
                                  child: Text(l10n.edit),
                                ),
                              ),
                            ],
                          )
                        : Center(
                            child: Column(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Icon(Icons.add_location_alt, size: 36, color: theme.colorScheme.onSurfaceVariant),
                                const SizedBox(height: 8),
                                Text(l10n.openMap, style: TextStyle(color: theme.colorScheme.onSurfaceVariant)),
                              ],
                            ),
                          ),
                  ),
                ),
                if (_selectedLatLng != null)
                  Padding(
                    padding: const EdgeInsets.symmetric(vertical: 4),
                    child: Text(
                      '${_selectedLatLng!.latitude.toStringAsFixed(6)}, ${_selectedLatLng!.longitude.toStringAsFixed(6)}',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                        fontFamily: 'monospace',
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ),
                const SizedBox(height: 12),
                SemanticTextField(
                  controller: _nameCtrl,
                  label: l10n.name,
                  semanticLabel: l10n.name,
                  prefixIcon: const Icon(Icons.place),
                  textInputAction: TextInputAction.next,
                ),
                const SizedBox(height: 8),
                SemanticTextField(
                  controller: _descCtrl,
                  label: l10n.description,
                  semanticLabel: l10n.description,
                  prefixIcon: const Icon(Icons.description),
                  textInputAction: TextInputAction.next,
                  maxLines: 2,
                ),
                const SizedBox(height: 8),
                SemanticTextField(
                  controller: _addrCtrl,
                  label: l10n.location,
                  semanticLabel: l10n.location,
                  prefixIcon: const Icon(Icons.location_on),
                  textInputAction: TextInputAction.next,
                ),
                const SizedBox(height: 8),
                Row(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Expanded(
                      child: SemanticTextField(
                        controller: _tagsCtrl,
                        label: l10n.tags,
                        semanticLabel: l10n.tags,
                        prefixIcon: const Icon(Icons.label),
                        textInputAction: TextInputAction.done,
                        onSubmitted: (_) => _addTag(),
                      ),
                    ),
                    const SizedBox(width: 8),
                    FilledButton.tonalIcon(
                      onPressed: _addTag,
                      icon: const Icon(Icons.add, size: 18),
                      label: Text(l10n.add),
                    ),
                  ],
                ),
                if (_tags.isNotEmpty) ...[
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 6,
                    runSpacing: 4,
                    children: _tags.map((tag) {
                      return Chip(
                        label: Text(tag, style: const TextStyle(fontSize: 12)),
                        deleteIcon: const Icon(Icons.close, size: 16),
                        onDeleted: () => _removeTag(tag),
                        materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                        visualDensity: VisualDensity.compact,
                        padding: EdgeInsets.zero,
                      );
                    }).toList(),
                  ),
                ],
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
            decoration: BoxDecoration(
              color: theme.colorScheme.surface,
              boxShadow: [
                BoxShadow(color: Colors.black.withAlpha(20), blurRadius: 8, offset: const Offset(0, -2)),
              ],
            ),
            child: SizedBox(
              width: double.infinity,
              child: FilledButton.icon(
                icon: const Icon(Icons.save),
                label: Text(l10n.save),
                onPressed: () {
                  if (_nameCtrl.text.trim().isEmpty) {
                    showAppSnack(context, l10n.getValidationMessage('required'));
                    return;
                  }
                  if (_selectedLatLng == null) {
                    showAppSnack(context, l10n.locationFetchError);
                    return;
                  }
                  Navigator.pop(
                    context,
                    LocationFormResult(
                      name: _nameCtrl.text.trim(),
                      description: _descCtrl.text.trim().isEmpty ? null : _descCtrl.text.trim(),
                      address: _addrCtrl.text.trim().isEmpty ? null : _addrCtrl.text.trim(),
                      latitude: _selectedLatLng!.latitude,
                      longitude: _selectedLatLng!.longitude,
                      tags: List.from(_tags),
                    ),
                  );
                },
              ),
            ),
          ),
        ],
      ),
    );
  }
}
