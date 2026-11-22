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

  /// Abre el diálogo de miembros y recarga el comité al cerrarlo.
  Future<void> _manageMembers(Committee c) async {
    if (c.id == null) return;
    await showDialog<void>(
      context: context,
      builder: (_) => _CommitteeMembersDialog(committee: c, api: api),
    );
    _loadData();
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
                                  IconButton(icon: const Icon(Icons.group_add_outlined, size: 20), tooltip: l10n.manageMembers, onPressed: () => _manageMembers(c)),
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

/// Diálogo que lista los miembros de un comité y permite añadirlos y eliminarlos.
class _CommitteeMembersDialog extends StatefulWidget {
  final Committee committee;
  final ApiService api;

  const _CommitteeMembersDialog({required this.committee, required this.api});

  @override
  State<_CommitteeMembersDialog> createState() => _CommitteeMembersDialogState();
}

class _CommitteeMembersDialogState extends State<_CommitteeMembersDialog> {
  List<CommitteeMember> _members = [];
  bool _isLoading = true;
  bool _busy = false;
  String? _error;
  AppLocalizations get l10n => AppLocalizations.of(context)!;

  @override
  void initState() {
    super.initState();
    _loadMembers();
  }

  Future<void> _loadMembers() async {
    if (!mounted) return;
    setState(() { _isLoading = true; _error = null; });
    try {
      final result = await widget.api.getCommitteeMembers(widget.committee.id!, size: 100);
      if (!mounted) return;
      setState(() { _members = result.items; _isLoading = false; });
    } catch (e) {
      debugPrint('Error: $e');
      if (!mounted) return;
      setState(() { _isLoading = false; _error = l10n.errorFor(e); });
    }
  }

  Future<void> _addMember() async {
    final userIdCtl = TextEditingController();
    final notesCtl = TextEditingController();
    String role = 'member';
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setDialogState) => AlertDialog(
          title: Text('${l10n.add} ${l10n.members}'),
          content: SingleChildScrollView(
            child: Column(mainAxisSize: MainAxisSize.min, children: [
              SemanticTextField(
                controller: userIdCtl,
                label: l10n.users,
                semanticLabel: l10n.users,
                keyboardType: TextInputType.number,
                textInputAction: TextInputAction.next,
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<String>(
                initialValue: role,
                decoration: InputDecoration(labelText: l10n.role),
                items: committeeRoles
                    .map((r) => DropdownMenuItem<String>(value: r, child: Text(r.replaceAll('_', ' '))))
                    .toList(),
                onChanged: (v) => setDialogState(() => role = v ?? 'member'),
              ),
              const SizedBox(height: 12),
              SemanticTextField(
                controller: notesCtl,
                label: l10n.notes,
                semanticLabel: l10n.notes,
                helperText: l10n.optional,
              ),
            ]),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx, false), child: Text(l10n.cancel)),
            FilledButton(onPressed: () => Navigator.pop(ctx, true), child: Text(l10n.add)),
          ],
        ),
      ),
    );
    if (confirmed != true || !mounted) return;
    final userId = int.tryParse(userIdCtl.text.trim());
    if (userId == null) {
      showAppSnack(context, l10n.invalidValue);
      return;
    }
    setState(() => _busy = true);
    try {
      await widget.api.addCommitteeMember(
        widget.committee.id!,
        CommitteeMember(
          committeeId: widget.committee.id!,
          userId: userId,
          roleInCommittee: role,
          notes: notesCtl.text.trim().isEmpty ? null : notesCtl.text.trim(),
        ),
      );
      if (mounted) showAppSnack(context, l10n.saved);
      _loadMembers();
    } catch (e) {
      if (mounted) showAppSnack(context, l10n.errorFor(e));
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _removeMember(CommitteeMember m) async {
    if (m.id == null) return;
    final confirm = await showConfirmDialog(
      context,
      title: l10n.delete,
      message: '${m.userName ?? l10n.users} #${m.userId}',
    );
    if (confirm != true || !mounted) return;
    try {
      await widget.api.removeCommitteeMember(m.id!);
      _loadMembers();
    } catch (e) {
      if (mounted) showAppSnack(context, l10n.errorFor(e));
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text('${l10n.manageMembers} — ${widget.committee.name}'),
      content: SizedBox(
        width: double.maxFinite,
        child: _isLoading
            ? const Padding(padding: EdgeInsets.all(32), child: Center(child: CircularProgressIndicator()))
            : _error != null
                ? Text(_error!)
                : _members.isEmpty
                    ? Padding(
                        padding: const EdgeInsets.symmetric(vertical: 24),
                        child: Text(l10n.noMembersFound, textAlign: TextAlign.center, style: Theme.of(context).textTheme.bodyMedium),
                      )
                    : ListView.builder(
                        shrinkWrap: true,
                        itemCount: _members.length,
                        itemBuilder: (ctx, i) {
                          final m = _members[i];
                          final displayName = m.userName ?? '${l10n.users} #${m.userId}';
                          return ListTile(
                            leading: CircleAvatar(child: Text(displayName.substring(0, 1).toUpperCase())),
                            title: Text(displayName),
                            subtitle: Text('${m.roleInCommittee.replaceAll('_', ' ')} • ${l10n.users} #${m.userId}'),
                            trailing: IconButton(
                              icon: const Icon(Icons.delete_outline, size: 20),
                              tooltip: l10n.delete,
                              onPressed: _busy ? null : () => _removeMember(m),
                            ),
                          );
                        },
                      ),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context), child: Text(l10n.close)),
        FilledButton.icon(
          onPressed: _busy ? null : _addMember,
          icon: const Icon(Icons.person_add_alt_1_outlined, size: 18),
          label: Text(l10n.add),
        ),
      ],
    );
  }
}
