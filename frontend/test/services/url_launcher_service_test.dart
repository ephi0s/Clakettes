import 'package:flutter_test/flutter_test.dart';
import 'package:clakettes/services/url_launcher_service.dart';

void main() {
  late List<Uri> launched;

  setUp(() {
    launched = [];
  });

  Future<bool> fakeLaunch(Uri uri) async {
    launched.add(uri);
    return true;
  }

  group('openUrl allowlist', () {
    test('normalizes scheme-less input to https', () async {
      final result = await openUrl('example.com/festival', launcher: fakeLaunch);
      expect(result, isTrue);
      expect(launched.single.toString(), 'https://example.com/festival');
    });

    test('allows http, https, mailto, tel and geo', () async {
      for (final value in [
        'http://localhost:8000',
        'https://example.com',
        'mailto:info@example.com',
        'tel:+34600000000',
        'geo:40.0,-3.0',
      ]) {
        await openUrl(value, launcher: fakeLaunch);
      }
      expect(launched.map((uri) => uri.scheme), ['http', 'https', 'mailto', 'tel', 'geo']);
    });

    test('rejects javascript, file, data and unknown schemes', () async {
      for (final value in [
        'javascript:alert(1)',
        'file:///etc/passwd',
        'data:text/html,<script>alert(1)</script>',
        'ftp://example.com/file',
      ]) {
        expect(await openUrl(value, launcher: fakeLaunch), isFalse);
      }
      expect(launched, isEmpty);
    });

    test('rejects empty input and hosts without authority', () async {
      expect(await openUrl('   ', launcher: fakeLaunch), isFalse);
      expect(await openUrl('https://', launcher: fakeLaunch), isFalse);
      expect(launched, isEmpty);
    });
  });
}
