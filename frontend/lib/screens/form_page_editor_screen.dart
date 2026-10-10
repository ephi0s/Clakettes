import 'package:flutter/material.dart' hide FormField;
import '../l10n/app_localizations.dart';
import '../services/api_service.dart';
import '../models/form_definition_model.dart';
import '../widgets/reusable_widgets.dart';
import '../widgets/confirm_dialog.dart';

/// Asocia cada tipo de campo con el icono mostrado en el selector de tipos y
/// en la lista.
Map<String, IconData> _fieldTypeIcons = {
  FormFieldType.string: Icons.text_fields,
  FormFieldType.email: Icons.email_outlined,
  FormFieldType.phone: Icons.phone_outlined,
  FormFieldType.url: Icons.link_outlined,
  FormFieldType.date: Icons.calendar_today_outlined,
  FormFieldType.number: Icons.numbers_outlined,
  FormFieldType.boolean: Icons.toggle_on_outlined,
  FormFieldType.select: Icons.arrow_drop_down_circle_outlined,
  FormFieldType.multiselect: Icons.checklist_outlined,
  FormFieldType.file: Icons.upload_file_outlined,
  FormFieldType.alias: Icons.person_outline,
  FormFieldType.roleSelector: Icons.badge_outlined,
  FormFieldType.tagSelector: Icons.label_outline,
  FormFieldType.sectionBreak: Icons.horizontal_rule,
  FormFieldType.staticText: Icons.article_outlined,
};

/// Etiquetas localizadas para cada tipo de campo admitido.
Map<String, String> _fieldTypeLabels(AppLocalizations l10n) => {
  FormFieldType.string: l10n.stringField,
  FormFieldType.email: l10n.emailField,
  FormFieldType.phone: l10n.phoneField,
  FormFieldType.url: l10n.urlField,
  FormFieldType.date: l10n.dateField,
  FormFieldType.number: l10n.numberField,
  FormFieldType.boolean: l10n.booleanField,
  FormFieldType.select: l10n.selectField,
  FormFieldType.multiselect: l10n.multiselectField,
  FormFieldType.file: l10n.fileField,
  FormFieldType.alias: l10n.aliasField,
  FormFieldType.roleSelector: l10n.roleSelectorField,
  FormFieldType.tagSelector: l10n.tagSelectorField,
  FormFieldType.sectionBreak: l10n.sectionBreakField,
  FormFieldType.staticText: l10n.staticTextField,
};

/// Editor de una única página de formulario: título, descripción y sus campos
/// con capacidad de añadir, editar, eliminar y reordenar.
class FormPageEditorScreen extends StatefulWidget {
  final FormDefinition form;
  final FormPage page;
  const FormPageEditorScreen({super.key, required this.form, required this.page});

  @override
  State<FormPageEditorScreen> createState() => _FormPageEditorScreenState();
}

/// Mantiene la copia local de los campos de la página y los controladores de
/// título/descripción inicializados a partir de la página.
class _FormPageEditorScreenState extends State<FormPageEditorScreen> {
  final ApiService api = ApiService();
  late List<FormField> _fields;
  late TextEditingController _titleCtl;
  late TextEditingController _descCtl;
  late AppLocalizations l10n;

  @override
  void initState() {
    super.initState();
    _titleCtl = TextEditingController(text: widget.page.title);
    _descCtl = TextEditingController(text: widget.page.description ?? '');
    _fields = List.from(widget.page.fields);
  }

  @override
  void dispose() {
    _titleCtl.dispose();
    _descCtl.dispose();
    super.dispose();
  }

