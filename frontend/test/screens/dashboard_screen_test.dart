import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:clakettes/screens/dashboard_screen.dart';
import 'package:clakettes/services/api_service.dart';
import 'test_helper.dart';

Widget _createScreen() {
  return wrapWithLocalization(const DashboardScreen());
}

void main() {
  setUp(() async {
    await setupApiTest();
  });

  testWidgets('testDashboardScreenRenders', (tester) async {
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

    expect(find.text('Welcome to Clakettes'), findsOneWidget);
    expect(find.text('No festivals available'), findsOneWidget);
  });

  testWidgets('testDashboardScreenShowsStats', (tester) async {
    ApiService().client = MockClient((request) async {
      if (request.url.path.contains('festivals')) {
        return http.Response(json.encode({
          'items': [{'id': 1, 'name': 'Sundance', 'is_active': true, 'latitude': 40.0, 'longitude': -111.0}],
          'total': 1, 'pages': 1,
        }), 200);
      }
      return http.Response(json.encode({
        'items': [], 'total': 0, 'pages': 0,
      }), 200);
    });

    await tester.pumpWidget(_createScreen());
    await tester.pump();
    await tester.pump();
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 100));
    await tester.pump(const Duration(milliseconds: 100));

    expect(find.text('Sundance'), findsOneWidget);
  });

  testWidgets('testDashboardScreenShowsErrorState', (tester) async {
    ApiService().client = MockClient((request) async {
      return http.Response('Internal Server Error', 500);
    });

    await tester.pumpWidget(_createScreen());
    await tester.pump();
    await tester.pump();
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 100));

    expect(find.text('Error'), findsOneWidget);
    expect(find.text('Refresh'), findsOneWidget);
  });
}
