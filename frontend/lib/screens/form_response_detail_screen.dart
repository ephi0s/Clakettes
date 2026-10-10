import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../services/api_service.dart';
import '../models/form_definition_model.dart';
import '../widgets/reusable_widgets.dart';
import '../widgets/loading_skeleton.dart';
import '../widgets/error_state_widget.dart';

/// Pantalla que muestra una única respuesta de formulario con sus respuestas
/// y las acciones para aprobarla o rechazarla.
class FormResponseDetailScreen extends StatefulWidget {
  final FormResponse response;
  const FormResponseDetailScreen({super.key, required this.response});

  @override
  State<FormResponseDetailScreen> createState() => _FormResponseDetailScreenState();
}

/// Mantiene la respuesta y la definición del formulario padre cargada para
/// resolver las etiquetas y los tipos de los campos.
class _FormResponseDetailScreenState extends State<FormResponseDetailScreen> {
  final ApiService api = ApiService();
  FormDefinition? _form;
  bool _isLoadingForm = false;
  bool _formError = false;
  bool _initialized = false;
  late AppLocalizations l10n;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    l10n = AppLocalizations.of(context)!;
    if (!_initialized) {
      _initialized = true;
      _loadForm();
    }
  }

  /// Carga la definición del formulario padre para resolver los metadatos de
  /// los campos.
  Future<void> _loadForm() async {
    if (!mounted) return;
    setState(() { _isLoadingForm = true; _formError = false; });
    try {
      _form = await api.getForm(widget.response.formId);
      if (!mounted) return;
      setState(() { _isLoadingForm = false; });
    } catch (e) {
      debugPrint('Error: $e');
      if (!mounted) return;
      setState(() { _isLoadingForm = false; _formError = true; });
    }
  }

  /// Busca la etiqueta del campo que coincide con el id indicado.
  String _findFieldLabel(int fieldId) {
    if (_form == null) return '#$fieldId';
    for (final page in _form!.pages) {
      for (final f in page.fields) {
        if (f.id == fieldId) return f.label;
      }
    }
    return '#$fieldId';
  }

  /// Formatea el valor de una respuesta guardada según su tipo de campo.
  String _formatValue(dynamic value, String fieldType) {
    if (value == null) return '-';
    if (fieldType == FormFieldType.boolean) {
      return value == true ? l10n.translate('yes') : l10n.translate('no');
    }
    if (fieldType == FormFieldType.multiselect && value is List) {
      return value.join(', ');
    }
    return value.toString();
  }

  /// Busca el tipo del campo que coincide con el id indicado.
  String? _findFieldType(int fieldId) {
    if (_form == null) return null;
    for (final page in _form!.pages) {
      for (final f in page.fields) {
        if (f.id == fieldId) return f.fieldType;
      }
    }
    return null;
  }

  /// Aprueba la respuesta y se cierra con `true` al tener éxito.
  Future<void> _approve() async {
    if (widget.response.id == null) return;
    try {
      await api.approveResponse(widget.response.id!);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.responseApproved), behavior: SnackBarBehavior.floating));
        Navigator.pop(context, true);
      }
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.errorFormatWith('$e')), behavior: SnackBarBehavior.floating));
    }
  }

  /// Rechaza la respuesta, recopilando antes un motivo opcional.
  Future<void> _reject() async {
    final reason = await showDialog<String>(
      context: context,
      builder: (ctx) {
        final ctl = TextEditingController();
        return AlertDialog(
          title: Text(l10n.rejectReason),
          content: TextField(controller: ctl, decoration: InputDecoration(labelText: l10n.reviewNotes), maxLines: 3),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: Text(l10n.cancel)),
            FilledButton(onPressed: () => Navigator.pop(ctx, ctl.text), child: Text(l10n.reject)),
          ],
        );
      },
    );
    if (reason == null || widget.response.id == null) return;
    try {
      await api.rejectResponse(widget.response.id!, reason: reason);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.responseRejected), behavior: SnackBarBehavior.floating));
        Navigator.pop(context, true);
      }
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.errorFormatWith('$e')), behavior: SnackBarBehavior.floating));
    }
  }

  @override
  Widget build(BuildContext context) {
    l10n = AppLocalizations.of(context)!;
    final r = widget.response;

    return Scaffold(
      appBar: AppBar(
        title: Text('${l10n.responseDetail} #${r.id}'),
        actions: [
          if (r.status != 'approved')
            IconButton(icon: const Icon(Icons.check_circle_outline), tooltip: l10n.approve, onPressed: _approve),
          if (r.status != 'rejected')
            IconButton(icon: const Icon(Icons.cancel_outlined), tooltip: l10n.reject, onPressed: _reject),
        ],
      ),
      body: _isLoadingForm
          ? const ListSkeleton()
          : _formError
              ? ErrorStateWidget(onRetry: _loadForm)
              : SingleChildScrollView(
                  padding: const EdgeInsets.all(16),
                  child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                    Card(
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            InfoRow(icon: Icons.info_outline, text: '${l10n.translate('status')}: ${r.status}', semanticLabel: r.status),
                            if (r.submittedAt != null)
                              InfoRow(icon: Icons.schedule, text: '${l10n.submittedAt}: ${r.submittedAt!.toIso8601String().substring(0, 16)}', semanticLabel: ''),
                            if (r.reviewNotes != null && r.reviewNotes!.isNotEmpty)
                              InfoRow(icon: Icons.notes, text: '${l10n.reviewNotes}: ${r.reviewNotes}', semanticLabel: ''),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),
                    Text(l10n.translate('fieldResponses'), style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600)),
                    const SizedBox(height: 8),
                    if (r.fieldResponses.isEmpty)
                      Padding(
                        padding: const EdgeInsets.all(16),
                        child: Text(l10n.translate('noFieldResponses'), style: TextStyle(color: Theme.of(context).colorScheme.onSurfaceVariant)),
                      )
                    else
                      ...r.fieldResponses.map((fr) {
                        final fieldType = _findFieldType(fr.fieldId) ?? FormFieldType.string;
                        return Card(
                          margin: const EdgeInsets.only(bottom: 8),
                          child: ListTile(
                            title: Text(_findFieldLabel(fr.fieldId), style: const TextStyle(fontWeight: FontWeight.w600)),
                            subtitle: Text(_formatValue(fr.value, fieldType)),
                          ),
                        );
                      }),
                  ]),
                ),
    );
  }
}
