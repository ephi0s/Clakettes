// Modelos de la agenda compartida (`/api/calendar`).
//
// Son estructuras de solo lectura que siempre llegan anidadas dentro de
// [Agenda] o [CalendarSettings], por lo que no se guardan en Hive (igual que
// `EventAttendee` en `event_model.dart`).

/// Niveles de visibilidad de un evento, en el orden en que se muestran al
/// administrador del festival.
enum EventVisibilityScope {
  /// Visible para cualquiera, sin iniciar sesión.
  public('public'),

  /// Visible solo para los miembros del festival.
  festivalMembers('festival_members'),

  /// Visible solo para quienes tengan alguno de los roles seleccionados.
  roles('roles'),

  /// Visible solo para las personas inscritas al evento.
  attendeesOnly('attendees_only');

  const EventVisibilityScope(this.value);

  /// Valor exchanged con el backend.
  final String value;

  /// Convierte el valor del backend en el enumerado, con [public] como respaldo.
  static EventVisibilityScope fromValue(String? value) {
    return EventVisibilityScope.values.firstWhere(
      (scope) => scope.value == value,
      orElse: () => EventVisibilityScope.public,
    );
  }

  /// Etiqueta legible; la traducción se aplica en la capa de widgets.
  String get labelKey => switch (this) {
        EventVisibilityScope.public => 'visibilityPublic',
        EventVisibilityScope.festivalMembers => 'visibilityFestivalMembers',
        EventVisibilityScope.roles => 'visibilityRoles',
        EventVisibilityScope.attendeesOnly => 'visibilityAttendeesOnly',
      };
}

/// Un evento de la agenda, enriquecido con el nombre de su festival.
class AgendaEvent {
  final int id;
  final int festivalId;
  final String festivalName;
  final String title;
  final String? description;
  final String? shortDescription;
  final String eventType;
  final DateTime startDate;
  final DateTime? endDate;
  final String? location;
  final String? venue;
  final String? imageUrl;
  final String? color;
  final int? capacity;
  final EventVisibilityScope visibilityScope;

  /// `true` cuando el evento solo se muestra a una audiencia restringida.
  final bool isPrivate;

  const AgendaEvent({
    required this.id,
    required this.festivalId,
    required this.festivalName,
    required this.title,
    required this.eventType,
    required this.startDate,
    this.description,
    this.shortDescription,
    this.endDate,
    this.location,
    this.venue,
    this.imageUrl,
    this.color,
    this.capacity,
    this.visibilityScope = EventVisibilityScope.public,
    this.isPrivate = false,
  });

  factory AgendaEvent.fromJson(Map<String, dynamic> json) {
    return AgendaEvent(
      id: json['id'] as int,
      festivalId: json['festival_id'] as int,
      festivalName: json['festival_name'] as String? ?? '',
      title: json['title'] as String,
      description: json['description'],
      shortDescription: json['short_description'],
      eventType: json['event_type'] as String? ?? 'other',
      startDate: DateTime.parse(json['start_date'] as String),
      endDate: json['end_date'] != null ? DateTime.parse(json['end_date'] as String) : null,
      location: json['location'],
      venue: json['venue'],
      imageUrl: json['image_url'],
      color: json['color'],
      capacity: json['capacity'],
      visibilityScope: EventVisibilityScope.fromValue(json['visibility_scope'] as String?),
      isPrivate: json['is_private'] ?? false,
    );
  }

  /// Devuelve `true` si el evento ocupa algún día entre [from] y [to] (ambos inclusive).
  bool spansDay(DateTime day) {
    final start = DateTime(startDate.year, startDate.month, startDate.day);
    final end = endDate == null
        ? start
        : DateTime(endDate!.year, endDate!.month, endDate!.day);
    final target = DateTime(day.year, day.month, day.day);
    return !target.isBefore(start) && !target.isAfter(end);
  }
}

/// Un festival que aporta eventos a la agenda.
class AgendaFestival {
  final int id;
  final String name;
  final String? logoUrl;
  final String? location;
  final int eventCount;

  const AgendaFestival({
    required this.id,
    required this.name,
    this.logoUrl,
    this.location,
    this.eventCount = 0,
  });

  factory AgendaFestival.fromJson(Map<String, dynamic> json) {
    return AgendaFestival(
      id: json['id'] as int,
      name: json['name'] as String,
      logoUrl: json['logo_url'],
      location: json['location'],
      eventCount: json['event_count'] ?? 0,
    );
  }
}

/// Respuesta de `GET /api/calendar/agenda`.
class Agenda {
  /// `false` cuando el administrador general ha desactivado la agenda.
  final bool enabled;
  final List<AgendaFestival> festivals;
  final List<AgendaEvent> events;

  const Agenda({
    this.enabled = true,
    this.festivals = const [],
    this.events = const [],
  });

  factory Agenda.fromJson(Map<String, dynamic> json) {
    return Agenda(
      enabled: json['enabled'] ?? true,
      festivals: (json['festivals'] as List? ?? [])
          .map((j) => AgendaFestival.fromJson(Map<String, dynamic>.from(j)))
          .toList(),
      events: (json['events'] as List? ?? [])
          .map((j) => AgendaEvent.fromJson(Map<String, dynamic>.from(j)))
          .toList(),
    );
  }

