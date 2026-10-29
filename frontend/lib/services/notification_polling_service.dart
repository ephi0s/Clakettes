import 'dart:async';
import 'package:flutter/foundation.dart';
import 'api_service.dart';

/// Servicio singleton que sondea el conteo de notificaciones no leídas
/// periódicamente (polling) mientras la app está en primer plano.
class NotificationPollingService {
  NotificationPollingService._();
  static final NotificationPollingService instance = NotificationPollingService._();

  final ApiService _api = ApiService();
  Timer? _timer;
  int _unread = 0;
  final ValueNotifier<int> unreadCount = ValueNotifier<int>(0);

  void start({Duration interval = const Duration(seconds: 60)}) {
    stop();
    _poll();
    _timer = Timer.periodic(interval, (_) => _poll());
  }

  void stop() {
    _timer?.cancel();
    _timer = null;
  }

  Future<void> _poll() async {
    try {
      final count = await _api.getUnreadNotificationCount();
      _unread = count;
      unreadCount.value = count;
    } catch (_) {
      // Silently ignore network errors during polling
    }
  }

  int get unread => _unread;
}