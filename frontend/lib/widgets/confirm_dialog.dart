import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';

/// Muestra un diálogo de confirmación con icono de advertencia, título y mensaje.
///
/// Devuelve `true` cuando el usuario acepta y `false` cuando cancela.
/// Las etiquetas de aceptar/cancelar usan la configuración regional actual.
Future<bool> showConfirmDialog(
  BuildContext context, {
  required String title,
  required String message,
}) async {
  final l10n = AppLocalizations.of(context)!;
  final colorScheme = Theme.of(context).colorScheme;
  final result = await showDialog<bool>(
    context: context,
    builder: (ctx) => AlertDialog(
      icon: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: colorScheme.errorContainer.withAlpha(120),
          shape: BoxShape.circle,
        ),
        child: Icon(Icons.warning_amber_rounded, size: 32, color: colorScheme.error),
      ),
      title: Text(title, textAlign: TextAlign.center),
      content: Text(message, textAlign: TextAlign.center),
      actions: [
        Row(
          children: [
            Expanded(
              child: OutlinedButton(
                onPressed: () => Navigator.of(ctx).pop(false),
                child: Text(l10n.cancel),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: FilledButton(
                onPressed: () => Navigator.of(ctx).pop(true),
                child: Text(l10n.accept),
              ),
            ),
          ],
        ),
      ],
    ),
  );
  return result ?? false;
}
