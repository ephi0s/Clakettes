import 'package:flutter/foundation.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:flutter_timezone/flutter_timezone.dart';
import 'package:timezone/data/latest_all.dart' as tz_data;
import 'package:timezone/timezone.dart' as tz;
import '../l10n/app_localizations.dart';
import '../models/event_model.dart';
import 'notification_platform.dart' as webnotify;

/// Servicio singleton que programa recordatorios de eventos 30 minutos antes.
///
/// Estrategia por plataforma (sin Firebase ni proveedores externos):
/// - Escritorio (Windows/macOS/Linux): [flutter_local_notifications] con
///   `zonedSchedule` (notificaciones del SO con la app instalada).
/// - Web: Notification API nativa del navegador mediante temporizadores
///   (requiere permiso y pestaña abierta; ver `notification_web.dart`).
/// - Móvil (Android/iOS): sin soporte por decisión de producto; [init]
///   marca como no soportado y programar no hace nada.
class NotificationService {
  /// Permite inyectar un plugin (p. ej. en tests).
  NotificationService({FlutterLocalNotificationsPlugin? plugin})
      : _plugin = plugin ?? FlutterLocalNotificationsPlugin();

  static final NotificationService _instance = NotificationService();

  /// Instancia global del servicio.
  static NotificationService get instance => _instance;

  /// Sustituye el plugin interno y reinicia el estado (solo para tests).
  ///
  /// Al inyectar un plugin mockeado se considera el servicio inicializado
  /// para poder ejercitar la lógica de programación sin plataforma real.
  @visibleForTesting
  static void resetForTesting(FlutterLocalNotificationsPlugin plugin) {
    _instance._plugin = plugin;
    _instance._initialized = true;
    _instance._supported = true;
    _instance._l10n = null;
    _instance._location = null;
    _instance._scheduledIds.clear();
  }

  FlutterLocalNotificationsPlugin _plugin;
  bool _initialized = false;

  /// True cuando la plataforma real soporta avisos (escritorio y web;
  /// móvil no por decisión de producto). Los tests lo fuerzan a true.
  bool _supported = true;

  /// Indica si la plataforma actual emite recordatorios.
  static bool get _isMobile =>
      !kIsWeb &&
      (defaultTargetPlatform == TargetPlatform.android ||
          defaultTargetPlatform == TargetPlatform.iOS ||
          defaultTargetPlatform == TargetPlatform.fuchsia);
  tz.Location? _location;
  AppLocalizations? _l10n;
  final Set<int> _scheduledIds = <int>{};

  static const int _reminderMinutes = 30;

  /// Inicializa el plugin y el huso horario local. Idempotente.
  Future<void> init({AppLocalizations? l10n}) async {
    _l10n = l10n;
    if (_initialized) return;
    if (_isMobile) {
      _supported = false;
      _initialized = true;
      return;
    }
    if (kIsWeb) {
      _supported = await webnotify.requestWebNotificationPermission();
      _initialized = true;
      return;
    }
    _initialized = true;

    try {
      tz_data.initializeTimeZones();
      final timezoneInfo = await FlutterTimezone.getLocalTimezone();
      _location = tz.getLocation(timezoneInfo.identifier);
    } catch (e) {
      debugPrint('NotificationService timezone error: $e');
    }

    const android = AndroidInitializationSettings('@mipmap/ic_launcher');
    const darwin = DarwinInitializationSettings(
      requestAlertPermission: false,
      requestSoundPermission: false,
      requestBadgePermission: false,
    );
    const windows = WindowsInitializationSettings(
      appName: 'Clakettes',
      appUserModelId: 'com.example.clakettes',
      guid: '24b1f4e0-6c3a-4d5e-9f8a-1b2c3d4e5f60',
    );
    const linux = LinuxInitializationSettings(defaultActionName: 'Clakettes');
    const settings = InitializationSettings(
      android: android,
      iOS: darwin,
      macOS: darwin,
      windows: windows,
      linux: linux,
    );

    try {
      await _plugin.initialize(settings: settings);
    } catch (e) {
      debugPrint('NotificationService init error: $e');
    }

    try {
      final macos = _plugin.resolvePlatformSpecificImplementation<MacOSFlutterLocalNotificationsPlugin>();
      await macos?.requestPermissions();
    } catch (e) {
      debugPrint('NotificationService macOS permission error: $e');
    }
  }

