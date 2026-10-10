import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../../models/message_model.dart';
import '../api_service.dart';
import '../backend_config.dart';
import 'abstract_chat_backend.dart';

/// Backend de chat basado en WebSocket para entrega de mensajes en tiempo real.
///
/// Conecta a `ws(s)://<backend>/api/chat/ws`, enviando el token de autenticación
/// como subprotocolo WebSocket. Se reconecta automáticamente con backoff
/// exponencial (hasta [_maxReconnectAttempts]) salvo que se cierre de forma
/// intencionada. Depende de [ApiService] y [BackendConfig].
class WebSocketChatBackend extends AbstractChatBackend {
  final ApiService _api;
  final StreamController<Message> _controller = StreamController<Message>.broadcast();
  final StreamController<bool> _reconnectingController = StreamController<bool>.broadcast();

  WebSocketChannel? _channel;
  StreamSubscription<dynamic>? _subscription;
  String? _token;
  int _reconnectAttempts = 0;
  final int _maxReconnectAttempts = 10;
  bool _disposed = false;
  bool _intentionalClose = false;

  /// Crea un backend que envuelve [api]; por defecto usa un [ApiService] nuevo.
  WebSocketChatBackend({ApiService? api}) : _api = api ?? ApiService();

  /// Emite los mensajes recibidos del servidor.
  @override
  Stream<Message> get onMessage => _controller.stream;

  /// Stream que emite true mientras se reconecta y false una vez conectado.
  @override
  Stream<bool> get onReconnecting => _reconnectingController.stream;

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

    final baseUrl = await BackendConfig.getUrl();
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
            _handlePayload(payload);
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

    Timer(delay, () async {
      if (!_disposed && !_intentionalClose) {
        _subscription?.cancel();
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
  void _handlePayload(Map<String, dynamic> payload) {
    final type = payload['type'] as String?;
    if (type == 'new_message') {
      final msgData = payload['message'] as Map<String, dynamic>;
      final msg = Message.fromJson(msgData);
      _controller.add(msg);
    }
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
    await _subscription?.cancel();
    await _channel?.sink.close();
    await _controller.close();
    await _reconnectingController.close();
  }
}

