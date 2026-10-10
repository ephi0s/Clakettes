import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:clakettes/screens/form_response_detail_screen.dart';
import 'package:clakettes/services/api_service.dart';
import 'test_helper.dart';

Widget _createScreen() {
  return wrapWithLocalization(FormResponseDetailScreen(response: sampleResponse()));
}

void main() {
  setUp(() async {
    await setupApiTest();
  });

  testWidgets('testFormResponseDetailScreenRenders', (tester) async {
    ApiService().client = MockClient((request) async {
      return http.Response(json.encode({
        'id': 1, 'festival_id': 1, 'title': 'Test Form', 'form_type': 'festival_registration', 'is_active': true, 'is_public': true,
        'pages': [], 'created_at': '2026-01-01T00:00:00.000Z',
      }), 200);
    });

    await tester.pumpWidget(_createScreen());
    await tester.pump();
    await tester.pump();
    await tester.pump();

    expect(find.text('Response detail #1'), findsOneWidget);
    expect(find.text('John Doe'), findsOneWidget);
    expect(find.text('john@example.com'), findsOneWidget);
  });
}
