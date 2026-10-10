import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../l10n/app_localizations.dart';
import '../models/festival_rulebook_model.dart';
import '../models/user_model.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import '../services/file_downloader.dart';
import '../widgets/confirm_dialog.dart';
import '../widgets/empty_state_widget.dart';
import '../widgets/error_state_widget.dart';
import '../widgets/loading_skeleton.dart';
import '../widgets/reusable_widgets.dart';

/// Sección de bases de un festival (sección oficial, concursos y actividades).
///
/// Cualquiera puede consultar las bases; solo la dirección/organización del
/// festival y la administración central pueden crearlas, editarlas o
/// eliminarlas (el backend responde 403 en caso contrario).
class FestivalRulebooksScreen extends StatefulWidget {
  final int festivalId;
  final String festivalName;

  const FestivalRulebooksScreen({super.key, required this.festivalId, required this.festivalName});

  @override
  State<FestivalRulebooksScreen> createState() => _FestivalRulebooksScreenState();
}

class _FestivalRulebooksScreenState extends State<FestivalRulebooksScreen> {
  final ApiService api = ApiService();
  List<FestivalRulebook> _items = [];
  bool _isLoading = true;
  bool _hasError = false;
  bool _initialized = false;
  bool _canEdit = false;
  String? _categoryFilter;
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

