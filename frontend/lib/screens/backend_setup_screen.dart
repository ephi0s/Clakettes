import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../services/backend_config.dart';
import '../services/api_service.dart';

/// Pantalla para configurar la URL de la API del backend y probar la conectividad.
///
/// Se usa en el primer arranque (bloquea la navegación) o manualmente desde los ajustes.
class BackendSetupScreen extends StatefulWidget {
  final String initialUrl;
  final bool onStartup;
  final VoidCallback? onConfigured;

  const BackendSetupScreen({
    super.key,
    this.initialUrl = BackendConfig.defaultUrl,
    this.onStartup = false,
    this.onConfigured,
  });

  @override
  State<BackendSetupScreen> createState() => _BackendSetupScreenState();
}

/// Mantiene el controlador de la URL y el estado de prueba/guardado de conexión.
class _BackendSetupScreenState extends State<BackendSetupScreen> {
  late TextEditingController _urlController;
  bool _isTesting = false;
  bool? _isConnected;
  bool _isSaved = false;
  late AppLocalizations l10n;

  @override
  void initState() {
    super.initState();
    _urlController = TextEditingController(text: widget.initialUrl);
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    l10n = AppLocalizations.of(context)!;
  }

  @override
  void dispose() {
    _urlController.dispose();
    super.dispose();
  }

  /// Establece la URL base y realiza una comprobación de salud contra el backend.
  Future<void> _testConnection() async {
    setState(() {
      _isTesting = true;
      _isConnected = null;
    });

    final url = _urlController.text.trim();
    if (url.isNotEmpty) {
      ApiService().setBaseUrl(url);
    }
    final ok = await ApiService().healthCheck();

    if (mounted) {
      setState(() {
        _isTesting = false;
        _isConnected = ok;
      });
    }
  }

  /// Persiste la URL configurada e invoca el callback o cierra la pantalla.
  Future<void> _save() async {
    final url = _urlController.text.trim();
    if (url.isEmpty) return;

    await BackendConfig.setUrl(url);
    ApiService().setBaseUrl(url);
    if (mounted) {
      setState(() => _isSaved = true);
      if (widget.onConfigured != null) {
        widget.onConfigured!.call();
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.success), behavior: SnackBarBehavior.floating),
        );
        Navigator.of(context).pop(true);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return PopScope(
      canPop: !widget.onStartup,
      child: Scaffold(
        body: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 480),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  ExcludeSemantics(
                    child: Container(
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        color: colorScheme.primary.withAlpha(25),
                        shape: BoxShape.circle,
                      ),
                      child: Icon(Icons.dns, size: 48, color: colorScheme.primary),
                    ),
                  ),
                  const SizedBox(height: 24),
                  Semantics(
                    header: true,
                    child: Text(
                      l10n.configureBackend,
                      style: theme.textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    l10n.backendUrlHint,
                    style: theme.textTheme.bodyMedium?.copyWith(color: colorScheme.onSurfaceVariant),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 32),
                  Semantics(
                    label: l10n.backendUrl,
                    child: TextField(
                      controller: _urlController,
                      decoration: InputDecoration(
                        labelText: l10n.backendUrl,
                        hintText: 'http://192.168.1.100:8000',
                        border: const OutlineInputBorder(),
                        prefixIcon: const Icon(Icons.link),
                        suffixIcon: _isSaved
                            ? Icon(Icons.check_circle, color: colorScheme.primary)
                            : null,
                      ),
                      keyboardType: TextInputType.url,
                      textInputAction: TextInputAction.go,
                      onSubmitted: (_) => _testConnection(),
                    ),
                  ),
                  const SizedBox(height: 16),
                  if (_isConnected != null)
                    Semantics(
                      label: _isConnected! ? l10n.connectionSuccess : l10n.connectionFailed,
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                        decoration: BoxDecoration(
                          color: _isConnected!
                              ? colorScheme.primaryContainer
                              : colorScheme.errorContainer,
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Row(
                          children: [
                            Icon(
                              _isConnected! ? Icons.check_circle : Icons.error,
                              color: _isConnected! ? colorScheme.primary : colorScheme.error,
                              size: 20,
                            ),
                            const SizedBox(width: 8),
                            Text(
                              _isConnected! ? l10n.connectionSuccess : l10n.connectionFailed,
                              style: TextStyle(
                                color: _isConnected! ? Colors.green : Colors.red,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  const SizedBox(height: 24),
                  Row(
                    children: [
                      Expanded(
                        child: Semantics(
                          label: l10n.testConnection,
                          child: OutlinedButton.icon(
                            onPressed: _isTesting ? null : _testConnection,
                            icon: _isTesting
                                ? const SizedBox(
                                    width: 16,
                                    height: 16,
                                    child: CircularProgressIndicator(strokeWidth: 2),
                                  )
                                : const Icon(Icons.wifi_find),
                            label: Text(l10n.testConnection),
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Semantics(
                          label: l10n.saveAndContinue,
                          child: FilledButton.icon(
                            onPressed: _isSaved || widget.onStartup ? _save : null,
                            icon: const Icon(Icons.save),
                            label: Text(l10n.saveAndContinue),
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
