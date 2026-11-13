/// Modelo de datos del cribado de una obra dentro de una proyección.
///
/// Mapea entre el JSON snake_case del backend y los campos camelCase de Dart.
class ScreeningItem {
  final int shortfilmId;
  final int sortOrder;
  final String? title;
  final int? duration;
  /// Estado del cribado: `pending`, `screened` o `disqualified`.
  final String status;
  final String? statusReason;
  final bool isDisqualified;
  final String? juryNotes;
  final String? minutes;
  /// Anotación del jurado: `special_mention`, `accesit` u `other`.
  final String? annotation;
  final int? annotatedBy;
  final DateTime? annotatedAt;

  ScreeningItem({
    required this.shortfilmId,
    this.sortOrder = 0,
    this.title,
    this.duration,
    this.status = 'pending',
    this.statusReason,
    this.isDisqualified = false,
    this.juryNotes,
    this.minutes,
    this.annotation,
    this.annotatedBy,
    this.annotatedAt,
  });

  /// Crea un [ScreeningItem] a partir de un mapa JSON (claves snake_case).
  factory ScreeningItem.fromJson(Map<String, dynamic> json) {
    return ScreeningItem(
      shortfilmId: json['shortfilm_id'],
      sortOrder: json['sort_order'] ?? 0,
      title: json['title'],
      duration: json['duration'],
      status: json['status'] ?? 'pending',
      statusReason: json['status_reason'],
      isDisqualified: json['is_disqualified'] ?? false,
      juryNotes: json['jury_notes'],
      minutes: json['minutes'],
      annotation: json['annotation'],
      annotatedBy: json['annotated_by'],
      annotatedAt: json['annotated_at'] != null
          ? DateTime.parse(json['annotated_at'])
          : null,
    );
  }

  bool get isPending => status == 'pending';
  bool get isScreened => status == 'screened';
  bool get isDisqualifiedStatus =>
      status == 'disqualified' || isDisqualified;
}

/// Bloque de cribado completo de un evento de tipo proyección.
class EventScreenings {
  final int eventId;
  final List<int> shortfilmIds;
  final List<ScreeningItem> items;
  final int totalDuration;
  final Map<String, int> countsByStatus;

  EventScreenings({
    required this.eventId,
    this.shortfilmIds = const [],
    this.items = const [],
    this.totalDuration = 0,
    this.countsByStatus = const {},
  });

  /// Crea un [EventScreenings] a partir de un mapa JSON (claves snake_case).
  factory EventScreenings.fromJson(Map<String, dynamic> json) {
    return EventScreenings(
      eventId: json['event_id'],
      shortfilmIds: json['shortfilm_ids'] != null
          ? List<int>.from(json['shortfilm_ids'] as List)
          : const [],
      items: json['items'] != null
          ? (json['items'] as List)
              .map((j) => ScreeningItem.fromJson(Map<String, dynamic>.from(j)))
              .toList()
          : const [],
      totalDuration: json['total_duration'] ?? 0,
      countsByStatus: json['counts_by_status'] != null
          ? Map<String, int>.from(json['counts_by_status'] as Map)
          : const {},
    );
  }
}
