import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:clakettes/widgets/reusable_widgets.dart';

void main() {
  group('SemanticTextField', () {
    testWidgets('renders TextFormField', (tester) async {
      final controller = TextEditingController();
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SemanticTextField(
              controller: controller,
              label: 'Username',
              semanticLabel: 'Username input',
            ),
          ),
        ),
      );
      expect(find.byType(TextFormField), findsOneWidget);
      controller.dispose();
    });

    testWidgets('shows label text', (tester) async {
      final controller = TextEditingController();
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SemanticTextField(
              controller: controller,
              label: 'Email',
              semanticLabel: 'Email input',
            ),
          ),
        ),
      );
      expect(find.text('Email'), findsOneWidget);
      controller.dispose();
    });

    testWidgets('shows helperText when provided', (tester) async {
      final controller = TextEditingController();
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SemanticTextField(
              controller: controller,
              label: 'Bio',
              semanticLabel: 'Bio input',
              helperText: 'Tell us about yourself',
            ),
          ),
        ),
      );
      expect(find.text('Tell us about yourself'), findsOneWidget);
      controller.dispose();
    });

    testWidgets('controller value is displayed', (tester) async {
      final controller = TextEditingController(text: 'Initial value');
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SemanticTextField(
              controller: controller,
              label: 'Name',
              semanticLabel: 'Name input',
            ),
          ),
        ),
      );
      expect(find.text('Initial value'), findsOneWidget);
      controller.dispose();
    });

    testWidgets('obscureText hides text', (tester) async {
      final controller = TextEditingController(text: 'secret123');
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SemanticTextField(
              controller: controller,
              label: 'Password',
              semanticLabel: 'Password input',
              obscureText: true,
            ),
          ),
        ),
      );
      final textField = tester.widget<TextField>(find.byType(TextField));
      expect(textField.obscureText, isTrue);
      controller.dispose();
    });

    testWidgets('keyboardType is passed to TextField', (tester) async {
      final controller = TextEditingController();
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SemanticTextField(
              controller: controller,
              label: 'Email',
              semanticLabel: 'Email input',
              keyboardType: TextInputType.emailAddress,
            ),
          ),
        ),
      );
      final textField = tester.widget<TextField>(find.byType(TextField));
      expect(textField.keyboardType, TextInputType.emailAddress);
      controller.dispose();
    });

    testWidgets('maxLines is passed to TextField', (tester) async {
      final controller = TextEditingController();
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SemanticTextField(
              controller: controller,
              label: 'Bio',
              semanticLabel: 'Bio input',
              maxLines: 3,
            ),
          ),
        ),
      );
      final textField = tester.widget<TextField>(find.byType(TextField));
      expect(textField.maxLines, 3);
      controller.dispose();
    });

    testWidgets('maxLength is passed to TextField', (tester) async {
      final controller = TextEditingController();
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SemanticTextField(
              controller: controller,
              label: 'Short',
              semanticLabel: 'Short input',
              maxLength: 10,
            ),
          ),
        ),
      );
      final textField = tester.widget<TextField>(find.byType(TextField));
      expect(textField.maxLength, 10);
      controller.dispose();
    });

    testWidgets('defaults to maxLines 1', (tester) async {
      final controller = TextEditingController();
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SemanticTextField(
              controller: controller,
              label: 'Line',
              semanticLabel: 'Line input',
            ),
          ),
        ),
      );
      final textField = tester.widget<TextField>(find.byType(TextField));
      expect(textField.maxLines, 1);
      controller.dispose();
    });
  });
}
