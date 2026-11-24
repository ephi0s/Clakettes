import 'dart:convert';
import 'package:material_ui/material_ui.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:clakettes/services/api_service.dart';
import 'package:clakettes/services/auth_service.dart';
import 'package:clakettes/widgets/markdown_text.dart';
import 'package:clakettes/widgets/publication_panel.dart';
import 'package:clakettes/widgets/reusable_widgets.dart';
import 'package:clakettes/widgets/rich_text_editor.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../screens/test_helper.dart';

Widget _createPanel() {
  return wrapWithLocalization(const PublicationPanel(scopeUserId: 1, canModerate: true, currentUserId: 1));
}

void main() {
  setUp(() async {
    SharedPreferences.setMockInitialValues({});
    await AuthService().clear();
    await setupApiTest();
  });

  testWidgets('publication panel renders posts with markdown and embed', (tester) async {
    ApiService().client = MockClient((request) async {
      return http.Response(
        json.encode({
          'items': [
            {
              'id': 1,
              'author_id': 1,
              'target_user_id': 1,
              'content': '# Novedad\nHello **world** ya disponible',
              'embed_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
              'embed_type': 'youtube',
              'allow_replies': true,
              'is_pinned': true,
              'is_hidden': false,
              'reply_count': 0,
              'created_at': '2026-01-01T00:00:00.000Z',
            },
          ],
          'total': 1,
          'pages': 1,
        }),
        200,
      );
    });

    await tester.pumpWidget(_createPanel());
    await tester.pump();
    await tester.pump();
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 100));

    expect(find.text('Novedad'), findsOneWidget);
    expect(find.text('Featured'), findsOneWidget);
    expect(find.textContaining('min read'), findsOneWidget);
    expect(find.byType(MarkdownText), findsWidgets);
    final bodies = tester.widgetList<MarkdownText>(find.byType(MarkdownText));
    expect(bodies.any((w) => w.data.contains('Hello')), isTrue);
    expect(find.text('YouTube'), findsOneWidget);
    expect(find.textContaining('User 1'), findsWidgets);
  });

  testWidgets('composer publishes the title as the first line', (tester) async {
    await AuthService().saveToken('test-token');
    String? postedContent;
    ApiService().client = MockClient((request) async {
      if (request.method == 'GET') {
        return http.Response(json.encode({'items': [], 'total': 0, 'pages': 0}), 200);
      }
      postedContent = json.decode(request.body)['content'] as String?;
      return http.Response(
        json.encode({
          'id': 2,
          'author_id': 1,
          'target_user_id': 1,
          'content': postedContent,
          'allow_replies': true,
          'created_at': '2026-01-01T00:00:00.000Z',
        }),
        201,
      );
    });

    await tester.pumpWidget(_createPanel());
    await tester.pump();
    await tester.pump();
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 100));

    expect(find.byType(SemanticTextField), findsOneWidget);
    await tester.enterText(find.byType(SemanticTextField), 'Mi título');
    await tester.pump();
    await tester.tap(find.text('Publish'));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 100));

    expect(postedContent, isNotNull);
    expect(plainTextFrom(postedContent!).trim(), 'Mi título');
  });

  testWidgets('publication panel shows empty state', (tester) async {
    ApiService().client = MockClient((request) async {
      return http.Response(json.encode({'items': [], 'total': 0, 'pages': 0}), 200);
    });

    await tester.pumpWidget(_createPanel());
    await tester.pump();
    await tester.pump();
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 100));

    expect(find.byType(PublicationPanel), findsOneWidget);
  });
}
