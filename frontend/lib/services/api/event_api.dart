part of '../api_service.dart';

/// Llamadas de event_.
extension EventApi on ApiService {
  /// Obtiene los eventos paginados de un festival, con filtro opcional de tipo.
  Future<PaginatedResult<FestivalEvent>> getEvents(int festivalId,
      {int page = 1, int size = 20, String? eventType}) async {
    final params = <String, String>{'page': '$page', 'size': '$size'};
    if (eventType != null) params['event_type'] = eventType;
    final data = await _get('/festivals/$festivalId/events/', params);
    return _paginated(data, FestivalEvent.fromJson);
  }

  /// Crea un evento en un festival y devuelve el [FestivalEvent] creado.
  Future<FestivalEvent> createEvent(int festivalId, FestivalEvent e) async {
    final data = await create('/festivals/$festivalId/events/', e.toJson());
    return FestivalEvent.fromJson(data);
  }

  /// Obtiene los eventos en los que el usuario actual está registrado (lista plana).
  Future<List<FestivalEvent>> getMyEvents() async {
    final data = await request('GET', '/users/me/events/');
    return (data as List).map((j) => FestivalEvent.fromJson(j)).toList();
  }

  /// Obtiene un evento por su id.
  Future<FestivalEvent> getEvent(int eventId) async {
    final data = await request('GET', '/events/$eventId');
    return FestivalEvent.fromJson(data);
  }

  /// Actualiza los campos indicados de un evento.
  Future<FestivalEvent> updateEvent(
      int eventId, Map<String, dynamic> fields) async {
    final data = await _put('/events/$eventId', fields);
    return FestivalEvent.fromJson(data);
  }

  /// Elimina un evento por su id.
  Future<void> deleteEvent(int eventId) async {
    await request('DELETE', '/events/$eventId');
  }

  Future<PaginatedResult<FestivalEvent>> getProgramacion(int festivalId,
      {int page = 1, int size = 50, String? venue}) async {
    final params = <String, String>{'page': '$page', 'size': '$size'};
    if (venue != null && venue.isNotEmpty) params['venue'] = venue;
    final data =
        await _get('/festivals/$festivalId/events/programacion', params);
    return _paginated(data, FestivalEvent.fromJson);
  }

  Future<Map<String, dynamic>> checkEventConflict(int festivalId,
      {required String venue,
      required DateTime start,
      DateTime? end,
      int? excludeEventId}) async {
    final params = <String, String>{
      'venue': venue,
      'start_date': start.toIso8601String()
    };
    if (end != null) params['end_date'] = end.toIso8601String();
    if (excludeEventId != null) params['exclude_event_id'] = '$excludeEventId';
    return Map<String, dynamic>.from(
        await _get('/festivals/$festivalId/events/check-conflict', params)
            as Map);
  }

  Future<List<int>> getEventScreenings(int eventId) async {
    final data = await request('GET', '/events/$eventId/screenings');
    return List<int>.from((data as Map)['shortfilm_ids'] as List? ?? []);
  }

  Future<Map<String, dynamic>> getEventScreeningBlock(int eventId) async {
    return Map<String, dynamic>.from(
        await request('GET', '/events/$eventId/screenings') as Map);
  }

  Future<List<int>> setEventScreenings(
      int eventId, List<int> shortfilmIds) async {
    final data = await request('PUT', '/events/$eventId/screenings',
        body: {'shortfilm_ids': shortfilmIds});
    return List<int>.from((data as Map)['shortfilm_ids'] as List? ?? []);
  }

  Future<Map<String, dynamic>> getEventOccupancy(int eventId) async {
    return Map<String, dynamic>.from(
        await request('GET', '/events/$eventId/occupancy') as Map);
  }

  Future<Payment> createPaymentCheckout(
      {int? registrationId,
      int? eventId,
      double? amount,
      String currency = 'EUR'}) async {
    final body = <String, dynamic>{'currency': currency};
    if (registrationId != null) body['registration_id'] = registrationId;
    if (eventId != null) body['event_id'] = eventId;
    if (amount != null) body['amount'] = amount;
    final data = await create('/payments/checkout', body);
    return Payment.fromJson(data);
  }

  Future<PaginatedResult<Payment>> getPayments(
      {int page = 1, int size = 20, String? status}) async {
    final params = <String, String>{'page': '$page', 'size': '$size'};
    if (status != null) params['status'] = status;
    final data = await _get('/payments/', params);
    return _paginated(data, Payment.fromJson);
  }

