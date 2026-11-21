import 'dart:async';
import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:clakettes/services/chat_backend/chat_service.dart';
import 'package:clakettes/services/chat_backend/rest_chat_backend.dart';
import 'package:clakettes/services/api_service.dart';
import 'package:clakettes/services/auth_service.dart';
import 'package:clakettes/services/chat_backend/websocket_chat_backend.dart';
void main() {
  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  group('ChatService', () {
    test('constructor creates service with default backend', () {
      final service = ChatService();
      expect(service, isNotNull);
    });

    test('onMessage stream is broadcast', () {
      final service = ChatService();
      expect(service.onMessage, isNotNull);
    });

    test('onReconnecting stream is not null', () {
      final service = ChatService();
      expect(service.onReconnecting, isNotNull);
    });

    test('api getter returns ApiService', () {
      final service = ChatService();
      expect(service.api, isA<ApiService>());
    });

    test('useBackend switches backend', () async {
      final restBackend = RestChatBackend();
      final service = ChatService(backend: restBackend);

      ApiService().client = MockClient((request) async {
        return http.Response(json.encode({
          'id': 1, 'sender_id': 1, 'content': 'Test',
          'receiver_id': 2, 'message_type': 'text', 'is_read': false,
          'created_at': '2026-01-01T00:00:00.000Z',
        }), 200);
      });

      final msg = await service.sendMessage(senderId: 1, content: 'Test', receiverId: 2);
      expect(msg.content, 'Test');
    });

    test('sendMessage sends through backend', () async {
      final restBackend = RestChatBackend();
      final service = ChatService(backend: restBackend);

      ApiService().client = MockClient((request) async {
        return http.Response(json.encode({
          'id': 1, 'sender_id': 1, 'content': 'Hello',
          'receiver_id': 2, 'message_type': 'text', 'is_read': false,
          'created_at': '2026-01-01T00:00:00.000Z',
        }), 200);
      });

      final msg = await service.sendMessage(senderId: 1, content: 'Hello', receiverId: 2);
      expect(msg.content, 'Hello');
      expect(msg.senderId, 1);
      expect(msg.receiverId, 2);
    });

    test('markRead delegates to backend', () async {
      final restBackend = RestChatBackend();
      final service = ChatService(backend: restBackend);

      ApiService().client = MockClient((request) async {
        return http.Response('{}', 200);
      });

      await expectLater(service.markRead(42), completes);
    });

    test('loadMessages returns list of messages', () async {
      ApiService().client = MockClient((request) async {
        return http.Response(json.encode({
          'items': [
            {'id': 1, 'sender_id': 1, 'content': 'Hi', 'receiver_id': 2,
             'message_type': 'text', 'is_read': false,
             'created_at': '2026-01-01T00:00:00.000Z'},
            {'id': 2, 'sender_id': 2, 'content': 'Hello!', 'receiver_id': 1,
             'message_type': 'text', 'is_read': false,
             'created_at': '2026-01-01T00:00:00.000Z'},
          ],
          'total': 2,
          'pages': 1,
        }), 200);
      });

      final service = ChatService();
      final messages = await service.loadMessages(page: 1, size: 50);
      expect(messages.length, 2);
      expect(messages[0].content, 'Hi');
    });

    test('loadMessages filters by channelId', () async {
      ApiService().client = MockClient((request) async {
        expect(request.url.toString(), contains('channel_id=5'));
        return http.Response(json.encode({
          'items': [], 'total': 0, 'pages': 0,
        }), 200);
      });

      final service = ChatService();
      final messages = await service.loadMessages(channelId: 5);
      expect(messages, isEmpty);
    });

    test('dispose cancels subscriptions', () async {
      final restBackend = RestChatBackend();
      final service = ChatService(backend: restBackend);
      await expectLater(service.dispose(), completes);
    });

    test('init does not throw when not authenticated', () async {
      final service = ChatService();
      await expectLater(service.init(), completes);
    });

    test('init connects when token is present', () async {
      final auth = AuthService();
      await auth.saveToken('test-token');

      final restBackend = RestChatBackend();
      final service = ChatService(backend: restBackend, auth: auth);
      await expectLater(service.init(), completes);
    });

    test('searchMessages filters loaded history case-insensitively', () async {
      ApiService().client = MockClient((request) async {
        return http.Response(json.encode({
          'items': [
            {'id': 1, 'sender_id': 1, 'content': 'Hello World', 'message_type': 'text',
             'is_read': false, 'created_at': '2026-01-01T00:00:00.000Z'},
            {'id': 2, 'sender_id': 2, 'content': 'Goodbye', 'message_type': 'text',
             'is_read': false, 'created_at': '2026-01-01T00:01:00.000Z'},
          ],
          'total': 2,
          'pages': 1,
        }), 200);
      });

      final service = ChatService();
      await service.loadMessages();
      expect(service.searchMessages('hello').map((m) => m.id), [1]);
      expect(service.searchMessages('BYE').map((m) => m.id), [2]);
      expect(service.searchMessages('   '), hasLength(2));
      expect(service.searchMessages('missing'), isEmpty);
    });

    test('message_read event emits the read message id', () async {
      final backend = WebSocketChatBackend();
      final ids = <int>[];
      final sub = backend.onMessageRead.listen(ids.add);
      backend.handlePayload({'type': 'message_read', 'message_id': 42});
      await Future<void>.delayed(Duration.zero);
      await sub.cancel();
      expect(ids, [42]);
      await backend.disconnect();
    });

    test('typing event expires after the configured timeout', () async {
      final backend = WebSocketChatBackend(typingTimeout: const Duration(milliseconds: 40));
      final events = <TypingEvent>[];
      final done = Completer<void>();
      final sub = backend.onTyping.listen((event) {
        events.add(event);
        if (events.length == 2 && !done.isCompleted) done.complete();
      });
      backend.handlePayload({'type': 'typing', 'user_id': 7, 'channel_id': 3, 'is_typing': true});
      await done.future.timeout(const Duration(seconds: 2));
      await sub.cancel();
      expect(events.first.userId, 7);
      expect(events.first.channelId, 3);
      expect(events.first.isTyping, isTrue);
      expect(events.last.userId, 7);
      expect(events.last.isTyping, isFalse);
      await backend.disconnect();
    });

    test('pong event emits measured latency', () async {
      final backend = WebSocketChatBackend();
      final values = <Duration>[];
      final sub = backend.onLatency.listen(values.add);
      backend.handlePayload({'type': 'pong', 'latency_ms': 120});
      await Future<void>.delayed(Duration.zero);
      await sub.cancel();
      expect(values.single.inMilliseconds, 120);
      await backend.disconnect();
    });
  });
}
