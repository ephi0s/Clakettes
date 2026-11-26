import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Excepción lanzada cuando una URL de backend no cumple la política de seguridad.
class InvalidBackendUrlException implements Exception {
  final String message;

  const InvalidBackendUrlException(this.message);

  @override
  String toString() => 'InvalidBackendUrlException: $message';
}

/// Resuelve y persiste la URL base del backend usada por la capa de API.
///
/// Multiplataforma:
/// - Web y escritorio/iOS: `http://localhost:8000` (mismo host).
/// - Android (emulador): `http://10.0.2.2:8000` (localhost del emulador es el
///   propio dispositivo virtual, no el host).
/// - Dispositivo físico o producción: override con
///   `--dart-define=BACKEND_URL=https://...` o la pantalla de configuración
///   (persiste en SharedPreferences vía [setUrl]).
///
/// Toda URL configurada debe ser https, salvo los hosts de desarrollo
/// explícitamente permitidos. Se rechazan userinfo, query y fragment.
class BackendConfig {
  static const String _key = 'backend_url';

  /// Hosts donde se tolera http para desarrollo local.
  static const Set<String> developmentHosts = {'localhost', '127.0.0.1', '10.0.2.2'};

  /// URL base por defecto del backend en host local.
  static const String defaultUrl = 'http://localhost:8000';

  /// URL por defecto en el emulador de Android.
  static const String androidEmulatorUrl = 'http://10.0.2.2:8000';

  /// Default según plataforma cuando no hay override ni valor guardado.
  static String get platformDefaultUrl {
    if (!kIsWeb && defaultTargetPlatform == TargetPlatform.android) {
      return androidEmulatorUrl;
    }
    return defaultUrl;
  }

  /// Override de compilación mediante `--dart-define=BACKEND_URL=...`
  static const String compileTimeUrl = String.fromEnvironment(
    'BACKEND_URL',
    defaultValue: defaultUrl,
  );

  /// Valida una URL de backend y devuelve su forma normalizada (sin barra final).
  static String validateUrl(String value) {
    final trimmed = value.trim();
    final uri = Uri.tryParse(trimmed);
    if (uri == null || (uri.scheme != 'http' && uri.scheme != 'https') || uri.host.isEmpty) {
      throw const InvalidBackendUrlException('La URL del backend debe ser http o https con un host válido');
    }
    if (uri.userInfo.isNotEmpty) {
      throw const InvalidBackendUrlException('La URL del backend no puede incluir credenciales');
    }
    if (uri.hasQuery || uri.hasFragment) {
      throw const InvalidBackendUrlException('La URL del backend no puede incluir query ni fragment');
    }
    if (uri.scheme == 'http' && !developmentHosts.contains(uri.host.toLowerCase())) {
      throw const InvalidBackendUrlException('La URL del backend debe usar https salvo en localhost, 127.0.0.1 o 10.0.2.2');
    }
    final normalized = trimmed.endsWith('/') ? trimmed.substring(0, trimmed.length - 1) : trimmed;
    return normalized;
  }

  /// URL efectiva: guardada > compilación > default por plataforma.
  static Future<String> getUrl() async {
    final prefs = await SharedPreferences.getInstance();
    final saved = prefs.getString(_key);
    if (saved != null) return saved;
    if (compileTimeUrl != defaultUrl) return compileTimeUrl;
    return platformDefaultUrl;
  }

  /// Persiste una URL de backend validada para que sobreviva a los reinicios.
  static Future<void> setUrl(String url) async {
    final normalized = validateUrl(url);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_key, normalized);
  }
}
