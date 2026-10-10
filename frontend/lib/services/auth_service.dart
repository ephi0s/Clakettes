import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user_model.dart';
import 'crypto_utils.dart';

/// Servicio singleton que gestiona el estado de autenticación JWT con soporte de refresh token.
///
/// Persiste el token de acceso, el refresh token y el usuario actual en [SharedPreferences]
/// para que las sesiones sobrevivan a los reinicios de la app. Proporciona lógica de
/// renovación de tokens. También gestiona el par de claves E2EE del usuario para el chat cifrado.
class AuthService {
  static const String _tokenKey = 'jwt_token';
  static const String _refreshTokenKey = 'refresh_token';
  static const String _userKey = 'current_user';
  static const String _privateKeyKey = 'e2ee_private_key';
  static const String _publicKeyKey = 'e2ee_public_key';

  static final AuthService _instance = AuthService._internal();
  factory AuthService() => _instance;
  AuthService._internal();

  String? _tokenCache;
  // String? _refreshTokenCache; // kept for future use

  /// Devuelve la clave privada E2EE almacenada, o null.
  Future<String?> getPrivateKey() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_privateKeyKey);
  }

  /// Devuelve la clave pública E2EE almacenada, o null.
  Future<String?> getPublicKey() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_publicKeyKey);
  }

  /// Garantiza que existe un par de claves, generándolo si es necesario.
  /// Devuelve la clave pública.
  Future<String> ensureKeyPair() async {
    final existing = await getPrivateKey();
    if (existing != null) {
      final pub = await getPublicKey();
      return pub!;
    }
    final keys = ChatCrypto.generateKeyPair();
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_privateKeyKey, keys[0]);
    await prefs.setString(_publicKeyKey, keys[1]);
    return keys[1];
  }

  /// Guarda el token de acceso JWT (persistido + caché en memoria).
  Future<void> saveToken(String token) async {
    _tokenCache = token;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, token);
  }

  /// Devuelve el token JWT almacenado (de la caché en memoria, o lo carga del disco una vez).
  Future<String?> getToken() async {
    if (_tokenCache != null) return _tokenCache;
    final prefs = await SharedPreferences.getInstance();
    _tokenCache = prefs.getString(_tokenKey);
    return _tokenCache;
  }

  /// Guarda el refresh token.
  Future<void> saveRefreshToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_refreshTokenKey, token);
  }

  /// Devuelve el refresh token almacenado.
  Future<String?> getRefreshToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_refreshTokenKey);
  }

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
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
    await prefs.remove(_refreshTokenKey);
    await prefs.remove(_userKey);
    await prefs.remove(_privateKeyKey);
    await prefs.remove(_publicKeyKey);
  }
}
