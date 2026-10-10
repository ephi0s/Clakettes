import 'package:hive/hive.dart';

part 'location_tag_model.g.dart';

/// Modelo de datos de una etiqueta propuesta o aprobada en una [Location].
///
/// Mapea entre el JSON snake_case del backend y los campos camelCase de Dart.
@HiveType(typeId: 23)
class LocationTag {
  @HiveField(0)
  final int? id;
  @HiveField(1)
  final int locationId;
  @HiveField(2)
  final String tag;
  /// Usuario que propuso la etiqueta.
  @HiveField(3)
  final int proposedBy;
  /// Estado de la etiqueta, p. ej. ``proposed``, ``approved`` o ``rejected``.
  @HiveField(4)
  final String status;
  @HiveField(5)
  final DateTime? createdAt;

  LocationTag({
    this.id,
    required this.locationId,
    required this.tag,
    required this.proposedBy,
    this.status = 'proposed',
    this.createdAt,
  });

  /// Crea un [LocationTag] a partir de un mapa JSON (claves snake_case del backend).
  factory LocationTag.fromJson(Map<String, dynamic> json) {
    return LocationTag(
      id: json['id'],
      locationId: json['location_id'],
      tag: json['tag'],
      proposedBy: json['proposed_by'],
      status: json['status'] ?? 'proposed',
      createdAt: json['created_at'] != null ? DateTime.parse(json['created_at']) : null,
    );
  }

  /// Serializa este [LocationTag] a un mapa JSON (claves snake_case).
  Map<String, dynamic> toJson() {
    return {
      'tag': tag,
    };
  }
}
