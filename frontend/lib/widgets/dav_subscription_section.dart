import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../l10n/app_localizations.dart';
import '../models/calendar_model.dart';
import '../services/api_service.dart';
import '../widgets/empty_state_widget.dart';
import '../widgets/error_state_widget.dart';
import '../widgets/reusable_widgets.dart';

/// Sección de suscripción CalDAV de la agenda en un cliente externo.
///
/// Permite generar, regenerar y revocar el token de acceso que da acceso a las
/// colecciones `/dav/<token>/calendars/`. El token solo se muestra una vez,
/// nada más crearlo o regenerarlo: [_revealedToken] se descarta al revocar o al
/// regenerar, y nunca se vuelve a pedir al backend.
///
/// Las direcciones CalDAV y webcal se construyen en cliente a partir de
/// [ApiService.rootUrl], ya que el backend no las devuelve.
class DavSubscriptionSection extends StatefulWidget {
  const DavSubscriptionSection({super.key});

  @override
  State<DavSubscriptionSection> createState() => _DavSubscriptionSectionState();
}

class _DavSubscriptionSectionState extends State<DavSubscriptionSection> {
  final ApiService _api = ApiService();

  bool _isLoading = true;

  /// Hay una petición de generación o revocación en curso.
  bool _isBusy = false;
  bool _hasError = false;
  bool _hasToken = false;
  List<DavCollection> _collections = const [];

  /// Token recién generado; se conserva solo mientras esta vista siga montada.
  String? _revealedToken;

  /// Raíz del backend sin el prefijo `/api` ni barra final, que es la base de
  /// las rutas DAV.
  String get _davBase {
    var base = _api.rootUrl.trim().replaceFirst(RegExp(r'/api/?$'), '');
    if (base.endsWith('/')) base = base.substring(0, base.length - 1);
    return base;
  }

  /// Dirección CalDAV de [collection] (Apple Calendar, Thunderbird, Google).
  String _calDavUrl(String token, DavCollection collection) {
    return '$_davBase/dav/$token/calendars/${collection.name}/';
  }

  /// Dirección webcal de [collection] (suscripción de solo lectura).
  String _webcalUrl(String token, DavCollection collection) {
    final url = '$_davBase/dav/$token/calendars/${collection.name}.ics';
    if (url.startsWith('https://')) return 'webcal://${url.substring(8)}';
    if (url.startsWith('http://')) return 'webcal://${url.substring(7)}';
    return url;
  }

  @override
  void initState() {
    super.initState();
    _loadStatus();
  }