  Future<Payment> confirmPayment(int paymentId) async {
    final data = await request('POST', '/payments/$paymentId/confirm');
    return Payment.fromJson(Map<String, dynamic>.from(data as Map));
  }

  Future<Payment> refundPayment(int paymentId) async {
    final data = await request('POST', '/payments/$paymentId/refund');
    return Payment.fromJson(Map<String, dynamic>.from(data as Map));
  }

  /// Obtiene los tipos de entrada de un evento.
  Future<List<EventTicketType>> getEventTicketTypes(int eventId) async {
    final data = await request('GET', '/events/$eventId/ticket-types/');
    return (data['items'] as List)
        .map((j) => EventTicketType.fromJson(j))
        .toList();
  }

  /// Crea un tipo de entrada para un evento.
  Future<EventTicketType> createEventTicketType(
      int eventId, EventTicketType t) async {
    final data = await create('/events/$eventId/ticket-types/', t.toJson());
    return EventTicketType.fromJson(data);
  }

  /// Elimina un tipo de entrada.
  Future<void> deleteEventTicketType(int ticketTypeId) async {
    await request('DELETE', '/ticket-types/$ticketTypeId');
  }

  /// Obtiene los asientos paginados de un evento, con filtro opcional de sección.
  Future<PaginatedResult<EventSeat>> getSeats(int eventId,
      {int page = 1, int size = 100, String? section}) async {
    final params = <String, String>{'page': '$page', 'size': '$size'};
    if (section != null) params['section'] = section;
    final data = await _get('/events/$eventId/seats/', params);
    return _paginated(data, EventSeat.fromJson);
  }

  /// Crea asientos en bloque para un evento y devuelve los [EventSeat] creados.
  Future<List<EventSeat>> bulkCreateSeats(
      int eventId, Map<String, dynamic> config) async {
    final data = await create('/events/$eventId/seats/bulk', config);
    return (data as List).map((j) => EventSeat.fromJson(j)).toList();
  }

  /// Obtiene las secciones de asientos de un evento.
  Future<List<String>> getSeatSections(int eventId) async {
    final data = await request('GET', '/events/$eventId/seats/sections');
    return (data as List).cast<String>();
  }

  /// Obtiene el recuento de asientos por estado de un evento.
  Future<Map<String, dynamic>> getSeatCounts(int eventId) async {
    return await request('GET', '/events/$eventId/seats/counts');
  }

  /// Actualiza los campos indicados de un asiento.
  Future<EventSeat> updateSeat(int seatId, Map<String, dynamic> fields) async {
    final data = await _put('/seats/$seatId', fields);
    return EventSeat.fromJson(data);
  }

  /// Libera un asiento reservado.
  Future<void> releaseSeat(int seatId) async {
    await request('POST', '/seats/$seatId/release');
  }

  /// Elimina un asiento.
  Future<void> deleteSeat(int seatId) async {
    await request('DELETE', '/seats/$seatId');
  }

  /// Obtiene la reserva del usuario actual para un evento, o `null` si no existe.
  Future<EventReservation?> getMyReservation(int eventId) async {
    try {
      final data =
          await request('GET', '/users/me/events/$eventId/reservation');
      return EventReservation.fromJson(data);
    } catch (e) {
      debugPrint('Error: $e');
      return null;
    }
  }

  /// Obtiene las reservas paginadas de un evento, con filtro opcional de estado.
  Future<PaginatedResult<EventReservation>> getEventReservations(int eventId,
      {int page = 1, int size = 20, String? status}) async {
    final params = <String, String>{'page': '$page', 'size': '$size'};
    if (status != null) params['status'] = status;
    final data = await _get('/events/$eventId/reservations/', params);
    return _paginated(data, EventReservation.fromJson);
  }

  /// Crea una reserva para un evento.
  Future<EventReservation> createReservation(
      int eventId, Map<String, dynamic> body) async {
    final data = await create('/events/$eventId/reservations/', body);
    return EventReservation.fromJson(data);
  }

  /// Confirma una reserva.
  Future<EventReservation> confirmReservation(int reservationId) async {
    final data = await request('POST', '/reservations/$reservationId/confirm');
    return EventReservation.fromJson(data);
  }

  /// Cancela una reserva.
  Future<EventReservation> cancelReservation(int reservationId) async {
    final data = await request('POST', '/reservations/$reservationId/cancel');
    return EventReservation.fromJson(data);
  }
}
