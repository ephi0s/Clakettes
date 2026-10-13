import 'dart:async';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Gestiona el locale de la app y notifica a los listeners cuando cambia.
///
/// Singleton creado de forma diferida ([instance]); persiste el locale
/// seleccionado en SharedPreferences y emite los cambios en [onLocaleChanged].
/// Depende de `shared_preferences`. Se carga al arrancar mediante [load],
/// tras lo cual el locale actual está disponible desde [currentLocale].
class LocaleService {
  static const String _key = 'app_locale';
  static LocaleService? _instance;

  final StreamController<Locale> _controller = StreamController<Locale>.broadcast();
  Locale? _locale;

  LocaleService._();

  /// El singleton compartido, creado de forma diferida en el primer acceso.
  static LocaleService get instance {
    _instance ??= LocaleService._();
    return _instance!;
  }

  /// Emite el nuevo locale cada vez que se cambia mediante [setLocale].
  Stream<Locale> get onLocaleChanged => _controller.stream;

  /// El locale activo, o `null` antes de que [load] complete.
  Locale? get currentLocale => _locale;

  /// Lista de locales soportados por la app.
  static const List<Locale> supportedLocales = [
    Locale('en'),
    Locale('es'),
    Locale('fr'),
    Locale('de'),
    Locale('it'),
    Locale('ca'),
    Locale('eu'),
    Locale('gl'),
    Locale('oc'),
  ];

  /// Nombres legibles de cada locale para mostrar en la UI.
  static const Map<String, String> localeNames = {
    'en': 'English',
    'es': 'Español',
    'fr': 'Français',
    'de': 'Deutsch',
    'it': 'Italiano',
    'ca': 'Català',
    'eu': 'Euskara',
    'gl': 'Galego',
    'oc': 'Aranés',
  };

  /// Restaura el locale persistido previamente, si existe.
  ///
  /// Devuelve el locale restaurado o `null` si no se había almacenado ninguno.
  Future<Locale?> load() async {
    final prefs = await SharedPreferences.getInstance();
    final code = prefs.getString(_key);
    if (code != null) {
      final supported = supportedLocales.any((l) => l.languageCode == code);
      _locale = Locale(supported ? code : 'en');
    }
    return _locale;
  }

  /// Establece el locale activo, lo persiste y notifica a los suscriptores.
  Future<void> setLocale(Locale locale) async {
    _locale = locale;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_key, locale.languageCode);
    _controller.add(locale);
  }

  /// Cierra el stream de cambios y libera los recursos.
  void dispose() {
    _controller.close();
  }
}
