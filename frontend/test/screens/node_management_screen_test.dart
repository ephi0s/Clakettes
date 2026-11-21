import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:clakettes/screens/node_management_screen.dart';
import 'package:clakettes/services/connectivity_monitor.dart';

void main() {
  Widget buildRow(NodeHealth? health, {required void Function() onRetry}) {
    return MaterialApp(
      home: Scaffold(
        body: NodeHealthRow(
          health: health,
          onlineLabel: 'online',
          offlineLabel: 'offline',
          retryTooltip: 'retry',
          onRetry: onRetry,
        ),
      ),
    );
  }

  testWidgets('node health row updates when monitor state changes', (tester) async {
    var retries = 0;
    final offline = NodeHealth(
      domain: 'a.example',
      online: false,
      lastCheck: DateTime(2026, 1, 1, 10, 30, 5),
      latencyMs: 17,
    );

    await tester.pumpWidget(buildRow(offline, onRetry: () => retries++));
    expect(find.text('offline'), findsOneWidget);
    expect(find.text('online'), findsNothing);
    expect(find.textContaining('17 ms'), findsOneWidget);

    final online = NodeHealth(
      domain: 'a.example',
      online: true,
      lastCheck: DateTime(2026, 1, 1, 10, 31, 12),
      latencyMs: 42,
    );
    await tester.pumpWidget(buildRow(online, onRetry: () => retries++));
    expect(find.text('online'), findsOneWidget);
    expect(find.text('offline'), findsNothing);
    expect(find.textContaining('42 ms'), findsOneWidget);

    await tester.tap(find.byTooltip('retry'));
    expect(retries, 1);
  });

  testWidgets('node health row handles missing health data', (tester) async {
    await tester.pumpWidget(buildRow(null, onRetry: () {}));
    expect(find.text('offline'), findsOneWidget);
    expect(find.textContaining('ms'), findsNothing);
  });
}
