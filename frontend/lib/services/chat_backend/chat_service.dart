import 'dart:async';
import 'package:flutter/foundation.dart';
import '../../models/message_model.dart';
import '../api_service.dart';
import '../auth_service.dart';
import 'abstract_chat_backend.dart';
import 'websocket_chat_backend.dart';

/// Fachada que gestiona el [AbstractChatBackend] activo y expone un
/// único [Stream] de mensajes entrantes.
class ChatService {
  final AuthService _auth;
  final ApiService _api;

  AbstractChatBackend _backend;
  StreamSubscription<Message>? _subscription;
  final StreamController<Message> _incomingController = StreamController<Message>.broadcast();

  ChatService({AbstractChatBackend? backend, ApiService? api, AuthService? auth})
      : _api = api ?? ApiService(),
        _auth = auth ?? AuthService(),
        _backend = backend ?? WebSocketChatBackend(api: ApiService());

  /// Expone el servicio de API crudo para subidas.
  ApiService get api => _api;

  /// Mensajes entrantes del backend activo.
  Stream<Message> get onMessage => _incomingController.stream;

  /// Estado de reconexión del backend activo.
  Stream<bool> get onReconnecting => _backend.onReconnecting;

  /// Intercambia el [backend] activo, desconectando el anterior.
  ///
  /// Reconecta el nuevo backend automáticamente; seguro de llamar tras [init].
  Future<void> useBackend(AbstractChatBackend backend) async {
    await _subscription?.cancel();
    await _backend.disconnect();
    _backend = backend;
    await _tryConnect();
  }

  Future<void> _tryConnect() async {
    try {
      final token = await _auth.getToken();
      if (token == null) return;
      await _backend.connect(token);
      _subscription = _backend.onMessage.listen(
        (msg) => _incomingController.add(msg),
        onError: (Object e) => debugPrint('[ChatService] stream error: $e'),
      );
    } catch (e) {
      debugPrint('[ChatService] connection error: $e');
    }
  }

  /// Conecta el backend por defecto usando el token de autenticación actual.
  ///
  /// Debe llamarse una vez tras autenticarse. No hace nada si aún no hay token
  /// disponible.
  Future<void> init() async {
    await _tryConnect();
  }

  /// Envía un mensaje a través del backend activo.
  ///
  /// [senderId] y [content] son obligatorios; el destino es uno de
  /// [receiverId], [groupId] o [channelId]. El contenido enriquecido opcional
  /// puede aportarse mediante [mediaUrl], [latitude]/[longitude], [vcardData] o
  /// [icalData]. Devuelve el [Message] enviado.
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
  }) {
    return _backend.sendMessage(
      senderId: senderId,
      content: content,
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
  }

  /// Carga un historial paginado de mensajes mediante la API REST.
  ///
  /// [page] (base 1) y [size] controlan la paginación; la conversación puede
  /// filtrarse por [senderId], [receiverId], [groupId] o [channelId]. Establece
  /// [unreadOnly] para obtener solo mensajes no leídos. Devuelve los items de la página.
  Future<List<Message>> loadMessages({
    int page = 1,
    int size = 50,
    int? senderId,
    int? receiverId,
    int? groupId,
    int? channelId,
    bool unreadOnly = false,
  }) async {
    final result = await _api.getMessages(
      page: page,
      size: size,
      senderId: senderId,
      receiverId: receiverId,
      groupId: groupId,
      channelId: channelId,
      unreadOnly: unreadOnly,
    );
    return result.items;
  }

  /// Marca [messageId] como leído en el backend activo.
  Future<void> markRead(int messageId) => _backend.markRead(messageId);

  /// Desconecta el backend, cancela las suscripciones y cierra los streams.
  Future<void> dispose() async {
    await _subscription?.cancel();
    await _backend.disconnect();
    await _incomingController.close();
  }
}
