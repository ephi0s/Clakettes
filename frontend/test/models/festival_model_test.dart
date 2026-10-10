import 'package:flutter_test/flutter_test.dart';
import 'package:clakettes/models/festival_model.dart';

void main() {
  group('Festival', () {
    final json = <String, dynamic>{
      'id': 1,
      'name': 'Test Fest',
      'description': 'A test',
      'location': 'Barcelona',
      'latitude': 41.3874,
      'longitude': 2.1686,
      'is_active': true,
      'website': 'http://example.com',
      'logo_url': 'http://example.com/logo.png',
      'created_at': '2026-01-01T00:00:00.000Z',
      'updated_at': '2026-06-01T00:00:00.000Z',
    };

    test('fromJson creates correct object', () {
      final festival = Festival.fromJson(json);

      expect(festival.id, equals(1));
      expect(festival.name, equals('Test Fest'));
      expect(festival.description, equals('A test'));
      expect(festival.location, equals('Barcelona'));
      expect(festival.latitude, equals(41.3874));
      expect(festival.longitude, equals(2.1686));
      expect(festival.isActive, isTrue);
      expect(festival.website, equals('http://example.com'));
      expect(festival.logoUrl, equals('http://example.com/logo.png'));
      expect(festival.createdAt, equals(DateTime.utc(2026, 1, 1)));
      expect(festival.updatedAt, equals(DateTime.utc(2026, 6, 1)));
    });

    test('toJson returns correct snake_case map', () {
      final festival = Festival(
        id: 1,
        name: 'Test Fest',
        description: 'A test',
        location: 'Barcelona',
        latitude: 41.3874,
        longitude: 2.1686,
        isActive: true,
        website: 'http://example.com',
        logoUrl: 'http://example.com/logo.png',
        createdAt: DateTime.utc(2026, 1, 1),
        updatedAt: DateTime.utc(2026, 6, 1),
      );

      final map = festival.toJson();

      expect(map['id'], equals(1));
      expect(map['name'], equals('Test Fest'));
      expect(map['description'], equals('A test'));
      expect(map['location'], equals('Barcelona'));
      expect(map['latitude'], equals(41.3874));
      expect(map['longitude'], equals(2.1686));
      expect(map['is_active'], isTrue);
      expect(map['website'], equals('http://example.com'));
      expect(map['logo_url'], equals('http://example.com/logo.png'));
    });

    test('fromJson handles null values', () {
      final minimal = <String, dynamic>{
        'name': 'Minimal Fest',
      };

      final festival = Festival.fromJson(minimal);

      expect(festival.id, isNull);
      expect(festival.name, equals('Minimal Fest'));
      expect(festival.description, isNull);
      expect(festival.location, isNull);
      expect(festival.latitude, isNull);
      expect(festival.longitude, isNull);
      expect(festival.isActive, isTrue);
      expect(festival.website, isNull);
      expect(festival.logoUrl, isNull);
      expect(festival.createdAt, isNull);
      expect(festival.updatedAt, isNull);
    });
  });
}
