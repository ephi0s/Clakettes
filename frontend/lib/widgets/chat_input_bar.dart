import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';

/// Barra de entrada del chat: emoji, adjuntos, campo de texto y envío.
class ChatInputBar extends StatelessWidget {
  final TextEditingController controller;
  final bool isSending;
  final AppLocalizations l10n;
  final VoidCallback onSend;
  final VoidCallback onEmoji;
  final VoidCallback onAttach;

  const ChatInputBar({
    super.key,
    required this.controller,
    required this.isSending,
    required this.l10n,
    required this.onSend,
    required this.onEmoji,
    required this.onAttach,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return Semantics(
      label: l10n.writeMessage,
      child: Container(
        decoration: BoxDecoration(
          color: colorScheme.surface,
          boxShadow: [
            BoxShadow(
              color: colorScheme.shadow.withAlpha(20),
              blurRadius: 4,
              offset: const Offset(0, -1),
            ),
          ],
        ),
        child: SafeArea(
          top: false,
          child: Padding(
            padding: EdgeInsets.only(
              left: 4,
              right: 4,
              bottom: MediaQuery.of(context).padding.bottom > 0 ? 0 : 4,
              top: 4,
            ),
            child: Row(
              children: [
                Semantics(
                  label: l10n.emoji,
                  child: Tooltip(
                    message: l10n.emoji,
                    child: IconButton(
                      icon: Icon(Icons.emoji_emotions, color: colorScheme.onSurfaceVariant),
                      onPressed: onEmoji,
                    ),
                  ),
                ),
                Semantics(
                  label: l10n.attachFile,
                  child: Tooltip(
                    message: l10n.attachFile,
                    child: IconButton(
                      icon: Icon(Icons.attach_file, color: colorScheme.onSurfaceVariant),
                      onPressed: onAttach,
                    ),
                  ),
                ),
                const SizedBox(width: 4),
                Expanded(
                  child: Semantics(
                    label: l10n.writeMessage,
                    child: TextField(
                      controller: controller,
                      decoration: InputDecoration(
                        hintText: l10n.writeMessage,
                        border: InputBorder.none,
                        filled: true,
                        fillColor: colorScheme.surfaceContainerHighest.withAlpha(120),
                        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                      ),
                      textInputAction: TextInputAction.send,
                      onSubmitted: (_) => onSend(),
                    ),
                  ),
                ),
                const SizedBox(width: 4),
                Semantics(
                  label: l10n.sendMessage,
                  child: Tooltip(
                    message: l10n.sendMessage,
                    child: IconButton(
                      icon: isSending
                          ? SizedBox(
                              height: 20,
                              width: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                color: colorScheme.primary,
                              ),
                            )
                          : Icon(Icons.send, color: colorScheme.primary),
                      onPressed: isSending ? null : onSend,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
