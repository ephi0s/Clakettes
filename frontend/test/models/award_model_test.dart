import 'package:flutter_test/flutter_test.dart';
import 'package:clakettes/models/award_model.dart';

void main() {
  group('Award', () {
    final json = <String, dynamic>{
      'id': 1,
      'festival_id': 1,
      'award_name': 'Best Short',
      'award_category': 'Fiction',
      'event_id': 1,
      'shortfilm_id': 1,
      'user_id': 1,
      'position': 1,
      'is_winner': true,
      'prize_amount': '1000',
      'description': 'Best fiction short film',
      'is_public': true,
      'is_verified': true,
      'year': 2026,
    };

    test('fromJson creates correct object', () {
      final a = Award.fromJson(json);

      expect(a.id, equals(1));
      expect(a.festivalId, equals(1));
      expect(a.awardName, equals('Best Short'));
      expect(a.awardCategory, equals('Fiction'));
      expect(a.eventId, equals(1));
      expect(a.shortfilmId, equals(1));
      expect(a.userId, equals(1));
      expect(a.position, equals(1));
      expect(a.isWinner, isTrue);
      expect(a.prizeAmount, equals('1000'));
      expect(a.description, equals('Best fiction short film'));
      expect(a.isPublic, isTrue);
      expect(a.isVerified, isTrue);
      expect(a.year, equals(2026));
    });

    test('toJson returns correct snake_case map', () {
      final a = Award(
        id: 1,
        festivalId: 1,
        awardName: 'Best Short',
        awardCategory: 'Fiction',
        eventId: 1,
        shortfilmId: 1,
        userId: 1,
        position: 1,
        isWinner: true,
        prizeAmount: '1000',
        description: 'Best fiction short film',
        isPublic: true,
        isVerified: true,
        year: 2026,
      );

      final map = a.toJson();

      expect(map['festival_id'], equals(1));
      expect(map['award_name'], equals('Best Short'));
      expect(map['award_category'], equals('Fiction'));
      expect(map['event_id'], equals(1));
      expect(map['shortfilm_id'], equals(1));
      expect(map['user_id'], equals(1));
      expect(map['position'], equals(1));
      expect(map['is_winner'], isTrue);
      expect(map['prize_amount'], equals('1000'));
      expect(map['description'], equals('Best fiction short film'));
      expect(map['is_public'], isTrue);
      expect(map['is_verified'], isTrue);
      expect(map['year'], equals(2026));
    });

    test('fromJson handles null values', () {
      final minimal = <String, dynamic>{
        'festival_id': 1,
        'award_name': 'Honorary',
      };

      final a = Award.fromJson(minimal);

      expect(a.id, isNull);
      expect(a.festivalId, equals(1));
      expect(a.awardName, equals('Honorary'));
      expect(a.awardCategory, isNull);
      expect(a.eventId, isNull);
      expect(a.shortfilmId, isNull);
      expect(a.userId, isNull);
      expect(a.position, isNull);
      expect(a.isWinner, isFalse);
      expect(a.prizeAmount, isNull);
      expect(a.description, isNull);
      expect(a.isPublic, isTrue);
      expect(a.isVerified, isFalse);
      expect(a.year, isNull);
    });
  });
}
