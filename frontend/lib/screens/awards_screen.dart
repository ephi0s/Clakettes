import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../services/api_service.dart';
import '../models/award_model.dart';
import '../widgets/reusable_widgets.dart';
import '../widgets/empty_state_widget.dart';
import '../widgets/loading_skeleton.dart';
import '../widgets/error_state_widget.dart';
import '../widgets/confirm_dialog.dart';

class AwardsScreen extends StatefulWidget {
  final int festivalId;
  final String festivalName;
  const AwardsScreen({super.key, required this.festivalId, required this.festivalName});

  @override
  State<AwardsScreen> createState() => _AwardsScreenState();
}

class _AwardsScreenState extends State<AwardsScreen> {
  final ApiService api = ApiService();
  List<Award> _awards = [];
  bool _isLoading = true;
  bool _hasError = false;
  bool _showOnlyWinners = false;
  String _search = '';
  int? _selectedYear;
  bool _initialized = false;
  late AppLocalizations l10n;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    l10n = AppLocalizations.of(context)!;
    if (!_initialized) {
      _initialized = true;
      _loadData();
    }
  }

  Future<void> _loadData() async {
    if (!mounted) return;
    setState(() {
      _isLoading = true;
      _hasError = false;
    });
    try {
      final result = await api.getAwards(widget.festivalId, size: 100);
      if (!mounted) return;
      setState(() {
        _awards = result.items;
        _isLoading = false;
      });
    } catch (e) {
      debugPrint('Error: $e');
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _hasError = true;
      });
    }
  }

  List<int> get _years {
    final set = <int>{};
    for (final a in _awards) {
      if (a.year != null) set.add(a.year!);
    }
    final list = set.toList()..sort((a, b) => b.compareTo(a));
    return list;
  }

  List<Award> get _filtered {
    final q = _search.trim().toLowerCase();
    return _awards.where((a) {
      if (_showOnlyWinners && !a.isWinner) return false;
      if (_selectedYear != null && a.year != _selectedYear) return false;
      if (q.isEmpty) return true;
      final hay = '${a.awardName} ${a.awardCategory ?? ''} ${a.description ?? ''}'.toLowerCase();
      return hay.contains(q);
    }).toList();
  }

  Map<int?, List<Award>> get _grouped {
    final map = <int?, List<Award>>{};
    for (final a in _filtered) {
      map.putIfAbsent(a.year, () => []).add(a);
    }
    final keys = map.keys.toList()
      ..sort((a, b) {
        if (a == null) return 1;
        if (b == null) return -1;
        return b.compareTo(a);
      });
    return {for (final k in keys) k: map[k]!};
  }

  Future<void> _createAward() => _showAwardWizard();

  Future<void> _editAward(Award a) => _showAwardWizard(existing: a);

  Future<void> _showAwardWizard({Award? existing}) async {
    final nameCtl = TextEditingController(text: existing?.awardName ?? '');
    final catCtl = TextEditingController(text: existing?.awardCategory ?? '');
    final yearCtl = TextEditingController(text: existing?.year?.toString() ?? '');
    final posCtl = TextEditingController(text: existing?.position?.toString() ?? '');
    final prizeCtl = TextEditingController(text: existing?.prizeAmount ?? '');
    final descCtl = TextEditingController(text: existing?.description ?? '');
    final shortCtl = TextEditingController(text: existing?.shortfilmId?.toString() ?? '');
    final userCtl = TextEditingController(text: existing?.userId?.toString() ?? '');
    final eventCtl = TextEditingController(text: existing?.eventId?.toString() ?? '');
    bool isWinner = existing?.isWinner ?? false;
    bool isPublic = existing?.isPublic ?? true;
    bool isVerified = existing?.isVerified ?? false;
    final formKey = GlobalKey<FormState>();

    final saved = await showDialog<bool>(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setDialog) => AlertDialog(
          title: Text(existing == null ? l10n.newAward : l10n.edit),
          content: SizedBox(
            width: 480,
            child: SingleChildScrollView(
              child: Form(
                key: formKey,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    SemanticHeader(text: 'Premio', style: Theme.of(ctx).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w700)),
                    const SizedBox(height: 8),
                    Semantics(
                      label: l10n.awardName,
                      child: TextFormField(
                        controller: nameCtl,
                        decoration: InputDecoration(labelText: l10n.awardNameRequired, helperText: l10n.awardName),
                        textInputAction: TextInputAction.next,
                        validator: (v) => (v == null || v.trim().isEmpty) ? l10n.awardNameRequired : null,
                      ),
                    ),
                    const SizedBox(height: 8),
                    SemanticTextField(controller: catCtl, label: l10n.category, semanticLabel: l10n.category, helperText: l10n.category, textInputAction: TextInputAction.next),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        Expanded(
                          child: SemanticTextField(controller: yearCtl, label: 'Año', semanticLabel: 'Año', helperText: 'Ej. 2025', keyboardType: TextInputType.number, textInputAction: TextInputAction.next),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: SemanticTextField(controller: posCtl, label: 'Posición', semanticLabel: 'Posición', helperText: l10n.optional, keyboardType: TextInputType.number, textInputAction: TextInputAction.next),
                        ),
                      ],
                    ),
                    const Divider(height: 24),
                    SemanticHeader(text: 'Ganador', style: Theme.of(ctx).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w700)),
                    SwitchListTile(
                      title: Text(isWinner ? l10n.winner : l10n.nominee),
                      subtitle: const Text('Ganador'),
                      value: isWinner,
                      onChanged: (v) => setDialog(() => isWinner = v),
                    ),
                    SemanticTextField(controller: prizeCtl, label: 'Premio', semanticLabel: 'Premio', helperText: 'Ej. 1.000 €', textInputAction: TextInputAction.next),
                    const SizedBox(height: 8),
                    SemanticTextField(controller: descCtl, label: l10n.description, semanticLabel: l10n.description, helperText: l10n.optional, maxLines: 3),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        Expanded(
                          child: SemanticTextField(controller: shortCtl, label: 'Cortometraje ID', semanticLabel: 'Cortometraje ID', keyboardType: TextInputType.number),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: SemanticTextField(controller: userCtl, label: 'Usuario ID', semanticLabel: 'Usuario ID', keyboardType: TextInputType.number),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: SemanticTextField(controller: eventCtl, label: 'Evento ID', semanticLabel: 'Evento ID', keyboardType: TextInputType.number),
                        ),
                      ],
                    ),
                    SwitchListTile(
                      title: Text(isPublic ? l10n.public : l10n.hidden),
                      subtitle: const Text('Visible'),
                      value: isPublic,
                      onChanged: (v) => setDialog(() => isPublic = v),
                    ),
                    SwitchListTile(
                      title: Text(isVerified ? l10n.verified : l10n.unverified),
                      subtitle: const Text('Verificado'),
                      value: isVerified,
                      onChanged: (v) => setDialog(() => isVerified = v),
                    ),
                  ],
                ),
              ),
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx, false), child: Text(l10n.cancel)),
            FilledButton(
              onPressed: () async {
                if (!(formKey.currentState?.validate() ?? false)) return;
                final year = int.tryParse(yearCtl.text.trim());
                final pos = int.tryParse(posCtl.text.trim());
                final shortId = int.tryParse(shortCtl.text.trim());
                final userId = int.tryParse(userCtl.text.trim());
                final eventId = int.tryParse(eventCtl.text.trim());
                try {
                  if (existing == null || existing.id == null) {
                    await api.createAward(
                      widget.festivalId,
                      Award(
                        festivalId: widget.festivalId,
                        awardName: nameCtl.text.trim(),
                        awardCategory: catCtl.text.trim().isEmpty ? null : catCtl.text.trim(),
                        year: year,
                        position: pos,
                        isWinner: isWinner,
                        prizeAmount: prizeCtl.text.trim().isEmpty ? null : prizeCtl.text.trim(),
                        description: descCtl.text.trim().isEmpty ? null : descCtl.text.trim(),
                        shortfilmId: shortId,
                        userId: userId,
                        eventId: eventId,
                        isPublic: isPublic,
                        isVerified: isVerified,
                      ),
                    );
                  } else {
                    await api.updateAward(existing.id!, {
                      'award_name': nameCtl.text.trim(),
                      'award_category': catCtl.text.trim().isEmpty ? null : catCtl.text.trim(),
                      'year': year,
                      'position': pos,
                      'is_winner': isWinner,
                      'prize_amount': prizeCtl.text.trim().isEmpty ? null : prizeCtl.text.trim(),
                      'description': descCtl.text.trim().isEmpty ? null : descCtl.text.trim(),
                      'shortfilm_id': shortId,
                      'user_id': userId,
                      'event_id': eventId,
                      'is_public': isPublic,
                      'is_verified': isVerified,
                    });
                  }
                  if (ctx.mounted) Navigator.pop(ctx, true);
                } catch (e) {
                  if (mounted) showAppSnack(context, l10n.errorFor(e));
                }
              },
              child: Text(l10n.save),
            ),
          ],
        ),
      ),
    );
    if (saved == true) _loadData();
  }

  Future<void> _verifyAward(Award a) async {
    if (a.id == null) return;
    try {
      await api.updateAward(a.id!, {'is_verified': !a.isVerified});
      _loadData();
    } catch (e) {
      if (mounted) showAppSnack(context, l10n.errorFor(e));
    }
  }

  Future<void> _deleteAward(Award a) async {
    if (a.id == null) return;
    final confirm = await showConfirmDialog(context, title: l10n.deleteAward, message: l10n.deleteEntityMessage(a.awardName));
    if (confirm == true) {
      try {
        await api.deleteAward(a.id!);
        _loadData();
      } catch (e) {
        if (mounted) showAppSnack(context, l10n.errorFor(e));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final cs = theme.colorScheme;
    final winners = _awards.where((a) => a.isWinner).length;
    final yearsCount = _years.length;
    final grouped = _grouped;

    return Scaffold(
      appBar: AppBar(title: Text('${l10n.awards} — ${widget.festivalName}')),
      body: _isLoading
          ? const ListSkeleton()
          : _hasError
              ? ErrorStateWidget(onRetry: _loadData)
              : RefreshIndicator(
                  onRefresh: _loadData,
                  child: _awards.isEmpty
                      ? EmptyStateWidget(icon: Icons.emoji_events_outlined, title: l10n.noAwards, subtitle: l10n.createAwardSubtitle)
                      : ListView(
                          padding: const EdgeInsets.all(16),
                          children: [
                            Card(
                              child: Padding(
                                padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 8),
                                child: Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                                  children: [
                                    Semantics(
                                      label: 'Total ${_awards.length}',
                                      child: Column(
                                        mainAxisSize: MainAxisSize.min,
                                        children: [
                                          Text('${_awards.length}', style: theme.textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w700)),
                                          const Text('Premios'),
                                        ],
                                      ),
                                    ),
                                    Semantics(
                                      label: 'Ganadores $winners',
                                      child: Column(
                                        mainAxisSize: MainAxisSize.min,
                                        children: [
                                          Text('$winners', style: theme.textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w700, color: Colors.amber.shade700)),
                                          const Text('Ganadores'),
                                        ],
                                      ),
                                    ),
                                    Semantics(
                                      label: 'Años $yearsCount',
                                      child: Column(
                                        mainAxisSize: MainAxisSize.min,
                                        children: [
                                          Text('$yearsCount', style: theme.textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w700)),
                                          const Text('Años'),
                                        ],
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                            const SizedBox(height: 12),
                            SearchBar(
                              hintText: l10n.search,
                              leading: const ExcludeSemantics(child: Icon(Icons.search_rounded)),
                              onChanged: (v) => setState(() => _search = v),
                            ),
                            const SizedBox(height: 8),
                            Wrap(
                              spacing: 8,
                              runSpacing: 8,
                              crossAxisAlignment: WrapCrossAlignment.center,
                              children: [
                                FilterChip(
                                  label: const Text('Todos'),
                                  selected: !_showOnlyWinners,
                                  onSelected: (v) => setState(() => _showOnlyWinners = false),
                                ),
                                FilterChip(
                                  label: Text(l10n.winner),
                                  selected: _showOnlyWinners,
                                  avatar: const ExcludeSemantics(child: Icon(Icons.workspace_premium_rounded, size: 16)),
                                  onSelected: (v) => setState(() => _showOnlyWinners = v),
                                ),
                                DropdownButton<int?>(
                                  value: _selectedYear,
                                  hint: const Text('Año'),
                                  items: [
                                    const DropdownMenuItem<int?>(value: null, child: Text('Todos')),
                                    for (final y in _years) DropdownMenuItem<int?>(value: y, child: Text('$y')),
                                  ],
                                  onChanged: (v) => setState(() => _selectedYear = v),
                                ),
                              ],
                            ),
                            const SizedBox(height: 8),
                            if (_filtered.isEmpty)
                              const EmptyStateWidget(icon: Icons.search_off_rounded, title: 'Sin resultados', subtitle: 'Prueba con otra búsqueda o filtro')
                            else
                              for (final entry in grouped.entries) ...[
                                Padding(
                                  padding: const EdgeInsets.only(top: 12, bottom: 4, left: 4),
                                  child: SemanticHeader(
                                    text: entry.key == null ? 'Sin año' : '${entry.key}',
                                    style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700),
                                  ),
                                ),
                                for (final a in entry.value)
                                  Card(
                                    margin: const EdgeInsets.only(bottom: 8),
                                    child: ListTile(
                                      leading: CircleAvatar(
                                        backgroundColor: a.isWinner ? Colors.amber.shade700 : cs.surfaceContainerHighest,
                                        child: ExcludeSemantics(
                                          child: Icon(Icons.emoji_events_rounded, color: a.isWinner ? Colors.white : cs.onSurfaceVariant),
                                        ),
                                      ),
                                      title: Text(a.awardName, style: const TextStyle(fontWeight: FontWeight.w600)),
                                      subtitle: Column(
                                        crossAxisAlignment: CrossAxisAlignment.start,
                                        mainAxisSize: MainAxisSize.min,
                                        children: [
                                          Text(
                                            [
                                              if (a.awardCategory != null && a.awardCategory!.isNotEmpty) a.awardCategory!,
                                              if (a.position != null) 'Posición ${a.position}',
                                              if (a.prizeAmount != null && a.prizeAmount!.isNotEmpty) a.prizeAmount!,
                                            ].join(' • '),
                                            style: theme.textTheme.bodySmall,
                                          ),
                                          const SizedBox(height: 4),
                                          StatusIndicator(
                                            isActive: a.isVerified,
                                            activeLabel: l10n.verified,
                                            inactiveLabel: l10n.unverified,
                                            useChip: true,
                                          ),
                                        ],
                                      ),
                                      trailing: Row(
                                        mainAxisSize: MainAxisSize.min,
                                        children: [
                                          Semantics(
                                            label: 'Verificar ${a.awardName}',
                                            child: IconButton(
                                              icon: Icon(a.isVerified ? Icons.check_circle_rounded : Icons.check_circle_outline_rounded, size: 20),
                                              tooltip: 'Verificar',
                                              color: a.isVerified ? cs.primary : null,
                                              onPressed: () => _verifyAward(a),
                                            ),
                                          ),
                                          Semantics(
                                            label: '${l10n.edit} ${a.awardName}',
                                            child: IconButton(
                                              icon: const Icon(Icons.edit_outlined, size: 20),
                                              tooltip: l10n.edit,
                                              onPressed: () => _editAward(a),
                                            ),
                                          ),
                                          Semantics(
                                            label: '${l10n.delete} ${a.awardName}',
                                            child: IconButton(
                                              icon: const Icon(Icons.delete_outline_rounded, size: 20),
                                              tooltip: l10n.delete,
                                              onPressed: () => _deleteAward(a),
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                  ),
                              ],
                          ],
                        ),
                ),
      floatingActionButton: FloatingActionButton(onPressed: _createAward, tooltip: l10n.createAward, child: const Icon(Icons.add_rounded)),
    );
  }
}
