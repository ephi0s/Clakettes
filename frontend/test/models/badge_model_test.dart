import 'package:flutter_test/flutter_test.dart';
import 'package:clakettes/models/badge_model.dart';

void main() {
  test('ProfileBadge fromJson creates correct object', () {
    final badge = ProfileBadge.fromJson({
      'id': 1,
      'name': 'Veterano',
      'description': 'Tres festivales',
      'image_url': '/uploads/badges/abc.svg',
      'scope': 'festival',
      'category': 'veteran',
      'festival_id': 2,
      'conditions': {'type': 'veteran', 'min_festivals': 3},
      'require_conditions': true,
      'is_active': true,
    });
    expect(badge.id, 1);
    expect(badge.name, 'Veterano');
    expect(badge.isSvg, isTrue);
    expect(badge.conditions?['min_festivals'], 3);
  });

  test('ProfileBadge toJson returns create payload', () {
    final badge = ProfileBadge(name: 'Top', scope: 'platform', conditions: {'type': 'manual'});
    final json = badge.toJson();
    expect(json['name'], 'Top');
    expect(json['scope'], 'platform');
    expect(json['conditions'], {'type': 'manual'});
    expect(json.containsKey('id'), isFalse);
  });

  test('ProfileBadge fromJson handles null optionals', () {
    final badge = ProfileBadge.fromJson({'name': 'X'});
    expect(badge.description, isNull);
    expect(badge.scope, 'platform');
    expect(badge.requireConditions, isTrue);
    expect(badge.isSvg, isFalse);
  });

  test('BadgeAssignment fromJson nests badge', () {
    final assignment = BadgeAssignment.fromJson({
      'id': 5,
      'badge_id': 1,
      'target_user_id': 7,
      'granted_by': 2,
      'reason': 'Great work',
      'badge': {'id': 1, 'name': 'Veterano', 'scope': 'festival'},
    });
    expect(assignment.id, 5);
    expect(assignment.targetUserId, 7);
    expect(assignment.badge?.name, 'Veterano');
  });
}
