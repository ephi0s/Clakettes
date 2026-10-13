import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../services/api_service.dart';
import '../models/award_model.dart';
import '../widgets/reusable_widgets.dart';
import '../widgets/empty_state_widget.dart';
import '../widgets/loading_skeleton.dart';
import '../widgets/error_state_widget.dart';
import '../widgets/confirm_dialog.dart';

/// Pantalla que gestiona los premios de un festival (crear, verificar, eliminar).
class AwardsScreen extends StatefulWidget {
  final int festivalId;
  final String festivalName;
  const AwardsScreen({super.key, required this.festivalId, required this.festivalName});

  @override
  State<AwardsScreen> createState() => _AwardsScreenState();
}

/// Mantiene la lista de premios cargada del festival; se carga una sola vez en
/// el primer build.
class _AwardsScreenState extends State<AwardsScreen> {
  final ApiService api = ApiService();
  List<Award> _awards = [];
  bool _isLoading = true;
  bool _hasError = false;
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

  /// Obtiene los premios del festival de la API y gestiona los errores.
  Future<void> _loadData() async {
    if (!mounted) return;
    setState(() { _isLoading = true; _hasError = false; });
    try {
      final result = await api.getAwards(widget.festivalId, size: 100);
      if (!mounted) return;
      setState(() { _awards = result.items; _isLoading = false; });
    } catch (e) {
      debugPrint('Error: $e');
      if (!mounted) return;
      setState(() { _isLoading = false; _hasError = true; });
    }
  }

  /// Muestra un diálogo para crear un nuevo premio y recarga la lista al tener éxito.
  Future<void> _createAward() async {
    final nameCtl = TextEditingController();
    final catCtl = TextEditingController();
    final descCtl = TextEditingController();
    final result = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(l10n.newAward),
        content: SingleChildScrollView(
          child: Column(mainAxisSize: MainAxisSize.min, children: [
            SemanticTextField(controller: nameCtl, label: l10n.awardNameRequired, semanticLabel: l10n.awardName, helperText: l10n.awardName),
            SemanticTextField(controller: catCtl, label: l10n.category, semanticLabel: l10n.category, helperText: l10n.category),
            SemanticTextField(controller: descCtl, label: l10n.description, semanticLabel: l10n.description, helperText: l10n.optional),
          ]),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: Text(l10n.cancel)),
          FilledButton(onPressed: () => Navigator.pop(ctx, true), child: Text(l10n.create)),
        ],
      ),
    );
    if (result == true && nameCtl.text.isNotEmpty) {
      try {
        await api.createAward(widget.festivalId, Award(festivalId: widget.festivalId, awardName: nameCtl.text, awardCategory: catCtl.text.isEmpty ? null : catCtl.text, description: descCtl.text.isEmpty ? null : descCtl.text));
        _loadData();
      } catch (e) {
        if (mounted) showAppSnack(context, l10n.errorFor(e));
      }
    }
  }

  /// Elimina el premio indicado tras un diálogo de confirmación.
  Future<void> _deleteAward(Award a) async {
    if (a.id == null) return;
    final confirm = await showConfirmDialog(context, title: l10n.deleteAward, message: l10n.deleteEntityMessage(a.awardName));
    if (confirm == true) {
      await api.deleteAward(a.id!);
      _loadData();
    }
  }

  @override
  Widget build(BuildContext context) {
    l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

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
                      : ListView.builder(
                          padding: const EdgeInsets.all(16),
                          itemCount: _awards.length,
                          itemBuilder: (ctx, i) {
                            final a = _awards[i];
                            return Card(
                              margin: const EdgeInsets.only(bottom: 12),
                              child: ListTile(
                                leading: CircleAvatar(child: Icon(Icons.emoji_events, color: Colors.yellow.shade700)),
                                title: Text(a.awardName, style: const TextStyle(fontWeight: FontWeight.w600)),
                                subtitle: Column(crossAxisAlignment: CrossAxisAlignment.start, mainAxisSize: MainAxisSize.min, children: [
                                  if (a.awardCategory != null) Text(a.awardCategory!, style: theme.textTheme.bodySmall),
                                  Text('${a.isWinner ? l10n.winner : l10n.nominee}  ${a.isPublic ? l10n.public : l10n.hidden}', style: theme.textTheme.bodySmall),
                                ]),
                                trailing: Row(mainAxisSize: MainAxisSize.min, children: [
                                  StatusIndicator(isActive: a.isVerified, activeLabel: l10n.verified, inactiveLabel: l10n.unverified),
                                  if (a.isWinner)
                                    Icon(Icons.workspace_premium, size: 20, color: Colors.amber.shade700)
                                  else
                                    IconButton(icon: const Icon(Icons.check_circle_outline, size: 20), tooltip: l10n.verify, onPressed: () {}),
                                  IconButton(icon: const Icon(Icons.delete_outline, size: 20), tooltip: l10n.delete, onPressed: () => _deleteAward(a)),
                                ]),
                              ),
                            );
                          },
                        ),
                ),
      floatingActionButton: FloatingActionButton(onPressed: _createAward, tooltip: l10n.createAward, child: const Icon(Icons.add)),
    );
  }
}
