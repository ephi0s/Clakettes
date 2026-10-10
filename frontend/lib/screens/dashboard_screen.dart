import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../models/festival_model.dart';
import '../services/api_service.dart';
import '../widgets/reusable_widgets.dart';
import '../widgets/agenda_calendar_widget.dart';
import '../widgets/error_state_widget.dart';
import '../widgets/list_item_animation.dart';
import 'festival_profile_screen.dart';

/// Panel de inicio que muestra recuentos globales, acciones rápidas y
/// festivales destacados.
///
/// Las acciones rápidas navegan a la pestaña principal correspondiente
/// mediante [onNavigateToTab].
class DashboardScreen extends StatefulWidget {
  final ValueChanged<int>? onNavigateToTab;

  const DashboardScreen({super.key, this.onNavigateToTab});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

/// Mantiene los recuentos de la plataforma y los festivales destacados
/// cargados al iniciar.
class _DashboardScreenState extends State<DashboardScreen> {
  final ApiService _api = ApiService();
  int _festivalCount = 0;
  int _userCount = 0;
  int _shortFilmCount = 0;
  List<Festival> _featuredFestivals = [];
  bool _isLoading = true;
  bool _hasError = false;
  late AppLocalizations l10n;

  @override
  void initState() {
    super.initState();
    _loadCounts();
  }

  /// Obtiene los recuentos de festivales y cortometrajes en paralelo y,
  /// después, el recuento de usuarios.
  Future<void> _loadCounts() async {
    setState(() { _isLoading = true; _hasError = false; });
    try {
      final results = await Future.wait([
        _api.getFestivals(size: 5, isActive: true),
        _api.getShortFilms(size: 1),
      ]);
      if (mounted) {
        setState(() {
          _featuredFestivals = (results[0] as PaginatedResult<Festival>).items;
          _festivalCount = (results[0] as PaginatedResult).total;
          _shortFilmCount = (results[1] as PaginatedResult).total;
        });
      }
    } catch (e) {
      debugPrint('Error: $e');
      if (mounted) setState(() { _isLoading = false; _hasError = true; });
    }
    await _loadUserCount();
  }

  /// Carga el recuento total de usuarios, tolerando el acceso sin autenticación.
  Future<void> _loadUserCount() async {
    try {
      final result = await _api.getUsers(size: 1);
      if (mounted) setState(() { _userCount = result.total; _isLoading = false; });
    } on UnauthorizedException {
      if (mounted) setState(() { _userCount = 0; _isLoading = false; });
    } catch (e) {
      debugPrint('Error: $e');
      if (mounted) setState(() { _userCount = 0; _isLoading = false; });
    }
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    l10n = AppLocalizations.of(context)!;
  }

