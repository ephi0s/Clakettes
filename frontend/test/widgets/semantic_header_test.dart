import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:clakettes/widgets/reusable_widgets.dart';

void main() {
  group('SemanticHeader', () {
    testWidgets('renders text', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: SemanticHeader(text: 'Festivals'),
          ),
        ),
      );
      expect(find.text('Festivals'), findsOneWidget);
    });

    testWidgets('applies custom style', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: SemanticHeader(
              text: 'Title',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
          ),
        ),
      );
      final textWidget = tester.widget<Text>(find.byType(Text));
      expect(textWidget.style?.fontSize, 24);
      expect(textWidget.style?.fontWeight, FontWeight.bold);
    });

    testWidgets('applies textAlign', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: SemanticHeader(
              text: 'Centered',
              textAlign: TextAlign.center,
            ),
          ),
        ),
      );
      final textWidget = tester.widget<Text>(find.byType(Text));
      expect(textWidget.textAlign, TextAlign.center);
    });

    testWidgets('uses default style when no style provided', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: SemanticHeader(text: 'Default Style'),
          ),
        ),
      );
      final textWidget = tester.widget<Text>(find.byType(Text));
      expect(textWidget.style, isNull);
    });

    testWidgets('SemanticHeader widget is in tree', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: SemanticHeader(text: 'Widget Test'),
          ),
        ),
      );
      expect(find.byType(SemanticHeader), findsOneWidget);
      expect(find.text('Widget Test'), findsOneWidget);
    });
  });
}
