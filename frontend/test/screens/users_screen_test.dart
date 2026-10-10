import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:clakettes/screens/users_screen.dart';
import 'package:clakettes/services/api_service.dart';
import 'test_helper.dart';

Widget _createScreen() {
  return wrapWithLocalization(const UsersScreen());
}

void main() {
  setUp(() async {
    await setupApiTest();
  });

  testWidgets('testUsersScreenRenders', (tester) async {
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

    expect(find.text('No users registered'), findsOneWidget);
  });

  testWidgets('testUsersScreenShowsUsers', (tester) async {
    ApiService().client = MockClient((request) async {
      return http.Response(json.encode({
        'items': [
          {'id': 1, 'username': 'jdoe', 'email': 'j@doe.com', 'full_name': 'John Doe', 'role': 'user', 'is_active': true, 'is_public': true, 'is_public_email': true, 'is_public_bio': false, 'is_public_location': false, 'bio': null, 'avatar_url': null, 'latitude': null, 'longitude': null, 'created_at': '2026-01-01T00:00:00.000Z', 'updated_at': '2026-06-01T00:00:00.000Z'},
        ],
        'total': 1, 'pages': 1,
      }), 200);
    });

    await tester.pumpWidget(_createScreen());
    await tester.pump();
    await tester.pump();
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 100));

    expect(find.text('John Doe'), findsOneWidget);
  });

  testWidgets('testUsersScreenHasFloatingActionButton', (tester) async {
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
    expect(find.text('No users registered'), findsOneWidget);
  });
}
