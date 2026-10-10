import 'package:flutter/material.dart';
import 'package:table_calendar/table_calendar.dart';

import '../l10n/app_localizations.dart';
import '../models/calendar_model.dart';
import '../services/api_service.dart';
import '../services/file_downloader.dart';
import 'empty_state_widget.dart';
import 'error_state_widget.dart';
import 'reusable_widgets.dart';
import '../screens/event_detail_screen.dart';

/// Sección de agenda compartida con calendario mensual y listado por día.
///
/// Consume `GET /api/calendar/agenda`, por lo que respeta el interruptor global
/// del administrador, los interruptores por festival y el alcance de visibilidad
/// de cada evento según haya sesión iniciada o no.
///
/// Si el backend responde `enabled: false` la sección se oculta por completo en
/// lugar de mostrar un error.
class AgendaCalendarSection extends StatefulWidget {
  /// Limita la agenda a ciertos festivales. Si es `null` se muestran todos
  /// los festivales visibles para el usuario.
  final List<int>? festivalIds;

  /// Encabezado mostrado encima del calendario. Por defecto, "Agenda".
  final String? title;

  /// Número máximo de eventos descargados en cada cambio de página.
  final int eventLimit;

  /// Muestra los filtros por festival. Desactivado si solo hay un festival.
  final bool showFestivalFilter;

  /// Permite exportar la agenda visible a un archivo ICS.
  final bool showExportAction;

  /// Se invoca al tocar un evento. Si es `null` se abre [EventDetailScreen].
  final void Function(AgendaEvent event)? onEventTap;

  /// Filtra por tipo de evento (p. ej. `screening` para la programación).
  final String? eventTypeFilter;

  /// Agrupa la lista del día por sede (`venue` o `location`).
  final bool groupByVenue;

  /// Gestos disponibles en el calendario.
  ///
  /// Usa [AvailableGestures.horizontalSwipe] cuando el widget vive dentro de una
  /// lista con desplazamiento vertical, para que el arrastre vertical desplace
  /// la página en lugar de cambiar de mes.
  final AvailableGestures gestures;

  const AgendaCalendarSection({
    super.key,
    this.festivalIds,
    this.title,
    this.eventLimit = 200,
    this.showFestivalFilter = true,
    this.showExportAction = true,
    this.onEventTap,
    this.eventTypeFilter,
    this.groupByVenue = false,
    this.gestures = AvailableGestures.all,
  });

  @override
  State<AgendaCalendarSection> createState() => _AgendaCalendarSectionState();
}

class _AgendaCalendarSectionState extends State<AgendaCalendarSection> {
  static const int _monthsBack = 1;
  static const int _monthsForward = 11;

  final ApiService _api = ApiService();

  bool _isLoading = true;
  bool _isExporting = false;
  bool _hasError = false;
  bool _isEnabled = true;

  DateTime _focusedDay = DateTime.now();
  DateTime _selectedDay = DateTime.now();
  int? _selectedFestivalId;
  Map<DateTime, List<AgendaEvent>> _eventMap = {};
  List<AgendaFestival> _festivals = const [];

  @override
  void initState() {
    super.initState();
    _selectedFestivalId = widget.festivalIds?.length == 1 ? widget.festivalIds!.first : null;
    _loadAgenda();
  }

  @override
  void didUpdateWidget(covariant AgendaCalendarSection oldWidget) {
    super.didUpdateWidget(oldWidget);
    final ids = widget.festivalIds;
    if (ids != null && ids.length == 1 && ids.first != _selectedFestivalId) {
      _selectedFestivalId = ids.first;
      _loadAgenda();
    }
  }

  /// Rango visible en el calendario; se amplía con cada cambio de página.
  DateTime get _rangeStart => DateTime(
        _focusedDay.year,
        _focusedDay.month - _monthsBack,
        1,
      );

  DateTime get _rangeEnd => DateTime(
        _focusedDay.year,
        _focusedDay.month + _monthsForward,
        1,
      );

  /// Descarga la agenda del rango visible y la indexa por día.
  Future<void> _loadAgenda() async {
    if (mounted) setState(() => _isLoading = true);
    try {
      final agenda = await _api.getAgenda(
        from: _rangeStart,
        to: _rangeEnd.add(const Duration(days: 1)),
        festivalIds: _selectedFestivalId != null ? [_selectedFestivalId!] : widget.festivalIds,
        eventType: widget.eventTypeFilter,
        limit: widget.eventLimit,
      );
      if (!mounted) return;
      if (!agenda.enabled) {
        setState(() {
          _isEnabled = false;
          _isLoading = false;
          _hasError = false;
          _eventMap = {};
          _festivals = const [];
        });
        return;
      }
      setState(() {
        _isEnabled = true;
        _isLoading = false;
        _hasError = false;
        _festivals = agenda.festivals;
        _eventMap = _buildEventMap(agenda.events);
      });
    } catch (e) {
      debugPrint('AgendaCalendarSection error: $e');
      if (mounted) {
        setState(() {
          _isLoading = false;
          _hasError = true;
        });
      }
    }
  }

