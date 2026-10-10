import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:clakettes/screens/festivals_screen.dart';
import 'package:clakettes/services/api_service.dart';
import 'test_helper.dart';

Widget _createScreen() {
  return wrapWithLocalization(const FestivalsScreen());
}

void main() {
  setUp(() async {
    await setupApiTest();
  });

  testWidgets('testFestivalsScreenRenders', (tester) async {
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

    expect(find.text('No festivals available'), findsOneWidget);
  });

  testWidgets('testFestivalsScreenShowsFestivals', (tester) async {
    ApiService().client = MockClient((request) async {
      return http.Response(json.encode({
        'items': [
          {'id': 1, 'name': 'Sundance', 'description': 'Test', 'location': 'Park City, UT', 'latitude': 40.0, 'longitude': -111.0, 'is_active': true, 'is_public': true, 'tags': [], 'created_at': '2026-01-01T00:00:00.000Z', 'updated_at': '2026-06-01T00:00:00.000Z'},
          {'id': 2, 'name': 'Cannes', 'description': 'Test', 'location': 'Cannes, FR', 'latitude': 43.0, 'longitude': 7.0, 'is_active': true, 'is_public': true, 'tags': [], 'created_at': '2026-01-01T00:00:00.000Z', 'updated_at': '2026-06-01T00:00:00.000Z'},
        ],
        'total': 2, 'pages': 1,
      }), 200);
    });

    await tester.pumpWidget(_createScreen());
    await tester.pump();
    await tester.pump();
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 100));

    expect(find.text('Sundance'), findsOneWidget);
    expect(find.text('Cannes'), findsOneWidget);
  });

  testWidgets('testFestivalsScreenHasFloatingActionButton', (tester) async {
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

    expect(find.byType(FloatingActionButton), findsOneWidget);
    expect(find.text('No festivals available'), findsOneWidget);
  });
}