  Future<void> _loadData() async {
    if (!mounted) return;
    setState(() {
      _isLoading = true;
      _hasError = false;
    });
    try {
      final results = await Future.wait([
        api.getRulebooks(widget.festivalId, size: 100, category: _categoryFilter),
        AuthService().getCurrentUser(),
      ]);
      if (!mounted) return;
      final page = results[0] as PaginatedResult<FestivalRulebook>;
      final user = results[1] as User?;
      final role = (user?.role ?? '').toLowerCase();
      setState(() {
        _items = page.items;
        _canEdit = role == 'admin' || role == 'organizer';
        _isLoading = false;
      });
    } catch (e) {
      debugPrint('Error: $e');
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _hasError = true;
      });
    }
  }

  String _resolveUrl(FestivalRulebook r) {
    final url = r.documentUrl;
    if (url.startsWith('http://') || url.startsWith('https://')) return url;
    return '${api.rootUrl}$url';
  }

  Future<void> _openDocument(FestivalRulebook r) async {
    if (!r.hasDocument) return;
    final uri = Uri.tryParse(_resolveUrl(r));
    if (uri == null) return;
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } else if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(l10n.loadError), behavior: SnackBarBehavior.floating),
      );
    }
  }

  Future<void> _downloadDocument(FestivalRulebook r) async {
    if (r.fileUrl == null) return;
    try {
      final bytes = await api.getBytes(r.fileUrl!);
      final name = r.fileUrl!.split('/').lastWhere((s) => s.isNotEmpty, orElse: () => 'bases.pdf');
      await downloadFile(bytes, name);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.exportSuccess), behavior: SnackBarBehavior.floating),
        );
      }
    } catch (e) {
      debugPrint('Error: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.exportError), behavior: SnackBarBehavior.floating),
        );
      }
    }
  }

  Future<void> _showEditDialog({FestivalRulebook? existing}) async {
    final titleCtl = TextEditingController(text: existing?.title ?? '');
    final descCtl = TextEditingController(text: existing?.description ?? '');
    final urlCtl = TextEditingController(text: existing?.externalUrl ?? '');
    String category = existing?.category ?? 'official_section';
    String? pickedPdfPath;
    String? pickedPdfName;
    final formKey = GlobalKey<FormState>();

    final saved = await showDialog<bool>(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setDialogState) => AlertDialog(
          title: Text(existing == null ? l10n.newRulebook : l10n.editRulebook),
          content: SingleChildScrollView(
            child: Form(
              key: formKey,
              child: Column(mainAxisSize: MainAxisSize.min, children: [
                SemanticTextField(
                  controller: titleCtl,
                  label: l10n.titleRequired,
                  semanticLabel: l10n.title,
                  validator: (v) => (v == null || v.trim().isEmpty) ? l10n.getValidationMessage('required') : null,
                ),
                const SizedBox(height: 12),
                Semantics(
                  label: l10n.rulebookCategory,
                  child: DropdownButtonFormField<String>(
                    initialValue: category,
                    decoration: InputDecoration(labelText: l10n.rulebookCategory),
                    items: FestivalRulebook.categories
                        .map((c) => DropdownMenuItem(value: c, child: Text(l10n.getRulebookCategory(c))))
                        .toList(),
                    onChanged: (v) => setDialogState(() => category = v ?? category),
                  ),
                ),
                const SizedBox(height: 12),
                SemanticTextField(
                  controller: descCtl,
                  label: l10n.description,
                  semanticLabel: l10n.description,
                  helperText: l10n.optional,
                  maxLines: 3,
                ),
                const SizedBox(height: 12),
                SemanticTextField(
                  controller: urlCtl,
                  label: l10n.rulebookExternalUrl,
                  semanticLabel: l10n.rulebookExternalUrl,
                  helperText: l10n.optional,
                  keyboardType: TextInputType.url,
                ),
                const SizedBox(height: 12),
                OutlinedButton.icon(
                  icon: const Icon(Icons.picture_as_pdf_outlined),
                  label: Text(pickedPdfName ?? l10n.rulebookPickPdf),
                  onPressed: () async {
                    final result = await FilePicker.platform.pickFiles(
                      type: FileType.custom,
                      allowedExtensions: ['pdf'],
                      withData: false,
                    );
                    if (result != null && result.files.single.path != null) {
                      setDialogState(() {
                        pickedPdfPath = result.files.single.path;
                        pickedPdfName = result.files.single.name;
                      });
                    }
                  },
                ),
                if (existing?.fileUrl != null)
                  Padding(
                    padding: const EdgeInsets.only(top: 4),
                    child: Text(l10n.rulebookCurrentFile, style: Theme.of(ctx).textTheme.bodySmall),
                  ),
              ]),
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx, false), child: Text(l10n.cancel)),
            FilledButton(
              onPressed: () {
                if (!(formKey.currentState?.validate() ?? false)) return;
                if (existing == null && pickedPdfPath == null && urlCtl.text.trim().isEmpty) {
                  ScaffoldMessenger.of(ctx).showSnackBar(
                    SnackBar(content: Text(l10n.rulebookDocumentRequired), behavior: SnackBarBehavior.floating),
                  );
                  return;
                }
                Navigator.pop(ctx, true);
              },
              child: Text(l10n.save),
            ),
          ],
        ),
      ),
    );
    if (saved != true) return;
    try {
      if (existing == null) {
        if (pickedPdfPath != null) {
          await api.uploadRulebook(
            widget.festivalId,
            pickedPdfPath!,
            title: titleCtl.text.trim(),
            description: descCtl.text.trim().isEmpty ? null : descCtl.text.trim(),
            category: category,
            externalUrl: urlCtl.text.trim().isEmpty ? null : urlCtl.text.trim(),
          );
        } else {
          await api.createRulebook(
            widget.festivalId,
            FestivalRulebook(
              festivalId: widget.festivalId,
              title: titleCtl.text.trim(),
              description: descCtl.text.trim().isEmpty ? null : descCtl.text.trim(),
              category: category,
              externalUrl: urlCtl.text.trim(),
            ),
          );
        }
      } else {
        await api.updateRulebook(widget.festivalId, existing.id!, {
          'title': titleCtl.text.trim(),
          'description': descCtl.text.trim().isEmpty ? null : descCtl.text.trim(),
          'category': category,
          'external_url': urlCtl.text.trim().isEmpty ? null : urlCtl.text.trim(),
        });
        if (pickedPdfPath != null) {
          await api.uploadRulebook(
            widget.festivalId,
            pickedPdfPath!,
            title: titleCtl.text.trim(),
            description: descCtl.text.trim().isEmpty ? null : descCtl.text.trim(),
            category: category,
            externalUrl: urlCtl.text.trim().isEmpty ? null : urlCtl.text.trim(),
          );
          await api.deleteRulebook(widget.festivalId, existing.id!);
        }
      }
      _loadData();
    } catch (e) {
      debugPrint('Error: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.errorFormatWith('$e')), behavior: SnackBarBehavior.floating),
        );
      }
    }
  }

  Future<void> _deleteItem(FestivalRulebook r) async {
    if (r.id == null) return;
    final confirm = await showConfirmDialog(context, title: l10n.deleteRulebook, message: l10n.deleteEntityMessage(r.title));
    if (confirm == true) {
      try {
        await api.deleteRulebook(widget.festivalId, r.id!);
        _loadData();
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(l10n.errorFormatWith('$e')), behavior: SnackBarBehavior.floating),
          );
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Scaffold(
      appBar: AppBar(title: Text('${l10n.rulebooks} — ${widget.festivalName}')),
      body: _isLoading
          ? const ListSkeleton()
          : _hasError
              ? ErrorStateWidget(onRetry: _loadData)
              : RefreshIndicator(
                  onRefresh: _loadData,
                  child: Column(
                    children: [
                      SingleChildScrollView(
                        scrollDirection: Axis.horizontal,
                        padding: const EdgeInsets.fromLTRB(16, 12, 16, 4),
                        child: Row(
                          children: [
                            FilterChip(
                              label: Text(l10n.all),
                              selected: _categoryFilter == null,
                              onSelected: (_) {
                                setState(() => _categoryFilter = null);
                                _loadData();
                              },
                            ),
                            const SizedBox(width: 8),
                            ...FestivalRulebook.categories.map((c) => Padding(
                                  padding: const EdgeInsets.only(right: 8),
                                  child: FilterChip(
                                    label: Text(l10n.getRulebookCategory(c)),
                                    selected: _categoryFilter == c,
                                    onSelected: (_) {
                                      setState(() => _categoryFilter = c);
                                      _loadData();
                                    },
                                  ),
                                )),
                          ],
                        ),
                      ),
                      Expanded(
                        child: _items.isEmpty
                            ? EmptyStateWidget(
                                icon: Icons.description_outlined,
                                title: l10n.noRulebooks,
                                subtitle: l10n.noRulebooksHint,
                              )
                            : ListView.builder(
                                padding: const EdgeInsets.all(16),
                                itemCount: _items.length,
                                itemBuilder: (ctx, i) {
                                  final r = _items[i];
                                  return Card(
                                    margin: const EdgeInsets.only(bottom: 12),
                                    child: ListTile(
                                      leading: CircleAvatar(
                                        backgroundColor: colorScheme.secondaryContainer,
                                        child: Icon(
                                          r.fileUrl != null ? Icons.picture_as_pdf : Icons.link,
                                          color: colorScheme.onSecondaryContainer,
                                        ),
                                      ),
                                      title: Text(r.title, style: const TextStyle(fontWeight: FontWeight.w600)),
                                      subtitle: Column(
                                        crossAxisAlignment: CrossAxisAlignment.start,
                                        mainAxisSize: MainAxisSize.min,
                                        children: [
                                          Text(l10n.getRulebookCategory(r.category), style: theme.textTheme.bodySmall),
                                          if (r.description != null && r.description!.isNotEmpty)
                                            Text(r.description!, style: theme.textTheme.bodySmall, maxLines: 2, overflow: TextOverflow.ellipsis),
                                        ],
                                      ),
                                      trailing: Row(mainAxisSize: MainAxisSize.min, children: [
                                        if (r.hasDocument)
                                          IconButton(
                                            icon: const Icon(Icons.open_in_new, size: 20),
                                            tooltip: l10n.open,
                                            onPressed: () => _openDocument(r),
                                          ),
                                        if (r.fileUrl != null)
                                          IconButton(
                                            icon: const Icon(Icons.download_outlined, size: 20),
                                            tooltip: l10n.export,
                                            onPressed: () => _downloadDocument(r),
                                          ),
                                        if (_canEdit) ...[
                                          IconButton(
                                            icon: const Icon(Icons.edit_outlined, size: 20),
                                            tooltip: l10n.edit,
                                            onPressed: () => _showEditDialog(existing: r),
                                          ),
                                          IconButton(
                                            icon: const Icon(Icons.delete_outline, size: 20),
                                            tooltip: l10n.delete,
                                            onPressed: () => _deleteItem(r),
                                          ),
                                        ],
                                      ]),
                                      onTap: r.hasDocument ? () => _openDocument(r) : null,
                                    ),
                                  );
                                },
                              ),
                      ),
                    ],
                  ),
                ),
      floatingActionButton: _canEdit && !_isLoading
          ? FloatingActionButton(
              onPressed: () => _showEditDialog(),
              tooltip: l10n.newRulebook,
              child: const Icon(Icons.add),
            )
          : null,
    );
  }
}
