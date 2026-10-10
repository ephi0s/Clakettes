import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:clakettes/models/user_model.dart';
import 'package:clakettes/screens/user_profile_screen.dart';
import 'package:clakettes/services/api_service.dart';
import 'test_helper.dart';

final _sampleUser = User(
  id: 1,
  username: 'jdoe',
  email: 'j@doe.com',
  fullName: 'John Doe',
  role: 'user',
  isActive: true,
  isPublic: true,
  isPublicEmail: true,
  isPublicBio: true,
  isPublicLocation: true,
);

Widget _createScreen() {
  return wrapWithLocalization(UserProfileScreen(user: _sampleUser));
}

void main() {
  setUp(() async {
    await setupApiTest();
    ApiService().client = MockClient((request) async {
      return http.Response('{"status":"ok"}', 200);
    });
  });

  testWidgets('testUserProfileScreenRenders', (tester) async {
    await tester.pumpWidget(_createScreen());
    await tester.pump();
    await tester.pump();

    expect(find.text('User Profile'), findsOneWidget);
    expect(find.text('John Doe'), findsOneWidget);
    expect(find.text('@jdoe'), findsOneWidget);
    expect(find.text('j@doe.com'), findsOneWidget);

    try {
      await tester.pumpAndSettle(const Duration(milliseconds: 100));
    } catch (_) {}
  });
}
