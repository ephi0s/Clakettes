import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';

/// Muestra un SnackBar flotante unificado (reemplaza ~113 ScaffoldMessenger directos).
void showAppSnack(BuildContext context, String message, {SnackBarAction? action}) {
  ScaffoldMessenger.of(context)
    ..hideCurrentSnackBar()
    ..showSnackBar(
      SnackBar(
        content: Text(message),
        behavior: SnackBarBehavior.floating,
        action: action,
      ),
    );
}

/// Avatar de perfil accesible con imagen de red, respaldo de iniciales y semántica.
/// 
/// Características:
/// - Imagen de red con ResizeImage para eficiencia de memoria
/// - ExcludeSemantics en las iniciales decorativas (los lectores de pantalla usan semanticLabel)
/// - Envoltorio Semantics para el anuncio del lector de pantalla
/// - Colores, radio e icono de respaldo personalizables
class ProfileAvatar extends StatelessWidget {
  final String? imageUrl;
  final String fallbackText;
  final double radius;
  final Color? backgroundColor;
  final Color? foregroundColor;
  final IconData fallbackIcon;
  final String semanticLabel;

  const ProfileAvatar({
    super.key,
    this.imageUrl,
    required this.fallbackText,
    this.radius = 60,
    this.backgroundColor,
    this.foregroundColor,
    this.fallbackIcon = Icons.person_rounded,
    this.semanticLabel = '',
  });

  @override
  Widget build(BuildContext context) {
    final initials = fallbackText.isNotEmpty ? fallbackText.substring(0, 1).toUpperCase() : '?';
    final colorScheme = Theme.of(context).colorScheme;
    final bg = backgroundColor ?? colorScheme.primaryContainer;
    final fg = foregroundColor ?? colorScheme.onPrimaryContainer;

    return Semantics(
      label: semanticLabel,
      child: CircleAvatar(
        radius: radius,
        backgroundColor: imageUrl == null ? bg : null,
        backgroundImage: imageUrl != null
            ? ResizeImage.resizeIfNeeded(
                (radius * 2 * MediaQuery.devicePixelRatioOf(context)).round(),
                (radius * 2 * MediaQuery.devicePixelRatioOf(context)).round(),
                NetworkImage(imageUrl!),
              )
            : null,
        child: imageUrl == null
            ? ExcludeSemantics(
                child: Text(
                  initials,
                  style: TextStyle(
                    fontSize: radius * 0.55,
                    color: fg,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              )
            : null,
      ),
    );
  }
}

/// Fila de información accesible con icono, etiqueta y acción de toque opcional.
/// 
/// Accesibilidad:
/// - Icono envuelto en ExcludeSemantics (decorativo)
/// - Etiqueta semántica anunciada para los lectores de pantalla
/// - InkWell para filas pulsables con semántica adecuada
class InfoRow extends StatelessWidget {
  final IconData icon;
  final String semanticLabel;
  final String text;
  final Color? iconColor;
  final Widget? trailing;
  final VoidCallback? onTap;

  const InfoRow({
    super.key,
    required this.icon,
    required this.semanticLabel,
    required this.text,
    this.iconColor,
    this.trailing,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    final content = Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        children: [
          ExcludeSemantics(
            child: Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: colorScheme.primaryContainer.withAlpha(60),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(
                icon,
                size: 18,
                color: iconColor ?? colorScheme.primary,
              ),
            ),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Text(
              text,
              style: theme.textTheme.bodyLarge?.copyWith(
                color: onTap != null
                    ? colorScheme.primary
                    : colorScheme.onSurface,
                decoration:
                    onTap != null ? TextDecoration.underline : null,
              ),
            ),
          ),
          if (trailing != null) trailing!,
        ],
      ),
    );

    if (onTap != null) {
      return Semantics(
        label: semanticLabel,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(8),
          child: content,
        ),
      );
    }

    return Semantics(
      label: semanticLabel,
      child: content,
    );
  }
}

/// Indicador de estado accesible (activo/inactivo) con variantes de chip o fila.
/// 
/// Accesibilidad:
/// - Icono envuelto en ExcludeSemantics
/// - La etiqueta semántica anuncia el estado
/// - El color no se usa solo para transmitir significado (icono + etiqueta)
class StatusIndicator extends StatelessWidget {
  final bool isActive;
  final String activeLabel;
  final String inactiveLabel;
  final IconData activeIcon;
  final IconData inactiveIcon;
  final Color? activeColor;
  final Color? inactiveColor;
  final bool useChip;
  final String semanticLabel;

  const StatusIndicator({
    super.key,
    required this.isActive,
    required this.activeLabel,
    required this.inactiveLabel,
    this.activeIcon = Icons.check_circle_rounded,
    this.inactiveIcon = Icons.cancel_rounded,
    this.activeColor,
    this.inactiveColor,
    this.useChip = false,
    this.semanticLabel = '',
  });

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;
    final label = isActive ? activeLabel : inactiveLabel;
    final icon = isActive ? activeIcon : inactiveIcon;
    final color = isActive
        ? (activeColor ?? cs.primary)
        : (inactiveColor ?? cs.onSurfaceVariant);

    return Semantics(
      label: semanticLabel.isNotEmpty ? semanticLabel : label,
      child: useChip
          ? Chip(
              avatar: ExcludeSemantics(
                child: Icon(icon, size: 16, color: color),
              ),
              label: Text(label, style: textTheme.labelLarge?.copyWith(color: color)),
              backgroundColor: color.withAlpha(20),
              side: BorderSide.none,
              padding: const EdgeInsets.symmetric(horizontal: 4),
              visualDensity: VisualDensity.compact,
            )
          : Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                ExcludeSemantics(
                  child: Icon(icon, color: color, size: 16),
                ),
                const SizedBox(width: 4),
                Text(label, style: textTheme.labelLarge?.copyWith(color: color)),
              ],
            ),
    );
  }
}

