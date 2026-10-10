import 'package:hive/hive.dart';

part 'location_image_model.g.dart';

/// Modelo de datos de una imagen adjunta a una [Location].
///
/// Mapea entre el JSON snake_case del backend y los campos camelCase de Dart.
@HiveType(typeId: 24)
class LocationImage {
  @HiveField(0)
  final int? id;
  @HiveField(1)
  final int locationId;
  @HiveField(2)
  final String url;
  /// Origen de la imagen, p. ej. ``upload``, ``url`` o ``film_frame``.
  @HiveField(3)
  final String source;
  @HiveField(4)
  final int addedBy;
  @HiveField(5)
  final DateTime? createdAt;

  LocationImage({
    this.id,
    required this.locationId,
    required this.url,
    this.source = 'upload',
    required this.addedBy,
    this.createdAt,
  });

  /// Crea un [LocationImage] a partir de un mapa JSON (claves snake_case del backend).
  factory LocationImage.fromJson(Map<String, dynamic> json) {
    return LocationImage(
      id: json['id'],
      locationId: json['location_id'],
      url: json['url'],
      source: json['source'] ?? 'upload',
      addedBy: json['added_by'],
      createdAt: json['created_at'] != null ? DateTime.parse(json['created_at']) : null,
    );
  }

  /// Serializa este [LocationImage] a un mapa JSON (claves snake_case).
  Map<String, dynamic> toJson() {
    return {
      'url': url,
    };
  }
}
