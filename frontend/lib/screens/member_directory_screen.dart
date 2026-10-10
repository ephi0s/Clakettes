import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../services/api_service.dart';
import '../models/user_model.dart';
import '../widgets/reusable_widgets.dart';
import '../widgets/empty_state_widget.dart';
import '../widgets/loading_skeleton.dart';
import '../widgets/error_state_widget.dart';

/// Directorio de miembros con filtros de búsqueda y rol, opcionalmente
/// acotado a un festival.
class MemberDirectoryScreen extends StatefulWidget {
  final int? festivalId;
  final String? festivalName;
  const MemberDirectoryScreen({super.key, this.festivalId, this.festivalName});

  @override
  State<MemberDirectoryScreen> createState() => _MemberDirectoryScreenState();
}

/// Estado de [MemberDirectoryScreen]. Carga los usuarios activos en el primer
/// build y mantiene los valores actuales de búsqueda y filtro por rol.
class _MemberDirectoryScreenState extends State<MemberDirectoryScreen> {
  final ApiService api = ApiService();
  List<User> _users = [];
  bool _isLoading = true;
  bool _hasError = false;
  bool _initialized = false;
  late AppLocalizations l10n;
  String _search = '';
  String _roleFilter = '';

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    l10n = AppLocalizations.of(context)!;
    if (!_initialized) {
      _initialized = true;
      _loadData();
    }
  }

  /// Obtiene los usuarios activos de la API.
  Future<void> _loadData() async {
    if (!mounted) return;
    setState(() { _isLoading = true; _hasError = false; });
    try {
      final result = await api.getUsers(size: 100, isActive: true);
      if (!mounted) return;
      setState(() { _users = result.items; _isLoading = false; });
    } catch (e) {
      debugPrint('Error: $e');
      if (!mounted) return;
      setState(() { _isLoading = false; _hasError = true; });
    }
  }

  /// Usuarios filtrados por la búsqueda actual y el filtro de rol.
  List<User> get _filtered {
    return _users.where((u) {
      if (_search.isNotEmpty) {
        final q = _search.toLowerCase();
        if (!(u.fullName?.toLowerCase().contains(q) ?? false) &&
            !u.username.toLowerCase().contains(q) &&
            !(u.email?.toLowerCase().contains(q) ?? false)) {
          return false;
        }
      }
      if (_roleFilter.isNotEmpty && u.role != _roleFilter) return false;
      return true;
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    l10n = AppLocalizations.of(context)!;
    final filtered = _filtered;

    return Scaffold(
      appBar: AppBar(title: Text(widget.festivalName ?? l10n.users)),
      body: _isLoading
          ? const ListSkeleton()
          : _hasError
              ? ErrorStateWidget(onRetry: _loadData)
              : RefreshIndicator(
                  onRefresh: _loadData,
                  child: Column(
                    children: [
                      Padding(
                        padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
                        child: TextField(
                          decoration: InputDecoration(hintText: '${l10n.search}...', prefixIcon: const Icon(Icons.search), isDense: true, contentPadding: const EdgeInsets.symmetric(vertical: 8, horizontal: 12)),
                          onChanged: (v) { setState(() { _search = v; }); },
                        ),
                      ),
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 16),
                        child: SingleChildScrollView(
                          scrollDirection: Axis.horizontal,
                          child: Row(children: [
                            FilterChip(label: Text(l10n.all), selected: _roleFilter.isEmpty, onSelected: (_) { setState(() { _roleFilter = ''; }); }),
                            const SizedBox(width: 6),
                            ...['admin', 'director', 'producer', 'user'].map((r) => Padding(
                              padding: const EdgeInsets.only(right: 6),
                              child: FilterChip(label: Text(l10n.getRoleTranslation(r)), selected: _roleFilter == r, onSelected: (_) { setState(() { _roleFilter = _roleFilter == r ? '' : r; }); }),
                            )),
                          ]),
                        ),
                      ),
                      const SizedBox(height: 8),
                      Expanded(
                        child: filtered.isEmpty
                            ? EmptyStateWidget(icon: Icons.people_outline, title: l10n.noMembersFound, subtitle: _search.isNotEmpty ? l10n.tryDifferentSearch : null)
                            : ListView.builder(
                                padding: const EdgeInsets.all(16),
                                itemCount: filtered.length,
                                itemBuilder: (ctx, i) {
                                  final u = filtered[i];
                                  return ListItemCard(
                                    leading: ProfileAvatar(imageUrl: u.avatarUrl, fallbackText: u.fullName ?? u.username, radius: 24),
                                    title: u.fullName ?? u.username,
                                    subtitle: Text(u.email != null ? '${l10n.getRoleTranslation(u.role ?? 'user')} • ${u.email}' : l10n.getRoleTranslation(u.role ?? 'user')),
                                    trailing: StatusIndicator(isActive: u.isPublic, activeLabel: l10n.public, inactiveLabel: l10n.private),
                                  );
                                },
                              ),
                      ),
                    ],
                  ),
                ),
    );
  }
}
