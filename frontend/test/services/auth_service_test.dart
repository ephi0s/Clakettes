import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:clakettes/services/auth_service.dart';
import 'package:clakettes/models/user_model.dart';

void main() {
  late User testUser;

  setUp(() async {
    SharedPreferences.setMockInitialValues({});
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

      await auth.clear();

      expect(await auth.getToken(), isNull);
      expect(await auth.getRefreshToken(), isNull);
      expect(await auth.getCurrentUser(), isNull);
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
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove('jwt_token');
      final token = await auth.getToken();
      expect(token, 'disk-token');
    });
  });
}
