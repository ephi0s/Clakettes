import 'package:flutter/material.dart';
import '../models/badge_model.dart';
import '../services/api_service.dart';
import 'badge_manage_sheet.dart';
import 'reusable_widgets.dart';

String badgeImageUrl(String? path) {
  if (path == null || path.isEmpty) return '';
  if (path.startsWith('http://') || path.startsWith('https://')) return path;
  return '${ApiService().rootUrl}$path';
}

class BadgeAvatar extends StatelessWidget {
  final ProfileBadge badge;
  final double radius;

  const BadgeAvatar({super.key, required this.badge, this.radius = 20});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final url = badgeImageUrl(badge.imageUrl);
    if (url.isEmpty || badge.isSvg) {
      return CircleAvatar(
        radius: radius,
        backgroundColor: colorScheme.tertiaryContainer,
        child: Icon(Icons.workspace_premium, size: radius, color: colorScheme.onTertiaryContainer),
      );
    }
    return CircleAvatar(
      radius: radius,
      backgroundColor: colorScheme.tertiaryContainer,
      backgroundImage: NetworkImage(url),
      onBackgroundImageError: (_, __) {},
    );
  }
}

class ProfileBadges extends StatefulWidget {
  final int? userId;
  final int? festivalId;
  final int? grantFestivalId;
  final bool canManage;
  final bool isAdmin;
  final String? currentUserRole;

  const ProfileBadges({
    super.key,
    this.userId,
    this.festivalId,
    this.grantFestivalId,
    this.canManage = false,
    this.isAdmin = false,
    this.currentUserRole,
  });

  @override
  State<ProfileBadges> createState() => _ProfileBadgesState();
}

class _ProfileBadgesState extends State<ProfileBadges> {
  final ApiService _api = ApiService();
  bool _enabled = false;
  bool _loading = true;
  List<BadgeAssignment> _assignments = [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final enabled = await _api.getBadgesEnabled();
      List<BadgeAssignment> items = [];
      if (enabled || widget.isAdmin) {
        if (widget.userId != null) {
          items = (await _api.getUserBadges(widget.userId!)).items;
        } else if (widget.festivalId != null) {
          items = (await _api.getFestivalBadges(widget.festivalId!)).items;
        }
      }
      if (mounted) {
        setState(() {
          _enabled = enabled;
          _assignments = items;
          _loading = false;
        });
      }
    } catch (_) {
      if (mounted) setState(() => _loading = false);
    }
  }

  void _openManage() {
    BadgeManageSheet.show(
      context,
      userId: widget.userId,
      festivalId: widget.festivalId,
      grantFestivalId: widget.grantFestivalId,
      isAdmin: widget.isAdmin,
      canManage: widget.canManage,
    ).then((_) => _load());
  }

  void _showDetail(BadgeAssignment assignment) {
    final badge = assignment.badge;
    if (badge == null) return;
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(badge.name),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(child: BadgeAvatar(badge: badge, radius: 36)),
            const SizedBox(height: 12),
            if (badge.description != null) Text(badge.description!),
            const SizedBox(height: 8),
            if (badge.category != null) Text('Categoría: ${badge.category}'),
            Text('Ámbito: ${badge.scope == 'festival' ? 'Festival' : 'Plataforma'}'),
            if (assignment.reason != null && assignment.reason!.isNotEmpty)
              Text('Motivo: ${assignment.reason}'),
            if (assignment.createdAt != null)
              Text('Otorgada: ${assignment.createdAt!.toLocal().toString().substring(0, 10)}'),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cerrar')),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const SizedBox.shrink();
    if (!_enabled && !widget.isAdmin) return const SizedBox.shrink();
    final theme = Theme.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        Row(
          children: [
            Expanded(
              child: SemanticHeader(
                text: 'Insignias${_assignments.isNotEmpty ? ' (${_assignments.length})' : ''}',
                style: theme.textTheme.titleSmall?.copyWith(color: theme.colorScheme.primary),
              ),
            ),
            if (!_enabled)
              const Chip(label: Text('Desactivadas'), visualDensity: VisualDensity.compact),
            if (widget.canManage || widget.isAdmin)
              Tooltip(
                message: 'Gestionar insignias',
                child: IconButton(icon: const Icon(Icons.settings_outlined, size: 20), onPressed: _openManage),
              ),
          ],
        ),
        if (!_enabled && widget.isAdmin)
          Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Text(
              'Solo visible para administración hasta activar la función',
              style: theme.textTheme.bodySmall?.copyWith(color: theme.colorScheme.onSurfaceVariant),
            ),
          ),
        if (_assignments.isEmpty)
          Padding(
            padding: const EdgeInsets.only(bottom: 4),
            child: Text(
              'Sin insignias todavía',
              style: theme.textTheme.bodySmall?.copyWith(color: theme.colorScheme.onSurfaceVariant),
            ),
          )
        else
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: _assignments.map((a) {
              final badge = a.badge;
              return ActionChip(
                avatar: badge != null ? BadgeAvatar(badge: badge, radius: 12) : null,
                label: Text(badge?.name ?? 'Insignia'),
                onPressed: () => _showDetail(a),
              );
            }).toList(),
          ),
      ],
    );
  }
}
