import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:image_picker/image_picker.dart';
import '../l10n/app_localizations.dart';
import '../models/festival_model.dart';
import '../models/festival_rulebook_model.dart';
import '../models/location_model.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import '../widgets/reusable_widgets.dart';
import '../widgets/location_selector.dart';
import '../widgets/festival_sections.dart';
import '../widgets/confirm_dialog.dart';
import '../widgets/open_in_maps_action.dart';
import 'location_detail_screen.dart';
import 'registration_forms_screen.dart';
import 'events_management_screen.dart';
import 'committees_screen.dart';
import 'awards_screen.dart';
import 'festival_rulebooks_screen.dart';
import 'member_directory_screen.dart';
import 'shortfilms_screen.dart';
import 'login_screen.dart';

/// Muestra y permite editar el perfil de un festival.
///
/// En modo lectura muestra el logo, el nombre, el estado, la descripción, la
/// ubicación, la web y las coordenadas. En modo edición muestra un formulario
/// con todos los campos. Incluye capacidad de eliminar con confirmación.
class FestivalProfileScreen extends StatefulWidget {
  final Festival festival;

  const FestivalProfileScreen({super.key, required this.festival});

  @override
  State<FestivalProfileScreen> createState() => _FestivalProfileScreenState();
}

/// Mantiene los datos del festival, los controladores del formulario de
/// edición, las imágenes de la galería y las localizaciones del festival;
/// carga las localizaciones y el estado de autenticación al iniciar.
class _FestivalProfileScreenState extends State<FestivalProfileScreen> {
  late TextEditingController _nameController;
  late TextEditingController _descriptionController;
  late TextEditingController _locationController;
  late TextEditingController _latitudeController;
  late TextEditingController _longitudeController;
  late TextEditingController _websiteController;
  late TextEditingController _logoUrlController;
  late bool _isActive;
  late Festival _festival;
  List<String> _images = [];
  List<Location> _festivalLocations = [];
  bool _locationsLoading = true;
  List<FestivalRulebook> _rulebooks = [];
  bool _rulebooksLoading = true;
  int _galleryIndex = 0;

  final _formKey = GlobalKey<FormState>();
  bool _isEditing = false;
  bool _isSaving = false;
  bool _isLoggedIn = false;
  late AppLocalizations l10n;

  @override
  void initState() {
    super.initState();
    final f = widget.festival;
    _festival = widget.festival;
    _nameController = TextEditingController(text: f.name);
    _descriptionController = TextEditingController(text: f.description ?? '');
    _locationController = TextEditingController(text: f.location ?? '');
    _latitudeController =
        TextEditingController(text: f.latitude?.toString() ?? '');
    _longitudeController =
        TextEditingController(text: f.longitude?.toString() ?? '');
    _websiteController = TextEditingController(text: f.website ?? '');
    _logoUrlController = TextEditingController(text: f.logoUrl ?? '');
    _isActive = f.isActive;
    _images = List.from(f.images);
    _checkAuth();
    _loadFestivalLocations();
    _loadRulebooks();
  }

  Future<void> _checkAuth() async {
    final loggedIn = await AuthService().isLoggedIn();
    if (mounted) setState(() => _isLoggedIn = loggedIn);
  }

