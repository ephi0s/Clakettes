import 'package:flutter_test/flutter_test.dart';
import 'package:clakettes/models/role_transition_model.dart';

void main() {
  group('RoleTransition', () {
    final json = <String, dynamic>{
      'id': 1,
      'user_id': 1,
      'from_role_id': 1,
      'to_role_id': 2,
      'from_festival_id': 1,
      'to_festival_id': 1,
      'transition_type': 'promotion',
      'changed_by': 3,
      'reason': 'Performance',
      'from_role': {'display_name': 'Member'},
      'to_role': {'display_name': 'Jury'},
    };

    test('fromJson creates correct object', () {
      final t = RoleTransition.fromJson(json);

      expect(t.id, equals(1));
      expect(t.userId, equals(1));
      expect(t.fromRoleId, equals(1));
      expect(t.toRoleId, equals(2));
      expect(t.fromFestivalId, equals(1));
      expect(t.toFestivalId, equals(1));
      expect(t.transitionType, equals('promotion'));
      expect(t.changedBy, equals(3));
      expect(t.reason, equals('Performance'));
      expect(t.fromRoleName, equals('Member'));
      expect(t.toRoleName, equals('Jury'));
    });

    test('toJson returns correct snake_case map', () {
      final t = RoleTransition(
        id: 1,
        userId: 1,
        fromRoleId: 1,
        toRoleId: 2,
        fromFestivalId: 1,
        toFestivalId: 1,
        transitionType: 'promotion',
        changedBy: 3,
        reason: 'Performance',
      );

      final map = t.toJson();

      expect(map['user_id'], equals(1));
      expect(map['from_role_id'], equals(1));
      expect(map['to_role_id'], equals(2));
      expect(map['from_festival_id'], equals(1));
      expect(map['to_festival_id'], equals(1));
      expect(map['transition_type'], equals('promotion'));
      expect(map['changed_by'], equals(3));
      expect(map['reason'], equals('Performance'));
    });

    test('fromJson handles null values', () {
      final minimal = <String, dynamic>{
        'user_id': 1,
        'to_role_id': 2,
        'transition_type': 'assignment',
        'changed_by': 3,
      };

      final t = RoleTransition.fromJson(minimal);

      expect(t.id, isNull);
      expect(t.userId, equals(1));
      expect(t.fromRoleId, isNull);
      expect(t.toRoleId, equals(2));
      expect(t.fromFestivalId, isNull);
      expect(t.toFestivalId, isNull);
      expect(t.transitionType, equals('assignment'));
      expect(t.changedBy, equals(3));
      expect(t.reason, isNull);
      expect(t.fromRoleName, isNull);
      expect(t.toRoleName, isNull);
    });
  });
}
