import 'package:hive/hive.dart';

part 'event_model.g.dart';

/// Modelo de datos de un evento del festival (proyección, gala, taller, ...).
///
/// Mapea entre el JSON snake_case del backend y los campos camelCase de Dart.
@HiveType(typeId: 5)
class FestivalEvent {
  @HiveField(0)
  final int? id;
  @HiveField(1)
  final int festivalId;
  @HiveField(2)
  final String title;
  @HiveField(3)
  final String? description;
  /// Tipo de evento, p. ej. ``screening``, ``gala`` o ``workshop``.
  @HiveField(4)
  final String? eventType;
  @HiveField(5)
  final DateTime? startDate;
  @HiveField(6)
  final DateTime? endDate;
  @HiveField(7)
  final String? location;
  @HiveField(8)
  final int? capacity;
  @HiveField(9)
  final bool isPublic;
  @HiveField(10)
  final bool isActive;
  @HiveField(11)
  final String? externalUrl;
  /// Notas internas visibles solo para el personal.
  @HiveField(12)
  final String? internalNotes;
  /// Código de color hexadecimal usado para mostrar el evento en los calendarios.
  @HiveField(13)
  final String? colorCode;
  /// Indica si el evento dispone de un mapa de asientos interactivo.
  @HiveField(14)
  final bool showSeatMap;
  @HiveField(15)
  final String? venue;
  @HiveField(16)
  final double? venueLatitude;
  @HiveField(17)
  final double? venueLongitude;
  /// Alcance de visibilidad del evento en la agenda compartida.
  ///
  /// Valores: ``public``, ``festival_members``, ``roles``, ``attendees_only``.
  @HiveField(18)
  final String visibilityScope;
  /// Ids de los roles del festival que pueden ver el evento
  /// (solo tiene efecto cuando [visibilityScope] es ``roles``).
  @HiveField(19)
  final List<int> visibleRoleIds;

  /// Cortometrajes proyectados (solo `eventType == screening`).
  final List<int> screeningShortfilmIds;

  FestivalEvent({
    this.id,
    required this.festivalId,
    required this.title,
    this.description,
    this.eventType,
    this.startDate,
    this.endDate,
    this.location,
    this.capacity,
    this.isPublic = true,
    this.isActive = true,
    this.externalUrl,
    this.internalNotes,
    this.colorCode,
    this.showSeatMap = false,
    this.venue,
    this.venueLatitude,
    this.venueLongitude,
    this.visibilityScope = 'public',
    this.visibleRoleIds = const [],
    this.screeningShortfilmIds = const [],
  });

  /// Crea un [FestivalEvent] a partir de un mapa JSON (claves snake_case del backend).
  factory FestivalEvent.fromJson(Map<String, dynamic> json) {
    return FestivalEvent(
      id: json['id'],
      festivalId: json['festival_id'],
      title: json['title'],
      description: json['description'],
      eventType: json['event_type'],
      startDate: json['start_date'] != null ? DateTime.parse(json['start_date']) : null,
      endDate: json['end_date'] != null ? DateTime.parse(json['end_date']) : null,
      location: json['location'],
      capacity: json['capacity'],
      isPublic: json['is_public'] ?? true,
      isActive: json['is_active'] ?? true,
      externalUrl: json['external_url'],
      internalNotes: json['internal_notes'],
      colorCode: json['color_code'] ?? json['color'],
      showSeatMap: json['show_seat_map'] ?? false,
      venue: json['venue'],
      venueLatitude: (json['venue_latitude'] as num?)?.toDouble(),
      venueLongitude: (json['venue_longitude'] as num?)?.toDouble(),
      visibilityScope: json['visibility_scope'] ?? 'public',
      visibleRoleIds: json['visible_role_ids'] != null
          ? List<int>.from(json['visible_role_ids'] as List)
          : const [],
      screeningShortfilmIds: json['screening_shortfilm_ids'] != null
          ? List<int>.from(json['screening_shortfilm_ids'] as List)
          : const [],
    );
  }

