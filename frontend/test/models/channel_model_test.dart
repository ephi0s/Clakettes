import 'package:flutter_test/flutter_test.dart';
import 'package:clakettes/models/channel_model.dart';

void main() {
  group('Channel', () {
    final json = <String, dynamic>{
      'id': 1,
      'name': 'general',
      'description': 'General chat',
      'channel_type': 'community',
      'max_members': 100,
      'created_by': 1,
      'is_active': true,
      'created_at': '2026-01-01T00:00:00.000Z',
      'updated_at': '2026-06-01T00:00:00.000Z',
    };

    test('fromJson creates correct object', () {
      final c = Channel.fromJson(json);

      expect(c.id, equals(1));
      expect(c.name, equals('general'));
      expect(c.description, equals('General chat'));
      expect(c.channelType, equals('community'));
      expect(c.maxMembers, equals(100));
      expect(c.createdBy, equals(1));
      expect(c.isActive, isTrue);
      expect(c.createdAt, equals(DateTime.utc(2026, 1, 1)));
      expect(c.updatedAt, equals(DateTime.utc(2026, 6, 1)));
    });

    test('toJson returns correct snake_case map', () {
      final c = Channel(
        id: 1,
        name: 'general',
        description: 'General chat',
        channelType: 'community',
        maxMembers: 100,
        createdBy: 1,
        isActive: true,
        createdAt: DateTime.utc(2026, 1, 1),
        updatedAt: DateTime.utc(2026, 6, 1),
      );

      final map = c.toJson();

      expect(map['id'], equals(1));
      expect(map['name'], equals('general'));
      expect(map['description'], equals('General chat'));
      expect(map['channel_type'], equals('community'));
      expect(map['max_members'], equals(100));
      expect(map['created_by'], equals(1));
      expect(map['is_active'], isTrue);
    });

    test('fromJson handles null values', () {
      final minimal = <String, dynamic>{
        'name': 'random',
        'created_by': 2,
      };

      final c = Channel.fromJson(minimal);

      expect(c.id, isNull);
      expect(c.name, equals('random'));
      expect(c.description, isNull);
      expect(c.channelType, equals('community'));
      expect(c.maxMembers, isNull);
      expect(c.createdBy, equals(2));
      expect(c.isActive, isTrue);
      expect(c.createdAt, isNull);
      expect(c.updatedAt, isNull);
    });
  });

  group('ChannelMember', () {
    final json = <String, dynamic>{
      'id': 1,
      'channel_id': 1,
      'user_id': 1,
      'role': 'admin',
      'is_active': true,
      'joined_at': '2026-01-15T00:00:00.000Z',
    };

    test('fromJson creates correct object', () {
      final m = ChannelMember.fromJson(json);

      expect(m.id, equals(1));
      expect(m.channelId, equals(1));
      expect(m.userId, equals(1));
      expect(m.role, equals('admin'));
      expect(m.isActive, isTrue);
      expect(m.joinedAt, equals(DateTime.utc(2026, 1, 15)));
    });

    test('toJson returns correct snake_case map', () {
      final m = ChannelMember(
        id: 1,
        channelId: 1,
        userId: 1,
        role: 'admin',
        isActive: true,
        joinedAt: DateTime.utc(2026, 1, 15),
      );

      final map = m.toJson();

      expect(map['channel_id'], equals(1));
      expect(map['user_id'], equals(1));
      expect(map['role'], equals('admin'));
    });

    test('fromJson handles null values', () {
      final minimal = <String, dynamic>{
        'channel_id': 1,
        'user_id': 2,
      };

      final m = ChannelMember.fromJson(minimal);

      expect(m.id, isNull);
      expect(m.channelId, equals(1));
      expect(m.userId, equals(2));
      expect(m.role, equals('member'));
      expect(m.isActive, isTrue);
      expect(m.joinedAt, isNull);
    });
  });
}