  @override
  Widget build(BuildContext context) {
    l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Scaffold(
      body: RefreshIndicator(
        onRefresh: _loadCounts,
        child: CustomScrollView(
          slivers: [
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(20, 24, 20, 8),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: colorScheme.primaryContainer,
                        borderRadius: BorderRadius.circular(14),
                      ),
                      child: Icon(Icons.movie_filter_rounded, color: colorScheme.onPrimaryContainer, size: 24),
                    ),
                    const SizedBox(width: 14),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Semantics(
                          header: true,
                          label: l10n.welcomeBack,
                          child: Text(l10n.welcomeBack,
                            style: theme.textTheme.titleLarge?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: colorScheme.onSurface,
                            ),
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(l10n.subtitle,
                          style: theme.textTheme.bodyMedium?.copyWith(
                            color: colorScheme.onSurfaceVariant,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            if (_hasError)
              SliverFillRemaining(child: ErrorStateWidget(onRetry: _loadCounts))
            else ...[
              SliverPadding(
                padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
                sliver: SliverToBoxAdapter(
                  child: Semantics(
                    liveRegion: true,
                    child: _isLoading ? _buildStatsSkeleton(colorScheme) : _buildStatsRow(theme, colorScheme),
                  ),
                ),
              ),
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(20, 24, 20, 12),
                  child: Text(l10n.quickActions,
                    style: theme.textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.w700,
                      color: colorScheme.onSurfaceVariant,
                      letterSpacing: 0.5,
                    ),
                  ),
                ),
              ),
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(16, 0, 16, 0),
                  child: SizedBox(
                    height: 44,
                    child: ListView(
                      scrollDirection: Axis.horizontal,
                      children: [
                        _actionBtn(Icons.festival_rounded, l10n.festivals, colorScheme.primary, () => _navigateToTab(1)),
                        const SizedBox(width: 8),
                        _actionBtn(Icons.people_rounded, l10n.users, colorScheme.secondary, () => _navigateToTab(2)),
                        const SizedBox(width: 8),
                        _actionBtn(Icons.movie_creation_rounded, l10n.shortFilms, colorScheme.tertiary, () => _navigateToTab(3)),
                        const SizedBox(width: 8),
                        _actionBtn(Icons.chat_rounded, l10n.chat, colorScheme.primary, () => _navigateToTab(4)),
                        const SizedBox(width: 8),
                        _actionBtn(Icons.location_on_rounded, l10n.locations, colorScheme.secondary, () => _navigateToTab(5)),
                      ],
                    ),
                  ),
                ),
              ),
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(20, 28, 20, 12),
                  child: Text(l10n.featuredFestivals,
                    style: theme.textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.w700,
                      color: colorScheme.onSurfaceVariant,
                      letterSpacing: 0.5,
                    ),
                  ),
                ),
              ),
              SliverPadding(
                padding: const EdgeInsets.fromLTRB(16, 0, 16, 24),
                sliver: _buildFeaturedList(colorScheme, theme),
              ),
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.only(bottom: 88),
                  child: AgendaCalendarSection(title: l10n.agenda),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildStatsSkeleton(ColorScheme colorScheme) {
    return Row(
      children: List.generate(3, (_) => Expanded(
        child: Container(
          margin: const EdgeInsets.symmetric(horizontal: 4),
          padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 12),
          decoration: BoxDecoration(
            color: colorScheme.surface,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: colorScheme.outlineVariant.withAlpha(40)),
          ),
          child: Column(children: [
            Container(height: 32, width: 32, decoration: BoxDecoration(color: colorScheme.surfaceContainerHighest.withAlpha(100), borderRadius: BorderRadius.circular(10))),
            const SizedBox(height: 10),
            Container(height: 22, width: 50, decoration: BoxDecoration(color: colorScheme.surfaceContainerHighest.withAlpha(100), borderRadius: BorderRadius.circular(6))),
            const SizedBox(height: 4),
            Container(height: 12, width: 70, decoration: BoxDecoration(color: colorScheme.surfaceContainerHighest.withAlpha(80), borderRadius: BorderRadius.circular(6))),
          ]),
        ),
      )),
    );
  }

  Widget _buildStatsRow(ThemeData theme, ColorScheme colorScheme) {
    return Row(
      children: [
        Expanded(child: _statCard(Icons.festival_rounded, l10n.totalFestivals, _festivalCount.toString(), colorScheme.primary, colorScheme.primaryContainer, theme, colorScheme)),
        const SizedBox(width: 8),
        Expanded(child: _statCard(Icons.people_rounded, l10n.totalUsers, _userCount.toString(), colorScheme.secondary, colorScheme.secondaryContainer, theme, colorScheme)),
        const SizedBox(width: 8),
        Expanded(child: _statCard(Icons.movie_rounded, l10n.totalShortFilms, _shortFilmCount.toString(), colorScheme.tertiary, colorScheme.tertiaryContainer, theme, colorScheme)),
      ],
    );
  }

  Widget _statCard(IconData icon, String label, String value, Color iconColor, Color containerColor, ThemeData theme, ColorScheme colorScheme) {
    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0, end: 1),
      duration: const Duration(milliseconds: 500),
      curve: Curves.easeOutCubic,
      builder: (context, anim, _) {
        final intVal = (int.tryParse(value) ?? 0).toDouble();
        final animatedVal = (intVal * anim).round().toString();
        return Container(
          padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 10),
          decoration: BoxDecoration(
            color: colorScheme.surface,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: colorScheme.outlineVariant.withAlpha(40)),
          ),
          child: Semantics(
            label: '$label: $value',
            child: Column(
              children: [
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: containerColor,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(icon, color: iconColor, size: 22),
                ),
                const SizedBox(height: 10),
                Text(animatedVal, style: theme.textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold, color: colorScheme.onSurface)),
                const SizedBox(height: 2),
                Text(label, style: theme.textTheme.bodySmall?.copyWith(color: colorScheme.onSurfaceVariant, fontWeight: FontWeight.w500), textAlign: TextAlign.center, maxLines: 1, overflow: TextOverflow.ellipsis),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _actionBtn(IconData icon, String label, Color color, VoidCallback onTap) {
    return ActionChip(
      avatar: Icon(icon, size: 16, color: color),
      label: Text(label, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w500)),
      onPressed: onTap,
      side: BorderSide(color: color.withAlpha(50)),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
    );
  }

  void _navigateToTab(int tabIndex) {
    widget.onNavigateToTab?.call(tabIndex);
  }

  Widget _buildFeaturedList(ColorScheme colorScheme, ThemeData theme) {
    if (_featuredFestivals.isEmpty) {
      return SliverToBoxAdapter(
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 32, horizontal: 24),
          decoration: BoxDecoration(
            color: colorScheme.surface,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: colorScheme.outlineVariant.withAlpha(40)),
          ),
          child: Semantics(
            label: l10n.noFestivals,
            child: Column(
              children: [
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: colorScheme.primaryContainer.withAlpha(100),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(Icons.festival_outlined, size: 36, color: colorScheme.primary),
                ),
                const SizedBox(height: 16),
                Text(l10n.noFestivals, style: theme.textTheme.bodyLarge?.copyWith(color: colorScheme.onSurfaceVariant, fontWeight: FontWeight.w500)),
                const SizedBox(height: 4),
                Text(l10n.subtitle, style: theme.textTheme.bodySmall?.copyWith(color: colorScheme.onSurfaceVariant.withAlpha(150))),
              ],
            ),
          ),
        ),
      );
    }

    return SliverList(
      delegate: SliverChildBuilderDelegate(
        (context, index) {
          final festival = _featuredFestivals[index];
          return ListItemAnimation(
            index: index,
            child: Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Material(
              color: colorScheme.surface,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(14),
                side: BorderSide(color: colorScheme.outlineVariant.withAlpha(40)),
              ),
              clipBehavior: Clip.antiAlias,
              child: ListTile(
                contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                leading: Hero(
                  tag: 'festival_${festival.id}',
                  child: ProfileAvatar(imageUrl: festival.logoUrl, fallbackText: festival.name, radius: 22),
                ),
                title: Text(festival.name, style: const TextStyle(fontWeight: FontWeight.w600), maxLines: 1, overflow: TextOverflow.ellipsis),
                subtitle: Text(festival.location ?? l10n.noLocations, maxLines: 1, overflow: TextOverflow.ellipsis),
                trailing: Icon(Icons.chevron_right_rounded, color: colorScheme.onSurfaceVariant.withAlpha(120), size: 20),
                onTap: () => Navigator.push(context, PageRouteBuilder(
                  transitionDuration: const Duration(milliseconds: 300),
                  pageBuilder: (_, animation, __) => FadeTransition(opacity: animation, child: FestivalProfileScreen(festival: festival)),
                )),
              ),
              ),
            ),
          );
        },
        childCount: _featuredFestivals.length,
      ),
    );
  }
}
