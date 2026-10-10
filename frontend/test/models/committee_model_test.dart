import 'package:flutter_test/flutter_test.dart';
import 'package:clakettes/models/committee_model.dart';

void main() {
  group('Committee', () {
    final json = <String, dynamic>{
      'id': 1,
      'festival_id': 1,
      'name': 'Selection Committee',
      'description': 'Selects the films',
      'role_id': 1,
      'is_active': true,
      'max_members': 10,
      'external_visible': true,
      'member_count': 5,
    };

    test('fromJson creates correct object', () {
      final c = Committee.fromJson(json);

      expect(c.id, equals(1));
      expect(c.festivalId, equals(1));
      expect(c.name, equals('Selection Committee'));
      expect(c.description, equals('Selects the films'));
      expect(c.roleId, equals(1));
      expect(c.isActive, isTrue);
      expect(c.maxMembers, equals(10));
      expect(c.externalVisible, isTrue);
      expect(c.memberCount, equals(5));
    });

    test('toJson returns correct snake_case map', () {
      final c = Committee(
        id: 1,
        festivalId: 1,
        name: 'Selection Committee',
        description: 'Selects the films',
        roleId: 1,
        isActive: true,
        maxMembers: 10,
        externalVisible: true,
        memberCount: 5,
      );

      final map = c.toJson();

      expect(map['festival_id'], equals(1));
      expect(map['name'], equals('Selection Committee'));
      expect(map['description'], equals('Selects the films'));
      expect(map['role_id'], equals(1));
      expect(map['is_active'], isTrue);
      expect(map['max_members'], equals(10));
      expect(map['external_visible'], isTrue);
    });

    test('fromJson handles null values', () {
      final minimal = <String, dynamic>{
        'festival_id': 1,
        'name': 'Minimal',
      };

      final c = Committee.fromJson(minimal);

      expect(c.id, isNull);
      expect(c.festivalId, equals(1));
      expect(c.name, equals('Minimal'));
      expect(c.description, isNull);
      expect(c.roleId, isNull);
      expect(c.isActive, isTrue);
      expect(c.maxMembers, isNull);
      expect(c.externalVisible, isFalse);
      expect(c.memberCount, equals(0));
    });
  });

  group('CommitteeMember', () {
    final json = <String, dynamic>{
      'id': 1,
      'committee_id': 1,
      'user_id': 1,
      'role_in_committee': 'chair',
      'assigned_by': 2,
      'is_active': true,
      'notes': 'Experienced juror',
      'user': {
        'full_name': 'Alice Smith',
        'avatar_url': 'http://example.com/alice.png',
      },
    };

    test('fromJson creates correct object', () {
      final m = CommitteeMember.fromJson(json);

      expect(m.id, equals(1));
      expect(m.committeeId, equals(1));
      expect(m.userId, equals(1));
      expect(m.roleInCommittee, equals('chair'));
      expect(m.assignedBy, equals(2));
      expect(m.isActive, isTrue);
      expect(m.notes, equals('Experienced juror'));
      expect(m.userName, equals('Alice Smith'));
      expect(m.userAvatar, equals('http://example.com/alice.png'));
    });

    test('toJson returns correct snake_case map', () {
      final m = CommitteeMember(
        id: 1,
        committeeId: 1,
        userId: 1,
        roleInCommittee: 'chair',
        assignedBy: 2,
        isActive: true,
        notes: 'Experienced juror',
        userName: 'Alice Smith',
        userAvatar: 'http://example.com/alice.png',
      );

      final map = m.toJson();

      expect(map['committee_id'], equals(1));
      expect(map['user_id'], equals(1));
      expect(map['role_in_committee'], equals('chair'));
      expect(map['assigned_by'], equals(2));
      expect(map['notes'], equals('Experienced juror'));
    });

    test('fromJson handles null values', () {
      final minimal = <String, dynamic>{
        'committee_id': 1,
        'user_id': 2,
      };

      final m = CommitteeMember.fromJson(minimal);

      expect(m.id, isNull);
      expect(m.committeeId, equals(1));
      expect(m.userId, equals(2));
      expect(m.roleInCommittee, equals('member'));
      expect(m.assignedBy, isNull);
      expect(m.isActive, isTrue);
      expect(m.notes, isNull);
      expect(m.userName, isNull);
      expect(m.userAvatar, isNull);
    });
  });
}
