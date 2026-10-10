import 'package:flutter_test/flutter_test.dart';
import 'package:clakettes/models/role_delegation_model.dart';

void main() {
  group('RoleDelegation', () {
    final json = <String, dynamic>{
      'id': 1,
      'delegator_id': 1,
      'delegate_id': 2,
      'role_id': 3,
      'festival_id': 1,
      'status': 'active',
      'reason': 'On vacation',
      'scope_limitations': 'No financial decisions',
      'revoked_by': null,
      'revoked_reason': null,
      'delegator': {'full_name': 'Alice', 'username': 'alice'},
      'delegate': {'full_name': 'Bob', 'username': 'bob'},
      'role': {'display_name': 'Jury'},
    };

    test('fromJson creates correct object', () {
      final d = RoleDelegation.fromJson(json);

      expect(d.id, equals(1));
      expect(d.delegatorId, equals(1));
      expect(d.delegateId, equals(2));
      expect(d.roleId, equals(3));
      expect(d.festivalId, equals(1));
      expect(d.status, equals('active'));
      expect(d.reason, equals('On vacation'));
      expect(d.scopeLimitations, equals('No financial decisions'));
      expect(d.revokedBy, isNull);
      expect(d.revokedReason, isNull);
      expect(d.delegatorName, equals('Alice'));
      expect(d.delegateName, equals('Bob'));
      expect(d.roleName, equals('Jury'));
    });

    test('toJson returns correct snake_case map', () {
      final d = RoleDelegation(
        id: 1,
        delegatorId: 1,
        delegateId: 2,
        roleId: 3,
        festivalId: 1,
        status: 'active',
        reason: 'On vacation',
        scopeLimitations: 'No financial decisions',
      );

      final map = d.toJson();

      expect(map['delegator_id'], equals(1));
      expect(map['delegate_id'], equals(2));
      expect(map['role_id'], equals(3));
      expect(map['festival_id'], equals(1));
      expect(map['reason'], equals('On vacation'));
      expect(map['scope_limitations'], equals('No financial decisions'));
    });

    test('fromJson handles null values', () {
      final minimal = <String, dynamic>{
        'delegator_id': 1,
        'delegate_id': 2,
        'role_id': 3,
      };

      final d = RoleDelegation.fromJson(minimal);

      expect(d.id, isNull);
      expect(d.delegatorId, equals(1));
      expect(d.delegateId, equals(2));
      expect(d.roleId, equals(3));
      expect(d.festivalId, isNull);
      expect(d.status, equals('active'));
      expect(d.reason, isNull);
      expect(d.scopeLimitations, isNull);
      expect(d.revokedBy, isNull);
      expect(d.revokedReason, isNull);
      expect(d.delegatorName, isNull);
      expect(d.delegateName, isNull);
      expect(d.roleName, isNull);
    });
  });
}