  /// Agrupa los eventos por día (día a medianoche) conservando el orden de llegada.
  Map<DateTime, List<AgendaEvent>> get eventsByDay {
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
}

/// Configuración de inclusión de un festival en la agenda (vista de admin).
class CalendarFestivalVisibility {
  final int id;
  final String name;
  final String? logoUrl;
  final String? location;
  final bool isActive;

  /// Si el admin general incluye los eventos de este festival en la agenda.
  final bool showInCalendar;
  final int eventCount;

  const CalendarFestivalVisibility({
    required this.id,
    required this.name,
    this.logoUrl,
    this.location,
    this.isActive = true,
    this.showInCalendar = true,
    this.eventCount = 0,
  });

  factory CalendarFestivalVisibility.fromJson(Map<String, dynamic> json) {
    return CalendarFestivalVisibility(
      id: json['id'] as int,
      name: json['name'] as String,
      logoUrl: json['logo_url'],
      location: json['location'],
      isActive: json['is_active'] ?? true,
      showInCalendar: json['show_in_calendar'] ?? true,
      eventCount: json['event_count'] ?? 0,
    );
  }

  CalendarFestivalVisibility copyWith({bool? showInCalendar}) {
    return CalendarFestivalVisibility(
      id: id,
      name: name,
      logoUrl: logoUrl,
      location: location,
      isActive: isActive,
      showInCalendar: showInCalendar ?? this.showInCalendar,
      eventCount: eventCount,
    );
  }
}

/// Configuración completa del calendario. Solo para administradores.
class CalendarSettings {
  /// Interruptor global de la agenda compartida.
  final bool calendarEnabled;
  final List<CalendarFestivalVisibility> festivals;

  const CalendarSettings({
    this.calendarEnabled = true,
    this.festivals = const [],
  });

  factory CalendarSettings.fromJson(Map<String, dynamic> json) {
    return CalendarSettings(
      calendarEnabled: json['calendar_enabled'] ?? true,
      festivals: (json['festivals'] as List? ?? [])
          .map((j) => CalendarFestivalVisibility.fromJson(Map<String, dynamic>.from(j)))
          .toList(),
    );
  }

  /// Ids de los festivales visibles actualmente en la agenda.
  List<int> get visibleFestivalIds =>
      festivals.where((f) => f.showInCalendar).map((f) => f.id).toList();

  CalendarSettings copyWith({
    bool? calendarEnabled,
    List<CalendarFestivalVisibility>? festivals,
  }) {
    return CalendarSettings(
      calendarEnabled: calendarEnabled ?? this.calendarEnabled,
      festivals: festivals ?? this.festivals,
    );
  }
}

/// Una colección CalDAV a la que el usuario puede suscribirse.
///
/// [name] es el identificador que usa el backend en las rutas (`agenda` para la
/// agenda global, `festival-<id>` para la de un festival).
class DavCollection {
  final String name;
  final String displayName;
  final String? description;

  const DavCollection({
    required this.name,
    required this.displayName,
    this.description,
  });

  factory DavCollection.fromJson(Map<String, dynamic> json) {
    return DavCollection(
      name: json['name'] as String,
      displayName: json['display_name'] as String? ?? '',
      description: json['description'],
    );
  }

  DavCollection copyWith({String? displayName, String? description}) {
    return DavCollection(
      name: name,
      displayName: displayName ?? this.displayName,
      description: description ?? this.description,
    );
  }
}

/// Estado del token DAV. Nunca contiene el token: se muestra una sola vez al generarlo.
class DavTokenStatus {
  final bool hasToken;
  final List<DavCollection> collections;

  const DavTokenStatus({
    this.hasToken = false,
    this.collections = const [],
  });

  factory DavTokenStatus.fromJson(Map<String, dynamic> json) {
    return DavTokenStatus(
      hasToken: json['has_token'] ?? false,
      collections: (json['collections'] as List? ?? [])
          .map((j) => DavCollection.fromJson(Map<String, dynamic>.from(j)))
          .toList(),
    );
  }

  DavTokenStatus copyWith({bool? hasToken, List<DavCollection>? collections}) {
    return DavTokenStatus(
      hasToken: hasToken ?? this.hasToken,
      collections: collections ?? this.collections,
    );
  }
}

/// Token recién generado. [token] solo está disponible en esta respuesta.
class DavToken {
  final String token;
  final List<DavCollection> collections;

  const DavToken({
    required this.token,
    this.collections = const [],
  });

  factory DavToken.fromJson(Map<String, dynamic> json) {
    return DavToken(
      token: json['token'] as String? ?? '',
      collections: (json['collections'] as List? ?? [])
          .map((j) => DavCollection.fromJson(Map<String, dynamic>.from(j)))
          .toList(),
    );
  }

  DavToken copyWith({String? token, List<DavCollection>? collections}) {
    return DavToken(
      token: token ?? this.token,
      collections: collections ?? this.collections,
    );
  }
}
