import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:clakettes/screens/awards_screen.dart';
import 'package:clakettes/services/api_service.dart';
import 'test_helper.dart';

Widget _createScreen() {
  return wrapWithLocalization(const AwardsScreen(festivalId: 1, festivalName: 'Sundance'));
}

void main() {
  setUp(() async {
    await setupApiTest();
  });

  testWidgets('testAwardsScreenRenders', (tester) async {
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

    expect(find.text('Awards — Sundance'), findsOneWidget);
    expect(find.text('No awards'), findsOneWidget);
  });

  testWidgets('testAwardsScreenShowsAwards', (tester) async {
    ApiService().client = MockClient((request) async {
      return http.Response(json.encode({
        'items': [
          {'id': 1, 'award_name': 'Best Director', 'description': 'Test', 'festival_id': 1, 'award_category': 'main', 'is_public': true, 'is_verified': false, 'created_at': '2026-01-01T00:00:00.000Z'},
        ],
        'total': 1, 'pages': 1,
      }), 200);
    });

    await tester.pumpWidget(_createScreen());
    await tester.pump();
    await tester.pump();
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 100));

    expect(find.text('Best Director'), findsOneWidget);
  });
}
