import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:clakettes/widgets/reusable_widgets.dart';

void main() {
  group('InfoRow', () {
    testWidgets('renders icon and text', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: InfoRow(
              icon: Icons.email,
              semanticLabel: 'Email',
              text: 'test@example.com',
            ),
          ),
        ),
      );
      expect(find.byIcon(Icons.email), findsOneWidget);
      expect(find.text('test@example.com'), findsOneWidget);
    });

    testWidgets('handles empty text', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: InfoRow(
              icon: Icons.phone,
              semanticLabel: 'Phone',
              text: '',
            ),
          ),
        ),
      );
      expect(find.byIcon(Icons.phone), findsOneWidget);
      expect(find.byType(Text), findsOneWidget);
    });

    testWidgets('applies iconColor when provided', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: InfoRow(
              icon: Icons.email,
              semanticLabel: 'Email',
              text: 'test@example.com',
              iconColor: Colors.red,
            ),
          ),
        ),
      );
      final icon = tester.widget<Icon>(find.byType(Icon));
      expect(icon.color, Colors.red);
    });

    testWidgets('uses theme color when iconColor is null', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: InfoRow(
              icon: Icons.email,
              semanticLabel: 'Email',
              text: 'test@example.com',
            ),
          ),
        ),
      );
      final icon = tester.widget<Icon>(find.byType(Icon));
      expect(icon.color, isNotNull);
    });
  });
}
