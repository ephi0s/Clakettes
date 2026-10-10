import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../models/session_model.dart';
import '../models/user_alias_model.dart';
import 'reusable_widgets.dart';

/// Tarjeta de sesiones activas con revocación individual y total.
class SessionsCard extends StatelessWidget {
  final AppLocalizations l10n;
  final List<UserSession> sessions;
  final bool loading;
  final VoidCallback onRevokeAll;
  final Future<void> Function(int sessionId) onRevoke;

  const SessionsCard({
    super.key,
    required this.l10n,
    required this.sessions,
    required this.loading,
    required this.onRevokeAll,
    required this.onRevoke,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainerLow,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: colorScheme.primaryContainer.withAlpha(100),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(Icons.devices, size: 20, color: colorScheme.primary),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text(l10n.activeSessions, style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600)),
              ),
              if (sessions.length > 1)
                TextButton.icon(
                  onPressed: onRevokeAll,
                  icon: const Icon(Icons.logout, size: 16),
                  label: Text(l10n.revokeAll),
                  style: TextButton.styleFrom(foregroundColor: colorScheme.error),
                ),
            ],
          ),
          const SizedBox(height: 12),
          if (loading)
            const Center(child: Padding(padding: EdgeInsets.all(16), child: CircularProgressIndicator(strokeWidth: 2)))
          else if (sessions.isEmpty)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 16),
              child: Center(child: Text(l10n.noActiveSessions, style: theme.textTheme.bodyMedium?.copyWith(color: colorScheme.onSurfaceVariant))),
            )
          else
            ...sessions.map((s) => _SessionItem(l10n: l10n, session: s, onRevoke: onRevoke)),
        ],
      ),
    );
  }
}

/// Fila de una sesión con dispositivo, última actividad y revocación.
class _SessionItem extends StatelessWidget {
  final AppLocalizations l10n;
  final UserSession session;
  final Future<void> Function(int sessionId) onRevoke;

  const _SessionItem({required this.l10n, required this.session, required this.onRevoke});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final deviceIcon = session.deviceName.contains('Windows') ? Icons.desktop_windows
        : session.deviceName.contains('macOS') ? Icons.desktop_mac
        : session.deviceName.contains('Android') ? Icons.phone_android
        : session.deviceName.contains('iOS') ? Icons.phone_iphone
        : Icons.devices;
    final timeAgo = DateTime.now().difference(session.lastUsedAt);
    final timeText = timeAgo.inMinutes < 1 ? l10n.timeJustNow
        : timeAgo.inMinutes < 60 ? l10n.timeMinutesAgo(timeAgo.inMinutes)
        : timeAgo.inHours < 24 ? l10n.timeHoursAgo(timeAgo.inHours)
        : l10n.timeDaysAgo(timeAgo.inDays);

    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(color: colorScheme.primaryContainer.withAlpha(100), borderRadius: BorderRadius.circular(10)),
            child: Icon(deviceIcon, size: 20, color: colorScheme.primary),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Flexible(child: Text(session.deviceName.isNotEmpty ? session.deviceName : l10n.unknownDevice, style: theme.textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.w500))),
                    if (session.isCurrent) ...[
                      const SizedBox(width: 6),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 1),
                        decoration: BoxDecoration(color: colorScheme.primary, borderRadius: BorderRadius.circular(8)),
                        child: Text(l10n.current, style: theme.textTheme.labelSmall?.copyWith(color: colorScheme.onPrimary, fontSize: 10)),
                      ),
                    ],
                  ],
                ),
                Text(l10n.lastUsed(timeText, session.ipAddress), style: theme.textTheme.bodySmall?.copyWith(color: colorScheme.onSurfaceVariant)),
              ],
            ),
          ),
          if (session.isActive && !session.isCurrent)
            IconButton(
              icon: Icon(Icons.close, size: 18, color: colorScheme.error),
              tooltip: l10n.revokeSession,
              onPressed: () => onRevoke(session.id),
            )
          else
            StatusIndicator(isActive: session.isCurrent || session.isActive, activeLabel: l10n.active, inactiveLabel: l10n.inactive),
        ],
      ),
    );
  }
}

/// Tarjeta con los alias del usuario y su gestión.
class AliasesCard extends StatelessWidget {
  final AppLocalizations l10n;
  final List<UserAlias> aliases;
  final bool loading;
  final bool canEdit;
  final bool canAdd;
  final VoidCallback onAdd;
  final Future<void> Function(UserAlias alias) onEdit;
  final Future<void> Function(UserAlias alias) onDelete;

  const AliasesCard({
    super.key,
    required this.l10n,
    required this.aliases,
    required this.loading,
    required this.canEdit,
    required this.canAdd,
    required this.onAdd,
    required this.onEdit,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainerLow,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: colorScheme.primaryContainer.withAlpha(100),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(Icons.alternate_email, size: 20, color: colorScheme.primary),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text(l10n.userAliases, style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600)),
              ),
              if (canAdd)
                TextButton.icon(
                  onPressed: onAdd,
                  icon: const Icon(Icons.add, size: 16),
                  label: Text(l10n.createAlias),
                ),
            ],
          ),
          const SizedBox(height: 12),
          if (loading)
            const Center(child: Padding(padding: EdgeInsets.all(16), child: CircularProgressIndicator(strokeWidth: 2)))
          else if (aliases.isEmpty)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 16),
              child: Center(child: Text(l10n.noAliases, style: theme.textTheme.bodyMedium?.copyWith(color: colorScheme.onSurfaceVariant))),
            )
          else
            ...aliases.map((a) => _AliasItem(l10n: l10n, alias: a, canEdit: canEdit, onEdit: onEdit, onDelete: onDelete)),
        ],
      ),
    );
  }
}

/// Fila de un alias con su contexto y acciones de edición/borrado.
class _AliasItem extends StatelessWidget {
  final AppLocalizations l10n;
  final UserAlias alias;
  final bool canEdit;
  final Future<void> Function(UserAlias alias) onEdit;
  final Future<void> Function(UserAlias alias) onDelete;

  const _AliasItem({
    required this.l10n,
    required this.alias,
    required this.canEdit,
    required this.onEdit,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(color: colorScheme.primaryContainer.withAlpha(100), borderRadius: BorderRadius.circular(10)),
            child: Icon(Icons.person_outline, size: 20, color: colorScheme.primary),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(alias.alias, style: theme.textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.w500)),
                Text('${alias.context} · ${alias.isPublic ? l10n.public : l10n.private}', style: theme.textTheme.bodySmall?.copyWith(color: colorScheme.onSurfaceVariant)),
              ],
            ),
          ),
          if (canEdit)
            Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                IconButton(
                  icon: Icon(Icons.edit, size: 18, color: colorScheme.primary),
                  tooltip: l10n.editAlias,
                  onPressed: () => onEdit(alias),
                ),
                IconButton(
                  icon: Icon(Icons.delete_outline, size: 18, color: colorScheme.error),
                  tooltip: l10n.deleteAlias,
                  onPressed: () => onDelete(alias),
                ),
              ],
            ),
        ],
      ),
    );
  }
}
