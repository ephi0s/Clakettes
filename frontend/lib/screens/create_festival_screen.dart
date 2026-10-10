import 'package:flutter/material.dart';
import 'package:latlong2/latlong.dart';
import '../l10n/app_localizations.dart';
import '../models/festival_model.dart';
import '../services/api_service.dart';
import '../services/sync_queue_service.dart';
import '../services/auth_service.dart';
import '../services/connectivity_monitor.dart';
import '../widgets/reusable_widgets.dart';
import '../widgets/map_picker.dart';

/// Formulario a pantalla completa para crear un nuevo festival.
///
/// Valida los campos obligatorios (nombre) mediante [SemanticTextField] con
/// mensajes de error localizados. Al tener éxito se cierra con `true`.
class CreateFestivalScreen extends StatefulWidget {
  const CreateFestivalScreen({super.key});

  @override
  State<CreateFestivalScreen> createState() => _CreateFestivalScreenState();
}

/// Mantiene los controladores del formulario, las coordenadas seleccionadas y
/// el estado de envío.
class _CreateFestivalScreenState extends State<CreateFestivalScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _locationController = TextEditingController();
  final _websiteController = TextEditingController();
  final _logoUrlController = TextEditingController();

  LatLng? _selectedLatLng;
  bool _isActive = true;
  bool _isLoading = false;
  late AppLocalizations l10n;

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
    _websiteController.dispose();
    _logoUrlController.dispose();
    super.dispose();
  }

  /// Abre el selector de mapa y guarda las coordenadas devueltas.
  Future<void> _pickLocation() async {
    final result = await Navigator.push<LatLng>(
      context,
      MaterialPageRoute(
        builder: (_) => MapPickerScreen(
          l10n: l10n,
          initialLocation: _selectedLatLng,
        ),
      ),
    );
    if (result != null && mounted) {
      setState(() => _selectedLatLng = result);
    }
  }

  /// Valida y envía el festival, encolándolo para sincronización offline en
  /// caso de error.
  Future<void> _submit() async {
    if (_isLoading) return;
    if (!_formKey.currentState!.validate()) return;

    final isLoggedIn = await AuthService().isLoggedIn();
    if (!isLoggedIn) {
      if (mounted) showAppSnack(context, l10n.loginRequired);
      return;
    }

    setState(() => _isLoading = true);

    final festival = Festival(
      name: _nameController.text.trim(),
      description: _descriptionController.text.isNotEmpty
          ? _descriptionController.text.trim()
          : null,
      location: _locationController.text.isNotEmpty
          ? _locationController.text.trim()
          : null,
      latitude: _selectedLatLng?.latitude,
      longitude: _selectedLatLng?.longitude,
      isActive: _isActive,
      website: _websiteController.text.isNotEmpty
          ? _websiteController.text.trim()
          : null,
      logoUrl: _logoUrlController.text.isNotEmpty
          ? _logoUrlController.text.trim()
          : null,
    );

    try {
      await ApiService().createFestival(festival);

      if (mounted) {
        showAppSnack(context, l10n.success);
        Navigator.pop(context, true);
      }
    } catch (e) {
      debugPrint('Error: $e');
      await SyncQueueService.instance.enqueue(
        entityType: 'festival',
        operation: 'create',
        payload: festival.toJson(),
      );
      if (mounted) {
        showAppSnack(
          context,
          ConnectivityMonitor.instance.isOnline ? l10n.loadError : '${l10n.success}. ${l10n.syncPending.replaceAll('{count}', '1')}',
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

    return Scaffold(
      appBar: AppBar(
        title: SemanticHeader(text: l10n.createFestival),
      ),
      body: LayoutBuilder(
        builder: (context, constraints) {
          final theme = Theme.of(context);
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
                      InkWell(
                        onTap: _pickLocation,
                        borderRadius: BorderRadius.circular(12),
                        child: Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            border: Border.all(
                              color: theme.colorScheme.outline.withAlpha(80),
                            ),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: _selectedLatLng != null
                              ? Row(
                                  children: [
                                    Icon(Icons.location_on,
                                        color: theme.colorScheme.primary),
                                    const SizedBox(width: 12),
                                    Expanded(
                                      child: Column(
                                        crossAxisAlignment:
                                            CrossAxisAlignment.start,
                                        children: [
                                          Text(
                                            l10n.location,
                                            style: theme.textTheme
                                                .labelSmall
                                                ?.copyWith(
                                              color: theme
                                                  .colorScheme
                                                  .onSurfaceVariant,
                                            ),
                                          ),
                                          const SizedBox(height: 2),
                                          Text(
                                            '${_selectedLatLng!.latitude.toStringAsFixed(6)}, ${_selectedLatLng!.longitude.toStringAsFixed(6)}',
                                            style: theme
                                                .textTheme.bodyMedium
                                                ?.copyWith(
                                              fontFamily: 'monospace',
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                    IconButton(
                                      icon: const Icon(Icons.refresh),
                                      onPressed: _pickLocation,
                                      tooltip: l10n.openMap,
                                    ),
                                    IconButton(
                                      icon: Icon(Icons.clear,
                                          color: theme.colorScheme.error),
                                      onPressed: () =>
                                          setState(() => _selectedLatLng = null),
                                      tooltip: l10n.delete,
                                    ),
                                  ],
                                )
                              : Row(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Icon(Icons.map,
                                        color: theme.colorScheme.primary),
                                    const SizedBox(width: 8),
                                    Text(l10n.openMap),
                                  ],
                                ),
                        ),
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
                      const SizedBox(height: 24),
                      Semantics(
                        label: l10n.createFestival,
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
                              : Text(l10n.createFestival),
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
}