  /// Serializa este [FestivalEvent] a un mapa JSON (claves snake_case).
  Map<String, dynamic> toJson() => {
    'festival_id': festivalId,
    'title': title,
    'description': description,
    'event_type': eventType,
    'start_date': startDate?.toIso8601String(),
    'end_date': endDate?.toIso8601String(),
    'location': location,
    'capacity': capacity,
    'is_public': isPublic,
    'is_active': isActive,
    'external_url': externalUrl,
    'internal_notes': internalNotes,
    'color_code': colorCode,
    'show_seat_map': showSeatMap,
    'venue': venue,
    'venue_latitude': venueLatitude,
    'venue_longitude': venueLongitude,
    'visibility_scope': visibilityScope,
    'visible_role_ids': visibleRoleIds,
    'screening_shortfilm_ids': screeningShortfilmIds,
  };

  /// Indica si el evento solo es visible para una audiencia restringida.
  bool get isRestricted => visibilityScope != 'public';
}


/// Modelo de datos de un tipo de entrada disponible para un [FestivalEvent].
///
/// Mapea entre el JSON snake_case del backend y los campos camelCase de Dart.
@HiveType(typeId: 6)
class EventTicketType {
  @HiveField(0)
  final int? id;
  @HiveField(1)
  final int eventId;
  @HiveField(2)
  final String name;
  @HiveField(3)
  final double? price;
  @HiveField(4)
  final int? capacity;
  /// Número máximo de entradas de este tipo por usuario.
  @HiveField(5)
  final int? maxPerUser;
  @HiveField(6)
  final String? description;
  @HiveField(7)
  final bool isActive;
  /// Código de color hexadecimal usado para mostrar el tipo de entrada en el mapa de asientos.
  @HiveField(8)
  final String? colorCode;

  EventTicketType({
    this.id,
    required this.eventId,
    required this.name,
    this.price,
    this.capacity,
    this.maxPerUser,
    this.description,
    this.isActive = true,
    this.colorCode,
  });

  /// Crea un [EventTicketType] a partir de un mapa JSON (claves snake_case del backend).
  factory EventTicketType.fromJson(Map<String, dynamic> json) {
    return EventTicketType(
      id: json['id'],
      eventId: json['event_id'],
      name: json['name'],
      price: (json['price'] as num?)?.toDouble(),
      capacity: json['capacity'],
      maxPerUser: json['max_per_user'],
      description: json['description'],
      isActive: json['is_active'] ?? true,
      colorCode: json['color_code'],
    );
  }

  /// Serializa este [EventTicketType] a un mapa JSON (claves snake_case).
  Map<String, dynamic> toJson() => {
    'event_id': eventId,
    'name': name,
    'price': price,
    'capacity': capacity,
    'max_per_user': maxPerUser,
    'description': description,
    'is_active': isActive,
    'color_code': colorCode,
  };
}


/// Modelo de datos de un asiento individual dentro del mapa de asientos de un evento.
///
/// Mapea entre el JSON snake_case del backend y los campos camelCase de Dart.
@HiveType(typeId: 7)
class EventSeat {
  @HiveField(0)
  final int? id;
  @HiveField(1)
  final int eventId;
  @HiveField(2)
  final int? ticketTypeId;
  @HiveField(3)
  final String section;
  @HiveField(4)
  final String? rowLabel;
  @HiveField(5)
  final int? number;
  /// Disponibilidad del asiento, p. ej. ``available``, ``reserved`` u ``occupied``.
  @HiveField(6)
  final String status;
  /// Posición horizontal normalizada (0-1) en el mapa de asientos.
  @HiveField(7)
  final double? x;
  /// Posición vertical normalizada (0-1) en el mapa de asientos.
  @HiveField(8)
  final double? y;
  /// Indica si el asiento está adaptado para movilidad reducida.
  @HiveField(9)
  final bool isAccessible;

  EventSeat({
    this.id,
    required this.eventId,
    this.ticketTypeId,
    required this.section,
    this.rowLabel,
    this.number,
    this.status = 'available',
    this.x,
    this.y,
    this.isAccessible = false,
  });

