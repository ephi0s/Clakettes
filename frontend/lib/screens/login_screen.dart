import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import '../services/channel_service.dart';
import '../widgets/reusable_widgets.dart';
import '../widgets/language_picker.dart';

/// Pantalla de inicio de sesión con un formulario de usuario/contraseña y un
/// callback opcional [onLoginSuccess] que se invoca tras un inicio exitoso.
class LoginScreen extends StatefulWidget {
  final VoidCallback? onLoginSuccess;

  const LoginScreen({super.key, this.onLoginSuccess});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

/// Estado de [LoginScreen]. Mantiene los controladores del formulario, el
/// estado de carga y el mensaje de error, y controla la animación de entrada.
class _LoginScreenState extends State<LoginScreen> with SingleTickerProviderStateMixin {
  final _formKey = GlobalKey<FormState>();
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();

  bool _isLoading = false;
  bool _obscurePassword = true;
  String? _errorMessage;
  late AppLocalizations l10n;
  late AnimationController _fadeController;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;

  @override
  void initState() {
    super.initState();
    _fadeController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 700),
    );
    _fadeAnimation = CurvedAnimation(parent: _fadeController, curve: Curves.easeOut);
    _slideAnimation = Tween<Offset>(begin: const Offset(0, 0.1), end: Offset.zero)
        .animate(CurvedAnimation(parent: _fadeController, curve: Curves.easeOutCubic));
    _fadeController.forward();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    l10n = AppLocalizations.of(context)!;
  }

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    _fadeController.dispose();
    super.dispose();
  }

  /// Devuelve el nombre de dispositivo enviado con la petición de inicio de sesión.
  String _getDeviceName() {
    return l10n.webDeviceName;
  }

