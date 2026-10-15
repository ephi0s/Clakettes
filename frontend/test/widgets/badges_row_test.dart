import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:clakettes/services/api_service.dart';
import 'package:clakettes/widgets/badges_row.dart';
import '../screens/test_helper.dart';

Widget _createBadges() {
  return wrapWithLocalization(const ProfileBadges(userId: 1));
}

void main() {
  setUp(() async {
    await setupApiTest();
  });

  testWidgets('badges hidden when feature disabled', (tester) async {
    ApiService().client = MockClient((request) async {
      if (request.url.path.endsWith('/badges/status')) {
        return http.Response(json.encode({'enabled': false}), 200);
      }
      return http.Response(json.encode({'items': [], 'total': 0, 'pages': 0}), 200);
    });

    await tester.pumpWidget(_createBadges());
    await tester.pump();
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 100));

    expect(find.text('Insignias'), findsNothing);
  });

  testWidgets('badges render assignments when enabled', (tester) async {
    ApiService().client = MockClient((request) async {
      if (request.url.path.endsWith('/badges/status')) {
        return http.Response(json.encode({'enabled': true}), 200);
      }
      return http.Response(
        json.encode({
          'items': [
            {
              'id': 1,
              'badge_id': 2,
              'target_user_id': 1,
              'granted_by': 3,
              'reason': 'Veterano',
              'created_at': '2026-01-01T00:00:00.000Z',
              'badge': {'id': 2, 'name': 'Veterano', 'scope': 'festival', 'category': 'veteran'},
            },
          ],
          'total': 1,
          'pages': 1,
        }),
        200,
      );
    });

    await tester.pumpWidget(_createBadges());
    await tester.pump();
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 100));

    expect(find.text('Veterano'), findsOneWidget);
  });
}