  /// Consulta el estado del token DAV del usuario.
  Future<void> _loadStatus() async {
    setState(() {
      _isLoading = true;
      _hasError = false;
      _revealedToken = null;
    });
    try {
      final status = await _api.getDavTokenStatus();
      if (!mounted) return;
      setState(() {
        _hasToken = status.hasToken;
        _collections = status.collections;
        _isLoading = false;
      });
    } catch (e) {
      debugPrint('DavSubscriptionSection load error: $e');
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _hasError = true;
      });
    }
  }

  /// Genera o regenera el token y lo revela una única vez.
  Future<void> _generateToken() async {
    final l10n = AppLocalizations.of(context);
    if (l10n == null) return;
    setState(() => _isBusy = true);
    try {
      final created = await _api.createDavToken();
      if (!mounted) return;
      setState(() {
        _hasToken = true;
        _collections = created.collections;
        _revealedToken = created.token;
        _isBusy = false;
      });
      _showMessage(l10n.davTokenGenerated);
    } catch (e) {
      debugPrint('DavSubscriptionSection generate error: $e');
      if (!mounted) return;
      setState(() => _isBusy = false);
      _showMessage(l10n.errorFor(e));
    }
  }

  /// Pide confirmación y revoca el token, descartando el revelado.
  Future<void> _revokeToken() async {
    final l10n = AppLocalizations.of(context);
    if (l10n == null) return;
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(l10n.davRevokeToken),
        content: Text(l10n.davRevokeTokenConfirm),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: Text(l10n.cancel),
          ),
          TextButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: TextButton.styleFrom(foregroundColor: Theme.of(ctx).colorScheme.error),
            child: Text(l10n.davRevokeToken),
          ),
        ],
      ),
    );
    if (confirmed != true || !mounted) return;
    setState(() => _isBusy = true);
    try {
      final status = await _api.revokeDavToken();
      if (!mounted) return;
      setState(() {
        _hasToken = status.hasToken;
        _collections = status.collections;
        _revealedToken = null;
        _isBusy = false;
      });
      _showMessage(l10n.davTokenRevoked);
    } catch (e) {
      debugPrint('DavSubscriptionSection revoke error: $e');
      if (!mounted) return;
      setState(() => _isBusy = false);
      _showMessage(l10n.errorFor(e));
    }
  }

  /// Copia [url] al portapapeles y confirma la acción.
  Future<void> _copyUrl(String url) async {
    final l10n = AppLocalizations.of(context);
    if (l10n == null) return;
    await Clipboard.setData(ClipboardData(text: url));
    if (!mounted) return;
    _showMessage(l10n.davUrlCopied);
  }

  void _showMessage(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), behavior: SnackBarBehavior.floating),
    );
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Semantics(
      container: true,
      label: l10n.davSubscriptionTitle,
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  ExcludeSemantics(
                    child: Icon(Icons.sync_alt, size: 20, color: colorScheme.primary),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: SemanticHeader(
                      text: l10n.davSubscriptionTitle,
                      style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                l10n.davSubscriptionIntro,
                style: theme.textTheme.bodyMedium?.copyWith(color: colorScheme.onSurfaceVariant),
              ),
              const SizedBox(height: 16),
              if (_isLoading)
                const Center(
                  child: Padding(
                    padding: EdgeInsets.all(16),
                    child: CircularProgressIndicator(),
                  ),
                )
              else if (_hasError)
                ErrorStateWidget(onRetry: _loadStatus)
              else if (_revealedToken != null)
                _buildTokenReveal(l10n, theme, colorScheme)
              else if (_hasToken)
                _buildActive(l10n, theme, colorScheme)
              else
                _buildInactive(l10n, theme, colorScheme),
            ],
          ),
        ),
      ),
    );
  }

  /// Estado sin token: explicación y una única acción de generación.
  Widget _buildInactive(AppLocalizations l10n, ThemeData theme, ColorScheme colorScheme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        StatusIndicator(
          isActive: false,
          activeLabel: l10n.davTokenActive,
          inactiveLabel: l10n.davTokenInactive,
          inactiveIcon: Icons.lock_outline_rounded,
          semanticLabel: l10n.davTokenInactive,
        ),
        const SizedBox(height: 12),
        FilledButton.icon(
          onPressed: _isBusy ? null : _generateToken,
          icon: _busyIcon() ?? const Icon(Icons.vpn_key_outlined, size: 18),
          label: Text(l10n.davGenerateToken),
        ),
      ],
    );
  }

  /// Estado con token activo: estado, colecciones y acciones de regenerar/revocar.
  Widget _buildActive(AppLocalizations l10n, ThemeData theme, ColorScheme colorScheme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        StatusIndicator(
          isActive: true,
          activeLabel: l10n.davTokenActive,
          inactiveLabel: l10n.davTokenInactive,
          activeIcon: Icons.verified_user_outlined,
          semanticLabel: l10n.davTokenActive,
        ),
        const SizedBox(height: 16),
        _buildCollections(l10n, theme, colorScheme),
        Wrap(
          spacing: 12,
          runSpacing: 8,
          children: [
            OutlinedButton.icon(
              onPressed: _isBusy ? null : _generateToken,
              icon: _busyIcon() ?? const Icon(Icons.refresh_rounded, size: 18),
              label: Text(l10n.davRegenerateToken),
            ),
            TextButton.icon(
              onPressed: _isBusy ? null : _revokeToken,
              icon: _busyIcon() ?? const Icon(Icons.link_off_rounded, size: 18),
              label: Text(l10n.davRevokeToken),
              style: TextButton.styleFrom(foregroundColor: colorScheme.error),
            ),
          ],
        ),
      ],
    );
  }

  /// Token revelado: advertencia, token en crudo y direcciones por colección.
  Widget _buildTokenReveal(AppLocalizations l10n, ThemeData theme, ColorScheme colorScheme) {
    final token = _revealedToken!;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Semantics(
          container: true,
          liveRegion: true,
          label: l10n.davTokenWarning,
          child: Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: colorScheme.errorContainer.withAlpha(120),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                ExcludeSemantics(
                  child: Icon(Icons.warning_amber_rounded, size: 20, color: colorScheme.error),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    l10n.davTokenWarning,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: colorScheme.onErrorContainer,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),
        Semantics(
          container: true,
          label: token,
          child: Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
            decoration: BoxDecoration(
              color: colorScheme.surfaceContainerHighest,
              borderRadius: BorderRadius.circular(8),
            ),
            child: SelectableText(
              token,
              style: theme.textTheme.bodyMedium?.copyWith(fontFamily: 'monospace'),
            ),
          ),
        ),
        const SizedBox(height: 16),
        _buildCollections(l10n, theme, colorScheme, token: token),
        Wrap(
          spacing: 12,
          runSpacing: 8,
          children: [
            OutlinedButton.icon(
              onPressed: _isBusy ? null : _generateToken,
              icon: _busyIcon() ?? const Icon(Icons.refresh_rounded, size: 18),
              label: Text(l10n.davRegenerateToken),
            ),
            TextButton.icon(
              onPressed: _isBusy ? null : _revokeToken,
              icon: _busyIcon() ?? const Icon(Icons.link_off_rounded, size: 18),
              label: Text(l10n.davRevokeToken),
              style: TextButton.styleFrom(foregroundColor: colorScheme.error),
            ),
          ],
        ),
      ],
    );
  }

  /// Lista de colecciones disponibles; sin token revelado solo muestra el nombre.
  Widget _buildCollections(
    AppLocalizations l10n,
    ThemeData theme,
    ColorScheme colorScheme, {
    String? token,
  }) {
    if (_collections.isEmpty) {
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: 16),
        child: EmptyStateWidget(
          icon: Icons.event_busy_outlined,
          title: l10n.davNoCollections,
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(bottom: 8),
          child: SemanticHeader(
            text: l10n.davCollection,
            style: theme.textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.w700,
              color: colorScheme.onSurfaceVariant,
            ),
          ),
        ),
        for (final collection in _collections)
          Semantics(
            container: true,
            label: '${l10n.davCollection}: ${collection.displayName}',
            child: Padding(
              padding: const EdgeInsets.only(bottom: 16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      ExcludeSemantics(
                        child: Icon(Icons.calendar_today_outlined, size: 18, color: colorScheme.primary),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          collection.displayName,
                          style: theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w600),
                        ),
                      ),
                    ],
                  ),
                  if ((collection.description ?? '').isNotEmpty) ...[
                    const SizedBox(height: 4),
                    Text(
                      collection.description!,
                      style: theme.textTheme.bodySmall?.copyWith(color: colorScheme.onSurfaceVariant),
                    ),
                  ],
                  if (token != null) ...[
                    const SizedBox(height: 8),
                    _buildUrlRow(l10n, theme, colorScheme, l10n.davCalDavUrl, _calDavUrl(token, collection)),
                    const SizedBox(height: 8),
                    _buildUrlRow(l10n, theme, colorScheme, l10n.davWebCalUrl, _webcalUrl(token, collection)),
                  ],
                ],
              ),
            ),
          ),
      ],
    );
  }

  /// Fila con una dirección de suscripción y su botón de copiar.
  Widget _buildUrlRow(
    AppLocalizations l10n,
    ThemeData theme,
    ColorScheme colorScheme,
    String label,
    String url,
  ) {
    return Semantics(
      container: true,
      label: '$label: $url',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: theme.textTheme.labelMedium?.copyWith(color: colorScheme.onSurfaceVariant),
          ),
          const SizedBox(height: 4),
          Row(
            children: [
              Expanded(
                child: Container(
                  width: double.infinity,
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                  decoration: BoxDecoration(
                    color: colorScheme.surfaceContainerHighest,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: SelectableText(
                    url,
                    style: theme.textTheme.bodySmall?.copyWith(fontFamily: 'monospace'),
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Semantics(
                label: l10n.davCopyUrl,
                child: Tooltip(
                  message: l10n.davCopyUrl,
                  child: IconButton(
                    icon: const Icon(Icons.copy_rounded, size: 18),
                    onPressed: () => _copyUrl(url),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  /// Spinner reutilizable para los botones en vuelo, o `null` si no hay ninguno.
  Widget? _busyIcon() {
    if (!_isBusy) return null;
    return const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2));
  }
}