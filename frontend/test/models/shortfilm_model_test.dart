import 'package:flutter_test/flutter_test.dart';
import 'package:clakettes/models/shortfilm_model.dart';

void main() {
  group('ShortFilm', () {
    final json = <String, dynamic>{
      'id': 1,
      'title': 'My Film',
      'description': 'A short film',
      'duration': 120,
      'video_url': 'http://example.com/video.mp4',
      'thumbnail_url': 'http://example.com/thumb.png',
      'festival_id': 1,
      'user_id': 1,
      'is_public': true,
      'tags': 'drama, comedy',
      'created_at': '2026-01-01T00:00:00.000Z',
      'updated_at': '2026-06-01T00:00:00.000Z',
    };

    test('fromJson creates correct object', () {
      final film = ShortFilm.fromJson(json);

      expect(film.id, equals(1));
      expect(film.title, equals('My Film'));
      expect(film.description, equals('A short film'));
      expect(film.duration, equals(120));
      expect(film.videoUrl, equals('http://example.com/video.mp4'));
      expect(film.thumbnailUrl, equals('http://example.com/thumb.png'));
      expect(film.festivalId, equals(1));
      expect(film.userId, equals(1));
      expect(film.isPublic, isTrue);
      expect(film.tags, equals('drama, comedy'));
      expect(film.createdAt, equals(DateTime.utc(2026, 1, 1)));
      expect(film.updatedAt, equals(DateTime.utc(2026, 6, 1)));
    });

    test('toJson returns correct snake_case map', () {
      final film = ShortFilm(
        id: 1,
        title: 'My Film',
        description: 'A short film',
        duration: 120,
        videoUrl: 'http://example.com/video.mp4',
        thumbnailUrl: 'http://example.com/thumb.png',
        festivalId: 1,
        userId: 1,
        isPublic: true,
        tags: 'drama, comedy',
        createdAt: DateTime.utc(2026, 1, 1),
        updatedAt: DateTime.utc(2026, 6, 1),
      );

      final map = film.toJson();

      expect(map['id'], equals(1));
      expect(map['title'], equals('My Film'));
      expect(map['description'], equals('A short film'));
      expect(map['duration'], equals(120));
      expect(map['video_url'], equals('http://example.com/video.mp4'));
      expect(map['thumbnail_url'], equals('http://example.com/thumb.png'));
      expect(map['festival_id'], equals(1));
      expect(map['user_id'], equals(1));
      expect(map['is_public'], isTrue);
      expect(map['tags'], equals('drama, comedy'));
    });

    test('fromJson handles null values', () {
      final minimal = <String, dynamic>{
        'title': 'No ID Film',
        'user_id': 2,
      };

      final film = ShortFilm.fromJson(minimal);

      expect(film.id, isNull);
      expect(film.title, equals('No ID Film'));
      expect(film.description, isNull);
      expect(film.duration, isNull);
      expect(film.videoUrl, isNull);
      expect(film.thumbnailUrl, isNull);
      expect(film.festivalId, isNull);
      expect(film.userId, equals(2));
      expect(film.isPublic, isTrue);
      expect(film.tags, isNull);
      expect(film.createdAt, isNull);
      expect(film.updatedAt, isNull);
    });
  });
}
