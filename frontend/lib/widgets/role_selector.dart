import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../models/role_model.dart';
import '../services/api_service.dart';

class RolePickerSheet extends StatefulWidget {
  final List<String> selected;
  final ValueChanged<List<String>> onSelected;
  final bool allowMultiple;

  const RolePickerSheet({
    super.key,
    this.selected = const [],
    required this.onSelected,
    this.allowMultiple = false,
  });

  static Future<void> show(
    BuildContext context,
    List<String> selected,
    ValueChanged<List<String>> onSelected, {
    bool allowMultiple = false,
  }) {
    return showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (_) => DraggableScrollableSheet(
        expand: false,
        builder: (_, controller) => RolePickerSheet(
          selected: selected,
          onSelected: onSelected,
          allowMultiple: allowMultiple,
        ),
      ),
    );
  }

  @override
  State<RolePickerSheet> createState() => _RolePickerSheetState();
}

class _RolePickerSheetState extends State<RolePickerSheet> {
  late List<String> _selected;
  List<RoleSummary> _roles = const [];
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _selected = List.of(widget.selected);
    _load();
  }

  Future<void> _load() async {
    try {
      final roles = await ApiService().getRoles();
      if (!mounted) return;
      setState(() {
        _roles = roles;
        _loading = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _error = 'error';
      });
    }
  }

  void _toggle(String name) {
    setState(() {
      if (widget.allowMultiple) {
        if (_selected.contains(name)) {
          _selected.remove(name);
        } else {
          _selected.add(name);
        }
      } else {
        _selected = [name];
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    return Semantics(
      label: 'Roles',
      child: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: _loading
                  ? const Center(child: CircularProgressIndicator())
                  : _error != null
                      ? Center(child: Text(_error!))
                      : widget.allowMultiple
                          ? ListView.builder(
                              itemCount: _roles.length,
                              itemBuilder: (context, i) {
                                final role = _roles[i];
                                final label =
                                    l10n?.getRoleTranslation(role.name) ??
                                        role.displayName;
                                final isSelected =
                                    _selected.contains(role.name);
                                return Semantics(
                                  selected: isSelected,
                                  button: true,
                                  label: label,
                                  child: CheckboxListTile(
                                    value: isSelected,
                                    title: Text(label),
                                    subtitle: role.description != null
                                        ? Text(role.description!)
                                        : null,
                                    onChanged: (_) => _toggle(role.name),
                                  ),
                                );
                              },
                            )
                          : RadioGroup<String>(
                              groupValue: _selected.isEmpty
                                  ? null
                                  : _selected.first,
                              onChanged: (v) {
                                if (v != null) _toggle(v);
                              },
                              child: ListView.builder(
                                itemCount: _roles.length,
                                itemBuilder: (context, i) {
                                  final role = _roles[i];
                                  final label =
                                      l10n?.getRoleTranslation(role.name) ??
                                          role.displayName;
                                  return Semantics(
                                    selected:
                                        _selected.contains(role.name),
                                    button: true,
                                    label: label,
                                    child: RadioListTile<String>(
                                      value: role.name,
                                      title: Text(label),
                                      subtitle: role.description != null
                                          ? Text(role.description!)
                                          : null,
                                    ),
                                  );
                                },
                              ),
                            ),
            ),
            Padding(
              padding: const EdgeInsets.all(16),
              child: FilledButton(
                onPressed: _selected.isEmpty
                    ? null
                    : () {
                        widget.onSelected(List.of(_selected));
                        Navigator.of(context).pop();
                      },
                child: const Text('OK'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class UserRolesCard extends StatefulWidget {
  final int userId;
  final VoidCallback? onChanged;

  const UserRolesCard({super.key, required this.userId, this.onChanged});

  @override
  State<UserRolesCard> createState() => _UserRolesCardState();
}

class _UserRolesCardState extends State<UserRolesCard> {
  List<Map<String, dynamic>> _roles = const [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final roles = await ApiService().getUserRoles(widget.userId);
      if (!mounted) return;
      setState(() {
        _roles = roles;
        _loading = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() => _loading = false);
    }
  }

  int? _roleId(Map<String, dynamic> ur) {
    for (final key in ['id', 'user_role_id', 'userRoleId']) {
      final v = ur[key];
      if (v is int) return v;
    }
    return null;
  }

  String _roleName(Map<String, dynamic> ur) {
    final nested = ur['role'];
    if (nested is Map && nested['name'] != null) {
      return nested['name'].toString();
    }
    return (ur['role_name'] ?? ur['name'] ?? '').toString();
  }

  bool _isPrimary(Map<String, dynamic> ur) {
    return ur['is_primary'] == true || ur['isPrimary'] == true;
  }

  Future<void> _remove(Map<String, dynamic> ur) async {
    final id = _roleId(ur);
    if (id == null) return;
    await ApiService().removeUserRole(widget.userId, id);
    widget.onChanged?.call();
    await _load();
  }

  Future<void> _add() async {
    await RolePickerSheet.show(context, const [], (names) async {
      if (names.isEmpty) return;
      await ApiService()
          .assignUserRole(widget.userId, {'role_name': names.first});
      widget.onChanged?.call();
      await _load();
    });
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    return Semantics(
      container: true,
      label: 'Roles',
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Expanded(child: Text('Roles')),
                  IconButton(
                    tooltip: 'Add',
                    icon: const Icon(Icons.add_outlined),
                    onPressed: _add,
                  ),
                ],
              ),
              if (_loading)
                const Center(child: CircularProgressIndicator())
              else
                for (final ur in _roles)
                  ListTile(
                    title: Text(l10n?.getRoleTranslation(_roleName(ur)) ??
                        _roleName(ur)),
                    trailing: Wrap(
                      spacing: 4,
                      crossAxisAlignment: WrapCrossAlignment.center,
                      children: [
                        if (_isPrimary(ur)) const Chip(label: Text('★')),
                        IconButton(
                          tooltip: 'Delete',
                          icon: const Icon(Icons.delete_outline),
                          onPressed: () => _remove(ur),
                        ),
                      ],
                    ),
                  ),
            ],
          ),
        ),
      ),
    );
  }
}
