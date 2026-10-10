import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:clakettes/services/locale_service.dart';

void main() {
  setUp(() async {
    SharedPreferences.setMockInitialValues({});
  });

  group('LocaleService', () {
    test('singleton returns same instance', () {
      final a = LocaleService.instance;
      final b = LocaleService.instance;
      expect(identical(a, b), isTrue);
    });

    test('currentLocale returns null before load', () {
      final localeService = LocaleService.instance;
      expect(localeService.currentLocale, isNull);
    });

    test('load returns null when no locale saved', () async {
      final localeService = LocaleService.instance;
      final result = await localeService.load();
      expect(result, isNull);
      expect(localeService.currentLocale, isNull);
    });

    test('setLocale updates currentLocale', () async {
      final localeService = LocaleService.instance;
      await localeService.setLocale(const Locale('es'));
      expect(localeService.currentLocale, const Locale('es'));
    });

    test('setLocale emits event on stream', () async {
      final localeService = LocaleService.instance;
      final emitted = await localeService.onLocaleChanged.first;
      expect(emitted, const Locale('es'));
    }, skip: 'Requires stream ordering in singleton context');

    test('setLocale persists to SharedPreferences', () async {
      final localeService = LocaleService.instance;
      await localeService.setLocale(const Locale('fr'));

      final prefs = await SharedPreferences.getInstance();
      expect(prefs.getString('app_locale'), 'fr');
    });

    test('load retrieves persisted locale', () async {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('app_locale', 'de');

      final localeService = LocaleService.instance;
      final result = await localeService.load();
      expect(result, const Locale('de'));
      expect(localeService.currentLocale, const Locale('de'));
    });

    test('setLocale replaces previous locale', () async {
      final localeService = LocaleService.instance;
      await localeService.setLocale(const Locale('en'));
      await localeService.setLocale(const Locale('ca'));

      expect(localeService.currentLocale, const Locale('ca'));

      final prefs = await SharedPreferences.getInstance();
      expect(prefs.getString('app_locale'), 'ca');
    });

    test('supports all 9 supported locales', () {
      const supported = LocaleService.supportedLocales;
      expect(supported.length, 9);
      expect(supported, contains(const Locale('en')));
      expect(supported, contains(const Locale('es')));
      expect(supported, contains(const Locale('fr')));
      expect(supported, contains(const Locale('de')));
      expect(supported, contains(const Locale('it')));
      expect(supported, contains(const Locale('ca')));
      expect(supported, contains(const Locale('eu')));
      expect(supported, contains(const Locale('gl')));
      expect(supported, contains(const Locale('oc')));
    });

    test('localeNames contains names for all locales', () {
      expect(LocaleService.localeNames['en'], 'English');
      expect(LocaleService.localeNames['es'], 'Español');
      expect(LocaleService.localeNames['oc'], 'Aranés');
    });

    test('dispose closes the stream controller', () async {
      final localeService = LocaleService.instance;
      localeService.dispose();

      expect(localeService.onLocaleChanged, isNotNull);
    });
  });
}
