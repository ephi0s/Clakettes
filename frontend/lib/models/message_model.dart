import 'package:hive/hive.dart';

part 'message_model.g.dart';

/// Modelo de datos de un mensaje de chat con soporte de contenido enriquecido.
///
/// Mapea entre el JSON snake_case del backend y los campos camelCase de Dart.
///
/// Tipos de mensaje:
/// - ``text``: texto plano en [content]
/// - ``image``: imagen en [mediaUrl], con [content] como pie opcional
/// - ``location``: [latitude]/[longitude] con [content] como etiqueta
/// - ``vcard``: tarjeta de contacto como JSON en [vcardData]
/// - ``ical``: evento de calendario como JSON en [icalData]
@HiveType(typeId: 10)
class Message {
  @HiveField(0)
  final int? id;
  @HiveField(1)
  final String content;
  @HiveField(2)
  final int senderId;
  @HiveField(3)
  final int? receiverId;
  @HiveField(4)
  final int? groupId;
  @HiveField(5)
  final int? channelId;
  @HiveField(6)
  final bool isRead;
  @HiveField(7)
  final DateTime? createdAt;
  @HiveField(8)
  final DateTime? updatedAt;
  @HiveField(9)
  final String messageType;
  @HiveField(10)
  final String? mediaUrl;
  @HiveField(11)
  final double? latitude;
  @HiveField(12)
  final double? longitude;
  @HiveField(13)
  final String? vcardData;
  @HiveField(14)
  final String? icalData;

  Message({
    this.id,
    required this.content,
    required this.senderId,
    this.receiverId,
    this.groupId,
    this.channelId,
    this.isRead = false,
    this.createdAt,
    this.updatedAt,
    this.messageType = 'text',
    this.mediaUrl,
    this.latitude,
    this.longitude,
    this.vcardData,
    this.icalData,
  });

  /// Crea un [Message] a partir de un mapa JSON (claves snake_case del backend).
  factory Message.fromJson(Map<String, dynamic> json) {
    return Message(
      id: json['id'],
      content: json['content'] ?? '',
      senderId: json['sender_id'],
      receiverId: json['receiver_id'],
      groupId: json['group_id'],
      channelId: json['channel_id'],
      isRead: json['is_read'] ?? false,
      createdAt: json['created_at'] != null ? DateTime.parse(json['created_at']) : null,
      updatedAt: json['updated_at'] != null ? DateTime.parse(json['updated_at']) : null,
      messageType: json['message_type'] ?? 'text',
      mediaUrl: json['media_url'],
      latitude: (json['latitude'] as num?)?.toDouble(),
      longitude: (json['longitude'] as num?)?.toDouble(),
      vcardData: json['vcard_data'],
      icalData: json['ical_data'],
    );
  }

  /// Serializa este [Message] a un mapa JSON (claves snake_case).
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'content': content,
      'sender_id': senderId,
      'receiver_id': receiverId,
      'group_id': groupId,
      'channel_id': channelId,
      'is_read': isRead,
      'message_type': messageType,
      'media_url': mediaUrl,
      'latitude': latitude,
      'longitude': longitude,
      'vcard_data': vcardData,
      'ical_data': icalData,
    };
  }
}
