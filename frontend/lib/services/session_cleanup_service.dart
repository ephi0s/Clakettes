import 'package:flutter/foundation.dart';
import 'package:hive/hive.dart';
import 'auth_service.dart';
import 'chat_backend/chat_service.dart';
import 'offline_cache_service.dart';
import 'sync_queue_service.dart';

/// Cierre de sesión centralizado: credenciales, caché, cola, Hive y socket de chat.
class SessionCleanupService {
  static const List<String> userBoxes = ['users', 'messages', 'festivals', 'shortfilms'];

  /// Limpia toda la información local de la sesión actual.
  ///
  /// Las cajas se vacían sin cerrarlas para que el resto de la app pueda
  /// seguir usándolas tras el logout. Cualquier fallo se ignora.
  static Future<void> logout() async {
    await AuthService().clear();

    try {
      await ChatService.disconnectAll();
    } catch (e) {
      debugPrint('[SessionCleanup] chat disconnect error: $e');
    }

    try {
      await OfflineCacheService.instance.clear();
      await SyncQueueService.instance.clear();
    } catch (e) {
      debugPrint('[SessionCleanup] cache clear error: $e');
    }

    for (final name in userBoxes) {
      try {
        final box = Hive.isBoxOpen(name) ? Hive.box(name) : await Hive.openBox(name);
        await box.clear();
      } catch (e) {
        debugPrint('[SessionCleanup] box $name clear error: $e');
      }
    }
  }
}
