import 'dart:convert';
import 'package:flutter/material.dart' hide FormField;
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:clakettes/screens/public_form_screen.dart';
import 'package:clakettes/services/api_service.dart';
import 'package:clakettes/models/form_definition_model.dart';
import 'test_helper.dart';

Widget _createScreen(String token) {
  return wrapWithLocalization(PublicFormScreen(token: token));
}

FormDefinition _publicForm() {
  return FormDefinition(
    id: 1,
    title: 'Festival Registration',
    description: 'Register for the festival',
    formType: FormType.festivalRegistration,
    isActive: true,
    isPublic: true,
    sortOrder: 0,
    pages: [
      FormPage(
        id: 1,
        formId: 1,
        title: 'Personal Info',
        sortOrder: 0,
        fields: [
          FormField(
            id: 1,
            pageId: 1,
            fieldType: FormFieldType.string,
            label: 'Full Name',
            isRequired: true,
            sortOrder: 0,
          ),
          FormField(
            id: 2,
            pageId: 1,
            fieldType: FormFieldType.email,
            label: 'Email',
            isRequired: true,
            sortOrder: 1,
          ),
          FormField(
            id: 3,
            pageId: 1,
            fieldType: FormFieldType.boolean,
            label: 'Accept Terms',
            isRequired: true,
            sortOrder: 2,
          ),
        ],
      ),
    ],
  );
}

void main() {
  setUp(() async {
    await setupApiTest();
  });

  testWidgets('testPublicFormScreenRenders', (tester) async {
    ApiService().client = MockClient((request) async {
      final uri = request.url.toString();
      if (uri.contains('/forms/public/')) {
        return http.Response(json.encode(formToApiJson(_publicForm())), 200);
      }
      return http.Response('{}', 200);
    });

    await tester.pumpWidget(_createScreen('test-token'));
    await tester.pump();
    await tester.pump();

    expect(find.text('Festival Registration'), findsOneWidget);
    expect(find.text('Register for the festival'), findsOneWidget);
    expect(find.text('Personal Info'), findsOneWidget);
    expect(find.text('Full Name'), findsOneWidget);
    expect(find.text('Email'), findsOneWidget);
    expect(find.text('Accept Terms'), findsOneWidget);
    expect(find.text('Submit'), findsOneWidget);
  });

  testWidgets('testPublicFormScreenSubmit', (tester) async {
    ApiService().client = MockClient((request) async {
      final uri = request.url.toString();
      if (uri.contains('/forms/public/') && request.method == 'GET') {
        return http.Response(json.encode(formToApiJson(_publicForm())), 200);
      }
      if (uri.contains('/submit') && request.method == 'POST') {
        return http.Response(
          json.encode(responseToApiJson(sampleResponse())),
          200,
        );
      }
      return http.Response('{}', 200);
    });

    await tester.pumpWidget(_createScreen('test-token'));
    await tester.pump();
    await tester.pump();

    await tester.enterText(find.byType(TextFormField).at(0), 'John Doe');
    await tester.pump();
    await tester.enterText(find.byType(TextFormField).at(1), 'john@example.com');
    await tester.pump();

    await tester.tap(find.text('Submit'));
    await tester.pump();
    await tester.pump();

    expect(find.text('Form submitted successfully'), findsOneWidget);
  });

  testWidgets('testPublicFormScreenValidation', (tester) async {
    ApiService().client = MockClient((request) async {
      final uri = request.url.toString();
      if (uri.contains('/forms/public/') && request.method == 'GET') {
        return http.Response(json.encode(formToApiJson(_publicForm())), 200);
      }
      return http.Response('{}', 200);
    });

    await tester.pumpWidget(_createScreen('test-token'));
    await tester.pump();
    await tester.pump();

    await tester.tap(find.text('Submit'));
    await tester.pump();
    await tester.pump();

    expect(find.text('This field is required'), findsWidgets);
  });
}
