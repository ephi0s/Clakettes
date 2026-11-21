import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hive/hive.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:clakettes/models/message_model.dart';
import 'package:clakettes/models/user_model.dart';
import 'package:clakettes/screens/chat_screen.dart';
import 'package:clakettes/widgets/chat_bubble.dart';
import 'package:clakettes/services/api_service.dart';
import 'package:clakettes/services/offline_cache_service.dart';
import 'package:clakettes/services/sync_queue_service.dart';
import 'package:clakettes/l10n/app_localizations.dart';
import 'test_helper.dart';

Widget _createScreen() {
  return wrapWithLocalization(const ChatScreen());
}

void main() {
  var servicesReady = false;

  setUp(() async {
    await setupApiTest();
    if (servicesReady) return;
    final hiveDir = Directory('build/hive_chat_test_${DateTime.now().microsecondsSinceEpoch}');
    hiveDir.createSync(recursive: true);
    Hive.init(hiveDir.path);
    await OfflineCacheService.instance.init();
    await SyncQueueService.instance.init();
    servicesReady = true;
  });

  testWidgets('testChatScreenRenders', (tester) async {
    ApiService().client = MockClient((request) async {
      return http.Response(json.encode({
        'items': [], 'total': 0, 'pages': 0,
      }), 200);
    });

    await tester.pumpWidget(_createScreen());
    await tester.pump();
    await tester.pump();
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 100));

    expect(find.text('Write a message...'), findsOneWidget);
  });

  testWidgets('testChatSendFailsShowsOfflineSnackBar', (tester) async {
    ApiService().client = MockClient((request) async {
      if (request.method == 'POST' && request.url.path.endsWith('/chat/messages')) {
        throw Exception('network error');
      }
      if (request.url.path.endsWith('/chat/messages')) {
        return http.Response(json.encode({
          'items': [], 'total': 0, 'pages': 0,
        }), 200);
      }
      return http.Response('{}', 500);
    });

    final user = User(id: 1, username: 'test');
    await tester.pumpWidget(wrapWithLocalization(ChatScreen(currentUser: user)));
    await tester.pump();
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 100));

    await tester.enterText(find.byType(TextField), 'hello offline');
    await tester.testTextInput.receiveAction(TextInputAction.send);
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 100));

    expect(
      find.text("Message saved. It will be sent when you're back online."),
      findsOneWidget,
    );
  });

  testWidgets('dedupAndSort removes duplicate ids and orders by createdAt then id', (tester) async {
    final later = Message(id: 2, content: 'later', senderId: 1, createdAt: DateTime.utc(2026, 1, 2));
    final earlier = Message(id: 1, content: 'earlier', senderId: 1, createdAt: DateTime.utc(2026, 1, 1));
    final duplicate = Message(id: 2, content: 'duplicate', senderId: 1, createdAt: DateTime.utc(2026, 1, 2));
    final sameTimeHigherId = Message(id: 3, content: 'third', senderId: 1, createdAt: DateTime.utc(2026, 1, 2));

    await tester.pumpWidget(const SizedBox.shrink());
    final result = ChatScreen.dedupAndSort([later, duplicate, sameTimeHigherId, earlier]);
    expect(result.map((m) => m.id), [1, 2, 3]);
    expect(result.map((m) => m.content), ['earlier', 'later', 'third']);
  });

  testWidgets('read message renders accessible read indicator', (tester) async {
    await tester.pumpWidget(wrapWithLocalization(ChatBubbleWidget(
      bubble: ChatBubble(
        message: Message(id: 9, content: 'hola', senderId: 2, isRead: true),
        isMe: false,
      ),
      l10n: AppLocalizations.test(const Locale('en'), loadTestLocalizations()),
    )));
    await tester.pump();
    await tester.pump();

    expect(find.byType(ChatBubbleWidget), findsOneWidget);
    expect(find.text('hola'), findsOneWidget);
    expect(find.text(ChatBubbleWidget.readLabel), findsOneWidget);
    expect(find.byIcon(Icons.done_all), findsOneWidget);
  });
}
