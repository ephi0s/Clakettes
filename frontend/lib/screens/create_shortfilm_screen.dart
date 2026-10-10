import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../models/shortfilm_model.dart';
import '../models/festival_model.dart';
import '../models/location_model.dart';
import '../models/film_location_model.dart';
import '../services/api_service.dart';
import '../services/sync_queue_service.dart';
import '../services/auth_service.dart';
import '../services/connectivity_monitor.dart';
import '../widgets/reusable_widgets.dart';
import '../widgets/film_location_card.dart';
import '../widgets/location_selector.dart';

/// Formulario a pantalla completa para crear un nuevo cortometraje.
///
/// Valida los campos obligatorios (título) y carga la lista de festivales
/// para el desplegable. Al tener éxito se cierra con `true`.
class CreateShortFilmScreen extends StatefulWidget {
  const CreateShortFilmScreen({super.key});

  @override
  State<CreateShortFilmScreen> createState() => _CreateShortFilmScreenState();
}

/// Mantiene los controladores del formulario, el festival elegido, las
/// localizaciones de rodaje y la lista de festivales cargada una sola vez en
/// el primer build.
class _CreateShortFilmScreenState extends State<CreateShortFilmScreen> {
  final _formKey = GlobalKey<FormState>();
  final _titleController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _durationController = TextEditingController();
  final _videoUrlController = TextEditingController();
  final _thumbnailUrlController = TextEditingController();
  final _tagsController = TextEditingController();

