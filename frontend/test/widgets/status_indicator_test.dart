import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:clakettes/widgets/reusable_widgets.dart';

void main() {
  group('StatusIndicator', () {
    testWidgets('shows active icon when isActive=true', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: StatusIndicator(
              isActive: true,
              activeLabel: 'Active',
              inactiveLabel: 'Inactive',
            ),
          ),
        ),
      );
      expect(find.byIcon(Icons.check_circle_rounded), findsOneWidget);
    });

    testWidgets('shows inactive icon when isActive=false', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: StatusIndicator(
              isActive: false,
              activeLabel: 'Active',
              inactiveLabel: 'Inactive',
            ),
          ),
        ),
      );
      expect(find.byIcon(Icons.cancel_rounded), findsOneWidget);
    });

    testWidgets('shows Chip when useChip=true', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: StatusIndicator(
              isActive: true,
              activeLabel: 'Active',
              inactiveLabel: 'Inactive',
              useChip: true,
            ),
          ),
        ),
      );
      expect(find.byType(Chip), findsOneWidget);
      expect(find.text('Active'), findsOneWidget);
    });

    testWidgets('shows Chip with inactive label', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: StatusIndicator(
              isActive: false,
              activeLabel: 'Active',
              inactiveLabel: 'Inactive',
              useChip: true,
            ),
          ),
        ),
      );
      expect(find.byType(Chip), findsOneWidget);
      expect(find.text('Inactive'), findsOneWidget);
    });

    testWidgets('no Chip when useChip=false', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: StatusIndicator(
              isActive: true,
              activeLabel: 'Active',
              inactiveLabel: 'Inactive',
              useChip: false,
            ),
          ),
        ),
      );
      expect(find.byType(Chip), findsNothing);
    });

    testWidgets('uses custom icons', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: StatusIndicator(
              isActive: true,
              activeLabel: 'Public',
              inactiveLabel: 'Private',
              activeIcon: Icons.visibility,
              inactiveIcon: Icons.visibility_off,
            ),
          ),
        ),
      );
      expect(find.byIcon(Icons.visibility), findsOneWidget);
    });

    testWidgets('uses custom active color', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: StatusIndicator(
              isActive: true,
              activeLabel: 'Active',
              inactiveLabel: 'Inactive',
              activeColor: Colors.blue,
            ),
          ),
        ),
      );
      final icon = tester.widget<Icon>(find.byType(Icon));
      expect(icon.color, Colors.blue);
    });
  });
}