  /// Persiste el título y la descripción de la página a través de la API.
  Future<bool?> _savePage() async {
    if (widget.page.id == null) return false;
    try {
      await api.updatePage(widget.form.id!, widget.page.id!, {
        'title': _titleCtl.text.trim(),
        'description': _descCtl.text.trim().isEmpty ? null : _descCtl.text.trim(),
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.saved), behavior: SnackBarBehavior.floating));
        return true;
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.errorFormatWith('$e')), behavior: SnackBarBehavior.floating));
      }
    }
    return false;
  }

  /// Crea un nuevo campo del tipo indicado y lo añade a la página.
  Future<void> _addField(String fieldType) async {
    if (widget.page.id == null) return;
    try {
      final field = await api.createField(widget.form.id!, widget.page.id!, {
        'field_type': fieldType,
        'label': l10n.translate('newField'),
        'page_id': widget.page.id!,
        'sort_order': _fields.length,
      });
      setState(() => _fields.add(field));
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.errorFormatWith('$e')), behavior: SnackBarBehavior.floating));
    }
  }

  /// Abre el diálogo de edición del campo y persiste los cambios devueltos.
  Future<void> _editField(int index) async {
    final field = _fields[index];
    final result = await showDialog<Map<String, dynamic>>(
      context: context,
      builder: (ctx) => _FieldEditDialog(field: field),
    );
    if (result == null || field.id == null) return;
    try {
      final updated = await api.updateField(widget.form.id!, field.id!, result);
      setState(() => _fields[index] = updated);
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.errorFormatWith('$e')), behavior: SnackBarBehavior.floating));
    }
  }

  /// Elimina el campo en el índice indicado tras un diálogo de confirmación.
  Future<void> _deleteField(int index) async {
    final field = _fields[index];
    if (field.id == null) return;
    final confirm = await showConfirmDialog(context, title: l10n.deleteField, message: l10n.translate('deleteFieldMessage'));
    if (confirm == true) {
      await api.deleteField(widget.form.id!, field.id!);
      setState(() => _fields.removeAt(index));
    }
  }

  /// Reordena un campo dentro de la página tras una operación de arrastrar y
  /// soltar (onReorderItem ya ajusta newIndex, sin corrección manual).
  Future<void> _moveField(int oldIndex, int newIndex) async {
    final field = _fields.removeAt(oldIndex);
    _fields.insert(newIndex, field);
    setState(() {});
  }

  /// Muestra la cuadrícula de hoja inferior con los tipos de campo disponibles
  /// para añadir.
  void _showFieldTypeSelector() {
    final labels = _fieldTypeLabels(l10n);
    showModalBottomSheet(
      context: context,
      builder: (ctx) => Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(l10n.selectFieldType, style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600)),
            const SizedBox(height: 12),
            GridView.count(
              crossAxisCount: 3,
              shrinkWrap: true,
              mainAxisSpacing: 8,
              crossAxisSpacing: 8,
              childAspectRatio: 1.1,
              children: _fieldTypeIcons.entries.map((entry) {
                return InkWell(
                  onTap: () { Navigator.pop(ctx); _addField(entry.key); },
                  borderRadius: BorderRadius.circular(12),
                  child: Container(
                    decoration: BoxDecoration(
                      border: Border.all(color: Theme.of(context).colorScheme.outlineVariant),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    padding: const EdgeInsets.all(8),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(entry.value, size: 28, color: Theme.of(context).colorScheme.primary),
                        const SizedBox(height: 6),
                        Text(labels[entry.key] ?? entry.key, style: const TextStyle(fontSize: 11), textAlign: TextAlign.center, maxLines: 2, overflow: TextOverflow.ellipsis),
                      ],
                    ),
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: 8),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    l10n = AppLocalizations.of(context)!;

    return Scaffold(
      appBar: AppBar(
        title: Text('${l10n.formBuilder} - ${widget.page.title}'),
        actions: [
          IconButton(
            icon: const Icon(Icons.save_outlined),
            tooltip: l10n.save,
            onPressed: () async { await _savePage(); if (!context.mounted) return; Navigator.pop(context, true); },
          ),
        ],
      ),
      body: Column(children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: Column(children: [
            SemanticTextField(controller: _titleCtl, label: l10n.titleRequired, semanticLabel: l10n.translate('pageTitle')),
            const SizedBox(height: 8),
            SemanticTextField(controller: _descCtl, label: l10n.description, maxLines: 2, semanticLabel: l10n.description, helperText: l10n.optionalDescription),
          ]),
        ),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Row(children: [
            Text(l10n.fieldsCount(_fields.length), style: TextStyle(color: Theme.of(context).colorScheme.onSurfaceVariant)),
            const Spacer(),
            FilledButton.tonalIcon(onPressed: _showFieldTypeSelector, icon: const Icon(Icons.add), label: Text(l10n.addField)),
          ]),
        ),
        const SizedBox(height: 8),
        Expanded(
          child: _fields.isEmpty
              ? Center(child: Text(l10n.translate('noFieldsHint'), style: TextStyle(color: Theme.of(context).colorScheme.onSurfaceVariant)))
              : ReorderableListView.builder(
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                  itemCount: _fields.length,
                  onReorderItem: _moveField,
                  itemBuilder: (ctx, i) {
                    final f = _fields[i];
                    final labels = _fieldTypeLabels(l10n);
                    return Card(
                      key: ValueKey(f.id ?? 'field_$i'),
                      margin: const EdgeInsets.only(bottom: 8),
                      child: ListTile(
                        leading: Icon(_fieldTypeIcons[f.fieldType] ?? Icons.text_fields, color: Theme.of(context).colorScheme.primary),
                        title: Text(f.label, style: const TextStyle(fontWeight: FontWeight.w600)),
                        subtitle: Text(labels[f.fieldType] ?? f.fieldType),
                        trailing: Row(mainAxisSize: MainAxisSize.min, children: [
                          if (f.isRequired)
                            Chip(
                              label: Text(l10n.isRequired, style: const TextStyle(fontSize: 11)),
                              visualDensity: VisualDensity.compact,
                              padding: EdgeInsets.zero,
                              materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                            ),
                          const SizedBox(width: 4),
                          IconButton(
                            icon: const Icon(Icons.edit_outlined, size: 20),
                            tooltip: l10n.editField,
                            onPressed: () => _editField(i),
                          ),
                          IconButton(
                            icon: const Icon(Icons.delete_outline, size: 20),
                            tooltip: l10n.delete,
                            onPressed: () => _deleteField(i),
                          ),
                          ReorderableDragStartListener(
                            index: i,
                            child: const Icon(Icons.drag_handle),
                          ),
                        ]),
                        onTap: () => _editField(i),
                      ),
                    );
                  },
                ),
        ),
      ]),
    );
  }
}

