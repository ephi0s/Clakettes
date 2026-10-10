import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:clakettes/screens/form_detail_screen.dart';
import 'package:clakettes/services/api_service.dart';
import 'test_helper.dart';

Widget _createScreen() {
  return wrapWithLocalization(const FormDetailScreen(formId: 1));
}

void main() {
  setUp(() async {
    await setupApiTest();
  });

  testWidgets('testFormDetailScreenRenders', (tester) async {
    ApiService().client = MockClient((request) async {
      final uri = request.url.toString();
      if (uri.contains('/responses') || uri.contains('/submissions')) {
        return http.Response(json.encode({
          'items': [], 'total': 0, 'pages': 0,
        }), 200);
      }
      return http.Response(json.encode({
        'id': 1, 'title': 'Test Form', 'form_type': 'festival_registration', 'festival_id': 1, 'is_active': true, 'is_public': true,
        'pages': [], 'created_at': '2026-01-01T00:00:00.000Z',
      }), 200);
    });

    await tester.pumpWidget(_createScreen());
    await tester.pump();
    await tester.pump();
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 100));

    expect(find.text('Test Form'), findsWidgets);
    expect(find.text('Details'), findsOneWidget);
  });
}
