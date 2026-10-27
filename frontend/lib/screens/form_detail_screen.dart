import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../l10n/app_localizations.dart';
import '../services/api_service.dart';
import '../models/form_definition_model.dart';
import '../widgets/reusable_widgets.dart';
import '../widgets/empty_state_widget.dart';
import '../widgets/loading_skeleton.dart';
import '../widgets/error_state_widget.dart';
import '../widgets/confirm_dialog.dart';
import 'form_page_editor_screen.dart';
import 'form_response_detail_screen.dart';

/// Pantalla con cuatro pestañas que gestiona un único formulario: detalles,
/// páginas, enlaces y respuestas enviadas.
class FormDetailScreen extends StatefulWidget {
  final int formId;
  const FormDetailScreen({super.key, required this.formId});

  @override
  State<FormDetailScreen> createState() => _FormDetailScreenState();
}

/// Mantiene el formulario cargado y el controlador de pestañas para las
/// cuatro pestañas.
class _FormDetailScreenState extends State<FormDetailScreen> with SingleTickerProviderStateMixin {
  final ApiService api = ApiService();
  late TabController _tabController;
  late FormDefinition _form;
  bool _isLoading = true;
  bool _hasError = false;
  bool _initialized = false;
  late AppLocalizations l10n;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    l10n = AppLocalizations.of(context)!;
    if (!_initialized) {
      _initialized = true;
      _loadForm();
    }
  }

  /// Carga la definición completa del formulario para el id indicado.
  Future<void> _loadForm() async {
    if (!mounted) return;
    setState(() { _isLoading = true; _hasError = false; });
    try {
      _form = await api.getForm(widget.formId);
      if (!mounted) return;
      setState(() { _isLoading = false; });
    } catch (e) {
      debugPrint('Error: $e');
      if (!mounted) return;
      setState(() { _isLoading = false; _hasError = true; });
    }
  }

  @override
  Widget build(BuildContext context) {
    l10n = AppLocalizations.of(context)!;

    return Scaffold(
      appBar: AppBar(
        title: Text(_isLoading ? '...' : _form.title),
        bottom: TabBar(
          controller: _tabController,
          tabs: [
            Tab(text: l10n.details, icon: const Icon(Icons.settings_outlined)),
            Tab(text: l10n.pagesTab, icon: const Icon(Icons.list_alt_outlined)),
            Tab(text: l10n.linksTab, icon: const Icon(Icons.link_outlined)),
            Tab(text: l10n.responsesTab, icon: const Icon(Icons.people_outline)),
          ],
        ),
      ),
      body: _isLoading
          ? const ListSkeleton()
          : _hasError
              ? ErrorStateWidget(onRetry: _loadForm)
              : TabBarView(
                  controller: _tabController,
                  children: [
                    _DetailsTab(form: _form, onChanged: _loadForm),
                    _PagesTab(form: _form, onChanged: _loadForm),
                    _FormLinksTab(formId: widget.formId),
                    _FormResponsesTab(formId: widget.formId, formTitle: _form.title),
                  ],
                ),
    );
  }
}

/// Pestaña que edita los metadatos del formulario (título, tipo, indicadores,
/// horarios).
class _DetailsTab extends StatefulWidget {
  final FormDefinition form;
  final VoidCallback onChanged;
  const _DetailsTab({required this.form, required this.onChanged});

  @override
  State<_DetailsTab> createState() => _DetailsTabState();
}

/// Mantiene los controladores y los indicadores inicializados a partir de la
/// definición del formulario.
class _DetailsTabState extends State<_DetailsTab> {
  final ApiService api = ApiService();
  late TextEditingController _titleCtl;
  late TextEditingController _descCtl;
  late TextEditingController _maxSubCtl;
  late TextEditingController _submitBtnCtl;
  late TextEditingController _successMsgCtl;
  late TextEditingController _sortOrderCtl;
  late TextEditingController _startCtl;
  late TextEditingController _endCtl;
  late bool _isActive;
  late bool _isPublic;
  late bool _requireAuth;
  late bool _requiresApproval;
  String _formType = FormType.festivalRegistration;
  late AppLocalizations l10n;

