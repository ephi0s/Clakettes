import 'dart:async';
import '../../models/message_model.dart';
import '../api_service.dart';
import 'abstract_chat_backend.dart';

/// Backend de chat basado en REST — el comportamiento original.
///
/// Sin entrega en tiempo real; los nuevos mensajes solo son visibles tras una
/// actualización manual. Esta clase existe como **fallback** para entornos
/// donde los WebSockets no están disponibles (p. ej., proxies corporativos),
/// y como implementación de referencia para backends personalizados.
class RestChatBackend extends AbstractChatBackend {
  final ApiService _api;
  final StreamController<Message> _controller = StreamController<Message>.broadcast();

  /// Crea un backend que envuelve [api]; por defecto usa un [ApiService] nuevo.
  RestChatBackend({ApiService? api}) : _api = api ?? ApiService();

  /// Emite los mensajes que se enviaron a través de este backend.
  @override
  Stream<Message> get onMessage => _controller.stream;

  /// No-op: REST no tiene una conexión persistente que establecer.
  @override
  Future<void> connect(String token) async {}

  /// Envía el mensaje mediante la API REST y lo emite localmente.
  @override
  Future<Message> sendMessage({
    required int senderId,
    required String content,
    int? receiverId,
    int? groupId,
    int? channelId,
    String messageType = 'text',
    String? mediaUrl,
    double? latitude,
    double? longitude,
    String? vcardData,
    String? icalData,
  }) async {
    final msg = await _api.sendMessage(
      senderId,
      content,
      receiverId: receiverId,
      groupId: groupId,
      channelId: channelId,
      messageType: messageType,
      mediaUrl: mediaUrl,
      latitude: latitude,
      longitude: longitude,
      vcardData: vcardData,
      icalData: icalData,
    );
    _controller.add(msg);
    return msg;
  }

  /// Marca [messageId] como leído mediante la API REST.
  @override
  Future<void> markRead(int messageId) async {
    await _api.markMessageRead(messageId);
  }

  /// Cierra el stream de mensajes y libera los recursos.
  @override
  Future<void> disconnect() async {
    await _controller.close();
  }
}
