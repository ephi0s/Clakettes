import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../services/api_service.dart';
import '../services/file_downloader.dart';
import '../models/registration_form_model.dart';
import '../widgets/reusable_widgets.dart';
import '../widgets/empty_state_widget.dart';
import '../widgets/loading_skeleton.dart';
import '../widgets/error_state_widget.dart';
import '../widgets/confirm_dialog.dart';

/// Formatea [fee] sin decimales innecesarios (25.0 -> "25", 25.5 -> "25.5").
String _formatFee(double? fee) {
  if (fee == null) return '';
  if (fee == fee.roundToDouble()) return fee.round().toString();
  return fee.toString();
}

/// Lista los formularios de inscripción de un festival y permite crearlos,
/// editarlos y eliminarlos.
class RegistrationFormsScreen extends StatefulWidget {
  final int festivalId;
  final String festivalName;
  const RegistrationFormsScreen({super.key, required this.festivalId, required this.festivalName});

  @override
  State<RegistrationFormsScreen> createState() => _RegistrationFormsScreenState();
}

/// Estado de [RegistrationFormsScreen]. Carga los formularios del festival en
/// el primer build y se refresca tras crear, editar o eliminar.
class _RegistrationFormsScreenState extends State<RegistrationFormsScreen> {
  final ApiService api = ApiService();
  List<RegistrationForm> _forms = [];
  bool _isLoading = true;
  bool _hasError = false;
  bool _isExporting = false;
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

  /// Obtiene los formularios de inscripción del festival de la API.
  Future<void> _loadData() async {
    if (!mounted) return;
    setState(() { _isLoading = true; _hasError = false; });
    try {
      final result = await api.getRegistrationForms(widget.festivalId, size: 100);
      if (!mounted) return;
      setState(() { _forms = result.items; _isLoading = false; });
    } catch (e) {
      debugPrint('Error: $e');
      if (!mounted) return;
      setState(() { _isLoading = false; _hasError = true; });
    }
  }

