import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:clakettes/screens/login_screen.dart';
import 'package:clakettes/services/api_service.dart';
import 'test_helper.dart';

Widget _createScreen() {
  return wrapWithLocalization(const LoginScreen());
}

void main() {
  setUp(() async {
    await setupApiTest();
  });

  testWidgets('testLoginScreenRenders', (tester) async {
    await tester.pumpWidget(_createScreen());
    await tester.pump();
    await tester.pump();

    expect(find.byType(TextFormField), findsNWidgets(2));
    expect(find.byType(FilledButton), findsOneWidget);
  });

  testWidgets('testLoginScreenCallsApiOnSubmit', (tester) async {
    ApiService().client = MockClient((request) async {
      return http.Response(json.encode({
        'access_token': 'test-token',
        'refresh_token': 'test-refresh',
        'token_type': 'bearer',
        'user': {'id': 1, 'username': 'test', 'email': 'test@test.com'},
      }), 200);
    });

    await tester.pumpWidget(_createScreen());
    await tester.pump();
    await tester.pump();

    await tester.enterText(find.byType(TextFormField).at(0), 'testuser');
    await tester.enterText(find.byType(TextFormField).at(1), 'password123');
    await tester.pump();

    await tester.ensureVisible(find.byType(FilledButton));
    await tester.tap(find.byType(FilledButton));
    await tester.pump();
    await tester.pump();
    expect(find.byType(TextFormField), findsNWidgets(2));
    expect(find.byType(FilledButton), findsOneWidget);
  });
}
