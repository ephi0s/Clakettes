import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../models/shortfilm_model.dart';
import '../models/location_model.dart';
import '../models/film_location_model.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import '../widgets/reusable_widgets.dart';
import '../widgets/confirm_dialog.dart';
import '../widgets/film_location_card.dart';
import '../widgets/location_selector.dart';
import 'login_screen.dart';
import 'festival_profile_screen.dart';
import 'location_detail_screen.dart';

/// Muestra el perfil de un cortometraje y permite editarlo.
///
/// Muestra miniatura, título, descripción, duración, etiquetas, enlace al
/// festival, enlace al usuario, estado público/privado y fechas. Incluye
/// edición/borrado.
class ShortFilmProfileScreen extends StatefulWidget {
  final ShortFilm shortFilm;

  const ShortFilmProfileScreen({super.key, required this.shortFilm});

  @override
  State<ShortFilmProfileScreen> createState() => _ShortFilmProfileScreenState();
}

/// Estado de [ShortFilmProfileScreen]. Mantiene los controladores de edición
/// y el indicador de visibilidad, y carga las localizaciones del cortometraje.
class _ShortFilmProfileScreenState extends State<ShortFilmProfileScreen> {
  late TextEditingController _titleController;
  late TextEditingController _descriptionController;
  late TextEditingController _durationController;
  late TextEditingController _videoUrlController;
  late TextEditingController _thumbnailUrlController;
  late TextEditingController _tagsController;

  late bool _isPublic;
  final _formKey = GlobalKey<FormState>();
  bool _isEditing = false;
  bool _isSaving = false;
  late AppLocalizations l10n;
  bool _isLoggedIn = false;
  List<FilmLocation> _filmLocations = [];
  final Map<int, Location> _locationCache = {};

  @override
  void initState() {
    super.initState();
    final s = widget.shortFilm;
    _titleController = TextEditingController(text: s.title);
    _descriptionController = TextEditingController(text: s.description ?? '');
    _durationController =
        TextEditingController(text: s.duration?.toString() ?? '');
    _videoUrlController = TextEditingController(text: s.videoUrl ?? '');
    _thumbnailUrlController =
        TextEditingController(text: s.thumbnailUrl ?? '');
    _tagsController = TextEditingController(text: s.tags ?? '');
    _isPublic = s.isPublic;
    _checkAuth();
    _loadFilmLocations();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    l10n = AppLocalizations.of(context)!;
  }

  @override
  void dispose() {
    _titleController.dispose();
    _descriptionController.dispose();
    _durationController.dispose();
    _videoUrlController.dispose();
    _thumbnailUrlController.dispose();
    _tagsController.dispose();
    super.dispose();
  }

  /// Carga las localizaciones de rodaje y almacena en caché cada localización asociada.
  Future<void> _loadFilmLocations() async {
    if (widget.shortFilm.id == null) return;
    try {
      final filmLocs = await ApiService().getFilmLocations(widget.shortFilm.id!);
      for (final fl in filmLocs) {
        if (!_locationCache.containsKey(fl.locationId)) {
          try {
            final loc = await ApiService().getLocation(fl.locationId);
            _locationCache[fl.locationId] = loc;
          } catch (e) { debugPrint('Error: $e'); }
        }
      }
      if (mounted) setState(() => _filmLocations = filmLocs);
    } catch (e) { debugPrint('Error: $e'); }
  }

