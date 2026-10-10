import 'package:flutter/material.dart';
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
import '../main_scaffold.dart';


/// Muestra el perfil de un usuario y permite editarlo.
///
/// En modo lectura muestra el avatar, nombre de usuario, email, rol, bio,
/// coordenadas de localización, privacidad y estado de actividad. En modo
/// edición muestra un formulario con widgets [SemanticTextField] para los
/// campos editables e interruptores de privacidad por campo.
///
/// Reglas de permisos:
/// - admin: puede editar cualquier usuario
/// - organizer: puede editar su propio perfil y los usuarios de sus festivales
/// - user: solo su propio perfil
/// - jury: solo su propio perfil
/// - borrado: solo admin y organizer
class UserProfileScreen extends StatefulWidget {
  final User user;
  final User? currentUser;

  const UserProfileScreen({super.key, required this.user, this.currentUser});

  @override
  State<UserProfileScreen> createState() => _UserProfileScreenState();
}

/// Estado de [UserProfileScreen]. Mantiene el usuario consultado, los
/// controladores de edición y los interruptores de privacidad, y carga
/// sesiones y alias cuando corresponde.
class _UserProfileScreenState extends State<UserProfileScreen> {
  late User _user;
  late TextEditingController _fullNameController;
  late TextEditingController _bioController;
  late TextEditingController _emailController;
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

  /// Indica si el usuario actual está viendo su propio perfil.
  bool get _isOwnProfile => (_fetchedCurrentUser ?? widget.currentUser)?.id == _user.id;
  /// Indica si el usuario actual puede editar el perfil según propiedad/rol.
  bool get _canEdit {
    final cu = _fetchedCurrentUser ?? widget.currentUser;
    if (cu == null) return false;
    if (_isOwnProfile) return true;
    if (cu.role == 'admin') return true;
    if (cu.role == 'organizer') return true;
    return false;
  }
  /// Indica si el usuario actual puede eliminar el perfil (solo admin/organizer).
  bool get _canDelete {
    final cu = _fetchedCurrentUser ?? widget.currentUser;
    if (cu == null) return false;
    final role = cu.role;
    if (role == 'admin') return true;
    if (role == 'organizer') return true;
    return false;
  }

  @override
  void initState() {
    super.initState();
    _user = widget.user;
    _fullNameController = TextEditingController(text: _user.fullName ?? '');
    _bioController = TextEditingController(text: _user.bio ?? '');
    _emailController = TextEditingController(text: _user.email ?? '');
    _isPublic = _user.isPublic;
    _isPublicEmail = _user.isPublicEmail;
    _isPublicBio = _user.isPublicBio;
    _isPublicLocation = _user.isPublicLocation;
    _loadCurrentUserIfNeeded();
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
    super.dispose();
  }

/// Abre las coordenadas en la app de mapas del sistema, usando
/// OpenStreetMap cuando el esquema geo no está disponible.
  Future<void> _openInMaps(double lat, double lng, String label) async {
    final encodedLabel = Uri.encodeComponent(label);
    final geoUri = Uri.parse('geo:0,0?q=$lat,$lng($encodedLabel)');
    if (await canLaunchUrl(geoUri)) {
      await launchUrl(geoUri);
      return;
    }
    final osmUri = Uri.parse(
      'https://www.openstreetmap.org/?mlat=$lat&mlon=$lng',
    );
    if (await canLaunchUrl(osmUri)) {
      await launchUrl(osmUri, mode: LaunchMode.externalApplication);
    }
  }

