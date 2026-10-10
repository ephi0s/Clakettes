import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../models/shortfilm_model.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import '../services/offline_cache_service.dart';
import '../widgets/empty_state_widget.dart';
import '../widgets/error_state_widget.dart';
import '../widgets/loading_skeleton.dart';
import '../widgets/list_item_animation.dart';
import 'create_shortfilm_screen.dart';
import 'login_screen.dart';
import 'shortfilm_profile_screen.dart';

/// Cuadrícula de cortometrajes con respaldo de caché offline, opcionalmente
/// acotada a un festival. Crear un cortometraje requiere iniciar sesión.
class ShortFilmsScreen extends StatefulWidget {
  final int? festivalId;
  final String? festivalName;

  const ShortFilmsScreen({super.key, this.festivalId, this.festivalName});

  @override
  State<ShortFilmsScreen> createState() => _ShortFilmsScreenState();
}

/// Estado de [ShortFilmsScreen]. Carga los cortometrajes al iniciar y
/// mantiene la lista filtrada además del estado de autenticación para la creación.
class _ShortFilmsScreenState extends State<ShortFilmsScreen> {
  final ApiService _apiService = ApiService();
  List<ShortFilm> _allShortFilms = [];
  List<ShortFilm> _filteredShortFilms = [];
  bool _isLoading = true;
  bool _hasError = false;
  bool _isOfflineData = false;
  final String _searchQuery = '';
  bool _isLoggedIn = false;
  late AppLocalizations l10n;