  /// Detalles Android con el canal de recordatorios localizado.
  AndroidNotificationDetails _androidDetails() {
    final channelName = _l10n?.notificationChannelName ?? 'Event reminders';
    final channelDescription =
        _l10n?.notificationChannelDescription ?? 'Reminders before festival events';
    return AndroidNotificationDetails(
      'event_reminders',
      channelName,
      channelDescription: channelDescription,
      importance: Importance.high,
      priority: Priority.high,
    );
  }

  /// Programa un recordatorio para [event] si tiene id y fecha futura.
  ///
  /// En web usa la Notification API del navegador; en escritorio el plugin
  /// programado; en móvil no hace nada (ver [_supported]).
  Future<void> scheduleReminder(FestivalEvent event) async {
    if (!_initialized || !_supported) return;
    final id = event.id;
    final start = event.startDate;
    if (id == null || start == null || !start.isAfter(DateTime.now())) return;

    final title = _l10n?.eventReminderTitle ?? 'Event reminder';
    final body = _l10n?.eventReminderBody(event.title) ?? '${event.title} starts in 30 minutes';

    if (kIsWeb) {
      final fireTime = start.subtract(const Duration(minutes: _reminderMinutes));
      if (!fireTime.isAfter(DateTime.now())) return;
      webnotify.scheduleWebNotification(id: id, fireTime: fireTime, title: title, body: body);
      _scheduledIds.add(id);
      return;
    }

    try {
      final fireTime = _fireTime(start);
      if (!fireTime.isAfter(tz.TZDateTime.now(_location ?? tz.UTC))) return;

      final details = NotificationDetails(
        android: _androidDetails(),
        iOS: const DarwinNotificationDetails(),
        macOS: const DarwinNotificationDetails(),
      );

      await _plugin.zonedSchedule(
        id: id,
        title: title,
        body: body,
        scheduledDate: fireTime,
        notificationDetails: details,
        androidScheduleMode: AndroidScheduleMode.inexactAllowWhileIdle,
      );
      _scheduledIds.add(id);
    } catch (e) {
      debugPrint('NotificationService schedule error: $e');
    }
  }

  /// Cancela el recordatorio programado para [event].
  Future<void> cancelReminder(FestivalEvent event) async {
    if (!_initialized) return;
    final id = event.id;
    if (id == null) return;
    await _cancelId(id);
    _scheduledIds.remove(id);
  }

  /// Cancela en el plugin y en el programador web (el no soportado ignora).
  Future<void> _cancelId(int id) async {
    webnotify.cancelWebNotification(id);
    try {
      await _plugin.cancel(id: id);
    } catch (e) {
      debugPrint('NotificationService cancel error: $e');
    }
  }

  /// Reconciliación determinista: cancela recordatorios de eventos que ya no
  /// existen y programa los que faltan. Usa `now` inyectable para los tests.
  Future<void> rescheduleAll(List<FestivalEvent> events, {DateTime? now}) async {
    if (!_initialized) return;
    final reference = now ?? DateTime.now();
    final validIds = <int>{};
    for (final event in events) {
      final id = event.id;
      if (id == null) continue;
      final start = event.startDate;
      if (start == null || !start.isAfter(reference)) continue;
      if (_scheduledIds.contains(id)) {
        validIds.add(id);
        continue;
      }
      await scheduleReminder(event);
      if (_scheduledIds.contains(id)) validIds.add(id);
    }
    for (final id in List<int>.from(_scheduledIds)) {
      if (!validIds.contains(id)) {
        await _cancelId(id);
        _scheduledIds.remove(id);
      }
    }
  }

  /// Conjunto de ids con recordatorio programado (solo para tests).
  @visibleForTesting
  Set<int> get scheduledIds => Set<int>.from(_scheduledIds);

  /// Momento de disparo del recordatorio: 30 minutos antes de [start].
  tz.TZDateTime _fireTime(DateTime start) {
    return tz.TZDateTime.from(
      start.subtract(const Duration(minutes: _reminderMinutes)),
      _location ?? tz.UTC,
    );
  }
}