  /// Reparte los eventos en cada día que abarcan, incluidos los de varios días.
  Map<DateTime, List<AgendaEvent>> _buildEventMap(List<AgendaEvent> events) {
    final map = <DateTime, List<AgendaEvent>>{};
    for (final event in events) {
      final start = event.startDate;
      final end = event.endDate ?? start;
      var day = DateTime(start.year, start.month, start.day);
      final last = DateTime(end.year, end.month, end.day);
      while (!day.isAfter(last)) {
        map.putIfAbsent(day, () => []).add(event);
        day = day.add(const Duration(days: 1));
      }
    }
    for (final list in map.values) {
      list.sort((a, b) => a.startDate.compareTo(b.startDate));
    }
    return map;
  }

  List<AgendaEvent> get _selectedDayEvents =>
      _eventMap[DateTime(_selectedDay.year, _selectedDay.month, _selectedDay.day)] ?? const [];

  /// Exporta los eventos visibles del rango actual a un archivo ICS.
  Future<void> _exportAgenda() async {
    final l10n = AppLocalizations.of(context);
    setState(() => _isExporting = true);
    try {
      final bytes = await _api.getAgendaIcs(
        from: _rangeStart,
        to: _rangeEnd.add(const Duration(days: 1)),
      );
      await downloadFile(bytes, 'agenda.ics');
    } catch (e) {
      debugPrint('AgendaCalendarSection export error: $e');
      if (mounted && l10n != null) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.exportFailed)),
        );
      }
    } finally {
      if (mounted) setState(() => _isExporting = false);
    }
  }

  Future<void> _openEvent(AgendaEvent event) async {
    final handler = widget.onEventTap;
    if (handler != null) {
      handler(event);
      return;
    }
    final id = event.id;
    if (!mounted) return;
    await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => EventDetailScreen(eventId: id, festivalName: event.festivalName),
      ),
    );
    if (mounted) _loadAgenda();
  }

  void _selectFestival(int? id) {
    setState(() => _selectedFestivalId = id);
    _loadAgenda();
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    if (!_isEnabled) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildHeader(l10n),
        if (_hasError)
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 24),
            child: ErrorStateWidget(onRetry: _loadAgenda),
          )
        else ...[
          if (widget.showFestivalFilter && _festivals.length > 1)
            _buildFestivalFilter(l10n),
          Semantics(
            label: l10n.calendar,
            child: _isLoading
                ? const Padding(
                    padding: EdgeInsets.symmetric(vertical: 48),
                    child: Center(child: CircularProgressIndicator()),
                  )
                : TableCalendar<AgendaEvent>(
                    locale: _calendarLocale(context),
                    firstDay: DateTime(_focusedDay.year - 2, 1, 1),
                    lastDay: DateTime(_focusedDay.year + 3, 12, 31),
                    focusedDay: _focusedDay,
                    selectedDayPredicate: (day) => isSameDay(day, _selectedDay),
                    eventLoader: (day) => _eventMap[day] ?? const [],
                    startingDayOfWeek: StartingDayOfWeek.monday,
                    onDaySelected: (selected, focused) {
                      setState(() {
                        _selectedDay = selected;
                        _focusedDay = focused;
                      });
                    },
                    onPageChanged: (focused) {
                      setState(() => _focusedDay = focused);
                      _loadAgenda();
                    },
                    headerStyle: const HeaderStyle(
                      formatButtonVisible: false,
                      titleCentered: true,
                      leftChevronIcon: Icon(Icons.chevron_left_rounded),
                      rightChevronIcon: Icon(Icons.chevron_right_rounded),
                    ),
                    availableGestures: widget.gestures,
                    calendarBuilders: CalendarBuilders<AgendaEvent>(
                      markerBuilder: (context, day, events) {
                        if (events.isEmpty) return null;
                        return Positioned(
                          right: 1,
                          bottom: 1,
                          child: _buildMarkers(events),
                        );
                      },
                    ),
                    calendarStyle: const CalendarStyle(
                      todayDecoration: BoxDecoration(
                        color: Colors.deepOrangeAccent,
                        shape: BoxShape.circle,
                      ),
                      selectedDecoration: BoxDecoration(
                        color: Color(0xFFB8956E),
                        shape: BoxShape.circle,
                      ),
                    ),
                  ),
          ),
          const SizedBox(height: 8),
          _buildDayList(l10n),
        ],
      ],
    );
  }

  Widget _buildHeader(AppLocalizations l10n) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 24, 12, 8),
      child: Row(
        children: [
          Expanded(
            child: SemanticHeader(
              text: widget.title ?? l10n.agenda,
              style: theme.textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.w700,
                color: theme.colorScheme.onSurfaceVariant,
                letterSpacing: 0.5,
              ),
            ),
          ),
          if (widget.showExportAction)
            Tooltip(
              message: l10n.exportCalendar,
              child: IconButton(
                onPressed: _isExporting ? null : _exportAgenda,
                icon: _isExporting
                    ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2))
                    : const Icon(Icons.ios_share_rounded),
                tooltip: l10n.exportCalendar,
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildFestivalFilter(AppLocalizations l10n) {
    return SizedBox(
      height: 44,
      child: ListView(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        children: [
          Padding(
            padding: const EdgeInsets.only(right: 8),
            child: FilterChip(
              label: Text(l10n.allFestivals, style: const TextStyle(fontSize: 13)),
              selected: _selectedFestivalId == null,
              onSelected: (_) => _selectFestival(null),
            ),
          ),
          for (final festival in _festivals)
            Padding(
              padding: const EdgeInsets.only(right: 8),
              child: FilterChip(
                avatar: CircleAvatar(
                  backgroundColor: _festivalColor(festival.id),
                  radius: 6,
                ),
                label: Text(festival.name, style: const TextStyle(fontSize: 13)),
                selected: _selectedFestivalId == festival.id,
                onSelected: (selected) => _selectFestival(selected ? festival.id : null),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildDayList(AppLocalizations l10n) {
    final events = _selectedDayEvents;
    final theme = Theme.of(context);
    if (events.isEmpty) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 4, 20, 4),
            child: Text(
              '${_formatDate(context, _selectedDay)} · 0',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 24),
            child: EmptyStateWidget(
              icon: Icons.event_busy_outlined,
              title: l10n.noEventsOnDay,
              subtitle: l10n.noEvents,
            ),
          ),
        ],
      );
    }
    if (!widget.groupByVenue) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 4, 20, 4),
            child: Text(
              '${_formatDate(context, _selectedDay)} · ${events.length}',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
          for (final event in events) _buildEventCard(l10n, event),
        ],
      );
    }
    final byVenue = <String, List<AgendaEvent>>{};
    for (final event in events) {
      final venue = (event.venue ?? event.location ?? '').trim();
      byVenue.putIfAbsent(venue.isEmpty ? '·' : venue, () => []).add(event);
    }
    final venues = byVenue.keys.toList()..sort();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        for (final venue in venues) ...[
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 12, 20, 4),
            child: Text(
              '$venue · ${byVenue[venue]!.length}',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.primary,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
          for (final event in byVenue[venue]!) _buildEventCard(l10n, event),
        ],
      ],
    );
  }

  Widget _buildEventCard(AppLocalizations l10n, AgendaEvent event) {
    final theme = Theme.of(context);
    final color = _eventColor(event);
    final start = _formatTime(event.startDate.toLocal());
    final location = (event.venue ?? event.location ?? '').trim();

    return ListItemCard(
      leading: CircleAvatar(
        backgroundColor: theme.colorScheme.primaryContainer,
        child: ExcludeSemantics(child: Icon(Icons.event_rounded, color: color)),
      ),
      title: event.title,
      titleSemanticLabel: '${l10n.events}: ${event.title}',
      subtitle: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (event.festivalName.isNotEmpty)
            Text(
              event.festivalName,
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.primary,
                fontWeight: FontWeight.w600,
              ),
            ),
          Text(
            [start, if (location.isNotEmpty) location].join(' · '),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
      trailing: event.isPrivate
          ? Tooltip(
              message: l10n.restrictedVisibility,
              child: Icon(Icons.lock_outline_rounded, size: 18, color: theme.colorScheme.onSurfaceVariant),
            )
          : null,
      onTap: () => _openEvent(event),
    );
  }

  Widget _buildMarkers(List<AgendaEvent> events) {
    final colors = events
        .map((e) => _eventColor(e))
        .take(3)
        .toList();
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        for (final color in colors)
          Container(
            width: 6,
            height: 6,
            margin: const EdgeInsets.symmetric(horizontal: 1),
            decoration: BoxDecoration(color: color, shape: BoxShape.circle),
          ),
      ],
    );
  }

  /// Color estable por festival, con el color del evento como prioridad.
  Color _eventColor(AgendaEvent event) {
    final parsed = _parseHexColor(event.color);
    return parsed ?? _festivalColor(event.festivalId);
  }

  Color _festivalColor(int festivalId) {
    const palette = [
      Color(0xFFB8956E),
      Color(0xFF7E9BC4),
      Color(0xFF8FBF9F),
      Color(0xFFC48B9C),
      Color(0xFFB4A36B),
      Color(0xFF9B8BC4),
    ];
    return palette[festivalId.abs() % palette.length];
  }

  Color? _parseHexColor(String? hex) {
    if (hex == null || hex.isEmpty) return null;
    final normalized = hex.replaceFirst('#', '');
    if (normalized.length != 6) return null;
    final value = int.tryParse(normalized, radix: 16);
    if (value == null) return null;
    return Color(0xFF000000 | value);
  }

  String _formatTime(DateTime time) =>
      '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}';

  String _calendarLocale(BuildContext context) {
    final code = Localizations.localeOf(context).languageCode;
    if (code == 'oc') return 'es';
    return code;
  }

  String _formatDate(BuildContext context, DateTime day) =>
      MaterialLocalizations.of(context).formatMediumDate(day);
}