  @override
  void initState() {
    super.initState();
    _initControllers();
  }

  void _initControllers() {
    _titleCtl = TextEditingController(text: widget.form.title);
    _descCtl = TextEditingController(text: widget.form.description ?? '');
    _isActive = widget.form.isActive;
    _isPublic = widget.form.isPublic;
    _requireAuth = widget.form.requireAuth;
    _requiresApproval = widget.form.requiresApproval;
    _formType = widget.form.formType;
    _maxSubCtl = TextEditingController(text: widget.form.maxSubmissions?.toString() ?? '');
    _submitBtnCtl = TextEditingController(text: widget.form.submitButtonText ?? '');
    _successMsgCtl = TextEditingController(text: widget.form.successMessage ?? '');
    _sortOrderCtl = TextEditingController(text: widget.form.sortOrder.toString());
    _startCtl = TextEditingController(text: widget.form.startsAt?.toIso8601String().substring(0, 16) ?? '');
    _endCtl = TextEditingController(text: widget.form.endsAt?.toIso8601String().substring(0, 16) ?? '');
  }

  @override
  void didUpdateWidget(covariant _DetailsTab oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.form.id != widget.form.id) _initControllers();
  }

  @override
  void dispose() {
    _titleCtl.dispose();
    _descCtl.dispose();
    _maxSubCtl.dispose();
    _submitBtnCtl.dispose();
    _successMsgCtl.dispose();
    _sortOrderCtl.dispose();
    _startCtl.dispose();
    _endCtl.dispose();
    super.dispose();
  }

  /// Recopila los campos editados y los persiste a través de la API.
  Future<void> _save() async {
    final fields = <String, dynamic>{
      'title': _titleCtl.text.trim(),
      'description': _descCtl.text.trim().isEmpty ? null : _descCtl.text.trim(),
      'is_active': _isActive,
      'is_public': _isPublic,
      'require_auth': _requireAuth,
      'requires_approval': _requiresApproval,
      'form_type': _formType,
      'sort_order': int.tryParse(_sortOrderCtl.text) ?? 0,
    };
    if (_maxSubCtl.text.isNotEmpty) fields['max_submissions'] = int.tryParse(_maxSubCtl.text);
    if (_submitBtnCtl.text.trim().isNotEmpty) fields['submit_button_text'] = _submitBtnCtl.text.trim();
    if (_successMsgCtl.text.trim().isNotEmpty) fields['success_message'] = _successMsgCtl.text.trim();
    if (_startCtl.text.isNotEmpty) fields['starts_at'] = '${_startCtl.text}:00';
    if (_endCtl.text.isNotEmpty) fields['ends_at'] = '${_endCtl.text}:00';
    try {
      await api.updateForm(widget.form.id!, fields);
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.saved), behavior: SnackBarBehavior.floating));
      widget.onChanged();
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.errorFor(e)), behavior: SnackBarBehavior.floating));
    }
  }

  /// Selecciona fecha y hora y escribe el valor ISO en el controlador.
  Future<void> _pickDate(TextEditingController ctl) async {
    final date = await showDatePicker(context: context, firstDate: DateTime(2020), lastDate: DateTime(2035));
    if (date == null) return;
    if (!mounted) return;
    final time = await showTimePicker(context: context, initialTime: TimeOfDay.fromDateTime(DateTime.now()));
    if (time == null) return;
    if (!mounted) return;
    ctl.text = '${date.toIso8601String().substring(0, 10)}T${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}';
  }

  @override
  Widget build(BuildContext context) {
    l10n = AppLocalizations.of(context)!;
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
        SemanticTextField(controller: _titleCtl, label: l10n.titleRequired, semanticLabel: l10n.formTitle, helperText: l10n.formTitle),
        const SizedBox(height: 12),
        SemanticTextField(controller: _descCtl, label: l10n.description, maxLines: 3, semanticLabel: l10n.description, helperText: l10n.optionalDescription),
        const SizedBox(height: 12),
        DropdownButtonFormField<String>(
          initialValue: _formType,
          decoration: InputDecoration(labelText: l10n.formType),
          items: [
            DropdownMenuItem(value: FormType.festivalRegistration, child: Text(l10n.translate('festivalRegistration'))),
            DropdownMenuItem(value: FormType.userCreation, child: Text(l10n.translate('userCreation'))),
            DropdownMenuItem(value: FormType.internal, child: Text(l10n.translate('internalForm'))),
          ],
          onChanged: (v) { if (v != null) setState(() { _formType = v; }); },
        ),
        const SizedBox(height: 16),
        SwitchListTile(title: Text(l10n.translate('isActive')), subtitle: Text(l10n.formActiveHint), value: _isActive, onChanged: (v) => setState(() { _isActive = v; })),
        SwitchListTile(title: Text(l10n.isPublic), subtitle: Text(l10n.translate('isPublicHint')), value: _isPublic, onChanged: (v) => setState(() { _isPublic = v; })),
        SwitchListTile(title: Text(l10n.requireAuth), subtitle: Text(l10n.translate('requireAuthHint')), value: _requireAuth, onChanged: (v) => setState(() { _requireAuth = v; })),
        SwitchListTile(title: Text(l10n.requiresApproval), subtitle: Text(l10n.translate('requiresApprovalHint')), value: _requiresApproval, onChanged: (v) => setState(() { _requiresApproval = v; })),
        const SizedBox(height: 12),
        TextField(controller: _maxSubCtl, decoration: InputDecoration(labelText: l10n.maxSubmissions, helperText: l10n.maxRegistrationsHint), keyboardType: TextInputType.number),
        const SizedBox(height: 12),
        TextField(controller: _submitBtnCtl, decoration: InputDecoration(labelText: l10n.submitButtonText, helperText: l10n.translate('submitButtonTextHint'))),
        const SizedBox(height: 12),
        TextField(controller: _successMsgCtl, decoration: InputDecoration(labelText: l10n.successMessage, helperText: l10n.translate('successMessageHint'))),
        const SizedBox(height: 12),
        TextField(controller: _sortOrderCtl, decoration: InputDecoration(labelText: l10n.sortOrder), keyboardType: TextInputType.number),
        const SizedBox(height: 12),
        TextField(controller: _startCtl, decoration: InputDecoration(labelText: l10n.startsAt, suffixIcon: IconButton(icon: const Icon(Icons.date_range), onPressed: () => _pickDate(_startCtl))), readOnly: true),
        const SizedBox(height: 12),
        TextField(controller: _endCtl, decoration: InputDecoration(labelText: l10n.endsAt, suffixIcon: IconButton(icon: const Icon(Icons.date_range), onPressed: () => _pickDate(_endCtl))), readOnly: true),
        const SizedBox(height: 20),
        FilledButton.icon(onPressed: _save, icon: const Icon(Icons.save), label: Text(l10n.saveChanges)),
      ]),
    );
  }
}

