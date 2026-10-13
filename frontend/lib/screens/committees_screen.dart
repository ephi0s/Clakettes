import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../services/api_service.dart';
import '../models/committee_model.dart';
import '../widgets/reusable_widgets.dart';
import '../widgets/empty_state_widget.dart';
import '../widgets/loading_skeleton.dart';
import '../widgets/error_state_widget.dart';
import '../widgets/confirm_dialog.dart';

/// Pantalla que gestiona los comités de un festival (crear, eliminar).
class CommitteesScreen extends StatefulWidget {
  final int festivalId;
  final String festivalName;
  const CommitteesScreen({super.key, required this.festivalId, required this.festivalName});

  @override
  State<CommitteesScreen> createState() => _CommitteesScreenState();
}

/// Mantiene la lista de comités cargada del festival; se carga en el primer build.
class _CommitteesScreenState extends State<CommitteesScreen> {
  final ApiService api = ApiService();
  List<Committee> _committees = [];
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

  /// Obtiene los comités del festival de la API y gestiona los errores.
  Future<void> _loadData() async {
    if (!mounted) return;
    setState(() { _isLoading = true; _hasError = false; });
    try {
      final result = await api.getCommittees(widget.festivalId, size: 100);
      if (!mounted) return;
      setState(() { _committees = result.items; _isLoading = false; });
    } catch (e) {
      debugPrint('Error: $e');
      if (!mounted) return;
      setState(() { _isLoading = false; _hasError = true; });
    }
  }

  /// Muestra un diálogo para crear un nuevo comité y recarga al tener éxito.
  Future<void> _createCommittee() async {
    final nameCtl = TextEditingController();
    final descCtl = TextEditingController();
    final result = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(l10n.newCommittee),
        content: SingleChildScrollView(
          child: Column(mainAxisSize: MainAxisSize.min, children: [
            SemanticTextField(controller: nameCtl, label: l10n.nameRequired, semanticLabel: l10n.committeeName, helperText: l10n.committeeName),
            SemanticTextField(controller: descCtl, label: l10n.description, semanticLabel: l10n.description, helperText: l10n.optional),
          ]),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: Text(l10n.cancel)),
          FilledButton(onPressed: () => Navigator.pop(ctx, true), child: Text(l10n.create)),
        ],
      ),
    );
    if (result == true && nameCtl.text.isNotEmpty) {
      try {
        await api.createCommittee(widget.festivalId, Committee(festivalId: widget.festivalId, name: nameCtl.text, description: descCtl.text));
        _loadData();
      } catch (e) {
        if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.errorFor(e)), behavior: SnackBarBehavior.floating));
      }
    }
  }

  /// Elimina el comité indicado tras un diálogo de confirmación.
  Future<void> _deleteCommittee(Committee c) async {
    if (c.id == null) return;
    final confirm = await showConfirmDialog(context, title: l10n.deleteCommittee, message: l10n.deleteEntityMessage(c.name));
    if (confirm == true) {
      await api.deleteCommittee(c.id!);
      _loadData();
    }
  }

  @override
  Widget build(BuildContext context) {
    l10n = AppLocalizations.of(context)!;

    return Scaffold(
      appBar: AppBar(title: Text('${l10n.committees} — ${widget.festivalName}')),
      body: _isLoading
          ? const ListSkeleton()
          : _hasError
              ? ErrorStateWidget(onRetry: _loadData)
              : RefreshIndicator(
                  onRefresh: _loadData,
                  child: _committees.isEmpty
                      ? EmptyStateWidget(icon: Icons.groups_outlined, title: l10n.noCommittees, subtitle: l10n.createCommitteeSubtitle)
                      : ListView.builder(
                          padding: const EdgeInsets.all(16),
                          itemCount: _committees.length,
                          itemBuilder: (ctx, i) {
                            final c = _committees[i];
                            return Card(
                              margin: const EdgeInsets.only(bottom: 12),
                              child: ListTile(
                                leading: const CircleAvatar(child: Icon(Icons.groups, color: Colors.white)),
                                title: Text(c.name, style: const TextStyle(fontWeight: FontWeight.w600)),
                                subtitle: Text('${c.description ?? ""}  ${l10n.memberCount(c.memberCount)}', style: Theme.of(context).textTheme.bodySmall),
                                trailing: Row(mainAxisSize: MainAxisSize.min, children: [
                                  StatusIndicator(isActive: c.isActive, activeLabel: l10n.active, inactiveLabel: l10n.inactive),
                                  IconButton(icon: const Icon(Icons.group_add_outlined, size: 20), tooltip: l10n.manageMembers, onPressed: () {}),
                                  IconButton(icon: const Icon(Icons.delete_outline, size: 20), tooltip: l10n.delete, onPressed: () => _deleteCommittee(c)),
                                ]),
                              ),
                            );
                          },
                        ),
                ),
      floatingActionButton: FloatingActionButton(onPressed: _createCommittee, tooltip: l10n.createCommittee, child: const Icon(Icons.add)),
    );
  }
}
