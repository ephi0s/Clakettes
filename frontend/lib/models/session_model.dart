import 'package:hive/hive.dart';

part 'session_model.g.dart';

/// Modelo de datos de una sesión de usuario (sesión de inicio activa con token de refresco).
@HiveType(typeId: 19)
class UserSession {
  @HiveField(0)
  final int id;
  @HiveField(1)
  final int userId;
  @HiveField(2)
  final String deviceName;
  @HiveField(3)
  final String ipAddress;
  @HiveField(4)
  final String userAgent;
  @HiveField(5)
  final DateTime lastUsedAt;
  @HiveField(6)
  final DateTime createdAt;
  @HiveField(7)
  final DateTime expiresAt;
  @HiveField(8)
  final bool isActive;

  /// Indica si esta sesión es la que usa actualmente la aplicación.
  final bool isCurrent;

  UserSession({
    required this.id,
    required this.userId,
    this.deviceName = '',
    this.ipAddress = '',
    this.userAgent = '',
    required this.lastUsedAt,
    required this.createdAt,
    required this.expiresAt,
    this.isActive = true,
    this.isCurrent = false,
  });

  /// Crea un [UserSession] a partir de un mapa JSON (claves snake_case del backend).
  factory UserSession.fromJson(Map<String, dynamic> json) {
    return UserSession(
      id: json['id'],
      userId: json['user_id'],
      deviceName: json['device_name'] ?? '',
      ipAddress: json['ip_address'] ?? '',
      userAgent: json['user_agent'] ?? '',
      lastUsedAt: DateTime.parse(json['last_used_at']),
      createdAt: DateTime.parse(json['created_at']),
      expiresAt: DateTime.parse(json['expires_at']),
      isActive: json['is_active'] ?? true,
      isCurrent: json['is_current'] ?? false,
    );
  }
}
