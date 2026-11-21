import 'dart:async';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'api_service.dart';
import 'node_service.dart';

class NodeHealth {
  final String domain;
  final bool online;
  final DateTime lastCheck;
  final int latencyMs;

  const NodeHealth({
    required this.domain,
    required this.online,
    required this.lastCheck,
    required this.latencyMs,
  });
}

/// Monitoriza la conectividad de red y mantiene la salud de cada nodo federado.
class ConnectivityMonitor {
  static final ConnectivityMonitor instance = ConnectivityMonitor._internal();

  factory ConnectivityMonitor({ApiService? api}) {
    final monitor = instance;
    if (api != null) monitor._apiOverride = api;
    return monitor;
  }

  ConnectivityMonitor._internal() : _api = ApiService();

  final ApiService _api;
  ApiService? _apiOverride;
  ApiService get _effectiveApi => _apiOverride ?? _api;

  final Connectivity _connectivity = Connectivity();
  final StreamController<bool> _controller = StreamController<bool>.broadcast();
  final Map<String, NodeHealth> _nodeHealth = <String, NodeHealth>{};

  bool _isOnline = true;
  StreamSubscription? _subscription;

  Stream<bool> get onStatusChanged => _controller.stream;

  bool get isOnline => _isOnline;

  Map<String, NodeHealth> get nodeHealth => Map<String, NodeHealth>.from(_nodeHealth);

  int get offlineNodeCount => _nodeHealth.values.where((h) => !h.online).length;

  int get onlineNodeCount => _nodeHealth.values.where((h) => h.online).length;

  bool get isDegraded => _nodeHealth.isNotEmpty && offlineNodeCount > 0 && onlineNodeCount > 0;

  void start() {
    _subscription = _connectivity.onConnectivityChanged.listen(_onConnectivityChange);
    checkNow();
  }

  Future<bool> checkNow() async {
    final api = _effectiveApi;
    bool healthy;
    try {
      healthy = await api.healthCheck();
    } catch (_) {
      healthy = false;
    }
    _isOnline = healthy;
    await _refreshNodeHealth(api);
    _emit();
    return healthy;
  }

  Future<void> _refreshNodeHealth(ApiService api) async {
    final nodes = NodeService().nodes;
    if (nodes.isEmpty) {
      final sw = Stopwatch()..start();
      bool ok;
      try {
        ok = await api.testNode(api.rootUrl);
      } catch (_) {
        ok = false;
      }
      sw.stop();
      _nodeHealth[api.rootUrl] = NodeHealth(
        domain: api.rootUrl,
        online: ok,
        lastCheck: DateTime.now(),
        latencyMs: sw.elapsedMilliseconds,
      );
      _nodeHealth.removeWhere((key, _) => key != api.rootUrl);
      return;
    }
    for (final node in nodes) {
      final sw = Stopwatch()..start();
      bool ok;
      try {
        ok = await api.testNode(node.effectiveUrl);
      } catch (_) {
        ok = false;
      }
      sw.stop();
      _nodeHealth[node.domain] = NodeHealth(
        domain: node.domain,
        online: ok,
        lastCheck: DateTime.now(),
        latencyMs: sw.elapsedMilliseconds,
      );
    }
    final domains = nodes.map((n) => n.domain).toSet();
    _nodeHealth.removeWhere((key, _) => !domains.contains(key));
  }

  Future<void> _onConnectivityChange(List<ConnectivityResult> results) async {
    final hasConnection = results.any((r) => r != ConnectivityResult.none);
    if (!hasConnection) {
      _isOnline = false;
      final now = DateTime.now();
      _nodeHealth.updateAll((key, value) => NodeHealth(
            domain: value.domain,
            online: false,
            lastCheck: now,
            latencyMs: value.latencyMs,
          ));
      _emit();
      return;
    }
    await checkNow();
  }

  void _emit() {
    if (!_controller.isClosed) _controller.add(_isOnline);
  }

  void dispose() {
    _subscription?.cancel();
    _controller.close();
  }
}
