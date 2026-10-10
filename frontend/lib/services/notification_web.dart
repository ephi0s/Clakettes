import 'dart:async';
import 'dart:js_interop';
import 'package:web/web.dart' as web;

/// Primitivas de notificación del navegador (Notification API).
///
/// Sin dependencias externas: usa la API nativa del navegador. Los avisos
/// solo se muestran con la pestaña abierta (sin Service Worker ni servidor
/// push); al cerrar la pestaña los temporizadores pendientes se pierden.

/// Pide permiso de notificación al navegador. Devuelve true si concedido.
Future<bool> requestWebNotificationPermission() async {
  try {
    if (web.Notification.permission == 'granted') return true;
    if (web.Notification.permission == 'denied') return false;
    final result = await web.Notification.requestPermission().toDart;
    return result == 'granted';
  } catch (_) {
    return false;
  }
}

final Map<int, Timer> _webTimers = <int, Timer>{};

/// Programa un aviso nativo para [fireTime] (reprograma si ya existía).
void scheduleWebNotification({
  required int id,
  required DateTime fireTime,
  required String title,
  required String body,
}) {
  cancelWebNotification(id);
  final delay = fireTime.difference(DateTime.now());
  if (delay.isNegative) return;
  _webTimers[id] = Timer(delay, () {
    _webTimers.remove(id);
    try {
      web.Notification(title, web.NotificationOptions(body: body));
    } catch (_) {}
  });
}

/// Cancela el aviso programado con [id], si existe.
void cancelWebNotification(int id) {
  _webTimers.remove(id)?.cancel();
}

/// Cancela todos los avisos programados (p. ej. al cerrar sesión).
void clearWebNotifications() {
  for (final timer in _webTimers.values) {
    timer.cancel();
  }
  _webTimers.clear();
}
