import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import '../models/registration_form_model.dart';
import '../widgets/loading_skeleton.dart';
import '../widgets/error_state_widget.dart';
import '../widgets/confirm_dialog.dart';

/// Permite inscribirse a un festival mediante un enlace público de un formulario
/// de inscripción ([RegistrationForm]) y muestra el resumen de la cuota antes
/// de enviar la solicitud.
class PublicRegistrationScreen extends StatefulWidget {
  final String token;
  const PublicRegistrationScreen({super.key, required this.token});

  @override
  State<PublicRegistrationScreen> createState() => _PublicRegistrationScreenState();
}

/// Estado de [PublicRegistrationScreen]. Carga el formulario público por token,
/// recoge la selección de secciones y envía la inscripción al confirmar.
class _PublicRegistrationScreenState extends State<PublicRegistrationScreen> {
  final ApiService api = ApiService();
  RegistrationForm? _form;
  FestivalRegistration? _registration;
  bool _isLoading = true;
  bool _hasError = false;
  bool _isSubmitting = false;
  bool _isSubmitted = false;
  bool _loggedIn = false;
  bool _initialized = false;
  late AppLocalizations l10n;
  final Map<int, int?> _selectedRole = {};
  final Map<int, Set<int>> _selectedTags = {};

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    l10n = AppLocalizations.of(context)!;
    if (!_initialized) {
      _initialized = true;
      _loadForm();
    }
  }

  /// Obtiene el formulario de inscripción público mediante el token y
  /// comprueba si el usuario tiene sesión iniciada.
  Future<void> _loadForm() async {
    if (!mounted) return;
    setState(() { _isLoading = true; _hasError = false; });
    try {
      final form = await api.getPublicRegistrationForm(widget.token);
      final loggedIn = await AuthService().isLoggedIn();
      if (!mounted) return;
      setState(() { _form = form; _loggedIn = loggedIn; _isLoading = false; });
    } catch (e) {
      debugPrint('Error: $e');
      if (!mounted) return;
      setState(() { _isLoading = false; _hasError = true; });
    }
  }

  /// Devuelve la cuota formateada ("25 EUR") o cadena vacía si no hay cuota.
  String _feeText(RegistrationForm form) {
    final fee = form.feeAmount;
    if (fee == null || fee <= 0) return '';
    final formatted = fee == fee.roundToDouble() ? fee.round().toString() : fee.toString();
    return '$formatted ${form.currency}';
  }

  /// Muestra el resumen de la cuota (si aplica) y envía la inscripción.
  Future<void> _submit() async {
    final form = _form;
    final formId = form?.id;
    if (form == null || formId == null) return;
    final feeText = _feeText(form);
    if (feeText.isNotEmpty) {
      final ok = await showConfirmDialog(context, title: l10n.registrationFee, message: l10n.payInstructions(feeText));
      if (ok != true) return;
    }
    if (!mounted) return;
    setState(() => _isSubmitting = true);
    try {
      final selections = <Map<String, dynamic>>[];
      for (final s in form.sections) {
        if (s.id == null) continue;
        selections.add({
          'section_id': s.id,
          'role_id': _selectedRole[s.id],
          'additional_tag_ids': (_selectedTags[s.id] ?? const <int>{}).toList(),
        });
      }
      final registration = await api.registerViaPublicLink(widget.token, formId, selections);
      if (!mounted) return;
      setState(() { _registration = registration; _isSubmitting = false; _isSubmitted = true; });
    } catch (e) {
      debugPrint('Error: $e');
      if (!mounted) return;
      setState(() => _isSubmitting = false);
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.errorFor(e)), behavior: SnackBarBehavior.floating));
    }
  }

  /// Tarjeta con el resumen de la cuota y las instrucciones de pago.
  Widget _buildFeeCard(String feeText) {
    final theme = Theme.of(context);
    return Card(
      margin: EdgeInsets.zero,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(children: [
          Icon(Icons.payments_outlined, color: theme.colorScheme.primary),
          const SizedBox(width: 12),
          Expanded(
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text('${l10n.registrationFee}: $feeText', style: const TextStyle(fontWeight: FontWeight.w600)),
              const SizedBox(height: 4),
              Text(l10n.payInstructions(feeText), style: theme.textTheme.bodySmall),
            ]),
          ),
        ]),
      ),
    );
  }

  /// Renderiza una sección del formulario con selector de rol y etiquetas.
  Widget _buildSection(RegistrationFormSection s) {
    final theme = Theme.of(context);
    final sectionId = s.id;
    if (sectionId == null) return const SizedBox.shrink();
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(s.title, style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600)),
          if (s.description != null && s.description!.isNotEmpty) ...[
            const SizedBox(height: 4),
            Text(s.description!, style: theme.textTheme.bodySmall),
          ],
          if (s.roleIds.isNotEmpty) ...[
            const SizedBox(height: 12),
            DropdownButtonFormField<int>(
              initialValue: _selectedRole[sectionId] ?? -1,
              decoration: InputDecoration(labelText: l10n.role),
              items: [
                DropdownMenuItem<int>(value: -1, child: Text(l10n.optional)),
                ...s.roleIds.map((roleId) => DropdownMenuItem<int>(value: roleId, child: Text('${l10n.role} #$roleId'))),
              ],
              onChanged: (v) => setState(() { _selectedRole[sectionId] = (v == null || v == -1) ? null : v; }),
            ),
          ],
          if (s.tagIds.isNotEmpty) ...[
            const SizedBox(height: 12),
            Text(l10n.tags, style: theme.textTheme.bodySmall),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: s.tagIds.map((tagId) {
                final selected = (_selectedTags[sectionId] ?? const <int>{}).contains(tagId);
                return FilterChip(
                  label: Text('${l10n.tags} #$tagId'),
                  selected: selected,
                  onSelected: (on) {
                    setState(() {
                      final current = {...(_selectedTags[sectionId] ?? const <int>{})};
                      if (on) {
                        current.add(tagId);
                      } else {
                        current.remove(tagId);
                      }
                      _selectedTags[sectionId] = current;
                    });
                  },
                );
              }).toList(),
            ),
          ],
        ]),
      ),
    );
  }

  /// Pantalla de confirmación mostrada tras enviar la inscripción.
  Widget _buildConfirmation() {
    final theme = Theme.of(context);
    final feeText = _form == null ? '' : _feeText(_form!);
    final isPending = _registration?.paymentStatus == 'pending';
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(mainAxisSize: MainAxisSize.min, children: [
          Icon(
            isPending ? Icons.hourglass_top : Icons.check_circle_outline,
            size: 64,
            color: isPending ? Colors.orange : theme.colorScheme.primary,
          ),
          const SizedBox(height: 16),
          Text(isPending ? l10n.paymentPending : l10n.formSubmitted, style: theme.textTheme.titleLarge),
          if (isPending && feeText.isNotEmpty) ...[
            const SizedBox(height: 8),
            Text(l10n.payInstructions(feeText), textAlign: TextAlign.center, style: theme.textTheme.bodyMedium),
          ],
          if (isPending) ...[
            const SizedBox(height: 8),
            Text(l10n.paymentRequiredForApproval, textAlign: TextAlign.center, style: theme.textTheme.bodySmall),
          ],
        ]),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    l10n = AppLocalizations.of(context)!;
    final form = _form;
    final feeText = form == null ? '' : _feeText(form);

    return Scaffold(
      appBar: AppBar(title: Text(form?.title ?? '...')),
      body: _isLoading
          ? const ListSkeleton()
          : _hasError
              ? ErrorStateWidget(onRetry: _loadForm)
              : _isSubmitted
                  ? _buildConfirmation()
                  : Form(
                      child: SingleChildScrollView(
                        padding: const EdgeInsets.all(16),
                        child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
                          if (form!.description != null && form.description!.isNotEmpty)
                            Padding(
                              padding: const EdgeInsets.only(bottom: 16),
                              child: Text(form.description!, style: Theme.of(context).textTheme.bodyLarge),
                            ),
                          if (feeText.isNotEmpty) ...[
                            _buildFeeCard(feeText),
                            const SizedBox(height: 16),
                          ],
                          ...form.sections.map((s) => _buildSection(s)),
                          const SizedBox(height: 8),
                          if (!_loggedIn) ...[
                            Text(l10n.loginRequired, style: TextStyle(color: Theme.of(context).colorScheme.error)),
                            const SizedBox(height: 8),
                          ],
                          FilledButton.icon(
                            onPressed: (_isSubmitting || !_loggedIn) ? null : _submit,
                            icon: _isSubmitting
                                ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2))
                                : const Icon(Icons.send),
                            label: Text(l10n.submitForm),
                          ),
                          const SizedBox(height: 32),
                        ]),
                      ),
                    ),
    );
  }
}
