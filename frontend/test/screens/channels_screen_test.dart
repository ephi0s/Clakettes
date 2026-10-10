import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:clakettes/screens/channels_screen.dart';
import 'package:clakettes/services/api_service.dart';
import 'test_helper.dart';

Widget _createScreen() {
  return wrapWithLocalization(const ChannelsScreen());
}

void main() {
  setUp(() async {
    await setupApiTest();
  });

  testWidgets('testChannelsScreenRenders', (tester) async {
    ApiService().client = MockClient((request) async {
      return http.Response(json.encode({
        'items': [], 'total': 0, 'pages': 0,
      }), 200);
    });

    await tester.pumpWidget(_createScreen());
    await tester.pump();
    await tester.pump();
    await tester.pump();

    expect(find.text('Chat'), findsOneWidget);
    expect(find.text('Create first channel'), findsOneWidget);
  });
}
