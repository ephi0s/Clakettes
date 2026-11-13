import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../services/api_service.dart';
import '../services/file_downloader.dart';
import '../models/event_model.dart';
import '../models/screening_model.dart';
import '../models/participant_tag_model.dart';
import '../widgets/reusable_widgets.dart';
import '../widgets/seat_map_widget.dart';
import '../widgets/empty_state_widget.dart';
import '../widgets/loading_skeleton.dart';
import 'payments_screen.dart';

/// Pantalla que muestra los detalles del evento, los tipos de entrada y un mapa
/// de asientos interactivo con creación, confirmación y cancelación de reservas.
class EventDetailScreen extends StatefulWidget {
  final int eventId;
  final String festivalName;

  const EventDetailScreen({super.key, required this.eventId, required this.festivalName});

  @override
  State<EventDetailScreen> createState() => _EventDetailScreenState();
}

/// Mantiene el evento cargado, los tipos de entrada, los asientos y la reserva
/// del usuario.
class _EventDetailScreenState extends State<EventDetailScreen> with SingleTickerProviderStateMixin {
  final ApiService api = ApiService();
  FestivalEvent? _event;
  List<EventTicketType> _ticketTypes = [];
  List<EventSeat> _seats = [];
  EventReservation? _myReservation;
  final Set<int> _selectedSeatIds = {};
  bool _isLoading = true;
  bool _hasError = false;
  bool _isExporting = false;
  EventScreenings? _screenings;
  bool _isLoadingScreenings = false;
  String? _screeningStatusFilter;
  bool _hideDisqualified = false;
  String? _screeningTagCategory;
  List<ParticipantTag> _screeningTags = [];
  late TabController _tabController;
  late AppLocalizations l10n;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _loadData();
  }

  /// Ajusta el número de pestañas según si el evento es una proyección.
  void _syncTabController(int length) {
    if (_tabController.length == length) return;
    _tabController.dispose();
    _tabController = TabController(length: length, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  /// Carga el evento, los tipos de entrada, los asientos y mi reserva en paralelo.
  Future<void> _loadData() async {
    setState(() { _isLoading = true; _hasError = false; });
    try {
      final results = await Future.wait([
        api.getEvent(widget.eventId),
        api.getEventTicketTypes(widget.eventId),
        api.getSeats(widget.eventId, size: 500),
        api.getMyReservation(widget.eventId),
      ]);
      if (mounted) {
        final event = results[0] as FestivalEvent;
        final isScreening = event.eventType == 'screening' &&
            event.screeningShortfilmIds.isNotEmpty;
        _syncTabController(isScreening ? 3 : 2);
        setState(() {
          _event = event;
          _ticketTypes = results[1] as List<EventTicketType>;
          _seats = (results[2] as PaginatedResult<EventSeat>).items;
          _myReservation = results[3] as EventReservation?;
          _isLoading = false;
        });
        if (isScreening) {
          await _loadScreenings();
        } else if (mounted) {
          setState(() => _screenings = null);
        }
      }
    } catch (e) {
      debugPrint('Error: $e');
      if (mounted) setState(() { _isLoading = false; _hasError = true; });
    }
  }

  /// Muestra un diálogo para generar en bloque una cuadrícula de asientos
  /// para el evento.
  Future<void> _bulkCreateSeats() async {
    final sectionCtl = TextEditingController();
    final rowsCtl = TextEditingController(text: '10');
    final seatsPerRowCtl = TextEditingController(text: '12');
    final startNumCtl = TextEditingController(text: '1');

    final result = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(l10n.generateSeats),
        content: SingleChildScrollView(
          child: Column(mainAxisSize: MainAxisSize.min, children: [
            TextField(controller: sectionCtl, decoration: InputDecoration(labelText: l10n.sectionLabel, hintText: l10n.sectionHint)),
            TextField(controller: rowsCtl, decoration: InputDecoration(labelText: l10n.rows), keyboardType: TextInputType.number),
            TextField(controller: seatsPerRowCtl, decoration: InputDecoration(labelText: l10n.seatsPerRow), keyboardType: TextInputType.number),
            TextField(controller: startNumCtl, decoration: InputDecoration(labelText: l10n.startNumber), keyboardType: TextInputType.number),
          ]),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: Text(l10n.cancel)),
          FilledButton(onPressed: () => Navigator.pop(ctx, true), child: Text(l10n.generate)),
        ],
      ),
    );

    if (result == true && sectionCtl.text.isNotEmpty) {
      try {
        final config = {
          'section': sectionCtl.text,
          'rows': int.tryParse(rowsCtl.text) ?? 10,
          'seats_per_row': int.tryParse(seatsPerRowCtl.text) ?? 12,
          'start_number': int.tryParse(startNumCtl.text) ?? 1,
        };
        await api.bulkCreateSeats(widget.eventId, config);
        _loadData();
      } catch (e) {
        if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.errorFor(e)), behavior: SnackBarBehavior.floating));
      }
    }
  }

  void _onSeatTap(EventSeat seat) {
    if (!mounted) return;
    setState(() {
      if (_selectedSeatIds.contains(seat.id)) {
        _selectedSeatIds.remove(seat.id);
      } else {
        _selectedSeatIds.add(seat.id!);
      }
    });
  }

  /// Crea una reserva de los asientos seleccionados para el usuario actual.
  Future<void> _createReservation() async {
    if (_myReservation != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(l10n.alreadyHasReservation), behavior: SnackBarBehavior.floating),
      );
      return;
    }
    try {
      final seats = _seats.where((s) => _selectedSeatIds.contains(s.id)).toList();
      final reservation = await api.createReservation(
        widget.eventId,
        {
          'notes': null,
          'attendees': seats.map((s) => {
            'seat_id': s.id,
            'ticket_type_id': s.ticketTypeId,
          }).toList(),
        },
      );
      if (mounted) {
        setState(() {
          _myReservation = reservation;
          _selectedSeatIds.clear();
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.reservationCreated), behavior: SnackBarBehavior.floating),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.errorFor(e)), behavior: SnackBarBehavior.floating),
        );
      }
    }
  }

  /// Confirma la reserva pendiente actual.
  Future<void> _confirmReservation() async {
    if (_myReservation?.id == null) return;
    try {
      final reservation = await api.confirmReservation(_myReservation!.id!);
      if (mounted) {
        setState(() => _myReservation = reservation);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.reservationConfirmed), behavior: SnackBarBehavior.floating),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.errorFor(e)), behavior: SnackBarBehavior.floating),
        );
      }
    }
  }

  /// Cancela la reserva actual y recarga los datos de los asientos.
  Future<void> _cancelReservation() async {
    if (_myReservation?.id == null) return;
    try {
      await api.cancelReservation(_myReservation!.id!);
      if (mounted) {
        setState(() => _myReservation = null);
        _loadData();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.reservationCancelled), behavior: SnackBarBehavior.floating),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.errorFor(e)), behavior: SnackBarBehavior.floating),
        );
      }
    }
  }

  /// Carga el bloque de cribado del evento aplicando los filtros actuales.
  Future<void> _loadScreenings() async {
    setState(() => _isLoadingScreenings = true);
    try {
      final tags =
          _screeningTags.isEmpty ? await api.getParticipantTags(size: 100) : null;
      final screenings = await api.getEventScreenings(
        widget.eventId,
        status: _screeningStatusFilter,
        includeDisqualified: !_hideDisqualified,
        participantTagCategory: _screeningTagCategory,
      );
      if (!mounted) return;
      setState(() {
        _screenings = screenings;
        _screeningTags = tags?.items ?? _screeningTags;
        _isLoadingScreenings = false;
      });
    } catch (e) {
      debugPrint('Error: $e');
      if (!mounted) return;
      setState(() => _isLoadingScreenings = false);
    }
  }

  /// Cambia el estado de cribado de una obra; pide motivo si se descalifica.
  Future<void> _setScreeningStatus(ScreeningItem item, String status) async {
    String? reason;
    if (status == 'disqualified') {
      reason = await _promptScreeningReason(item);
      if (reason == null) return;
    }
    try {
      await api.setScreeningStatus(widget.eventId, item.shortfilmId, status,
          reason: reason);
      await _loadScreenings();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
              content: Text(l10n.errorFor(e)),
              behavior: SnackBarBehavior.floating),
        );
      }
    }
  }

  /// Pide el motivo de descalificación de una obra.
  Future<String?> _promptScreeningReason(ScreeningItem item) {
    final reasonCtl = TextEditingController(text: item.statusReason ?? '');
    return showDialog<String>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(l10n.disqualify),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(item.title ?? '${item.shortfilmId}'),
            const SizedBox(height: 8),
            SemanticTextField(
              controller: reasonCtl,
              label: l10n.statusReason,
              semanticLabel: l10n.statusReason,
              maxLines: 2,
            ),
          ],
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(ctx), child: Text(l10n.cancel)),
          FilledButton(
              onPressed: () => Navigator.pop(ctx, reasonCtl.text.trim()),
              child: Text(l10n.disqualify)),
        ],
      ),
    );
  }

  /// Guarda las notas y la anotación del jurado para una obra.
  Future<void> _editScreeningNotes(ScreeningItem item) async {
    final notesCtl = TextEditingController(text: item.juryNotes ?? '');
    final minutesCtl = TextEditingController(text: item.minutes ?? '');
    String? annotation = item.annotation;
    final saved = await showDialog<bool>(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setDialog) => AlertDialog(
          title: Text(l10n.screeningNotesTitle),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(item.title ?? '${item.shortfilmId}'),
              const SizedBox(height: 8),
              SemanticTextField(
                controller: notesCtl,
                label: l10n.juryNotes,
                semanticLabel: l10n.juryNotes,
                maxLines: 3,
              ),
              const SizedBox(height: 8),
              SemanticTextField(
                controller: minutesCtl,
                label: l10n.minutes,
                semanticLabel: l10n.minutes,
              ),
              const SizedBox(height: 8),
              DropdownButtonFormField<String?>(
                initialValue: annotation,
                decoration: InputDecoration(labelText: l10n.annotation),
                items: [
                  const DropdownMenuItem<String?>(value: null, child: Text('—')),
                  DropdownMenuItem<String?>(
                      value: 'special_mention', child: Text(l10n.specialMention)),
                  DropdownMenuItem<String?>(
                      value: 'accesit', child: Text(l10n.accesit)),
                  DropdownMenuItem<String?>(
                      value: 'other', child: Text(l10n.other)),
                ],
                onChanged: (v) => setDialog(() => annotation = v),
              ),
            ],
          ),
          actions: [
            TextButton(
                onPressed: () => Navigator.pop(ctx, false),
                child: Text(l10n.cancel)),
            FilledButton(
                onPressed: () => Navigator.pop(ctx, true),
                child: Text(l10n.save)),
          ],
        ),
      ),
    );
    if (saved != true) return;
    try {
      await api.setScreeningNotes(
        widget.eventId,
        item.shortfilmId,
        juryNotes: notesCtl.text.trim().isEmpty ? null : notesCtl.text.trim(),
        minutes: minutesCtl.text.trim().isEmpty ? null : minutesCtl.text.trim(),
        annotation: annotation,
      );
      await _loadScreenings();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
              content: Text(l10n.errorFor(e)),
              behavior: SnackBarBehavior.floating),
        );
      }
    }
  }

  String _screeningStatusLabel(ScreeningItem item) {
    switch (item.status) {
      case 'screened':
        return l10n.screened;
      case 'disqualified':
        return l10n.disqualified;
      default:
        return l10n.pending;
    }
  }

  Widget _buildScreeningTab(ColorScheme cs) {
    if (_isLoadingScreenings && _screenings == null) return const ListSkeleton();
    final screenings = _screenings;
    if (screenings == null || screenings.items.isEmpty) {
      return EmptyStateWidget(
          icon: Icons.movie_filter_outlined,
          title: l10n.noScreenings,
          subtitle: '');
    }
    final categories = _screeningTags.map((t) => t.category).toSet().toList()
      ..sort();
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          child: Wrap(
            spacing: 8,
            runSpacing: 8,
            crossAxisAlignment: WrapCrossAlignment.center,
            children: [
              FilterChip(
                label: Text(l10n.all),
                selected: _screeningStatusFilter == null && !_hideDisqualified,
                onSelected: (_) {
                  setState(() {
                    _screeningStatusFilter = null;
                    _hideDisqualified = false;
                  });
                  _loadScreenings();
                },
              ),
              FilterChip(
                label: Text(l10n.pending),
                selected: _screeningStatusFilter == 'pending',
                onSelected: (_) {
                  setState(() => _screeningStatusFilter = 'pending');
                  _loadScreenings();
                },
              ),
              FilterChip(
                label: Text(l10n.screened),
                selected: _screeningStatusFilter == 'screened',
                onSelected: (_) {
                  setState(() => _screeningStatusFilter = 'screened');
                  _loadScreenings();
                },
              ),
              FilterChip(
                label: Text(l10n.disqualified),
                selected: _screeningStatusFilter == 'disqualified',
                onSelected: (_) {
                  setState(() => _screeningStatusFilter = 'disqualified');
                  _loadScreenings();
                },
              ),
              FilterChip(
                label: Text(l10n.hideDisqualified),
                selected: _hideDisqualified,
                onSelected: (v) {
                  setState(() => _hideDisqualified = v);
                  _loadScreenings();
                },
              ),
              if (categories.isNotEmpty)
                DropdownButton<String?>(
                  value: _screeningTagCategory,
                  hint: Text(l10n.eligibilityTags),
                  items: [
                    DropdownMenuItem<String?>(
                        value: null, child: Text(l10n.all)),
                    for (final c in categories)
                      DropdownMenuItem<String?>(value: c, child: Text(c)),
                  ],
                  onChanged: (v) {
                    setState(() => _screeningTagCategory = v);
                    _loadScreenings();
                  },
                ),
            ],
          ),
        ),
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.symmetric(horizontal: 12),
            itemCount: screenings.items.length,
            itemBuilder: (ctx, i) {
              final item = screenings.items[i];
              return Card(
                margin: const EdgeInsets.only(bottom: 8),
                child: ListTile(
                  leading: CircleAvatar(
                    radius: 14,
                    child: Text('${item.sortOrder + 1}',
                        style: const TextStyle(fontSize: 12)),
                  ),
                  title: Text(item.title ?? '${item.shortfilmId}',
                      style: const TextStyle(fontWeight: FontWeight.w600)),
                  subtitle: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Row(
                        children: [
                          StatusIndicator(
                            isActive: item.isDisqualifiedStatus,
                            activeLabel: l10n.disqualified,
                            inactiveLabel: _screeningStatusLabel(item),
                            useChip: true,
                          ),
                          if (item.duration != null) ...[
                            const SizedBox(width: 8),
                            Text('${item.duration} ${l10n.minutes}'),
                          ],
                        ],
                      ),
                      if (item.statusReason != null &&
                          item.statusReason!.isNotEmpty)
                        Text('${l10n.statusReason}: ${item.statusReason}',
                            style: Theme.of(ctx).textTheme.bodySmall),
                      if (item.annotation != null)
                        Text(
                          '${l10n.annotation}: ${item.annotation == 'special_mention' ? l10n.specialMention : item.annotation == 'accesit' ? l10n.accesit : l10n.other}',
                          style: Theme.of(ctx).textTheme.bodySmall,
                        ),
                      if (item.juryNotes != null && item.juryNotes!.isNotEmpty)
                        Text(item.juryNotes!,
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                            style: Theme.of(ctx).textTheme.bodySmall),
                    ],
                  ),
                  trailing: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      IconButton(
                        icon: const Icon(Icons.edit_note_outlined, size: 20),
                        tooltip: l10n.screeningNotesTitle,
                        onPressed: () => _editScreeningNotes(item),
                      ),
                      PopupMenuButton<String>(
                        tooltip: l10n.status,
                        icon: const Icon(Icons.flag_outlined, size: 20),
                        onSelected: (v) => _setScreeningStatus(item, v),
                        itemBuilder: (ctx) => [
                          PopupMenuItem(
                              value: 'screened', child: Text(l10n.markScreened)),
                          PopupMenuItem(
                              value: 'disqualified',
                              child: Text(l10n.disqualify)),
                          PopupMenuItem(
                              value: 'pending', child: Text(l10n.restorePending)),
                        ],
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  /// Descarga el CSV de asistentes del evento y notifica el resultado.
  Future<void> _exportAttendees() async {
    if (_isExporting) return;
    setState(() { _isExporting = true; });
    try {
      final bytes = await api.getBytes('/events/${widget.eventId}/attendees/export/csv');
      await downloadFile(bytes, 'attendees.csv');
      if (!mounted) return;
      setState(() { _isExporting = false; });
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.exportSuccess), behavior: SnackBarBehavior.floating));
    } catch (e) {
      debugPrint('Error: $e');
      if (!mounted) return;
      setState(() { _isExporting = false; });
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.errorFor(e)), behavior: SnackBarBehavior.floating));
    }
  }

  @override
  Widget build(BuildContext context) {
    l10n = AppLocalizations.of(context)!;
    final cs = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(
        title: Text(_event?.title ?? '${l10n.events} — ${widget.festivalName}'),
        actions: [
          IconButton(
            icon: _isExporting
                ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2))
                : const Icon(Icons.people_alt_outlined),
            tooltip: l10n.exportAttendees,
            onPressed: _isExporting ? null : _exportAttendees,
          ),
        ],
        bottom: _event != null
            ? TabBar(
                controller: _tabController,
                tabs: [
                  Tab(text: l10n.details),
                  Tab(text: '${l10n.seats} (${_seats.length})'),
                  if (_event!.eventType == 'screening')
                    Tab(text: l10n.screening),
                ],
              )
            : null,
      ),
      body: _isLoading
          ? const ListSkeleton()
          : _hasError
              ? Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.error_outline, size: 48),
                      const SizedBox(height: 16),
                      FilledButton(onPressed: _loadData, child: Text(l10n.retry)),
                    ],
                  ),
                )
              : TabBarView(
                  controller: _tabController,
                  children: [
                    _buildInfoTab(cs),
                    _buildSeatsTab(cs),
                    if (_event?.eventType == 'screening') _buildScreeningTab(cs),
                  ],
                ),
    );
  }

  Widget _buildInfoTab(ColorScheme cs) {
    if (_event == null) return const SizedBox.shrink();
    final e = _event!;
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(children: [
                    Icon(Icons.event, size: 20, color: cs.primary),
                    const SizedBox(width: 8),
                    Text(e.title, style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: cs.onSurface)),
                  ]),
                  const SizedBox(height: 12),
                  _infoRow(cs, Icons.description_outlined, l10n.description, e.description ?? '-'),
                  _infoRow(cs, Icons.category_outlined, l10n.type, e.eventType ?? '-'),
                  _infoRow(cs, Icons.calendar_today, l10n.start, e.startDate?.toLocal().toString().substring(0, 16) ?? '-'),
                  _infoRow(cs, Icons.calendar_today, l10n.end, e.endDate?.toLocal().toString().substring(0, 16) ?? '-'),
                  if (e.venue != null)
                    _infoRow(cs, Icons.location_on, l10n.venue, e.venue!),
                  _infoRow(cs, Icons.people, l10n.capacity, '${e.capacity ?? '-'}'),
                  _infoRow(cs, Icons.event_seat, l10n.seatMap, e.showSeatMap ? l10n.yes : l10n.no),
                  if (e.screeningShortfilmIds.isNotEmpty)
                    _infoRow(cs, Icons.movie_outlined, 'Cortos', '${e.screeningShortfilmIds.length}'),
                ],
              ),
            ),
          ),
          if (e.eventType == 'screening' &&
              _screenings != null &&
              _screenings!.items.isNotEmpty)
            Card(
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '${l10n.screening} (${_screenings!.items.length})${_screenings!.totalDuration > 0 ? ' · ${_screenings!.totalDuration} ${l10n.minutes}' : ''}',
                      style: const TextStyle(fontWeight: FontWeight.w700),
                    ),
                    const SizedBox(height: 4),
                    for (var i = 0; i < _screenings!.items.length; i++)
                      ListTile(
                        dense: true,
                        contentPadding: EdgeInsets.zero,
                        leading: CircleAvatar(
                            radius: 12,
                            child: Text('${i + 1}',
                                style: const TextStyle(fontSize: 12))),
                        title: Text(
                          _screenings!.items[i].title ??
                              'Corto ${_screenings!.items[i].shortfilmId}',
                          style: const TextStyle(fontSize: 13),
                        ),
                        trailing: Text(
                          _screeningStatusLabel(_screenings!.items[i]),
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                      ),
                  ],
                ),
              ),
            ),
          const SizedBox(height: 12),
          FutureBuilder<Map<String, dynamic>>(
            future: api.getEventOccupancy(widget.eventId),
            builder: (ctx, snap) {
              if (!snap.hasData) return const SizedBox.shrink();
              final occ = snap.data!;
              return Card(
                child: ListTile(
                  leading: const Icon(Icons.meeting_room_outlined),
                  title: Text('Ocupación: ${occ['attendee_count'] ?? 0}/${occ['capacity'] ?? '-'}'),
                  subtitle: Text((occ['is_full'] ?? false) ? 'Completo' : 'Disponibles: ${occ['available_capacity'] ?? '-'}'),
                ),
              );
            },
          ),
          const SizedBox(height: 12),
          FilledButton.tonalIcon(
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => PaymentsScreen(eventId: widget.eventId)),
            ),
            icon: const Icon(Icons.payments_outlined),
            label: const Text('Pagar / Pagos (mock)'),
          ),
          const SizedBox(height: 16),
          Text(l10n.ticketTypes, style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600, color: cs.onSurface)),
          const SizedBox(height: 8),
          if (_ticketTypes.isEmpty)
            EmptyStateWidget(icon: Icons.confirmation_number_outlined, title: l10n.noTicketTypes, subtitle: '')
          else
            ..._ticketTypes.map((t) => Card(
              margin: const EdgeInsets.only(bottom: 8),
              child: ListTile(
                leading: Container(
                  width: 12, height: 12,
                  decoration: BoxDecoration(
                    color: t.colorCode != null ? Color(int.parse(t.colorCode!.replaceFirst('#', '0xFF'))) : cs.primary,
                    borderRadius: BorderRadius.circular(3),
                  ),
                ),
                title: Text(t.name, style: const TextStyle(fontWeight: FontWeight.w600)),
                subtitle: Text('${t.price?.toStringAsFixed(2) ?? '-'}  |  ${l10n.capacityFormat(t.capacity)}'),
              ),
            )),
        ],
      ),
    );
  }

  Widget _infoRow(ColorScheme cs, IconData icon, String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 18, color: cs.onSurfaceVariant),
          const SizedBox(width: 8),
          SizedBox(width: 80, child: Text(label, style: TextStyle(color: cs.onSurfaceVariant, fontSize: 13))),
          Expanded(child: Text(value, style: const TextStyle(fontSize: 13))),
        ],
      ),
    );
  }

  Widget _buildSeatsTab(ColorScheme cs) {
    return Column(
      children: [
        if (_event?.showSeatMap == true) ...[
          if (_myReservation != null)
            _buildReservationBanner(cs),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: Row(
              children: [
                FilledButton.tonalIcon(
                  onPressed: _bulkCreateSeats,
                  icon: const Icon(Icons.add, size: 18),
                  label: Text(l10n.generateSeats),
                ),
                const SizedBox(width: 8),
                if (_selectedSeatIds.isNotEmpty)
                  FilledButton.tonalIcon(
                    onPressed: () {
                      setState(() => _selectedSeatIds.clear());
                    },
                    icon: const Icon(Icons.clear, size: 18),
                    label: Text('${l10n.clear} (${_selectedSeatIds.length})'),
                  ),
                const Spacer(),
                if (_myReservation == null && _selectedSeatIds.isNotEmpty)
                  FilledButton.icon(
                    onPressed: _createReservation,
                    icon: const Icon(Icons.book_online, size: 18),
                    label: Text(l10n.reserveCount(_selectedSeatIds.length)),
                  ),
              ],
            ),
          ),
          Expanded(
            child: SeatMapWidget(
              seats: _seats,
              selectedSeatIds: _selectedSeatIds,
              onSeatTap: _onSeatTap,
            ),
          ),
        ] else
          Expanded(
            child:             EmptyStateWidget(
              icon: Icons.event_seat_outlined,
              title: l10n.seatMapDisabled,
              subtitle: l10n.enableSeatMapHint,
            ),
          ),
      ],
    );
  }

  Widget _buildReservationBanner(ColorScheme cs) {
    final r = _myReservation!;
    final isPending = r.status == 'pending';
    final isConfirmed = r.status == 'confirmed';
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      color: isConfirmed ? cs.primaryContainer.withValues(alpha: 0.3) : cs.tertiaryContainer.withValues(alpha: 0.3),
      child: Row(
        children: [
          Icon(isConfirmed ? Icons.check_circle : Icons.pending, size: 20, color: isConfirmed ? cs.primary : cs.tertiary),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              isConfirmed ? l10n.reservationConfirmed : l10n.reservationPending,
              style: TextStyle(fontWeight: FontWeight.w600, color: isConfirmed ? cs.primary : cs.tertiary),
            ),
          ),
          if (isPending)
            FilledButton.tonalIcon(
              onPressed: _confirmReservation,
              icon: const Icon(Icons.check, size: 16),
              label: Text(l10n.confirm),
              style: FilledButton.styleFrom(visualDensity: VisualDensity.compact),
            ),
          const SizedBox(width: 4),
          TextButton.icon(
            onPressed: _cancelReservation,
            icon: const Icon(Icons.close, size: 16),
            label: Text(l10n.cancel),
            style: TextButton.styleFrom(visualDensity: VisualDensity.compact),
          ),
        ],
      ),
    );
  }
}
