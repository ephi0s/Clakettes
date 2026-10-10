import 'package:flutter/material.dart' hide FormField;
import '../l10n/app_localizations.dart';
import '../services/api_service.dart';
import '../models/form_definition_model.dart';
import '../widgets/loading_skeleton.dart';
import '../widgets/error_state_widget.dart';

/// Renderiza una definición de formulario compartida mediante un token
/// público y envía las respuestas recogidas sin requerir autenticación.
class PublicFormScreen extends StatefulWidget {
  final String token;
  const PublicFormScreen({super.key, required this.token});

  @override
  State<PublicFormScreen> createState() => _PublicFormScreenState();
}

/// Estado de [PublicFormScreen]. Carga el formulario por token en el primer
/// build y mantiene los valores y controladores de cada campo renderizado.
class _PublicFormScreenState extends State<PublicFormScreen> {
  final ApiService api = ApiService();
  FormDefinition? _form;
  bool _isLoading = true;
  bool _hasError = false;
  bool _isSubmitting = false;
  bool _isSubmitted = false;
  bool _initialized = false;
  late AppLocalizations l10n;
  final Map<int, dynamic> _values = {};
  final Map<int, TextEditingController> _controllers = {};
  final Map<int, bool> _booleans = {};
  final Map<int, List<String>> _multiselects = {};
  final _formKey = GlobalKey<FormState>();

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    l10n = AppLocalizations.of(context)!;
    if (!_initialized) {
      _initialized = true;
      _loadForm();
    }
  }

  /// Obtiene la definición del formulario para el token público e inicializa los valores.
  Future<void> _loadForm() async {
    if (!mounted) return;
    setState(() { _isLoading = true; _hasError = false; });
    try {
      _form = await api.getPublicForm(widget.token);
      if (!mounted) return;
      _initValues();
      setState(() { _isLoading = false; });
    } catch (e) {
      debugPrint('Error: $e');
      if (!mounted) return;
      setState(() { _isLoading = false; _hasError = true; });
    }
  }

  /// Crea controladores, valores booleanos y multiselecciones a partir de los valores por defecto.
  void _initValues() {
    if (_form == null) return;
    for (final page in _form!.pages) {
      for (final f in page.fields) {
        if (f.id == null) continue;
        if (f.fieldType == FormFieldType.boolean) {
          _booleans[f.id!] = f.defaultValue == 'true';
        } else if (f.fieldType == FormFieldType.multiselect) {
          _multiselects[f.id!] = [];
        } else {
          _controllers[f.id!] = TextEditingController(text: f.defaultValue);
        }
      }
    }
  }

  @override
  void dispose() {
    for (final c in _controllers.values) {
      c.dispose();
    }
    super.dispose();
  }

  /// Valida un campo: comprobación de obligatorio más reglas de longitud y regex.
  String? _validateField(FormField f) {
    if (f.id == null) return null;
    if (f.isRequired) {
      if (f.fieldType == FormFieldType.boolean) {
        return null;
      }
      if (f.fieldType == FormFieldType.multiselect) {
        if ((_multiselects[f.id!] ?? []).isEmpty) return l10n.translate('fieldRequired');
        return null;
      }
      final val = _controllers[f.id!]?.text.trim() ?? '';
      if (val.isEmpty) return l10n.translate('fieldRequired');
    }
    final val = _controllers[f.id!]?.text.trim() ?? '';
    if (val.isEmpty) return null;
    if (f.minLength != null && val.length < f.minLength!) {
      return l10n.translate('minLengthError');
    }
    if (f.maxLength != null && val.length > f.maxLength!) {
      return l10n.translate('maxLengthError');
    }
    if (f.regexPattern != null && f.regexPattern!.isNotEmpty) {
      try {
        if (!RegExp(f.regexPattern!).hasMatch(val)) {
          return f.errorMessage ?? l10n.translate('invalidFormat');
        }
      } catch (e) { debugPrint('Error: $e'); }
    }
    return null;
  }

  /// Valida el formulario y envía las respuestas recogidas mediante la API.
  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    if (_form == null) return;
    setState(() => _isSubmitting = true);
    try {
      final data = <String, dynamic>{};
      final fieldResponses = <Map<String, dynamic>>[];
      for (final page in _form!.pages) {
        for (final f in page.fields) {
          if (f.id == null) continue;
          dynamic value;
          if (f.fieldType == FormFieldType.boolean) {
            value = _booleans[f.id!];
          } else if (f.fieldType == FormFieldType.multiselect) {
            value = _multiselects[f.id!];
          } else if (f.fieldType == FormFieldType.select) {
            value = _values[f.id!];
          } else {
            value = _controllers[f.id!]?.text.trim() ?? '';
          }
          fieldResponses.add({'field_id': f.id!, 'value': value});
        }
      }
      data['field_responses'] = fieldResponses;
      await api.submitPublicResponse(widget.token, data);
      if (mounted) setState(() { _isSubmitting = false; _isSubmitted = true; });
    } catch (e) {
      if (mounted) {
        setState(() => _isSubmitting = false);
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.errorFormatWith('$e')), behavior: SnackBarBehavior.floating));
      }
    }
  }

  /// Construye el widget de un campo de formulario según su tipo.
  Widget _buildField(FormField f) {
    final id = f.id;
    if (id == null) return const SizedBox.shrink();
    switch (f.fieldType) {
      case FormFieldType.sectionBreak:
        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 16),
          child: Column(children: [
            const Divider(),
            if (f.label.isNotEmpty) Text(f.label, style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600)),
            if (f.helpText != null && f.helpText!.isNotEmpty) Text(f.helpText!, style: Theme.of(context).textTheme.bodySmall),
          ]),
        );
      case FormFieldType.staticText:
        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 8),
          child: Text(f.label, style: Theme.of(context).textTheme.bodyLarge),
        );
      case FormFieldType.boolean:
        return SwitchListTile(
          title: Text(f.label),
          subtitle: f.helpText != null ? Text(f.helpText!) : null,
          value: _booleans[id] ?? false,
          onChanged: (v) => setState(() { _booleans[id] = v; }),
        );
      case FormFieldType.select:
        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 8),
          child: DropdownButtonFormField<String>(
            initialValue: _values[id] as String?,
            decoration: InputDecoration(labelText: f.label, helperText: f.helpText),
            items: f.options.map((o) => DropdownMenuItem(value: o.value, child: Text(o.label))).toList(),
            onChanged: (v) { if (v != null) setState(() { _values[id] = v; }); },
            validator: (_) => f.isRequired && _values[id] == null ? l10n.translate('fieldRequired') : null,
          ),
        );
      case FormFieldType.multiselect:
        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 8),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(f.label, style: const TextStyle(fontWeight: FontWeight.w600)),
            if (f.helpText != null) Text(f.helpText!, style: Theme.of(context).textTheme.bodySmall),
            ...f.options.map((o) => CheckboxListTile(
              title: Text(o.label),
              value: (_multiselects[id] ?? []).contains(o.value),
              onChanged: (checked) {
                setState(() {
                  if (checked == true) {
                    _multiselects[id] = [...(_multiselects[id] ?? []), o.value];
                  } else {
                    _multiselects[id] = (_multiselects[id] ?? []).where((x) => x != o.value).toList();
                  }
                });
              },
              dense: true,
            )),
          ]),
        );
      case FormFieldType.email:
        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 8),
          child: TextFormField(
            controller: _controllers[id],
            decoration: InputDecoration(labelText: f.label, helperText: f.helpText ?? f.placeholder),
            keyboardType: TextInputType.emailAddress,
            validator: (_) => _validateField(f),
          ),
        );
      case FormFieldType.phone:
        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 8),
          child: TextFormField(
            controller: _controllers[id],
            decoration: InputDecoration(labelText: f.label, helperText: f.helpText ?? f.placeholder),
            keyboardType: TextInputType.phone,
            validator: (_) => _validateField(f),
          ),
        );
      case FormFieldType.url:
        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 8),
          child: TextFormField(
            controller: _controllers[id],
            decoration: InputDecoration(labelText: f.label, helperText: f.helpText ?? f.placeholder),
            keyboardType: TextInputType.url,
            validator: (_) => _validateField(f),
          ),
        );
      case FormFieldType.date:
        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 8),
          child: TextFormField(
            controller: _controllers[id],
            decoration: InputDecoration(
              labelText: f.label,
              helperText: f.helpText,
              suffixIcon: IconButton(icon: const Icon(Icons.date_range), onPressed: () async {
                final date = await showDatePicker(context: context, firstDate: DateTime(2020), lastDate: DateTime(2035));
                if (date != null) _controllers[id]?.text = date.toIso8601String().substring(0, 10);
              }),
            ),
            readOnly: true,
            validator: (_) => _validateField(f),
          ),
        );
      case FormFieldType.number:
        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 8),
          child: TextFormField(
            controller: _controllers[id],
            decoration: InputDecoration(labelText: f.label, helperText: f.helpText),
            keyboardType: TextInputType.number,
            validator: (_) => _validateField(f),
          ),
        );
      case FormFieldType.file:
        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 8),
          child: OutlinedButton.icon(
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.translate('fileUploadNotSupported')), behavior: SnackBarBehavior.floating));
            },
            icon: const Icon(Icons.upload_file),
            label: Text(f.label),
          ),
        );
      default:
        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 8),
          child: TextFormField(
            controller: _controllers[id],
            decoration: InputDecoration(labelText: f.label, helperText: f.helpText ?? f.placeholder),
            validator: (_) => _validateField(f),
          ),
        );
    }
  }

  @override
  Widget build(BuildContext context) {
    l10n = AppLocalizations.of(context)!;

    return Scaffold(
      appBar: AppBar(title: Text(_form?.title ?? '...')),
      body: _isLoading
          ? const ListSkeleton()
          : _hasError
              ? ErrorStateWidget(onRetry: _loadForm)
              : _isSubmitted
                  ? Center(
                      child: Padding(
                        padding: const EdgeInsets.all(32),
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(Icons.check_circle_outline, size: 64, color: Theme.of(context).colorScheme.primary),
                            const SizedBox(height: 16),
                            Text(_form?.successMessage ?? l10n.formSubmitted, style: Theme.of(context).textTheme.titleLarge),
                          ],
                        ),
                      ),
                    )
                  : Form(
                      key: _formKey,
                      child: SingleChildScrollView(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            if (_form?.description != null && _form!.description!.isNotEmpty)
                              Padding(
                                padding: const EdgeInsets.only(bottom: 16),
                                child: Text(_form!.description!, style: Theme.of(context).textTheme.bodyLarge),
                              ),
                            for (final page in _form?.pages ?? [])
                              Padding(
                                padding: const EdgeInsets.only(bottom: 24),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.stretch,
                                  children: [
                                    Text(page.title, style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w600)),
                                    if (page.description != null && page.description!.isNotEmpty)
                                      Padding(
                                        padding: const EdgeInsets.only(top: 4, bottom: 12),
                                        child: Text(page.description!, style: Theme.of(context).textTheme.bodyMedium),
                                      ),
                                    ...page.fields.map((f) => _buildField(f)),
                                  ],
                                ),
                              ),
                            const SizedBox(height: 16),
                            FilledButton.icon(
                              onPressed: _isSubmitting ? null : _submit,
                              icon: _isSubmitting ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2)) : const Icon(Icons.send),
                              label: Text(_form?.submitButtonText ?? l10n.submitForm),
                            ),
                            const SizedBox(height: 32),
                          ],
                        ),
                      ),
                    ),
    );
  }
}
