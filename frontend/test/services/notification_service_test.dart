import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:timezone/data/latest_all.dart' as tz_data;
import 'package:timezone/timezone.dart' as tz;
import 'package:clakettes/models/event_model.dart';
import 'package:clakettes/services/notification_service.dart';

class MockNotifications extends Mock implements FlutterLocalNotificationsPlugin {}

void main() {
  late MockNotifications mock;

  setUp(() {
    tz_data.initializeTimeZones();
    tz.setLocalLocation(tz.getLocation('UTC'));
    registerFallbackValue(0);
    registerFallbackValue(tz.TZDateTime.now(tz.UTC));
    registerFallbackValue(const NotificationDetails());
    registerFallbackValue(AndroidScheduleMode.inexactAllowWhileIdle);
    mock = MockNotifications();
    when(() => mock.zonedSchedule(
          id: any(named: 'id'),
          title: any(named: 'title'),
          body: any(named: 'body'),
          scheduledDate: any(named: 'scheduledDate'),
          notificationDetails: any(named: 'notificationDetails'),
          androidScheduleMode: any(named: 'androidScheduleMode'),
        )).thenAnswer((_) async {});
    when(() => mock.cancel(id: any(named: 'id'))).thenAnswer((_) async {});
    NotificationService.resetForTesting(mock);
  });

  tearDown(resetMocktailState);

  FestivalEvent eventWith({int? id = 42, DateTime? start}) {
    return FestivalEvent(
      id: id,
      festivalId: 1,
      title: 'Gala Night',
      startDate: start ?? DateTime.now().add(const Duration(hours: 2)),
    );
  }

  group('scheduleReminder', () {
    test('schedules a reminder 30 minutes before a future event', () async {
      final start = DateTime.now().add(const Duration(hours: 2));
      final expected =
          tz.TZDateTime.from(start.subtract(const Duration(minutes: 30)), tz.UTC);

      await NotificationService.instance.scheduleReminder(eventWith(start: start));

      verify(() => mock.zonedSchedule(
            id: 42,
            title: 'Event reminder',
            body: 'Gala Night starts in 30 minutes',
            scheduledDate: expected,
            notificationDetails: any(named: 'notificationDetails'),
            androidScheduleMode: AndroidScheduleMode.inexactAllowWhileIdle,
          )).called(1);
      expect(NotificationService.instance.scheduledIds, {42});
    });

    test('does not schedule past events', () async {
      final past = DateTime.now().subtract(const Duration(days: 1));

      await NotificationService.instance.scheduleReminder(eventWith(start: past));

      verifyNever(() => mock.zonedSchedule(
            id: any(named: 'id'),
            title: any(named: 'title'),
            body: any(named: 'body'),
            scheduledDate: any(named: 'scheduledDate'),
            notificationDetails: any(named: 'notificationDetails'),
            androidScheduleMode: any(named: 'androidScheduleMode'),
          ));
      expect(NotificationService.instance.scheduledIds, isEmpty);
    });

    test('does not schedule events without an id', () async {
      await NotificationService.instance.scheduleReminder(eventWith(id: null));

      verifyNever(() => mock.zonedSchedule(
            id: any(named: 'id'),
            title: any(named: 'title'),
            body: any(named: 'body'),
            scheduledDate: any(named: 'scheduledDate'),
            notificationDetails: any(named: 'notificationDetails'),
            androidScheduleMode: any(named: 'androidScheduleMode'),
          ));
    });
  });

  group('cancelReminder', () {
    test('cancels the scheduled reminder', () async {
      await NotificationService.instance.scheduleReminder(eventWith());
      expect(NotificationService.instance.scheduledIds, {42});

      await NotificationService.instance.cancelReminder(eventWith());

      verify(() => mock.cancel(id: 42)).called(1);
      expect(NotificationService.instance.scheduledIds, isEmpty);
    });
  });

  group('rescheduleAll', () {
    test('schedules missing, keeps existing and cancels removed', () async {
      final event = eventWith();

      await NotificationService.instance.rescheduleAll([event]);
      verify(() => mock.zonedSchedule(
            id: 42,
            title: 'Event reminder',
            body: 'Gala Night starts in 30 minutes',
            scheduledDate: any(named: 'scheduledDate'),
            notificationDetails: any(named: 'notificationDetails'),
            androidScheduleMode: AndroidScheduleMode.inexactAllowWhileIdle,
          )).called(1);
      expect(NotificationService.instance.scheduledIds, {42});

      clearInteractions(mock);
      await NotificationService.instance.rescheduleAll([event]);
      verifyNever(() => mock.zonedSchedule(
            id: 42,
            title: 'Event reminder',
            body: 'Gala Night starts in 30 minutes',
            scheduledDate: any(named: 'scheduledDate'),
            notificationDetails: any(named: 'notificationDetails'),
            androidScheduleMode: AndroidScheduleMode.inexactAllowWhileIdle,
          ));
      verifyNever(() => mock.cancel(id: 42));
      expect(NotificationService.instance.scheduledIds, {42});

      clearInteractions(mock);
      await NotificationService.instance.rescheduleAll([]);
      verify(() => mock.cancel(id: 42)).called(1);
      expect(NotificationService.instance.scheduledIds, isEmpty);

      clearInteractions(mock);
      await NotificationService.instance.rescheduleAll([event]);
      verify(() => mock.zonedSchedule(
            id: 42,
            title: 'Event reminder',
            body: 'Gala Night starts in 30 minutes',
            scheduledDate: any(named: 'scheduledDate'),
            notificationDetails: any(named: 'notificationDetails'),
            androidScheduleMode: AndroidScheduleMode.inexactAllowWhileIdle,
          )).called(1);
    });
  });
}
