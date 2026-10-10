import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:clakettes/main.dart';
import 'package:clakettes/services/database_service.dart';
import 'package:clakettes/services/offline_cache_service.dart';
import 'package:clakettes/services/sync_queue_service.dart';
import 'package:clakettes/services/connectivity_monitor.dart';
import 'package:clakettes/services/locale_service.dart';
import 'package:clakettes/main_scaffold.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  setUpAll(() async {
    MainScaffold.skipBackendCheck = true;
    await DatabaseService.init();
    await OfflineCacheService.instance.init();
    await SyncQueueService.instance.init();
    ConnectivityMonitor.instance.start();
    await LocaleService.instance.load();
  });

  group('App Integration Tests', () {
    testWidgets('renders AppBar and navigation tabs', (tester) async {
      await tester.pumpWidget(const ClakettesApp());
      await tester.pump();

      expect(find.byType(AppBar), findsOneWidget);
      expect(
        find.byWidgetPredicate((w) => w is NavigationBar || w is NavigationRail),
        findsOneWidget,
      );
    });

    testWidgets('shows Dashboard and Festivals when not logged in', (tester) async {
      await tester.pumpWidget(const ClakettesApp());
      await tester.pump();

      expect(find.text('Dashboard'), findsWidgets);
      expect(find.text('Festivals'), findsOneWidget);
    });

    testWidgets('shows login button when not logged in', (tester) async {
      await tester.pumpWidget(const ClakettesApp());
      await tester.pump();

      expect(find.text('Log In'), findsWidgets);
    });

    testWidgets('navigation switches to Festivals tab', (tester) async {
      await tester.pumpWidget(const ClakettesApp());
      await tester.pump();

      await tester.tap(find.text('Festivals'));
      await tester.pump();

      expect(find.text('Festivals'), findsWidgets);
    });

    testWidgets('search dialog opens and closes', (tester) async {
      await tester.pumpWidget(const ClakettesApp());
      await tester.pump();

      await tester.tap(find.byIcon(Icons.search_rounded));
      await tester.pump();

      expect(find.byType(AlertDialog), findsOneWidget);

      await tester.tap(find.text('Close'));
      await tester.pump();

      expect(find.byType(AlertDialog), findsNothing);
    });
  });
}
