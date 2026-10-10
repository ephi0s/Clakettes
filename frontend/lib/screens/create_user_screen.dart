import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../models/user_model.dart';
import '../services/api_service.dart';
import '../services/sync_queue_service.dart';
import '../services/connectivity_monitor.dart';
import '../services/auth_service.dart';
import '../widgets/reusable_widgets.dart';

/// Formulario a pantalla completa para crear un nuevo usuario de la plataforma.
///
/// Valida los campos obligatorios (usuario, email, contraseña) mediante
/// [SemanticTextField] con mensajes de error localizados. Al tener éxito la
/// pantalla se cierra con `true` para que la pantalla padre pueda refrescar
/// la lista de usuarios.
class CreateUserScreen extends StatefulWidget {
  const CreateUserScreen({super.key});

  @override
  State<CreateUserScreen> createState() => _CreateUserScreenState();
}

/// Mantiene los controladores del formulario, el rol seleccionado, los
/// interruptores de privacidad y el rol del usuario actual (obtenido una vez
/// para restringir las opciones de rol).
class _CreateUserScreenState extends State<CreateUserScreen> {
  final _formKey = GlobalKey<FormState>();
  final _usernameController = TextEditingController();
  final _emailController = TextEditingController();
  final _fullNameController = TextEditingController();
  final _bioController = TextEditingController();
  final _passwordController = TextEditingController();

  String? _selectedRole;
  bool _isPublic = true;
  bool _isPublicEmail = true;
  bool _isPublicBio = true;
  bool _isPublicLocation = true;
  bool _isLoading = false;
  bool _obscurePassword = true;
  bool _initialized = false;
  late AppLocalizations l10n;
  String? _currentUserRole;

