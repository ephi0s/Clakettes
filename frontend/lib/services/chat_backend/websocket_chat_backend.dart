import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../../models/message_model.dart';
import '../api_service.dart';
import 'abstract_chat_backend.dart';

/// Estado de escritura de un usuario, opcionalmente en un canal.
class TypingEvent {
  final int userId;
  final int? channelId;
  final bool isTyping;

  const TypingEvent({required this.userId, this.channelId, this.isTyping = true});

  String get key => '$channelId:$userId';

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is TypingEvent &&
          other.userId == userId &&
          other.channelId == channelId &&
          other.isTyping == isTyping;

  @override
  int get hashCode => Object.hash(userId, channelId, isTyping);
}

/// Capacidades de presencia/latencia que un backend puede exponer además del
/// contrato básico de mensajería.
abstract class ChatPresenceBackend {
  Stream<TypingEvent> get onTyping;
  Stream<Duration> get onLatency;
  Stream<int> get onMessageRead;
}

/// Backend de chat basado en WebSocket para entrega de mensajes en tiempo real.
///
/// Conecta a `ws(s)://<backend>/api/chat/ws`, enviando el token de autenticación
/// como subprotocolo WebSocket. Se reconecta automáticamente con backoff
/// exponencial (hasta [_maxReconnectAttempts]) salvo que se cierre de forma
/// intencionada. La URL se resuelve desde [ApiService], igual que el REST.
class WebSocketChatBackend extends AbstractChatBackend implements ChatPresenceBackend {
  final ApiService _api;
  final StreamController<Message> _controller = StreamController<Message>.broadcast();
  final StreamController<bool> _reconnectingController = StreamController<bool>.broadcast();
  final StreamController<TypingEvent> _typingController = StreamController<TypingEvent>.broadcast();
  final StreamController<Duration> _latencyController = StreamController<Duration>.broadcast();
  final StreamController<int> _messageReadController = StreamController<int>.broadcast();
  final Map<String, Timer> _typingTimers = {};

  WebSocketChannel? _channel;
  StreamSubscription<dynamic>? _subscription;
  Timer? _reconnectTimer;
  String? _token;
  int _reconnectAttempts = 0;
  final int _maxReconnectAttempts = 10;
  final Duration typingTimeout;
  bool _disposed = false;
  bool _intentionalClose = false;

  /// Crea un backend que envuelve [api]; por defecto usa un [ApiService] nuevo.
  WebSocketChatBackend({ApiService? api, this.typingTimeout = const Duration(seconds: 5)})
      : _api = api ?? ApiService();

  /// Emite los mensajes recibidos del servidor.
  @override
  Stream<Message> get onMessage => _controller.stream;

  /// Stream que emite true mientras se reconecta y false una vez conectado.
  @override
  Stream<bool> get onReconnecting => _reconnectingController.stream;

  /// Eventos de escritura; al expirar el temporizador se emite `isTyping: false`.
  @override
  Stream<TypingEvent> get onTyping => _typingController.stream;

  /// Latencia medida del último `pong`.
  @override
  Stream<Duration> get onLatency => _latencyController.stream;

  /// Identificadores de mensajes confirmados como leídos por el servidor.
  @override
  Stream<int> get onMessageRead => _messageReadController.stream;

  /// Abre el WebSocket usando [token] y restablece el estado de reconexión.
  @override
  Future<void> connect(String token) async {
    _token = token;
    _reconnectAttempts = 0;
    _intentionalClose = false;
    await _doConnect();
  }

  Future<void> _doConnect() async {
    if (_disposed) return;
    final token = _token;
    if (token == null) return;

    final baseUrl = _api.rootUrl;
    final wsBase = baseUrl
        .replaceFirst('https://', 'wss://')
        .replaceFirst('http://', 'ws://');
    final uri = Uri.parse('$wsBase/api/chat/ws');

    try {
      _channel = WebSocketChannel.connect(uri, protocols: [token]);
      _reconnectAttempts = 0;
      _reconnectingController.add(false);

      _subscription = _channel!.stream.listen(
        (data) {
          if (_disposed) return;
          try {
            final payload = json.decode(data as String) as Map<String, dynamic>;
            handlePayload(payload);
          } catch (e) {
            debugPrint('[WebSocketChatBackend] JSON decode error: $e');
          }
        },
        onError: (Object e) {
          debugPrint('[WebSocketChatBackend] stream error: $e');
          _scheduleReconnect();
        },
        onDone: () {
          debugPrint('[WebSocketChatBackend] connection closed');
          _scheduleReconnect();
        },
      );
    } catch (e) {
      debugPrint('[WebSocketChatBackend] connection error: $e');
      _scheduleReconnect();
    }
  }

