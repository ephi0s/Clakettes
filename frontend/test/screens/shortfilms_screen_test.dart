import 'dart:convert';
import 'package:material_ui/material_ui.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:clakettes/screens/shortfilms_screen.dart';
import 'package:clakettes/services/api_service.dart';
import 'test_helper.dart';

Widget _createScreen() {
  return wrapWithLocalization(const ShortFilmsScreen(festivalId: 1, festivalName: 'Fest'));
}

Future<void> _pump(WidgetTester tester) async {
  await tester.pump();
  await tester.pump();
  await tester.pump();
  await tester.pump(const Duration(milliseconds: 100));
}

void main() {
  setUp(() async {
    await setupApiTest();
    SharedPreferences.setMockInitialValues({});
  });

  testWidgets('testShortFilmsScreenRenders', (tester) async {
    ApiService().client = MockClient((request) async {
      return http.Response(json.encode({
        'items': [], 'total': 0, 'pages': 0,
      }), 200);
    });

    await tester.pumpWidget(_createScreen());
    await _pump(tester);

    expect(find.text('No short films available'), findsOneWidget);
  });

  testWidgets('testShortFilmsScreenShowsFilms', (tester) async {
    ApiService().client = MockClient((request) async {
      return http.Response(json.encode({
        'items': [
          {'id': 1, 'title': 'The Last Frame', 'description': 'A great short film', 'duration': 15, 'user_id': 1, 'tags': null, 'is_public': true, 'video_url': null, 'thumbnail_url': null, 'festival_id': 1, 'contest_type': 'official_section', 'created_at': '2026-01-01T00:00:00.000Z', 'updated_at': '2026-06-01T00:00:00.000Z'},
        ],
        'total': 1,
        'pages': 1,
      }), 200);
    });

    await tester.pumpWidget(_createScreen());
    await _pump(tester);

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
    await _pump(tester);

    expect(find.byType(FloatingActionButton), findsOneWidget);
    expect(find.text('No short films available'), findsOneWidget);
  });
}
