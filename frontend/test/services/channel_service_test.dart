import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:clakettes/services/channel_service.dart';
import 'package:clakettes/services/api_service.dart';

Map<String, dynamic> _channelJson({int id = 1, String name = 'General'}) => {
  'id': id,
  'name': name,
  'channel_type': 'community',
  'description': 'A test channel',
  'is_active': true,
  'member_count': 5,
  'max_members': 100,
  'created_by': 1,
  'created_at': '2026-01-01T00:00:00.000Z',
  'updated_at': '2026-06-01T00:00:00.000Z',
};

Map<String, dynamic> _memberJson({int userId = 1, String role = 'member'}) => {
  'id': 1,
  'channel_id': 1,
  'user_id': userId,
  'role': role,
  'joined_at': '2026-01-01T00:00:00.000Z',
};

List<Map<String, dynamic>> _channelListJson({int count = 2}) =>
    List.generate(count, (i) => _channelJson(id: i + 1, name: 'Channel ${i + 1}'));

void main() {
  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  group('ChannelApiService', () {
    test('getMyChannels returns list of channels', () async {
      ApiService().client = MockClient((request) async {
        return http.Response(
          json.encode({'items': _channelListJson(), 'total': 2, 'pages': 1}),
          200,
        );
      });

      final service = ChannelApiService();
      final channels = await service.getMyChannels();
      expect(channels.length, 2);
      expect(channels[0].name, 'Channel 1');
      expect(channels[1].name, 'Channel 2');
    });

    test('getMyChannels returns empty list when no channels', () async {
      ApiService().client = MockClient((request) async {
        return http.Response(
          json.encode({'items': [], 'total': 0, 'pages': 0}),
          200,
        );
      });

      final service = ChannelApiService();
      final channels = await service.getMyChannels();
      expect(channels, isEmpty);
    });

    test('createChannel returns created channel', () async {
      ApiService().client = MockClient((request) async {
        return http.Response(
          json.encode(_channelJson(name: 'New Channel')),
          200,
        );
      });

      final service = ChannelApiService();
      final channel = await service.createChannel(name: 'New Channel', description: 'Desc');
      expect(channel.name, 'New Channel');
    });

    test('getChannel returns channel by id', () async {
      ApiService().client = MockClient((request) async {
        return http.Response(json.encode(_channelJson(id: 42)), 200);
      });

      final service = ChannelApiService();
      final channel = await service.getChannel(42);
      expect(channel.id, 42);
    });

    test('getChannelMembers returns list of members', () async {
      ApiService().client = MockClient((request) async {
        return http.Response(
          json.encode([_memberJson(userId: 1), _memberJson(userId: 2)]),
          200,
        );
      });

      final service = ChannelApiService();
      final members = await service.getChannelMembers(1);
      expect(members.length, 2);
    });

    test('addMember succeeds', () async {
      ApiService().client = MockClient((request) async {
        return http.Response('{}', 200);
      });

      final service = ChannelApiService();
      await expectLater(service.addMember(1, 2), completes);
    });

    test('removeMember succeeds', () async {
      ApiService().client = MockClient((request) async {
        return http.Response('{}', 200);
      });

      final service = ChannelApiService();
      await expectLater(service.removeMember(1, 2), completes);
    });

    test('uploadPublicKey succeeds', () async {
      ApiService().client = MockClient((request) async {
        return http.Response('{}', 200);
      });

      final service = ChannelApiService();
      await expectLater(service.uploadPublicKey('dGVzdC1rZXk='), completes);
    });

    test('getPublicKey returns key string', () async {
      ApiService().client = MockClient((request) async {
        return http.Response(
          json.encode({'public_key_x25519': 'dGVzdC1wdWJsaWMta2V5'}),
          200,
        );
      });

      final service = ChannelApiService();
      final key = await service.getPublicKey(1);
      expect(key, 'dGVzdC1wdWJsaWMta2V5');
    });

    test('getPublicKey returns null on error', () async {
      ApiService().client = MockClient((request) async {
        return http.Response('Not Found', 404);
      });

      final service = ChannelApiService();
      final key = await service.getPublicKey(999);
      expect(key, isNull);
    });
  });
}
