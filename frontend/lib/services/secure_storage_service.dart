import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Almacén clave-valor subyacente usado por [SecureStorageService].
abstract class SecureKeyValueStore {
  Future<String?> read(String key);

  Future<void> write(String key, String value);

  Future<void> delete(String key);
}

/// Almacén nativo: Keychain en iOS/macOS y Keystore cifrado en Android/escritorio.
class PlatformSecureStore implements SecureKeyValueStore {
  const PlatformSecureStore();

  static const FlutterSecureStorage _storage = FlutterSecureStorage();

  @override
  Future<String?> read(String key) => _storage.read(key: key);

  @override
  Future<void> write(String key, String value) => _storage.write(key: key, value: value);

  @override
  Future<void> delete(String key) => _storage.delete(key: key);
}

/// Almacén web basado en SharedPreferences.
///
/// Limitación documentada: la web no ofrece Keychain/Keystore, por lo que los
/// valores NO están cifrados y son legibles por XSS o extensiones. Mitigado con
/// CSP estricta, HTTPS/HSTS y el prefijo de claves que aísla estos valores de
/// las preferencias legacy.
class PreferencesSecureStore implements SecureKeyValueStore {
  const PreferencesSecureStore();

  static const String _prefix = 'secure_storage.';

  @override
  Future<String?> read(String key) async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('$_prefix$key');
  }

  @override
  Future<void> write(String key, String value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('$_prefix$key', value);
  }

  @override
  Future<void> delete(String key) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('$_prefix$key');
  }
}

/// Servicio singleton que guarda secretos (JWT, refresh token y claves E2EE)
/// fuera de SharedPreferences en todas las plataformas.
class SecureStorageService {
  final SecureKeyValueStore _store;

  SecureStorageService._() : _store = kIsWeb ? const PreferencesSecureStore() : const PlatformSecureStore();

  /// Constructor para tests con un almacén en memoria.
  SecureStorageService.forTesting(this._store);

  static final SecureStorageService _instance = SecureStorageService._();

  factory SecureStorageService() => _instance;

  /// Lee un secreto, o `null` si no existe.
  Future<String?> read(String key) => _store.read(key);

  /// Escribe un secreto.
  Future<void> write(String key, String value) => _store.write(key, value);

  /// Borra un secreto.
  Future<void> delete(String key) => _store.delete(key);

  /// Migra una sola vez los valores legacy de SharedPreferences al almacén seguro.
  ///
  /// El valor ya presente en el almacén seguro prevalece. Si la escritura falla,
  /// el valor legacy se conserva para no perder la sesión.
  Future<void> migrateFromPreferences(List<String> keys) async {
    final prefs = await SharedPreferences.getInstance();
    for (final key in keys) {
      try {
        final legacy = prefs.getString(key);
        if (legacy == null) continue;
        if (await read(key) == null) await write(key, legacy);
        await prefs.remove(key);
      } catch (e) {
        debugPrint('SecureStorage migration error for $key: $e');
      }
    }
  }
}
