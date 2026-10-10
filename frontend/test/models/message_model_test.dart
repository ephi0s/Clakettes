import 'package:flutter_test/flutter_test.dart';
import 'package:clakettes/models/message_model.dart';

void main() {
  group('Message', () {
    final json = <String, dynamic>{
      'id': 1,
      'content': 'Hello!',
      'sender_id': 1,
      'receiver_id': 2,
      'group_id': null,
      'channel_id': null,
      'is_read': false,
      'created_at': '2026-01-01T00:00:00.000Z',
      'updated_at': '2026-06-01T00:00:00.000Z',
      'message_type': 'text',
      'media_url': null,
      'latitude': null,
      'longitude': null,
      'vcard_data': null,
      'ical_data': null,
    };

    test('fromJson creates correct object', () {
      final msg = Message.fromJson(json);

      expect(msg.id, equals(1));
      expect(msg.content, equals('Hello!'));
      expect(msg.senderId, equals(1));
      expect(msg.receiverId, equals(2));
      expect(msg.groupId, isNull);
      expect(msg.channelId, isNull);
      expect(msg.isRead, isFalse);
      expect(msg.createdAt, equals(DateTime.utc(2026, 1, 1)));
      expect(msg.updatedAt, equals(DateTime.utc(2026, 6, 1)));
      expect(msg.messageType, equals('text'));
      expect(msg.mediaUrl, isNull);
      expect(msg.latitude, isNull);
      expect(msg.longitude, isNull);
      expect(msg.vcardData, isNull);
      expect(msg.icalData, isNull);
    });

    test('toJson returns correct snake_case map', () {
      final msg = Message(
        id: 1,
        content: 'Hello!',
        senderId: 1,
        receiverId: 2,
        groupId: null,
        channelId: null,
        isRead: false,
        createdAt: DateTime.utc(2026, 1, 1),
        updatedAt: DateTime.utc(2026, 6, 1),
        messageType: 'text',
        mediaUrl: null,
        latitude: null,
        longitude: null,
        vcardData: null,
        icalData: null,
      );

      final map = msg.toJson();

      expect(map['id'], equals(1));
      expect(map['content'], equals('Hello!'));
      expect(map['sender_id'], equals(1));
      expect(map['receiver_id'], equals(2));
      expect(map['group_id'], isNull);
      expect(map['channel_id'], isNull);
      expect(map['is_read'], isFalse);
      expect(map['message_type'], equals('text'));
      expect(map['media_url'], isNull);
      expect(map['latitude'], isNull);
      expect(map['longitude'], isNull);
      expect(map['vcard_data'], isNull);
      expect(map['ical_data'], isNull);
    });

    test('fromJson handles null values with defaults', () {
      final minimal = <String, dynamic>{
        'content': 'Hi',
        'sender_id': 1,
      };

      final msg = Message.fromJson(minimal);

      expect(msg.id, isNull);
      expect(msg.content, equals('Hi'));
      expect(msg.senderId, equals(1));
      expect(msg.receiverId, isNull);
      expect(msg.groupId, isNull);
      expect(msg.channelId, isNull);
      expect(msg.isRead, isFalse);
      expect(msg.createdAt, isNull);
      expect(msg.updatedAt, isNull);
      expect(msg.messageType, equals('text'));
      expect(msg.mediaUrl, isNull);
      expect(msg.latitude, isNull);
      expect(msg.longitude, isNull);
      expect(msg.vcardData, isNull);
      expect(msg.icalData, isNull);
    });
  });
}
