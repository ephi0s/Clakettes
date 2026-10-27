import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:url_launcher/url_launcher.dart';
import '../l10n/app_localizations.dart';
import '../models/user_model.dart';
import '../models/session_model.dart';
import '../models/user_alias_model.dart';
import '../services/api_service.dart';
import '../services/locale_service.dart';
import '../widgets/reusable_widgets.dart';
import '../widgets/user_profile_cards.dart';
import '../widgets/confirm_dialog.dart';
import '../widgets/dav_subscription_section.dart';
import '../widgets/language_picker.dart';
import '../services/auth_service.dart';
import '../services/offline_cache_service.dart';
import '../services/sync_queue_service.dart';
import '../widgets/open_in_maps_action.dart';
import '../widgets/publication_panel.dart';
import '../widgets/badges_row.dart';
import '../main_scaffold.dart';

class UserProfileScreen extends StatefulWidget {
  final User user;
  final User? currentUser;

  const UserProfileScreen({super.key, required this.user, this.currentUser});

  @override
  State<UserProfileScreen> createState() => _UserProfileScreenState();
}

class _UserProfileScreenState extends State<UserProfileScreen> {
  late User _user;
  late TextEditingController _fullNameController;
  late TextEditingController _bioController;
  late TextEditingController _emailController;
  late TextEditingController _taglineController;
  late TextEditingController _bannerController;
  late TextEditingController _avatarController;
  Map<String, String> _socialLinks = {};
  late TextEditingController _websiteController;
  late TextEditingController _instagramController;
  late TextEditingController _xController;
  late TextEditingController _youtubeController;
  final _formKey = GlobalKey<FormState>();
  bool _isEditing = false;
  bool _isSaving = false;
  late bool _isPublic;
  late bool _isPublicEmail;
  late bool _isPublicBio;
  late bool _isPublicLocation;
  late AppLocalizations l10n;

  List<UserSession> _sessions = [];
  bool _sessionsLoading = false;
  List<UserAlias> _aliases = [];
  bool _aliasesLoading = false;
  User? _fetchedCurrentUser;
  List<dynamic> _userRoles = [];
  List<dynamic> _palmares = [];
  List<String> _availableRoles = ['admin', 'organizer', 'user', 'jury'];

  bool get _isOwnProfile => (_fetchedCurrentUser ?? widget.currentUser)?.id == _user.id;
  bool get _canEdit {
    final cu = _fetchedCurrentUser ?? widget.currentUser;
    if (cu == null) return false;
    if (_isOwnProfile) return true;
    if (cu.role == 'admin') return true;
    if (cu.role == 'organizer') return true;
    return false;
  }
  bool get _canDelete {
    final cu = _fetchedCurrentUser ?? widget.currentUser;
    if (cu == null) return false;
    final role = cu.role;
    if (role == 'admin') return true;
    if (role == 'organizer') return true;
    return false;
  }
  bool get _canModerateWall {
    final cu = _fetchedCurrentUser ?? widget.currentUser;
    if (cu == null) return false;
    if (_isOwnProfile) return true;
    if (cu.role == 'admin') return true;
    return false;
  }
  bool get _isAdmin => (_fetchedCurrentUser ?? widget.currentUser)?.role == 'admin';

  String get _bannerUrl {
    try {
      final v = (widget.user as dynamic).bannerUrl as String?;
      if (v != null && v.isNotEmpty) return v;
    } catch (_) {}
    return _bannerController.text.trim();
  }

  String get _tagline {
    try {
      final v = (widget.user as dynamic).tagline as String?;
      if (v != null && v.isNotEmpty) return v;
    } catch (_) {}
    return _taglineController.text.trim();
  }

  @override
  void initState() {
    super.initState();
    _user = widget.user;
    _fullNameController = TextEditingController(text: _user.fullName ?? '');
    _bioController = TextEditingController(text: _user.bio ?? '');
    _emailController = TextEditingController(text: _user.email ?? '');
    String taglineInit = '';
    String bannerInit = '';
    String avatarInit = _user.avatarUrl ?? '';
    Map<String, String> socialInit = {};
    try {
      final d = _user as dynamic;
      try {
        final t = d.tagline as String?;
        if (t != null) taglineInit = t;
      } catch (_) {}
      try {
        final b = d.bannerUrl as String?;
        if (b != null) bannerInit = b;
      } catch (_) {}
      try {
        final s = d.socialLinks;
        if (s is Map) {
          for (final e in s.entries) {
            socialInit[e.key.toString()] = e.value.toString();
          }
        }
      } catch (_) {}
    } catch (_) {}
    _taglineController = TextEditingController(text: taglineInit);
    _bannerController = TextEditingController(text: bannerInit);
    _avatarController = TextEditingController(text: avatarInit);
    _socialLinks = socialInit;
    _websiteController = TextEditingController(text: socialInit['website'] ?? '');
    _instagramController = TextEditingController(text: socialInit['instagram'] ?? '');
    _xController = TextEditingController(text: socialInit['x'] ?? socialInit['twitter'] ?? '');
    _youtubeController = TextEditingController(text: socialInit['youtube'] ?? '');
    _isPublic = _user.isPublic;
    _isPublicEmail = _user.isPublicEmail;
    _isPublicBio = _user.isPublicBio;
    _isPublicLocation = _user.isPublicLocation;
    _loadCurrentUserIfNeeded();
    _loadExtras();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    l10n = AppLocalizations.of(context)!;
  }

