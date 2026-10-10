import 'package:flutter_test/flutter_test.dart';
import 'package:clakettes/models/location_model.dart';

void main() {
  group('Location', () {
    final json = <String, dynamic>{
      'id': 1,
      'name': 'Sala Montjuïc',
      'description': 'Open-air cinema',
      'address': 'Carrer de l\'Arquebisbe 1, Barcelona',
      'latitude': 41.3712,
      'longitude': 2.1679,
      'tags': ['outdoor', 'historical'],
      'images': ['http://example.com/img1.jpg'],
      'is_active': true,
      'created_at': '2026-01-01T00:00:00.000Z',
      'updated_at': '2026-06-01T00:00:00.000Z',
    };

    test('fromJson creates correct object with all fields', () {
      final location = Location.fromJson(json);

      expect(location.id, equals(1));
      expect(location.name, equals('Sala Montjuïc'));
      expect(location.description, equals('Open-air cinema'));
      expect(location.address, equals('Carrer de l\'Arquebisbe 1, Barcelona'));
      expect(location.latitude, equals(41.3712));
      expect(location.longitude, equals(2.1679));
      expect(location.tags, equals(['outdoor', 'historical']));
      expect(location.images, equals(['http://example.com/img1.jpg']));
      expect(location.isActive, isTrue);
      expect(location.createdAt, equals(DateTime.utc(2026, 1, 1)));
      expect(location.updatedAt, equals(DateTime.utc(2026, 6, 1)));
    });

    test('toJson returns correct snake_case map', () {
      final location = Location(
        id: 1,
        name: 'Sala Montjuïc',
        description: 'Open-air cinema',
        address: 'Carrer de l\'Arquebisbe 1, Barcelona',
        latitude: 41.3712,
        longitude: 2.1679,
        tags: ['outdoor', 'historical'],
        images: ['http://example.com/img1.jpg'],
        isActive: true,
        createdAt: DateTime.utc(2026, 1, 1),
        updatedAt: DateTime.utc(2026, 6, 1),
      );

      final map = location.toJson();

      expect(map['id'], equals(1));
      expect(map['name'], equals('Sala Montjuïc'));
      expect(map['description'], equals('Open-air cinema'));
      expect(map['address'], equals('Carrer de l\'Arquebisbe 1, Barcelona'));
      expect(map['latitude'], equals(41.3712));
      expect(map['longitude'], equals(2.1679));
      expect(map['tags'], equals(['outdoor', 'historical']));
      expect(map['images'], equals(['http://example.com/img1.jpg']));
      expect(map['is_active'], isTrue);
    });

    test('fromJson handles null optionals', () {
      final minimal = <String, dynamic>{
        'name': 'Test Location',
        'latitude': 0.0,
        'longitude': 0.0,
      };

      final location = Location.fromJson(minimal);

      expect(location.id, isNull);
      expect(location.name, equals('Test Location'));
      expect(location.description, isNull);
      expect(location.address, isNull);
      expect(location.tags, isEmpty);
      expect(location.images, isEmpty);
      expect(location.isActive, isTrue);
      expect(location.createdAt, isNull);
      expect(location.updatedAt, isNull);
    });

    test('toJson converts default values correctly', () {
      final location = Location(
        name: 'Default Location',
        latitude: 10.0,
        longitude: 20.0,
      );

      final map = location.toJson();

      expect(map['id'], isNull);
      expect(map['name'], equals('Default Location'));
      expect(map['latitude'], equals(10.0));
      expect(map['longitude'], equals(20.0));
      expect(map['tags'], isEmpty);
      expect(map['images'], isEmpty);
      expect(map['is_active'], isTrue);
    });

    test('fromJson handles num types for lat/lng', () {
      final json = <String, dynamic>{
        'name': 'Test',
        'latitude': 41,
        'longitude': 2,
      };

      final location = Location.fromJson(json);
      expect(location.latitude, equals(41.0));
      expect(location.longitude, equals(2.0));
    });
  });
}
