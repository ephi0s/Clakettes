import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../services/api_service.dart';
import '../models/role_group_model.dart';
import '../widgets/reusable_widgets.dart';
import '../widgets/loading_skeleton.dart';
import '../widgets/error_state_widget.dart';

/// Pantalla de administración para gestionar grupos de roles: listarlos,
/// crearlos y eliminarlos.
class RolesManagementScreen extends StatefulWidget {
  const RolesManagementScreen({super.key});

  @override
  State<RolesManagementScreen> createState() => _RolesManagementScreenState();
}

/// Estado de [RolesManagementScreen]. Carga los grupos de roles en el primer build.
class _RolesManagementScreenState extends State<RolesManagementScreen> {
  final ApiService api = ApiService();
  List<RoleGroup> _groups = [];
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

  /// Obtiene los grupos de roles de la API.
  Future<void> _loadData() async {
    if (!mounted) return;
    setState(() { _isLoading = true; _hasError = false; });
    try {
      final result = await api.getRoleGroups(size: 100);
      if (!mounted) return;
      setState(() { _groups = result.items; _isLoading = false; });
    } catch (e) {
      debugPrint('Error: $e');
      if (!mounted) return;
      setState(() { _isLoading = false; _hasError = true; });
    }
  }

  /// Muestra un diálogo para los campos del grupo y lo crea al confirmar.
  Future<void> _createGroup() async {
    final nameCtl = TextEditingController();
    final displayCtl = TextEditingController();
    final descCtl = TextEditingController();
    final result = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(l10n.newRoleGroup),
        content: SingleChildScrollView(
          child: Column(mainAxisSize: MainAxisSize.min, children: [
            SemanticTextField(controller: nameCtl, label: l10n.nameRequired, semanticLabel: l10n.groupName, helperText: l10n.groupName),
            SemanticTextField(controller: displayCtl, label: l10n.displayNameRequired, semanticLabel: l10n.displayName, helperText: l10n.displayName),
            SemanticTextField(controller: descCtl, label: l10n.description, semanticLabel: l10n.description, helperText: l10n.optional),
          ]),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: Text(l10n.cancel)),
          Semantics(
            label: l10n.createRoleGroup,
            button: true,
            child: FilledButton(onPressed: () => Navigator.pop(ctx, true), child: Text(l10n.create)),
          ),
        ],
      ),
    );
    if (result == true && nameCtl.text.isNotEmpty && displayCtl.text.isNotEmpty) {
      try {
        await api.createRoleGroup(RoleGroup(name: nameCtl.text, displayName: displayCtl.text, description: descCtl.text));
        _loadData();
      } catch (e) {
        if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.errorFormatWith('$e')), behavior: SnackBarBehavior.floating));
      }
    }
  }

  /// Pide confirmación y elimina el grupo de roles indicado.
  Future<void> _deleteGroup(RoleGroup g) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(l10n.deleteRoleGroup),
        content: Text(l10n.deleteRoleGroupMessage(g.displayName)),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: Text(l10n.cancel)),
          FilledButton(onPressed: () => Navigator.pop(ctx, true), style: FilledButton.styleFrom(backgroundColor: Colors.red), child: Text(l10n.delete)),
        ],
      ),
    );
    if (confirm == true && g.id != null) {
      await api.deleteRoleGroup(g.id!);
      _loadData();
    }
  }

  @override
  Widget build(BuildContext context) {
    l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: Semantics(header: true, child: Text(l10n.roleGroupsManagement))),
      body: _isLoading
          ? const ListSkeleton()
          : _hasError
              ? ErrorStateWidget(onRetry: _loadData)
              : RefreshIndicator(
                  onRefresh: _loadData,
                  child: ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: _groups.length + 1,
                    itemBuilder: (ctx, i) {
                      if (i == 0) {
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 16),
                          child: Semantics(
                          label: l10n.roleGroupCount(_groups.length),
                          child: Text(l10n.roleGroupCount(_groups.length), style: theme.textTheme.bodySmall),
                          ),
                        );
                      }
                      final g = _groups[i - 1];
                      return ListItemCard(
                        leading: CircleAvatar(child: Icon(g.sortOrder == 0 ? Icons.category : Icons.group, color: Colors.white)),
                        title: g.displayName,
                        subtitle: Text(g.description ?? g.name),
                        trailing: Row(mainAxisSize: MainAxisSize.min, children: [
                          StatusIndicator(isActive: g.isActive, activeLabel: l10n.active, inactiveLabel: l10n.inactive, semanticLabel: g.isActive ? l10n.active : l10n.inactive),
                          Semantics(
                            label: '${l10n.delete} ${g.displayName}',
                            button: true,
                            child: IconButton(icon: const Icon(Icons.delete_outline, size: 20), tooltip: l10n.delete, onPressed: () => _deleteGroup(g)),
                          ),
                        ]),
                        semanticLabel: l10n.roleGroupLabel(g.displayName, g.description ?? g.name),
                      );
                    },
                  ),
                ),
      floatingActionButton: Semantics(
        label: l10n.createRoleGroup,
        button: true,
        child: FloatingActionButton(
          onPressed: _createGroup,
          tooltip: l10n.createRoleGroup,
          child: const Icon(Icons.add),
        ),
      ),
    );
  }
}
