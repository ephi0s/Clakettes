import 'dart:async';
import 'package:flutter/material.dart';
import 'l10n/app_localizations.dart';
import 'services/offline_cache_service.dart';
import 'services/sync_queue_service.dart';
import 'services/connectivity_monitor.dart';
import 'screens/dashboard_screen.dart';
import 'screens/festivals_screen.dart';
import 'screens/users_screen.dart';
import 'screens/shortfilms_screen.dart';
import 'screens/channels_screen.dart';
import 'screens/locations_screen.dart';
import 'screens/admin_screen.dart';
import 'screens/notifications_screen.dart';
import 'screens/login_screen.dart';
import 'screens/backend_setup_screen.dart';
import 'screens/form_definitions_screen.dart';
import 'screens/calendar_screen.dart';
import 'services/api_service.dart';
import 'services/auth_service.dart';
import 'services/locale_service.dart';
import 'models/user_model.dart';
import 'widgets/reusable_widgets.dart';
import 'widgets/language_picker.dart';

/// Scaffold de navegación principal con layout responsive.
///
/// Características:
/// - NavigationRail en pantallas anchas (>800px), NavigationBar en estrechas
/// - Drawer persistente para navegación en todos los tamaños
/// - Banner offline con acción de sincronización
/// - Pestañas protegidas por autenticación (Users, Chat, Locations, Admin, Notifications, Forms)
/// - Diálogo de búsqueda global
/// - Monitorización de conectividad con auto-sync al reconectar
class MainScaffold extends StatefulWidget {
  const MainScaffold({super.key});

  /// Establecer a true en los entry points de test para omitir el health check del backend al arrancar.
  static bool skipBackendCheck = false;

  @override
  State<MainScaffold> createState() => _MainScaffoldState();
}

