import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:clakettes/widgets/reusable_widgets.dart';

void main() {
  group('ListItemCard', () {
    testWidgets('renders title and leading widget', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: ListItemCard(
              leading: Icon(Icons.person),
              title: 'John Doe',
            ),
          ),
        ),
      );
      expect(find.text('John Doe'), findsOneWidget);
      expect(find.byIcon(Icons.person), findsOneWidget);
      expect(find.byType(Card), findsOneWidget);
      expect(find.byType(ListTile), findsOneWidget);
    });

    testWidgets('renders subtitle when provided', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: ListItemCard(
              leading: Icon(Icons.person),
              title: 'John Doe',
              subtitle: Text('john@example.com'),
            ),
          ),
        ),
      );
      expect(find.text('john@example.com'), findsOneWidget);
    });

    testWidgets('renders trailing when provided', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: ListItemCard(
              leading: Icon(Icons.person),
              title: 'John Doe',
              trailing: Icon(Icons.arrow_forward),
            ),
          ),
        ),
      );
      expect(find.byIcon(Icons.arrow_forward), findsOneWidget);
    });

    testWidgets('onTap callback works', (tester) async {
      bool tapped = false;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: ListItemCard(
              leading: const Icon(Icons.person),
              title: 'John Doe',
              onTap: () => tapped = true,
            ),
          ),
        ),
      );
      await tester.tap(find.byType(ListTile));
      expect(tapped, isTrue);
    });

    testWidgets('onLongPress callback works', (tester) async {
      bool longPressed = false;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: ListItemCard(
              leading: const Icon(Icons.person),
              title: 'John Doe',
              onLongPress: () => longPressed = true,
            ),
          ),
        ),
      );
      await tester.longPress(find.byType(ListTile));
      expect(longPressed, isTrue);
    });

    testWidgets('no subtitle renders only title', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: ListItemCard(
              leading: Icon(Icons.person),
              title: 'Only Title',
            ),
          ),
        ),
      );
      expect(find.text('Only Title'), findsOneWidget);
      expect(find.byType(Text), findsOneWidget);
    });
  });
}
