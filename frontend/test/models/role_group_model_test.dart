import 'package:flutter_test/flutter_test.dart';
import 'package:clakettes/models/role_group_model.dart';

void main() {
  group('RoleGroup', () {
    final json = <String, dynamic>{
      'id': 1,
      'name': 'directors',
      'display_name': 'Directors',
      'description': 'Film directors group',
      'sort_order': 1,
      'is_active': true,
    };

    test('fromJson creates correct object', () {
      final g = RoleGroup.fromJson(json);

      expect(g.id, equals(1));
      expect(g.name, equals('directors'));
      expect(g.displayName, equals('Directors'));
      expect(g.description, equals('Film directors group'));
      expect(g.sortOrder, equals(1));
      expect(g.isActive, isTrue);
    });

    test('toJson returns correct snake_case map', () {
      final g = RoleGroup(
        id: 1,
        name: 'directors',
        displayName: 'Directors',
        description: 'Film directors group',
        sortOrder: 1,
        isActive: true,
      );

      final map = g.toJson();

      expect(map['name'], equals('directors'));
      expect(map['display_name'], equals('Directors'));
      expect(map['description'], equals('Film directors group'));
      expect(map['sort_order'], equals(1));
      expect(map['is_active'], isTrue);
    });

    test('fromJson handles null values', () {
      final minimal = <String, dynamic>{
        'name': 'editors',
        'display_name': 'Editors',
      };

      final g = RoleGroup.fromJson(minimal);

      expect(g.id, isNull);
      expect(g.name, equals('editors'));
      expect(g.displayName, equals('Editors'));
      expect(g.description, isNull);
      expect(g.sortOrder, equals(0));
      expect(g.isActive, isTrue);
    });
  });

  group('RoleGroupMembership', () {
    final json = <String, dynamic>{
      'id': 1,
      'group_id': 1,
      'role_id': 2,
      'level': 3,
      'is_leader': true,
      'is_active': true,
      'role': {'display_name': 'Jury'},
    };

    test('fromJson creates correct object', () {
      final m = RoleGroupMembership.fromJson(json);

      expect(m.id, equals(1));
      expect(m.groupId, equals(1));
      expect(m.roleId, equals(2));
      expect(m.level, equals(3));
      expect(m.isLeader, isTrue);
      expect(m.isActive, isTrue);
      expect(m.roleName, equals('Jury'));
    });

    test('toJson returns correct snake_case map', () {
      final m = RoleGroupMembership(
        id: 1,
        groupId: 1,
        roleId: 2,
        level: 3,
        isLeader: true,
        isActive: true,
      );

      final map = m.toJson();

      expect(map['group_id'], equals(1));
      expect(map['role_id'], equals(2));
      expect(map['level'], equals(3));
      expect(map['is_leader'], isTrue);
    });

    test('fromJson handles null values', () {
      final minimal = <String, dynamic>{
        'group_id': 1,
        'role_id': 2,
      };

      final m = RoleGroupMembership.fromJson(minimal);

      expect(m.id, isNull);
      expect(m.groupId, equals(1));
      expect(m.roleId, equals(2));
      expect(m.level, equals(0));
      expect(m.isLeader, isFalse);
      expect(m.isActive, isTrue);
      expect(m.roleName, isNull);
    });
  });
}
