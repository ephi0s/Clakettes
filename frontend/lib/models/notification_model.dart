import 'package:hive/hive.dart';

part 'notification_model.g.dart';

/// Modelo de datos de una notificación dentro de la aplicación.
///
/// Mapea entre el JSON snake_case del backend y los campos camelCase de Dart.
@HiveType(typeId: 11)
class AppNotification {
  @HiveField(0)
  final int id;
  @HiveField(1)
  final int userId;
  @HiveField(2)
  final String title;
  @HiveField(3)
  final String message;
  /// Tipo de notificación, p. ej. ``profile_update`` o ``festival_message``.
  @HiveField(4)
  final String notificationType;
  @HiveField(5)
  final bool isRead;
  @HiveField(6)
  final int? relatedUserId;
  @HiveField(7)
  final DateTime? createdAt;

  AppNotification({
    required this.id,
    required this.userId,
    required this.title,
    required this.message,
    this.notificationType = 'profile_update',
    this.isRead = false,
    this.relatedUserId,
    this.createdAt,
  });

  /// Crea un [AppNotification] a partir de un mapa JSON (claves snake_case del backend).
  factory AppNotification.fromJson(Map<String, dynamic> json) {
    return AppNotification(
      id: json['id'],
      userId: json['user_id'],
      title: json['title'],
      message: json['message'],
      notificationType: json['notification_type'] ?? 'profile_update',
      isRead: json['is_read'] ?? false,
      relatedUserId: json['related_user_id'],
      createdAt: json['created_at'] != null ? DateTime.parse(json['created_at']) : null,
    );
  }

  /// Serializa este [AppNotification] a un mapa JSON (claves snake_case).
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'title': title,
      'message': message,
      'notification_type': notificationType,
      'is_read': isRead,
      'related_user_id': relatedUserId,
    };
  }
}
