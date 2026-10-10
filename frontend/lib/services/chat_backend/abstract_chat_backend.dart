import 'dart:async';
import '../../models/message_model.dart';

/// Interfaz abstracta para un backend de entrega de chat en el lado cliente.
///
/// Las implementaciones pueden usar WebSockets, polling REST, MQTT, XMPP o
/// cualquier otro transporte. El resto de la aplicación depende de esta interfaz
/// para que el transporte pueda intercambiarse mediante [ChatService] sin cambiar
/// el código de la UI.
abstract class AbstractChatBackend {
  Stream<Message> get onMessage;

  /// Stream que emite true mientras se reconecta y false una vez reconectado.
  Stream<bool> get onReconnecting => const Stream.empty();

  /// Conecta al backend (p. ej., abrir WebSocket, iniciar el temporizador de polling).
  Future<void> connect(String token);

  /// Envía un mensaje a través del backend con contenido enriquecido opcional.
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
  });

  Future<void> markRead(int messageId);

  Future<void> disconnect();
}