  @override
  void initState() {
    super.initState();
    _loadShortFilms();
    _checkAuth();
  }

/// Obtiene los cortometrajes de la API, con respaldo de la caché offline
/// cuando la petición falla.
  Future<void> _loadShortFilms() async {
    setState(() {
      _isLoading = true;
      _hasError = false;
      _isOfflineData = false;
    });

    try {
      final result = await _apiService.getShortFilms(size: 100, festivalId: widget.festivalId);
      if (!mounted) return;
      setState(() {
        _allShortFilms = result.items;
        _applyFilter();
        _isLoading = false;
      });
    } catch (e) {
      debugPrint('Error: $e');
      if (!mounted) return;
      final cached = OfflineCacheService.instance.get('shortfilm');
      if (cached is List && cached.isNotEmpty && widget.festivalId == null) {
        _allShortFilms = cached.map((j) => ShortFilm.fromJson(Map<String, dynamic>.from(j))).toList();
        _applyFilter();
      }
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _hasError = _allShortFilms.isEmpty;
        _isOfflineData = _allShortFilms.isNotEmpty;
      });
    }
  }

  /// Recalcula la lista filtrada a partir de la búsqueda actual.
  void _applyFilter() {
    if (_searchQuery.isEmpty) {
      _filteredShortFilms = List.from(_allShortFilms);
    } else {
      _filteredShortFilms = _allShortFilms.where((f) =>
          f.title.toLowerCase().contains(_searchQuery.toLowerCase()) ||
          (f.tags?.toLowerCase().contains(_searchQuery.toLowerCase()) ?? false)).toList();
    }
  }

  /// Refresca el estado de sesión usado para restringir las acciones de creación.
  Future<void> _checkAuth() async {
    final loggedIn = await AuthService().isLoggedIn();
    if (mounted) setState(() => _isLoggedIn = loggedIn);
  }

  /// Ejecuta [action] si hay sesión iniciada; si no, muestra una hoja de aviso de inicio.
  void _requireAuthThen(VoidCallback action) {
    if (_isLoggedIn) {
      action();
    } else {
      showModalBottomSheet(
        context: context,
        isScrollControlled: true,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
        ),
        builder: (ctx) => Padding(
          padding: EdgeInsets.fromLTRB(24, 24, 24, MediaQuery.of(ctx).viewInsets.bottom + 24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.primaryContainer,
                  shape: BoxShape.circle,
                ),
                child: Icon(Icons.lock_outline_rounded, size: 32, color: Theme.of(context).colorScheme.onPrimaryContainer),
              ),
              const SizedBox(height: 20),
              Text(l10n.login, style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Text(
                l10n.loginRequired,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: Theme.of(context).colorScheme.onSurfaceVariant),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 28),
              SizedBox(
                width: double.infinity,
                child: FilledButton(
                  onPressed: () {
                    Navigator.pop(ctx);
                    _navigateToLogin();
                  },
                  child: Text(l10n.login),
                ),
              ),
              const SizedBox(height: 8),
            ],
          ),
        ),
      );
    }
  }

  /// Abre la pantalla de inicio de sesión y refresca el estado de autenticación al lograrlo.
  void _navigateToLogin() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => LoginScreen(
          onLoginSuccess: () {
            Navigator.pop(context);
            _checkAuth();
          },
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Scaffold(
      appBar: widget.festivalId != null
          ? AppBar(
              title: Text(widget.festivalName ?? l10n.shortFilms),
              leading: const BackButton(),
            )
          : null,
      body: Column(
        children: [
          if (_isOfflineData)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
              color: colorScheme.surfaceContainerHigh,
              child: Row(
                children: [
                  Icon(Icons.wifi_off_rounded, size: 14, color: colorScheme.onSurfaceVariant),
                  const SizedBox(width: 6),
                  Text(l10n.cacheData, style: TextStyle(fontSize: 12, color: colorScheme.onSurfaceVariant)),
                ],
              ),
            ),
          Expanded(child: _buildBody(theme, colorScheme)),
        ],
      ),
      floatingActionButton: Semantics(
        label: '${l10n.add} ${l10n.shortFilms.toLowerCase()}',
        child: Tooltip(
          message: l10n.add,
          child: FloatingActionButton(
            onPressed: () => _requireAuthThen(() async {
              final result = await Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const CreateShortFilmScreen()),
              );
              if (result == true) _loadShortFilms();
            }),
            child: const Icon(Icons.add_rounded),
          ),
        ),
      ),
    );
  }

  /// Construye el cuerpo de la pantalla según el estado de carga y datos.
  Widget _buildBody(ThemeData theme, ColorScheme colorScheme) {
    if (_isLoading) {
      return Padding(
        padding: const EdgeInsets.all(16),
        child: GridView.builder(
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2,
            childAspectRatio: 0.75,
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
          ),
          itemCount: 6,
          itemBuilder: (_, __) => const ShimmerLoading(child: Card()),
        ),
      );
    }

    if (_hasError) return ErrorStateWidget(onRetry: _loadShortFilms);

    if (_filteredShortFilms.isEmpty) {
      return EmptyStateWidget(
        icon: Icons.movie_outlined,
        title: l10n.noShortFilms,
        subtitle: l10n.subtitle,
        actionLabel: l10n.add,
        onAction: () => _requireAuthThen(() async {
          final result = await Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => const CreateShortFilmScreen()),
          );
          if (result == true) _loadShortFilms();
        }),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadShortFilms,
      child: Semantics(
        liveRegion: true,
        label: '${l10n.shortFilms}: ${_filteredShortFilms.length} ${l10n.shortFilms.toLowerCase()}',
        child: GridView.builder(
          padding: const EdgeInsets.all(12),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2,
            childAspectRatio: 0.75,
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
          ),
          itemCount: _filteredShortFilms.length,
          itemBuilder: (context, index) {
            final shortFilm = _filteredShortFilms[index];
            return ListItemAnimation(
              index: index,
              child: Semantics(
                label: '${l10n.shortFilms}: ${shortFilm.title}${shortFilm.duration != null ? ', ${l10n.duration}: ${shortFilm.duration} ${l10n.minutes}' : ''}',
                child: Container(
                  decoration: BoxDecoration(
                    color: colorScheme.surface,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: colorScheme.outlineVariant.withAlpha(40)),
                  ),
                  clipBehavior: Clip.antiAlias,
                  child: Material(
                    color: Colors.transparent,
                    child: InkWell(
                      onTap: () async {
                        await Navigator.push(
                          context,
                          PageRouteBuilder(
                            transitionDuration: const Duration(milliseconds: 300),
                            pageBuilder: (_, animation, __) => FadeTransition(
                              opacity: animation,
                              child: ShortFilmProfileScreen(shortFilm: shortFilm),
                            ),
                          ),
                        );
                        _loadShortFilms();
                      },
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          Expanded(
                            child: shortFilm.thumbnailUrl != null
                                ? Image.network(
                                    shortFilm.thumbnailUrl!,
                                    fit: BoxFit.cover,
                                    semanticLabel: '${l10n.shortFilms}: ${shortFilm.title}',
                                    cacheWidth: (400 * MediaQuery.devicePixelRatioOf(context)).round(),
                                    errorBuilder: (_, __, ___) => Container(
                                      color: colorScheme.surfaceContainerHighest.withAlpha(80),
                                      child: Icon(Icons.movie_rounded, size: 48, color: colorScheme.onSurfaceVariant.withAlpha(100)),
                                    ),
                                  )
                                : ExcludeSemantics(
                                    child: Container(
                                      color: colorScheme.surfaceContainerHighest.withAlpha(80),
                                      child: Icon(
                                        Icons.movie_rounded,
                                        size: 48,
                                        color: colorScheme.onSurfaceVariant.withAlpha(100),
                                      ),
                                    ),
                                  ),
                          ),
                          Padding(
                            padding: const EdgeInsets.all(10),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Semantics(
                                  label: '${l10n.shortFilms}: ${shortFilm.title}',
                                  child: Text(
                                    shortFilm.title,
                                    style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w600, color: colorScheme.onSurface),
                                    maxLines: 2,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ),
                                if (shortFilm.duration != null)
                                  Semantics(
                                    label: '${l10n.duration}: ${shortFilm.duration} ${l10n.minutes}',
                                    child: Text(
                                      '${shortFilm.duration} ${l10n.minutes}',
                                      style: Theme.of(context).textTheme.labelMedium?.copyWith(color: colorScheme.onSurfaceVariant),
                                    ),
                                  ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}