  /// Abre el selector de localización y vincula la elegida como principal.
  Future<void> _addFilmLocation() async {
    if (widget.shortFilm.id == null) return;
    await LocationSelector.show(
      context,
      onSelected: (location) async {
        try {
          final fl = await ApiService().addFilmLocation(widget.shortFilm.id!, {
            'location_id': location.id,
            'role': 'primary',
          });
          if (mounted) setState(() {
            _filmLocations.add(fl);
            _locationCache[location.id!] = location;
          });
        } catch (e) {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('${l10n.error}: $e')));
          }
        }
      },
    );
  }

  /// Confirma y elimina un vínculo de localización de rodaje.
  Future<void> _removeFilmLocation(FilmLocation fl) async {
    if (widget.shortFilm.id == null || fl.id == null) return;
    final confirmed = await showConfirmDialog(
      context,
      title: l10n.delete,
      message: '${l10n.delete} ${_locationCache[fl.locationId]?.name ?? l10n.location}?',
    );
    if (!confirmed) return;
    try {
      await ApiService().removeFilmLocation(widget.shortFilm.id!, fl.id!);
      if (mounted) setState(() => _filmLocations.removeWhere((f) => f.id == fl.id));
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('${l10n.error}: $e')));
      }
    }
  }

  /// Valida el formulario y persiste los campos del perfil editados.
  Future<void> _saveProfile() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isSaving = true);

    try {
      await ApiService().updateShortFilm(widget.shortFilm.id!, {
        'title': _titleController.text.trim(),
        'description': _descriptionController.text.isNotEmpty
            ? _descriptionController.text.trim()
            : null,
        'duration': int.tryParse(_durationController.text),
        'video_url': _videoUrlController.text.isNotEmpty
            ? _videoUrlController.text.trim()
            : null,
        'thumbnail_url': _thumbnailUrlController.text.isNotEmpty
            ? _thumbnailUrlController.text.trim()
            : null,
        'is_public': _isPublic,
        'tags': _tagsController.text.isNotEmpty
            ? _tagsController.text.trim()
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

  /// Confirma y elimina el cortometraje, cerrando la pantalla en caso de éxito.
  Future<void> _deleteShortFilm() async {
    final confirmed = await showConfirmDialog(
      context,
      title: l10n.delete,
      message: l10n.confirmDelete,
    );
    if (!confirmed) return;

    try {
      await ApiService().deleteShortFilm(widget.shortFilm.id!);
      if (mounted) Navigator.pop(context, true);
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

  /// Refresca el estado de sesión usado para restringir las acciones de edición.
  Future<void> _checkAuth() async {
    final loggedIn = await AuthService().isLoggedIn();
    if (mounted) setState(() => _isLoggedIn = loggedIn);
  }

  /// Abre el perfil del festival indicado.
  Future<void> _openFestival(int festivalId) async {
    try {
      final festival = await ApiService().getFestival(festivalId);
      if (mounted) {
        Navigator.push(context, MaterialPageRoute(builder: (_) => FestivalProfileScreen(festival: festival)));
      }
    } catch (e) {
      debugPrint('Error: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.error), behavior: SnackBarBehavior.floating));
      }
    }
  }

  /// Ejecuta [action] si hay sesión iniciada; si no, muestra una hoja de aviso de inicio.
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
        builder: (ctx) => Padding(
          padding: EdgeInsets.fromLTRB(24, 24, 24, MediaQuery.of(ctx).viewInsets.bottom + 24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.primaryContainer,
                  shape: BoxShape.circle,
                ),
                child: Icon(Icons.lock_outline_rounded, size: 32, color: Theme.of(context).colorScheme.onPrimaryContainer),
              ),
              const SizedBox(height: 20),
              Text(l10n.login, style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Text(
                l10n.loginRequired,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: Theme.of(context).colorScheme.onSurfaceVariant),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 28),
              SizedBox(
                width: double.infinity,
                child: FilledButton(
                  onPressed: () {
                    Navigator.pop(ctx);
                    _navigateToLogin();
                  },
                  child: Text(l10n.login),
                ),
              ),
              const SizedBox(height: 8),
            ],
          ),
        ),
      );
    }
  }

  /// Abre la pantalla de inicio de sesión y refresca el estado de autenticación al lograrlo.
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
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Scaffold(
      appBar: AppBar(
        title: SemanticHeader(text: l10n.shortFilmProfile),
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
          else if (_isLoggedIn) ...[
            Semantics(
              label: l10n.delete,
              child: Tooltip(
                message: l10n.delete,
                child: IconButton(
                  icon: const Icon(Icons.delete_outline),
                  onPressed: () => _requireAuthThen(_deleteShortFilm),
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
                    ? _buildEditForm(colorScheme)
                    : _buildReadView(theme, colorScheme, isWide),
              ),
            ),
          );
        },
      ),
    );
  }

  /// Construye la vista de solo lectura con los datos del cortometraje.
  Widget _buildReadView(ThemeData theme, ColorScheme colorScheme, bool isWide) {
    final s = widget.shortFilm;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        if (s.thumbnailUrl != null)
          ClipRRect(
            borderRadius: BorderRadius.circular(16),
            child: Semantics(
              label: '${l10n.shortFilms}: ${s.title}',
              child: Image.network(
                s.thumbnailUrl!,
                height: isWide ? 300 : 200,
                width: double.infinity,
                fit: BoxFit.cover,
                gaplessPlayback: true,
                filterQuality: FilterQuality.medium,
                errorBuilder: (_, __, ___) => Container(height: isWide ? 300 : 200, color: colorScheme.surfaceContainerHighest, child: Icon(Icons.broken_image, color: colorScheme.onSurfaceVariant)),
              ),
            ),
          )
        else
          Container(
            height: isWide ? 300 : 200,
            width: double.infinity,
            decoration: BoxDecoration(
              color: colorScheme.surfaceContainerHighest,
              borderRadius: BorderRadius.circular(16),
            ),
            child: Icon(Icons.movie, size: 80, color: colorScheme.onSurfaceVariant),
          ),
        const SizedBox(height: 24),
        SemanticHeader(
          text: s.title,
          style: theme.textTheme.headlineMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 8),
        StatusIndicator(
          isActive: s.isPublic,
          activeLabel: l10n.public,
          inactiveLabel: l10n.private,
          useChip: true,
          semanticLabel: s.isPublic ? l10n.public : l10n.private,
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
              if (s.description != null) ...[
                SemanticHeader(
                  text: l10n.description,
                  style: theme.textTheme.titleSmall?.copyWith(
                    color: colorScheme.primary,
                  ),
                ),
                const SizedBox(height: 8),
                Semantics(
                  label: '${l10n.description}: ${s.description}',
                  child: Text(
                    s.description!,
                    style: theme.textTheme.bodyLarge,
                  ),
                ),
                const SizedBox(height: 24),
              ],
              if (s.duration != null)
                InfoRow(
                  icon: Icons.timer,
                  semanticLabel: '${l10n.duration}: ${s.duration} ${l10n.minutes}',
                  text: '${s.duration} ${l10n.minutes}',
                ),
              if (s.tags != null && s.tags!.isNotEmpty) ...[
                const SizedBox(height: 12),
                InfoRow(
                  icon: Icons.label,
                  semanticLabel: '${l10n.tags}: ${s.tags}',
                  text: s.tags!,
                ),
              ],
              if (s.festivalId != null) ...[
                const SizedBox(height: 12),
                GestureDetector(
                  onTap: () => _openFestival(s.festivalId!),
                  child: InfoRow(
                    icon: Icons.festival,
                    iconColor: colorScheme.primary,
                    semanticLabel: '${l10n.festivals}: ID ${s.festivalId}',
                    text: '${l10n.festivals} #${s.festivalId}',
                    trailing: Icon(Icons.open_in_new, size: 14, color: colorScheme.primary),
                  ),
                ),
              ],
              const SizedBox(height: 12),
              InfoRow(
                icon: Icons.person,
                semanticLabel: '${l10n.users}: ID ${s.userId}',
                text: '${l10n.users} #${s.userId}',
              ),
              if (s.createdAt != null) ...[
                const SizedBox(height: 12),
                InfoRow(
                  icon: Icons.calendar_today,
                  semanticLabel: '${l10n.createdAt}: ${s.createdAt}',
                  text: '${s.createdAt}',
                ),
              ],
            ],
          ),
        ),
        const SizedBox(height: 24),
        _buildFilmLocationsSection(theme, colorScheme),
      ],
    );
  }

  /// Construye el formulario de edición de los campos del perfil.
  Widget _buildEditForm(ColorScheme colorScheme) {
    return Form(
      key: _formKey,
      autovalidateMode: AutovalidateMode.onUserInteraction,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          SemanticTextField(
            controller: _titleController,
            label: l10n.name,
            semanticLabel: l10n.name,
            prefixIcon: const Icon(Icons.movie),
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
            controller: _durationController,
            label: '${l10n.duration} (${l10n.minutes})',
            semanticLabel: '${l10n.duration} (${l10n.minutes})',
            helperText: l10n.optional,
            prefixIcon: const Icon(Icons.timer),
            keyboardType: TextInputType.number,
            textInputAction: TextInputAction.next,
          ),
          const SizedBox(height: 16),
          SemanticTextField(
            controller: _videoUrlController,
            label: l10n.videoUrl,
            semanticLabel: l10n.videoUrl,
            helperText: l10n.optional,
            prefixIcon: const Icon(Icons.videocam),
            keyboardType: TextInputType.url,
            textInputAction: TextInputAction.next,
            maxLength: 200,
          ),
          const SizedBox(height: 16),
          SemanticTextField(
            controller: _thumbnailUrlController,
            label: l10n.thumbnailUrl,
            semanticLabel: l10n.thumbnailUrl,
            helperText: l10n.optional,
            prefixIcon: const Icon(Icons.image),
            keyboardType: TextInputType.url,
            textInputAction: TextInputAction.next,
            maxLength: 200,
          ),
          const SizedBox(height: 16),
          SemanticTextField(
            controller: _tagsController,
            label: l10n.tags,
            semanticLabel: l10n.tags,
            helperText: l10n.optional,
            prefixIcon: const Icon(Icons.label),
            textInputAction: TextInputAction.done,
            maxLength: 200,
          ),
          const SizedBox(height: 16),
          Semantics(
            label: l10n.publicProfile,
            child: SwitchListTile(
              title: Text(l10n.publicProfile),
              subtitle: Text(_isPublic ? l10n.public : l10n.private),
              value: _isPublic,
              onChanged: (v) => setState(() => _isPublic = v),
            ),
          ),
        ],
      ),
    );
  }

  /// Sección con las localizaciones de rodaje del cortometraje.
  Widget _buildFilmLocationsSection(ThemeData theme, ColorScheme colorScheme) {
    return Container(
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
              Icon(Icons.place, color: colorScheme.primary, size: 20),
              const SizedBox(width: 8),
              Expanded(
                child: Semantics(
                  header: true,
                  child: Text(l10n.filmLocations, style: theme.textTheme.titleSmall?.copyWith(color: colorScheme.primary)),
                ),
              ),
              if (_isLoggedIn)
                Semantics(
                  label: l10n.addFilmLocation,
                  child: Tooltip(
                    message: l10n.addFilmLocation,
                    child: IconButton(
                      icon: Icon(Icons.add_location_alt, size: 20, color: colorScheme.primary),
                      onPressed: _addFilmLocation,
                      visualDensity: VisualDensity.compact,
                      padding: EdgeInsets.zero,
                      constraints: const BoxConstraints(),
                    ),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 12),
          if (_filmLocations.isEmpty)
            Semantics(
              label: l10n.noLocationsShotHere,
              child: Padding(
                padding: const EdgeInsets.symmetric(vertical: 8),
                child: Text(
                  l10n.noLocationsShotHere,
                  style: theme.textTheme.bodySmall?.copyWith(color: colorScheme.onSurfaceVariant),
                ),
              ),
            )
          else
            ..._filmLocations.map((fl) => FilmLocationCard(
              filmLocation: fl,
              location: _locationCache[fl.locationId],
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => LocationDetailScreen(locationId: fl.locationId)),
                );
              },
              onRemove: _isLoggedIn ? () => _removeFilmLocation(fl) : null,
              showActions: _isLoggedIn,
            )),
        ],
      ),
    );
  }
}
