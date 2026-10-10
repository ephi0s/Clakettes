import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../models/user_model.dart';
import '../services/api_service.dart';
import '../services/offline_cache_service.dart';
import '../widgets/reusable_widgets.dart';
import '../services/auth_service.dart';
import '../widgets/empty_state_widget.dart';
import '../widgets/error_state_widget.dart';
import '../widgets/loading_skeleton.dart';
import '../widgets/list_item_animation.dart';
import 'create_user_screen.dart';
import 'login_screen.dart';
import 'user_profile_screen.dart';

/// Lista de todos los usuarios con respaldo de caché offline. Crear un
/// usuario requiere que el usuario actual tenga sesión iniciada.
class UsersScreen extends StatefulWidget {
  const UsersScreen({super.key});

  @override
  State<UsersScreen> createState() => _UsersScreenState();
}

/// Estado de [UsersScreen]. Carga los usuarios al iniciar y mantiene la lista
/// filtrada además del estado de autenticación para la creación.
class _UsersScreenState extends State<UsersScreen> {
  final ApiService _apiService = ApiService();
  List<User> _allUsers = [];
  List<User> _filteredUsers = [];
  bool _isLoading = true;
  bool _hasError = false;
  bool _isOfflineData = false;
  final String _searchQuery = '';
  bool _isLoggedIn = false;
  late AppLocalizations l10n;

  @override
  void initState() {
    super.initState();
    _loadUsers();
    _checkAuth();
  }

/// Obtiene los usuarios de la API, con respaldo de la caché offline cuando
/// la petición falla.
  Future<void> _loadUsers() async {
    setState(() {
      _isLoading = true;
      _hasError = false;
      _isOfflineData = false;
    });

    try {
      final result = await _apiService.getUsers(size: 100);
      if (!mounted) return;
      setState(() {
        _allUsers = result.items;
        _applyFilter();
        _isLoading = false;
      });
    } catch (e) {
      debugPrint('Error: $e');
      if (!mounted) return;
      final cached = OfflineCacheService.instance.get('user');
      if (cached is List && cached.isNotEmpty) {
        _allUsers = cached.map((j) => User.fromJson(Map<String, dynamic>.from(j))).toList();
        _applyFilter();
      }
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _hasError = _allUsers.isEmpty;
        _isOfflineData = _allUsers.isNotEmpty;
      });
    }
  }

  /// Recalcula la lista filtrada a partir de la búsqueda actual.
  void _applyFilter() {
    if (_searchQuery.isEmpty) {
      _filteredUsers = List.from(_allUsers);
    } else {
      _filteredUsers = _allUsers.where((u) =>
          (u.fullName?.toLowerCase().contains(_searchQuery.toLowerCase()) ?? false) ||
          u.username.toLowerCase().contains(_searchQuery.toLowerCase()) ||
          (u.email?.toLowerCase().contains(_searchQuery.toLowerCase()) ?? false)).toList();
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
        label: '${l10n.add} ${l10n.users.toLowerCase()}',
        child: FloatingActionButton(
          tooltip: l10n.add,
          onPressed: () => _requireAuthThen(() async {
            final result = await Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => const CreateUserScreen()),
            );
            if (result == true) _loadUsers();
          }),
          child: const Icon(Icons.add_rounded),
        ),
      ),
    );
  }

  /// Construye el cuerpo de la pantalla según el estado de carga y datos.
  Widget _buildBody() {
    if (_isLoading) return const ListSkeleton();
    if (_hasError) return ErrorStateWidget(onRetry: _loadUsers);
    if (_filteredUsers.isEmpty) {
      return EmptyStateWidget(
        icon: Icons.people_outline_rounded,
        title: l10n.noUsers,
        subtitle: l10n.subtitle,
        actionLabel: l10n.createUser,
        onAction: () => _requireAuthThen(() async {
          final result = await Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => const CreateUserScreen()),
          );
          if (result == true) _loadUsers();
        }),
      );
    }
    return RefreshIndicator(
      onRefresh: _loadUsers,
      child: Semantics(
        liveRegion: true,
        label: '${l10n.users}: ${_filteredUsers.length} ${l10n.users.toLowerCase()}',
        child: ListView.builder(
          padding: const EdgeInsets.only(bottom: 88, top: 4),
          itemCount: _filteredUsers.length,
          itemBuilder: (context, index) {
            final user = _filteredUsers[index];
            return ListItemAnimation(
              index: index,
              child: ListItemCard(
                leading: Hero(
                  tag: 'user_${user.id}',
                  child: ProfileAvatar(
                    imageUrl: user.avatarUrl,
                    fallbackText: user.username,
                    semanticLabel: '${l10n.viewProfile}: ${user.fullName ?? user.username}',
                  ),
                ),
                title: user.fullName ?? user.username,
                titleSemanticLabel: '${l10n.username}: ${user.fullName ?? user.username}',
                subtitle: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(user.role ?? l10n.noRole),
                    if (user.email != null)
                      Text(user.email!, style: const TextStyle(fontSize: 12)),
                  ],
                ),
                trailing: StatusIndicator(
                  isActive: user.isPublic,
                  activeLabel: l10n.public,
                  inactiveLabel: l10n.private,
                  activeIcon: Icons.public_rounded,
                  inactiveIcon: Icons.lock_rounded,
                  activeColor: Colors.blue,
                  semanticLabel: user.isPublic ? l10n.public : l10n.private,
                ),
                onTap: () async {
                  await Navigator.push(
                    context,
                    PageRouteBuilder(
                      transitionDuration: const Duration(milliseconds: 300),
                      pageBuilder: (_, animation, __) => FadeTransition(
                        opacity: animation,
                        child: UserProfileScreen(user: user, currentUser: null),
                      ),
                    ),
                  );
                  _loadUsers();
                },
                semanticLabel: '${l10n.username}: ${user.fullName ?? user.username}, ${l10n.role}: ${user.role ?? l10n.noRole}, ${l10n.publicProfile}: ${user.isPublic ? l10n.public : l10n.private}',
              ),
            );
          },
        ),
      ),
    );
  }
}
