import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:clakettes/models/location_model.dart';
import 'package:clakettes/widgets/location_cards.dart';

void main() {
  group('LocationCard', () {
    testWidgets('renders name and description', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: LocationCard(
              location: Location(name: 'Plaza Mayor', latitude: 40.4, longitude: -3.7, description: 'Centro'),
              onTap: () {},
            ),
          ),
        ),
      );
      expect(find.text('Plaza Mayor'), findsOneWidget);
      expect(find.text('Centro'), findsOneWidget);
    });

    testWidgets('shows delete button when onDelete provided', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: LocationCard(
              location: Location(name: 'Plaza Mayor', latitude: 40.4, longitude: -3.7),
              onTap: () {},
              onDelete: () {},
            ),
          ),
        ),
      );
      expect(find.byIcon(Icons.delete_outline), findsOneWidget);
    });

    testWidgets('calls onDelete when delete pressed', (tester) async {
      var called = false;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: LocationCard(
              location: Location(name: 'Plaza Mayor', latitude: 40.4, longitude: -3.7),
              onTap: () {},
              onDelete: () => called = true,
            ),
          ),
        ),
      );
      await tester.tap(find.byIcon(Icons.delete_outline));
      await tester.pump();
      expect(called, isTrue);
    });
  });
}