  /// Muestra un diálogo para título/descripción y crea el formulario al confirmar.
  Future<void> _createForm() async {
    final titleCtl = TextEditingController();
    final descCtl = TextEditingController();
    final result = await showDialog<Map<String, String>>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(l10n.newRegistrationForm),
        content: SingleChildScrollView(
          child: Column(mainAxisSize: MainAxisSize.min, children: [
            SemanticTextField(controller: titleCtl, label: l10n.titleRequired, semanticLabel: l10n.formTitle, helperText: l10n.formTitle),
            const SizedBox(height: 12),
            SemanticTextField(controller: descCtl, label: l10n.description, semanticLabel: l10n.description, helperText: l10n.optionalDescription),
          ]),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: Text(l10n.cancel)),
          FilledButton(
            onPressed: () {
              if (titleCtl.text.trim().isEmpty) return;
              Navigator.pop(ctx, {'title': titleCtl.text.trim(), 'description': descCtl.text.trim()});
            },
            child: Text(l10n.create),
          ),
        ],
      ),
    );
    if (result == null) return;
    try {
      final form = await api.createRegistrationForm(
        widget.festivalId,
        RegistrationForm(festivalId: widget.festivalId, title: result['title']!, description: result['description']),
      );
      if (mounted) _openFormDetail(form);
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.errorFormatWith('$e')), behavior: SnackBarBehavior.floating));
    }
  }

  /// Abre el editor de detalle del formulario y recarga la lista si cambió.
  Future<void> _openFormDetail(RegistrationForm form) async {
    if (form.id == null) return;
    final changed = await Navigator.push<bool>(
      context,
      MaterialPageRoute(builder: (_) => FormDetailScreen(formId: form.id!, festivalName: widget.festivalName)),
    );
    if (changed == true) _loadData();
  }

  /// Pide confirmación y elimina el formulario indicado.
  Future<void> _deleteForm(RegistrationForm form) async {
    if (form.id == null) return;
    final confirm = await showConfirmDialog(context, title: l10n.deleteForm, message: l10n.deleteFormMessage(form.title));
    if (confirm == true) {
      await api.deleteRegistrationForm(form.id!);
      _loadData();
    }
  }

  /// Descarga las inscripciones del festival en [format] (`csv` o `pdf`).
  Future<void> _exportRegistrations(String format) async {
    if (_isExporting) return;
    setState(() { _isExporting = true; });
    try {
      final bytes = await api.getBytes('/festivals/${widget.festivalId}/registrations/export/$format');
      await downloadFile(bytes, format == 'csv' ? 'registrations.csv' : 'registrations.pdf');
      if (!mounted) return;
      setState(() { _isExporting = false; });
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.exportSuccess), behavior: SnackBarBehavior.floating));
    } catch (e) {
      debugPrint('Error: $e');
      if (!mounted) return;
      setState(() { _isExporting = false; });
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.errorFormatWith('$e')), behavior: SnackBarBehavior.floating));
    }
  }

  @override
  Widget build(BuildContext context) {
    l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Text('${l10n.festivals} — ${widget.festivalName}'),
        actions: [
          IconButton(
            icon: const Icon(Icons.table_chart_outlined),
            tooltip: l10n.exportCsv,
            onPressed: _isExporting ? null : () => _exportRegistrations('csv'),
          ),
          IconButton(
            icon: const Icon(Icons.picture_as_pdf_outlined),
            tooltip: l10n.exportPdf,
            onPressed: _isExporting ? null : () => _exportRegistrations('pdf'),
          ),
        ],
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(24),
          child: Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Text(l10n.registrationFormCount(_forms.length), style: TextStyle(color: theme.colorScheme.onSurfaceVariant)),
          ),
        ),
      ),
      body: _isLoading
          ? const ListSkeleton()
          : _hasError
              ? ErrorStateWidget(onRetry: _loadData)
              : RefreshIndicator(
                  onRefresh: _loadData,
                  child: _forms.isEmpty
                      ? EmptyStateWidget(icon: Icons.assignment_outlined, title: l10n.noRegistrationForms, subtitle: l10n.createOneToStart)
                      : ListView.builder(
                          padding: const EdgeInsets.all(16),
                          itemCount: _forms.length,
                          itemBuilder: (ctx, i) {
                            final f = _forms[i];
                            return Card(
                              margin: const EdgeInsets.only(bottom: 12),
                              child: ListTile(
                                leading: CircleAvatar(
                                  child: Icon(
                                    f.isActive ? Icons.check_circle_outline : Icons.block,
                                    color: Colors.white,
                                  ),
                                ),
                                title: Text(f.title, style: const TextStyle(fontWeight: FontWeight.w600)),
                                subtitle: Text(
                                  '${f.sections.length} ${l10n.sectionCount(f.sections.length)} • ${f.isActive ? l10n.active : l10n.inactive}',
                                ),
                                trailing: Row(mainAxisSize: MainAxisSize.min, children: [
                                  IconButton(
                                    icon: const Icon(Icons.edit_outlined),
                                    tooltip: l10n.editForm,
                                    onPressed: () => _openFormDetail(f),
                                  ),
                                  IconButton(
                                    icon: const Icon(Icons.delete_outline),
                                    tooltip: l10n.delete,
                                    onPressed: () => _deleteForm(f),
                                  ),
                                ]),
                                onTap: () => _openFormDetail(f),
                              ),
                            );
                          },
                        ),
                ),
      floatingActionButton: FloatingActionButton(onPressed: _createForm, tooltip: l10n.createForm, child: const Icon(Icons.add)),
    );
  }
}


/// Editor de detalle de un formulario de inscripción con pestañas para
/// detalles, secciones, enlaces e inscripciones.
class FormDetailScreen extends StatefulWidget {
  final int formId;
  final String festivalName;
  const FormDetailScreen({super.key, required this.formId, required this.festivalName});

