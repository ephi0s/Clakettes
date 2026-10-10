import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:clakettes/screens/form_definitions_screen.dart';
import 'package:clakettes/services/api_service.dart';
import 'package:clakettes/models/form_definition_model.dart';
import 'test_helper.dart';

Widget _createScreen() {
  return wrapWithLocalization(const FormDefinitionsScreen());
}

void main() {
  setUp(() async {
    await setupApiTest();
  });

  testWidgets('testFormDefinitionsScreenRenders', (tester) async {
    ApiService().client = MockClient((request) async {
      return http.Response(
        json.encode({'items': [], 'total': 0, 'pages': 0}),
        200,
      );
    });

    await tester.pumpWidget(_createScreen());
    await tester.pump();
    await tester.pump();

    expect(find.text('Form Definitions'), findsOneWidget);
  });

  testWidgets('testFormDefinitionsScreenShowsForms', (tester) async {
    final forms = [
      sampleForm(id: 1, title: 'Festival Registration'),
      sampleForm(id: 2, title: 'User Creation', formType: FormType.userCreation),
    ];

    ApiService().client = MockClient((request) async {
      return http.Response(
        json.encode({
          'items': forms.map(formToApiJson).toList(),
          'total': 2,
          'pages': 1,
        }),
        200,
      );
    });

    await tester.pumpWidget(_createScreen());
    await tester.pump();
    await tester.pump();

    expect(find.text('Festival Registration'), findsOneWidget);
    expect(find.text('User Creation'), findsOneWidget);
  });

  testWidgets('testFormDefinitionsScreenTypeFilter', (tester) async {
    final formsAll = [
      sampleForm(id: 1, title: 'Festival Registration'),
      sampleForm(id: 2, title: 'User Creation', formType: FormType.userCreation),
    ];

    ApiService().client = MockClient((request) async {
      final uri = request.url.toString();
      if (uri.contains('form_type=')) {
        final filtered = formsAll.where((f) => uri.contains(f.formType)).toList();
        return http.Response(
          json.encode({
            'items': filtered.map(formToApiJson).toList(),
            'total': filtered.length,
            'pages': 1,
          }),
          200,
        );
      }
      return http.Response(
        json.encode({
          'items': formsAll.map(formToApiJson).toList(),
          'total': formsAll.length,
          'pages': 1,
        }),
        200,
      );
    });

    await tester.pumpWidget(_createScreen());
    await tester.pump();
    await tester.pump();

    expect(find.text('Festival Registration'), findsOneWidget);
    expect(find.text('User Creation'), findsOneWidget);

    await tester.tap(find.text('All'));
    await tester.pump();
    await tester.pump();

    expect(find.text('Festival registration'), findsOneWidget);
  });

  testWidgets('testFormDefinitionsScreenCreateForm', (tester) async {
    ApiService().client = MockClient((request) async {
      final uri = request.url.toString();
      if (request.method == 'GET') {
        return http.Response(
          json.encode({'items': [], 'total': 0, 'pages': 0}),
          200,
        );
      }
      if (request.method == 'POST' && uri.endsWith('/forms/')) {
        return http.Response(
          json.encode(formToApiJson(sampleForm())),
          200,
        );
      }
      return http.Response('{}', 200);
    });

    await tester.pumpWidget(_createScreen());
    await tester.pump();
    await tester.pump();

    await tester.tap(find.byType(FloatingActionButton));
    await tester.pump();
    await tester.pump();

    expect(find.text('New Form'), findsOneWidget);
  });

  testWidgets('testFormDefinitionsScreenDeleteForm', (tester) async {
    final form = sampleForm(id: 1, title: 'Festival Registration', isActive: true);

    ApiService().client = MockClient((request) async {
      if (request.method == 'GET') {
        return http.Response(
          json.encode({
            'items': [formToApiJson(form)],
            'total': 1,
            'pages': 1,
          }),
          200,
        );
      }
      return http.Response('{}', 200);
    });

    await tester.pumpWidget(_createScreen());
    await tester.pump();
    await tester.pump();

    expect(find.text('Festival Registration'), findsOneWidget);

    final popup = find.byType(PopupMenuButton<String>);
    expect(popup, findsOneWidget);
  });
}
