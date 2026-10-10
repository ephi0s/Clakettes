import 'package:flutter/material.dart';

import '../l10n/app_localizations.dart';
import '../models/calendar_model.dart';
import '../services/api_service.dart';
import '../widgets/empty_state_widget.dart';
import '../widgets/error_state_widget.dart';
import '../widgets/reusable_widgets.dart';

/// Ajustes de la agenda compartida, solo para el administrador global.
///
/// Permite activar o desactivar la agenda para toda la plataforma y elegir qué
/// festivales aportan sus eventos. Los interruptores por festival se guardan en
/// bloque: [ApiService.updateCalendarSettings] envía la lista completa de los
/// que deben seguir visibles.
class CalendarSettingsScreen extends StatefulWidget {
  const CalendarSettingsScreen({super.key});

  @override
  State<CalendarSettingsScreen> createState() => _CalendarSettingsScreenState();
}

class _CalendarSettingsScreenState extends State<CalendarSettingsScreen> {
  final ApiService _api = ApiService();

  bool _isLoading = true;
  bool _isSaving = false;
  bool _hasError = false;
  bool _calendarEnabled = true;
  List<CalendarFestivalVisibility> _festivals = const [];

  /// Copia editable; los interruptores se aplican aquí y se guardan juntos.
  late Map<int, bool> _draft;

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    setState(() {
      _isLoading = true;
      _hasError = false;
    });
    try {
      final settings = await _api.getCalendarSettings();
      if (!mounted) return;
      setState(() {
        _calendarEnabled = settings.calendarEnabled;
        _festivals = settings.festivals;
        _draft = {for (final f in settings.festivals) f.id: f.showInCalendar};
        _isLoading = false;
      });
    } catch (e) {
      debugPrint('CalendarSettingsScreen error: $e');
      if (mounted) {
        setState(() {
          _isLoading = false;
          _hasError = true;
        });
      }
    }
  }

  /// Guarda el interruptor global y la visibilidad de cada festival.
  Future<void> _save() async {
    final l10n = AppLocalizations.of(context);
    if (l10n == null) return;
    setState(() => _isSaving = true);
    try {
      final visibleIds = _draft.entries.where((e) => e.value).map((e) => e.key).toList();
      final settings = await _api.updateCalendarSettings(
        calendarEnabled: _calendarEnabled,
        festivalIds: visibleIds,
      );
      if (!mounted) return;
      setState(() {
        _calendarEnabled = settings.calendarEnabled;
        _festivals = settings.festivals;
        _draft = {for (final f in settings.festivals) f.id: f.showInCalendar};
        _isSaving = false;
      });
      _showMessage(l10n.settingsSaved);
    } catch (e) {
      debugPrint('CalendarSettingsScreen save error: $e');
      if (!mounted) return;
      setState(() => _isSaving = false);
      _showMessage(l10n.errorFormatWith('$e'));
    }
  }

  void _showMessage(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), behavior: SnackBarBehavior.floating),
    );
  }

  /// Elimina de [visibleIds] el festival con el interruptor apagado.
  void _setFestival(int id, bool value) {
    setState(() {
      _draft[id] = value;
      _festivals = _festivals
          .map((f) => f.id == id ? f.copyWith(showInCalendar: value) : f)
          .toList();
    });
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return Scaffold(
      appBar: AppBar(title: Text(l10n.calendarSettings)),
      body: _buildBody(l10n),
      floatingActionButton: _isLoading || _hasError
          ? null
          : FloatingActionButton.extended(
              onPressed: _isSaving ? null : _save,
              icon: _isSaving
                  ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2))
                  : const Icon(Icons.save_outlined),
              label: Text(l10n.save),
              tooltip: l10n.settingsSaved,
            ),
    );
  }

  Widget _buildBody(AppLocalizations l10n) {
    if (_isLoading) return const Center(child: CircularProgressIndicator());
    if (_hasError) return ErrorStateWidget(onRetry: _loadSettings);

    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 96),
      children: [
        Semantics(
          container: true,
          label: l10n.enableAgenda,
          child: Card(
            child: SwitchListTile(
              value: _calendarEnabled,
              onChanged: (v) => setState(() => _calendarEnabled = v),
              title: Text(l10n.enableAgenda),
              subtitle: Text(l10n.calendarSettingsDescription),
              secondary: const Icon(Icons.calendar_month_outlined),
              isThreeLine: true,
            ),
          ),
        ),
        const SizedBox(height: 16),
        if (!_calendarEnabled)
          Padding(
            padding: const EdgeInsets.only(bottom: 16),
            child: EmptyStateWidget(
              icon: Icons.event_busy_outlined,
              title: l10n.agendaDisabled,
              subtitle: l10n.calendarSettingsDescription,
            ),
          ),
        Padding(
          padding: const EdgeInsets.fromLTRB(4, 0, 4, 8),
          child: SemanticHeader(
            text: l10n.visibleFestivals,
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.w700,
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                ),
          ),
        ),
        if (_festivals.isEmpty)
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 32),
            child: EmptyStateWidget(
              icon: Icons.festival_outlined,
              title: l10n.noFestivals,
              subtitle: l10n.subtitle,
            ),
          )
        else
          Card(
            child: Column(
              children: [
                for (var i = 0; i < _festivals.length; i++) ...[
                  if (i > 0) const Divider(height: 1),
                  _buildFestivalTile(l10n, _festivals[i]),
                ],
              ],
            ),
          ),
      ],
    );
  }

  Widget _buildFestivalTile(AppLocalizations l10n, CalendarFestivalVisibility festival) {
    final enabled = _draft[festival.id] ?? festival.showInCalendar;
    return Semantics(
      container: true,
      label: '${festival.name}: ${enabled ? l10n.showInAgenda : l10n.hideFromAgenda}',
      child: SwitchListTile(
        value: enabled,
        onChanged: (v) => _setFestival(festival.id, v),
        title: Text(festival.name),
        subtitle: Text(
          [
            if ((festival.location ?? '').isNotEmpty) festival.location!,
            if (festival.eventCount > 0) '${festival.eventCount}',
          ].join(' · '),
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        secondary: CircleAvatar(
          backgroundImage: festival.logoUrl != null ? NetworkImage(festival.logoUrl!) : null,
          child: festival.logoUrl != null
              ? null
              : ExcludeSemantics(child: Text(festival.name.substring(0, 1).toUpperCase())),
        ),
      ),
    );
  }
}