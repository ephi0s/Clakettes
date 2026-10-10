import 'dart:async';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'api_service.dart';

/// Monitoriza la conectividad de red y proporciona el estado online/offline en tiempo real.
///
/// Usa [connectivity_plus] para detectar cambios de red y realiza un ping de
/// health check contra el backend para confirmar conectividad real (no solo
/// un enlace de red local).
class ConnectivityMonitor {
  static final ConnectivityMonitor instance = ConnectivityMonitor._internal();

  factory ConnectivityMonitor({ApiService? api}) => instance;

  ConnectivityMonitor._internal() : _api = ApiService();

  final ApiService _api;
  final Connectivity _connectivity = Connectivity();
  final StreamController<bool> _controller = StreamController<bool>.broadcast();

  bool _isOnline = true;
  StreamSubscription? _subscription;

  /// Emite `true` cuando se restaura la conectividad, `false` cuando se pierde.
  Stream<bool> get onStatusChanged => _controller.stream;

  /// Estado online actual.
  bool get isOnline => _isOnline;

  /// Empieza a escuchar los cambios de conectividad.
  void start() {
    _subscription = _connectivity.onConnectivityChanged.listen(_onConnectivityChange);
  }

  /// Deja de escuchar y libera los recursos.
  void dispose() {
    _subscription?.cancel();
    _controller.close();
  }

  Future<void> _onConnectivityChange(List<ConnectivityResult> results) async {
    final hasConnection = results.any((r) => r != ConnectivityResult.none);

    if (!hasConnection) {
      _updateStatus(false);
      return;
    }

    // Connectivity+ says we have a link, but we still verify with a health check.
    final healthy = await _api.healthCheck();
    _updateStatus(healthy);
  }

  void _updateStatus(bool online) {
    if (_isOnline == online) return;
    _isOnline = online;
    _controller.add(online);
  }
}
