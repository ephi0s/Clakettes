import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:clakettes/services/auth_service.dart';
import 'package:clakettes/services/secure_storage_service.dart';
import 'package:clakettes/models/user_model.dart';

class _MemorySecureStore implements SecureKeyValueStore {
  final Map<String, String> values = {};

  @override
  Future<String?> read(String key) async => values[key];

  @override
  Future<void> write(String key, String value) async => values[key] = value;

  @override
  Future<void> delete(String key) async => values.remove(key);
}

void main() {
  late User testUser;
  late _MemorySecureStore store;

  setUp(() async {
    SharedPreferences.setMockInitialValues({});
    store = _MemorySecureStore();
    AuthService().setSecureStorage(SecureStorageService.forTesting(store));
    await AuthService().clear();
    testUser = User(
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      fullName: 'Test User',
      role: 'user',
      isActive: true,
      isPublic: true,
    );
  });

  group('AuthService', () {
    test('singleton returns same instance', () {
      final a = AuthService();
      final b = AuthService();
      expect(identical(a, b), isTrue);
    });

    test('saveToken and getToken round-trip', () async {
      final auth = AuthService();
      await auth.saveToken('my-jwt-token');
      final token = await auth.getToken();
      expect(token, 'my-jwt-token');
    });

    test('tokens are not written to SharedPreferences', () async {
      final auth = AuthService();
      await auth.saveToken('my-jwt-token');
      await auth.saveRefreshToken('my-refresh-token');
      final prefs = await SharedPreferences.getInstance();
      expect(prefs.getString('jwt_token'), isNull);
      expect(prefs.getString('refresh_token'), isNull);
      expect(store.values['jwt_token'], 'my-jwt-token');
      expect(store.values['refresh_token'], 'my-refresh-token');
    });

    test('getToken returns null when no token saved', () async {
      final auth = AuthService();
      final token = await auth.getToken();
      expect(token, isNull);
    });

    test('saveToken overwrites previous token', () async {
      final auth = AuthService();
      await auth.saveToken('first-token');
      await auth.saveToken('second-token');
      final token = await auth.getToken();
      expect(token, 'second-token');
    });

    test('saveRefreshToken and getRefreshToken round-trip', () async {
      final auth = AuthService();
      await auth.saveRefreshToken('my-refresh-token');
      final token = await auth.getRefreshToken();
      expect(token, 'my-refresh-token');
    });

    test('E2EE keys are stored in secure storage', () async {
      final pub = await AuthService().ensureKeyPair();
      expect(pub, isNotEmpty);
      expect(await AuthService().getPrivateKey(), isNotEmpty);
      expect(await AuthService().getPublicKey(), pub);
      final prefs = await SharedPreferences.getInstance();
      expect(prefs.getString('e2ee_private_key'), isNull);
      expect(prefs.getString('e2ee_public_key'), isNull);
    });

    test('isLoggedIn returns false when no token', () async {
      final auth = AuthService();
      final loggedIn = await auth.isLoggedIn();
      expect(loggedIn, isFalse);
    });

    test('isLoggedIn returns true when token exists', () async {
      final auth = AuthService();
      await auth.saveToken('some-token');
      final loggedIn = await auth.isLoggedIn();
      expect(loggedIn, isTrue);
    });

    test('saveUser and getCurrentUser round-trip', () async {
      final auth = AuthService();
      await auth.saveUser(testUser);
      final user = await auth.getCurrentUser();
      expect(user, isNotNull);
      expect(user!.id, testUser.id);
      expect(user.username, testUser.username);
      expect(user.email, testUser.email);
    });

    test('getCurrentUser returns null when no user saved', () async {
      final auth = AuthService();
      final user = await auth.getCurrentUser();
      expect(user, isNull);
    });

    test('clear removes all auth data', () async {
      final auth = AuthService();
      await auth.saveToken('token');
      await auth.saveRefreshToken('refresh');
      await auth.saveUser(testUser);
      await auth.ensureKeyPair();

      await auth.clear();

      expect(await auth.getToken(), isNull);
      expect(await auth.getRefreshToken(), isNull);
      expect(await auth.getCurrentUser(), isNull);
      expect(await auth.getPrivateKey(), isNull);
      expect(store.values, isEmpty);
      expect(await auth.isLoggedIn(), isFalse);
    });

    test('clear also clears in-memory token cache', () async {
      final auth = AuthService();
      await auth.saveToken('cached-token');
      await auth.clear();
      final token = await auth.getToken();
      expect(token, isNull);
    });

    test('token is cached in memory after first load', () async {
      final auth = AuthService();
      await auth.saveToken('disk-token');
      await store.delete('jwt_token');
      final token = await auth.getToken();
      expect(token, 'disk-token');
    });
  });
}
