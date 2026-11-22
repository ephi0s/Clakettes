import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../models/badge_model.dart';
import '../services/api_service.dart';
import 'badges_row.dart';
import 'reusable_widgets.dart';

class BadgeManageSheet extends StatefulWidget {
  final int? userId;
  final int? festivalId;
  final int? grantFestivalId;
  final bool isAdmin;
  final bool canManage;

  const BadgeManageSheet({
    super.key,
    this.userId,
    this.festivalId,
    this.grantFestivalId,
    this.isAdmin = false,
    this.canManage = false,
  });

  static Future<void> show(
    BuildContext context, {
    int? userId,
    int? festivalId,
    int? grantFestivalId,
    bool isAdmin = false,
    bool canManage = false,
  }) {
    return showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(24))),
      builder: (_) => DraggableScrollableSheet(
        expand: false,
        initialChildSize: 0.9,
        builder: (_, controller) => BadgeManageSheet(
          userId: userId,
          festivalId: festivalId,
          grantFestivalId: grantFestivalId,
          isAdmin: isAdmin,
          canManage: canManage,
        ),
      ),
    );
  }

  @override
  State<BadgeManageSheet> createState() => _BadgeManageSheetState();
}

class _BadgeManageSheetState extends State<BadgeManageSheet> {
  final ApiService _api = ApiService();
  AppLocalizations get l10n => AppLocalizations.of(context)!;
  bool _enabled = false;
  bool _loading = true;
  List<ProfileBadge> _badges = [];
  List<BadgeAssignment> _assignments = [];
  int? _selectedBadgeId;
  String? _eligibility;
  bool _busy = false;

