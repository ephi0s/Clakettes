import 'package:flutter_test/flutter_test.dart';
import 'package:clakettes/models/session_model.dart';

void main() {
  group('UserSession', () {
    final json = <String, dynamic>{
      'id': 1,
      'user_id': 1,
      'device_name': 'Chrome Windows',
      'ip_address': '192.168.1.1',
      'user_agent': 'Mozilla/5.0',
      'last_used_at': '2026-06-01T12:00:00.000Z',
      'created_at': '2026-01-01T00:00:00.000Z',
      'expires_at': '2026-07-01T00:00:00.000Z',
      'is_active': true,
    };

    test('fromJson creates correct object', () {
      final s = UserSession.fromJson(json);

      expect(s.id, equals(1));
      expect(s.userId, equals(1));
      expect(s.deviceName, equals('Chrome Windows'));
      expect(s.ipAddress, equals('192.168.1.1'));
      expect(s.userAgent, equals('Mozilla/5.0'));
      expect(s.lastUsedAt, equals(DateTime.utc(2026, 6, 1, 12)));
      expect(s.createdAt, equals(DateTime.utc(2026, 1, 1)));
      expect(s.expiresAt, equals(DateTime.utc(2026, 7, 1)));
      expect(s.isActive, isTrue);
    });

    test('fromJson handles null values with defaults', () {
      final minimal = <String, dynamic>{
        'id': 2,
        'user_id': 3,
        'last_used_at': '2026-06-01T00:00:00.000Z',
        'created_at': '2026-01-01T00:00:00.000Z',
        'expires_at': '2026-07-01T00:00:00.000Z',
      };

      final s = UserSession.fromJson(minimal);

      expect(s.id, equals(2));
      expect(s.userId, equals(3));
      expect(s.deviceName, isEmpty);
      expect(s.ipAddress, isEmpty);
      expect(s.userAgent, isEmpty);
      expect(s.isActive, isTrue);
    });
  });
}
