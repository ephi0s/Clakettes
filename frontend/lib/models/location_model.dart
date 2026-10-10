import 'package:hive/hive.dart';
import 'location_tag_model.dart';
import 'location_image_model.dart';
import 'film_location_model.dart';

part 'location_model.g.dart';

/// Modelo de datos de una localización de rodaje registrada en la plataforma.
///
/// Mapea entre el JSON snake_case del backend y los campos camelCase de Dart.
@HiveType(typeId: 25)
class Location {
  @HiveField(0)
  final int? id;
  @HiveField(1)
  final String name;
  @HiveField(2)
  final String? description;
  @HiveField(3)
  final String? address;
  @HiveField(4)
  final double latitude;
  @HiveField(5)
  final double longitude;
  @HiveField(6)
  final List<String> tags;
  @HiveField(7)
  final List<String> images;
  @HiveField(8)
  final bool isActive;
  @HiveField(9)
  final DateTime? createdAt;
  @HiveField(10)
  final DateTime? updatedAt;
  @HiveField(12)
  final int? addedBy;
  /// Etiqueta visual corta mostrada en el mapa (p. ej. ``SC`` para un plató de sonido).
  @HiveField(13)
  final String? badge;
  @HiveField(14)
  final List<LocationTag> locationTags;
  @HiveField(15)
  final List<LocationImage> locationImages;
  /// IDs de otras localizaciones relacionadas con esta.
  @HiveField(16)
  final List<int> relatedLocationIds;
  @HiveField(17)
  final List<FilmLocation> filmLocations;

  Location({
    this.id,
    required this.name,
    this.description,
    this.address,
    required this.latitude,
    required this.longitude,
    this.tags = const [],
    this.images = const [],
    this.isActive = true,
    this.createdAt,
    this.updatedAt,
    this.addedBy,
    this.badge,
    this.locationTags = const [],
    this.locationImages = const [],
    this.relatedLocationIds = const [],
    this.filmLocations = const [],
  });

  /// Crea un [Location] a partir de un mapa JSON (claves snake_case del backend).
  factory Location.fromJson(Map<String, dynamic> json) {
    return Location(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      address: json['address'],
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      tags: json['tags'] != null ? List<String>.from(json['tags']) : [],
      images: json['images'] != null ? List<String>.from(json['images']) : [],
      isActive: json['is_active'] ?? true,
      createdAt: json['created_at'] != null ? DateTime.parse(json['created_at']) : null,
      updatedAt: json['updated_at'] != null ? DateTime.parse(json['updated_at']) : null,
      addedBy: json['added_by'],
      badge: json['badge'],
      locationTags: json['location_tags'] != null
          ? List<LocationTag>.from(json['location_tags'].map((j) => LocationTag.fromJson(j)))
          : [],
      locationImages: json['location_images'] != null
          ? List<LocationImage>.from(json['location_images'].map((j) => LocationImage.fromJson(j)))
          : [],
      relatedLocationIds: json['related_location_ids'] != null
          ? List<int>.from(json['related_location_ids'])
          : [],
      filmLocations: json['film_locations'] != null
          ? List<FilmLocation>.from(json['film_locations'].map((j) => FilmLocation.fromJson(j)))
          : [],
    );
  }

  /// Serializa este [Location] a un mapa JSON (claves snake_case).
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'address': address,
      'latitude': latitude,
      'longitude': longitude,
      'tags': tags,
      'images': images,
      'is_active': isActive,
      'badge': badge,
    };
  }
}
