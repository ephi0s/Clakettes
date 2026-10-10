import 'package:flutter/material.dart';

import '../l10n/app_localizations.dart';
import '../models/calendar_model.dart';
import '../models/role_model.dart';

/// Selector de alcance de visibilidad de un evento en la agenda compartida.
///
/// Devuelve el alcance elegido mediante [onChanged]; cuando el alcance es
/// [EventVisibilityScope.roles], también informa de los roles seleccionados.
/// Si el festival no tiene roles configurados, se avisa en lugar de dejar el
/// selector en un estado que el backend no puede aplicar.
class EventVisibilityPicker extends StatelessWidget {
  final EventVisibilityScope scope;
  final Set<int> roleIds;
  final List<RoleSummary> roles;
  final ValueChanged<EventVisibilityScope> onScopeChanged;
  final ValueChanged<Set<int>> onRolesChanged;

  const EventVisibilityPicker({
    super.key,
    required this.scope,
    required this.roleIds,
    required this.roles,
    required this.onScopeChanged,
    required this.onRolesChanged,
  });

  /// Traduce el valor del enumerado a la clave de localización correspondiente.
  String _label(AppLocalizations l10n, EventVisibilityScope value) {
    switch (value) {
      case EventVisibilityScope.public:
        return l10n.visibilityPublic;
      case EventVisibilityScope.festivalMembers:
        return l10n.visibilityFestivalMembers;
      case EventVisibilityScope.roles:
        return l10n.visibilityRoles;
      case EventVisibilityScope.attendeesOnly:
        return l10n.visibilityAttendeesOnly;
    }
  }

  IconData _icon(EventVisibilityScope value) {
    switch (value) {
      case EventVisibilityScope.public:
        return Icons.public;
      case EventVisibilityScope.festivalMembers:
        return Icons.groups_outlined;
      case EventVisibilityScope.roles:
        return Icons.badge_outlined;
      case EventVisibilityScope.attendeesOnly:
        return Icons.confirmation_number_outlined;
    }
  }

  void _toggleRole(int id) {
    final next = Set<int>.from(roleIds);
    if (!next.remove(id)) next.add(id);
    onRolesChanged(next);
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Semantics(
          header: true,
          child: Text(l10n.visibility, style: theme.textTheme.titleSmall),
        ),
        const SizedBox(height: 4),
        Text(
          l10n.visibilityDescription,
          style: theme.textTheme.bodySmall?.copyWith(color: theme.colorScheme.onSurfaceVariant),
        ),
        const SizedBox(height: 8),
        RadioGroup<EventVisibilityScope>(
          groupValue: scope,
          onChanged: (v) {
            if (v != null) onScopeChanged(v);
          },
          child: Column(
            children: [
              for (final value in EventVisibilityScope.values)
                Semantics(
                  container: true,
                  selected: scope == value,
                  child: RadioListTile<EventVisibilityScope>(
                    value: value,
                    dense: true,
                    contentPadding: EdgeInsets.zero,
                    title: Text(_label(l10n, value)),
                    secondary: Icon(_icon(value), size: 20),
                  ),
                ),
            ],
          ),
        ),
        if (scope == EventVisibilityScope.roles) ...[
          const SizedBox(height: 8),
          if (roles.isEmpty)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 4),
              child: Text(
                l10n.noRolesSelected,
                style: theme.textTheme.bodySmall?.copyWith(color: theme.colorScheme.error),
              ),
            )
          else ...[
            Padding(
              padding: const EdgeInsets.fromLTRB(4, 0, 4, 4),
              child: Text(l10n.selectRoles, style: theme.textTheme.labelLarge),
            ),
            for (final role in roles)
              Semantics(
                container: true,
                checked: roleIds.contains(role.id),
                label: role.displayName,
                child: CheckboxListTile(
                  value: roleIds.contains(role.id),
                  onChanged: (_) => _toggleRole(role.id),
                  dense: true,
                  contentPadding: EdgeInsets.zero,
                  title: Text(role.displayName),
                  subtitle: (role.description ?? '').isEmpty ? null : Text(role.description!),
                ),
              ),
          ],
        ],
      ],
    );
  }
}