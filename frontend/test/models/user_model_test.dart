import 'package:flutter_test/flutter_test.dart';
import 'package:clakettes/models/user_model.dart';

void main() {
  group('User', () {
    final json = <String, dynamic>{
      'id': 1,
      'username': 'jdoe',
      'email': 'j@doe.com',
      'full_name': 'John Doe',
      'role': 'admin',
      'bio': 'Filmmaker',
      'avatar_url': 'http://example.com/avatar.png',
      'is_active': true,
      'is_public': true,
      'is_public_email': true,
      'is_public_bio': false,
      'is_public_location': true,
      'latitude': 41.3874,
      'longitude': 2.1686,
      'created_at': '2026-01-01T00:00:00.000Z',
      'updated_at': '2026-06-01T00:00:00.000Z',
    };

    test('fromJson creates correct object with all fields', () {
      final user = User.fromJson(json);

      expect(user.id, equals(1));
      expect(user.username, equals('jdoe'));
      expect(user.email, equals('j@doe.com'));
      expect(user.fullName, equals('John Doe'));
      expect(user.role, equals('admin'));
      expect(user.bio, equals('Filmmaker'));
      expect(user.avatarUrl, equals('http://example.com/avatar.png'));
      expect(user.isActive, isTrue);
      expect(user.isPublic, isTrue);
      expect(user.isPublicEmail, isTrue);
      expect(user.isPublicBio, isFalse);
      expect(user.isPublicLocation, isTrue);
      expect(user.latitude, equals(41.3874));
      expect(user.longitude, equals(2.1686));
      expect(user.createdAt, equals(DateTime.utc(2026, 1, 1)));
      expect(user.updatedAt, equals(DateTime.utc(2026, 6, 1)));
    });

    test('toJson returns correct snake_case map', () {
      final user = User(
        id: 1,
        username: 'jdoe',
        email: 'j@doe.com',
        fullName: 'John Doe',
        role: 'admin',
        bio: 'Filmmaker',
        avatarUrl: 'http://example.com/avatar.png',
        isActive: true,
        isPublic: true,
        isPublicEmail: true,
        isPublicBio: false,
        isPublicLocation: true,
        latitude: 41.3874,
        longitude: 2.1686,
        createdAt: DateTime.utc(2026, 1, 1),
        updatedAt: DateTime.utc(2026, 6, 1),
      );

      final map = user.toJson();

      expect(map['id'], equals(1));
      expect(map['username'], equals('jdoe'));
      expect(map['email'], equals('j@doe.com'));
      expect(map['full_name'], equals('John Doe'));
      expect(map['role'], equals('admin'));
      expect(map['bio'], equals('Filmmaker'));
      expect(map['avatar_url'], equals('http://example.com/avatar.png'));
      expect(map['is_active'], isTrue);
      expect(map['is_public'], isTrue);
      expect(map['is_public_email'], isTrue);
      expect(map['is_public_bio'], isFalse);
      expect(map['is_public_location'], isTrue);
      expect(map['latitude'], equals(41.3874));
      expect(map['longitude'], equals(2.1686));
    });

    test('fromJson handles null optionals', () {
      final minimal = <String, dynamic>{
        'username': 'test',
        'email': 'test@test.com',
      };

      final user = User.fromJson(minimal);

      expect(user.id, isNull);
      expect(user.username, equals('test'));
      expect(user.email, equals('test@test.com'));
      expect(user.fullName, isNull);
      expect(user.role, isNull);
      expect(user.bio, isNull);
      expect(user.avatarUrl, isNull);
      expect(user.isActive, isTrue);
      expect(user.isPublic, isTrue);
      expect(user.isPublicEmail, isTrue);
      expect(user.isPublicBio, isTrue);
      expect(user.isPublicLocation, isTrue);
      expect(user.latitude, isNull);
      expect(user.longitude, isNull);
      expect(user.createdAt, isNull);
      expect(user.updatedAt, isNull);
    });

    test('copyWith creates new instance with overridden fields', () {
      final user = User(
        id: 1,
        username: 'jdoe',
        email: 'j@doe.com',
        fullName: 'John Doe',
        role: 'admin',
        bio: 'Filmmaker',
        avatarUrl: 'http://example.com/avatar.png',
        isActive: true,
        isPublic: true,
        isPublicEmail: true,
        isPublicBio: false,
        isPublicLocation: true,
        latitude: 41.3874,
        longitude: 2.1686,
      );

      final copy = user.copyWith(
        fullName: 'Jane Doe',
        email: 'jane@doe.com',
        latitude: 40.4168,
        longitude: -3.7038,
      );

      expect(copy.id, equals(1));
      expect(copy.username, equals('jdoe'));
      expect(copy.email, equals('jane@doe.com'));
      expect(copy.fullName, equals('Jane Doe'));
      expect(copy.role, equals('admin'));
      expect(copy.latitude, equals(40.4168));
      expect(copy.longitude, equals(-3.7038));
      expect(copy.isPublic, isTrue);
    });

    test('copyWith preserves unchanged fields', () {
      final user = User(
        id: 1,
        username: 'jdoe',
        email: 'j@doe.com',
        role: 'admin',
      );

      final copy = user.copyWith(username: 'jdoe2');

      expect(copy.id, equals(1));
      expect(copy.username, equals('jdoe2'));
      expect(copy.email, equals('j@doe.com'));
      expect(copy.role, equals('admin'));
    });
  });
}