  final List<String> _roles = ['admin', 'organizer', 'user', 'jury'];

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    l10n = AppLocalizations.of(context)!;
    if (!_initialized) {
      _initialized = true;
      _loadCurrentUserRole();
    }
  }

  @override
  void dispose() {
    _usernameController.dispose();
    _emailController.dispose();
    _fullNameController.dispose();
    _bioController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  /// Carga el rol del usuario actual para restringir el rol admin en el desplegable.
  Future<void> _loadCurrentUserRole() async {
    final user = await AuthService().getCurrentUser();
    if (mounted) {
      setState(() => _currentUserRole = user?.role);
    }
  }

  /// Valida y crea el usuario, encolando la creación offline en caso de error.
  Future<void> _submit() async {
    if (_isLoading) return;
    if (!_formKey.currentState!.validate()) {
      // Don't show a SnackBar; individual fields display validation errors.
      return;
    }

    setState(() => _isLoading = true);

    final role = (_selectedRole == 'admin' && _currentUserRole != 'admin') ? 'user' : _selectedRole;
    final user = User(
      username: _usernameController.text.trim(),
      email: _emailController.text.trim(),
      fullName: _fullNameController.text.isNotEmpty ? _fullNameController.text.trim() : null,
      role: role,
      bio: _bioController.text.isNotEmpty ? _bioController.text.trim() : null,
      isPublic: _isPublic,
      isPublicEmail: _isPublicEmail,
      isPublicBio: _isPublicBio,
      isPublicLocation: _isPublicLocation,
    );

    try {
      final apiService = ApiService();
      await apiService.createUser(user, _passwordController.text);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(l10n.userCreated),
            behavior: SnackBarBehavior.floating,
          ),
        );
        Navigator.pop(context, true);
      }
    } catch (e) {
      final queue = SyncQueueService.instance;
      final payload = user.toJson();
      if (!queue.contains(
          entityType: 'user', operation: 'create', payload: payload)) {
        await queue.enqueue(
          entityType: 'user',
          operation: 'create',
          payload: payload,
        );
      }
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(ConnectivityMonitor.instance.isOnline ? l10n.loadError : '${l10n.userCreated}. ${l10n.syncPending.replaceAll('{count}', '1')}'),
            behavior: SnackBarBehavior.floating,
          ),
        );
        Navigator.pop(context, true);
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    l10n = AppLocalizations.of(context)!;

    return Scaffold(
      appBar: AppBar(
        title: SemanticHeader(text: l10n.createUser),
      ),
      body: LayoutBuilder(
        builder: (context, constraints) {
          return Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 600),
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(24),
                child: Form(
                  key: _formKey,
                  autovalidateMode: AutovalidateMode.onUserInteraction,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      SemanticTextField(
                        controller: _usernameController,
                        label: l10n.username,
                        semanticLabel: l10n.username,
                        helperText: l10n.getValidationMessage('minLength', args: {'min': 3}),
                        prefixIcon: const Icon(Icons.person),
                        textInputAction: TextInputAction.next,
                        maxLength: 50,
                        validator: (v) {
                          if (v == null || v.trim().isEmpty) return l10n.getValidationMessage('required');
                          if (v.trim().length < 3) return l10n.getValidationMessage('minLength', args: {'min': 3});
                          return null;
                        },
                      ),
                      const SizedBox(height: 16),
                      SemanticTextField(
                        controller: _emailController,
                        label: l10n.email,
                        semanticLabel: l10n.email,
                        helperText: l10n.email,
                        prefixIcon: const Icon(Icons.email),
                        keyboardType: TextInputType.emailAddress,
                        textInputAction: TextInputAction.next,
                        maxLength: 100,
                        validator: (v) {
                          if (v == null || v.trim().isEmpty) return l10n.getValidationMessage('required');
                          if (!v.contains('@')) return l10n.getValidationMessage('emailInvalid');
                          return null;
                        },
                      ),
                      const SizedBox(height: 16),
                      SemanticTextField(
                        controller: _fullNameController,
                        label: l10n.fullName,
                        semanticLabel: l10n.fullName,
                        helperText: l10n.optional,
                        prefixIcon: const Icon(Icons.badge),
                        textInputAction: TextInputAction.next,
                        maxLength: 100,
                      ),
                      const SizedBox(height: 16),
                      Semantics(
                        label: l10n.role,
                        child: DropdownButtonFormField<String>(
                          initialValue: _selectedRole,
                          decoration: InputDecoration(
                            labelText: l10n.role,
                            border: const OutlineInputBorder(),
                            prefixIcon: const Icon(Icons.admin_panel_settings),
                          ),
                          items: (_currentUserRole == 'admin' ? _roles : _roles.where((r) => r != 'admin').toList())
                              .map((role) => DropdownMenuItem(
                                    value: role,
                                    child: Text(l10n.getRoleTranslation(role)),
                                  ))
                              .toList(),
                          onChanged: (value) => setState(() => _selectedRole = value),
                        ),
                      ),
                      const SizedBox(height: 16),
                      SemanticTextField(
                        controller: _bioController,
                        label: l10n.bio,
                        semanticLabel: l10n.bio,
                        helperText: l10n.getValidationMessage('maxLength', args: {'max': 500}),
                        prefixIcon: const Icon(Icons.description),
                        maxLines: 3,
                        maxLength: 500,
                        textInputAction: TextInputAction.next,
                      ),
                      const SizedBox(height: 16),
                      SemanticTextField(
                        controller: _passwordController,
                        label: l10n.password,
                        semanticLabel: l10n.password,
                        helperText: l10n.getValidationMessage('minLength', args: {'min': 8}),
                        prefixIcon: const Icon(Icons.lock),
                        obscureText: _obscurePassword,
                        suffixIcon: IconButton(
                          icon: Icon(
                            _obscurePassword ? Icons.visibility : Icons.visibility_off,
                          ),
                          tooltip: _obscurePassword ? l10n.password : l10n.password,
                          onPressed: () {
                            setState(() => _obscurePassword = !_obscurePassword);
                          },
                        ),
                        textInputAction: TextInputAction.done,
                        onSubmitted: (_) => _submit(),
                        validator: (v) {
                          if (v == null || v.isEmpty) return l10n.getValidationMessage('required');
                          if (v.length < 8) return l10n.getValidationMessage('minLength', args: {'min': 8});
                          return null;
                        },
                      ),
                      const SizedBox(height: 16),
                      Semantics(
                        label: l10n.privacySettings,
                        child: Card(
                          child: Padding(
                            padding: const EdgeInsets.all(16),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(l10n.privacySettings, style: Theme.of(context).textTheme.titleMedium),
                                const SizedBox(height: 8),
                                SwitchListTile(
                                  title: Text(l10n.publicProfile),
                                  subtitle: Text(_isPublic ? l10n.visibleToAll : l10n.onlyVisibleToYou),
                                  value: _isPublic,
                                  onChanged: (v) => setState(() => _isPublic = v),
                                  contentPadding: EdgeInsets.zero,
                                ),
                                SwitchListTile(
                                  title: Text(l10n.showEmail),
                                  subtitle: Text(_isPublicEmail ? l10n.visibleToAll : l10n.onlyVisibleToYou),
                                  value: _isPublicEmail,
                                  onChanged: (v) => setState(() => _isPublicEmail = v),
                                  contentPadding: EdgeInsets.zero,
                                ),
                                SwitchListTile(
                                  title: Text(l10n.showBio),
                                  subtitle: Text(_isPublicBio ? l10n.visibleToAll : l10n.onlyVisibleToYou),
                                  value: _isPublicBio,
                                  onChanged: (v) => setState(() => _isPublicBio = v),
                                  contentPadding: EdgeInsets.zero,
                                ),
                                SwitchListTile(
                                  title: Text(l10n.showLocation),
                                  subtitle: Text(_isPublicLocation ? l10n.visibleToAll : l10n.onlyVisibleToYou),
                                  value: _isPublicLocation,
                                  onChanged: (v) => setState(() => _isPublicLocation = v),
                                  contentPadding: EdgeInsets.zero,
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: 24),
                      Semantics(
                        label: l10n.createUser,
                        child: FilledButton(
                          style: FilledButton.styleFrom(
                            padding: const EdgeInsets.symmetric(vertical: 16),
                            minimumSize: const Size.fromHeight(50),
                          ),
                          onPressed: _isLoading ? null : _submit,
                          child: _isLoading
                              ? const SizedBox(
                                  height: 20,
                                  width: 20,
                                  child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                                )
                              : Text(l10n.createUser),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}
