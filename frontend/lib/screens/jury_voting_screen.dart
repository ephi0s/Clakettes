import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../models/festival_model.dart';
import '../models/shortfilm_model.dart';
import '../models/user_model.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import '../widgets/reusable_widgets.dart';
import '../widgets/empty_state_widget.dart';
import '../widgets/error_state_widget.dart';
import '../widgets/loading_skeleton.dart';

/// Pantalla de votación del jurado (Fase 5).
///
/// - Rol `jury`: lista de cortometrajes del festival con puntuación 0–10,
///   comentario opcional y voto.
/// - Rol `organizer` / `admin`: resultados agregados (promedio por cortometraje,
///   conteo de votos y lista de scores), ordenados por puntuación media.
/// Cualquier otro rol ve un mensaje de acceso denegado.
class JuryVotingScreen extends StatefulWidget {
  final int? festivalId;

  const JuryVotingScreen({super.key, this.festivalId});

  @override
  State<JuryVotingScreen> createState() => _JuryVotingScreenState();
}

class _JuryVotingScreenState extends State<JuryVotingScreen> {
  final ApiService _apiService = ApiService();
  late AppLocalizations l10n;

  User? _currentUser;
  List<Festival> _festivals = [];
  int? _selectedFestivalId;
  List<ShortFilm> _shortFilms = [];
  List<Map<String, dynamic>> _aggregate = [];
  /// Estado de cribado por cortometraje (shortfilm_id -> datos del screening).
  final Map<int, Map<String, dynamic>> _screeningByFilm = {};
  /// IDs de cortometrajes descalificados en el cribado (no elegibles para voto).
  final Set<int> _disqualifiedIds = {};
  bool _isLoading = true;
  bool _hasError = false;
  String? _errorMessage;

  /// Puntuación seleccionada por corto (shortfilmId -> score 0-10).
  final Map<int, double> _scores = {};
  /// Comentario por corto.
  final Map<int, String> _comments = {};
  /// IDs de cortometrajes ya votados por el usuario actual (evita duplicados).
  final Set<int> _votedShortFilmIds = {};

  @override
  void initState() {
    super.initState();
    _loadCurrentUser();
    if (widget.festivalId != null) {
      _selectedFestivalId = widget.festivalId;
      _loadFestival(widget.festivalId!);
    } else {
      _loadFestivals();
    }
  }

  Future<void> _loadCurrentUser() async {
    final user = await AuthService().getCurrentUser();
    if (mounted) setState(() => _currentUser = user);
  }

  bool get _canVote {
    final role = _currentUser?.role?.toLowerCase();
    return role == 'jury' || role == 'organizer' || role == 'admin';
  }

  bool get _canSeeResults {
    final role = _currentUser?.role?.toLowerCase();
    return role == 'organizer' || role == 'admin';
  }

  /// Carga el festival fijo recibido por parámetro.
  Future<void> _loadFestival(int id) async {
    try {
      final festival = await _apiService.getFestival(id);
      if (!mounted) return;
      setState(() {
        _festivals = [festival];
        _selectedFestivalId = festival.id ?? id;
      });
      _loadShortFilms(_selectedFestivalId!);
    } catch (e) {
      debugPrint('Error cargando festival: $e');
      if (!mounted) return;
      setState(() {
        _hasError = true;
        _errorMessage = AppLocalizations.of(context)!.juryFestivalLoadFailed;
      });
    }
  }

  /// Carga la lista de festivales activos (para el selector cuando no hay festival fijo).
  Future<void> _loadFestivals() async {
    try {
      final result = await _apiService.getFestivals(size: 100, isActive: true);
      if (!mounted) return;
      setState(() {
        _festivals = result.items;
        if (_selectedFestivalId == null && _festivals.isNotEmpty) {
          _selectedFestivalId = _festivals.first.id;
        }
      });
    } catch (e) {
      debugPrint('Error cargando festivales: $e');
    }
  }

