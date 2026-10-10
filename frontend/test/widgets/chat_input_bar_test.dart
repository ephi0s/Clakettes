import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:clakettes/l10n/app_localizations.dart';
import 'package:clakettes/widgets/chat_input_bar.dart';
import '../screens/test_helper.dart';

Widget _wrap({bool isSending = false, VoidCallback? onSend}) {
  final controller = TextEditingController();
  return wrapWithLocalization(Builder(builder: (ctx) {
    return ChatInputBar(
      controller: controller,
      isSending: isSending,
      l10n: AppLocalizations.of(ctx)!,
      onSend: onSend ?? () {},
      onEmoji: () {},
      onAttach: () {},
    );
  }));
}

void main() {
  group('ChatInputBar', () {
    testWidgets('renders text field and send button', (tester) async {
      await tester.pumpWidget(_wrap());
      await tester.pump();
      expect(find.byType(TextField), findsOneWidget);
      expect(find.byIcon(Icons.send), findsOneWidget);
    });

    testWidgets('shows progress indicator while sending', (tester) async {
      await tester.pumpWidget(_wrap(isSending: true));
      await tester.pump();
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('calls onSend when send pressed', (tester) async {
      var called = false;
      await tester.pumpWidget(_wrap(onSend: () => called = true));
      await tester.pump();
      await tester.tap(find.byIcon(Icons.send));
      expect(called, isTrue);
    });
  });
}