  @override
  State<FormDetailScreen> createState() => _FormDetailScreenState();
}

/// Estado de [FormDetailScreen]. Carga el formulario en el primer build y
/// controla el TabController usado por las cuatro pestañas.
class _FormDetailScreenState extends State<FormDetailScreen> with SingleTickerProviderStateMixin {
  final ApiService api = ApiService();
  late TabController _tabController;
  late RegistrationForm _form;
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

  /// Obtiene la definición completa del formulario de inscripción de la API.
  Future<void> _loadForm() async {
    if (!mounted) return;
    setState(() { _isLoading = true; _hasError = false; });
    try {
      _form = await api.getRegistrationForm(widget.formId);
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
            Tab(text: l10n.sectionsTab, icon: const Icon(Icons.list_alt_outlined)),
            Tab(text: l10n.linksTab, icon: const Icon(Icons.link_outlined)),
            Tab(text: l10n.registrationsTab, icon: const Icon(Icons.people_outline)),
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
                    _SectionsTab(form: _form, onChanged: _loadForm),
                    _LinksTab(formId: widget.formId),
                    _RegistrationsTab(formId: widget.formId, formTitle: _form.title),
                  ],
                ),
    );
  }
}


/// Pestaña para editar los metadatos del formulario: título, descripción,
/// opciones y rango de fechas.
class _DetailsTab extends StatefulWidget {
  final RegistrationForm form;
  final VoidCallback onChanged;
  const _DetailsTab({required this.form, required this.onChanged});

  @override
  State<_DetailsTab> createState() => _DetailsTabState();
}

/// Estado de [_DetailsTab]. Mantiene los controladores e interruptores de
/// edición, inicializados a partir del formulario recibido.
class _DetailsTabState extends State<_DetailsTab> {
  final ApiService api = ApiService();
  late TextEditingController _titleCtl;
  late TextEditingController _descCtl;
  late bool _isActive;
  late bool _requireExisting;
  late bool _allowRoles;
  late bool _allowTags;
  late TextEditingController _maxRegCtl;
  late TextEditingController _startCtl;
  late TextEditingController _endCtl;
  late TextEditingController _feeCtl;
  late String _currency;
  late AppLocalizations l10n;

  @override
  void initState() {
    super.initState();
    _initControllers();
  }

  /// Inicializa los controladores y valores desde el formulario recibido.
  void _initControllers() {
    _titleCtl = TextEditingController(text: widget.form.title);
    _descCtl = TextEditingController(text: widget.form.description ?? '');
    _isActive = widget.form.isActive;
    _requireExisting = widget.form.requireExistingAccount;
    _allowRoles = widget.form.allowRoleSelection;
    _allowTags = widget.form.allowTagSelection;
    _maxRegCtl = TextEditingController(text: widget.form.maxRegistrations?.toString() ?? '');
    _startCtl = TextEditingController(text: widget.form.startsAt?.toIso8601String().substring(0, 16) ?? '');
    _endCtl = TextEditingController(text: widget.form.endsAt?.toIso8601String().substring(0, 16) ?? '');
    _feeCtl = TextEditingController(text: _formatFee(widget.form.feeAmount));
    _currency = widget.form.currency.isEmpty ? 'EUR' : widget.form.currency;
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
    _maxRegCtl.dispose();
    _startCtl.dispose();
    _endCtl.dispose();
    _feeCtl.dispose();
    super.dispose();
  }

