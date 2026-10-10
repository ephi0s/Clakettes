import 'package:hive/hive.dart';
import 'film_location_model.dart';

part 'shortfilm_model.g.dart';

/// Modelo de datos de un cortometraje presentado a un festival.
///
/// Mapea entre el JSON snake_case del backend y los campos camelCase de Dart.
@HiveType(typeId: 20)
class ShortFilm {
  @HiveField(0)
  final int? id;
  @HiveField(1)
  final String title;
  @HiveField(2)
  final String? description;
  /// Duración de la película en segundos.
  @HiveField(3)
  final int? duration;
  @HiveField(4)
  final String? videoUrl;
  @HiveField(5)
  final String? thumbnailUrl;
  @HiveField(6)
  final int? festivalId;
  @HiveField(7)
  final int userId;
  @HiveField(8)
  final bool isPublic;
  /// Lista de etiquetas separadas por comas, tal como la guarda el backend.
  @HiveField(9)
  final String? tags;
  @HiveField(10)
  final DateTime? createdAt;
  @HiveField(11)
  final DateTime? updatedAt;
  @HiveField(12)
  final List<FilmLocation> filmLocations;

  ShortFilm({
    this.id,
    required this.title,
    this.description,
    this.duration,
    this.videoUrl,
    this.thumbnailUrl,
    this.festivalId,
    required this.userId,
    this.isPublic = true,
    this.tags,
    this.createdAt,
    this.updatedAt,
    this.filmLocations = const [],
  });

  /// Crea un [ShortFilm] a partir de un mapa JSON (claves snake_case del backend).
  factory ShortFilm.fromJson(Map<String, dynamic> json) {
    return ShortFilm(
      id: json['id'],
      title: json['title'],
      description: json['description'],
      duration: json['duration'],
      videoUrl: json['video_url'],
      thumbnailUrl: json['thumbnail_url'],
      festivalId: json['festival_id'],
      userId: json['user_id'],
      isPublic: json['is_public'] ?? true,
      tags: json['tags'],
      createdAt: json['created_at'] != null ? DateTime.parse(json['created_at']) : null,
      updatedAt: json['updated_at'] != null ? DateTime.parse(json['updated_at']) : null,
      filmLocations: json['film_locations'] != null
          ? List<FilmLocation>.from(json['film_locations'].map((j) => FilmLocation.fromJson(j)))
          : [],
    );
  }

  /// Serializa este [ShortFilm] a un mapa JSON (claves snake_case).
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'description': description,
      'duration': duration,
      'video_url': videoUrl,
      'thumbnail_url': thumbnailUrl,
      'festival_id': festivalId,
      'user_id': userId,
      'is_public': isPublic,
      'tags': tags,
    };
  }
}
