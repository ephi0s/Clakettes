import 'package:flutter_test/flutter_test.dart';
import 'package:clakettes/models/user_alias_model.dart';

void main() {
  group('UserAlias', () {
    final json = <String, dynamic>{
      'id': 1,
      'user_id': 1,
      'alias': 'cinephile99',
      'context': 'festival',
      'context_id': 1,
      'is_primary': true,
      'is_public': true,
      'show_awards': true,
      'profile_token': 'abc123',
      'visibility_scope': 'public',
      'notes': 'Main alias for festival',
    };

    test('fromJson creates correct object', () {
      final a = UserAlias.fromJson(json);

      expect(a.id, equals(1));
      expect(a.userId, equals(1));
      expect(a.alias, equals('cinephile99'));
      expect(a.context, equals('festival'));
      expect(a.contextId, equals(1));
      expect(a.isPrimary, isTrue);
      expect(a.isPublic, isTrue);
      expect(a.showAwards, isTrue);
      expect(a.profileToken, equals('abc123'));
      expect(a.visibilityScope, equals('public'));
      expect(a.notes, equals('Main alias for festival'));
    });

    test('toJson returns correct snake_case map', () {
      final a = UserAlias(
        id: 1,
        userId: 1,
        alias: 'cinephile99',
        context: 'festival',
        contextId: 1,
        isPrimary: true,
        isPublic: true,
        showAwards: true,
        profileToken: 'abc123',
        visibilityScope: 'public',
        notes: 'Main alias for festival',
      );

      final map = a.toJson();

      expect(map['user_id'], equals(1));
      expect(map['alias'], equals('cinephile99'));
      expect(map['context'], equals('festival'));
      expect(map['context_id'], equals(1));
      expect(map['is_primary'], isTrue);
      expect(map['is_public'], isTrue);
      expect(map['show_awards'], isTrue);
      expect(map['visibility_scope'], equals('public'));
      expect(map['notes'], equals('Main alias for festival'));
    });

    test('fromJson handles null values', () {
      final minimal = <String, dynamic>{
        'user_id': 1,
        'alias': 'guest',
      };

      final a = UserAlias.fromJson(minimal);

      expect(a.id, isNull);
      expect(a.userId, equals(1));
      expect(a.alias, equals('guest'));
      expect(a.context, equals('global'));
      expect(a.contextId, isNull);
      expect(a.isPrimary, isFalse);
      expect(a.isPublic, isTrue);
      expect(a.showAwards, isFalse);
      expect(a.profileToken, isNull);
      expect(a.visibilityScope, equals('festival_only'));
      expect(a.notes, isNull);
    });
  });
}
