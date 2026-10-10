import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../models/notification_model.dart';
import '../services/api_service.dart';
import '../widgets/empty_state_widget.dart';
import '../widgets/error_state_widget.dart';
import '../widgets/loading_skeleton.dart';
import '../widgets/list_item_animation.dart';
import '../widgets/reusable_widgets.dart';

/// Pantalla que muestra las notificaciones de la app para el usuario actual.
///
/// Muestra una lista de notificaciones con estado leído/no leído, con la
/// posibilidad de marcar como leída, marcar todas como leídas y eliminar
/// notificaciones individuales.
class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({super.key});

  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

/// Estado de [NotificationsScreen]. Carga las notificaciones al iniciar y
/// controla el estado leído/no leído según interactúa el usuario.
class _NotificationsScreenState extends State<NotificationsScreen> {
  final ApiService _api = ApiService();
  List<AppNotification> _notifications = [];
  bool _isLoading = true;
  bool _hasError = false;
  late AppLocalizations l10n;

  @override
  void initState() {
    super.initState();
    _loadNotifications();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    l10n = AppLocalizations.of(context)!;
  }

  /// Obtiene las últimas notificaciones de la API.
  Future<void> _loadNotifications() async {
    setState(() {
      _isLoading = true;
      _hasError = false;
    });
    try {
      final result = await _api.getNotifications(size: 50);
      if (mounted) {
        setState(() {
          _notifications = result.items;
          _isLoading = false;
        });
      }
    } catch (e) {
      debugPrint('Error: $e');
      if (mounted) setState(() { _isLoading = false; _hasError = true; });
    }
  }

  /// Marca todas las notificaciones como leídas en el servidor y localmente.
  Future<void> _markAllAsRead() async {
    try {
      await _api.markAllNotificationsRead();
      if (mounted) {
        setState(() {
          _notifications = _notifications.map((n) =>
            AppNotification(
              id: n.id, userId: n.userId, title: n.title,
              message: n.message, notificationType: n.notificationType,
              isRead: true, relatedUserId: n.relatedUserId, createdAt: n.createdAt,
            )).toList();
        });
      }
    } catch (e) { debugPrint('Error: $e'); }
  }

  /// Marca una notificación como leída si todavía está sin leer.
  Future<void> _markAsRead(AppNotification notif) async {
    if (notif.isRead) return;
    try {
      await _api.markNotificationRead(notif.id);
      if (mounted) {
        setState(() {
          final idx = _notifications.indexWhere((n) => n.id == notif.id);
          if (idx != -1) {
            _notifications[idx] = AppNotification(
              id: notif.id, userId: notif.userId, title: notif.title,
              message: notif.message, notificationType: notif.notificationType,
              isRead: true, relatedUserId: notif.relatedUserId, createdAt: notif.createdAt,
            );
          }
        });
      }
    } catch (e) { debugPrint('Error: $e'); }
  }

  /// Elimina una notificación y la quita de la lista.
  Future<void> _deleteNotification(AppNotification notif) async {
    try {
      await _api.deleteNotification(notif.id);
      if (mounted) {
        setState(() => _notifications.removeWhere((n) => n.id == notif.id));
      }
    } catch (e) { debugPrint('Error: $e'); }
  }

  /// Icono usado para una notificación según su tipo.
  IconData _typeIcon(String type) {
    return switch (type) {
      'profile_update' => Icons.person_off,
      'profile_created' => Icons.person_add,
      'role_changed' => Icons.badge,
      _ => Icons.info_outline,
    };
  }

  @override
  Widget build(BuildContext context) {
    l10n = AppLocalizations.of(context)!;
    final colorScheme = Theme.of(context).colorScheme;
    final unreadCount = _notifications.where((n) => !n.isRead).length;

    return Scaffold(
      appBar: AppBar(
        title: SemanticHeader(text: l10n.notifications),
        actions: [
          if (unreadCount > 0)
            Tooltip(
              message: l10n.markAllAsRead,
              child: IconButton(
                icon: const Icon(Icons.mark_email_read),
                onPressed: _markAllAsRead,
              ),
            ),
          Tooltip(
            message: l10n.refresh,
            child: IconButton(
              icon: const Icon(Icons.refresh),
              onPressed: _loadNotifications,
            ),
          ),
        ],
      ),
      body: _buildBody(colorScheme),
    );
  }

  /// Construye el cuerpo de la pantalla según el estado de carga y datos.
  Widget _buildBody(ColorScheme colorScheme) {
    if (_isLoading) return const ListSkeleton();
    if (_hasError) return ErrorStateWidget(onRetry: _loadNotifications);
    if (_notifications.isEmpty) {
      return EmptyStateWidget(
        icon: Icons.notifications_none,
        title: l10n.noNotifications,
        subtitle: l10n.noNotificationsSubtitle,
      );
    }
    return RefreshIndicator(
      onRefresh: _loadNotifications,
      child: Semantics(
        liveRegion: true,
        label: '${l10n.notifications}: ${_notifications.length}',
        child: ListView.builder(
          padding: const EdgeInsets.only(bottom: 80, top: 8),
          itemCount: _notifications.length,
          itemBuilder: (context, index) {
            final notif = _notifications[index];
            return ListItemAnimation(
              index: index,
              child: _NotificationItem(
                notification: notif,
                icon: _typeIcon(notif.notificationType),
                onTap: () => _markAsRead(notif),
                onDelete: () => _deleteNotification(notif),
              ),
            );
          },
        ),
      ),
    );
  }
}

/// Fila de una notificación con estilo de no leída, tocar para leer y una
/// acción de borrado.
class _NotificationItem extends StatelessWidget {
  final AppNotification notification;
  final IconData icon;
  final VoidCallback onTap;
  final VoidCallback onDelete;

  const _NotificationItem({
    required this.notification,
    required this.icon,
    required this.onTap,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final l10n = AppLocalizations.of(context)!;
    final isUnread = !notification.isRead;

    return Semantics(
      label: '${notification.title}: ${notification.message}',
      child: Card(
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
        color: isUnread ? colorScheme.primaryContainer.withAlpha(30) : null,
        child: ListTile(
          leading: CircleAvatar(
            backgroundColor: isUnread ? colorScheme.primary : colorScheme.surfaceContainerHighest,
            child: Icon(icon, color: isUnread ? colorScheme.onPrimary : colorScheme.onSurfaceVariant, size: 20),
          ),
          title: Text(
            notification.title,
            style: TextStyle(fontWeight: isUnread ? FontWeight.bold : FontWeight.normal),
          ),
          subtitle: Text(
            notification.message,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
          trailing: PopupMenuButton<String>(
            onSelected: (value) {
              if (value == 'delete') onDelete();
            },
            itemBuilder: (context) => [
              PopupMenuItem(value: 'delete', child: Text(l10n.delete)),
            ],
          ),
          onTap: onTap,
        ),
      ),
    );
  }
}
