import 'package:flutter_test/flutter_test.dart';
import 'package:clakettes/models/notification_model.dart';

void main() {
  group('AppNotification', () {
    final json = <String, dynamic>{
      'id': 1,
      'user_id': 1,
      'title': 'New Message',
      'message': 'You have a new message',
      'notification_type': 'message',
      'is_read': false,
      'related_user_id': 2,
      'created_at': '2026-01-01T00:00:00.000Z',
    };

    test('fromJson creates correct object', () {
      final notif = AppNotification.fromJson(json);

      expect(notif.id, equals(1));
      expect(notif.userId, equals(1));
      expect(notif.title, equals('New Message'));
      expect(notif.message, equals('You have a new message'));
      expect(notif.notificationType, equals('message'));
      expect(notif.isRead, isFalse);
      expect(notif.relatedUserId, equals(2));
      expect(notif.createdAt, equals(DateTime.utc(2026, 1, 1)));
    });

    test('toJson returns correct snake_case map', () {
      final notif = AppNotification(
        id: 1,
        userId: 1,
        title: 'New Message',
        message: 'You have a new message',
        notificationType: 'message',
        isRead: false,
        relatedUserId: 2,
        createdAt: DateTime.utc(2026, 1, 1),
      );

      final map = notif.toJson();

      expect(map['id'], equals(1));
      expect(map['user_id'], equals(1));
      expect(map['title'], equals('New Message'));
      expect(map['message'], equals('You have a new message'));
      expect(map['notification_type'], equals('message'));
      expect(map['is_read'], isFalse);
      expect(map['related_user_id'], equals(2));
    });

    test('fromJson handles null values with defaults', () {
      final minimal = <String, dynamic>{
        'id': 2,
        'user_id': 3,
        'title': 'Test',
        'message': 'Test body',
      };

      final notif = AppNotification.fromJson(minimal);

      expect(notif.id, equals(2));
      expect(notif.userId, equals(3));
      expect(notif.title, equals('Test'));
      expect(notif.message, equals('Test body'));
      expect(notif.notificationType, equals('profile_update'));
      expect(notif.isRead, isFalse);
      expect(notif.relatedUserId, isNull);
      expect(notif.createdAt, isNull);
    });
  });
}
