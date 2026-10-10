import 'package:flutter/material.dart';
import 'package:table_calendar/table_calendar.dart';
import '../l10n/app_localizations.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import '../services/notification_service.dart';
import '../widgets/agenda_calendar_widget.dart';

/// Calendario mensual de la agenda compartida.
///
/// Ya no consulta cada festival por separado: delega en
/// `GET /api/calendar/agenda`, que aplica el interruptor global, los
/// interruptores por festival y el alcance de visibilidad de cada evento.
/// Funciona con sesión (agenda completa) y sin ella (solo eventos públicos).
///
/// Los recordatorios siguen alimentándose de `getMyEvents()`, que devuelve los
/// eventos propios del usuario; la agenda es informativa y no genera avisos.
class CalendarScreen extends StatefulWidget {
  const CalendarScreen({super.key});

  @override
  State<CalendarScreen> createState() => _CalendarScreenState();
}

class _CalendarScreenState extends State<CalendarScreen> {
  int _agendaKey = 0;
  bool _isLoggedIn = false;
  bool _isLoadingSession = true;
  bool _screeningsOnly = false;
  bool _groupByVenue = false;

  @override
  void initState() {
    super.initState();
    _loadSession();
  }

  /// Detecta la sesión para reconstruir la agenda y refrescar los recordatorios.
  Future<void> _loadSession() async {
    final loggedIn = await AuthService().isLoggedIn();
    if (!mounted) return;
    setState(() {
      _isLoggedIn = loggedIn;
      _agendaKey++;
      _isLoadingSession = false;
    });
    if (loggedIn) _syncReminders();
  }

  /// Reprograma los avisos de los eventos propios del usuario.
  Future<void> _syncReminders() async {
    try {
      final events = await ApiService().getMyEvents();
      await NotificationService.instance.rescheduleAll(events);
    } catch (e) {
      debugPrint('CalendarScreen rescheduleAll error: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    if (_isLoadingSession) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      body: RefreshIndicator(
        onRefresh: _loadSession,
        child: ListView(
          padding: const EdgeInsets.only(bottom: 88),
          children: [
            if (_isLoggedIn)
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
                child: Align(
                  alignment: Alignment.centerLeft,
                  child: Semantics(
                    label: l10n.remindersEnabled,
                    child: Chip(
                      avatar: const Icon(Icons.notifications_active_outlined, size: 18),
                      label: Text(
                        l10n.remindersEnabled,
                        style: const TextStyle(fontSize: 12),
                      ),
                    ),
                  ),
                ),
              ),
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
              child: Wrap(
                spacing: 8,
                children: [
                  FilterChip(
                    label: Text(l10n.screenings),
                    selected: _screeningsOnly,
                    onSelected: (v) => setState(() { _screeningsOnly = v; _agendaKey++; }),
                  ),
                  FilterChip(
                    label: Text(l10n.byVenue),
                    selected: _groupByVenue,
                    onSelected: (v) => setState(() { _groupByVenue = v; _agendaKey++; }),
                  ),
                ],
              ),
            ),
            AgendaCalendarSection(
              key: ValueKey('${_agendaKey}_${_screeningsOnly}_$_groupByVenue'),
              title: l10n.calendar,
              eventTypeFilter: _screeningsOnly ? 'screening' : null,
              groupByVenue: _groupByVenue,
              gestures: AvailableGestures.horizontalSwipe,
            ),
          ],
        ),
      ),
    );
  }
}