import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../l10n/app_localizations.dart';
import '../models/message_model.dart';
import '../services/api_service.dart';

/// Una única burbuja de chat en la lista de conversación.
class ChatBubble {
  final Message message;
  final bool isMe;
  final String senderName;
  ChatBubble({required this.message, required this.isMe, String? senderName, AppLocalizations? l10n})
      : senderName = senderName ?? (l10n?.userDefaultName(message.senderId) ?? 'User #${message.senderId}');
}

/// Burbuja de mensaje con contenido enriquecido (imagen, ubicación, vCard, iCal).
class ChatBubbleWidget extends StatelessWidget {
  final ChatBubble bubble;
  final AppLocalizations l10n;

  const ChatBubbleWidget({super.key, required this.bubble, required this.l10n});

  static Future<void> openInMaps(double lat, double lng) async {
    final geoUri = Uri.parse('geo:0,0?q=$lat,$lng');
    if (await canLaunchUrl(geoUri)) {
      await launchUrl(geoUri);
      return;
    }
    final osmUri = Uri.parse(
      'https://www.openstreetmap.org/?mlat=$lat&mlon=$lng',
    );
    if (await canLaunchUrl(osmUri)) {
      await launchUrl(osmUri, mode: LaunchMode.externalApplication);
    }
  }

  String _bubblePreview(Message msg) {
    switch (msg.messageType) {
      case 'image': return '📷 ${msg.content.isNotEmpty ? msg.content : l10n.image}';
      case 'location': return '📍 ${msg.content}';
      case 'vcard': return '👤 ${msg.content}';
      case 'ical': return '📅 ${msg.content}';
      default: return msg.content;
    }
  }

  static const _emojiFallback = ['NotoColorEmoji'];

  @override
  Widget build(BuildContext context) {
    final msg = bubble.message;
    final isMe = bubble.isMe;
    final bgColor = isMe
        ? Theme.of(context).colorScheme.primaryContainer
        : Theme.of(context).colorScheme.surfaceContainerHighest;

    final senderLabel = isMe ? l10n.me : bubble.senderName;
    return Semantics(
      label: '${l10n.chat}: $senderLabel: ${_bubblePreview(msg)}',
      child: LayoutBuilder(
        builder: (context, constraints) {
          return Align(
            alignment: isMe ? Alignment.centerRight : Alignment.centerLeft,
            child: Container(
              margin: const EdgeInsets.symmetric(vertical: 3),
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              constraints: BoxConstraints(maxWidth: constraints.maxWidth * 0.75),
              decoration: BoxDecoration(
                color: bgColor,
                borderRadius: BorderRadius.only(
                  topLeft: const Radius.circular(16),
                  topRight: const Radius.circular(16),
                  bottomLeft: isMe ? const Radius.circular(16) : const Radius.circular(4),
                  bottomRight: isMe ? const Radius.circular(4) : const Radius.circular(16),
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (!isMe)
                    Semantics(
                      label: '${l10n.username}: ${bubble.senderName}',
                      child: Padding(
                        padding: const EdgeInsets.only(bottom: 4),
                        child: Text(
                          bubble.senderName,
                          style: TextStyle(
                            fontWeight: FontWeight.w600,
                            fontSize: 12,
                            color: Theme.of(context).colorScheme.primary,
                          ),
                        ),
                      ),
                    ),
                  _buildMessageContent(context, msg),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildMessageContent(BuildContext context, Message msg) {
    return DefaultTextStyle(
      style: const TextStyle(fontSize: 14, fontFamilyFallback: _emojiFallback),
      child: switch (msg.messageType) {
        'image' => _buildImageContent(context, msg),
        'location' => _buildLocationContent(context, msg),
        'vcard' => _buildVcardContent(context, msg),
        'ical' => _buildIcalContent(context, msg),
        _ => Text(msg.content),
      },
    );
  }

  Widget _buildImageContent(BuildContext context, Message msg) {
    final rootUrl = ApiService().rootUrl;
    final fullUrl = msg.mediaUrl != null ? '$rootUrl${msg.mediaUrl}' : null;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (fullUrl != null)
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: Image.network(fullUrl, width: 200, height: 150, fit: BoxFit.cover,
              cacheWidth: (200 * MediaQuery.devicePixelRatioOf(context)).round(),
              cacheHeight: (150 * MediaQuery.devicePixelRatioOf(context)).round(),
              errorBuilder: (_, __, ___) => Container(
                height: 100, color: Theme.of(context).colorScheme.surfaceContainerHighest,
                child: Center(child: Icon(Icons.broken_image, size: 40, color: Theme.of(context).colorScheme.onSurfaceVariant)),
              ),
            ),
          ),
        if (msg.content.isNotEmpty) ...[const SizedBox(height: 4), Text(msg.content, style: const TextStyle(fontSize: 14))],
      ],
    );
  }

  Widget _buildLocationContent(BuildContext context, Message msg) {
    final lat = msg.latitude;
    final lng = msg.longitude;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(children: [
          Icon(Icons.location_on, size: 18, color: Theme.of(context).colorScheme.primary),
          const SizedBox(width: 4),
          Text(msg.content, style: const TextStyle(fontSize: 14)),
        ]),
        if (lat != null && lng != null) ...[
          const SizedBox(height: 4),
          Text('${lat.toStringAsFixed(6)}, ${lng.toStringAsFixed(6)}', style: TextStyle(fontSize: 11, color: Theme.of(context).colorScheme.onSurfaceVariant)),
          const SizedBox(height: 4),
          Semantics(
            label: l10n.openInMaps,
            child: Tooltip(
              message: l10n.openInMaps,
              child: TextButton.icon(
                icon: const Icon(Icons.map, size: 16),
                label: Text(l10n.viewOnMap, style: const TextStyle(fontSize: 12)),
                onPressed: () => openInMaps(lat, lng),
              ),
            ),
          ),
        ],
      ],
    );
  }

  Widget _buildVcardContent(BuildContext context, Message msg) {
    Map<String, dynamic> data = {};
    if (msg.vcardData != null) {
      try { data = json.decode(msg.vcardData!) as Map<String, dynamic>; } catch (e) { debugPrint('Error: $e'); }
    }
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(border: Border.all(color: Theme.of(context).colorScheme.outlineVariant), borderRadius: BorderRadius.circular(8)),
      child: Row(children: [
        Icon(Icons.contact_page, size: 32, color: Theme.of(context).colorScheme.primary),
        const SizedBox(width: 8),
        Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(data['name'] ?? msg.content, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
          if (data['phone'] != null) Text('📞 ${data['phone']}', style: const TextStyle(fontSize: 12)),
          if (data['email'] != null) Text('✉️ ${data['email']}', style: const TextStyle(fontSize: 12)),
        ])),
      ]),
    );
  }

  Widget _buildIcalContent(BuildContext context, Message msg) {
    Map<String, dynamic> data = {};
    if (msg.icalData != null) {
      try { data = json.decode(msg.icalData!) as Map<String, dynamic>; } catch (e) { debugPrint('Error: $e'); }
    }
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(border: Border.all(color: Theme.of(context).colorScheme.outlineVariant), borderRadius: BorderRadius.circular(8)),
      child: Row(children: [
        Icon(Icons.calendar_today, size: 32, color: Theme.of(context).colorScheme.primary),
        const SizedBox(width: 8),
        Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(data['title'] ?? msg.content, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
          if (data['start'] != null) Text('🕐 ${data['start']}', style: const TextStyle(fontSize: 12)),
          if (data['end'] != null) Text('🔚 ${data['end']}', style: const TextStyle(fontSize: 12)),
        ])),
      ]),
    );
  }
}