/// Valida el formulario, inicia sesión a través de la API, asegura que existe
/// el par de claves del usuario y notifica a [LoginScreen.onLoginSuccess].
  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final api = ApiService();
      final user = await api.login(
        _usernameController.text.trim(),
        _passwordController.text,
        deviceName: _getDeviceName(),
      );

      if (user.id != null) {
        final pubKey = await AuthService().ensureKeyPair();
        try {
          await ChannelApiService().uploadPublicKey(pubKey);
        } catch (e) {
          debugPrint('Error: $e');
        }
      }

      if (mounted) {
        widget.onLoginSuccess?.call();
      }
    } on UnauthorizedException catch (_) {
      if (mounted) {
        setState(() => _errorMessage = l10n.loginError);
      }
    } catch (e) {
      debugPrint('Error: $e');
      if (mounted) {
        setState(() => _errorMessage = l10n.loadError);
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final size = MediaQuery.of(context).size;
    final isWide = size.width > 600;

    final canPop = Navigator.of(context).canPop();
    return Scaffold(
      appBar: canPop ? AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        automaticallyImplyLeading: true,
        iconTheme: IconThemeData(color: colorScheme.onSurfaceVariant),
      ) : null,
      body: Container(
        width: double.infinity,
        height: double.infinity,
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: isWide
                ? [
                    colorScheme.primaryContainer.withAlpha(80),
                    colorScheme.surface,
                    colorScheme.tertiaryContainer.withAlpha(60),
                  ]
                : [
                    colorScheme.surface,
                    colorScheme.surface,
                  ],
            stops: isWide ? const [0.0, 0.5, 1.0] : const [0.0, 1.0],
          ),
        ),
        child: SafeArea(
          child: Center(
            child: FadeTransition(
              opacity: _fadeAnimation,
              child: SlideTransition(
                position: _slideAnimation,
                child: SingleChildScrollView(
                  padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 48),
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 400),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        _buildHeader(theme, colorScheme),
                        const SizedBox(height: 36),
                        Container(
                          decoration: BoxDecoration(
                            color: colorScheme.surface,
                            borderRadius: BorderRadius.circular(20),
                            border: Border.all(color: colorScheme.outlineVariant.withAlpha(40)),
                          ),
                          child: Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 32),
                            child: Form(
                              key: _formKey,
                              autovalidateMode: AutovalidateMode.onUserInteraction,
                              child: Column(
                                children: [
                                  Text(l10n.login, style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
                                  const SizedBox(height: 24),
                                  SemanticTextField(
                                    controller: _usernameController,
                                    label: l10n.username,
                                    semanticLabel: l10n.username,
                                    helperText: ' ',
                                    prefixIcon: Icon(Icons.person_outline_rounded, color: colorScheme.primary, size: 20),
                                    textInputAction: TextInputAction.next,
                                    maxLength: 50,
                                    validator: (v) {
                                      if (v == null || v.trim().isEmpty) {
                                        return l10n.getValidationMessage('required');
                                      }
                                      return null;
                                    },
                                  ),
                                  const SizedBox(height: 16),
                                  SemanticTextField(
                                    controller: _passwordController,
                                    label: l10n.password,
                                    semanticLabel: l10n.password,
                                    helperText: ' ',
                                    prefixIcon: Icon(Icons.lock_outline_rounded, color: colorScheme.primary, size: 20),
                                    obscureText: _obscurePassword,
                                    suffixIcon: IconButton(
                                      icon: Icon(_obscurePassword ? Icons.visibility_outlined : Icons.visibility_off_outlined, size: 20),
                                      tooltip: l10n.password,
                                      onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
                                    ),
                                    textInputAction: TextInputAction.done,
                                    onSubmitted: (_) => _submit(),
                                    validator: (v) {
                                      if (v == null || v.isEmpty) {
                                        return l10n.getValidationMessage('required');
                                      }
                                      return null;
                                    },
                                  ),
                                  const SizedBox(height: 16),
                                  Visibility(
                                    visible: _errorMessage != null,
                                    maintainSize: true,
                                    maintainAnimation: true,
                                    maintainState: true,
                                    child: _errorMessage != null
                                        ? _buildError(colorScheme)
                                        : const SizedBox(width: double.infinity, height: 46),
                                  ),
                                  const SizedBox(height: 28),
                                  SizedBox(
                                    width: double.infinity,
                                    child: FilledButton(
                                      onPressed: _isLoading ? null : _submit,
                                      child: _isLoading
                                          ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                                          : Text(l10n.login, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(height: 24),
                        Text(l10n.appTitle, style: theme.textTheme.bodySmall?.copyWith(color: colorScheme.onSurfaceVariant, letterSpacing: 0.5)),
                        const SizedBox(height: 8),
                        TextButton.icon(
                          onPressed: () => showLanguagePicker(context),
                          icon: const Icon(Icons.language, size: 18),
                          label: Text(l10n.language),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  /// Cabecera con el logo, el título de la app y el subtítulo de acceso.
  Widget _buildHeader(ThemeData theme, ColorScheme colorScheme) {
    return Column(
      children: [
        Container(
          width: 80,
          height: 80,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            gradient: LinearGradient(
              colors: [colorScheme.primary, colorScheme.tertiary],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            boxShadow: [
              BoxShadow(color: colorScheme.primary.withAlpha(60), blurRadius: 16, offset: const Offset(0, 6)),
            ],
          ),
          child: const Icon(Icons.movie_filter_rounded, size: 40, color: Colors.white),
        ),
        const SizedBox(height: 18),
        Text(
          l10n.appTitle,
          style: theme.textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold, letterSpacing: -0.5),
        ),
        const SizedBox(height: 6),
        Text(
          l10n.loginTitle,
          style: theme.textTheme.bodyLarge?.copyWith(color: colorScheme.onSurfaceVariant),
        ),
      ],
    );
  }

  /// Muestra el mensaje de error de inicio de sesión.
  Widget _buildError(ColorScheme colorScheme) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: colorScheme.errorContainer.withAlpha(140),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Icon(Icons.error_outline_rounded, size: 20, color: colorScheme.onErrorContainer),
          const SizedBox(width: 10),
          Expanded(
            child: Text(_errorMessage!, style: TextStyle(color: colorScheme.onErrorContainer, fontSize: 14)),
          ),
        ],
      ),
    );
  }
}