  int? _selectedFestivalId;
  bool _isPublic = true;
  bool _isLoading = false;
  bool _isLoadingFestivals = true;
  bool _initialized = false;
  List<Festival> _festivals = [];
  final List<_FilmLocationEntry> _filmLocations = [];
  final Map<int, Location> _locationCache = {};
  late AppLocalizations l10n;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    l10n = AppLocalizations.of(context)!;
    if (!_initialized) {
      _initialized = true;
      _loadFestivals();
    }
  }

  /// Carga los festivales disponibles para el desplegable de selección.
  Future<void> _loadFestivals() async {
    try {
      final result = await ApiService().getFestivals();
      if (mounted) {
        setState(() {
          _festivals = result.items;
          _isLoadingFestivals = false;
        });
      }
    } catch (e) {
      debugPrint('Error: $e');
      if (mounted) setState(() => _isLoadingFestivals = false);
    }
  }

  /// Abre el selector de localizaciones y añade la localización de rodaje elegida.
  void _addFilmLocation() {
    LocationSelector.show(
      context,
      onSelected: (location) async {
        if (_filmLocations.any((e) => e.locationId == location.id)) return;
        setState(() {
          _filmLocations.add(_FilmLocationEntry(
            locationId: location.id!,
            role: 'primary',
          ));
          _locationCache[location.id!] = location;
        });
      },
    );
  }

  void _removeFilmLocation(int index) {
    setState(() => _filmLocations.removeAt(index));
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

  /// Valida y envía el cortometraje junto con sus localizaciones de rodaje,
  /// encolando la creación para sincronización offline cuando la API no está
  /// disponible.
  Future<void> _submit() async {
    if (_isLoading) return;
    if (!_formKey.currentState!.validate()) return;

    final isLoggedIn = await AuthService().isLoggedIn();
    if (!isLoggedIn) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(l10n.loginRequired),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
      return;
    }

    setState(() => _isLoading = true);

    final shortFilm = ShortFilm(
      title: _titleController.text.trim(),
      description: _descriptionController.text.isNotEmpty
          ? _descriptionController.text.trim()
          : null,
      duration: int.tryParse(_durationController.text),
      videoUrl: _videoUrlController.text.isNotEmpty
          ? _videoUrlController.text.trim()
          : null,
      thumbnailUrl: _thumbnailUrlController.text.isNotEmpty
          ? _thumbnailUrlController.text.trim()
          : null,
      festivalId: _selectedFestivalId,
      userId: 0,
      isPublic: _isPublic,
      tags: _tagsController.text.isNotEmpty
          ? _tagsController.text.trim()
          : null,
    );

    try {
      final created = await ApiService().createShortFilm(shortFilm);

      if (_filmLocations.isNotEmpty && created.id != null) {
        for (final entry in _filmLocations) {
          try {
            await ApiService().addFilmLocation(created.id!, {
              'location_id': entry.locationId,
              'role': entry.role,
            });
          } catch (e) { debugPrint('Error: $e'); }
        }
      }

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(l10n.success),
            behavior: SnackBarBehavior.floating,
          ),
        );
        Navigator.pop(context, true);
      }
    } catch (e) {
      debugPrint('Error: $e');
      final queue = SyncQueueService.instance;
      final payload = shortFilm.toJson();
      if (!queue.contains(
          entityType: 'shortfilm', operation: 'create', payload: payload)) {
        await queue.enqueue(
          entityType: 'shortfilm',
          operation: 'create',
          payload: payload,
        );
      }
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(ConnectivityMonitor.instance.isOnline ? l10n.loadError : '${l10n.success}. ${l10n.syncPending.replaceAll('{count}', '1')}'),
            behavior: SnackBarBehavior.floating,
          ),
        );
        Navigator.pop(context, true);
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Scaffold(
      appBar: AppBar(
        title: SemanticHeader(text: l10n.createShortFilm),
      ),
      body: LayoutBuilder(
        builder: (context, constraints) {
          return Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 600),
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(24),
                child: Form(
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
                      if (_isLoadingFestivals)
                        const LinearProgressIndicator()
                      else
                        Semantics(
                          label: l10n.festivals,
                          child: DropdownButtonFormField<int>(
                            initialValue: _selectedFestivalId,
                            decoration: InputDecoration(
                              labelText: l10n.festivals,
                              border: const OutlineInputBorder(),
                              prefixIcon: const Icon(Icons.festival),
                            ),
                            items: [
                              DropdownMenuItem<int>(
                                value: null,
                                child: Text(l10n.optional),
                              ),
                              ..._festivals.map((f) => DropdownMenuItem(
                                    value: f.id,
                                    child: Text(f.name),
                                  )),
                            ],
                            onChanged: (v) =>
                                setState(() => _selectedFestivalId = v),
                          ),
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
                          subtitle:
                              Text(_isPublic ? l10n.public : l10n.private),
                          value: _isPublic,
                          onChanged: (v) => setState(() => _isPublic = v),
                        ),
                      ),
                      const SizedBox(height: 24),
                      _buildFilmLocationsSection(theme, colorScheme),
                      const SizedBox(height: 24),
                      Semantics(
                        label: l10n.createShortFilm,
                        child: FilledButton(
                          style: FilledButton.styleFrom(
                            padding: const EdgeInsets.symmetric(vertical: 16),
                            minimumSize: const Size.fromHeight(50),
                          ),
                          onPressed: _isLoading ? null : _submit,
                          child: _isLoading
                              ? const SizedBox(
                                  height: 20,
                                  width: 20,
                                  child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                                )
                              : Text(l10n.createShortFilm),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          );
        },
      ),
    );
  }

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
                  child: Text(l10n.whereWasItFilmed, style: theme.textTheme.titleSmall?.copyWith(color: colorScheme.primary)),
                ),
              ),
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
            ..._filmLocations.asMap().entries.map((entry) {
              final i = entry.key;
              final flEntry = entry.value;
              final loc = _locationCache[flEntry.locationId];
              return Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Row(
                  children: [
                    Expanded(
                      child: FilmLocationCard(
                        filmLocation: FilmLocation(
                          shortfilmId: 0,
                          locationId: flEntry.locationId,
                          role: flEntry.role,
                          createdBy: 0,
                        ),
                        location: loc,
                        onTap: null,
                        showActions: false,
                      ),
                    ),
                    IconButton(
                      icon: Icon(Icons.close_rounded, size: 18, color: colorScheme.onSurfaceVariant),
                      onPressed: () => _removeFilmLocation(i),
                      visualDensity: VisualDensity.compact,
                      padding: EdgeInsets.zero,
                      constraints: const BoxConstraints(minWidth: 32, minHeight: 32),
                    ),
                  ],
                ),
              );
            }),
        ],
      ),
    );
  }
}

/// Entrada de localización de rodaje pendiente seleccionada para el nuevo
/// cortometraje.
class _FilmLocationEntry {
  final int locationId;
  String role;

  _FilmLocationEntry({required this.locationId, this.role = 'primary'});
}
