import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../models/location_tag_model.dart';

/// Editor de las etiquetas de una ubicación: chips aprobados y pendientes más proponer/revocar.
///
/// Úsalo donde usuarios o administradores gestionen etiquetas de ubicación. Los chips
/// distinguen etiquetas aprobadas de propuestas; una pulsación larga abre un menú para
/// aprobar (admin) o revocar/eliminar, y un chip de añadir abre un diálogo para proponer una nueva.
class LocationTagEditor extends StatelessWidget {
  final List<LocationTag> tags;
  final bool isAdmin;
  final ValueChanged<String> onPropose;
  final void Function(LocationTag tag) onRevoke;

  const LocationTagEditor({
    super.key,
    required this.tags,
    required this.isAdmin,
    required this.onPropose,
    required this.onRevoke,
  });

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

    final proposed = tags.where((t) => t.status == 'approved').toList();
    final pending = tags.where((t) => t.status == 'proposed').toList();
    final allTags = [...proposed, ...pending];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        Wrap(
          spacing: 8,
          runSpacing: 6,
          children: [
            ...allTags.map((tag) => _buildTagChip(context, tag)),
            _AddTagChip(
              onTap: () => _showProposeDialog(context, l10n),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildTagChip(BuildContext context, LocationTag tag) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final isPending = tag.status == 'proposed';

    return Semantics(
      label: tag.tag,
      button: true,
      child: GestureDetector(
        onLongPress: () => _showTagMenu(context, tag),
        child: Chip(
          label: Text(
            tag.tag,
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w500,
              color: isPending ? colorScheme.onSurfaceVariant : colorScheme.onSurface,
            ),
          ),
          backgroundColor: isPending
              ? colorScheme.surfaceContainerHighest.withAlpha(80)
              : colorScheme.primaryContainer.withAlpha(60),
          side: isPending
              ? BorderSide(color: colorScheme.outlineVariant.withAlpha(60))
              : BorderSide.none,
          padding: const EdgeInsets.symmetric(horizontal: 4),
          visualDensity: VisualDensity.compact,
          materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
          avatar: isPending
              ? ExcludeSemantics(
                  child: Icon(Icons.schedule_rounded, size: 14, color: colorScheme.onSurfaceVariant),
                )
              : null,
        ),
      ),
    );
  }

  /// Muestra un menú en bottom sheet con las acciones de aprobar/revocar para la etiqueta dada.
  void _showTagMenu(BuildContext context, LocationTag tag) {
    final l10n = AppLocalizations.of(context)!;
    showModalBottomSheet(
      context: context,
      builder: (ctx) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Padding(
              padding: const EdgeInsets.all(16),
              child: Text(
                tag.tag,
                style: Theme.of(ctx).textTheme.titleMedium,
              ),
            ),
            if (isAdmin && tag.status == 'proposed') ...[
              ListTile(
                leading: const Icon(Icons.check_circle_rounded),
                title: Text(l10n.approve),
                onTap: () {
                  Navigator.pop(ctx);
                },
              ),
            ],
            if (isAdmin) ...[
              ListTile(
                leading: Icon(Icons.remove_circle_outline_rounded, color: Theme.of(ctx).colorScheme.error),
                title: Text(l10n.revokeTag, style: TextStyle(color: Theme.of(ctx).colorScheme.error)),
                onTap: () {
                  Navigator.pop(ctx);
                  onRevoke(tag);
                },
              ),
            ] else ...[
              ListTile(
                leading: Icon(Icons.remove_circle_outline_rounded, color: Theme.of(ctx).colorScheme.error),
                title: Text(l10n.delete, style: TextStyle(color: Theme.of(ctx).colorScheme.error)),
                onTap: () {
                  Navigator.pop(ctx);
                  onRevoke(tag);
                },
              ),
            ],
          ],
        ),
      ),
    );
  }

  /// Muestra un diálogo que solicita el texto de una nueva etiqueta para proponer.
  void _showProposeDialog(BuildContext context, AppLocalizations l10n) {
    final controller = TextEditingController();

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(l10n.proposeTag),
        content: TextField(
          controller: controller,
          autofocus: true,
          decoration: InputDecoration(
            hintText: l10n.proposeTagHint,
          ),
          textInputAction: TextInputAction.done,
          onSubmitted: (value) {
            if (value.trim().isNotEmpty) {
              Navigator.pop(ctx);
              onPropose(value.trim());
            }
          },
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: Text(l10n.cancel),
          ),
          FilledButton(
            onPressed: () {
              if (controller.text.trim().isNotEmpty) {
                Navigator.pop(ctx);
                onPropose(controller.text.trim());
              }
            },
            child: Text(l10n.save),
          ),
        ],
      ),
    );
  }
}

/// Chip de acción accesible que abre el diálogo para proponer una etiqueta.
class _AddTagChip extends StatelessWidget {
  final VoidCallback onTap;

  const _AddTagChip({required this.onTap});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final l10n = AppLocalizations.of(context)!;

    return Semantics(
      label: l10n.addTag,
      button: true,
      child: ActionChip(
        avatar: ExcludeSemantics(
          child: Icon(Icons.add_rounded, size: 16, color: colorScheme.primary),
        ),
        label: Text(
          l10n.add,
          style: TextStyle(fontSize: 12, color: colorScheme.primary),
        ),
        onPressed: onTap,
        backgroundColor: colorScheme.primaryContainer.withAlpha(30),
        side: BorderSide(color: colorScheme.primary.withAlpha(60)),
        padding: const EdgeInsets.symmetric(horizontal: 4),
        visualDensity: VisualDensity.compact,
        materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
      ),
    );
  }
}