/// Pestaña que lista las páginas del formulario, abriendo cada una en el
/// editor de páginas.
class _PagesTab extends StatelessWidget {
  final FormDefinition form;
  final VoidCallback onChanged;
  const _PagesTab({required this.form, required this.onChanged});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final pages = form.pages;

    if (pages.isEmpty) {
      return EmptyStateWidget(icon: Icons.list_alt_outlined, title: l10n.translate('noPages'), subtitle: l10n.translate('noPagesHint'));
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: pages.length,
      itemBuilder: (ctx, i) {
        final p = pages[i];
        return Card(
          margin: const EdgeInsets.only(bottom: 8),
          child: ListTile(
            leading: CircleAvatar(child: Text('${p.sortOrder}', style: const TextStyle(color: Colors.white))),
            title: Text(p.title, style: const TextStyle(fontWeight: FontWeight.w600)),
            subtitle: Text(l10n.fieldsCount(p.fields.length)),
            trailing: Row(mainAxisSize: MainAxisSize.min, children: [
              IconButton(
                icon: const Icon(Icons.edit_outlined),
                tooltip: l10n.edit,
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => FormPageEditorScreen(form: form, page: p),
                    ),
                  ).then((changed) { if (changed == true) onChanged(); });
                },
              ),
            ]),
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => FormPageEditorScreen(form: form, page: p),
                ),
              ).then((changed) { if (changed == true) onChanged(); });
            },
          ),
        );
      },
    );
  }
}

