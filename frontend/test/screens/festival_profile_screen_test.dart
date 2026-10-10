import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:clakettes/models/festival_model.dart';
import 'package:clakettes/screens/festival_profile_screen.dart';
import 'package:clakettes/services/api_service.dart';
import 'test_helper.dart';

final _sampleFestival = Festival(
  id: 1,
  name: 'Sundance',
  description: 'Test festival',
  location: 'Park City, UT',
  latitude: 40.0,
  longitude: -111.0,
  isActive: true,
);

Widget _createScreen() {
  return wrapWithLocalization(FestivalProfileScreen(festival: _sampleFestival));
}

void main() {
  setUp(() async {
    await setupApiTest();
    ApiService().client = MockClient((request) async {
      if (request.method == 'GET' && request.url.path.endsWith('/locations')) {
        return http.Response('[]', 200);
      }
      return http.Response('{"status":"ok"}', 200);
    });
  });

  testWidgets('testFestivalProfileScreenRenders', (tester) async {
    await tester.pumpWidget(_createScreen());
    await tester.pump();
    await tester.pump();
    await tester.pump();

    expect(find.text('Festival Profile'), findsOneWidget);
    expect(find.text('Sundance'), findsOneWidget);
    expect(find.text('Test festival'), findsOneWidget);
    expect(find.text('Park City, UT'), findsOneWidget);

    try {
      await tester.pumpAndSettle(const Duration(milliseconds: 100));
    } catch (_) {}
  });
}
