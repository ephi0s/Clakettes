import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../services/locale_service.dart';

/// Muestra la hoja inferior de selección de idioma y persiste la elección.
///
/// Reutilizable desde cualquier pantalla, también sin autenticación.
/// Al seleccionar un idioma notifica a los suscriptores mediante
/// [LocaleService.setLocale], lo que reconstruye [MaterialApp] con el nuevo locale.
Future<void> showLanguagePicker(BuildContext context) {
  final current = LocaleService.instance.currentLocale?.languageCode ?? 'en';
  return showModalBottomSheet(
    context: context,
    builder: (ctx) {
      final l10n = AppLocalizations.of(context)!;
      return SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
              child: Semantics(
                header: true,
                child: Text(
                  l10n.language,
                  style: Theme.of(ctx).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
                ),
              ),
            ),
            for (final locale in LocaleService.supportedLocales)
              _LanguageTile(code: locale.languageCode, selected: locale.languageCode == current),
          ],
        ),
      );
    },
  );
}

/// ListTile individual de un idioma dentro de [showLanguagePicker].
class _LanguageTile extends StatelessWidget {
  const _LanguageTile({required this.code, required this.selected});

  final String code;
  final bool selected;

  @override
  Widget build(BuildContext context) {
    final name = LocaleService.localeNames[code] ?? code;
    return ListTile(
      leading: Icon(
        selected ? Icons.radio_button_checked : Icons.radio_button_unchecked,
        color: selected ? Theme.of(context).colorScheme.primary : null,
      ),
      title: Text(name),
      onTap: () {
        LocaleService.instance.setLocale(Locale(code));
        Navigator.pop(context);
      },
    );
  }
}
