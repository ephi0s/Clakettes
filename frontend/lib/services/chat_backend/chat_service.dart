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
  static final List<ChatService> _liveInstances = <ChatService>[];

  /// Desconecta todas las instancias activas, sin cerrar sus streams.
  static Future<void> disconnectAll() async {
    for (final instance in List<ChatService>.from(_liveInstances)) {
      try {
        await instance._backend.disconnect();
      } catch (e) {
        debugPrint('[ChatService] disconnect error: $e');
      }
    }
  }

  final AuthService _auth;
  final ApiService _api;

  AbstractChatBackend _backend;
  StreamSubscription<Message>? _subscription;
  StreamSubscription<TypingEvent>? _typingSubscription;
  StreamSubscription<Duration>? _latencySubscription;
  StreamSubscription<int>? _readSubscription;
  final StreamController<Message> _incomingController = StreamController<Message>.broadcast();
  final StreamController<TypingEvent> _typingController = StreamController<TypingEvent>.broadcast();
  final StreamController<Duration> _latencyController = StreamController<Duration>.broadcast();
  final StreamController<int> _messageReadController = StreamController<int>.broadcast();
  final List<Message> _history = [];

  ChatService({AbstractChatBackend? backend, ApiService? api, AuthService? auth})
      : _api = api ?? ApiService(),
        _auth = auth ?? AuthService(),
        _backend = backend ?? WebSocketChatBackend(api: api) {
    _liveInstances.add(this);
  }

  /// Expone el servicio de API crudo para subidas.
  ApiService get api => _api;

  /// Mensajes entrantes del backend activo.
  Stream<Message> get onMessage => _incomingController.stream;

  /// Estado de reconexión del backend activo.
  Stream<bool> get onReconnecting => _backend.onReconnecting;

  /// Eventos de escritura reenviados por el backend activo.
  Stream<TypingEvent> get onTyping => _typingController.stream;

  /// Latencia reenviada por el backend activo.
  Stream<Duration> get onLatency => _latencyController.stream;

  /// Confirmaciones de lectura reenviadas por el backend activo.
  Stream<int> get onMessageRead => _messageReadController.stream;

  /// Historial local cargado, sin exponer la lista mutable interna.
  List<Message> get history => List.unmodifiable(_history);

  /// Intercambia el [backend] activo, desconectando el anterior.
  ///
  /// Reconecta el nuevo backend automáticamente; seguro de llamar tras [init].
  Future<void> useBackend(AbstractChatBackend backend) async {
    await _subscription?.cancel();
    await _typingSubscription?.cancel();
    await _latencySubscription?.cancel();
    await _readSubscription?.cancel();
    await _backend.disconnect();
    _backend = backend;
    await _tryConnect();
  }

  void _subscribePresence() {
    if (_backend is! ChatPresenceBackend) return;
    final presence = _backend as ChatPresenceBackend;
    _typingSubscription = presence.onTyping.listen(
      (event) => _typingController.add(event),
      onError: (Object e) => debugPrint('[ChatService] typing stream error: $e'),
    );
    _latencySubscription = presence.onLatency.listen(
      (value) => _latencyController.add(value),
      onError: (Object e) => debugPrint('[ChatService] latency stream error: $e'),
    );
    _readSubscription = presence.onMessageRead.listen(
      (id) => _messageReadController.add(id),
      onError: (Object e) => debugPrint('[ChatService] read stream error: $e'),
    );
  }

  void _remember(Message msg) {
    final id = msg.id;
    if (id == null) return;
    final index = _history.indexWhere((m) => m.id == id);
    if (index == -1) {
      _history.add(msg);
    } else {
      _history[index] = msg;
    }
  }

  Future<void> _tryConnect() async {
    try {
      final token = await _auth.getToken();
      if (token == null) return;
      await _backend.connect(token);
      _subscription = _backend.onMessage.listen(
        (msg) {
          _remember(msg);
          _incomingController.add(msg);
        },
        onError: (Object e) => debugPrint('[ChatService] stream error: $e'),
      );
      _subscribePresence();
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
    if (page <= 1) _history.clear();
    for (final msg in result.items) {
      _remember(msg);
    }
    return result.items;
  }

  /// Filtra el historial local cargado por contenido, sin distinguir mayúsculas.
  List<Message> searchMessages(String query) {
    final needle = query.trim().toLowerCase();
    if (needle.isEmpty) return List.unmodifiable(_history);
    return _history.where((m) => m.content.toLowerCase().contains(needle)).toList();
  }

  /// Marca [messageId] como leído en el backend activo.
  Future<void> markRead(int messageId) => _backend.markRead(messageId);

  /// Desconecta el backend, cancela las suscripciones y cierra los streams.
  Future<void> dispose() async {
    _liveInstances.remove(this);
    await _subscription?.cancel();
    await _typingSubscription?.cancel();
    await _latencySubscription?.cancel();
    await _readSubscription?.cancel();
    await _backend.disconnect();
    await _incomingController.close();
    await _typingController.close();
    await _latencyController.close();
    await _messageReadController.close();
  }
}
