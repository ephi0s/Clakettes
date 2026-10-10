import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Resuelve y persiste la URL base del backend usada por la capa de API.
///
/// Multiplataforma:
/// - Web y escritorio/iOS: `http://localhost:8000` (mismo host).
/// - Android (emulador): `http://10.0.2.2:8000` (localhost del emulador es el
///   propio dispositivo virtual, no el host).
/// - Dispositivo físico o producción: override con
///   `--dart-define=BACKEND_URL=https://...` o la pantalla de configuración
///   (persiste en SharedPreferences vía [setUrl]).
class BackendConfig {
  static const String _key = 'backend_url';

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

  /// URL efectiva: guardada > compilación > default por plataforma.
  static Future<String> getUrl() async {
    final prefs = await SharedPreferences.getInstance();
    final saved = prefs.getString(_key);
    if (saved != null) return saved;
    if (compileTimeUrl != defaultUrl) return compileTimeUrl;
    return platformDefaultUrl;
  }

  /// Persiste una URL de backend para que sobreviva a los reinicios.
  static Future<void> setUrl(String url) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_key, url);
  }
}