  /// Persiste los metadatos editados mediante la API y notifica al padre.
  Future<void> _save() async {
    final feeText = _feeCtl.text.trim().replaceAll(',', '.');
    final fee = double.tryParse(feeText);
    final fields = <String, dynamic>{
      'title': _titleCtl.text.trim(),
      'description': _descCtl.text.trim().isEmpty ? null : _descCtl.text.trim(),
      'is_active': _isActive,
      'require_existing_account': _requireExisting,
      'allow_role_selection': _allowRoles,
      'allow_tag_selection': _allowTags,
      'max_registrations': int.tryParse(_maxRegCtl.text),
      'fee_amount': fee,
      'currency': _currency,
    };
    if (_startCtl.text.isNotEmpty) fields['starts_at'] = '${_startCtl.text}:00';
    if (_endCtl.text.isNotEmpty) fields['ends_at'] = '${_endCtl.text}:00';
    try {
      await api.updateRegistrationForm(widget.form.id!, fields);
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.saved), behavior: SnackBarBehavior.floating));
      widget.onChanged();
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.errorFormatWith('$e')), behavior: SnackBarBehavior.floating));
    }
  }

  /// Selecciona fecha y hora y escribe el valor combinado en el controlador.
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
        const SizedBox(height: 16),
        SwitchListTile(title: Text(l10n.formActive), subtitle: Text(l10n.formActiveHint), value: _isActive, onChanged: (v) => setState(() { _isActive = v; })),
        SwitchListTile(title: Text(l10n.requireExisting), subtitle: Text(l10n.requireExistingHint), value: _requireExisting, onChanged: (v) => setState(() { _requireExisting = v; })),
        SwitchListTile(title: Text(l10n.allowRoleSelect), subtitle: Text(l10n.allowRoleSelectHint), value: _allowRoles, onChanged: (v) => setState(() { _allowRoles = v; })),
        SwitchListTile(title: Text(l10n.allowTagSelect), subtitle: Text(l10n.allowTagSelectHint), value: _allowTags, onChanged: (v) => setState(() { _allowTags = v; })),
        const SizedBox(height: 12),
        TextField(controller: _maxRegCtl, decoration: InputDecoration(labelText: l10n.maxRegistrations, helperText: l10n.maxRegistrationsHint), keyboardType: TextInputType.number),
        const SizedBox(height: 12),
        TextField(controller: _feeCtl, decoration: InputDecoration(labelText: l10n.registrationFee, helperText: l10n.registrationFeeHint), keyboardType: const TextInputType.numberWithOptions(decimal: true)),
        const SizedBox(height: 12),
        DropdownButtonFormField<String>(
          initialValue: _currency,
          decoration: InputDecoration(labelText: l10n.currency),
          items: ['EUR', 'USD', 'GBP']
              .map((c) => DropdownMenuItem(value: c, child: Text(c)))
              .toList(),
          onChanged: (v) { if (v != null) setState(() { _currency = v; }); },
        ),
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


/// Pestaña que lista las secciones del formulario con sus restricciones de rol y etiqueta.
class _SectionsTab extends StatelessWidget {
  final RegistrationForm form;
  final VoidCallback onChanged;
  const _SectionsTab({required this.form, required this.onChanged});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final sections = form.sections;

    if (sections.isEmpty) {
      return EmptyStateWidget(icon: Icons.list_alt_outlined, title: l10n.noSections, subtitle: l10n.noSectionsHint);
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: sections.length,
      itemBuilder: (ctx, i) {
        final s = sections[i];
        return Card(
          margin: const EdgeInsets.only(bottom: 8),
          child: ListTile(
            leading: CircleAvatar(child: Text('${s.sortOrder}', style: const TextStyle(color: Colors.white))),
            title: Text(s.title, style: const TextStyle(fontWeight: FontWeight.w600)),
            subtitle: Text(
              '${l10n.rolesCount(s.roleIds.length)} • ${l10n.tagsCount(s.tagIds.length)} • ${s.isRequired ? l10n.requiredLabel : l10n.optional}',
            ),
            trailing: Text(s.allowMultipleRoles ? l10n.multipleRoles : l10n.singleRole),
          ),
        );
      },
    );
  }
}


/// Pestaña que gestiona los enlaces de inscripción (tokens) del formulario.
class _LinksTab extends StatefulWidget {
  final int formId;
  const _LinksTab({required this.formId});

  @override
  State<_LinksTab> createState() => _LinksTabState();
}

