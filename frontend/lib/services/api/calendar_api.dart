part of '../api_service.dart';

/// Cliente de la agenda compartida (`/api/calendar`).
///
/// [getAgenda] es público: sin token devuelve solo los eventos públicos de los
/// portables; con token incluye además los dirigidos al usuario.
extension CalendarApi on ApiService {
  /// Descarga la agenda visible para el usuario actual (o para el público).
  ///
  /// [from] y [to] acotan el rango; [festivalIds] acota a ciertos festivales.
  Future<Agenda> getAgenda({
    DateTime? from,
    DateTime? to,
    List<int>? festivalIds,
    String? eventType,
    int limit = 200,
  }) async {
    final params = <String, String>{'limit': '$limit'};
    if (from != null) params['date_from'] = from.toIso8601String();
    if (to != null) params['date_to'] = to.toIso8601String();
    if (eventType != null) params['event_type'] = eventType;
    var path = '/calendar/agenda';
    final query = _buildQuery(params);
    if (query.isNotEmpty) path = '$path?$query';
    if (festivalIds != null && festivalIds.isNotEmpty) {
      final repeated =
          festivalIds.map((i) => 'festival_ids=$i').join('&');
      path = query.isEmpty ? '$path?$repeated' : '$path&$repeated';
    }
    final data = await request('GET', path);
    return Agenda.fromJson(Map<String, dynamic>.from(data as Map));
  }

  /// Descarga la agenda como archivo ICS.
  Future<Uint8List> getAgendaIcs({DateTime? from, DateTime? to}) async {
    final params = <String, String>{};
    if (from != null) params['date_from'] = from.toIso8601String();
    if (to != null) params['date_to'] = to.toIso8601String();
    return getBytes(
        '/calendar/agenda/export/ics', params.isEmpty ? null : params);
  }

  /// Consulta el interruptor global de la agenda. No requiere autenticación.
  Future<bool> isCalendarEnabled() async {
    final data = await _get('/calendar/settings');
    return (data as Map)['calendar_enabled'] as bool? ?? true;
  }

  /// Obtiene la configuración completa del calendario. Solo administradores.
  Future<CalendarSettings> getCalendarSettings() async {
    final data = await _get('/calendar/admin/settings');
    return CalendarSettings.fromJson(Map<String, dynamic>.from(data as Map));
  }

  /// Guarda los ajustes del calendario. Solo administradores.
  ///
  /// Los campos omitidos se conservan: pasar `null` en [festivalIds] deja los
  /// interruptores por festival tal como están.
  Future<CalendarSettings> updateCalendarSettings({
    bool? calendarEnabled,
    List<int>? festivalIds,
  }) async {
    final body = <String, dynamic>{};
    if (calendarEnabled != null) body['calendar_enabled'] = calendarEnabled;
    if (festivalIds != null) body['festival_ids'] = festivalIds;
    final data = await _put('/calendar/admin/settings', body);
    return CalendarSettings.fromJson(Map<String, dynamic>.from(data as Map));
  }

  // ---------------------------------------------------------------------------
  // Suscripción CalDAV
  // ---------------------------------------------------------------------------

  /// Consulta si el usuario tiene un token DAV activo y qué colecciones expone.
  ///
  /// Nunca devuelve el token: solo indica si existe.
  Future<DavTokenStatus> getDavTokenStatus() async {
    final data = await _get('/calendar/dav/token');
    return DavTokenStatus.fromJson(Map<String, dynamic>.from(data as Map));
  }

  /// Genera (o regenera) el token DAV del usuario.
  ///
  /// El token devuelto en [DavToken.token] es la única copia que verá el
  /// usuario; el backend solo guarda su hash.
  Future<DavToken> createDavToken() async {
    final data = await request('POST', '/calendar/dav/token');
    return DavToken.fromJson(Map<String, dynamic>.from(data as Map));
  }

  /// Revoca el token DAV, rompiendo todas las suscripciones que lo usen.
  Future<DavTokenStatus> revokeDavToken() async {
    final data = await request('DELETE', '/calendar/dav/token');
    return DavTokenStatus.fromJson(Map<String, dynamic>.from(data as Map));
  }
}
