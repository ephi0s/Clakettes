import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../services/api_service.dart';
import '../models/form_definition_model.dart';
import '../widgets/reusable_widgets.dart';
import '../widgets/empty_state_widget.dart';
import '../widgets/loading_skeleton.dart';
import '../widgets/error_state_widget.dart';
import '../widgets/confirm_dialog.dart';
import 'form_detail_screen.dart';

/// Pantalla que lista las definiciones de formulario con filtro por tipo,
/// crear, clonar y eliminar.
class FormDefinitionsScreen extends StatefulWidget {
  const FormDefinitionsScreen({super.key});

  @override
  State<FormDefinitionsScreen> createState() => _FormDefinitionsScreenState();
}

/// Mantiene los formularios cargados y el filtro de tipo activo; se carga en
/// el primer build.
class _FormDefinitionsScreenState extends State<FormDefinitionsScreen> {
  final ApiService api = ApiService();
  List<FormDefinition> _forms = [];
  String? _typeFilter;
  bool _isLoading = true;
  bool _hasError = false;
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

  /// Carga las definiciones de formulario, opcionalmente filtradas por tipo.
  Future<void> _loadData() async {
    if (!mounted) return;
    setState(() { _isLoading = true; _hasError = false; });
    try {
      final result = await api.getForms(formType: _typeFilter, size: 100);
      if (!mounted) return;
      setState(() { _forms = result.items; _isLoading = false; });
    } catch (e) {
      debugPrint('Error: $e');
      if (!mounted) return;
      setState(() { _isLoading = false; _hasError = true; });
    }
  }

