import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:table_calendar/table_calendar.dart';
import 'package:clakettes/models/calendar_model.dart';
import 'package:clakettes/screens/calendar_screen.dart';
import 'package:clakettes/services/api_service.dart';
import 'package:clakettes/services/auth_service.dart';
import 'package:clakettes/widgets/error_state_widget.dart';
import 'test_helper.dart';

Widget _createScreen() => wrapWithLocalization(const CalendarScreen());

Map<String, dynamic> _agendaEventJson(int id, String title, DateTime start) => {
      'id': id,
      'festival_id': 7,
      'festival_name': 'Locarno',
      'title': title,
      'start_date': start.toIso8601String(),
      'end_date': start.add(const Duration(hours: 2)).toIso8601String(),
      'event_type': 'gala',
      'location': 'Piazza Grande',
      'color': '#B8956E',
      'visibility_scope': 'public',
      'is_private': false,
    };

Map<String, dynamic> _agendaJson({
  bool enabled = true,
  List<Map<String, dynamic>>? events,
  List<Map<String, dynamic>>? festivals,
}) =>
    {
      'enabled': enabled,
      'festivals': festivals ??
          [
            {'id': 7, 'name': 'Locarno', 'event_count': 1},
          ],
      'events': events ?? const [],
    };

void main() {
  testWidgets('renders the shared agenda with events of the selected day', (tester) async {
    await setupApiTest();
    await AuthService().saveToken('test-token');

    final now = DateTime.now();
    final start = DateTime(now.year, now.month, now.day, 20);

    ApiService().client = MockClient((request) async {
      if (request.url.path.endsWith('/calendar/agenda')) {
        return http.Response(
          json.encode(_agendaJson(events: [_agendaEventJson(42, 'Gala Night', start)])),
          200,
        );
      }
      return http.Response('{"items": [], "total": 0, "pages": 0}', 200);
    });

    await tester.pumpWidget(_createScreen());
    await tester.pump();
    await tester.pump();
    await tester.pump();

    expect(find.byType(TableCalendar<AgendaEvent>), findsOneWidget);
    expect(find.text('Reminders enabled'), findsOneWidget);
    expect(find.text('Gala Night'), findsOneWidget);
    expect(find.text('Locarno'), findsOneWidget);
  });

  testWidgets('shows the error state when the agenda request fails', (tester) async {
    await setupApiTest();
    await AuthService().saveToken('test-token');

    ApiService().client = MockClient((_) async => http.Response('error', 500));

    await tester.pumpWidget(_createScreen());
    await tester.pump();
    await tester.pump();
    await tester.pump();

    expect(find.byType(ErrorStateWidget), findsOneWidget);
  });

  testWidgets('hides the section entirely when the agenda is disabled', (tester) async {
    await setupApiTest();

    ApiService().client = MockClient((request) async {
      if (request.url.path.endsWith('/calendar/agenda')) {
        return http.Response(json.encode(_agendaJson(enabled: false)), 200);
      }
      return http.Response('[]', 200);
    });

    await tester.pumpWidget(_createScreen());
    await tester.pump();
    await tester.pump();
    await tester.pump();

    expect(find.byType(TableCalendar<AgendaEvent>), findsNothing);
    expect(find.byType(CalendarScreen), findsOneWidget);
  });

  testWidgets('loads the public agenda without an active session', (tester) async {
    await setupApiTest();

    final now = DateTime.now();
    final start = DateTime(now.year, now.month, now.day, 18);

    ApiService().client = MockClient((request) async {
      if (request.url.path.endsWith('/calendar/agenda')) {
        return http.Response(
          json.encode(_agendaJson(events: [_agendaEventJson(7, 'Open Screening', start)])),
          200,
        );
      }
      return http.Response('[]', 200);
    });

    await tester.pumpWidget(_createScreen());
    await tester.pump();
    await tester.pump();
    await tester.pump();

    expect(find.byType(TableCalendar<AgendaEvent>), findsOneWidget);
    expect(find.text('Open Screening'), findsOneWidget);
    expect(find.text('Reminders enabled'), findsNothing);
  });
}