import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:clakettes/screens/shortfilms_screen.dart';
import 'package:clakettes/services/api_service.dart';
import 'test_helper.dart';

Widget _createScreen() {
  return wrapWithLocalization(const ShortFilmsScreen());
}

void main() {
  setUp(() async {
    await setupApiTest();
  });

  testWidgets('testShortFilmsScreenRenders', (tester) async {
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

    expect(find.text('No short films available'), findsOneWidget);
  });

  testWidgets('testShortFilmsScreenShowsFilms', (tester) async {
    ApiService().client = MockClient((request) async {
      return http.Response(json.encode({
        'items': [
          {'id': 1, 'title': 'The Last Frame', 'description': 'A great short film', 'duration': 15, 'user_id': 1, 'tags': null, 'is_public': true, 'video_url': null, 'thumbnail_url': null, 'festival_id': null, 'created_at': '2026-01-01T00:00:00.000Z', 'updated_at': '2026-06-01T00:00:00.000Z'},
        ],
        'total': 1, 'pages': 1,
      }), 200);
    });

    await tester.pumpWidget(_createScreen());
    await tester.pump();
    await tester.pump();
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 100));

    expect(find.text('The Last Frame'), findsOneWidget);
    expect(find.text('15 min'), findsOneWidget);
  });

  testWidgets('testShortFilmsScreenHasFloatingActionButton', (tester) async {
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
    expect(find.text('No short films available'), findsOneWidget);
  });
}
