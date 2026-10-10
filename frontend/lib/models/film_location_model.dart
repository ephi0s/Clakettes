import 'package:hive/hive.dart';

part 'film_location_model.g.dart';

/// Modelo de datos del vínculo entre un cortometraje y una localización de rodaje.
///
/// Mapea entre el JSON snake_case del backend y los campos camelCase de Dart.
@HiveType(typeId: 27)
class FilmLocation {
  @HiveField(0)
  final int? id;
  @HiveField(1)
  final int shortfilmId;
  @HiveField(2)
  final int locationId;
  /// Rol de la localización en la película, p. ej. ``primary`` o ``secondary``.
  @HiveField(3)
  final String role;
  /// Hora de inicio de la escena, expresada en minutos.
  @HiveField(4)
  final double? startTime;
  /// Hora de fin de la escena, expresada en minutos.
  @HiveField(5)
  final double? endTime;
  @HiveField(6)
  final String? notes;
  @HiveField(7)
  final int createdBy;
  @HiveField(8)
  final DateTime? createdAt;

  FilmLocation({
    this.id,
    required this.shortfilmId,
    required this.locationId,
    this.role = 'primary',
    this.startTime,
    this.endTime,
    this.notes,
    required this.createdBy,
    this.createdAt,
  });

  /// Crea un [FilmLocation] a partir de un mapa JSON (claves snake_case del backend).
  factory FilmLocation.fromJson(Map<String, dynamic> json) {
    return FilmLocation(
      id: json['id'],
      shortfilmId: json['shortfilm_id'],
      locationId: json['location_id'],
      role: json['role'] ?? 'primary',
      startTime: json['start_time']?.toDouble(),
      endTime: json['end_time']?.toDouble(),
      notes: json['notes'],
      createdBy: json['created_by'],
      createdAt: json['created_at'] != null ? DateTime.parse(json['created_at']) : null,
    );
  }

  /// Serializa este [FilmLocation] a un mapa JSON (claves snake_case).
  Map<String, dynamic> toJson() {
    return {
      'location_id': locationId,
      'role': role,
      if (startTime != null) 'start_time': startTime,
      if (endTime != null) 'end_time': endTime,
      if (notes != null) 'notes': notes,
    };
  }
}
