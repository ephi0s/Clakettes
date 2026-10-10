import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hive/hive.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:clakettes/models/user_model.dart';
import 'package:clakettes/screens/chat_screen.dart';
import 'package:clakettes/services/api_service.dart';
import 'package:clakettes/services/offline_cache_service.dart';
import 'package:clakettes/services/sync_queue_service.dart';
import 'test_helper.dart';

Widget _createScreen() {
  return wrapWithLocalization(const ChatScreen());
}

void main() {
  setUp(() async {
    await setupApiTest();
    Hive.init('.');
    await OfflineCacheService.instance.init();
    await SyncQueueService.instance.init();
    await SyncQueueService.instance.clear();
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
}
