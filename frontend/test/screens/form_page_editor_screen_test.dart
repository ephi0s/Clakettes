import 'dart:convert';
import 'package:flutter/material.dart' hide FormField;
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:clakettes/screens/form_page_editor_screen.dart';
import 'package:clakettes/services/api_service.dart';
import 'package:clakettes/models/form_definition_model.dart';
import 'test_helper.dart';

Widget _createEditor(FormDefinition form, FormPage page) {
  return wrapWithLocalization(FormPageEditorScreen(form: form, page: page));
}

void main() {
  setUp(() async {
    await setupApiTest();
  });

  testWidgets('testFormPageEditorScreenRenders', (tester) async {
    final form = sampleForm();
    final page = samplePage();

    ApiService().client = MockClient((request) async {
      return http.Response(
        json.encode(pageToApiJson(page)),
        200,
      );
    });

    await tester.pumpWidget(_createEditor(form, page));
    await tester.pump();
    await tester.pump();

    expect(find.text('Form Builder - Personal Info'), findsOneWidget);
    expect(find.text('Full Name'), findsWidgets);
    expect(find.text('Email'), findsWidgets);
    expect(find.text('Add Field'), findsOneWidget);
  });

  testWidgets('testFormPageEditorScreenAddField', (tester) async {
    final form = sampleForm();
    final page = samplePage();

    ApiService().client = MockClient((request) async {
      final uri = request.url.toString();
      if (request.method == 'PUT' && uri.contains('/pages/')) {
        return http.Response(json.encode(pageToApiJson(page)), 200);
      }
      return http.Response('{}', 200);
    });

    await tester.pumpWidget(_createEditor(form, page));
    await tester.pump();
    await tester.pump();

    expect(find.text('Add Field'), findsOneWidget);
  });

  testWidgets('testFormPageEditorScreenEditField', (tester) async {
    final form = sampleForm();
    final page = samplePage();
    final field = sampleField();

    ApiService().client = MockClient((request) async {
      final uri = request.url.toString();
      if (request.method == 'PUT' && uri.contains('/fields/')) {
        return http.Response(json.encode(fieldToApiJson(field)), 200);
      }
      return http.Response('{}', 200);
    });

    await tester.pumpWidget(_createEditor(form, page));
    await tester.pump();
    await tester.pump();

    await tester.tap(find.text('Full Name'));
    await tester.pump();
    await tester.pump();

    expect(find.text('Edit Field'), findsOneWidget);
    expect(find.text('Field Label'), findsOneWidget);
  });
}
