import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:clakettes/l10n/app_localizations.dart';
import 'package:clakettes/models/session_model.dart';
import 'package:clakettes/models/user_alias_model.dart';
import 'package:clakettes/widgets/user_profile_cards.dart';
import '../screens/test_helper.dart';

UserSession _session({int id = 1, bool isCurrent = false}) {
  final now = DateTime.now();
  return UserSession(
    id: id,
    userId: 1,
    deviceName: 'Test Device',
    ipAddress: '127.0.0.1',
    lastUsedAt: now,
    createdAt: now,
    expiresAt: now.add(const Duration(days: 30)),
    isCurrent: isCurrent,
  );
}

void main() {
  group('SessionsCard', () {
    testWidgets('renders session device name', (tester) async {
      await tester.pumpWidget(wrapWithLocalization(Builder(builder: (ctx) {
        return SessionsCard(
          l10n: AppLocalizations.of(ctx)!,
          sessions: [_session()],
          loading: false,
          onRevokeAll: () {},
          onRevoke: (_) async {},
        );
      })));
      await tester.pump();
      expect(find.text('Test Device'), findsOneWidget);
    });

    testWidgets('shows revoke-all when multiple sessions', (tester) async {
      await tester.pumpWidget(wrapWithLocalization(Builder(builder: (ctx) {
        return SessionsCard(
          l10n: AppLocalizations.of(ctx)!,
          sessions: [_session(id: 1), _session(id: 2)],
          loading: false,
          onRevokeAll: () {},
          onRevoke: (_) async {},
        );
      })));
      await tester.pump();
      expect(find.byIcon(Icons.logout), findsOneWidget);
    });
  });

  group('AliasesCard', () {
    testWidgets('renders alias text', (tester) async {
      await tester.pumpWidget(wrapWithLocalization(Builder(builder: (ctx) {
        return AliasesCard(
          l10n: AppLocalizations.of(ctx)!,
          aliases: [UserAlias(userId: 1, alias: 'Stage Name')],
          loading: false,
          canEdit: false,
          canAdd: false,
          onAdd: () {},
          onEdit: (_) async {},
          onDelete: (_) async {},
        );
      })));
      await tester.pump();
      expect(find.text('Stage Name'), findsOneWidget);
    });

    testWidgets('shows edit actions when canEdit', (tester) async {
      await tester.pumpWidget(wrapWithLocalization(Builder(builder: (ctx) {
        return AliasesCard(
          l10n: AppLocalizations.of(ctx)!,
          aliases: [UserAlias(userId: 1, alias: 'Stage Name')],
          loading: false,
          canEdit: true,
          canAdd: true,
          onAdd: () {},
          onEdit: (_) async {},
          onDelete: (_) async {},
        );
      })));
      await tester.pump();
      expect(find.byIcon(Icons.edit), findsOneWidget);
      expect(find.byIcon(Icons.delete_outline), findsOneWidget);
    });
  });
}
