import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:clakettes/widgets/reusable_widgets.dart';

void main() {
  group('ProfileAvatar', () {
    testWidgets('renders CircleAvatar', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: ProfileAvatar(fallbackText: 'John Doe'),
          ),
        ),
      );
      expect(find.byType(CircleAvatar), findsOneWidget);
    });

    testWidgets('shows initials when no imageUrl', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: ProfileAvatar(fallbackText: 'John Doe'),
          ),
        ),
      );
      expect(find.text('J'), findsOneWidget);
    });

    testWidgets('shows first letter of fallbackText capitalized', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: ProfileAvatar(fallbackText: 'alice'),
          ),
        ),
      );
      expect(find.text('A'), findsOneWidget);
    });

    testWidgets('shows question mark when fallbackText is empty', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: ProfileAvatar(fallbackText: ''),
          ),
        ),
      );
      expect(find.text('?'), findsOneWidget);
    });

    testWidgets('backgroundImage is null when no imageUrl', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: ProfileAvatar(fallbackText: 'John'),
          ),
        ),
      );
      final avatar = tester.widget<CircleAvatar>(find.byType(CircleAvatar));
      expect(avatar.backgroundImage, isNull);
    });

    testWidgets('applies custom radius', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: ProfileAvatar(
              fallbackText: 'John',
              radius: 30,
            ),
          ),
        ),
      );
      final avatar = tester.widget<CircleAvatar>(find.byType(CircleAvatar));
      expect(avatar.radius, 30);
    });
  });
}