  /// Crea un [EventSeat] a partir de un mapa JSON (claves snake_case del backend).
  factory EventSeat.fromJson(Map<String, dynamic> json) {
    return EventSeat(
      id: json['id'],
      eventId: json['event_id'],
      ticketTypeId: json['ticket_type_id'],
      section: json['section'],
      rowLabel: json['row_label'],
      number: json['number'],
      status: json['status'] ?? 'available',
      x: (json['x'] as num?)?.toDouble(),
      y: (json['y'] as num?)?.toDouble(),
      isAccessible: json['is_accessible'] ?? false,
    );
  }

  /// Serializa este [EventSeat] a un mapa JSON (claves snake_case).
  Map<String, dynamic> toJson() => {
    'event_id': eventId,
    'ticket_type_id': ticketTypeId,
    'section': section,
    'row_label': rowLabel,
    'number': number,
    'status': status,
    'x': x,
    'y': y,
    'is_accessible': isAccessible,
  };
}

/// Modelo de datos de un asistente a un evento (usuario registrado o invitado).
///
/// Mapea entre el JSON snake_case del backend y los campos camelCase de Dart.
class EventAttendee {
  final int? id;
  final int? userId;
  final int? seatId;
  /// Estado de asistencia, p. ej. ``registered``, ``checked_in`` o ``cancelled``.
  final String status;
  /// Indica si el asistente es un invitado externo en lugar de un usuario registrado.
  final bool isGuest;
  final String? guestName;
  final DateTime? checkedInAt;

  EventAttendee({
    this.id,
    this.userId,
    this.seatId,
    this.status = 'registered',
    this.isGuest = false,
    this.guestName,
    this.checkedInAt,
  });

  /// Crea un [EventAttendee] a partir de un mapa JSON (claves snake_case del backend).
  factory EventAttendee.fromJson(Map<String, dynamic> json) {
    return EventAttendee(
      id: json['id'],
      userId: json['user_id'],
      seatId: json['seat_id'],
      status: json['status'] ?? 'registered',
      isGuest: json['is_guest'] ?? false,
      guestName: json['guest_name'],
      checkedInAt: json['checked_in_at'] != null ? DateTime.parse(json['checked_in_at']) : null,
    );
  }
}

/// Modelo de datos de una reserva de entradas de un evento y sus asistentes.
///
/// Mapea entre el JSON snake_case del backend y los campos camelCase de Dart.
@HiveType(typeId: 8)
class EventReservation {
  @HiveField(0)
  final int? id;
  @HiveField(1)
  final int eventId;
  @HiveField(2)
  final int? userId;
  /// Estado de la reserva, p. ej. ``pending``, ``confirmed`` o ``cancelled``.
  @HiveField(3)
  final String status;
  @HiveField(4)
  final int totalQuantity;
  @HiveField(5)
  final String? notes;
  @HiveField(6)
  final int? createdBy;
  @HiveField(7)
  final DateTime? confirmedAt;
  @HiveField(8)
  final DateTime? cancelledAt;
  @HiveField(9)
  final List<EventAttendee>? attendees;

  EventReservation({
    this.id,
    required this.eventId,
    this.userId,
    this.status = 'pending',
    this.totalQuantity = 1,
    this.notes,
    this.createdBy,
    this.confirmedAt,
    this.cancelledAt,
    this.attendees,
  });

  /// Crea un [EventReservation] a partir de un mapa JSON (claves snake_case del backend).
  factory EventReservation.fromJson(Map<String, dynamic> json) {
    return EventReservation(
      id: json['id'],
      eventId: json['event_id'],
      userId: json['user_id'],
      status: json['status'] ?? 'pending',
      totalQuantity: json['total_quantity'] ?? 1,
      notes: json['notes'],
      createdBy: json['created_by'],
      confirmedAt: json['confirmed_at'] != null ? DateTime.parse(json['confirmed_at']) : null,
      cancelledAt: json['cancelled_at'] != null ? DateTime.parse(json['cancelled_at']) : null,
      attendees: json['attendees'] != null
          ? (json['attendees'] as List).map((a) => EventAttendee.fromJson(a)).toList()
          : null,
    );
  }

  /// Serializa este [EventReservation] a un mapa JSON (claves snake_case).
  Map<String, dynamic> toJson() => {
    'event_id': eventId,
    'user_id': userId,
    'status': status,
    'total_quantity': totalQuantity,
    'notes': notes,
  };
}