/// Tarjeta de elemento de lista accesible con contenido inicial, título, subtítulo, final y manejadores de toque.
/// 
/// Accesibilidad:
/// - Etiqueta semántica para el lector de pantalla
/// - Tarjeta con borde sutil para separación visual
/// - InkWell para la respuesta táctil
/// - Icono de chevron excluido de la semántica
class ListItemCard extends StatelessWidget {
  final Widget leading;
  final String title;
  final String titleSemanticLabel;
  final Widget? subtitle;
  final Widget? trailing;
  final VoidCallback? onTap;
  final VoidCallback? onLongPress;
  final String? semanticLabel;

  const ListItemCard({
    super.key,
    required this.leading,
    required this.title,
    this.titleSemanticLabel = '',
    this.subtitle,
    this.trailing,
    this.onTap,
    this.onLongPress,
    this.semanticLabel,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;

    return Semantics(
      label: semanticLabel ?? title,
      child: Card(
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: BorderSide(color: colorScheme.outlineVariant.withAlpha(30)),
        ),
        child: InkWell(
          borderRadius: BorderRadius.circular(16),
          onTap: onTap,
          onLongPress: onLongPress,
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 4),
            child: ListTile(
              leading: leading,
              title: Text(title, style: textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w600, color: colorScheme.onSurface)),
              subtitle: subtitle,
              trailing: trailing ?? Icon(Icons.chevron_right_rounded, color: colorScheme.onSurfaceVariant.withAlpha(120), size: 20),
            ),
          ),
        ),
      ),
    );
  }
}

/// Encabezado semántico para la navegación por lector de pantalla.
/// 
/// Uso: envuelve los títulos de sección para que los usuarios de lectores de pantalla
/// puedan navegar por encabezados. Equivalente a <h1>-<h6> de HTML para accesibilidad.
class SemanticHeader extends StatelessWidget {
  final String text;
  final TextStyle? style;
  final TextAlign? textAlign;

  const SemanticHeader({
    super.key,
    required this.text,
    this.style,
    this.textAlign,
  });

  @override
  Widget build(BuildContext context) {
    return Semantics(
      header: true,
      label: text,
      child: Text(
        text,
        style: style,
        textAlign: textAlign,
      ),
    );
  }
}

/// TextFormField accesible con etiqueta semántica para lectores de pantalla.
/// 
/// Envuelve TextFormField en Semantics para un anuncio adecuado.
/// Admite todas las propiedades estándar de TextFormField.
class SemanticTextField extends StatelessWidget {
  final TextEditingController controller;
  final String label;
  final String semanticLabel;
  final String? helperText;
  final TextInputType? keyboardType;
  final TextInputAction? textInputAction;
  final int? maxLength;
  final int? maxLines;
  final bool obscureText;
  final String? Function(String?)? validator;
  final void Function(String)? onSubmitted;
  final Widget? suffixIcon;
  final Widget? prefixIcon;

  const SemanticTextField({
    super.key,
    required this.controller,
    required this.label,
    required this.semanticLabel,
    this.helperText,
    this.keyboardType,
    this.textInputAction,
    this.maxLength,
    this.maxLines = 1,
    this.obscureText = false,
    this.validator,
    this.onSubmitted,
    this.suffixIcon,
    this.prefixIcon,
  });

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: semanticLabel,
      child: TextFormField(
        controller: controller,
        decoration: InputDecoration(
          labelText: label,
          helperText: helperText,
          suffixIcon: suffixIcon,
          prefixIcon: prefixIcon,
        ),
        keyboardType: keyboardType,
        textInputAction: textInputAction,
        maxLength: maxLength,
        maxLines: maxLines,
        obscureText: obscureText,
        validator: validator,
        onFieldSubmitted: onSubmitted,
      ),
    );
  }
}

/// Contenido de bottom sheet que pide al usuario iniciar sesión para una acción protegida.
/// 
/// Usado por MainScaffold al acceder a pestañas protegidas por autenticación.
/// Accesible: encabezado semántico y semántica de botón adecuada.
class LoginPromptSheet extends StatelessWidget {
  final VoidCallback onLogin;
  final String? title;
  final String? subtitle;

  const LoginPromptSheet({
    super.key,
    required this.onLogin,
    this.title,
    this.subtitle,
  });

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final t = title ?? l10n?.login ?? '';
    final s = subtitle ?? l10n?.loginRequired ?? '';
    return Padding(
      padding: EdgeInsets.fromLTRB(24, 24, 24, MediaQuery.of(context).viewInsets.bottom + 24),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: colorScheme.primaryContainer,
              shape: BoxShape.circle,
            ),
            child: Icon(Icons.lock_outline_rounded, size: 32, color: colorScheme.onPrimaryContainer),
          ),
          const SizedBox(height: 20),
          Text(t, style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          Text(
            s,
            style: theme.textTheme.bodyMedium?.copyWith(color: colorScheme.onSurfaceVariant),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 28),
          SizedBox(
            width: double.infinity,
            child: FilledButton(
              onPressed: () {
                Navigator.pop(context);
                onLogin();
              },
              child: Text(t),
            ),
          ),
          const SizedBox(height: 8),
        ],
      ),
    );
  }
}
