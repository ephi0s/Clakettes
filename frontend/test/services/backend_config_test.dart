import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:clakettes/services/backend_config.dart';

void main() {
  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  group('BackendConfig', () {
    test('getUrl returns default URL when nothing saved', () async {
      final url = await BackendConfig.getUrl();
      expect(url, BackendConfig.platformDefaultUrl);
    });

    test('platformDefaultUrl uses emulator loopback on Android test platform', () {
      expect(BackendConfig.platformDefaultUrl, BackendConfig.androidEmulatorUrl);
    });

    test('setUrl and getUrl round-trip', () async {
      await BackendConfig.setUrl('https://192.168.1.100:8000');
      final url = await BackendConfig.getUrl();
      expect(url, 'https://192.168.1.100:8000');
    });

    test('setUrl overwrites previous value', () async {
      await BackendConfig.setUrl('https://first.url');
      await BackendConfig.setUrl('https://second.url');
      final url = await BackendConfig.getUrl();
      expect(url, 'https://second.url');
    });

    test('getUrl returns persisted value', () async {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('backend_url', 'https://custom.url:8080');

      final url = await BackendConfig.getUrl();
      expect(url, 'https://custom.url:8080');
    });

    test('has defaultUrl constant', () {
      expect(BackendConfig.defaultUrl, 'http://localhost:8000');
    });

    test('allows http only on explicit development hosts', () {
      for (final host in BackendConfig.developmentHosts) {
        expect(BackendConfig.validateUrl('http://$host:8000'), 'http://$host:8000');
      }
      expect(
        () => BackendConfig.validateUrl('http://example.com:8000'),
        throwsA(isA<InvalidBackendUrlException>()),
      );
    });

    test('rejects userinfo, query, fragment and unsupported schemes', () {
      expect(
        () => BackendConfig.validateUrl('https://user:pass@example.com'),
        throwsA(isA<InvalidBackendUrlException>()),
      );
      expect(
        () => BackendConfig.validateUrl('https://example.com?key=value'),
        throwsA(isA<InvalidBackendUrlException>()),
      );
      expect(
        () => BackendConfig.validateUrl('https://example.com#section'),
        throwsA(isA<InvalidBackendUrlException>()),
      );
      expect(
        () => BackendConfig.validateUrl('javascript:alert(1)'),
        throwsA(isA<InvalidBackendUrlException>()),
      );
    });

    test('setUrl rejects invalid URLs without persisting them', () async {
      expect(
        BackendConfig.setUrl('http://example.com'),
        throwsA(isA<InvalidBackendUrlException>()),
      );
      final prefs = await SharedPreferences.getInstance();
      expect(prefs.getString('backend_url'), isNull);
    });
  });
}
