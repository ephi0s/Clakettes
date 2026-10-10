import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:clakettes/screens/admin_screen.dart';
import 'package:clakettes/services/api_service.dart';
import 'test_helper.dart';

Widget _createScreen() {
  return wrapWithLocalization(const AdminScreen());
}

void main() {
  setUp(() async {
    await setupApiTest();
    ApiService().client = MockClient((request) async {
      return http.Response('{"status":"ok"}', 200);
    });
  });

  testWidgets('testAdminScreenRenders', (tester) async {
    await tester.pumpWidget(_createScreen());
    await tester.pump();
    await tester.pump();

    expect(find.text('Admin Panel'), findsOneWidget);
    expect(find.text('Error'), findsOneWidget);
  });
}
