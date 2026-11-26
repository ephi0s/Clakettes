import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:clakettes/services/secure_storage_service.dart';

void main() {
  group('SecureStorageService', () {
    setUp(() {
      SharedPreferences.setMockInitialValues({});
    });

    test('migrates legacy values and removes them from SharedPreferences', () async {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('jwt_token', 'legacy-token');
      await prefs.setString('e2ee_private_key', 'legacy-key');
      final service = SecureStorageService.forTesting(const PreferencesSecureStore());

      await service.migrateFromPreferences(['jwt_token', 'e2ee_private_key']);

      expect(prefs.getString('jwt_token'), isNull);
      expect(prefs.getString('e2ee_private_key'), isNull);
      expect(await service.read('jwt_token'), 'legacy-token');
      expect(prefs.getString('secure_storage.jwt_token'), 'legacy-token');
      expect(await service.read('e2ee_private_key'), 'legacy-key');
    });

    test('existing secure value wins over legacy value', () async {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('jwt_token', 'legacy-token');
      final service = SecureStorageService.forTesting(const PreferencesSecureStore());
      await service.write('jwt_token', 'new-token');

      await service.migrateFromPreferences(['jwt_token']);

      expect(await service.read('jwt_token'), 'new-token');
      expect(prefs.getString('jwt_token'), isNull);
    });

    test('delete removes only the secure value', () async {
      final prefs = await SharedPreferences.getInstance();
      final service = SecureStorageService.forTesting(const PreferencesSecureStore());
      await service.write('refresh_token', 'secret');

      await service.delete('refresh_token');

      expect(await service.read('refresh_token'), isNull);
      expect(prefs.getString('secure_storage.refresh_token'), isNull);
    });
  });
}