  final _nameCtl = TextEditingController();
  final _descCtl = TextEditingController();
  final _reasonCtl = TextEditingController();
  String _scope = 'platform';
  String _category = 'merit';
  String _conditionType = 'manual';
  final _minFestivalsCtl = TextEditingController(text: '3');
  final _roleCtl = TextEditingController(text: 'organizer');
  PlatformFile? _pickedImage;

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _nameCtl.dispose();
    _descCtl.dispose();
    _reasonCtl.dispose();
    _minFestivalsCtl.dispose();
    _roleCtl.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    try {
      final enabled = await _api.getBadgesEnabled();
      final badges = (await _api.getBadges(size: 100)).items;
      List<BadgeAssignment> assignments = [];
      if (widget.userId != null) {
        assignments = (await _api.getUserBadges(widget.userId!)).items;
      } else if (widget.festivalId != null) {
        assignments = (await _api.getFestivalBadges(widget.festivalId!)).items;
      }
      if (mounted) {
        setState(() {
          _enabled = enabled;
          _badges = badges;
          _assignments = assignments;
          _loading = false;
          _selectedBadgeId ??= badges.isNotEmpty ? badges.first.id : null;
        });
      }
      _refreshEligibility();
    } catch (_) {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _refreshEligibility() async {
    if (_selectedBadgeId == null || widget.userId == null) {
      if (mounted) setState(() => _eligibility = null);
      return;
    }
    try {
      final result = await _api.checkBadgeEligibility(_selectedBadgeId!, widget.userId!);
      if (mounted) {
        setState(() => _eligibility = result['eligible'] == true
            ? l10n.translate('badgeConditionsMet', args: {'reason': result['reason'] ?? ''})
            : l10n.translate('badgeConditionsNotMet', args: {'reason': result['reason'] ?? ''}));
      }
    } catch (_) {
      if (mounted) setState(() => _eligibility = null);
    }
  }

  Future<void> _toggleEnabled(bool value) async {
    setState(() => _busy = true);
    try {
      final enabled = await _api.setBadgesEnabled(value);
      if (mounted) {
        setState(() => _enabled = enabled);
        showAppSnack(context, enabled ? l10n.badgeEnabled : l10n.badgeDisabled);
      }
    } catch (_) {
      if (mounted) showAppSnack(context, l10n.badgeToggleFailed);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Map<String, dynamic>? _buildConditions() {
    if (_conditionType == 'manual') return {'type': 'manual'};
    if (_conditionType == 'veteran') {
      return {'type': 'veteran', 'min_festivals': int.tryParse(_minFestivalsCtl.text) ?? 3};
    }
    if (_conditionType == 'role') {
      return {'type': 'role', 'role': _roleCtl.text.trim().toLowerCase()};
    }
    if (_conditionType == 'award') return {'type': 'award'};
    return {'type': 'manual'};
  }

  Future<void> _pickImage() async {
    final files = await FilePicker.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['svg', 'png', 'jpg', 'jpeg', 'webp'],
    );
    if (files.isNotEmpty) {
      setState(() => _pickedImage = files.single);
    }
  }

  Future<void> _createBadge() async {
    if (_nameCtl.text.trim().isEmpty || _busy) return;
    setState(() => _busy = true);
    try {
      final fields = <String, dynamic>{
        'name': _nameCtl.text.trim(),
        if (_descCtl.text.trim().isNotEmpty) 'description': _descCtl.text.trim(),
        'scope': _scope,
        'category': _category,
        'conditions': _buildConditions(),
        if (_scope == 'festival' && (widget.grantFestivalId ?? widget.festivalId) != null)
          'festival_id': widget.grantFestivalId ?? widget.festivalId,
      };
      var badge = await _api.createBadge(fields);
      if (_pickedImage != null && badge.id != null) {
        try {
          badge = await _api.uploadBadgeImage(badge.id!, platformFileToXFile(_pickedImage!));
        } catch (_) {
          await _api.deleteBadge(badge.id!);
          rethrow;
        }
      }
      if (mounted) {
        setState(() {
          _nameCtl.clear();
          _descCtl.clear();
          _pickedImage = null;
        });
        showAppSnack(context, l10n.badgeCreated);
      }
      _load();
    } catch (e) {
      if (mounted) showAppSnack(context, l10n.badgeCreateFailed);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _assign() async {
    if (_selectedBadgeId == null || _busy) return;
    setState(() => _busy = true);
    try {
      final fields = <String, dynamic>{
        if (widget.userId != null) 'target_user_id': widget.userId,
        if (widget.festivalId != null) 'target_festival_id': widget.festivalId,
        if ((widget.grantFestivalId ?? widget.festivalId) != null && widget.userId != null)
          'grant_festival_id': widget.grantFestivalId ?? widget.festivalId,
        if (_reasonCtl.text.trim().isNotEmpty) 'reason': _reasonCtl.text.trim(),
      };
      await _api.assignBadge(_selectedBadgeId!, fields);
      if (mounted) {
        _reasonCtl.clear();
        showAppSnack(context, l10n.badgeGranted);
      }
      _load();
    } catch (_) {
      if (mounted) showAppSnack(context, l10n.badgeGrantFailed);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _removeAssignment(BadgeAssignment assignment) async {
    if (assignment.id == null) return;
    try {
      await _api.deleteBadgeAssignment(assignment.id!);
      _load();
    } catch (_) {
      if (mounted) showAppSnack(context, l10n.badgeRevokeFailed);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    if (_loading) {
      return const Padding(padding: EdgeInsets.all(32), child: Center(child: CircularProgressIndicator()));
    }
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SemanticHeader(text: l10n.badgeTitle, style: theme.textTheme.titleLarge),
          if (widget.isAdmin) ...[
            const SizedBox(height: 8),
            SwitchListTile(
              title: Text(l10n.badgeFeatureActive),
              subtitle: Text(l10n.badgeFeatureAdminOnly),
              value: _enabled,
              onChanged: _busy ? null : _toggleEnabled,
              contentPadding: EdgeInsets.zero,
            ),
          ],
          if (!_enabled && !widget.isAdmin)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 12),
              child: Text(l10n.badgeFeatureOff),
            ),
          if (_enabled || widget.isAdmin) ...[
            const SizedBox(height: 8),
            SemanticHeader(text: l10n.badgeGrantToProfile, style: theme.textTheme.titleSmall),
            if (_badges.isEmpty)
              Text(l10n.badgeNoneCreated)
            else ...[
              DropdownButtonFormField<int>(
                initialValue: _selectedBadgeId,
                decoration: InputDecoration(labelText: l10n.badgeLabel, border: const OutlineInputBorder()),
                items: _badges.map((b) => DropdownMenuItem(value: b.id, child: Text(b.name))).toList(),
                onChanged: (v) {
                  setState(() => _selectedBadgeId = v);
                  _refreshEligibility();
                },
              ),
              if (_eligibility != null) ...[
                const SizedBox(height: 4),
                Text(_eligibility!, style: theme.textTheme.bodySmall),
              ],
              const SizedBox(height: 8),
              TextField(
                controller: _reasonCtl,
                decoration: InputDecoration(labelText: l10n.badgeReasonOptional, border: const OutlineInputBorder()),
                maxLines: 2,
              ),
              const SizedBox(height: 8),
              FilledButton.icon(
                onPressed: _busy ? null : _assign,
                icon: const Icon(Icons.verified_outlined, size: 18),
                label: Text(l10n.badgeGrant),
              ),
            ],
            const SizedBox(height: 16),
            SemanticHeader(text: l10n.translate('badgeOnProfile', args: {'count': _assignments.length}), style: theme.textTheme.titleSmall),
            ..._assignments.map((a) => ListTile(
                  contentPadding: EdgeInsets.zero,
                  leading: a.badge != null ? BadgeAvatar(badge: a.badge!) : null,
                  title: Text(a.badge?.name ?? l10n.badgeLabel),
                  subtitle: a.reason != null ? Text(a.reason!, maxLines: 1, overflow: TextOverflow.ellipsis) : null,
                  trailing: (widget.isAdmin || widget.canManage)
                      ? IconButton(icon: const Icon(Icons.delete_outline, size: 20), tooltip: l10n.badgeRevoke, onPressed: () => _removeAssignment(a))
                      : null,
                )),
            if (widget.isAdmin) ...[
              const Divider(height: 32),
              SemanticHeader(text: l10n.badgeCreate, style: theme.textTheme.titleSmall),
              const SizedBox(height: 8),
              TextField(controller: _nameCtl, decoration: InputDecoration(labelText: l10n.nameRequired, border: const OutlineInputBorder())),
              const SizedBox(height: 8),
              TextField(controller: _descCtl, decoration: InputDecoration(labelText: l10n.description, border: const OutlineInputBorder()), maxLines: 2),
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: DropdownButtonFormField<String>(
                      initialValue: _scope,
                      decoration: InputDecoration(labelText: l10n.badgeScope, border: const OutlineInputBorder()),
                      items: [DropdownMenuItem(value: 'platform', child: Text(l10n.badgePlatform)), DropdownMenuItem(value: 'festival', child: Text(l10n.typeFestival))],
                      onChanged: (v) => setState(() => _scope = v ?? 'platform'),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: DropdownButtonFormField<String>(
                      initialValue: _category,
                      decoration: InputDecoration(labelText: l10n.category, border: const OutlineInputBorder()),
                      items: [
                        DropdownMenuItem(value: 'merit', child: Text(l10n.badgeMerit)),
                        DropdownMenuItem(value: 'veteran', child: Text(l10n.badgeVeteran)),
                        DropdownMenuItem(value: 'popular', child: Text(l10n.badgePopular)),
                        DropdownMenuItem(value: 'role', child: Text(l10n.role)),
                        DropdownMenuItem(value: 'special', child: Text(l10n.badgeSpecial)),
                      ],
                      onChanged: (v) => setState(() => _category = v ?? 'merit'),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              DropdownButtonFormField<String>(
                initialValue: _conditionType,
                decoration: InputDecoration(labelText: l10n.badgeCondition, border: const OutlineInputBorder()),
                items: [
                  DropdownMenuItem(value: 'manual', child: Text(l10n.badgeConditionManual)),
                  DropdownMenuItem(value: 'veteran', child: Text(l10n.badgeConditionVeteran)),
                  DropdownMenuItem(value: 'role', child: Text(l10n.badgeConditionRole)),
                  DropdownMenuItem(value: 'award', child: Text(l10n.badgeConditionAwarded)),
                ],
                onChanged: (v) => setState(() => _conditionType = v ?? 'manual'),
              ),
              if (_conditionType == 'veteran') ...[
                const SizedBox(height: 8),
                TextField(controller: _minFestivalsCtl, keyboardType: TextInputType.number, decoration: InputDecoration(labelText: l10n.badgeMinFestivals, border: const OutlineInputBorder())),
              ],
              if (_conditionType == 'role') ...[
                const SizedBox(height: 8),
                TextField(controller: _roleCtl, decoration: InputDecoration(labelText: l10n.badgeRequiredRole, border: const OutlineInputBorder())),
              ],
              const SizedBox(height: 8),
              OutlinedButton.icon(
                onPressed: _pickImage,
                icon: const Icon(Icons.upload_outlined, size: 18),
                label: Text(_pickedImage == null ? l10n.badgeUploadImage : _pickedImage!.name),
              ),
              const SizedBox(height: 8),
              FilledButton.icon(
                onPressed: _busy ? null : _createBadge,
                icon: const Icon(Icons.add, size: 18),
                label: Text(l10n.badgeCreate),
              ),
              const SizedBox(height: 24),
            ],
          ],
        ],
      ),
    );
  }
}
