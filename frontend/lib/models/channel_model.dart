import 'package:hive/hive.dart';

part 'channel_model.g.dart';

/// Modelo de datos de un canal de mensajería dentro de la plataforma.
///
/// Mapea entre el JSON snake_case del backend y los campos camelCase de Dart.
@HiveType(typeId: 1)
class Channel {
  @HiveField(0)
  final int? id;
  @HiveField(1)
  final String name;
  @HiveField(2)
  final String? description;
  /// Tipo de canal, p. ej. ``community``, ``direct`` o ``announcements``.
  @HiveField(3)
  final String channelType;
  @HiveField(4)
  final int? maxMembers;
  @HiveField(5)
  final int createdBy;
  @HiveField(6)
  final bool isActive;
  @HiveField(7)
  final DateTime? createdAt;
  @HiveField(8)
  final DateTime? updatedAt;

  Channel({
    this.id,
    required this.name,
    this.description,
    this.channelType = 'community',
    this.maxMembers,
    required this.createdBy,
    this.isActive = true,
    this.createdAt,
    this.updatedAt,
  });

  /// Crea un [Channel] a partir de un mapa JSON (claves snake_case del backend).
  factory Channel.fromJson(Map<String, dynamic> json) {
    return Channel(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      channelType: json['channel_type'] ?? 'community',
      maxMembers: json['max_members'],
      createdBy: json['created_by'],
      isActive: json['is_active'] ?? true,
      createdAt: json['created_at'] != null ? DateTime.parse(json['created_at']) : null,
      updatedAt: json['updated_at'] != null ? DateTime.parse(json['updated_at']) : null,
    );
  }

  /// Serializa este [Channel] a un mapa JSON (claves snake_case).
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'channel_type': channelType,
      'max_members': maxMembers,
      'created_by': createdBy,
      'is_active': isActive,
    };
  }
}

/// Modelo de datos de la pertenencia de un usuario a un [Channel].
///
/// Mapea entre el JSON snake_case del backend y los campos camelCase de Dart.
@HiveType(typeId: 2)
class ChannelMember {
  @HiveField(0)
  final int? id;
  @HiveField(1)
  final int channelId;
  @HiveField(2)
  final int userId;
  /// Rol dentro del canal, p. ej. ``member``, ``moderator`` u ``owner``.
  @HiveField(3)
  final String role;
  @HiveField(4)
  final bool isActive;
  @HiveField(5)
  final DateTime? joinedAt;

  ChannelMember({
    this.id,
    required this.channelId,
    required this.userId,
    this.role = 'member',
    this.isActive = true,
    this.joinedAt,
  });

  /// Crea un [ChannelMember] a partir de un mapa JSON (claves snake_case del backend).
  factory ChannelMember.fromJson(Map<String, dynamic> json) {
    return ChannelMember(
      id: json['id'],
      channelId: json['channel_id'],
      userId: json['user_id'],
      role: json['role'] ?? 'member',
      isActive: json['is_active'] ?? true,
      joinedAt: json['joined_at'] != null ? DateTime.parse(json['joined_at']) : null,
    );
  }

  /// Serializa este [ChannelMember] a un mapa JSON (claves snake_case).
  Map<String, dynamic> toJson() {
    return {
      'channel_id': channelId,
      'user_id': userId,
      'role': role,
    };
  }
}