/// Pestaña que gestiona los enlaces compartibles del formulario (crear,
/// eliminar, regenerar).
class _FormLinksTab extends StatefulWidget {
  final int formId;
  const _FormLinksTab({required this.formId});

  @override
  State<_FormLinksTab> createState() => _FormLinksTabState();
}

/// Mantiene los enlaces del formulario cargados; se cargan en el primer build.
class _FormLinksTabState extends State<_FormLinksTab> {
  final ApiService api = ApiService();
  List<FormLink> _links = [];
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
      _loadLinks();
    }
  }

  /// Obtiene los enlaces compartibles del formulario de la API.
  Future<void> _loadLinks() async {
    if (!mounted) return;
    setState(() { _isLoading = true; _hasError = false; });
    try {
      _links = await api.getFormLinks(widget.formId, size: 100);
      if (!mounted) return;
      setState(() { _isLoading = false; });
    } catch (e) {
      debugPrint('Error: $e');
      if (!mounted) return;
      setState(() { _isLoading = false; _hasError = true; });
    }
  }

  /// Muestra un diálogo para configurar y crear un nuevo enlace de formulario.
  Future<void> _createLink() async {
    final isUnique = ValueNotifier(false);
    final isPublic = ValueNotifier(true);
    final maxUsesCtl = TextEditingController();
    final assignedUserCtl = TextEditingController();

    final result = await showDialog<Map<String, dynamic>>(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setDialogState) => AlertDialog(
          title: Text(l10n.createLink),
          content: Column(mainAxisSize: MainAxisSize.min, children: [
            SwitchListTile(title: Text(l10n.linkPublic), value: isPublic.value, onChanged: (v) { isPublic.value = v; setDialogState(() {}); }),
            SwitchListTile(title: Text(l10n.linkUnique), value: isUnique.value, onChanged: (v) { isUnique.value = v; setDialogState(() {}); }),
            TextField(controller: maxUsesCtl, decoration: InputDecoration(labelText: l10n.maxUses), keyboardType: TextInputType.number),
            TextField(controller: assignedUserCtl, decoration: InputDecoration(labelText: l10n.assignedUser), keyboardType: TextInputType.number),
          ]),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: Text(l10n.cancel)),
            FilledButton(
              onPressed: () {
                final data = <String, dynamic>{
                  'is_unique': isUnique.value,
                  'is_public': isPublic.value,
                };
                if (maxUsesCtl.text.isNotEmpty) data['max_uses'] = int.tryParse(maxUsesCtl.text);
                if (assignedUserCtl.text.isNotEmpty) data['assigned_user_id'] = int.tryParse(assignedUserCtl.text);
                Navigator.pop(ctx, data);
              },
              child: Text(l10n.create),
            ),
          ],
        ),
      ),
    );
    isUnique.dispose();
    isPublic.dispose();
    maxUsesCtl.dispose();
    assignedUserCtl.dispose();
    if (result == null) return;
    try {
      await api.createFormLink(widget.formId, result);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.linkCreated), behavior: SnackBarBehavior.floating));
        _loadLinks();
      }
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.errorFor(e)), behavior: SnackBarBehavior.floating));
    }
  }

  /// Elimina el enlace de formulario indicado tras un diálogo de confirmación.
  Future<void> _deleteLink(FormLink link) async {
    if (link.id == null) return;
    final confirm = await showConfirmDialog(context, title: l10n.deleteLink, message: l10n.deleteLinkMessage);
    if (confirm == true) {
      await api.deleteFormLink(widget.formId, link.id!);
      _loadLinks();
    }
  }

  /// Regenera el token del formulario, invalidando los enlaces existentes.
  Future<void> _regenerateLink(FormLink link) async {
    if (link.id == null) return;
    try {
      await api.updateForm(widget.formId, {'_regenerate_token': true});
      _loadLinks();
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.tokenRegenerated), behavior: SnackBarBehavior.floating));
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.errorFor(e)), behavior: SnackBarBehavior.floating));
    }
  }

  @override
  Widget build(BuildContext context) {
    l10n = AppLocalizations.of(context)!;

    if (_isLoading) return const ListSkeleton();
    if (_hasError) return ErrorStateWidget(onRetry: _loadLinks);

    return Column(children: [
      Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: Row(children: [
          Expanded(child: Text('${_links.length} ${l10n.translate('links')}', style: TextStyle(color: Theme.of(context).colorScheme.onSurfaceVariant))),
          FilledButton.tonalIcon(onPressed: _createLink, icon: const Icon(Icons.add), label: Text(l10n.createLink)),
        ]),
      ),
      Expanded(
        child: _links.isEmpty
            ? EmptyStateWidget(icon: Icons.link_off, title: l10n.noLinksYet, subtitle: l10n.noLinksYetHint)
            : ListView.builder(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                itemCount: _links.length,
                itemBuilder: (ctx, i) {
                  final l = _links[i];
                  return Card(
                    margin: const EdgeInsets.only(bottom: 8),
                    child: ListTile(
                      leading: CircleAvatar(child: Icon(l.isActive ? Icons.link : Icons.link_off, color: Colors.white)),
                      title: Text(l.token, style: const TextStyle(fontWeight: FontWeight.w600, fontFamily: 'monospace')),
                      subtitle: Text('${l.useCount} ${l10n.translate('uses')} - ${l.isUnique ? l10n.unique : l10n.shared}'),
                      trailing: Row(mainAxisSize: MainAxisSize.min, children: [
                        IconButton(icon: const Icon(Icons.refresh), tooltip: l10n.regenerateToken, onPressed: () => _regenerateLink(l)),
                        IconButton(icon: const Icon(Icons.delete_outline), tooltip: l10n.delete, onPressed: () => _deleteLink(l)),
                      ]),
                    ),
                  );
                },
              ),
      ),
    ]);
  }
}

