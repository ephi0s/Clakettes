import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:clakettes/l10n/app_localizations.dart';
import 'package:clakettes/models/message_model.dart';
import 'package:clakettes/widgets/chat_bubble.dart';
import '../screens/test_helper.dart';

Widget _wrap(ChatBubble bubble) {
  return wrapWithLocalization(Builder(builder: (ctx) {
    return ChatBubbleWidget(bubble: bubble, l10n: AppLocalizations.of(ctx)!);
  }));
}

void main() {
  group('ChatBubbleWidget', () {
    testWidgets('renders text content', (tester) async {
      await tester.pumpWidget(_wrap(ChatBubble(
        message: Message(content: 'hello', senderId: 2),
        isMe: false,
      )));
      await tester.pump();
      expect(find.text('hello'), findsOneWidget);
    });

    testWidgets('renders location content with coordinates', (tester) async {
      await tester.pumpWidget(_wrap(ChatBubble(
        message: Message(content: 'here', senderId: 2, messageType: 'location', latitude: 40.1, longitude: -3.7),
        isMe: false,
      )));
      await tester.pump();
      expect(find.text('here'), findsOneWidget);
      expect(find.textContaining('40.100000'), findsOneWidget);
    });

    testWidgets('renders vcard name', (tester) async {
      await tester.pumpWidget(_wrap(ChatBubble(
        message: Message(content: 'K', senderId: 2, messageType: 'vcard', vcardData: '{"name":"K","phone":"1"}'),
        isMe: true,
      )));
      await tester.pump();
      expect(find.text('K'), findsWidgets);
    });
  });
}
