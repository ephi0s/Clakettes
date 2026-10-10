/// Bases de un festival (sección oficial, concursos y actividades).
///
/// Mapea entre el JSON snake_case del backend y los campos camelCase de Dart.
class FestivalRulebook {
  final int? id;
  final int festivalId;
  final int? eventId;
  final String title;
  final String? description;
  final String category;
  final String? fileUrl;
  final String? externalUrl;
  final bool isPublished;

  const FestivalRulebook({
    this.id,
    required this.festivalId,
    this.eventId,
    required this.title,
    this.description,
    this.category = 'official_section',
    this.fileUrl,
    this.externalUrl,
    this.isPublished = true,
  });

  static const List<String> categories = [
    'official_section',
    'contest',
    'activity',
    'other',
  ];

  factory FestivalRulebook.fromJson(Map<String, dynamic> json) {
    return FestivalRulebook(
      id: json['id'],
      festivalId: json['festival_id'],
      eventId: json['event_id'],
      title: json['title'] ?? '',
      description: json['description'],
      category: json['category'] ?? 'official_section',
      fileUrl: json['file_url'],
      externalUrl: json['external_url'],
      isPublished: json['is_published'] ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'title': title,
      'description': description,
      'category': category,
      'event_id': eventId,
      'file_url': fileUrl,
      'external_url': externalUrl,
      'is_published': isPublished,
    };
  }

  String get documentUrl => fileUrl ?? externalUrl ?? '';
  bool get hasDocument => fileUrl != null || externalUrl != null;
}
