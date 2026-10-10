import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:clakettes/screens/create_channel_screen.dart';
import 'package:clakettes/services/api_service.dart';
import 'test_helper.dart';

Widget _createScreen() {
  return wrapWithLocalization(const CreateChannelScreen());
}

void main() {
  setUp(() async {
    await setupApiTest();
    ApiService().client = MockClient((request) async {
      return http.Response('{"status":"ok"}', 200);
    });
  });

  testWidgets('testCreateChannelScreenRenders', (tester) async {
    await tester.pumpWidget(_createScreen());
    await tester.pump();
    await tester.pump();

    expect(find.byType(TextFormField), findsWidgets);
    expect(find.text('Community'), findsOneWidget);
    expect(find.text('Private'), findsOneWidget);
  });
}