  @override
  void dispose() {
    _fullNameController.dispose();
    _bioController.dispose();
    _emailController.dispose();
    _taglineController.dispose();
    _bannerController.dispose();
    _avatarController.dispose();
    _websiteController.dispose();
    _instagramController.dispose();
    _xController.dispose();
    _youtubeController.dispose();
    super.dispose();
  }

  Future<void> _openInMaps(double lat, double lng, String label) =>
      openInMaps(lat, lng, label: label);

  Map<String, String> _collectSocialLinks() {
    final m = <String, String>{};
    if (_websiteController.text.trim().isNotEmpty) m['website'] = _websiteController.text.trim();
    if (_instagramController.text.trim().isNotEmpty) m['instagram'] = _instagramController.text.trim();
    if (_xController.text.trim().isNotEmpty) m['x'] = _xController.text.trim();
    if (_youtubeController.text.trim().isNotEmpty) m['youtube'] = _youtubeController.text.trim();
    for (final e in _socialLinks.entries) {
      if (!m.containsKey(e.key) && e.value.trim().isNotEmpty) m[e.key] = e.value.trim();
    }
    return m;
  }

  Future<void> _saveProfile() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _isSaving = true);
    try {
      final updated = await ApiService().updateUser(_user.id!, {
        'full_name': _fullNameController.text.isNotEmpty ? _fullNameController.text.trim() : null,
        if (_emailController.text.trim().isNotEmpty) 'email': _emailController.text.trim(),
        'bio': _bioController.text.isNotEmpty ? _bioController.text.trim() : null,
        'avatar_url': _avatarController.text.trim().isNotEmpty ? _avatarController.text.trim() : null,
        'banner_url': _bannerController.text.trim().isNotEmpty ? _bannerController.text.trim() : null,
        'tagline': _taglineController.text.trim().isNotEmpty ? _taglineController.text.trim() : null,
        'social_links': _collectSocialLinks(),
        'is_public': _isPublic,
        'is_public_email': _isPublicEmail,
        'is_public_bio': _isPublicBio,
        'is_public_location': _isPublicLocation,
      });
      if (mounted) {
        setState(() {
          _user = updated;
          _socialLinks = _collectSocialLinks();
          _isEditing = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.profileUpdated), behavior: SnackBarBehavior.floating),
        );
      }
    } catch (e) {
      debugPrint('Error: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.loadError), behavior: SnackBarBehavior.floating),
        );
      }
    } finally {
      if (mounted) setState(() => _isSaving = false);
    }
  }

  Future<void> _deleteUser() async {
    final confirmed = await showConfirmDialog(context, title: l10n.delete, message: l10n.confirmDelete);
    if (!confirmed) return;
    try {
      await ApiService().deleteUser(_user.id!);
      if (mounted) Navigator.pop(context, true);
    } catch (e) {
      debugPrint('Error: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.loadError), behavior: SnackBarBehavior.floating),
        );
      }
    }
  }

  Future<void> _loadCurrentUserIfNeeded() async {
    if (widget.currentUser == null) {
      final user = await AuthService().getCurrentUser();
      if (mounted) setState(() => _fetchedCurrentUser = user);
    }
    if (mounted && _isOwnProfile) _loadSessions();
    if (mounted) _loadAliases();
  }

  Future<void> _loadExtras() async {
    await _loadAvailableRoles();
    await _loadUserRoles();
    await _loadPalmares();
  }

  Future<void> _loadAvailableRoles() async {
    try {
      final data = await ApiService().request('GET', '/roles/');
      final items = data is List ? data : (data is Map && data['items'] is List ? data['items'] as List : <dynamic>[]);
      if (items.isNotEmpty && mounted) {
        setState(() {
          _availableRoles = items.map((e) {
            if (e is Map) {
              final d = (e['display_name'] ?? e['displayName'] ?? e['name'])?.toString();
              return d ?? 'user';
            }
            return e.toString();
          }).toList();
        });
      }
    } catch (_) {}
  }

  Future<void> _loadUserRoles() async {
    final id = _user.id;
    if (id == null) return;
    try {
      dynamic data;
      try {
        data = await (ApiService() as dynamic).getUserRoles(id);
      } catch (_) {
        data = await ApiService().request('GET', '/users/$id/roles/');
      }
      final items = data is List ? data : (data is Map && data['items'] is List ? data['items'] as List : <dynamic>[]);
      if (mounted) setState(() => _userRoles = items);
    } catch (_) {}
  }

  Future<void> _loadPalmares() async {
    final id = _user.id;
    if (id == null) return;
    try {
      final data = await ApiService().request('GET', '/users/$id/awards/');
      final items = data is List ? data : (data is Map && data['items'] is List ? data['items'] as List : <dynamic>[]);
      if (mounted) setState(() => _palmares = items);
    } catch (_) {}
  }

  String _roleLabel(dynamic r) {
    if (r is Map) {
      final raw = (r['role'] ?? r['name'] ?? r['display_name'] ?? r['displayName'] ?? '').toString();
      try {
        return l10n.getRoleTranslation(raw);
      } catch (_) {
        return raw.isNotEmpty ? raw : r.toString();
      }
    }
    try {
      return l10n.getRoleTranslation(r.toString());
    } catch (_) {
      return r.toString();
    }
  }

  Future<void> _showRoleDialog() async {
    String? selected;
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setD) => AlertDialog(
          title: const Text('Asignar rol'),
          content: DropdownButtonFormField<String>(
            initialValue: selected,
            decoration: const InputDecoration(labelText: 'Rol', border: OutlineInputBorder()),
            items: _availableRoles.map((r) {
              String label;
              try {
                label = l10n.getRoleTranslation(r);
              } catch (_) {
                label = r;
              }
              return DropdownMenuItem(value: r, child: Text(label));
            }).toList(),
            onChanged: (v) => setD(() => selected = v),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx, false), child: Text(l10n.cancel)),
            ElevatedButton(onPressed: () => Navigator.pop(ctx, true), child: Text(l10n.save)),
          ],
        ),
      ),
    );
    if (ok != true || selected == null) return;
    final id = _user.id;
    if (id == null) return;
    try {
      await ApiService().updateUser(id, {'role': selected});
    } catch (_) {}
    try {
      await ApiService().request('POST', '/users/$id/roles/', body: json.encode({'role': selected}));
    } catch (_) {}
    await _loadUserRoles();
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(l10n.profileUpdated), behavior: SnackBarBehavior.floating),
      );
    }
  }

  Future<void> _removeRole(dynamic r) async {
    final id = _user.id;
    if (id == null) return;
    try {
      int? roleId;
      if (r is Map) {
        roleId = r['id'] is int ? r['id'] as int : int.tryParse('${r['id'] ?? ''}');
      }
      if (roleId != null) {
        await ApiService().request('DELETE', '/users/$id/roles/$roleId');
      } else {
        await ApiService().request('DELETE', '/users/$id/roles/', body: json.encode({'role': r.toString()}));
      }
      await _loadUserRoles();
    } catch (e) {
      debugPrint('Error: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.loadError), behavior: SnackBarBehavior.floating),
        );
      }
    }
  }

  Future<void> _loadSessions() async {
    setState(() => _sessionsLoading = true);
    try {
      final result = await ApiService().getSessions();
      if (mounted) setState(() { _sessions = result.items; _sessionsLoading = false; });
    } catch (e) {
      debugPrint('Error: $e');
      if (mounted) setState(() => _sessionsLoading = false);
    }
  }

  Future<void> _revokeSession(int sessionId) async {
    try {
      await ApiService().revokeSession(sessionId);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.sessionRevoked), behavior: SnackBarBehavior.floating),
        );
      }
      await _loadSessions();
    } on UnauthorizedException {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.sessionRevoked), behavior: SnackBarBehavior.floating),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.failedRevokeSession), behavior: SnackBarBehavior.floating),
        );
      }
    }
  }

  Future<void> _revokeAllSessions() async {
    final confirmed = await showConfirmDialog(context, title: l10n.revokeAllSessionsTitle, message: l10n.revokeAllConfirm);
    if (!confirmed) return;
    try {
      await ApiService().revokeAllSessions();
      await AuthService().clear();
      await OfflineCacheService.instance.clear();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.allSessionsRevoked), behavior: SnackBarBehavior.floating),
        );
        Navigator.pushAndRemoveUntil(context, MaterialPageRoute(builder: (_) => const MainScaffold()), (_) => false);
      }
    } catch (e) {
      debugPrint('Error: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.failedRevokeSessions), behavior: SnackBarBehavior.floating),
        );
      }
    }
  }

  Future<void> _exportMyData() async {
    try {
      final data = await ApiService().exportMyData();
      final jsonStr = const JsonEncoder.withIndent('  ').convert(data);
      if (!mounted) return;
      await showDialog(
        context: context,
        builder: (ctx) => AlertDialog(
          title: Text(l10n.translate('exportDataTitle')),
          content: SizedBox(
            width: 500,
            height: 400,
            child: SingleChildScrollView(child: SelectableText(jsonStr, style: const TextStyle(fontFamily: 'monospace', fontSize: 12))),
          ),
          actions: [
            TextButton(
              onPressed: () {
                Clipboard.setData(ClipboardData(text: jsonStr));
                Navigator.pop(ctx);
                ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.translate('copiedToClipboard')), behavior: SnackBarBehavior.floating));
              },
              child: Text(l10n.translate('copy')),
            ),
            TextButton(onPressed: () => Navigator.pop(ctx), child: Text(l10n.close)),
          ],
        ),
      );
    } catch (e) {
      debugPrint('Error: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.translate('exportDataFailed')), behavior: SnackBarBehavior.floating));
      }
    }
  }

  Future<void> _deleteMyAccount() async {
    final confirmed = await showConfirmDialog(context, title: l10n.translate('deleteAccountTitle'), message: l10n.translate('deleteAccountConfirm'));
    if (!confirmed) return;
    try {
      await ApiService().deleteMyAccount();
      await AuthService().clear();
      await OfflineCacheService.instance.clear();
      await SyncQueueService.instance.clear();
      if (mounted) {
        Navigator.pushAndRemoveUntil(context, MaterialPageRoute(builder: (_) => const MainScaffold()), (_) => false);
      }
    } catch (e) {
      debugPrint('Error: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.translate('deleteAccountFailed')), behavior: SnackBarBehavior.floating));
      }
    }
  }

  Future<void> _loadAliases() async {
    setState(() => _aliasesLoading = true);
    try {
      final result = await ApiService().getUserAliases(_user.id!);
      if (mounted) setState(() { _aliases = result.items; _aliasesLoading = false; });
    } catch (e) {
      debugPrint('Error: $e');
      if (mounted) setState(() => _aliasesLoading = false);
    }
  }

  Future<void> _showAliasDialog({UserAlias? existing}) async {
    final aliasController = TextEditingController(text: existing?.alias ?? '');
    String contextValue = existing?.context ?? 'global';
    bool isPublic = existing?.isPublic ?? true;
    String visibility = existing?.visibilityScope ?? 'festival_only';
    final saved = await showDialog<bool>(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setDialogState) => AlertDialog(
          title: Text(existing != null ? l10n.editAlias : l10n.createAlias),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(controller: aliasController, decoration: InputDecoration(labelText: l10n.aliasName)),
                const SizedBox(height: 12),
                DropdownButtonFormField<String>(
                  initialValue: contextValue,
                  decoration: InputDecoration(labelText: l10n.aliasContext),
                  items: ['global', 'festival', 'shortfilm', 'chat', 'public_profile', 'credits']
                      .map((c) => DropdownMenuItem(value: c, child: Text(c)))
                      .toList(),
                  onChanged: (v) => setDialogState(() => contextValue = v!),
                ),
                SwitchListTile(title: Text(l10n.aliasPublic), value: isPublic, onChanged: (v) => setDialogState(() => isPublic = v), contentPadding: EdgeInsets.zero),
                DropdownButtonFormField<String>(
                  initialValue: visibility,
                  decoration: InputDecoration(labelText: l10n.aliasVisibility),
                  items: ['festival_only', 'all_associated', 'selected'].map((v) => DropdownMenuItem(value: v, child: Text(v))).toList(),
                  onChanged: (v) => setDialogState(() => visibility = v!),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx, false), child: Text(l10n.cancel)),
            ElevatedButton(onPressed: () { if (aliasController.text.trim().isEmpty) return; Navigator.pop(ctx, true); }, child: Text(l10n.save)),
          ],
        ),
      ),
    );
    if (saved != true) return;
    try {
      if (existing != null) {
        await ApiService().updateUserAlias(_user.id!, existing.id!, {'alias': aliasController.text.trim(), 'context': contextValue, 'is_public': isPublic, 'visibility_scope': visibility});
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.aliasUpdated), behavior: SnackBarBehavior.floating));
        }
      } else {
        await ApiService().createUserAlias(_user.id!, UserAlias(userId: _user.id!, alias: aliasController.text.trim(), context: contextValue, isPublic: isPublic, visibilityScope: visibility));
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.aliasCreated), behavior: SnackBarBehavior.floating));
        }
      }
      _loadAliases();
    } catch (e) {
      debugPrint('Error: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.loadError), behavior: SnackBarBehavior.floating));
      }
    }
  }

  Future<void> _deleteAlias(UserAlias alias) async {
    final confirmed = await showConfirmDialog(context, title: l10n.deleteAlias, message: '${l10n.confirmDeleteAlias} "${alias.alias}"?');
    if (!confirmed) return;
    try {
      await ApiService().deleteUserAlias(_user.id!, alias.id!);
      _loadAliases();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.aliasDeleted), behavior: SnackBarBehavior.floating));
      }
    } catch (e) {
      debugPrint('Error: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.loadError), behavior: SnackBarBehavior.floating));
      }
    }
  }

  void _showLanguagePicker() {
    showLanguagePicker(context);
  }

  void _dummyAction(String label) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(label), behavior: SnackBarBehavior.floating));
  }

  void _editBanner() {
    if (!_canEdit) return;
    setState(() => _isEditing = true);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final user = _user;
    l10n = AppLocalizations.of(context)!;
    return Scaffold(
      appBar: AppBar(
        title: SemanticHeader(text: l10n.userProfile),
        actions: [
          if (_isEditing)
            Semantics(
              label: l10n.save,
              child: Tooltip(
                message: l10n.save,
                child: IconButton(
                  icon: _isSaving
                      ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2))
                      : const Icon(Icons.save),
                  onPressed: _isSaving ? null : () { _saveProfile(); },
                ),
              ),
            )
          else if (_canEdit) ...[
            if (_canDelete)
              Semantics(
                label: l10n.delete,
                child: Tooltip(
                  message: l10n.delete,
                  child: IconButton(icon: const Icon(Icons.delete_outline), onPressed: _deleteUser),
                ),
              ),
            Semantics(
              label: l10n.edit,
              child: Tooltip(
                message: l10n.edit,
                child: IconButton(icon: const Icon(Icons.edit), onPressed: () => setState(() => _isEditing = true)),
              ),
            ),
          ],
        ],
      ),
      body: _isEditing
          ? SingleChildScrollView(padding: const EdgeInsets.all(24), child: Center(child: ConstrainedBox(constraints: const BoxConstraints(maxWidth: 600), child: _buildEditForm())))
          : DefaultTabController(
              length: 4,
              child: NestedScrollView(
                headerSliverBuilder: (ctx, inner) => [SliverToBoxAdapter(child: _buildCoverHeader(user, theme, colorScheme))],
                body: Column(
                  children: [
                    TabBar(tabs: [Tab(text: l10n.bio), const Tab(text: 'Palmarés'), const Tab(text: 'Roles'), const Tab(text: 'Publicaciones')]),
                    Expanded(
                      child: TabBarView(
                        children: [
                          SingleChildScrollView(padding: const EdgeInsets.all(24), child: _buildInfoTab(user, theme, colorScheme)),
                          SingleChildScrollView(padding: const EdgeInsets.all(24), child: _buildPalmaresTab(theme, colorScheme)),
                          SingleChildScrollView(padding: const EdgeInsets.all(24), child: _buildRolesTab(theme, colorScheme)),
                          SingleChildScrollView(
                            padding: const EdgeInsets.all(24),
                            child: PublicationPanel(
                              scopeUserId: user.id,
                              canModerate: _canModerateWall,
                              currentUserId: (_fetchedCurrentUser ?? widget.currentUser)?.id,
                            ),
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

  Widget _buildCoverHeader(User user, ThemeData theme, ColorScheme colorScheme) {
    final banner = _bannerUrl;
    return Column(
      children: [
        Stack(
          clipBehavior: Clip.none,
          children: [
            SizedBox(
              height: 180,
              width: double.infinity,
              child: banner.isNotEmpty
                  ? Image.network(banner, fit: BoxFit.cover, errorBuilder: (_, __, ___) => Container(decoration: BoxDecoration(gradient: LinearGradient(colors: [colorScheme.primaryContainer, colorScheme.tertiaryContainer]))))
                  : Container(decoration: BoxDecoration(gradient: LinearGradient(colors: [colorScheme.primaryContainer, colorScheme.tertiaryContainer]))),
            ),
            if (_canEdit)
              Positioned(
                top: 8,
                right: 8,
                child: Material(
                  color: colorScheme.surfaceContainerHighest,
                  borderRadius: BorderRadius.circular(24),
                  elevation: 4,
                  child: InkWell(
                    borderRadius: BorderRadius.circular(24),
                    onTap: _editBanner,
                    child: const Padding(padding: EdgeInsets.all(10), child: Icon(Icons.edit, size: 20)),
                  ),
                ),
              ),
            Positioned(
              bottom: -45,
              left: 24,
              child: Container(
                decoration: BoxDecoration(shape: BoxShape.circle, border: Border.all(color: colorScheme.surface, width: 4)),
                child: Hero(
                  tag: 'user_${user.id}',
                  child: ProfileAvatar(
                    imageUrl: user.avatarUrl,
                    fallbackText: user.fullName ?? user.username,
                    radius: 45,
                    backgroundColor: colorScheme.primaryContainer,
                    foregroundColor: colorScheme.onPrimaryContainer,
                    semanticLabel: '${l10n.viewProfile}: ${user.fullName ?? user.username}',
                  ),
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 53),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(user.fullName ?? user.username, style: theme.textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold)),
              Text('@${user.username}', style: theme.textTheme.titleMedium?.copyWith(color: theme.colorScheme.onSurfaceVariant)),
              if (_tagline.isNotEmpty) ...[
                const SizedBox(height: 4),
                Text(_tagline, style: theme.textTheme.bodyMedium?.copyWith(color: theme.colorScheme.onSurfaceVariant)),
              ],
              const SizedBox(height: 8),
              _SocialLinksRow(links: _socialLinks.isNotEmpty ? _socialLinks : _collectSocialLinks()),
              const SizedBox(height: 12),
              Row(
                children: [
                  _StatItem(value: '${_palmares.length}', label: 'Premios'),
                  const SizedBox(width: 24),
                  _StatItem(value: '${_userRoles.length}', label: 'Festivales'),
                  const SizedBox(width: 24),
                  _StatItem(value: '${_aliases.length}', label: 'Alias'),
                ],
              ),
              const SizedBox(height: 12),
              if (!_isOwnProfile)
                Row(
                  children: [
                    FilledButton.icon(icon: const Icon(Icons.person_add, size: 18), label: const Text('Seguir'), onPressed: () => _dummyAction('Seguir')),
                    const SizedBox(width: 8),
                    OutlinedButton.icon(icon: const Icon(Icons.message, size: 18), label: const Text('Mensaje'), onPressed: () => _dummyAction('Mensaje')),
                  ],
                )
              else if (_canEdit)
                OutlinedButton.icon(icon: const Icon(Icons.edit, size: 18), label: Text(l10n.edit), onPressed: () => setState(() => _isEditing = true)),
            ],
          ),
        ),
        const SizedBox(height: 8),
      ],
    );
  }

  Widget _buildInfoTab(User user, ThemeData theme, ColorScheme colorScheme) {
    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 800),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (user.id != null)
              ProfileBadges(userId: user.id, canManage: _canModerateWall, isAdmin: _isAdmin),
            if (user.email != null) InfoRow(icon: Icons.email, semanticLabel: '${l10n.email}: ${user.email}', text: user.email!),
            if (user.role != null) ...[
              const SizedBox(height: 12),
              InfoRow(icon: Icons.badge, semanticLabel: '${l10n.role}: ${user.role}', text: _roleLabel(user.role!)),
            ],
            if (user.bio != null) ...[
              const SizedBox(height: 24),
              SemanticHeader(text: l10n.bio, style: theme.textTheme.titleSmall?.copyWith(color: theme.colorScheme.primary)),
              const SizedBox(height: 8),
              Semantics(label: '${l10n.bio}: ${user.bio}', child: Text(user.bio!, style: theme.textTheme.bodyLarge)),
            ],
            const SizedBox(height: 24),
            _buildPrivacyAndStatus(user, colorScheme),
            if (_isOwnProfile) ...[
              const SizedBox(height: 24),
              SessionsCard(l10n: l10n, sessions: _sessions, loading: _sessionsLoading, onRevokeAll: _revokeAllSessions, onRevoke: _revokeSession),
              const SizedBox(height: 24),
              const DavSubscriptionSection(),
              const SizedBox(height: 24),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(l10n.translate('privacyAndData'), style: theme.textTheme.titleMedium),
                      const SizedBox(height: 12),
                      Wrap(
                        spacing: 12,
                        runSpacing: 8,
                        children: [
                          OutlinedButton.icon(
                            icon: const Icon(Icons.download),
                            label: Text(l10n.translate('exportMyData')),
                            onPressed: _exportMyData,
                          ),
                          OutlinedButton.icon(
                            icon: const Icon(Icons.delete_forever),
                            label: Text(l10n.translate('deleteMyAccount')),
                            onPressed: _deleteMyAccount,
                            style: OutlinedButton.styleFrom(foregroundColor: Colors.red),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ],
            if (user.latitude != null && user.longitude != null) ...[
              const SizedBox(height: 24),
              SizedBox(
                height: 200,
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(12),
                  child: Stack(
                    children: [
                      FlutterMap(
                        options: MapOptions(initialCenter: LatLng(user.latitude!, user.longitude!), initialZoom: 13, interactionOptions: const InteractionOptions(flags: InteractiveFlag.all)),
                        children: [
                          TileLayer(urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png', userAgentPackageName: 'com.clakettes.app'),
                          MarkerLayer(markers: [Marker(point: LatLng(user.latitude!, user.longitude!), width: 80, height: 80, child: Icon(Icons.place, color: theme.colorScheme.primary, size: 40))]),
                        ],
                      ),
                      Positioned(
                        top: 8,
                        right: 8,
                        child: Material(
                          color: theme.colorScheme.surfaceContainerHighest,
                          borderRadius: BorderRadius.circular(24),
                          elevation: 4,
                          child: InkWell(
                            borderRadius: BorderRadius.circular(24),
                            onTap: () => _openInMaps(user.latitude!, user.longitude!, user.fullName ?? user.username),
                            child: Padding(padding: const EdgeInsets.all(10), child: Icon(Icons.directions, color: theme.colorScheme.primary, size: 22)),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
            const SizedBox(height: 24),
            AliasesCard(l10n: l10n, aliases: _aliases, loading: _aliasesLoading, canEdit: _canEdit, canAdd: _canEdit && _user.id != null, onAdd: () => _showAliasDialog(), onEdit: (a) => _showAliasDialog(existing: a), onDelete: _deleteAlias),
          ],
        ),
      ),
    );
  }

  Widget _buildPalmaresTab(ThemeData theme, ColorScheme colorScheme) {
    if (_palmares.isEmpty) {
      return Center(child: Padding(padding: const EdgeInsets.all(32), child: Text('Sin premios todavía', style: theme.textTheme.bodyMedium?.copyWith(color: colorScheme.onSurfaceVariant))));
    }
    final Map<String, List<dynamic>> byYear = {};
    for (final p in _palmares) {
      String year = '—';
      if (p is Map) {
        year = (p['year'] ?? p['edition_year'] ?? p['created_at']?.toString().substring(0, 4) ?? '—').toString();
      }
      byYear.putIfAbsent(year, () => []).add(p);
    }
    final years = byYear.keys.toList()..sort((a, b) => b.compareTo(a));
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        for (final y in years) ...[
          SemanticHeader(text: y, style: theme.textTheme.titleMedium?.copyWith(color: colorScheme.primary)),
          const SizedBox(height: 8),
          for (int i = 0; i < byYear[y]!.length; i++)
            IntrinsicHeight(
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Column(
                    children: [
                      Container(width: 12, height: 12, decoration: BoxDecoration(shape: BoxShape.circle, color: colorScheme.primary)),
                      if (i < byYear[y]!.length - 1) Expanded(child: Container(width: 2, color: colorScheme.outlineVariant)),
                    ],
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Card(
                      child: Padding(
                        padding: const EdgeInsets.all(12),
                        child: Text(_awardTitle(byYear[y]![i]), style: theme.textTheme.bodyMedium),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          const SizedBox(height: 16),
        ],
      ],
    );
  }

  String _awardTitle(dynamic p) {
    if (p is Map) {
      for (final k in ['title', 'name', 'award_name', 'category', 'festival_name']) {
        final v = p[k];
        if (v != null && v.toString().isNotEmpty) return v.toString();
      }
      return p.toString();
    }
    return p.toString();
  }

  Widget _buildRolesTab(ThemeData theme, ColorScheme colorScheme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            for (final r in _userRoles)
              Chip(label: Text(_roleLabel(r)), deleteIcon: _canEdit ? const Icon(Icons.close, size: 18) : null, onDeleted: _canEdit ? () => _removeRole(r) : null),
            if (_userRoles.isEmpty) Text('Sin roles asignados', style: theme.textTheme.bodyMedium?.copyWith(color: colorScheme.onSurfaceVariant)),
          ],
        ),
        if (_canEdit) ...[
          const SizedBox(height: 16),
          OutlinedButton.icon(icon: const Icon(Icons.add), label: const Text('Añadir rol'), onPressed: _showRoleDialog),
        ],
      ],
    );
  }

  Widget _buildEditForm() {
    return Form(
      key: _formKey,
      autovalidateMode: AutovalidateMode.onUserInteraction,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          SemanticTextField(controller: _fullNameController, label: l10n.fullName, semanticLabel: l10n.fullName, helperText: l10n.fullName, textInputAction: TextInputAction.next),
          const SizedBox(height: 16),
          SemanticTextField(controller: _emailController, label: l10n.email, semanticLabel: l10n.email, helperText: l10n.email, keyboardType: TextInputType.emailAddress, textInputAction: TextInputAction.next),
          const SizedBox(height: 16),
          SemanticTextField(controller: _bioController, label: l10n.bio, semanticLabel: l10n.bio, helperText: l10n.bioLengthHint(500), maxLines: 3, maxLength: 500, textInputAction: TextInputAction.next),
          const SizedBox(height: 16),
          SemanticTextField(controller: _taglineController, label: 'Tagline', semanticLabel: 'Tagline', helperText: 'Tagline', textInputAction: TextInputAction.next, maxLength: 120),
          const SizedBox(height: 16),
          SemanticTextField(controller: _avatarController, label: 'Avatar URL', semanticLabel: 'Avatar URL', helperText: 'Avatar URL', keyboardType: TextInputType.url, textInputAction: TextInputAction.next),
          const SizedBox(height: 16),
          SemanticTextField(controller: _bannerController, label: 'Portada URL', semanticLabel: 'Portada URL', helperText: 'Portada URL', keyboardType: TextInputType.url, textInputAction: TextInputAction.next),
          const SizedBox(height: 16),
          SemanticTextField(controller: _websiteController, label: 'Web', semanticLabel: 'Web', helperText: 'Web', keyboardType: TextInputType.url, textInputAction: TextInputAction.next),
          const SizedBox(height: 16),
          SemanticTextField(controller: _instagramController, label: 'Instagram', semanticLabel: 'Instagram', helperText: 'Instagram', textInputAction: TextInputAction.next),
          const SizedBox(height: 16),
          SemanticTextField(controller: _xController, label: 'X', semanticLabel: 'X', helperText: 'X', textInputAction: TextInputAction.next),
          const SizedBox(height: 16),
          SemanticTextField(controller: _youtubeController, label: 'YouTube', semanticLabel: 'YouTube', helperText: 'YouTube', textInputAction: TextInputAction.next, onSubmitted: (_) => _saveProfile()),
        ],
      ),
    );
  }

  Widget _buildPrivacyAndStatus(User user, ColorScheme colorScheme) {
    return Material(
      color: colorScheme.surfaceContainerLow,
      borderRadius: BorderRadius.circular(12),
      clipBehavior: Clip.antiAlias,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SemanticHeader(text: l10n.privacySettings, style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 16),
            SwitchListTile(title: Text(l10n.publicProfile), subtitle: Text(_isPublic ? l10n.visibleToAll : l10n.onlyVisibleToYou), value: _isPublic, onChanged: _isEditing ? (v) => setState(() => _isPublic = v) : null, secondary: Icon(_isPublic ? Icons.public : Icons.lock), contentPadding: EdgeInsets.zero),
            SwitchListTile(title: Text(l10n.showEmail), subtitle: Text(_isPublicEmail ? l10n.visibleToAll : l10n.onlyVisibleToYou), value: _isPublicEmail, onChanged: _isEditing ? (v) => setState(() => _isPublicEmail = v) : null, secondary: Icon(_isPublicEmail ? Icons.email : Icons.email_outlined), contentPadding: EdgeInsets.zero),
            SwitchListTile(title: Text(l10n.showBio), subtitle: Text(_isPublicBio ? l10n.visibleToAll : l10n.onlyVisibleToYou), value: _isPublicBio, onChanged: _isEditing ? (v) => setState(() => _isPublicBio = v) : null, secondary: Icon(_isPublicBio ? Icons.description : Icons.description_outlined), contentPadding: EdgeInsets.zero),
            SwitchListTile(title: Text(l10n.showLocation), subtitle: Text(_isPublicLocation ? l10n.visibleToAll : l10n.onlyVisibleToYou), value: _isPublicLocation, onChanged: _isEditing ? (v) => setState(() => _isPublicLocation = v) : null, secondary: Icon(_isPublicLocation ? Icons.location_on : Icons.location_off), contentPadding: EdgeInsets.zero),
            const Divider(height: 24),
            ListTile(
              leading: const Icon(Icons.language),
              title: Text(l10n.language),
              subtitle: Text(LocaleService.localeNames[LocaleService.instance.currentLocale?.languageCode ?? 'en'] ?? 'English'),
              contentPadding: EdgeInsets.zero,
              onTap: _showLanguagePicker,
            ),
            const Divider(height: 24),
            InfoRow(icon: user.isActive ? Icons.check_circle : Icons.cancel, semanticLabel: user.isActive ? l10n.active : l10n.inactive, text: user.isActive ? l10n.active : l10n.inactive, iconColor: user.isActive ? colorScheme.primary : colorScheme.onSurfaceVariant),
          ],
        ),
      ),
    );
  }
}

class _StatItem extends StatelessWidget {
  final String value;
  final String label;
  const _StatItem({required this.value, required this.label});
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(value, style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
        Text(label, style: theme.textTheme.bodySmall?.copyWith(color: theme.colorScheme.onSurfaceVariant)),
      ],
    );
  }
}

class _SocialLinksRow extends StatelessWidget {
  final Map<String, String> links;
  const _SocialLinksRow({required this.links});
  Future<void> _open(String url) async {
    var uri = Uri.tryParse(url);
    if (uri != null && !uri.hasScheme) uri = Uri.parse('https://$url');
    if (uri != null && await canLaunchUrl(uri)) await launchUrl(uri, mode: LaunchMode.externalApplication);
  }
  @override
  Widget build(BuildContext context) {
    final entries = links.entries.where((e) => e.value.trim().isNotEmpty).toList();
    if (entries.isEmpty) return const SizedBox.shrink();
    IconData iconFor(String key) {
      switch (key.toLowerCase()) {
        case 'website':
          return Icons.language;
        case 'instagram':
          return Icons.camera_alt;
        case 'x':
        case 'twitter':
          return Icons.alternate_email;
        case 'youtube':
          return Icons.play_circle;
        default:
          return Icons.link;
      }
    }
    return Wrap(
      spacing: 4,
      children: [for (final e in entries) IconButton(tooltip: e.key, icon: Icon(iconFor(e.key), size: 20), onPressed: () => _open(e.value))],
    );
  }
}
