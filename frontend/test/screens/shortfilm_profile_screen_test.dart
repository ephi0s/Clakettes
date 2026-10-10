import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:clakettes/models/shortfilm_model.dart';
import 'package:clakettes/screens/shortfilm_profile_screen.dart';
import 'package:clakettes/services/api_service.dart';
import 'test_helper.dart';

final _sampleShortFilm = ShortFilm(
  id: 1,
  title: 'The Last Frame',
  description: 'A great short film',
  duration: 15,
  festivalId: 1,
  userId: 1,
  isPublic: true,
);

Widget _createScreen() {
  return wrapWithLocalization(ShortFilmProfileScreen(shortFilm: _sampleShortFilm));
}

void main() {
  setUp(() async {
    await setupApiTest();
    ApiService().client = MockClient((request) async {
      return http.Response('{"status":"ok"}', 200);
    });
  });

  testWidgets('testShortFilmProfileScreenRenders', (tester) async {
    await tester.pumpWidget(_createScreen());
    await tester.pump();
    await tester.pump();

    expect(find.text('Short Film Profile'), findsOneWidget);
    expect(find.text('The Last Frame'), findsOneWidget);
    expect(find.text('A great short film'), findsOneWidget);
  });
}