/// Pestaña que lista las respuestas enviadas del formulario con filtros de
/// estado y exportación.
class _FormResponsesTab extends StatefulWidget {
  final int formId;
  final String formTitle;
  const _FormResponsesTab({required this.formId, required this.formTitle});

  @override
  State<_FormResponsesTab> createState() => _FormResponsesTabState();
}

/// Mantiene las respuestas cargadas y el filtro de estado activo.
class _FormResponsesTabState extends State<_FormResponsesTab> {
  final ApiService api = ApiService();
  List<FormResponse> _responses = [];
  String _statusFilter = '';
  bool _isLoading = true;
  bool _hasError = false;
  bool _isExporting = false;
  bool _initialized = false;
  late AppLocalizations l10n;

  /// Obtiene la URL de exportación CSV y la abre en el navegador externo.
  Future<void> _exportCsv() async {
    setState(() { _isExporting = true; });
    try {
      final url = await api.getFormResponsesCsvUrl(widget.formId);
      await launchUrl(Uri.parse(url), mode: LaunchMode.externalApplication);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text(l10n.errorFor(e)),
          behavior: SnackBarBehavior.floating,
        ));
      }
    } finally {
      if (mounted) setState(() { _isExporting = false; });
    }
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    l10n = AppLocalizations.of(context)!;
    if (!_initialized) {
      _initialized = true;
      _loadData();
    }
  }

  /// Carga las respuestas, opcionalmente filtradas por estado de envío.
  Future<void> _loadData() async {
    if (!mounted) return;
    setState(() { _isLoading = true; _hasError = false; });
    try {
      final result = await api.getFormResponses(widget.formId, size: 100, status: _statusFilter.isEmpty ? null : _statusFilter);
      if (!mounted) return;
      setState(() { _responses = result.items; _isLoading = false; });
    } catch (e) {
      debugPrint('Error: $e');
      if (!mounted) return;
      setState(() { _isLoading = false; _hasError = true; });
    }
  }

  /// Aprueba, rechaza (con motivo opcional) o restablece el estado de una
  /// respuesta.
  Future<void> _updateStatus(FormResponse r, String newStatus) async {
    if (r.id == null) return;
    try {
      if (newStatus == 'approved') {
        await api.approveResponse(r.id!);
      } else if (newStatus == 'rejected') {
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
        await api.rejectResponse(r.id!, reason: reason);
      } else {
        await api.updateFormResponse(r.id!, {'status': newStatus});
      }
      _loadData();
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.errorFor(e)), behavior: SnackBarBehavior.floating));
    }
  }

  @override
  Widget build(BuildContext context) {
    l10n = AppLocalizations.of(context)!;
    return Column(children: [
      Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: Row(children: [
          Expanded(
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(children: [
                FilterChip(label: Text(l10n.all), selected: _statusFilter.isEmpty, onSelected: (_) { setState(() { _statusFilter = ''; }); _loadData(); }),
                const SizedBox(width: 8),
                FilterChip(label: Text(l10n.pending), selected: _statusFilter == 'submitted', onSelected: (_) { setState(() { _statusFilter = 'submitted'; }); _loadData(); }),
                const SizedBox(width: 8),
                FilterChip(label: Text(l10n.approved), selected: _statusFilter == 'approved', onSelected: (_) { setState(() { _statusFilter = 'approved'; }); _loadData(); }),
                const SizedBox(width: 8),
                FilterChip(label: Text(l10n.rejected), selected: _statusFilter == 'rejected', onSelected: (_) { setState(() { _statusFilter = 'rejected'; }); _loadData(); }),
                const SizedBox(width: 8),
                FilterChip(label: Text(l10n.translate('draft')), selected: _statusFilter == 'draft', onSelected: (_) { setState(() { _statusFilter = 'draft'; }); _loadData(); }),
              ]),
            ),
          ),
          IconButton(
            icon: _isExporting
                ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2))
                : const Icon(Icons.download),
            tooltip: l10n.translate('exportCsv'),
            onPressed: _isExporting ? null : _exportCsv,
          ),
        ]),
      ),
      Expanded(
        child: _isLoading
            ? const ListSkeleton()
            : _hasError
                ? ErrorStateWidget(onRetry: _loadData)
                : _responses.isEmpty
                    ? EmptyStateWidget(icon: Icons.person_off, title: l10n.noResponses, subtitle: l10n.noResponsesHint)
                    : ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: _responses.length,
                        itemBuilder: (ctx, i) {
                          final r = _responses[i];
                          final color = r.status == 'approved' ? Colors.green : r.status == 'rejected' ? Colors.red : null;
                          return Card(
                            margin: const EdgeInsets.only(bottom: 8),
                            child: ListTile(
                              leading: CircleAvatar(
                                child: Text('#${r.id}', style: const TextStyle(color: Colors.white, fontSize: 12)),
                              ),
                              title: Text('${l10n.translate('response')} #${r.id}', style: const TextStyle(fontWeight: FontWeight.w600)),
                              subtitle: Text(r.status, style: TextStyle(color: color)),
                              trailing: PopupMenuButton<String>(
                                onSelected: (s) => _updateStatus(r, s),
                                itemBuilder: (_) => [
                                  PopupMenuItem(value: 'approved', child: Text(l10n.approve)),
                                  PopupMenuItem(value: 'rejected', child: Text(l10n.reject)),
                                  PopupMenuItem(value: 'submitted', child: Text(l10n.pending)),
                                ],
                              ),
                              onTap: () {
                                Navigator.push(
                                  context,
                                  MaterialPageRoute(
                                    builder: (_) => FormResponseDetailScreen(response: r),
                                  ),
                                );
                              },
                            ),
                          );
                        },
                      ),
      ),
    ]);
  }
}
