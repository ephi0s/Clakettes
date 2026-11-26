import 'dart:async';

import 'package:clakettes/services/auth_service.dart';
import 'package:clakettes/services/secure_storage_service.dart';

/// Los tests no tienen Keychain/Keystore: se usa el almacén de preferencias
/// mockable, de modo que SharedPreferences.setMockInitialValues({}) reinicia
/// también los secretos entre pruebas.
Future<void> testExecutable(FutureOr<void> Function() testMain) async {
  AuthService().setSecureStorage(SecureStorageService.forTesting(const PreferencesSecureStore()));
  await testMain();
}
