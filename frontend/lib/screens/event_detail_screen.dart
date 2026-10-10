import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../services/api_service.dart';
import '../services/file_downloader.dart';
import '../models/event_model.dart';
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
  late TabController _tabController;
  late AppLocalizations l10n;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _loadData();
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
        setState(() {
          _event = results[0] as FestivalEvent;
          _ticketTypes = results[1] as List<EventTicketType>;
          _seats = (results[2] as PaginatedResult<EventSeat>).items;
          _myReservation = results[3] as EventReservation?;
          _isLoading = false;
        });
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
        if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.errorFormatWith(e.toString())), behavior: SnackBarBehavior.floating));
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
          SnackBar(content: Text(l10n.errorFormatWith(e.toString())), behavior: SnackBarBehavior.floating),
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
          SnackBar(content: Text(l10n.errorFormatWith(e.toString())), behavior: SnackBarBehavior.floating),
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
          SnackBar(content: Text(l10n.errorFormatWith(e.toString())), behavior: SnackBarBehavior.floating),
        );
      }
    }
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
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.errorFormatWith('$e')), behavior: SnackBarBehavior.floating));
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
          if (e.eventType == 'screening' && e.screeningShortfilmIds.isNotEmpty)
            FutureBuilder<Map<String, dynamic>>(
              future: api.getEventScreeningBlock(widget.eventId),
              builder: (ctx, snap) {
                if (!snap.hasData) return const SizedBox.shrink();
                final items = List<Map<String, dynamic>>.from(snap.data!['items'] as List? ?? []);
                final total = snap.data!['total_duration'];
                if (items.isEmpty) return const SizedBox.shrink();
                return Card(
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Bloque (${items.length})${total != null && (total as int) > 0 ? ' · $total min' : ''}',
                            style: const TextStyle(fontWeight: FontWeight.w700)),
                        const SizedBox(height: 4),
                        for (var i = 0; i < items.length; i++)
                          ListTile(
                            dense: true,
                            contentPadding: EdgeInsets.zero,
                            leading: CircleAvatar(radius: 12, child: Text('${i + 1}', style: const TextStyle(fontSize: 12))),
                            title: Text('${items[i]['title'] ?? 'Corto ${items[i]['shortfilm_id']}'}',
                                style: const TextStyle(fontSize: 13)),
                            trailing: items[i]['duration'] != null ? Text('${items[i]['duration']} min') : null,
                          ),
                      ],
                    ),
                  ),
                );
              },
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
