import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:clakettes/main_scaffold.dart';
import 'package:clakettes/services/api_service.dart';
import 'package:clakettes/services/connectivity_monitor.dart';
import 'package:clakettes/services/node_info_model.dart';
import 'package:clakettes/services/node_service.dart';

class _FakeClient extends http.BaseClient {
  final Map<String, int> statuses;

  _FakeClient(this.statuses);

  @override
  Future<http.StreamedResponse> send(http.BaseRequest request) async {
    final status = statuses[request.url.host] ?? 200;
    return http.StreamedResponse(Stream<List<int>>.value(<int>[]), status);
  }
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  List<NodeInfo> twoNodes() => [
        const NodeInfo(id: 'a', domain: 'a.example', baseUrl: 'http://a.example:8000', isActive: true),
        const NodeInfo(id: 'b', domain: 'b.example', baseUrl: 'http://b.example:8000'),
      ];

  Future<ApiService> configureApi(Map<String, int> statuses, List<NodeInfo> nodes) async {
    SharedPreferences.setMockInitialValues({
      'backend_nodes': nodes.map((n) => jsonEncode(n.toJson())).toList(),
    });
    await NodeService().load();
    final api = ApiService();
    api.setClient(_FakeClient(statuses));
    return api;
  }

  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  group('ConnectivityMonitor', () {
    test('singleton returns same instance', () {
      final a = ConnectivityMonitor.instance;
      final b = ConnectivityMonitor.instance;
      expect(identical(a, b), isTrue);
    });

    test('isOnline defaults to true', () {
      final monitor = ConnectivityMonitor.instance;
      expect(monitor.isOnline, isTrue);
    });

    test('onStatusChanged stream is not null', () {
      final monitor = ConnectivityMonitor.instance;
      expect(monitor.onStatusChanged, isNotNull);
    });

    test('factory constructor forwards injected api', () {
      final api = ApiService();
      final monitor = ConnectivityMonitor(api: api);
      expect(identical(monitor, ConnectivityMonitor.instance), isTrue);
      expect(monitor.nodeHealth, isA<Map<String, NodeHealth>>());
    });
  });

  group('ConnectivityMonitor node health', () {
    test('checkNow builds per-node health with one node down', () async {
      final api = await configureApi({'a.example': 200, 'b.example': 500}, twoNodes());
      final monitor = ConnectivityMonitor(api: api);

      final result = await monitor.checkNow();

      expect(result, isTrue);
      expect(monitor.isOnline, isTrue);
      final health = monitor.nodeHealth;
      expect(health.keys, containsAll(<String>['a.example', 'b.example']));
      expect(health['a.example']!.online, isTrue);
      expect(health['b.example']!.online, isFalse);
      expect(health['b.example']!.lastCheck, isNotNull);
      expect(health['b.example']!.latencyMs, greaterThanOrEqualTo(0));
      expect(monitor.offlineNodeCount, 1);
      expect(monitor.onlineNodeCount, 1);
      expect(monitor.isDegraded, isTrue);
    });

    test('checkNow with all nodes down reports offline', () async {
      final api = await configureApi({'a.example': 500, 'b.example': 500}, twoNodes());
      final monitor = ConnectivityMonitor(api: api);

      final result = await monitor.checkNow();

      expect(result, isFalse);
      expect(monitor.isOnline, isFalse);
      expect(monitor.offlineNodeCount, 2);
      expect(monitor.onlineNodeCount, 0);
      expect(monitor.isDegraded, isFalse);
    });

    test('checkNow emits on onStatusChanged after updating the map', () async {
      final api = await configureApi({'a.example': 200, 'b.example': 500}, twoNodes());
      final monitor = ConnectivityMonitor(api: api);
      final emitted = <bool>[];
      final sub = monitor.onStatusChanged.listen(emitted.add);
      addTearDown(sub.cancel);

      await monitor.checkNow();
      await Future<void>.delayed(Duration.zero);

      expect(emitted, isNotEmpty);
      expect(emitted.last, isTrue);
      expect(monitor.nodeHealth['b.example']!.online, isFalse);
    });
  });

  testWidgets('degraded banner shows down node count and allows retry', (tester) async {
    var retried = false;
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: DegradedNodesBanner(
          downNodeCount: 2,
          offlineLabel: 'offline',
          retryLabel: 'retry',
          onRetry: () => retried = true,
        ),
      ),
    ));

    expect(find.text('2 offline'), findsOneWidget);
    await tester.tap(find.text('retry'));
    expect(retried, isTrue);
  });
}
