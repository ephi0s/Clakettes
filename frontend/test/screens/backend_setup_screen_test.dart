import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:clakettes/screens/backend_setup_screen.dart';
import 'package:clakettes/services/api_service.dart';
import 'test_helper.dart';

Widget _createScreen({bool onStartup = false}) {
  return wrapWithLocalization(BackendSetupScreen(onStartup: onStartup));
}

void main() {
  setUp(() async {
    await setupApiTest();
    ApiService().client = MockClient((request) async {
      return http.Response('{"status":"ok"}', 200);
    });
  });

  testWidgets('testBackendSetupScreenRenders', (tester) async {
    await tester.pumpWidget(_createScreen());
    await tester.pump();
    await tester.pump();

    expect(find.byType(TextField), findsOneWidget);
    expect(find.text('http://localhost:8000'), findsOneWidget);
  });
}
