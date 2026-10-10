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
      await BackendConfig.setUrl('http://192.168.1.100:8000');
      final url = await BackendConfig.getUrl();
      expect(url, 'http://192.168.1.100:8000');
    });

    test('setUrl overwrites previous value', () async {
      await BackendConfig.setUrl('http://first.url');
      await BackendConfig.setUrl('http://second.url');
      final url = await BackendConfig.getUrl();
      expect(url, 'http://second.url');
    });

    test('getUrl returns persisted value', () async {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('backend_url', 'http://custom.url:8080');

      final url = await BackendConfig.getUrl();
      expect(url, 'http://custom.url:8080');
    });

    test('has defaultUrl constant', () {
      expect(BackendConfig.defaultUrl, 'http://localhost:8000');
    });
  });
}
