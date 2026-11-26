import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user_model.dart';
import 'crypto_utils.dart';
import 'secure_storage_service.dart';

/// Servicio singleton que gestiona el estado de autenticación JWT con soporte de refresh token.
///
/// Persiste tokens y claves E2EE en [SecureStorageService] (Keychain/Keystore)
/// y el perfil del usuario en [SharedPreferences] para que las sesiones
/// sobrevivan a los reinicios de la app. Proporciona lógica de renovación de tokens.
class AuthService {
  static const String _tokenKey = 'jwt_token';
  static const String _refreshTokenKey = 'refresh_token';
  static const String _userKey = 'current_user';
  static const String _privateKeyKey = 'e2ee_private_key';
  static const String _publicKeyKey = 'e2ee_public_key';

  /// Claves que deben migrarse desde SharedPreferences al almacén seguro.
  static const List<String> secureKeys = [
    _tokenKey,
    _refreshTokenKey,
    _privateKeyKey,
    _publicKeyKey,
  ];

  static final AuthService _instance = AuthService._internal();
  factory AuthService() => _instance;
  AuthService._internal();

  SecureStorageService _secureStorage = SecureStorageService();

  String? _tokenCache;

  /// Sustituye el almacén seguro (útil en tests).
  @visibleForTesting
  void setSecureStorage(SecureStorageService storage) => _secureStorage = storage;

  /// Migra los secretos legacy de SharedPreferences al almacén seguro.
  Future<void> migrateLegacySecrets() => _secureStorage.migrateFromPreferences(secureKeys);

  /// Devuelve la clave privada E2EE almacenada, o null.
  Future<String?> getPrivateKey() => _secureStorage.read(_privateKeyKey);

  /// Devuelve la clave pública E2EE almacenada, o null.
  Future<String?> getPublicKey() => _secureStorage.read(_publicKeyKey);

  /// Garantiza que existe un par de claves, generándolo si es necesario.
  /// Devuelve la clave pública.
  Future<String> ensureKeyPair() async {
    final existing = await getPrivateKey();
    if (existing != null) {
      final pub = await getPublicKey();
      return pub!;
    }
    final keys = ChatCrypto.generateKeyPair();
    await _secureStorage.write(_privateKeyKey, keys[0]);
    await _secureStorage.write(_publicKeyKey, keys[1]);
    return keys[1];
  }

  /// Guarda el token de acceso JWT (persistido + caché en memoria).
  Future<void> saveToken(String token) async {
    _tokenCache = token;
    await _secureStorage.write(_tokenKey, token);
  }

  /// Devuelve el token JWT almacenado (de la caché en memoria, o lo carga del disco una vez).
  Future<String?> getToken() async {
    if (_tokenCache != null) return _tokenCache;
    _tokenCache = await _secureStorage.read(_tokenKey);
    return _tokenCache;
  }

  /// Guarda el refresh token.
  Future<void> saveRefreshToken(String token) => _secureStorage.write(_refreshTokenKey, token);

  /// Devuelve el refresh token almacenado.
  Future<String?> getRefreshToken() => _secureStorage.read(_refreshTokenKey);

  /// Guarda el perfil del [User] actual.
  Future<void> saveUser(User user) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_userKey, json.encode(user.toJson()));
  }

  /// Devuelve el [User] almacenado, o `null` si no está disponible.
  Future<User?> getCurrentUser() async {
    final prefs = await SharedPreferences.getInstance();
    final jsonString = prefs.getString(_userKey);
    if (jsonString == null) return null;
    try {
      return User.fromJson(json.decode(jsonString));
    } catch (e) {
      debugPrint('Error: $e');
      return null;
    }
  }

  /// Devuelve `true` si hay un token JWT almacenado.
  Future<bool> isLoggedIn() async {
    final token = await getToken();
    return token != null && token.isNotEmpty;
  }

  /// Limpia todos los datos de autenticación (token + refresh token + usuario + claves E2EE).
  Future<void> clear() async {
    _tokenCache = null;
    for (final key in secureKeys) {
      await _secureStorage.delete(key);
    }
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_userKey);
  }
}