  /// Valida el formulario y persiste los campos del perfil editados.
  Future<void> _saveProfile() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isSaving = true);

    try {
      final updated = await ApiService().updateUser(_user.id!, {
        'full_name': _fullNameController.text.isNotEmpty
            ? _fullNameController.text.trim()
            : null,
        if (_emailController.text.trim().isNotEmpty)
          'email': _emailController.text.trim(),
        'bio': _bioController.text.isNotEmpty
            ? _bioController.text.trim()
            : null,
        'is_public': _isPublic,
        'is_public_email': _isPublicEmail,
        'is_public_bio': _isPublicBio,
        'is_public_location': _isPublicLocation,
      });

      if (mounted) {
        setState(() {
          _user = updated;
          _isEditing = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(l10n.profileUpdated),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } catch (e) {
      debugPrint('Error: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(l10n.loadError),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _isSaving = false);
    }
  }

  /// Confirma y elimina el usuario, cerrando la pantalla en caso de éxito.
  Future<void> _deleteUser() async {
    final confirmed = await showConfirmDialog(
      context,
      title: l10n.delete,
      message: l10n.confirmDelete,
    );
    if (!confirmed) return;

    try {
      await ApiService().deleteUser(_user.id!);
      if (mounted) {
        Navigator.pop(context, true);
      }
    } catch (e) {
      debugPrint('Error: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(l10n.loadError),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    }
  }

/// Obtiene el usuario actual cuando no se proporciona y, según la propiedad
/// del perfil, carga sesiones y alias.
  Future<void> _loadCurrentUserIfNeeded() async {
    if (widget.currentUser == null) {
      final user = await AuthService().getCurrentUser();
      if (mounted) {
        setState(() => _fetchedCurrentUser = user);
      }
    }
    if (mounted && _isOwnProfile) _loadSessions();
    if (mounted) _loadAliases();
  }

  /// Carga las sesiones activas del propio perfil.
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

  /// Revoca una única sesión y recarga la lista de sesiones.
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

  /// Revoca todas las sesiones, limpia auth/caché y vuelve al scaffold principal.
  Future<void> _revokeAllSessions() async {
    final confirmed = await showConfirmDialog(
      context,
      title: l10n.revokeAllSessionsTitle,
      message: l10n.revokeAllConfirm,
    );
    if (!confirmed) return;
    try {
      await ApiService().revokeAllSessions();
      await AuthService().clear();
      await OfflineCacheService.instance.clear();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.allSessionsRevoked), behavior: SnackBarBehavior.floating),
        );
        Navigator.pushAndRemoveUntil(
          context,
          MaterialPageRoute(builder: (_) => const MainScaffold()),
          (_) => false,
        );
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

  /// Carga los alias del usuario consultado.
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

  /// Muestra el diálogo de creación/edición de alias y persiste los cambios.
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
                TextField(
                  controller: aliasController,
                  decoration: InputDecoration(labelText: l10n.aliasName),
                ),
                const SizedBox(height: 12),
                DropdownButtonFormField<String>(
                  initialValue: contextValue,
                  decoration: InputDecoration(labelText: l10n.aliasContext),
                  items: ['global', 'festival', 'shortfilm', 'chat', 'public_profile', 'credits']
                      .map((c) => DropdownMenuItem(value: c, child: Text(c)))
                      .toList(),
                  onChanged: (v) => setDialogState(() => contextValue = v!),
                ),
                SwitchListTile(
                  title: Text(l10n.aliasPublic),
                  value: isPublic,
                  onChanged: (v) => setDialogState(() => isPublic = v),
                  contentPadding: EdgeInsets.zero,
                ),
                DropdownButtonFormField<String>(
                  initialValue: visibility,
                  decoration: InputDecoration(labelText: l10n.aliasVisibility),
                  items: ['festival_only', 'all_associated', 'selected']
                      .map((v) => DropdownMenuItem(value: v, child: Text(v)))
                      .toList(),
                  onChanged: (v) => setDialogState(() => visibility = v!),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx, false), child: Text(l10n.cancel)),
            ElevatedButton(
              onPressed: () {
                if (aliasController.text.trim().isEmpty) return;
                Navigator.pop(ctx, true);
              },
              child: Text(l10n.save),
            ),
          ],
        ),
      ),
    );

    if (saved != true) return;

    try {
      if (existing != null) {
        await ApiService().updateUserAlias(_user.id!, existing.id!, {
          'alias': aliasController.text.trim(),
          'context': contextValue,
          'is_public': isPublic,
          'visibility_scope': visibility,
        });
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(l10n.aliasUpdated), behavior: SnackBarBehavior.floating),
          );
        }
      } else {
        await ApiService().createUserAlias(
          _user.id!,
          UserAlias(
            userId: _user.id!,
            alias: aliasController.text.trim(),
            context: contextValue,
            isPublic: isPublic,
            visibilityScope: visibility,
          ),
        );
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(l10n.aliasCreated), behavior: SnackBarBehavior.floating),
          );
        }
      }
      _loadAliases();
    } catch (e) {
      debugPrint('Error: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.loadError), behavior: SnackBarBehavior.floating),
        );
      }
    }
  }

  /// Confirma y elimina el alias indicado.
  Future<void> _deleteAlias(UserAlias alias) async {
    final confirmed = await showConfirmDialog(
      context,
      title: l10n.deleteAlias,
      message: '${l10n.confirmDeleteAlias} "${alias.alias}"?',
    );
    if (!confirmed) return;
    try {
      await ApiService().deleteUserAlias(_user.id!, alias.id!);
      _loadAliases();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.aliasDeleted), behavior: SnackBarBehavior.floating),
        );
      }
    } catch (e) {
      debugPrint('Error: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.loadError), behavior: SnackBarBehavior.floating),
        );
      }
    }
  }

  /// Muestra la hoja inferior de selección de idioma y persiste la elección.
  void _showLanguagePicker() {
    showLanguagePicker(context);
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
                      ? const SizedBox(
                          height: 20,
                          width: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Icon(Icons.save),
                  onPressed: _isSaving
                      ? null
                      : () {
                          _saveProfile();
                        },
                ),
              ),
            )
          else if (_canEdit) ...[
            if (_canDelete)
              Semantics(
                label: l10n.delete,
                child: Tooltip(
                  message: l10n.delete,
                  child: IconButton(
                    icon: const Icon(Icons.delete_outline),
                    onPressed: _deleteUser,
                  ),
                ),
              ),
            Semantics(
              label: l10n.edit,
              child: Tooltip(
                message: l10n.edit,
                child: IconButton(
                  icon: const Icon(Icons.edit),
                  onPressed: () => setState(() => _isEditing = true),
                ),
              ),
            ),
          ],
        ],
      ),
      body: LayoutBuilder(
        builder: (context, constraints) {
          final isWide = constraints.maxWidth > 800;
          return Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 800),
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(24),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    Hero(
                      tag: 'user_${user.id}',
                      child: ProfileAvatar(
                        imageUrl: user.avatarUrl,
                        fallbackText: user.fullName ?? user.username,
                        radius: isWide ? 80 : 60,
                        backgroundColor: colorScheme.primaryContainer,
                        foregroundColor: colorScheme.onPrimaryContainer,
                        semanticLabel: '${l10n.viewProfile}: ${user.fullName ?? user.username}',
                      ),
                    ),
                    const SizedBox(height: 24),
                    _buildUserInfo(user, theme, isWide),
                    const SizedBox(height: 32),
                    _buildPrivacyAndStatus(user, colorScheme),
                    if (_isOwnProfile) ...[
                      const SizedBox(height: 24),
                      SessionsCard(
                        l10n: l10n,
                        sessions: _sessions,
                        loading: _sessionsLoading,
                        onRevokeAll: _revokeAllSessions,
                        onRevoke: _revokeSession,
                      ),
                      const SizedBox(height: 24),
                      const DavSubscriptionSection(),
                    ],
                    const SizedBox(height: 24),
                    AliasesCard(
                      l10n: l10n,
                      aliases: _aliases,
                      loading: _aliasesLoading,
                      canEdit: _canEdit,
                      canAdd: _canEdit && _user.id != null,
                      onAdd: () => _showAliasDialog(),
                      onEdit: (a) => _showAliasDialog(existing: a),
                      onDelete: _deleteAlias,
                    ),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  /// Construye la zona de información del usuario, con edición o lectura.
  Widget _buildUserInfo(User user, ThemeData theme, bool isWide) {
    return Form(
      key: _formKey,
      autovalidateMode: AutovalidateMode.onUserInteraction,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (_isEditing)
            Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 500),
                child: Column(
                  children: [
                    SemanticTextField(
                      controller: _fullNameController,
                      label: l10n.fullName,
                      semanticLabel: l10n.fullName,
                      helperText: l10n.fullName,
                      textInputAction: TextInputAction.next,
                      validator: (value) {
                        if (value != null && value.length > 100) {
                          return l10n.getValidationMessage('maxLength', args: {'max': 100});
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),
                    SemanticTextField(
                      controller: _emailController,
                      label: l10n.email,
                      semanticLabel: l10n.email,
                      helperText: l10n.email,
                      keyboardType: TextInputType.emailAddress,
                      textInputAction: TextInputAction.next,
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return l10n.getValidationMessage('required');
                        }
                        if (!value.contains('@')) {
                          return l10n.getValidationMessage('emailInvalid');
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),
                    SemanticTextField(
                      controller: _bioController,
                      label: l10n.bio,
                      semanticLabel: l10n.bio,
                      helperText: l10n.bioLengthHint(500),
                      maxLines: 3,
                      maxLength: 500,
                      textInputAction: TextInputAction.done,
                      onSubmitted: (_) => _saveProfile(),
                    ),
                  ],
                ),
              ),
            )
          else
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                SemanticHeader(
                  text: user.fullName ?? user.username,
                  style: theme.textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 8),
                Semantics(
                  label: '${l10n.username}: @${user.username}',
                  child: Center(
                    child: Text(
                      '@${user.username}',
                      style: theme.textTheme.titleMedium?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                if (user.email != null)
                  InfoRow(
                    icon: Icons.email,
                    semanticLabel: '${l10n.email}: ${user.email}',
                    text: user.email!,
                  ),
                if (user.role != null) ...[
                  const SizedBox(height: 12),
                  InfoRow(
                    icon: Icons.badge,
                    semanticLabel: '${l10n.role}: ${l10n.getRoleTranslation(user.role!)}',
                    text: l10n.getRoleTranslation(user.role!),
                  ),
                ],
                if (user.bio != null) ...[
                  const SizedBox(height: 24),
                  SemanticHeader(
                    text: l10n.bio,
                    style: theme.textTheme.titleSmall?.copyWith(
                      color: theme.colorScheme.primary,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Semantics(
                    label: '${l10n.bio}: ${user.bio}',
                    child: Text(user.bio!, style: theme.textTheme.bodyLarge),
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
                            options: MapOptions(
                              initialCenter: LatLng(
                                user.latitude!,
                                user.longitude!,
                              ),
                              initialZoom: 13,
                              interactionOptions: const InteractionOptions(
                                flags: InteractiveFlag.all,
                              ),
                            ),
                            children: [
                              TileLayer(
                                urlTemplate:
                                    'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                                userAgentPackageName: 'com.clakettes.app',
                              ),
                              MarkerLayer(
                                markers: [
                                  Marker(
                                    point: LatLng(
                                      user.latitude!,
                                      user.longitude!,
                                    ),
                                    width: 80,
                                    height: 80,
                                    child: Icon(
                                      Icons.place,
                                      color: theme.colorScheme.primary,
                                      size: 40,
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),
                          Positioned(
                            top: 8,
                            right: 8,
                            child: Material(
                              color:
                                  theme.colorScheme.surfaceContainerHighest,
                              borderRadius: BorderRadius.circular(24),
                              elevation: 4,
                              child: InkWell(
                                borderRadius: BorderRadius.circular(24),
                                onTap: () => _openInMaps(
                                  user.latitude!,
                                  user.longitude!,
                                  user.fullName ?? user.username,
                                ),
                                child: Padding(
                                  padding: const EdgeInsets.all(10),
                                  child: Icon(
                                    Icons.directions,
                                    color: theme.colorScheme.primary,
                                    size: 22,
                                  ),
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ],
            ),
        ],
      ),
    );
  }

  /// Tarjeta con privacidad, idioma y estado de actividad del usuario.
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
          SemanticHeader(
            text: l10n.privacySettings,
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 16),
          SwitchListTile(
            title: Text(l10n.publicProfile),
            subtitle: Text(_isPublic ? l10n.visibleToAll : l10n.onlyVisibleToYou),
            value: _isPublic,
            onChanged: _isEditing ? (v) => setState(() => _isPublic = v) : null,
            secondary: Icon(_isPublic ? Icons.public : Icons.lock),
            contentPadding: EdgeInsets.zero,
          ),
          SwitchListTile(
            title: Text(l10n.showEmail),
            subtitle: Text(_isPublicEmail ? l10n.visibleToAll : l10n.onlyVisibleToYou),
            value: _isPublicEmail,
            onChanged: _isEditing ? (v) => setState(() => _isPublicEmail = v) : null,
            secondary: Icon(_isPublicEmail ? Icons.email : Icons.email_outlined),
            contentPadding: EdgeInsets.zero,
          ),
          SwitchListTile(
            title: Text(l10n.showBio),
            subtitle: Text(_isPublicBio ? l10n.visibleToAll : l10n.onlyVisibleToYou),
            value: _isPublicBio,
            onChanged: _isEditing ? (v) => setState(() => _isPublicBio = v) : null,
            secondary: Icon(_isPublicBio ? Icons.description : Icons.description_outlined),
            contentPadding: EdgeInsets.zero,
          ),
          SwitchListTile(
            title: Text(l10n.showLocation),
            subtitle: Text(_isPublicLocation ? l10n.visibleToAll : l10n.onlyVisibleToYou),
            value: _isPublicLocation,
            onChanged: _isEditing ? (v) => setState(() => _isPublicLocation = v) : null,
            secondary: Icon(_isPublicLocation ? Icons.location_on : Icons.location_off),
            contentPadding: EdgeInsets.zero,
          ),
          const Divider(height: 24),
          ListTile(
            leading: const Icon(Icons.language),
            title: Text(l10n.language),
            subtitle: Text(LocaleService.localeNames[
                LocaleService.instance.currentLocale?.languageCode ?? 'en'] ?? 'English'),
            contentPadding: EdgeInsets.zero,
            onTap: _showLanguagePicker,
          ),
          const Divider(height: 24),
          InfoRow(
            icon: user.isActive ? Icons.check_circle : Icons.cancel,
            semanticLabel: user.isActive ? l10n.active : l10n.inactive,
            text: user.isActive ? l10n.active : l10n.inactive,
            iconColor: user.isActive ? colorScheme.primary : colorScheme.onSurfaceVariant,
          ),
        ],
      ),
      ),
    );
  }

  /// Tarjeta con las sesiones activas y la opción de revocarlas.

}
