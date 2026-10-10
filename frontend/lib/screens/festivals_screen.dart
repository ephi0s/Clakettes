import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../models/festival_model.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import '../services/offline_cache_service.dart';
import '../widgets/reusable_widgets.dart';
import '../widgets/empty_state_widget.dart';
import '../widgets/error_state_widget.dart';
import '../widgets/loading_skeleton.dart';
import '../widgets/list_item_animation.dart';
import 'festival_profile_screen.dart';
import 'create_festival_screen.dart';
import 'login_screen.dart';

/// Pantalla que lista todos los festivales con respaldo offline y creación
/// mediante FAB.
class FestivalsScreen extends StatefulWidget {
  const FestivalsScreen({super.key});

  @override
  State<FestivalsScreen> createState() => _FestivalsScreenState();
}

/// Mantiene las listas de festivales, el estado de búsqueda/offline y el
/// estado de autenticación.
class _FestivalsScreenState extends State<FestivalsScreen> {
  final ApiService _apiService = ApiService();
  List<Festival> _allFestivals = [];
  List<Festival> _filteredFestivals = [];
  bool _isLoading = true;
  bool _hasError = false;
  bool _isOfflineData = false;
  final String _searchQuery = '';
  bool _isLoggedIn = false;
  late AppLocalizations l10n;

  @override
  void initState() {
    super.initState();
    _loadFestivals();
    _checkAuth();
  }

  Future<void> _checkAuth() async {
    final loggedIn = await AuthService().isLoggedIn();
    if (mounted) setState(() => _isLoggedIn = loggedIn);
  }

  /// Ejecuta la acción si hay sesión iniciada; si no, muestra la hoja de
  /// inicio de sesión.
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
        builder: (ctx) => LoginPromptSheet(onLogin: _navigateToLogin),
      );
    }
  }

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

  /// Carga los festivales de la API, recurriendo a la caché offline como respaldo.
  Future<void> _loadFestivals() async {
    setState(() {
      _isLoading = true;
      _hasError = false;
      _isOfflineData = false;
    });

    try {
      final result = await _apiService.getFestivals(size: 100);
      if (!mounted) return;
      setState(() {
        _allFestivals = result.items;
        _applyFilter();
        _isLoading = false;
      });
    } catch (e) {
      debugPrint('Error: $e');
      if (!mounted) return;
      final cached = OfflineCacheService.instance.get('festival');
      if (cached is List && cached.isNotEmpty) {
        _allFestivals = cached.map((j) => Festival.fromJson(Map<String, dynamic>.from(j))).toList();
        _applyFilter();
      }
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _hasError = _allFestivals.isEmpty;
        _isOfflineData = _allFestivals.isNotEmpty;
      });
    }
  }

  /// Aplica la consulta de búsqueda actual a la lista de festivales cargada.
  void _applyFilter() {
    if (_searchQuery.isEmpty) {
      _filteredFestivals = List.from(_allFestivals);
    } else {
      _filteredFestivals = _allFestivals.where((f) =>
          f.name.toLowerCase().contains(_searchQuery.toLowerCase()) ||
          (f.location?.toLowerCase().contains(_searchQuery.toLowerCase()) ?? false)).toList();
    }
  }

  @override
  Widget build(BuildContext context) {
    l10n = AppLocalizations.of(context)!;

    return Scaffold(
      body: Column(
        children: [
          if (_isOfflineData)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
              color: Theme.of(context).colorScheme.surfaceContainerHigh,
              child: Row(
                children: [
                  Icon(Icons.wifi_off_rounded, size: 14, color: Theme.of(context).colorScheme.onSurfaceVariant),
                  const SizedBox(width: 6),
                  Text(l10n.cacheData, style: TextStyle(fontSize: 12, color: Theme.of(context).colorScheme.onSurfaceVariant)),
                ],
              ),
            ),
          Expanded(child: _buildBody()),
        ],
      ),
      floatingActionButton: Semantics(
        label: '${l10n.add} ${l10n.festivals.toLowerCase()}',
        child: Tooltip(
          message: l10n.add,
          child: FloatingActionButton(
            onPressed: () => _requireAuthThen(() async {
              final result = await Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const CreateFestivalScreen()),
              );
              if (result == true) _loadFestivals();
            }),
            child: const Icon(Icons.add_rounded),
          ),
        ),
      ),
    );
  }

  Widget _buildBody() {
    if (_isLoading) return const ListSkeleton();
    if (_hasError) return ErrorStateWidget(onRetry: _loadFestivals);
    if (_filteredFestivals.isEmpty) {
      return EmptyStateWidget(
        icon: Icons.festival_rounded,
        title: l10n.noFestivals,
        subtitle: l10n.subtitle,
        actionLabel: l10n.add,
        onAction: () => _requireAuthThen(() async {
          final result = await Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => const CreateFestivalScreen()),
          );
          if (result == true) _loadFestivals();
        }),
      );
    }
    return RefreshIndicator(
      onRefresh: _loadFestivals,
      child: Semantics(
        liveRegion: true,
        label: '${l10n.festivals}: ${_filteredFestivals.length} ${l10n.festivals.toLowerCase()}',
        child: ListView.builder(
          padding: const EdgeInsets.only(bottom: 88, top: 4),
          itemCount: _filteredFestivals.length,
          itemBuilder: (context, index) {
            final festival = _filteredFestivals[index];
            return ListItemAnimation(
              index: index,
              child: ListItemCard(
                leading: Hero(
                  tag: 'festival_${festival.id}',
                  child: ProfileAvatar(
                    imageUrl: festival.logoUrl,
                    fallbackText: festival.name,
                    fallbackIcon: Icons.festival_rounded,
                    semanticLabel: '${l10n.festivalProfile}: ${festival.name}',
                  ),
                ),
                title: festival.name,
                titleSemanticLabel: '${l10n.festivals}: ${festival.name}',
                subtitle: Text(festival.location ?? l10n.noLocations),
                trailing: StatusIndicator(
                  isActive: festival.isActive,
                  activeLabel: l10n.active,
                  inactiveLabel: l10n.inactive,
                  semanticLabel: festival.isActive ? l10n.active : l10n.inactive,
                ),
                onTap: () async {
                  await Navigator.push(
                    context,
                    PageRouteBuilder(
                      transitionDuration: const Duration(milliseconds: 300),
                      pageBuilder: (_, animation, __) => FadeTransition(
                        opacity: animation,
                        child: FestivalProfileScreen(festival: festival),
                      ),
                    ),
                  );
                  _loadFestivals();
                },
                semanticLabel: '${l10n.festivals}: ${festival.name}, ${l10n.active}: ${festival.isActive ? l10n.active : l10n.inactive}, ${l10n.location}: ${festival.location ?? l10n.noLocations}',
              ),
            );
          },
        ),
      ),
    );
  }
}