  void _scheduleReconnect() {
    if (_disposed || _intentionalClose) return;
    if (_reconnectAttempts >= _maxReconnectAttempts) {
      debugPrint('[WebSocketChatBackend] max reconnect attempts reached');
      return;
    }

    _reconnectAttempts++;
    _reconnectingController.add(true);

    final delay = Duration(
      seconds: (_reconnectAttempts <= 3)
          ? _reconnectAttempts
          : 3 + (_reconnectAttempts - 3) * 2,
    );
    debugPrint('[WebSocketChatBackend] reconnecting in ${delay.inSeconds}s '
        '(attempt $_reconnectAttempts/$_maxReconnectAttempts)');

    _reconnectTimer?.cancel();
    _reconnectTimer = Timer(delay, () async {
      if (!_disposed && !_intentionalClose) {
        await _subscription?.cancel();
        _channel?.sink.close();
        try {
          await _doConnect();
        } catch (e) {
          debugPrint('[WebSocketChatBackend] reconnect error: $e');
          _scheduleReconnect();
        }
      }
    });
  }

  /// Despacha un frame de servidor decodificado a su handler.
  void handlePayload(Map<String, dynamic> payload) {
    final type = payload['type'] as String?;
    switch (type) {
      case 'new_message':
        final msgData = payload['message'] as Map<String, dynamic>?;
        if (msgData != null) _controller.add(Message.fromJson(msgData));
        break;
      case 'pong':
        _handlePong(payload);
        break;
      case 'typing':
        _handleTyping(payload);
        break;
      case 'message_read':
        _handleMessageRead(payload);
        break;
    }
  }

  void _handlePong(Map<String, dynamic> payload) {
    final explicit = payload['latency_ms'] ?? payload['latency'];
    if (explicit is num) {
      _latencyController.add(Duration(milliseconds: explicit.toInt() < 0 ? 0 : explicit.toInt()));
      return;
    }
    final raw = payload['timestamp'] ?? payload['ts'] ?? payload['time'];
    if (raw is! num) {
      _latencyController.add(Duration.zero);
      return;
    }
    final nowMicros = DateTime.now().microsecondsSinceEpoch;
    final value = raw.toDouble();
    final sentMicros = value > 1e14 ? value.toInt() : value.toInt() * 1000;
    final diff = nowMicros - sentMicros;
    _latencyController.add(Duration(microseconds: diff < 0 ? 0 : diff));
  }

  void _handleTyping(Map<String, dynamic> payload) {
    final userId = (payload['user_id'] ?? payload['sender_id']) as int?;
    if (userId == null) return;
    final channelId = payload['channel_id'] as int?;
    final rawTyping = payload['is_typing'] ?? payload['typing'];
    final isTyping = rawTyping is bool ? rawTyping : true;
    final event = TypingEvent(userId: userId, channelId: channelId, isTyping: isTyping);
    final key = event.key;

    _typingTimers[key]?.cancel();
    if (!_typingController.isClosed) _typingController.add(event);
    if (!isTyping) {
      _typingTimers.remove(key);
      return;
    }
    _typingTimers[key] = Timer(typingTimeout, () {
      _typingTimers.remove(key);
      if (!_disposed && !_typingController.isClosed) {
        _typingController.add(TypingEvent(userId: userId, channelId: channelId, isTyping: false));
      }
    });
  }

  void _handleMessageRead(Map<String, dynamic> payload) {
    final id = (payload['message_id'] ?? payload['id']) as int?;
    if (id != null && !_messageReadController.isClosed) _messageReadController.add(id);
  }

  /// Envía un mensaje mediante la API REST (la entrega se confirma allí).
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
    return _api.sendMessage(
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
  }

  /// Marca [messageId] como leído mediante la API REST.
  @override
  Future<void> markRead(int messageId) async {
    await _api.markMessageRead(messageId);
  }

  /// Cierra el socket y los streams, impidiendo reconexiones posteriores.
  @override
  Future<void> disconnect() async {
    _intentionalClose = true;
    _disposed = true;
    _reconnectTimer?.cancel();
    for (final timer in _typingTimers.values) {
      timer.cancel();
    }
    _typingTimers.clear();
    await _subscription?.cancel();
    await _channel?.sink.close();
    await _controller.close();
    await _reconnectingController.close();
    await _typingController.close();
    await _latencyController.close();
    await _messageReadController.close();
  }
}