  /// Carga los cortometrajes del festival seleccionado.
  Future<void> _loadShortFilms(int festivalId) async {
    setState(() {
      _isLoading = true;
      _hasError = false;
      _shortFilms = [];
      _aggregate = [];
      _screeningByFilm.clear();
      _disqualifiedIds.clear();
    });
    try {
      final result = await _apiService.getShortFilms(size: 100, festivalId: festivalId);
      if (!mounted) return;
      setState(() {
        _shortFilms = result.items;
        _isLoading = false;
      });
      _loadUserVotes(festivalId);
      _loadScreenings(festivalId);
    } catch (e) {
      debugPrint('Error cargando cortos: $e');
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _hasError = true;
        _errorMessage = AppLocalizations.of(context)!.juryShortFilmsLoadFailed;
      });
    }
  }

  /// Carga el estado de cribado de las obras del festival para saber cuáles son
  /// elegibles para votación del jurado.
  Future<void> _loadScreenings(int festivalId) async {
    try {
      final data = await _apiService.getFestivalScreenings(festivalId);
      if (!mounted) return;
      final screenings = (data['screenings'] as List? ?? [])
          .cast<Map<String, dynamic>>();
      for (final s in screenings) {
        final id = s['shortfilm_id'] as int;
        _screeningByFilm[id] = s;
        if (s['is_disqualified'] == true) {
          _disqualifiedIds.add(id);
        }
      }
      if (!mounted) return;
      setState(() {});
    } catch (e) {
      debugPrint('Error cargando cribado: $e');
    }
  }

  /// Carga los votos ya emitidos por el usuario actual en este festival.
  Future<void> _loadUserVotes(int festivalId) async {
    try {
      final votes = await _apiService.getVotes(festivalId);
      if (!mounted) return;
      setState(() {
        _votedShortFilmIds
          ..clear()
          ..addAll(votes
              .where((v) => v['juror_id'] == _currentUser?.id)
              .map((v) => v['shortfilm_id'] as int));
      });
    } catch (e) {
      debugPrint('Error cargando votos del usuario: $e');
    }
  }

  /// Carga la agregación de resultados del festival (organizer/admin).
  Future<void> _loadAggregate(int festivalId) async {
    try {
      final data = await _apiService.getAggregate(festivalId);
      if (!mounted) return;
      final results = (data['results'] as List? ?? [])
          .cast<Map<String, dynamic>>()
          .map((r) => {
                'shortfilm_id': r['shortfilm_id'],
                'average_score': (r['average_score'] as num).toDouble(),
                'vote_count': r['vote_count'] as int,
                'scores': List<double>.from((r['scores'] as List).cast<num>().map((e) => e.toDouble())),
              })
          .toList()
        ..sort((a, b) => b['average_score'].compareTo(a['average_score']));
      setState(() => _aggregate = results);
    } catch (e) {
      debugPrint('Error cargando agregación: $e');
    }
  }

  /// Emite un voto para un cortometraje.
  Future<void> _castVote(ShortFilm film) async {
    final score = _scores[film.id!];
    if (score == null) {
      showAppSnack(context, l10n.voteScoreRequired);
      return;
    }
    try {
      await _apiService.castVote(
        festivalId: _selectedFestivalId!,
        shortfilmId: film.id!,
        score: score,
        comment: _comments[film.id!],
        anonymous: false,
      );
      if (!mounted) return;
      setState(() {
        _votedShortFilmIds.add(film.id!);
        _scores.remove(film.id!);
        _comments.remove(film.id!);
      });
      showAppSnack(context, l10n.voteSaved);
      if (_canSeeResults) {
        await _loadAggregate(_selectedFestivalId!);
      }
    } catch (e) {
      debugPrint('Error emitiendo voto: $e');
      if (!mounted) return;
      showAppSnack(context, '${l10n.voteFailed}: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    l10n = AppLocalizations.of(context)!;
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;

    if (!_canVote) {
      return _accessDenied(colorScheme);
    }

    // Si no hay festival seleccionado, mostrar selector.
    if (_selectedFestivalId == null) {
      return _festivalSelector(colorScheme);
    }

    final festival = _festivals.firstWhere(
      (f) => f.id == _selectedFestivalId,
      orElse: () => Festival(id: _selectedFestivalId, name: '#$_selectedFestivalId'),
    );
    final title = '${l10n.votingFor} ${festival.name}';

    return Scaffold(
      appBar: AppBar(title: Text(title)),
      body: _isLoading
          ? const ListSkeleton()
          : _hasError
              ? ErrorStateWidget(message: _errorMessage ?? '', onRetry: () => _loadShortFilms(_selectedFestivalId!))
              : _canSeeResults
                  ? _resultsView(festival, textTheme)
                  : _votingView(festival, textTheme),
    );
  }

  Widget _accessDenied(ColorScheme colorScheme) {
    final textTheme = Theme.of(context).textTheme;
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.lock_outline_rounded, size: 64, color: colorScheme.onSurfaceVariant.withAlpha(120)),
          const SizedBox(height: 16),
          Text(l10n.voteNoAccess, style: textTheme.titleMedium),
          const SizedBox(height: 8),
          Text(
            l10n.voteNoAccessDetail,
            style: textTheme.bodyMedium?.copyWith(color: colorScheme.onSurfaceVariant),
          ),
        ],
      ),
    );
  }

  Widget _festivalSelector(ColorScheme colorScheme) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          SemanticHeader(text: l10n.selectFestival),
          const SizedBox(height: 16),
          if (_festivals.isEmpty)
            Text(l10n.noFestivals, style: Theme.of(context).textTheme.bodyMedium)
          else
            DropdownButton<int>(
              hint: Text(l10n.selectFestival),
              value: _selectedFestivalId,
              items: _festivals
                  .map((f) => DropdownMenuItem<int>(
                        value: f.id,
                        child: Text(f.name),
                      ))
                  .toList(),
              onChanged: (id) async {
                if (id == null) return;
                setState(() => _selectedFestivalId = id);
                await _loadShortFilms(id);
                if (_canSeeResults) await _loadAggregate(id);
              },
            ),
        ],
      ),
    );
  }

  /// Vista de jurado: lista de cortometrajes con puntuación y comentario.
  Widget _votingView(Festival festival, TextTheme textTheme) {
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              SemanticHeader(text: festival.name),
              const SizedBox(height: 4),
              Text(
                l10n.voteJuryInstructions,
                style: textTheme.bodyMedium?.copyWith(color: Theme.of(context).colorScheme.onSurfaceVariant),
              ),
              const SizedBox(height: 16),
              Text(
                '${l10n.voteYourVotes}: ${_votedShortFilmIds.length}',
                style: textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w600),
              ),
            ],
          ),
        ),
        Expanded(
          child: _shortFilms.isEmpty
              ? EmptyStateWidget(icon: Icons.movie_rounded, title: l10n.noShortFilms)
              : ListView.builder(
                  itemCount: _shortFilms.length,
                  itemBuilder: (ctx, i) {
                    final film = _shortFilms[i];
                    final alreadyVoted = _votedShortFilmIds.contains(film.id);
                    final isDisqualified = _disqualifiedIds.contains(film.id);
                    return _voteCard(film, alreadyVoted, isDisqualified);
                  },
                ),
        ),
      ],
    );
  }

  Widget _voteCard(ShortFilm film, bool alreadyVoted, bool isDisqualified) {
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;
    final score = _scores[film.id!] ?? 0.0;
    final screening = _screeningByFilm[film.id!];
    final isEligible = !isDisqualified && !alreadyVoted;
    final disqualifiedReason = screening?['status_reason'] as String?;

    return ListItemCard(
      leading: CircleAvatar(
        child: Text(film.title.isNotEmpty ? film.title[0].toUpperCase() : '?'),
      ),
      title: film.title,
      subtitle: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (film.description != null && film.description!.isNotEmpty)
            Text(
              film.description!,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              style: textTheme.bodySmall?.copyWith(color: colorScheme.onSurfaceVariant),
            ),
          const SizedBox(height: 8),
          Row(
            children: [
              Icon(Icons.star_rounded, size: 18, color: colorScheme.primary),
              const SizedBox(width: 6),
              Text(
                '${l10n.voteScore}: ${score.toInt()}',
                style: textTheme.labelLarge?.copyWith(fontWeight: FontWeight.w600),
              ),
            ],
          ),
          const SizedBox(height: 6),
          if (isDisqualified) ...[
            Row(
              children: [
                Icon(Icons.cancel_rounded, size: 16, color: colorScheme.error),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(
                    '${l10n.voteNotEligible}: ${disqualifiedReason ?? l10n.voteDisqualified}',
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: textTheme.labelSmall?.copyWith(color: colorScheme.error, fontWeight: FontWeight.w600),
                  ),
                ),
              ],
            ),
          ] else if (alreadyVoted) ...[
            StatusIndicator(
              isActive: true,
              activeLabel: l10n.voteCast,
              inactiveLabel: l10n.voteCast,
              activeIcon: Icons.check_circle_rounded,
              activeColor: colorScheme.primary,
              semanticLabel: l10n.voteCast,
            ),
          ],
        ],
      ),
      trailing: isDisqualified
          ? const SizedBox.shrink()
          : alreadyVoted
              ? StatusIndicator(
                  isActive: true,
                  activeLabel: l10n.voteCast,
                  inactiveLabel: l10n.voteCast,
                  activeIcon: Icons.check_circle_rounded,
                  activeColor: colorScheme.primary,
                  semanticLabel: l10n.voteCast,
                )
              : Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Slider(
                      value: score,
                      min: 0,
                      max: 10,
                      divisions: 10,
                      label: score.toInt().toString(),
                      onChanged: isEligible
                          ? (v) => setState(() => _scores[film.id!] = v)
                          : null,
                    ),
                    const SizedBox(height: 6),
                    TextField(
                      decoration: InputDecoration(
                        labelText: l10n.voteComment,
                        helperText: l10n.voteCommentHint,
                        border: const OutlineInputBorder(),
                        isDense: true,
                      ),
                      maxLines: 1,
                      maxLength: 500,
                      enabled: isEligible,
                      onChanged: (v) => setState(() => _comments[film.id!] = v),
                    ),
                    const SizedBox(height: 8),
                    FilledButton.tonal(
                      onPressed: isEligible ? () => _castVote(film) : null,
                      child: Text(l10n.voteCastButton),
                    ),
                  ],
                ),
    );
  }

  /// Vista de organizador/admin: resultados agregados ordenados por promedio.
  Widget _resultsView(Festival festival, TextTheme textTheme) {
    final totalVotes = _aggregate.fold<int>(0, (s, r) => s + (r['vote_count'] as int));

    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              SemanticHeader(text: '${l10n.votingResults} — ${festival.name}'),
              const SizedBox(height: 4),
              Text(
                '${l10n.voteTotalVotes}: $totalVotes',
                style: textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 16),
            ],
          ),
        ),
        Expanded(
          child: _aggregate.isEmpty
              ? EmptyStateWidget(
                  icon: Icons.bar_chart_rounded,
                  title: l10n.voteNoResultsYet,
                )
              : ListView.builder(
                  itemCount: _aggregate.length,
                  itemBuilder: (ctx, i) {
                    final r = _aggregate[i];
                    final film =
                        _shortFilms.firstWhere((f) => f.id == r['shortfilm_id'], orElse: () => ShortFilm(id: r['shortfilm_id'], title: '', festivalId: 0, userId: 0));
                    final scores = r['scores'] as List<double>;
                    return ListItemCard(
                      leading: CircleAvatar(
                        child: Text('${i + 1}'),
                      ),
                      title: film.title,
                      subtitle: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              const Icon(Icons.star_rounded, size: 18, color: Colors.amber),
                              const SizedBox(width: 6),
                              Text(
                                '${r['average_score'].toStringAsFixed(1)} / 10',
                                style: textTheme.labelLarge?.copyWith(fontWeight: FontWeight.bold),
                              ),
                              const SizedBox(width: 16),
                              StatusIndicator(
                                isActive: true,
                                activeLabel: '${l10n.voteVotes}: ${r['vote_count']}',
                                inactiveLabel: '${l10n.voteVotes}: ${r['vote_count']}',
                                activeIcon: Icons.star_rounded,
                                semanticLabel: '${l10n.voteVotes}: ${r['vote_count']}',
                              ),
                            ],
                          ),
                          const SizedBox(height: 6),
                          Wrap(
                            spacing: 4,
                            children: scores.take(8).map((s) => Chip(
                                  label: Text(s.toInt().toString()),
                                  visualDensity: VisualDensity.compact,
                                  materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                                )).toList(),
                          ),
                          if (scores.length > 8)
                            Padding(
                              padding: const EdgeInsets.only(top: 4),
                              child: Text(
                                '${l10n.voteAndMore}: ${scores.length - 8}',
                                style: textTheme.labelSmall?.copyWith(color: Theme.of(context).colorScheme.onSurfaceVariant),
                              ),
                            ),
                        ],
                      ),
                    );
                  },
                ),
        ),
      ],
    );
  }
}