/// Diálogo para editar la configuración y las opciones de un único campo de
/// formulario.
class _FieldEditDialog extends StatefulWidget {
  final FormField field;
  const _FieldEditDialog({required this.field});

  @override
  State<_FieldEditDialog> createState() => _FieldEditDialogState();
}

/// Mantiene los controladores de cada propiedad editable del campo y sus
/// opciones.
class _FieldEditDialogState extends State<_FieldEditDialog> {
  late TextEditingController _labelCtl;
  late TextEditingController _helpCtl;
  late TextEditingController _placeholderCtl;
  late TextEditingController _minLengthCtl;
  late TextEditingController _maxLengthCtl;
  late TextEditingController _minValueCtl;
  late TextEditingController _maxValueCtl;
  late TextEditingController _regexCtl;
  late TextEditingController _dependsOnValueCtl;
  late bool _isRequired;
  late bool _isVisible;
  late bool _isReadOnly;
  late String _widthClass;
  List<FormFieldOption> _options = [];

  @override
  void initState() {
    super.initState();
    final f = widget.field;
    _labelCtl = TextEditingController(text: f.label);
    _helpCtl = TextEditingController(text: f.helpText ?? '');
    _placeholderCtl = TextEditingController(text: f.placeholder ?? '');
    _minLengthCtl = TextEditingController(text: f.minLength?.toString() ?? '');
    _maxLengthCtl = TextEditingController(text: f.maxLength?.toString() ?? '');
    _minValueCtl = TextEditingController(text: f.minValue?.toString() ?? '');
    _maxValueCtl = TextEditingController(text: f.maxValue?.toString() ?? '');
    _regexCtl = TextEditingController(text: f.regexPattern ?? '');
    _dependsOnValueCtl = TextEditingController(text: f.dependsOnValue ?? '');
    _isRequired = f.isRequired;
    _isVisible = f.isVisible;
    _isReadOnly = f.isReadOnly;
    _widthClass = f.widthClass ?? 'full';
    _options = List.from(f.options);
  }