class _MainScaffoldState extends State<MainScaffold> with WidgetsBindingObserver {
  int _selectedIndex = 0;
  User? _currentUser;
  late AppLocalizations l10n;
  /// Widgets de pantalla cacheados (inicialización diferida)
  final List<Widget?> _screens = List.filled(10, null);
  bool _initialized = false;
  int _unreadNotificationCount = 0;
  bool _isOffline = false;
  StreamSubscription? _connectivitySubscription;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _isOffline = !ConnectivityMonitor.instance.isOnline;
    _connectivitySubscription = ConnectivityMonitor.instance.onStatusChanged.listen(_onConnectivityChanged);
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _connectivitySubscription?.cancel();
    super.dispose();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    l10n = AppLocalizations.of(context)!;
    if (!_initialized) {
      _initialized = true;
      _loadCurrentUser();
      _checkBackend();
    }
  }

  /// Carga el usuario actual desde AuthService (sesión persistida).
  /// Si el usuario cambió, limpia la caché de pantallas y recarga el contador de no leídos.
  Future<void> _loadCurrentUser() async {
    final user = await AuthService().getCurrentUser();
    if (mounted) {
      final changed = _currentUser?.id != user?.id;
      _currentUser = user;
      if (changed) {
        _screens.fillRange(0, _screens.length, null);
        setState(() {});
        if (user != null) _loadUnreadCount();
      }
    }
  }

  /// Obtiene el contador de notificaciones no leídas del usuario actual.
  Future<void> _loadUnreadCount() async {
    if (_currentUser == null) return;
    try {
      final count = await ApiService().getUnreadNotificationCount();
      if (mounted) setState(() => _unreadNotificationCount = count);
    } catch (e) { debugPrint('Error: $e'); }
  }

  /// Comprueba la salud del backend al arrancar; muestra la pantalla de configuración si no es accesible.
  Future<void> _checkBackend() async {
    if (MainScaffold.skipBackendCheck) return;
    final ok = await ApiService().healthCheck();
    if (!ok && mounted) {
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => const BackendSetupScreen(onStartup: true),
          fullscreenDialog: true,
        ),
      );
    }
  }

  /// Gestiona los cambios de conectividad del stream de ConnectivityMonitor.
  void _onConnectivityChanged(bool online) {
    if (!mounted) return;
    setState(() => _isOffline = !online);
    if (online) {
      _onReconnected();
    } else {
      _onDisconnected();
    }
  }

  /// Muestra un snackbar offline cuando se pierde la conexión.
  void _onDisconnected() {
    if (!mounted) return;
    final colorScheme = Theme.of(context).colorScheme;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            Icon(Icons.wifi_off_rounded, color: colorScheme.onSurfaceVariant, size: 18),
            const SizedBox(width: 12),
            Expanded(child: Text(l10n.offline)),
          ],
        ),
        backgroundColor: colorScheme.surfaceContainerHigh,
        behavior: SnackBarBehavior.floating,
        duration: const Duration(seconds: 5),
      ),
    );
  }

  /// Muestra un snackbar de reconexión con acción de sincronización opcional si hay cambios pendientes.
  void _onReconnected() {
    if (!mounted) return;
    final colorScheme = Theme.of(context).colorScheme;
    final pending = SyncQueueService.instance.pendingCount;
    final hasPendingChanges = pending > 0;

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            Icon(Icons.wifi_rounded, color: colorScheme.onPrimary, size: 18),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                hasPendingChanges
                    ? '${l10n.online}. ${l10n.syncPending.replaceAll('{count}', pending.toString())}.'
                    : l10n.online,
              ),
            ),
            if (hasPendingChanges) ...[
              TextButton(
                onPressed: () => _performSync(),
                child: Text(l10n.syncNow, style: TextStyle(color: colorScheme.onPrimary, fontWeight: FontWeight.bold, fontSize: 13)),
              ),
              TextButton(
                onPressed: () => ScaffoldMessenger.of(context).hideCurrentSnackBar(),
                child: Text(l10n.syncLater, style: TextStyle(color: colorScheme.onPrimary.withAlpha(180), fontSize: 13)),
              ),
            ],
          ],
        ),
        backgroundColor: colorScheme.primary,
        behavior: SnackBarBehavior.floating,
        duration: hasPendingChanges ? const Duration(seconds: 15) : const Duration(seconds: 4),
      ),
    );
  }

  /// Ejecuta la sincronización completa mediante SyncQueueService; muestra snackbars de progreso/resultado.
  Future<void> _performSync() async {
    if (!mounted) return;
    final colorScheme = Theme.of(context).colorScheme;
    ScaffoldMessenger.of(context).hideCurrentSnackBar();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2, color: colorScheme.onPrimary)),
            const SizedBox(width: 12),
            Text(l10n.syncing),
          ],
        ),
        backgroundColor: colorScheme.primary,
        behavior: SnackBarBehavior.floating,
        duration: const Duration(seconds: 30),
      ),
    );

    final messenger = ScaffoldMessenger.of(context);
    final result = await SyncQueueService.instance.syncAll();

    if (!mounted) return;
    messenger.hideCurrentSnackBar();

    if (result['failed'] == 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Row(
            children: [
              Icon(Icons.check_circle_rounded, color: colorScheme.onPrimary, size: 18),
              const SizedBox(width: 12),
              Expanded(child: Text(l10n.syncSuccess)),
            ],
          ),
          backgroundColor: colorScheme.primary,
          behavior: SnackBarBehavior.floating,
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Row(
            children: [
              Icon(Icons.error_outline_rounded, color: colorScheme.onError, size: 18),
              const SizedBox(width: 12),
              Expanded(
                child: Text(l10n.syncFailed.replaceAll('{count}', result['failed'].toString())),
              ),
            ],
          ),
          backgroundColor: colorScheme.error,
          behavior: SnackBarBehavior.floating,
          duration: const Duration(seconds: 8),
        ),
      );
    }
  }

  /// Navega al índice de pestaña, protegiendo tras el login las pestañas que requieren autenticación.
  /// Requieren autenticación: Users(2), Chat(4), Locations(5), Admin(6), Notifications(7), Forms(8), Calendar(9)
  /// La pestaña Admin además requiere rol de administrador.
  void _navigateToScreen(int screenIndex) {
    if (_currentUser == null && (screenIndex == 2 || screenIndex == 4 || screenIndex == 5 || screenIndex == 6 || screenIndex == 7 || screenIndex == 8 || screenIndex == 9)) {
      _showLoginPrompt();
      return;
    }
    if (screenIndex == 6 && _currentUser?.role?.toLowerCase() != 'admin') {
      return;
    }
    setState(() => _selectedIndex = screenIndex);
  }

  /// Muestra el bottom sheet de inicio de sesión para acceder a pestañas sin autenticar.
  void _showLoginPrompt() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) => LoginPromptSheet(onLogin: _navigateToLogin),
    );
  }

  /// Abre LoginScreen; al tener éxito, cierra el prompt y recarga el usuario.
  void _navigateToLogin() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => LoginScreen(
          onLoginSuccess: () {
            Navigator.pop(context);
            _loadCurrentUser();
          },
        ),
      ),
    );
  }

  /// Diálogo de búsqueda global con llamadas a la API con debounce.
  /// Busca en festivales, usuarios, cortometrajes, etc.
  void _showSearchDialog() {
    final controller = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) {
        Map<String, dynamic>? lastResults;
        bool searching = false;

        return StatefulBuilder(
          builder: (ctx, setDialogState) {
            Future<void> performSearch(String q) async {
              if (q.trim().isEmpty) return;
              setDialogState(() { searching = true; });
              try {
                final results = await ApiService().search(q.trim());
                if (ctx.mounted) setDialogState(() { lastResults = results; searching = false; });
              } catch (e) {
                debugPrint('Error: $e');
                if (ctx.mounted) setDialogState(() { searching = false; });
              }
            }

            return AlertDialog(
              title: Semantics(header: true, child: Text(l10n.search)),
              content: SizedBox(
                width: 420,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    TextField(
                      controller: controller,
                      autofocus: true,
                      decoration: InputDecoration(
                        hintText: l10n.search,
                        prefixIcon: const Icon(Icons.search_rounded, size: 20),
                      ),
                      textInputAction: TextInputAction.search,
                      onSubmitted: (q) => performSearch(q),
                    ),
                    if (searching) ...[
                      const SizedBox(height: 20),
                      const Center(child: CircularProgressIndicator(strokeWidth: 2.5)),
                    ],
                    if (lastResults != null && !searching) ...[
                      const SizedBox(height: 16),
                      ...lastResults!.entries.map((entry) {
                        if (entry.value is List && (entry.value as List).isEmpty) {
                          return const SizedBox.shrink();
                        }
                        final label = entry.key;
                        final items = entry.value as List? ?? [];
                        return Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            if (items.isNotEmpty) ...[
                              Padding(
                                padding: const EdgeInsets.only(top: 8, bottom: 4),
                                child: Text(label, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13, letterSpacing: 0.5)),
                              ),
                              ...items.take(5).map((item) {
                                String title;
                                if (item is Map) {
                                  title = (item['name'] ?? item['title'] ?? item['username'] ?? item['id']).toString();
                                } else {
                                  title = item.toString();
                                }
                                return ListTile(
                                  dense: true,
                                  leading: const Icon(Icons.search_rounded, size: 18),
                                  title: Text(title, maxLines: 1, overflow: TextOverflow.ellipsis),
                                );
                              }),
                            ],
                          ],
                        );
                      }),
                    ],
                    if (lastResults != null && lastResults!.isEmpty && !searching)
                      Padding(
                        padding: const EdgeInsets.only(top: 20),
                        child: Text(l10n.noUsers, style: TextStyle(color: Theme.of(ctx).colorScheme.onSurfaceVariant)),
                      ),
                  ],
                ),
              ),
              actions: [
                TextButton(onPressed: () => Navigator.pop(ctx), child: Text(l10n.close)),
              ],
            );
          },
        );
      },
    ).then((_) => controller.dispose());
  }

  /// Fábrica de pantallas diferida: crea los widgets de pantalla en el primer acceso y los cachea.
  /// Mapa de índices: 0=Dashboard, 1=Festivals, 2=Users, 3=ShortFilms, 4=Chat,
  /// 5=Locations, 6=Admin, 7=Notifications, 8=FormDefinitions, 9=Calendar
  Widget _getScreenWidget(int index) {
    if (index < 0 || index >= _screens.length) return const DashboardScreen();
    _screens[index] ??= switch (index) {
      0 => DashboardScreen(onNavigateToTab: (i) => _navigateToScreen(i)),
      1 => const FestivalsScreen(),
      2 => const UsersScreen(),
      3 => const ShortFilmsScreen(),
      4 => ChannelsScreen(currentUser: _currentUser),
      5 => const LocationsScreen(),
      6 => const AdminScreen(),
       7 => const NotificationsScreen(key: ValueKey('notifications')),
       8 => const FormDefinitionsScreen(),
       9 => const CalendarScreen(),
      _ => const DashboardScreen(),
    };
    return _screens[index] ?? const DashboardScreen();
  }

  /// Construye los items de navegación según el estado de autenticación y el rol del usuario.
  /// Públicas: Dashboard, Festivals, ShortFilms
  /// Autenticadas: Calendar, Users, Chat, Locations, Notifications, Forms
  /// Solo admin: Admin
  List<_NavItem> get _visibleNavItems => [
        _NavItem(icon: Icons.dashboard_rounded, label: l10n.dashboard, semanticLabel: l10n.dashboard, screenIndex: 0),
        _NavItem(icon: Icons.festival_rounded, label: l10n.festivals, semanticLabel: l10n.festivals, screenIndex: 1),
        _NavItem(icon: Icons.movie_rounded, label: l10n.shortFilms, semanticLabel: l10n.shortFilms, screenIndex: 3),
        if (_currentUser != null)
          _NavItem(icon: Icons.calendar_month_outlined, label: l10n.calendar, semanticLabel: l10n.calendar, screenIndex: 9),
        if (_currentUser != null)
          _NavItem(icon: Icons.people_rounded, label: l10n.users, semanticLabel: l10n.users, screenIndex: 2),
        if (_currentUser != null)
          _NavItem(icon: Icons.chat_rounded, label: l10n.chat, semanticLabel: l10n.chat, screenIndex: 4),
        if (_currentUser != null)
          _NavItem(icon: Icons.location_on_rounded, label: l10n.locations, semanticLabel: l10n.locations, screenIndex: 5),
        if (_currentUser?.role?.toLowerCase() == 'admin')
          _NavItem(icon: Icons.admin_panel_settings_rounded, label: l10n.admin, semanticLabel: l10n.admin, screenIndex: 6),
        if (_currentUser != null)
          _NavItem(icon: Icons.notifications_rounded, label: l10n.notifications, semanticLabel: l10n.notifications, screenIndex: 7, badge: _unreadNotificationCount),
        if (_currentUser != null)
          _NavItem(icon: Icons.assignment_rounded, label: l10n.forms, semanticLabel: l10n.forms, screenIndex: 8),
      ];

  /// Título localizado de la pestaña actual (usado en AppBar y en semántica).
  String get _currentTitle {
    switch (_selectedIndex) {
      case 0: return l10n.dashboard;
      case 1: return l10n.festivals;
      case 2: return l10n.users;
      case 3: return l10n.shortFilms;
      case 4: return l10n.chat;
      case 5: return l10n.locations;
      case 6: return l10n.admin;
      case 7: return l10n.notifications;
      case 8: return l10n.formDefinitions;
      case 9: return l10n.calendar;
      default: return '';
    }
  }

  /// Construye el icono de navegación con badge y tooltip opcionales.
  Widget _navIcon(_NavItem item, {String? tooltip}) {
    final icon = item.badge <= 0 ? Icon(item.icon) : Badge.count(count: item.badge, child: Icon(item.icon));
    if (tooltip == null) return icon;
    return Tooltip(message: tooltip, child: icon);
  }

  /// Construye el contenido del cuerpo con el banner offline y la región viva semántica.
  Widget _buildBodyContent(ColorScheme colorScheme) {
    final textTheme = Theme.of(context).textTheme;
    return Column(
      children: [
        if (_isOffline)
          Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
            color: colorScheme.errorContainer,
            child: SafeArea(
              top: false,
              bottom: false,
              child: Row(
                children: [
                  Icon(Icons.wifi_off_rounded, color: colorScheme.onErrorContainer, size: 14),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(l10n.offline,
                      style: textTheme.labelMedium?.copyWith(color: colorScheme.onErrorContainer, fontWeight: FontWeight.w500),
                    ),
                  ),
                  if (SyncQueueService.instance.pendingCount > 0)
                    TextButton(
                      onPressed: _performSync,
                      style: TextButton.styleFrom(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                        minimumSize: Size.zero,
                        tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                      ),
                      child: Text(l10n.pendingChanges,
                        style: textTheme.labelSmall?.copyWith(color: colorScheme.onErrorContainer, fontWeight: FontWeight.w600),
                      ),
                    ),
                ],
              ),
            ),
          ),
        Expanded(
          child: Semantics(
            liveRegion: true,
            label: _currentTitle,
            child: _getScreenWidget(_selectedIndex),
          ),
        ),
      ],
    );
  }

  /// Construye el drawer de navegación con la cabecera de perfil de usuario y los items de navegación.
  Widget _buildDrawer(ColorScheme colorScheme) {
    return Drawer(
      child: Column(
        children: [
          DrawerHeader(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  colorScheme.primary,
                  colorScheme.primary.withAlpha(180),
                ],
              ),
            ),
            child: SizedBox(
              width: double.infinity,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  ProfileAvatar(
                    imageUrl: _currentUser?.avatarUrl,
                    fallbackText: _currentUser?.username ?? '',
                    radius: 28,
                    backgroundColor: colorScheme.onPrimary.withAlpha(60),
                    foregroundColor: colorScheme.onPrimary,
                  ),
                  const SizedBox(height: 12),
                  Text(
                    _currentUser?.fullName ?? _currentUser?.username ?? l10n.appTitle,
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(color: colorScheme.onPrimary, fontWeight: FontWeight.bold),
                  ),
                  if (_currentUser?.role != null)
                    Text(
                      _currentUser?.role ?? '',
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: colorScheme.onPrimary.withAlpha(180)),
                    ),
                ],
              ),
            ),
          ),
          Expanded(
            child: ListView(
              padding: EdgeInsets.zero,
              children: [
                for (final item in _visibleNavItems)
                  ListTile(
                    leading: Icon(item.icon, size: 22),
                    title: Text(item.label, style: Theme.of(context).textTheme.bodyLarge),
                    selected: _selectedIndex == item.screenIndex,
                    selectedTileColor: colorScheme.primaryContainer.withAlpha(80),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    onTap: () {
                      Navigator.pop(context);
                      _navigateToScreen(item.screenIndex);
                    },
                  ),
                const Divider(),
                ListTile(
                  leading: const Icon(Icons.language, size: 22),
                  title: Text(l10n.language, style: Theme.of(context).textTheme.bodyLarge),
                  subtitle: Text(LocaleService.localeNames[
                      LocaleService.instance.currentLocale?.languageCode ?? 'en'] ?? 'English'),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  onTap: () => showLanguagePicker(context),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    l10n = AppLocalizations.of(context)!;
    final colorScheme = Theme.of(context).colorScheme;

    return LayoutBuilder(
      builder: (context, constraints) {
        final isWide = constraints.maxWidth > 800;
        final navItems = _visibleNavItems;
        final selectedPosition = navItems.indexWhere((item) => item.screenIndex == _selectedIndex);
        final selected = selectedPosition == -1 ? 0 : selectedPosition;

        return Scaffold(
          appBar: AppBar(
            leading: isWide
                ? null
                : Builder(
                    builder: (ctx) => IconButton(
                      icon: const Icon(Icons.menu_rounded),
                      tooltip: l10n.menu,
                      onPressed: () => Scaffold.of(ctx).openDrawer(),
                    ),
                  ),
            title: Text(_currentTitle),
            actions: [
              Tooltip(
                message: l10n.search,
                child: IconButton(
                  icon: const Icon(Icons.search_rounded),
                  onPressed: _showSearchDialog,
                ),
              ),
              if (_currentUser == null)
                Padding(
                  padding: const EdgeInsets.only(right: 4),
                  child: FilledButton.tonalIcon(
                    onPressed: _navigateToLogin,
                    icon: const Icon(Icons.login_rounded, size: 16),
                    label: Text(l10n.login),
                    style: FilledButton.styleFrom(
                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                      minimumSize: Size.zero,
                      tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                    ),
                  ),
                )
              else
                Tooltip(
                  message: l10n.logout,
                  child: IconButton(
                    icon: const Icon(Icons.logout_rounded),
                    onPressed: () async {
                      await AuthService().clear();
                      await OfflineCacheService.instance.clear();
                      await SyncQueueService.instance.clear();
                      if (mounted) setState(() => _currentUser = null);
                      _screens.fillRange(0, _screens.length, null);
                      if (mounted) setState(() => _selectedIndex = 0);
                    },
                  ),
                ),
            ],
          ),
          body: Row(
            children: [
              if (isWide) ...[
                NavigationRail(
                  selectedIndex: selected,
                  onDestinationSelected: (i) => _navigateToScreen(navItems[i].screenIndex),
                  destinations: [
                    for (final item in navItems)
                      NavigationRailDestination(
                        icon: _navIcon(item, tooltip: item.semanticLabel),
                        label: Text(item.label, maxLines: 1, overflow: TextOverflow.ellipsis),
                      ),
                  ],
                ),
                const VerticalDivider(width: 1, thickness: 0.5),
              ],
              Expanded(child: _buildBodyContent(colorScheme)),
            ],
          ),
          bottomNavigationBar: isWide
              ? null
              : NavigationBar(
                  selectedIndex: selected,
                  onDestinationSelected: (i) => _navigateToScreen(navItems[i].screenIndex),
                  destinations: [
                    for (final item in navItems)
                      NavigationDestination(
                        icon: _navIcon(item),
                        label: item.label,
                        tooltip: item.semanticLabel,
                      ),
                  ],
                ),
          drawer: isWide ? null : _buildDrawer(colorScheme),
        );
      },
    );
  }
}

/// Modelo de item de navegación para la navegación responsive.
/// Usado por NavigationRail, NavigationBar y Drawer.
class _NavItem {
  final IconData icon;
  final String label;
  final String semanticLabel; // For accessibility (screen readers)
  final int screenIndex;
  final int badge; // Notification count badge

  const _NavItem({
    required this.icon,
    required this.label,
    required this.semanticLabel,
    required this.screenIndex,
    this.badge = 0,
  });
}
