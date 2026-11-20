import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

const _locales = ['en', 'es', 'fr', 'de', 'it', 'ca', 'eu', 'gl', 'oc'];

Map<String, String> _load(String locale) {
  final file = File('assets/l10n/app_$locale.arb');
  final map = jsonDecode(file.readAsStringSync()) as Map<String, dynamic>;
  return {
    for (final entry in map.entries)
      if (entry.value is String) entry.key: entry.value as String
  };
}

Set<String> _placeholders(String value) =>
    RegExp(r'\{(\w+)\}').allMatches(value).map((m) => m.group(1)!).toSet();

void main() {
  test('all ARB files have the same keys and placeholders', () {
    final reference = _load('es');
    for (final locale in _locales) {
      final current = _load(locale);
      expect(current.keys.toSet(), equals(reference.keys.toSet()),
          reason: 'Key mismatch in $locale');
      for (final entry in reference.entries) {
        expect(
          _placeholders(current[entry.key]!),
          equals(_placeholders(entry.value)),
          reason: 'Placeholder mismatch for ${entry.key} in $locale',
        );
      }
    }
  });
}