  @override
  void dispose() {
    _labelCtl.dispose();
    _helpCtl.dispose();
    _placeholderCtl.dispose();
    _minLengthCtl.dispose();
    _maxLengthCtl.dispose();
    _minValueCtl.dispose();
    _maxValueCtl.dispose();
    _regexCtl.dispose();
    _dependsOnValueCtl.dispose();
    super.dispose();
  }

  bool _isTextLike() {
    final t = widget.field.fieldType;
    return t == FormFieldType.string || t == FormFieldType.email || t == FormFieldType.phone || t == FormFieldType.url;
  }

  bool _isNumberLike() {
    return widget.field.fieldType == FormFieldType.number;
  }

  bool _isSelectLike() {
    final t = widget.field.fieldType;
    return t == FormFieldType.select || t == FormFieldType.multiselect;
  }

  bool _isSimpleField() {
    final t = widget.field.fieldType;
    return t != FormFieldType.sectionBreak && t != FormFieldType.staticText;
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return AlertDialog(
      title: Text(l10n.editField),
      content: SingleChildScrollView(
        child: Column(mainAxisSize: MainAxisSize.min, children: [
          SemanticTextField(controller: _labelCtl, label: l10n.fieldLabel, semanticLabel: l10n.fieldLabel),
          const SizedBox(height: 8),
          if (_isSimpleField()) ...[
            SemanticTextField(controller: _helpCtl, label: l10n.helpText, semanticLabel: l10n.helpText),
            const SizedBox(height: 8),
            SemanticTextField(controller: _placeholderCtl, label: l10n.placeholder, semanticLabel: l10n.placeholder),
            const SizedBox(height: 8),
          ],
          if (_isTextLike()) ...[
            TextField(controller: _minLengthCtl, decoration: InputDecoration(labelText: l10n.translate('minLength')), keyboardType: TextInputType.number),
            const SizedBox(height: 8),
            TextField(controller: _maxLengthCtl, decoration: InputDecoration(labelText: l10n.translate('maxLength')), keyboardType: TextInputType.number),
            const SizedBox(height: 8),
            TextField(controller: _regexCtl, decoration: InputDecoration(labelText: l10n.regexPattern, helperText: l10n.translate('regexHint'))),
            const SizedBox(height: 8),
          ],
          if (_isNumberLike()) ...[
            TextField(controller: _minValueCtl, decoration: InputDecoration(labelText: l10n.translate('minValue')), keyboardType: TextInputType.number),
            const SizedBox(height: 8),
            TextField(controller: _maxValueCtl, decoration: InputDecoration(labelText: l10n.translate('maxValue')), keyboardType: TextInputType.number),
            const SizedBox(height: 8),
          ],
          if (_isSelectLike()) ...[
            Text(l10n.optionsLabel, style: const TextStyle(fontWeight: FontWeight.w600)),
            const SizedBox(height: 4),
            ..._options.asMap().entries.map((entry) {
              final i = entry.key;
              final o = entry.value;
              return ListTile(
                dense: true,
                title: Text('${o.label} (${o.value})'),
                trailing: IconButton(
                  icon: const Icon(Icons.delete_outline, size: 18),
                  onPressed: () { setState(() => _options.removeAt(i)); },
                ),
              );
            }),
            TextButton.icon(
              onPressed: () async {
                final valCtl = TextEditingController();
                final lblCtl = TextEditingController();
                final result = await showDialog<Map<String, String>>(
                  context: context,
                  builder: (ctx) => AlertDialog(
                    title: Text(l10n.addOption),
                    content: Column(mainAxisSize: MainAxisSize.min, children: [
                      TextField(controller: lblCtl, decoration: InputDecoration(labelText: l10n.optionLabel)),
                      const SizedBox(height: 8),
                      TextField(controller: valCtl, decoration: InputDecoration(labelText: l10n.optionValue)),
                    ]),
                    actions: [
                      TextButton(onPressed: () => Navigator.pop(ctx), child: Text(l10n.cancel)),
                      FilledButton(onPressed: () { if (lblCtl.text.isNotEmpty) Navigator.pop(ctx, {'label': lblCtl.text, 'value': valCtl.text}); }, child: Text(l10n.add)),
                    ],
                  ),
                );
                if (result != null) {
                  setState(() => _options.add(FormFieldOption(value: result['value'] ?? result['label']!, label: result['label']!)));
                }
              },
              icon: const Icon(Icons.add, size: 18),
              label: Text(l10n.addOption),
            ),
            const SizedBox(height: 8),
          ],
          if (_isSimpleField()) ...[
            SwitchListTile(title: Text(l10n.isRequired), value: _isRequired, onChanged: (v) => setState(() { _isRequired = v; }), dense: true),
            SwitchListTile(title: Text(l10n.isVisible), value: _isVisible, onChanged: (v) => setState(() { _isVisible = v; }), dense: true),
            SwitchListTile(title: Text(l10n.isReadOnly), value: _isReadOnly, onChanged: (v) => setState(() { _isReadOnly = v; }), dense: true),
          ],
          const SizedBox(height: 8),
          DropdownButtonFormField<String>(
            initialValue: _widthClass,
            decoration: InputDecoration(labelText: l10n.widthClass),
            items: [
              DropdownMenuItem(value: 'full', child: Text(l10n.fullWidth)),
              DropdownMenuItem(value: 'half', child: Text(l10n.halfWidth)),
              DropdownMenuItem(value: 'third', child: Text(l10n.thirdWidth)),
            ],
            onChanged: (v) { if (v != null) setState(() { _widthClass = v; }); },
          ),
          const SizedBox(height: 8),
          TextField(controller: _dependsOnValueCtl, decoration: InputDecoration(labelText: l10n.translate('dependsOnValue'), helperText: l10n.translate('dependsOnValueHint'))),
        ]),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context), child: Text(l10n.cancel)),
        FilledButton(
          onPressed: () {
            final data = <String, dynamic>{
              'label': _labelCtl.text.trim(),
              'help_text': _helpCtl.text.trim().isEmpty ? null : _helpCtl.text.trim(),
              'placeholder': _placeholderCtl.text.trim().isEmpty ? null : _placeholderCtl.text.trim(),
              'is_required': _isRequired,
              'is_visible': _isVisible,
              'is_read_only': _isReadOnly,
              'width_class': _widthClass,
            };
            if (_minLengthCtl.text.isNotEmpty) data['min_length'] = int.tryParse(_minLengthCtl.text);
            if (_maxLengthCtl.text.isNotEmpty) data['max_length'] = int.tryParse(_maxLengthCtl.text);
            if (_minValueCtl.text.isNotEmpty) data['min_value'] = num.tryParse(_minValueCtl.text);
            if (_maxValueCtl.text.isNotEmpty) data['max_value'] = num.tryParse(_maxValueCtl.text);
            if (_regexCtl.text.isNotEmpty) data['regex_pattern'] = _regexCtl.text;
            if (_dependsOnValueCtl.text.isNotEmpty) data['depends_on_value'] = _dependsOnValueCtl.text.trim();
            if (_isSelectLike()) {
              data['options'] = _options.map((o) => o.toJson()).toList();
            }
            Navigator.pop(context, data);
          },
          child: Text(l10n.save),
        ),
      ],
    );
  }
}
