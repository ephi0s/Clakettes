import 'package:flutter_test/flutter_test.dart';
import 'package:clakettes/models/registration_form_model.dart';

void main() {
  group('RegistrationForm', () {
    final json = <String, dynamic>{
      'id': 1,
      'festival_id': 1,
      'title': 'Jury Application',
      'description': 'Apply to be a jury member',
      'is_active': true,
      'require_existing_account': true,
      'starts_at': '2026-03-01T00:00:00.000Z',
      'ends_at': '2026-05-01T00:00:00.000Z',
      'max_registrations': 50,
      'allow_role_selection': true,
      'allow_tag_selection': true,
    };

    test('fromJson creates correct object', () {
      final f = RegistrationForm.fromJson(json);

      expect(f.id, equals(1));
      expect(f.festivalId, equals(1));
      expect(f.title, equals('Jury Application'));
      expect(f.description, equals('Apply to be a jury member'));
      expect(f.isActive, isTrue);
      expect(f.requireExistingAccount, isTrue);
      expect(f.startsAt, equals(DateTime.utc(2026, 3, 1)));
      expect(f.endsAt, equals(DateTime.utc(2026, 5, 1)));
      expect(f.maxRegistrations, equals(50));
      expect(f.allowRoleSelection, isTrue);
      expect(f.allowTagSelection, isTrue);
    });

    test('toJson returns correct snake_case map', () {
      final f = RegistrationForm(
        id: 1,
        festivalId: 1,
        title: 'Jury Application',
        description: 'Apply to be a jury member',
        isActive: true,
        requireExistingAccount: true,
        startsAt: DateTime.utc(2026, 3, 1),
        endsAt: DateTime.utc(2026, 5, 1),
        maxRegistrations: 50,
        allowRoleSelection: true,
        allowTagSelection: true,
      );

      final map = f.toJson();

      expect(map['festival_id'], equals(1));
      expect(map['title'], equals('Jury Application'));
      expect(map['description'], equals('Apply to be a jury member'));
      expect(map['is_active'], isTrue);
      expect(map['require_existing_account'], isTrue);
      expect(map['starts_at'], equals('2026-03-01T00:00:00.000Z'));
      expect(map['ends_at'], equals('2026-05-01T00:00:00.000Z'));
      expect(map['max_registrations'], equals(50));
      expect(map['allow_role_selection'], isTrue);
      expect(map['allow_tag_selection'], isTrue);
    });

    test('fromJson handles null values', () {
      final minimal = <String, dynamic>{
        'festival_id': 1,
        'title': 'Minimal',
      };

      final f = RegistrationForm.fromJson(minimal);

      expect(f.id, isNull);
      expect(f.festivalId, equals(1));
      expect(f.title, equals('Minimal'));
      expect(f.description, isNull);
      expect(f.isActive, isTrue);
      expect(f.requireExistingAccount, isTrue);
      expect(f.startsAt, isNull);
      expect(f.endsAt, isNull);
      expect(f.maxRegistrations, isNull);
      expect(f.allowRoleSelection, isTrue);
      expect(f.allowTagSelection, isTrue);
    });
  });

  group('RegistrationFormSection', () {
    final json = <String, dynamic>{
      'id': 1,
      'form_id': 1,
      'title': 'Personal Info',
      'description': 'Your details',
      'sort_order': 1,
      'allow_multiple_roles': true,
      'max_selections': 5,
      'is_required': true,
      'role_assignments': [
        {'role_id': 1},
        {'role_id': 2},
      ],
      'tag_assignments': [
        {'tag_id': 10},
        {'tag_id': 20},
      ],
    };

    test('fromJson creates correct object', () {
      final s = RegistrationFormSection.fromJson(json);

      expect(s.id, equals(1));
      expect(s.formId, equals(1));
      expect(s.title, equals('Personal Info'));
      expect(s.description, equals('Your details'));
      expect(s.sortOrder, equals(1));
      expect(s.isRequired, isTrue);
      expect(s.allowMultipleRoles, isTrue);
      expect(s.maxSelections, equals(5));
      expect(s.roleIds, equals([1, 2]));
      expect(s.tagIds, equals([10, 20]));
    });

    test('toJson returns correct snake_case map', () {
      final s = RegistrationFormSection(
        id: 1,
        formId: 1,
        title: 'Personal Info',
        description: 'Your details',
        sortOrder: 1,
        isRequired: true,
        allowMultipleRoles: true,
        maxSelections: 5,
        roleIds: [1, 2],
        tagIds: [10, 20],
      );

      final map = s.toJson();

      expect(map['form_id'], equals(1));
      expect(map['title'], equals('Personal Info'));
      expect(map['description'], equals('Your details'));
      expect(map['sort_order'], equals(1));
      expect(map['is_required'], isTrue);
      expect(map['allow_multiple_roles'], isTrue);
      expect(map['max_selections'], equals(5));
    });

    test('fromJson handles null values', () {
      final minimal = <String, dynamic>{
        'form_id': 1,
        'title': 'Minimal',
      };

      final s = RegistrationFormSection.fromJson(minimal);

      expect(s.id, isNull);
      expect(s.formId, equals(1));
      expect(s.title, equals('Minimal'));
      expect(s.description, isNull);
      expect(s.sortOrder, equals(0));
      expect(s.isRequired, isFalse);
      expect(s.allowMultipleRoles, isFalse);
      expect(s.maxSelections, isNull);
      expect(s.roleIds, isEmpty);
      expect(s.tagIds, isEmpty);
    });
  });

  group('FestivalRegistration', () {
    final json = <String, dynamic>{
      'id': 1,
      'form_id': 1,
      'user_id': 1,
      'festival_id': 1,
      'status': 'approved',
      'assigned_by': 2,
      'approved_by': 3,
      'notes': 'Welcome',
      'user': {
        'full_name': 'Charlie',
        'username': 'charlie',
        'email': 'c@test.com',
      },
    };

    test('fromJson creates correct object', () {
      final r = FestivalRegistration.fromJson(json);

      expect(r.id, equals(1));
      expect(r.formId, equals(1));
      expect(r.userId, equals(1));
      expect(r.festivalId, equals(1));
      expect(r.status, equals('approved'));
      expect(r.assignedBy, equals(2));
      expect(r.approvedBy, equals(3));
      expect(r.notes, equals('Welcome'));
      expect(r.userName, equals('Charlie'));
      expect(r.userEmail, equals('c@test.com'));
    });

    test('toJson returns correct snake_case map', () {
      final r = FestivalRegistration(
        id: 1,
        formId: 1,
        userId: 1,
        festivalId: 1,
        status: 'approved',
        assignedBy: 2,
        approvedBy: 3,
        notes: 'Welcome',
      );

      final map = r.toJson();

      expect(map['form_id'], equals(1));
      expect(map['user_id'], equals(1));
      expect(map['festival_id'], equals(1));
      expect(map['status'], equals('approved'));
      expect(map['notes'], equals('Welcome'));
    });

    test('fromJson handles null values', () {
      final minimal = <String, dynamic>{
        'form_id': 1,
        'user_id': 2,
      };

      final r = FestivalRegistration.fromJson(minimal);

      expect(r.id, isNull);
      expect(r.formId, equals(1));
      expect(r.userId, equals(2));
      expect(r.festivalId, isNull);
      expect(r.status, equals('pending'));
      expect(r.assignedBy, isNull);
      expect(r.approvedBy, isNull);
      expect(r.notes, isNull);
      expect(r.userName, isNull);
      expect(r.userEmail, isNull);
    });
  });
}