/// Estado de [_LinksTab]. Carga los enlaces del formulario en el primer build.
class _LinksTabState extends State<_LinksTab> {
  final ApiService api = ApiService();
  List<RegistrationFormLink> _links = [];
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

  /// Obtiene los enlaces de inscripción del formulario de la API.
  Future<void> _loadLinks() async {
    if (!mounted) return;
    setState(() { _isLoading = true; _hasError = false; });
    try {
      final result = await api.getRegistrationFormLinks(widget.formId, size: 100);
      if (!mounted) return;
      setState(() { _links = result.items; _isLoading = false; });
    } catch (e) {
      debugPrint('Error: $e');
      if (!mounted) return;
      setState(() { _isLoading = false; _hasError = true; });
    }
  }

  /// Crea un nuevo enlace (token) para el formulario.
  Future<void> _createLink() async {
    try {
      await api.createRegistrationFormLink(
        widget.formId,
        RegistrationFormLink(formId: widget.formId, token: ''),
      );
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.linkCreated), behavior: SnackBarBehavior.floating));
        _loadLinks();
      }
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.errorFormatWith('$e')), behavior: SnackBarBehavior.floating));
    }
  }

  /// Pide confirmación y elimina el enlace indicado.
  Future<void> _deleteLink(RegistrationFormLink link) async {
    if (link.id == null) return;
    final confirm = await showConfirmDialog(context, title: l10n.deleteLink, message: l10n.deleteLinkMessage);
    if (confirm == true) {
      await api.deleteRegistrationFormLink(link.id!);
      _loadLinks();
    }
  }

  /// Genera un nuevo token para el enlace indicado.
  Future<void> _regenerateToken(RegistrationFormLink link) async {
    if (link.id == null) return;
    try {
      await api.regenerateFormLinkToken(link.id!);
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.tokenRegenerated), behavior: SnackBarBehavior.floating));
      _loadLinks();
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.errorFormatWith('$e')), behavior: SnackBarBehavior.floating));
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
          Expanded(child: Text('${_links.length} ${l10n.linksTab}', style: TextStyle(color: Theme.of(context).colorScheme.onSurfaceVariant))),
          FilledButton.tonalIcon(onPressed: _createLink, icon: const Icon(Icons.add), label: Text(l10n.createLink)),
        ]),
      ),
      Expanded(
        child: _links.isEmpty
            ? EmptyStateWidget(icon: Icons.link_off, title: l10n.noLinks, subtitle: l10n.noLinksHint)
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
                      subtitle: Text('${l.useCount} ${l10n.uses} • ${l.isUnique ? l10n.unique : l10n.shared}'),
                      trailing: Row(mainAxisSize: MainAxisSize.min, children: [
                        IconButton(icon: const Icon(Icons.refresh), tooltip: l10n.regenerateToken, onPressed: () => _regenerateToken(l)),
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


/// Pestaña que lista las inscripciones con filtro y actualización de estado.
class _RegistrationsTab extends StatefulWidget {
  final int formId;
  final String formTitle;
  const _RegistrationsTab({required this.formId, required this.formTitle});

  @override
  State<_RegistrationsTab> createState() => _RegistrationsTabState();
}

/// Estado de [_RegistrationsTab]. Carga las inscripciones filtradas por estado.
class _RegistrationsTabState extends State<_RegistrationsTab> {
  final ApiService api = ApiService();
  List<FestivalRegistration> _registrations = [];
  String _statusFilter = '';
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

  /// Obtiene las inscripciones del formulario, opcionalmente filtradas por estado.
  Future<void> _loadData() async {
    if (!mounted) return;
    setState(() { _isLoading = true; _hasError = false; });
    try {
      final result = await api.getFestivalRegistrations(
        widget.formId, size: 100,
        status: _statusFilter.isEmpty ? null : _statusFilter,
      );
      if (!mounted) return;
      setState(() { _registrations = result.items; _isLoading = false; });
    } catch (e) {
      debugPrint('Error: $e');
      if (!mounted) return;
      setState(() { _isLoading = false; _hasError = true; });
    }
  }

  /// Devuelve la traducción legible para el estado de pago [status].
  String _paymentLabel(String? status) {
    switch (status) {
      case 'paid':
        return l10n.paymentPaid;
      case 'pending':
        return l10n.paymentPending;
      case 'refunded':
        return l10n.paymentRefunded;
      case 'unpaid':
        return l10n.paymentUnpaid;
      default:
        return status ?? l10n.paymentStatus;
    }
  }

  /// Devuelve el color representativo del estado de pago [status].
  Color _paymentColor(String? status) {
    switch (status) {
      case 'paid':
        return Colors.green;
      case 'pending':
        return Colors.orange;
      case 'refunded':
        return Colors.blueGrey;
      case 'unpaid':
      case 'cancelled':
        return Colors.red;
      default:
        return Theme.of(context).colorScheme.onSurfaceVariant;
    }
  }

  /// Devuelve el icono representativo del estado de pago [status].
  IconData _paymentIcon(String? status) {
    switch (status) {
      case 'paid':
        return Icons.paid_outlined;
      case 'pending':
        return Icons.hourglass_top;
      case 'refunded':
        return Icons.replay;
      case 'unpaid':
        return Icons.money_off;
      case 'cancelled':
        return Icons.cancel_outlined;
      default:
        return Icons.credit_card_off;
    }
  }

  /// Actualiza el estado de una inscripción y recarga la lista filtrada.
  Future<void> _updateStatus(FestivalRegistration reg, String newStatus) async {
    if (reg.id == null) return;
    try {
      await api.updateFestivalRegistration(reg.id!, {'status': newStatus});
      _loadData();
    } catch (e) {
      if (mounted) {
        final message = e.toString().contains('409') ? l10n.paymentRequiredForApproval : l10n.errorFormatWith('$e');
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message), behavior: SnackBarBehavior.floating));
      }
    }
  }

  /// Pide método/ID de transacción y marca la inscripción como pagada.
  Future<void> _markPaid(FestivalRegistration reg) async {
    if (reg.id == null) return;
    final methodCtl = TextEditingController(text: reg.paymentMethod ?? '');
    final txCtl = TextEditingController(text: reg.transactionId ?? '');
    final result = await showDialog<Map<String, String>>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(l10n.markPaid),
        content: SingleChildScrollView(
          child: Column(mainAxisSize: MainAxisSize.min, children: [
            Text(l10n.confirmMarkPaid),
            const SizedBox(height: 12),
            SemanticTextField(controller: methodCtl, label: l10n.paymentMethod, semanticLabel: l10n.paymentMethod, helperText: l10n.optional),
            const SizedBox(height: 12),
            SemanticTextField(controller: txCtl, label: l10n.transactionId, semanticLabel: l10n.transactionId, helperText: l10n.optional),
          ]),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: Text(l10n.cancel)),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, {'method': methodCtl.text.trim(), 'transaction_id': txCtl.text.trim()}),
            child: Text(l10n.confirm),
          ),
        ],
      ),
    );
    if (result == null) return;
    try {
      await api.markRegistrationPaid(
        reg.id!,
        method: result['method']!.isEmpty ? null : result['method'],
        transactionId: result['transaction_id']!.isEmpty ? null : result['transaction_id'],
      );
      _loadData();
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.errorFormatWith('$e')), behavior: SnackBarBehavior.floating));
    }
  }

  /// Pide confirmación y marca la inscripción como reembolsada.
  Future<void> _markRefunded(FestivalRegistration reg) async {
    if (reg.id == null) return;
    final confirm = await showConfirmDialog(context, title: l10n.markRefunded, message: l10n.markRefunded);
    if (confirm != true) return;
    try {
      await api.markRegistrationRefunded(reg.id!);
      _loadData();
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.errorFormatWith('$e')), behavior: SnackBarBehavior.floating));
    }
  }

  /// Enruta las acciones del menú contextual de cada inscripción.
  Future<void> _onMenuAction(FestivalRegistration reg, String action) async {
    if (action == '__mark_paid') {
      await _markPaid(reg);
    } else if (action == '__mark_refunded') {
      await _markRefunded(reg);
    } else {
      await _updateStatus(reg, action);
    }
  }

  @override
  Widget build(BuildContext context) {
    l10n = AppLocalizations.of(context)!;
    return Column(children: [
      Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(children: [
            FilterChip(label: Text(l10n.all), selected: _statusFilter.isEmpty, onSelected: (_) { setState(() { _statusFilter = ''; }); _loadData(); }),
            const SizedBox(width: 8),
            FilterChip(label: Text(l10n.pending), selected: _statusFilter == 'pending', onSelected: (_) { setState(() { _statusFilter = 'pending'; }); _loadData(); }),
            const SizedBox(width: 8),
            FilterChip(label: Text(l10n.approved), selected: _statusFilter == 'approved', onSelected: (_) { setState(() { _statusFilter = 'approved'; }); _loadData(); }),
            const SizedBox(width: 8),
            FilterChip(label: Text(l10n.rejected), selected: _statusFilter == 'rejected', onSelected: (_) { setState(() { _statusFilter = 'rejected'; }); _loadData(); }),
          ]),
        ),
      ),
      Expanded(
        child: _isLoading
            ? const ListSkeleton()
            : _hasError
                ? ErrorStateWidget(onRetry: _loadData)
                : _registrations.isEmpty
                    ? EmptyStateWidget(icon: Icons.person_off, title: l10n.noRegistrations, subtitle: l10n.noRegistrationsHint)
                    : ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: _registrations.length,
                        itemBuilder: (ctx, i) {
                          final r = _registrations[i];
                          return Card(
                            margin: const EdgeInsets.only(bottom: 8),
                            child: ListTile(
                              leading: CircleAvatar(child: Text(r.userName?.substring(0, 1).toUpperCase() ?? '?', style: const TextStyle(color: Colors.white))),
                              title: Text(r.userName ?? l10n.userDefaultName(r.userId)),
                              subtitle: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(r.userEmail ?? r.status, style: TextStyle(color: r.status == 'approved' ? Colors.green : r.status == 'rejected' ? Colors.red : null)),
                                  const SizedBox(height: 4),
                                  Row(mainAxisSize: MainAxisSize.min, children: [
                                    Icon(_paymentIcon(r.paymentStatus), size: 14, color: _paymentColor(r.paymentStatus)),
                                    const SizedBox(width: 4),
                                    Text(_paymentLabel(r.paymentStatus), style: TextStyle(fontSize: 12, color: _paymentColor(r.paymentStatus))),
                                  ]),
                                  if ((r.paymentMethod ?? '').isNotEmpty || (r.transactionId ?? '').isNotEmpty) ...[
                                    const SizedBox(height: 2),
                                    Text(
                                      [r.paymentMethod, r.transactionId].whereType<String>().join(' • '),
                                      style: const TextStyle(fontSize: 11),
                                      maxLines: 1,
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ],
                                ],
                              ),
                              trailing: PopupMenuButton<String>(
                                onSelected: (s) => _onMenuAction(r, s),
                                itemBuilder: (_) => [
                                  PopupMenuItem(value: 'approved', child: Text(l10n.approved)),
                                  PopupMenuItem(value: 'rejected', child: Text(l10n.rejected)),
                                  PopupMenuItem(value: 'pending', child: Text(l10n.pending)),
                                  const PopupMenuDivider(),
                                  PopupMenuItem(value: '__mark_paid', child: Text(l10n.markPaid)),
                                  PopupMenuItem(value: '__mark_refunded', child: Text(l10n.markRefunded)),
                                ],
                              ),
                            ),
                          );
                        },
                      ),
      ),
    ]);
  }
}
