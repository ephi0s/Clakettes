import 'package:hive/hive.dart';

part 'user_model.g.dart';

/// Modelo de datos de un usuario de la plataforma.
///
/// Mapea entre el JSON snake_case del backend y los campos camelCase de Dart.
@HiveType(typeId: 22)
class User {
  @HiveField(0)
  final int? id;
  @HiveField(1)
  final String username;
  @HiveField(2)
  final String? email;
  @HiveField(3)
  final String? fullName;
  @HiveField(4)
  final String? role;
  @HiveField(5)
  final String? bio;
  @HiveField(6)
  final String? avatarUrl;
  @HiveField(7)
  final bool isActive;
  @HiveField(8)
  final bool isPublic;
  @HiveField(9)
  final bool isPublicEmail;
  @HiveField(10)
  final bool isPublicBio;
  @HiveField(11)
  final bool isPublicLocation;
  @HiveField(12)
  final double? latitude;
  @HiveField(13)
  final double? longitude;
  @HiveField(14)
  final DateTime? createdAt;
  @HiveField(15)
  final DateTime? updatedAt;

  User({
    this.id,
    required this.username,
    this.email,
    this.fullName,
    this.role,
    this.bio,
    this.avatarUrl,
    this.isActive = true,
    this.isPublic = true,
    this.isPublicEmail = true,
    this.isPublicBio = true,
    this.isPublicLocation = true,
    this.latitude,
    this.longitude,
    this.createdAt,
    this.updatedAt,
  });

  /// Crea un [User] a partir de un mapa JSON (claves snake_case del backend).
  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      username: json['username'],
      email: json['email'],
      fullName: json['full_name'],
      role: json['role'],
      bio: json['bio'],
      avatarUrl: json['avatar_url'],
      isActive: json['is_active'] ?? true,
      isPublic: json['is_public'] ?? true,
      isPublicEmail: json['is_public_email'] ?? true,
      isPublicBio: json['is_public_bio'] ?? true,
      isPublicLocation: json['is_public_location'] ?? true,
      latitude: json['latitude']?.toDouble(),
      longitude: json['longitude']?.toDouble(),
      createdAt: json['created_at'] != null ? DateTime.parse(json['created_at']) : null,
      updatedAt: json['updated_at'] != null ? DateTime.parse(json['updated_at']) : null,
    );
  }

  /// Serializa este [User] a un mapa JSON (claves snake_case).
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'username': username,
      'email': email,
      'full_name': fullName,
      'role': role,
      'bio': bio,
      'avatar_url': avatarUrl,
      'is_active': isActive,
      'is_public': isPublic,
      'is_public_email': isPublicEmail,
      'is_public_bio': isPublicBio,
      'is_public_location': isPublicLocation,
      'latitude': latitude,
      'longitude': longitude,
    };
  }

  /// Devuelve una copia con sobrescritura selectiva de campos.
  User copyWith({
    int? id,
    String? username,
    String? email,
    String? fullName,
    String? role,
    String? bio,
    String? avatarUrl,
    bool? isActive,
    bool? isPublic,
    bool? isPublicEmail,
    bool? isPublicBio,
    bool? isPublicLocation,
    double? latitude,
    double? longitude,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return User(
      id: id ?? this.id,
      username: username ?? this.username,
      email: email ?? this.email,
      fullName: fullName ?? this.fullName,
      role: role ?? this.role,
      bio: bio ?? this.bio,
      avatarUrl: avatarUrl ?? this.avatarUrl,
      isActive: isActive ?? this.isActive,
      isPublic: isPublic ?? this.isPublic,
      isPublicEmail: isPublicEmail ?? this.isPublicEmail,
      isPublicBio: isPublicBio ?? this.isPublicBio,
      isPublicLocation: isPublicLocation ?? this.isPublicLocation,
      latitude: latitude ?? this.latitude,
      longitude: longitude ?? this.longitude,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}