  /// Muestra un diálogo para crear un nuevo formulario y lo abre en la
  /// pantalla de detalle.
  Future<void> _createForm() async {
    final titleCtl = TextEditingController();
    final descCtl = TextEditingController();
    String selectedType = FormType.festivalRegistration;
    final result = await showDialog<Map<String, dynamic>>(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setDialogState) => AlertDialog(
          title: Text(l10n.newForm),
          content: SingleChildScrollView(
            child: Column(mainAxisSize: MainAxisSize.min, children: [
              SemanticTextField(controller: titleCtl, label: l10n.titleRequired, semanticLabel: l10n.formTitle, helperText: l10n.formTitle),
              const SizedBox(height: 12),
              SemanticTextField(controller: descCtl, label: l10n.description, semanticLabel: l10n.description, helperText: l10n.optionalDescription),
              const SizedBox(height: 12),
              DropdownButton<String>(
                value: selectedType,
                isExpanded: true,
                underline: const SizedBox(),
                items: [
                  DropdownMenuItem(value: FormType.festivalRegistration, child: Text(l10n.translate('festivalRegistration'))),
                  DropdownMenuItem(value: FormType.userCreation, child: Text(l10n.translate('userCreation'))),
                  DropdownMenuItem(value: FormType.internal, child: Text(l10n.translate('internalForm'))),
                ],
                onChanged: (v) { if (v != null) setDialogState(() { selectedType = v; }); },
              ),
            ]),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: Text(l10n.cancel)),
            FilledButton(
              onPressed: () {
                if (titleCtl.text.trim().isEmpty) return;
                Navigator.pop(ctx, {'title': titleCtl.text.trim(), 'description': descCtl.text.trim(), 'form_type': selectedType});
              },
              child: Text(l10n.create),
            ),
          ],
        ),
      ),
    );
    if (result == null) return;
    try {
      final form = await api.createForm(result);
      if (mounted) _openFormDetail(form);
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.errorFormatWith('$e')), behavior: SnackBarBehavior.floating));
    }
  }

  /// Abre la pantalla de detalle del formulario, recargando si se notificó
  /// algún cambio.
  Future<void> _openFormDetail(FormDefinition form) async {
    if (form.id == null) return;
    final changed = await Navigator.push<bool>(
      context,
      MaterialPageRoute(builder: (_) => FormDetailScreen(formId: form.id!)),
    );
    if (changed == true) _loadData();
  }

  /// Elimina el formulario indicado tras un diálogo de confirmación.
  Future<void> _deleteForm(FormDefinition form) async {
    if (form.id == null) return;
    final confirm = await showConfirmDialog(context, title: l10n.deleteForm, message: l10n.deleteFormMessage(form.title));
    if (confirm == true) {
      await api.deleteForm(form.id!);
      _loadData();
    }
  }

  /// Clona el formulario indicado y recarga la lista.
  Future<void> _cloneForm(FormDefinition form) async {
    if (form.id == null) return;
    try {
      final cloned = await api.cloneForm(form.id!);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text(l10n.translate('cloneFormMessage').replaceFirst('{title}', cloned.title)),
          behavior: SnackBarBehavior.floating,
        ));
        _loadData();
      }
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.errorFormatWith('$e')), behavior: SnackBarBehavior.floating));
    }
  }

  IconData _typeIcon(String type) {
    switch (type) {
      case FormType.festivalRegistration: return Icons.festival_rounded;
      case FormType.userCreation: return Icons.person_add_rounded;
      case FormType.internal: return Icons.admin_panel_settings_rounded;
      default: return Icons.assignment_outlined;
    }
  }

  @override
  Widget build(BuildContext context) {
    l10n = AppLocalizations.of(context)!;

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.formDefinitions),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 8),
            child: DropdownButtonHideUnderline(
              child: DropdownButton<String?>(
                value: _typeFilter,
                hint: Text(l10n.all, style: const TextStyle(fontSize: 14)),
                items: [
                  DropdownMenuItem(value: null, child: Text(l10n.all, style: const TextStyle(fontSize: 14))),
                  DropdownMenuItem(value: FormType.festivalRegistration, child: Text(l10n.translate('festivalRegistration'), style: const TextStyle(fontSize: 14))),
                  DropdownMenuItem(value: FormType.userCreation, child: Text(l10n.translate('userCreation'), style: const TextStyle(fontSize: 14))),
                  DropdownMenuItem(value: FormType.internal, child: Text(l10n.translate('internalForm'), style: const TextStyle(fontSize: 14))),
                ],
                onChanged: (v) { setState(() { _typeFilter = v; }); _loadData(); },
              ),
            ),
          ),
        ],
      ),
      body: _isLoading
          ? const ListSkeleton()
          : _hasError
              ? ErrorStateWidget(onRetry: _loadData)
              : RefreshIndicator(
                  onRefresh: _loadData,
                  child: _forms.isEmpty
                      ? EmptyStateWidget(icon: Icons.assignment_outlined, title: l10n.noForms, subtitle: l10n.noFormsHint)
                      : ListView.builder(
                          padding: const EdgeInsets.all(16),
                          itemCount: _forms.length,
                          itemBuilder: (ctx, i) {
                            final f = _forms[i];
                            final subtitle = '${f.pages.length} ${l10n.translate('pages')} - ${f.isActive ? l10n.active : l10n.inactive}';
                            return Card(
                              margin: const EdgeInsets.only(bottom: 12),
                              child: ListTile(
                                leading: CircleAvatar(child: Icon(_typeIcon(f.formType), color: Colors.white)),
                                title: Text(f.title, style: const TextStyle(fontWeight: FontWeight.w600)),
                                subtitle: Text(subtitle),
                                trailing: PopupMenuButton<String>(
                                  onSelected: (action) {
                                    switch (action) {
                                      case 'edit':
                                        _openFormDetail(f);
                                        break;
                                      case 'clone':
                                        _cloneForm(f);
                                        break;
                                      case 'delete':
                                        _deleteForm(f);
                                        break;
                                    }
                                  },
                                  itemBuilder: (_) => [
                                    PopupMenuItem(value: 'edit', child: ListTile(leading: const Icon(Icons.edit_outlined), title: Text(l10n.edit), dense: true)),
                                    PopupMenuItem(value: 'clone', child: ListTile(leading: const Icon(Icons.copy_outlined), title: Text(l10n.translate('cloneForm')), dense: true)),
                                    PopupMenuItem(value: 'delete', child: ListTile(leading: const Icon(Icons.delete_outlined), title: Text(l10n.delete), dense: true)),
                                  ],
                                ),
                                onTap: () => _openFormDetail(f),
                              ),
                            );
                          },
                        ),
                ),
      floatingActionButton: FloatingActionButton(onPressed: _createForm, tooltip: l10n.translate('newForm'), child: const Icon(Icons.add)),
    );
  }
}
