import 'dart:convert';
import 'dart:io';

import 'package:clakettes/l10n/app_localizations.dart';
import 'package:clakettes/services/api_service.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

AppLocalizations _l10n(String lang) {
  final raw = File('assets/l10n/app_$lang.arb').readAsStringSync();
  return AppLocalizations.test(
      Locale(lang), Map<String, dynamic>.from(json.decode(raw)));
}

void main() {
  group('errorFor', () {
    test('maps status codes in Spanish', () {
      final l10n = _l10n('es');
      expect(l10n.errorFor(ApiException('x', statusCode: 404)), l10n.errorNotFound);
      expect(l10n.errorFor(ApiException('x', statusCode: 403)), l10n.errorForbidden);
      expect(l10n.errorFor(ApiException('x', statusCode: 409)), l10n.errorConflict);
      expect(l10n.errorFor(ApiException('x', statusCode: 422)), l10n.errorUnprocessable);
      expect(l10n.errorFor(ApiException('x', statusCode: 429)), l10n.errorTooMany);
      expect(l10n.errorFor(ApiException('x', statusCode: 500)), l10n.errorServer);
      expect(l10n.errorFor(ApiException('x', timedOut: true)), l10n.errorTimeout);
      expect(l10n.errorFor(ApiException('x')), l10n.errorNetwork);
      expect(l10n.errorFor(UnauthorizedException()), l10n.errorUnauthorized);
    });

    test('every locale resolves all error keys', () {
      for (final lang in ['en', 'es', 'fr', 'de', 'it', 'ca', 'eu', 'gl', 'oc']) {
        final l10n = _l10n(lang);
        expect(l10n.errorFor(ApiException('x', statusCode: 404)), isNotEmpty);
        expect(l10n.errorFor(ApiException('x', statusCode: 500)), isNotEmpty);
        expect(l10n.errorFor(ApiException('x', timedOut: true)), isNotEmpty);
        expect(l10n.errorFor(UnauthorizedException()), isNotEmpty);
      }
    });

    test('no English technical leak in Spanish messages', () {
      final l10n = _l10n('es');
      final msg = l10n.errorFor(ApiException('GET /x failed (404)', statusCode: 404));
      expect(msg.contains('GET'), isFalse);
      expect(msg.contains('failed'), isFalse);
    });
  });
}
