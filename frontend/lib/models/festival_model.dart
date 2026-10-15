import 'package:hive/hive.dart';

part 'festival_model.g.dart';

/// Modelo de datos de un festival de cine.
///
/// Mapea entre el JSON snake_case del backend y los campos camelCase de Dart.
@HiveType(typeId: 9)
class Festival {
  @HiveField(0)
  final int? id;
  @HiveField(1)
  final String name;
  @HiveField(2)
  final String? description;
  @HiveField(3)
  final String? location;
  @HiveField(4)
  final double? latitude;
  @HiveField(5)
  final double? longitude;
  @HiveField(6)
  final bool isActive;
  @HiveField(7)
  final String? website;
  @HiveField(8)
  final String? logoUrl;
  @HiveField(9)
  final DateTime? createdAt;
  @HiveField(10)
  final DateTime? updatedAt;
  /// URLs de las imágenes de la galería del festival.
  @HiveField(11)
  final List<String> images;
  /// Indica si los participantes pueden mostrar un alias en lugar de su nombre real.
  @HiveField(12)
  final bool allowAliasDisplay;
  /// Indica si el admin general incluye los eventos de este festival en la agenda.
  @HiveField(13)
  final bool showInCalendar;
  @HiveField(14)
  final String? bannerUrl;
  @HiveField(15)
  final String? tagline;
  @HiveField(16)
  final Map<String, String>? socialLinks;

  Festival({
    this.id,
    required this.name,
    this.description,
    this.location,
    this.latitude,
    this.longitude,
    this.isActive = true,
    this.website,
    this.logoUrl,
    this.createdAt,
    this.updatedAt,
    this.images = const [],
    this.allowAliasDisplay = false,
    this.showInCalendar = true,
    this.bannerUrl,
    this.tagline,
    this.socialLinks,
  });

  /// Crea un [Festival] a partir de un mapa JSON (claves snake_case del backend).
  factory Festival.fromJson(Map<String, dynamic> json) {
    return Festival(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      location: json['location'],
      latitude: json['latitude']?.toDouble(),
      longitude: json['longitude']?.toDouble(),
      isActive: json['is_active'] ?? true,
      website: json['website'],
      logoUrl: json['logo_url'],
      createdAt: json['created_at'] != null ? DateTime.parse(json['created_at']) : null,
      updatedAt: json['updated_at'] != null ? DateTime.parse(json['updated_at']) : null,
      images: json['images'] != null ? List<String>.from(json['images']) : [],
      allowAliasDisplay: json['allow_alias_display'] ?? false,
      showInCalendar: json['show_in_calendar'] ?? true,
      bannerUrl: json['banner_url'],
      tagline: json['tagline'],
      socialLinks: json['social_links'] != null
          ? Map<String, String>.from(
              (json['social_links'] as Map).map((k, v) => MapEntry(k.toString(), v.toString())))
          : null,
     );
  }

  /// Serializa este [Festival] a un mapa JSON (claves snake_case).
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'location': location,
      'latitude': latitude,
      'longitude': longitude,
      'is_active': isActive,
      'website': website,
      'logo_url': logoUrl,
      'images': images,
      'allow_alias_display': allowAliasDisplay,
      'show_in_calendar': showInCalendar,
      'banner_url': bannerUrl,
      'tagline': tagline,
      'social_links': socialLinks,
    };
  }
}
