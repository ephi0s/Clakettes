import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import '../models/user_model.dart';
import '../widgets/loading_skeleton.dart';
import 'calendar_settings_screen.dart';
import 'roles_management_screen.dart';
import 'member_directory_screen.dart';
import 'user_profile_screen.dart';

/// Pantalla del panel de administración que muestra estadísticas de la base de
/// datos, recuentos de tablas y acciones de administración.
///
/// Solo accesible para usuarios con el rol "admin".
class AdminScreen extends StatefulWidget {
  const AdminScreen({super.key});

  @override
  State<AdminScreen> createState() => _AdminScreenState();
}

/// Mantiene las estadísticas de administración, los recuentos de tablas y el
/// usuario actual; los carga al iniciar.
class _AdminScreenState extends State<AdminScreen> {
  final ApiService _api = ApiService();
  User? _currentUser;
  Map<String, dynamic>? _stats;
  Map<String, dynamic>? _tables;
  bool _isLoading = true;
  bool _hasError = false;
  bool _isForbidden = false;
  late AppLocalizations l10n;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  /// Obtiene las estadísticas y los recuentos de tablas de administración;
  /// activa un estado de acceso denegado si el usuario actual no tiene el
  /// rol "admin".
  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
      _hasError = false;
      _isForbidden = false;
    });

    try {
      _currentUser = await AuthService().getCurrentUser();
      if (_currentUser == null || _currentUser!.role?.toLowerCase() != 'admin') {
        if (mounted) {
          setState(() {
            _isLoading = false;
            _isForbidden = true;
          });
        }
        return;
      }

      final results = await Future.wait([
        _api.getAdminStats(),
        _api.getAdminTables(),
      ]);

      if (mounted) {
        setState(() {
          _stats = results[0];
          _tables = results[1]['tables'];
          _isLoading = false;
        });
      }
    } catch (e) {
      debugPrint('Error: $e');
      if (mounted) setState(() { _isLoading = false; _hasError = true; });
    }
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    l10n = AppLocalizations.of(context)!;
  }

  @override
  void dispose() {
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Scaffold(
      appBar: AppBar(
        title: Semantics(header: true, child: Text(l10n.adminPanel)),
        actions: [
          Semantics(
            label: l10n.refresh,
            button: true,
            child: Tooltip(
              message: l10n.refresh,
              child: IconButton(
                icon: const Icon(Icons.refresh),
                onPressed: _loadData,
              ),
            ),
          ),
        ],
      ),
      body: _buildBody(theme, colorScheme),
    );
  }

  Widget _buildBody(ThemeData theme, ColorScheme colorScheme) {
    if (_isLoading) {
      return const Padding(
        padding: EdgeInsets.all(16),
        child: ListSkeleton(),
      );
    }

    if (_isForbidden) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: colorScheme.errorContainer.withAlpha(100),
                  shape: BoxShape.circle,
                ),
                child: Icon(Icons.lock, size: 48, color: colorScheme.error),
              ),
              const SizedBox(height: 16),
              Text(l10n.error, style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Text(l10n.loadError, style: theme.textTheme.bodyMedium?.copyWith(color: colorScheme.onSurfaceVariant), textAlign: TextAlign.center),
            ],
          ),
        ),
      );
    }

    if (_hasError) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.error_outline, size: 64, color: colorScheme.error.withAlpha(180)),
              const SizedBox(height: 16),
              Text(l10n.error, style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Text(l10n.loadError, style: theme.textTheme.bodyMedium?.copyWith(color: colorScheme.onSurfaceVariant), textAlign: TextAlign.center),
              const SizedBox(height: 24),
              Semantics(
                label: l10n.refresh,
                child: ElevatedButton.icon(
                  onPressed: _loadData,
                  icon: const Icon(Icons.refresh),
                  label: Text(l10n.refresh),
                ),
              ),
            ],
          ),
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadData,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Semantics(
            header: true,
            child: Text(l10n.databaseStats, style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
          ),
          const SizedBox(height: 12),
          _buildStatsGrid(theme, colorScheme),
          const SizedBox(height: 24),
          Semantics(
            header: true,
            child: Text(l10n.tableCounts, style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
          ),
          const SizedBox(height: 12),
          _buildTablesList(theme, colorScheme),
          const SizedBox(height: 24),
          Semantics(
            header: true,
            child: Text(l10n.management, style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
          ),
          const SizedBox(height: 12),
          Card(
            child: Column(children: [
              Semantics(
                container: true,
                label: l10n.roleGroupsManagement,
                child: ListTile(
                  leading: const Icon(Icons.category),
                  title: Text(l10n.roleGroupsManagement),
                  subtitle: Text(l10n.roleGroupsDescription),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const RolesManagementScreen())),
                ),
              ),
              const Divider(height: 1),
              Semantics(
                container: true,
                label: l10n.memberDirectory,
                child: ListTile(
                  leading: const Icon(Icons.people),
                  title: Text(l10n.memberDirectory),
                  subtitle: Text(l10n.memberDirectoryDescription),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const MemberDirectoryScreen())),
                ),
              ),
              const Divider(height: 1),
              Semantics(
                container: true,
                label: l10n.activeSessions,
                child: ListTile(
                  leading: const Icon(Icons.devices),
                  title: Text(l10n.activeSessions),
                  subtitle: Text(l10n.manageSessions),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () => _showSessionsDialog(),
                ),
              ),
              const Divider(height: 1),
              Semantics(
                container: true,
                label: l10n.userAliases,
                child: ListTile(
                  leading: const Icon(Icons.alternate_email),
                  title: Text(l10n.userAliases),
                  subtitle: Text(l10n.manageAliases),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () => _showAliasesDialog(),
                ),
              ),
              const Divider(height: 1),
              Semantics(
                container: true,
                label: l10n.calendarSettings,
                child: ListTile(
                  leading: const Icon(Icons.calendar_month_outlined),
                  title: Text(l10n.calendarSettings),
                  subtitle: Text(l10n.calendarSettingsDescription),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () => Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => const CalendarSettingsScreen()),
                  ),
                ),
              ),
            ]),
          ),
          const SizedBox(height: 24),
          Semantics(
            header: true,
            child: Text(l10n.resetDatabase, style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
          ),
          const SizedBox(height: 12),
          _buildResetSection(theme, colorScheme),
        ],
      ),
    );
  }

  Widget _buildStatsGrid(ThemeData theme, ColorScheme colorScheme) {
    if (_stats == null) return const SizedBox.shrink();

    final items = [
      _StatItem(Icons.people, l10n.totalUsers, '${_stats!['users'] ?? 0}', colorScheme.primary),
      _StatItem(Icons.festival, l10n.totalFestivals, '${_stats!['festivals'] ?? 0}', colorScheme.secondary),
      _StatItem(Icons.movie, l10n.totalShortFilms, '${_stats!['shortfilms'] ?? 0}', colorScheme.tertiary),
      _StatItem(Icons.chat, l10n.totalMessages, '${_stats!['messages'] ?? 0}', colorScheme.primary),
      _StatItem(Icons.person, l10n.activeUsers, '${_stats!['active_users'] ?? 0}', colorScheme.secondary),
      _StatItem(Icons.check_circle, l10n.activeFestivals, '${_stats!['active_festivals'] ?? 0}', colorScheme.tertiary),
    ];

    return GridView.count(
      crossAxisCount: 3,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      mainAxisSpacing: 8,
      crossAxisSpacing: 8,
      childAspectRatio: 1.4,
      children: items.map((item) => Semantics(
        label: '${item.label}: ${item.value}',
        child: Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: colorScheme.surfaceContainerLow,
            borderRadius: BorderRadius.circular(12),
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(item.icon, color: item.color, size: 24),
              const SizedBox(height: 6),
              Text(item.value, style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
              Text(item.label, style: theme.textTheme.bodySmall?.copyWith(color: colorScheme.onSurfaceVariant), textAlign: TextAlign.center, maxLines: 1, overflow: TextOverflow.ellipsis),
            ],
          ),
        ),
      )).toList(),
    );
  }

  Widget _buildTablesList(ThemeData theme, ColorScheme colorScheme) {
    if (_tables == null || _tables!.isEmpty) return const SizedBox.shrink();

    return Card(
      child: Column(
        children: _tables!.entries.map((entry) {
          return ListTile(
            leading: ExcludeSemantics(
              child: Icon(_getTableIcon(entry.key), color: colorScheme.primary),
            ),
            title: Text(entry.key),
            trailing: Semantics(
              label: l10n.rowCount(entry.value),
              child: Chip(label: Text('${entry.value}')),
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildResetSection(ThemeData theme, ColorScheme colorScheme) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Semantics(
              label: l10n.resetDatabaseConfirm,
              child: Text(
                l10n.resetDatabaseConfirm,
                style: theme.textTheme.bodyMedium?.copyWith(color: colorScheme.error),
              ),
            ),
            const SizedBox(height: 12),
            Semantics(
              label: l10n.resetDatabase,
              child: ElevatedButton.icon(
                onPressed: _showResetDialog,
                icon: const Icon(Icons.warning, size: 18),
                label: Text(l10n.resetDatabase),
                style: ElevatedButton.styleFrom(
                  backgroundColor: colorScheme.error,
                  foregroundColor: colorScheme.onError,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// Pide al administrador que escriba "yes" antes de reiniciar la base de datos.
  void _showResetDialog() {
    final controller = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(l10n.resetDatabase),
        content: TextField(
          controller: controller,
          decoration: InputDecoration(
            hintText: l10n.typeYesToConfirm,
            border: const OutlineInputBorder(),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: Text(l10n.cancel),
          ),
          TextButton(
            onPressed: () async {
              if (controller.text == 'yes') {
                Navigator.pop(ctx);
                try {
                  await _api.search(''); // just to verify auth
                  final client = _api.client;
                  final uri = Uri.parse('${_api.baseUrl}/admin/reset?confirm=yes');
                  final headers = await _getAuthHeaders();
                  await client.post(uri, headers: headers);
                  if (mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text(l10n.databaseReset), behavior: SnackBarBehavior.floating),
                    );
                    _loadData();
                  }
                } catch (e) {
                  debugPrint('Error: $e');
                  if (mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text(l10n.error), behavior: SnackBarBehavior.floating),
                    );
                  }
                }
              }
            },
            child: Text(l10n.accept),
          ),
        ],
      ),
    );
  }

  void _showSessionsDialog() {
    if (_currentUser == null) return;
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => UserProfileScreen(user: _currentUser!, currentUser: _currentUser!),
      ),
    );
  }

  void _showAliasesDialog() {
    if (_currentUser == null) return;
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => UserProfileScreen(user: _currentUser!, currentUser: _currentUser!),
      ),
    );
  }

  /// Construye las cabeceras de petición autenticadas a partir del token JWT guardado.
  Future<Map<String, String>> _getAuthHeaders() async {
    final token = await AuthService().getToken();
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  IconData _getTableIcon(String tableName) {
    switch (tableName) {
      case 'users': return Icons.people;
      case 'festivals': return Icons.festival;
      case 'shortfilms': return Icons.movie;
      case 'messages': return Icons.chat;
      case 'user_festival': return Icons.link;
      default: return Icons.table_chart;
    }
  }
}

/// Descriptor inmutable para una única tarjeta de estadísticas de la base de datos.
class _StatItem {
  final IconData icon;
  final String label;
  final String value;
  final Color color;

  const _StatItem(this.icon, this.label, this.value, this.color);
}
