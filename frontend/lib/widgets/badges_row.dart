import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../models/badge_model.dart';
import '../services/api_service.dart';
import 'badge_manage_sheet.dart';
import 'reusable_widgets.dart';

String badgeImageUrl(String? path) => resolveMediaUrl(path);

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
  AppLocalizations get l10n => AppLocalizations.of(context)!;
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
            if (badge.category != null) Text(l10n.translate('badgeCategoryLabel', args: {'category': badge.category})),
            Text(l10n.translate('badgeScopeLabel', args: {'scope': badge.scope == 'festival' ? l10n.typeFestival : l10n.badgePlatform})),
            if (assignment.reason != null && assignment.reason!.isNotEmpty)
              Text(l10n.translate('badgeReasonLabel', args: {'reason': assignment.reason})),
            if (assignment.createdAt != null)
              Text(l10n.translate('badgeGrantedAt', args: {'date': assignment.createdAt!.toLocal().toString().substring(0, 10)})),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: Text(l10n.close)),
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
                text: '${l10n.badgeTitle}${_assignments.isNotEmpty ? ' (${_assignments.length})' : ''}',
                style: theme.textTheme.titleSmall?.copyWith(color: theme.colorScheme.primary),
              ),
            ),
            if (!_enabled)
              Chip(label: Text(l10n.badgeDisabledChip), visualDensity: VisualDensity.compact),
            if (widget.canManage || widget.isAdmin)
              Tooltip(
                message: l10n.badgeManage,
                child: IconButton(icon: const Icon(Icons.settings_outlined, size: 20), onPressed: _openManage),
              ),
          ],
        ),
        if (!_enabled && widget.isAdmin)
          Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Text(
              l10n.badgeAdminOnlyHint,
              style: theme.textTheme.bodySmall?.copyWith(color: theme.colorScheme.onSurfaceVariant),
            ),
          ),
        if (_assignments.isEmpty)
          Padding(
            padding: const EdgeInsets.only(bottom: 4),
            child: Text(
              l10n.badgeNoneYet,
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
                label: Text(badge?.name ?? l10n.badgeLabel),
                onPressed: () => _showDetail(a),
              );
            }).toList(),
          ),
      ],
    );
  }
}