  /// Ejecuta la acción si hay sesión iniciada; si no, pide al usuario que
  /// inicie sesión.
  void _requireAuthThen(VoidCallback action) {
    if (_isLoggedIn) {
      action();
    } else {
      showModalBottomSheet(
        context: context,
        isScrollControlled: true,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
        ),
        builder: (ctx) => LoginPromptSheet(onLogin: _navigateToLogin),
      );
    }
  }

  void _navigateToLogin() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => LoginScreen(
          onLoginSuccess: () {
            Navigator.pop(context);
            _checkAuth();
          },
        ),
      ),
    );
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    l10n = AppLocalizations.of(context)!;
  }

  @override
  void dispose() {
    _nameController.dispose();
    _descriptionController.dispose();
    _locationController.dispose();
    _latitudeController.dispose();
    _longitudeController.dispose();
    _websiteController.dispose();
    _logoUrlController.dispose();
    super.dispose();
  }

  /// Valida y envía los campos editados del festival a través de la API.
  Future<void> _saveProfile() async {
    if (!(_formKey.currentState?.validate() ?? false)) return;
    final fid = _festival.id;
    if (fid == null) return;

    setState(() => _isSaving = true);

    try {
      await ApiService().updateFestival(fid, {
        'name': _nameController.text.trim(),
        'description': _descriptionController.text.isNotEmpty
            ? _descriptionController.text.trim()
            : null,
        'location': _locationController.text.isNotEmpty
            ? _locationController.text.trim()
            : null,
        'latitude': double.tryParse(_latitudeController.text),
        'longitude': double.tryParse(_longitudeController.text),
        'is_active': _isActive,
        'website': _websiteController.text.isNotEmpty
            ? _websiteController.text.trim()
            : null,
        'logo_url': _logoUrlController.text.isNotEmpty
            ? _logoUrlController.text.trim()
            : null,
      });

      if (mounted) {
        setState(() => _isEditing = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(l10n.profileUpdated),
            behavior: SnackBarBehavior.floating,
          ),
        );
        Navigator.pop(context, true);
      }
    } catch (e) {
      debugPrint('Error: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(l10n.loadError),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _isSaving = false);
    }
  }

  Future<void> _openInMaps(double lat, double lng, String label) =>
      openInMaps(lat, lng, label: label);

  Future<void> _openWebsite(String url) async {
    var uri = Uri.tryParse(url);
    if (uri != null && !uri.hasScheme) {
      uri = Uri.parse('https://$url');
    }
    if (uri != null && await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
  }

  /// Carga las localizaciones asociadas al festival desde la API.
  Future<void> _loadFestivalLocations() async {
    final id = _festival.id;
    if (id == null) {
      if (mounted) setState(() => _locationsLoading = false);
      return;
    }
    try {
      final locations = await ApiService().getFestivalLocations(id);
      if (mounted) {
        setState(() {
          _festivalLocations = locations;
          _locationsLoading = false;
        });
      }
    } catch (e) {
      debugPrint('Error: $e');
      if (mounted) setState(() => _locationsLoading = false);
    }
  }

  /// Carga las bases publicadas del festival desde la API.
  Future<void> _loadRulebooks() async {
    final id = _festival.id;
    if (id == null) {
      if (mounted) setState(() => _rulebooksLoading = false);
      return;
    }
    try {
      final result = await ApiService().getRulebooks(id, size: 100);
      if (mounted) {
        setState(() {
          _rulebooks = result.items;
          _rulebooksLoading = false;
        });
      }
    } catch (e) {
      debugPrint('Error: $e');
      if (mounted) setState(() => _rulebooksLoading = false);
    }
  }

  void _openRulebooks() {
    final id = _festival.id;
    if (id == null) return;
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => FestivalRulebooksScreen(festivalId: id, festivalName: _festival.name),
      ),
    ).then((_) => _loadRulebooks());
  }

  /// Selecciona una localización mediante el selector y la vincula al festival.
  Future<void> _addFestivalLocation() async {
    _requireAuthThen(() async {
      await LocationSelector.show(
        context,
        onSelected: (location) async {
          try {
            final fid = _festival.id;
            final lid = location.id;
            if (fid == null || lid == null) return;
            await ApiService().addFestivalLocation(
              fid,
              lid,
            );
            await _loadFestivalLocations();
            if (mounted) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(l10n.profileUpdated),
                  behavior: SnackBarBehavior.floating,
                ),
              );
            }
          } catch (e) {
            debugPrint('Error: $e');
            if (mounted) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(l10n.loadError),
                  behavior: SnackBarBehavior.floating,
                ),
              );
            }
          }
        },
      );
    });
  }

  /// Desvincula una localización del festival tras un diálogo de confirmación.
  Future<void> _removeFestivalLocation(Location location) async {
    final festivalId = _festival.id;
    final locationId = location.id;
    if (festivalId == null || locationId == null) return;
    final confirmed = await showConfirmDialog(
      context,
      title: l10n.delete,
      message: l10n.deleteEntityMessage(location.name),
    );
    if (!confirmed) return;
    try {
      await ApiService().removeFestivalLocation(festivalId, locationId);
      await _loadFestivalLocations();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(l10n.profileUpdated),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } catch (e) {
      debugPrint('Error: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(l10n.loadError),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    }
  }

  void _openLocationDetail(Location location) {
    if (location.id == null) return;
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => LocationDetailScreen(locationId: location.id!),
      ),
    );
  }

  String _imageUrl(String path) {
    if (path.startsWith('http://') || path.startsWith('https://')) {
      return path;
    }
    return '${ApiService().rootUrl}$path';
  }

  /// Selecciona y sube una imagen de galería para el festival.
  Future<void> _addImage() async {
    final picker = ImagePicker();
    final picked = await picker.pickImage(source: ImageSource.gallery);
    if (picked == null) return;
    try {
      final updated = await ApiService().uploadFestivalImage(
        _festival.id!,
        picked.path,
      );
      if (mounted) setState(() => _images = List.from(updated.images));
    } catch (e) {
      debugPrint('Error: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(l10n.loadError),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    }
  }

  Future<void> _removeImage(String url) async {
    try {
      final updated = await ApiService().deleteFestivalImage(
        _festival.id!,
        url,
      );
      if (mounted) setState(() => _images = List.from(updated.images));
    } catch (e) {
      debugPrint('Error: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(l10n.loadError),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    }
  }

  /// Elimina el festival tras la confirmación y se cierra con `true`.
  Future<void> _deleteFestival() async {
    final confirmed = await showConfirmDialog(
      context,
      title: l10n.delete,
      message: l10n.confirmDelete,
    );
    if (!confirmed) return;
    final fid = _festival.id;
    if (fid == null) return;

    try {
      await ApiService().deleteFestival(fid);
      if (mounted) {
        Navigator.pop(context, true);
      }
    } catch (e) {
      debugPrint('Error: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(l10n.loadError),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final l10n = AppLocalizations.of(context)!;

    return Scaffold(
      appBar: AppBar(
        title: SemanticHeader(text: l10n.festivalProfile),
        actions: [
          if (_isEditing)
            Semantics(
              label: l10n.save,
              child: Tooltip(
                message: l10n.save,
                child: IconButton(
                  icon: _isSaving
                      ? const SizedBox(
                          height: 20,
                          width: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Icon(Icons.save),
                  onPressed: _isSaving ? null : _saveProfile,
                ),
              ),
            )
          else ...[
              Semantics(
                label: l10n.delete,
                child: Tooltip(
                  message: l10n.delete,
                  child: IconButton(
                    icon: const Icon(Icons.delete_outline),
                    onPressed: () => _requireAuthThen(_deleteFestival),
                  ),
                ),
              ),
              Semantics(
                label: l10n.edit,
                child: Tooltip(
                  message: l10n.edit,
                  child: IconButton(
                    icon: const Icon(Icons.edit),
                    onPressed: () => _requireAuthThen(() => setState(() => _isEditing = true)),
                  ),
                ),
              ),
          ],
        ],
      ),
      body: LayoutBuilder(
        builder: (context, constraints) {
          final isWide = constraints.maxWidth > 800;
          return Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 800),
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(24),
                child: _isEditing
                    ? _buildEditForm(theme, colorScheme)
                    : _buildReadView(theme, colorScheme, isWide),
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildReadView(ThemeData theme, ColorScheme colorScheme, bool isWide) {
    final f = _festival;
    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Hero(
            tag: 'festival_${f.id}',
            child: ProfileAvatar(
              imageUrl: f.logoUrl,
              fallbackText: f.name,
              radius: isWide ? 80 : 60,
              backgroundColor: colorScheme.secondaryContainer,
              foregroundColor: colorScheme.onSecondaryContainer,
              fallbackIcon: Icons.festival,
              semanticLabel: '${l10n.festivalProfile}: ${f.name}',
            ),
          ),
          const SizedBox(height: 24),
          SemanticHeader(
            text: f.name,
            style: theme.textTheme.headlineMedium?.copyWith(
              fontWeight: FontWeight.bold,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 8),
          StatusIndicator(
            isActive: f.isActive,
            activeLabel: l10n.active,
            inactiveLabel: l10n.inactive,
            useChip: true,
            semanticLabel: f.isActive ? l10n.active : l10n.inactive,
          ),
          const SizedBox(height: 24),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: colorScheme.surfaceContainerLow,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (f.description != null) ...[
                  SemanticHeader(
                    text: l10n.description,
                    style: theme.textTheme.titleSmall?.copyWith(
                      color: colorScheme.primary,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Semantics(
                    label: '${l10n.description}: ${f.description}',
                    child: Text(
                      f.description!,
                      style: theme.textTheme.bodyLarge,
                    ),
                  ),
                  const SizedBox(height: 24),
                ],
                InfoRow(
                  icon: Icons.location_on,
                  semanticLabel: '${l10n.location}: ${f.location ?? '-'}',
                  text: f.location ?? '-',
                ),
                if (f.website != null) ...[
                  const SizedBox(height: 12),
                  InfoRow(
                    icon: Icons.language,
                    semanticLabel: '${l10n.website}: ${f.website!}',
                    text: f.website!,
                    onTap: () => _openWebsite(f.website!),
                  ),
                ],
                if (f.latitude != null && f.longitude != null) ...[
                  const SizedBox(height: 16),
                  SizedBox(
                    height: 200,
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(12),
                      child: Stack(
                        children: [
                          FlutterMap(
                            options: MapOptions(
                              initialCenter: LatLng(f.latitude!, f.longitude!),
                              initialZoom: 13,
                              interactionOptions: const InteractionOptions(
                                flags: InteractiveFlag.all,
                              ),
                            ),
                            children: [
                              TileLayer(
                                urlTemplate:
                                    'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                                userAgentPackageName: 'com.clakettes.app',
                              ),
                              MarkerLayer(
                                markers: [
                                  Marker(
                                    point: LatLng(f.latitude!, f.longitude!),
                                    width: 80,
                                    height: 80,
                                    child: Icon(
                                      Icons.place,
                                      color: colorScheme.primary,
                                      size: 40,
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),
                          Positioned(
                            top: 8,
                            right: 8,
                            child: Material(
                              color: colorScheme.surfaceContainerHighest,
                              borderRadius: BorderRadius.circular(24),
                              elevation: 4,
                              child: InkWell(
                                borderRadius: BorderRadius.circular(24),
                                onTap: () => _openInMaps(
                                  f.latitude!,
                                  f.longitude!,
                                  f.name,
                                ),
                                child: Padding(
                                  padding: const EdgeInsets.all(10),
                                  child: Icon(
                                    Icons.directions,
                                    color: colorScheme.primary,
                                    size: 22,
                                  ),
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ],
            ),
          ),
          const SizedBox(height: 24),
          FestivalLocationsSection(
            l10n: l10n,
            locations: _festivalLocations,
            loading: _locationsLoading,
            isLoggedIn: _isLoggedIn,
            onAdd: _addFestivalLocation,
            onRemove: _removeFestivalLocation,
            onOpen: _openLocationDetail,
          ),
          const SizedBox(height: 24),
          RulebooksSection(
            l10n: l10n,
            rulebooks: _rulebooks,
            loading: _rulebooksLoading,
            onOpenList: _openRulebooks,
            onOpenUrl: _openWebsite,
          ),
          if (_images.isNotEmpty) ...[
            const SizedBox(height: 24),
            SizedBox(
              height: 200,
              child: ClipRRect(
                borderRadius: BorderRadius.circular(12),
                child: Stack(
                  children: [
                    PageView.builder(
                      itemCount: _images.length,
                      onPageChanged: (i) =>
                          setState(() => _galleryIndex = i),
                      itemBuilder: (_, i) => Image.network(
                        _imageUrl(_images[i]),
                        fit: BoxFit.cover,
                        gaplessPlayback: true,
                        filterQuality: FilterQuality.medium,
                        errorBuilder: (_, __, ___) => Center(
                          child: Icon(
                            Icons.broken_image,
                            size: 48,
                            color: colorScheme.onSurfaceVariant,
                          ),
                        ),
                      ),
                    ),
                    if (_images.length > 1)
                      Positioned(
                        bottom: 8,
                        left: 0,
                        right: 0,
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: List.generate(_images.length, (i) {
                            return Container(
                              margin:
                                  const EdgeInsets.symmetric(horizontal: 3),
                              width: _galleryIndex == i ? 10 : 8,
                              height: _galleryIndex == i ? 10 : 8,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                color: _galleryIndex == i
                                    ? colorScheme.primary
                                    : colorScheme.onSurface.withAlpha(100),
                              ),
                            );
                          }),
                        ),
                      ),
                  ],
                ),
              ),
            ),
          ],
          if (_isLoggedIn) ...[
            const SizedBox(height: 24),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: colorScheme.surfaceContainerLow,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  SemanticHeader(text: l10n.management, style: theme.textTheme.titleSmall?.copyWith(color: colorScheme.primary)),
                  const SizedBox(height: 12),
                  Wrap(spacing: 8, runSpacing: 8, children: [
                    ActionChip(
                      avatar: Icon(Icons.assignment_outlined, size: 18, color: colorScheme.primary),
                      label: Text(l10n.registrationForms),
                      onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => RegistrationFormsScreen(festivalId: f.id!, festivalName: f.name))),
                    ),
                    ActionChip(
                      avatar: Icon(Icons.event, size: 18, color: colorScheme.secondary),
                      label: Text(l10n.events),
                      onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => EventsManagementScreen(festivalId: f.id!, festivalName: f.name))),
                    ),
                    ActionChip(
                      avatar: Icon(Icons.groups, size: 18, color: colorScheme.tertiary),
                      label: Text(l10n.committees),
                      onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => CommitteesScreen(festivalId: f.id!, festivalName: f.name))),
                    ),
                    ActionChip(
                      avatar: Icon(Icons.emoji_events, size: 18, color: colorScheme.primary),
                      label: Text(l10n.awards),
                      onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => AwardsScreen(festivalId: f.id!, festivalName: f.name))),
                    ),
                    ActionChip(
                      avatar: Icon(Icons.description_outlined, size: 18, color: colorScheme.secondary),
                      label: Text(l10n.rulebooks),
                      onPressed: _openRulebooks,
                    ),
                    ActionChip(
                      avatar: Icon(Icons.people, size: 18, color: colorScheme.secondary),
                      label: Text(l10n.members),
                      onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => MemberDirectoryScreen(festivalId: f.id, festivalName: f.name))),
                    ),
                    ActionChip(
                      avatar: Icon(Icons.movie, size: 18, color: colorScheme.tertiary),
                      label: Text(l10n.shortFilms),
                      onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => ShortFilmsScreen(festivalId: f.id, festivalName: f.name))),
                    ),
                  ]),
                ],
              ),
            ),
            ],
          ],
        ),
      );
    }

  Widget _buildEditForm(ThemeData theme, ColorScheme colorScheme) {
    return Form(
      key: _formKey,
      autovalidateMode: AutovalidateMode.onUserInteraction,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          SemanticTextField(
            controller: _nameController,
            label: l10n.name,
            semanticLabel: l10n.name,
            prefixIcon: const Icon(Icons.festival),
            textInputAction: TextInputAction.next,
            maxLength: 100,
            validator: (v) {
              if (v == null || v.trim().isEmpty) {
                return l10n.getValidationMessage('required');
              }
              return null;
            },
          ),
          const SizedBox(height: 16),
          SemanticTextField(
            controller: _descriptionController,
            label: l10n.description,
            semanticLabel: l10n.description,
            helperText: l10n.optional,
            prefixIcon: const Icon(Icons.description),
            maxLines: 3,
            maxLength: 500,
            textInputAction: TextInputAction.next,
          ),
          const SizedBox(height: 16),
          SemanticTextField(
            controller: _locationController,
            label: l10n.location,
            semanticLabel: l10n.location,
            helperText: l10n.optional,
            prefixIcon: const Icon(Icons.location_on),
            textInputAction: TextInputAction.next,
            maxLength: 100,
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: SemanticTextField(
                  controller: _latitudeController,
                  label: l10n.latitude,
                  semanticLabel: l10n.latitude,
                  helperText: l10n.optional,
                  prefixIcon: const Icon(Icons.north),
                  keyboardType: TextInputType.number,
                  textInputAction: TextInputAction.next,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: SemanticTextField(
                  controller: _longitudeController,
                  label: l10n.longitude,
                  semanticLabel: l10n.longitude,
                  helperText: l10n.optional,
                  prefixIcon: const Icon(Icons.east),
                  keyboardType: TextInputType.number,
                  textInputAction: TextInputAction.next,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          SemanticTextField(
            controller: _websiteController,
            label: l10n.website,
            semanticLabel: l10n.website,
            helperText: l10n.optional,
            prefixIcon: const Icon(Icons.link),
            keyboardType: TextInputType.url,
            textInputAction: TextInputAction.next,
            maxLength: 200,
          ),
          const SizedBox(height: 16),
          SemanticTextField(
            controller: _logoUrlController,
            label: l10n.logoUrl,
            semanticLabel: l10n.logoUrl,
            helperText: l10n.optional,
            prefixIcon: const Icon(Icons.image),
            keyboardType: TextInputType.url,
            textInputAction: TextInputAction.done,
            maxLength: 200,
          ),
          const SizedBox(height: 24),
          SemanticHeader(
            text: l10n.images,
            style: theme.textTheme.titleSmall?.copyWith(
              color: colorScheme.primary,
            ),
          ),
          const SizedBox(height: 12),
          if (_images.isNotEmpty)
            SizedBox(
              height: 120,
              child: ListView.separated(
                scrollDirection: Axis.horizontal,
                itemCount: _images.length,
                separatorBuilder: (_, __) => const SizedBox(width: 8),
                itemBuilder: (_, i) => ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: Stack(
                    children: [
                      Image.network(
                        _imageUrl(_images[i]),
                        width: 120,
                        height: 120,
                        cacheWidth: (120 * MediaQuery.devicePixelRatioOf(context)).round(),
                        cacheHeight: (120 * MediaQuery.devicePixelRatioOf(context)).round(),
                        fit: BoxFit.cover,
                        errorBuilder: (_, __, ___) => Container(
                          width: 120,
                          height: 120,
                          color: colorScheme.surfaceContainerHighest,
                          child: Icon(
                            Icons.broken_image,
                            color: colorScheme.onSurfaceVariant,
                          ),
                        ),
                      ),
                      Positioned(
                        top: 4,
                        right: 4,
                        child: Material(
                          color: Colors.black54,
                          borderRadius: BorderRadius.circular(16),
                          child: InkWell(
                            borderRadius: BorderRadius.circular(16),
                            onTap: () => _removeImage(_images[i]),
                            child: const Padding(
                              padding: EdgeInsets.all(4),
                              child: Icon(
                                Icons.close,
                                color: Colors.white,
                                size: 18,
                              ),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            )
          else
            Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Text(
                l10n.noImages,
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: colorScheme.onSurfaceVariant,
                ),
              ),
            ),
          const SizedBox(height: 8),
          OutlinedButton.icon(
            icon: const Icon(Icons.add_photo_alternate),
            label: Text(l10n.addImage),
            onPressed: _addImage,
          ),
          const SizedBox(height: 16),
          Semantics(
            label: l10n.active,
            child: SwitchListTile(
              title: Text(l10n.active),
              subtitle: Text(_isActive ? l10n.active : l10n.inactive),
              value: _isActive,
              onChanged: (v) => setState(() => _isActive = v),
            ),
          ),
        ],
      ),
    );
  }
}
