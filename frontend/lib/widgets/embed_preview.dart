import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

class EmbedInfo {
  final String platform;
  final String label;
  final IconData icon;
  final String? videoId;
  final String? thumbnailUrl;
  final String url;

  const EmbedInfo({
    required this.platform,
    required this.label,
    required this.icon,
    required this.url,
    this.videoId,
    this.thumbnailUrl,
  });
}

String? _youtubeId(Uri uri) {
  if (uri.host.contains('youtu.be')) {
    return uri.pathSegments.isNotEmpty ? uri.pathSegments.first : null;
  }
  if (uri.host.contains('youtube.com')) {
    final v = uri.queryParameters['v'];
    if (v != null && v.isNotEmpty) return v;
    final seg = uri.pathSegments;
    if (seg.length >= 2 && (seg[0] == 'embed' || seg[0] == 'shorts' || seg[0] == 'live')) {
      return seg[1];
    }
  }
  return null;
}

String? _vimeoId(Uri uri) {
  final match = RegExp(r'vimeo\.com/(?:video/)?(\d+)').firstMatch(uri.toString());
  return match?.group(1);
}

String? _dailymotionId(Uri uri) {
  final match = RegExp(r'dailymotion\.com/video/([A-Za-z0-9]+)').firstMatch(uri.toString()) ??
      RegExp(r'dai\.ly/([A-Za-z0-9]+)').firstMatch(uri.toString());
  return match?.group(1);
}

EmbedInfo? detectEmbed(String rawUrl) {
  final trimmed = rawUrl.trim();
  if (trimmed.isEmpty) return null;
  var normalized = trimmed;
  if (!normalized.contains('://')) normalized = 'https://$normalized';
  final uri = Uri.tryParse(normalized);
  if (uri == null || !uri.hasScheme || uri.host.isEmpty) return null;
  if (!RegExp(r'^[A-Za-z0-9.-]+$').hasMatch(uri.host) || !uri.host.contains('.')) return null;
  final host = uri.host.toLowerCase();
  if (host.contains('youtube.com') || host.contains('youtu.be')) {
    final id = _youtubeId(uri);
    return EmbedInfo(
      platform: 'youtube',
      label: 'YouTube',
      icon: Icons.play_circle_fill,
      url: normalized,
      videoId: id,
      thumbnailUrl: id != null ? 'https://img.youtube.com/vi/$id/hqdefault.jpg' : null,
    );
  }
  if (host.contains('vimeo.com')) {
    return EmbedInfo(platform: 'vimeo', label: 'Vimeo', icon: Icons.play_circle_fill, url: normalized, videoId: _vimeoId(uri));
  }
  if (host.contains('dailymotion.com') || host == 'dai.ly') {
    return EmbedInfo(platform: 'dailymotion', label: 'Dailymotion', icon: Icons.play_circle_fill, url: normalized, videoId: _dailymotionId(uri));
  }
  if (host.contains('odysee.com')) {
    return EmbedInfo(platform: 'odysee', label: 'Odysee', icon: Icons.play_circle_fill, url: normalized);
  }
  if (host.contains('ivoox.com')) {
    return EmbedInfo(platform: 'ivoox', label: 'iVoox', icon: Icons.podcasts, url: normalized);
  }
  if (host.contains('podimo.com')) {
    return EmbedInfo(platform: 'podimo', label: 'Podimo', icon: Icons.podcasts, url: normalized);
  }
  return EmbedInfo(platform: 'generic', label: host, icon: Icons.link, url: normalized);
}

Future<void> openEmbedUrl(BuildContext context, String url) async {
  var uri = Uri.tryParse(url.trim());
  if (uri != null && !uri.hasScheme) uri = Uri.parse('https://${url.trim()}');
  if (uri != null && await canLaunchUrl(uri)) {
    await launchUrl(uri, mode: LaunchMode.externalApplication);
  }
}

class EmbedPreview extends StatelessWidget {
  final EmbedInfo embed;
  final bool compact;

  const EmbedPreview({super.key, required this.embed, this.compact = false});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    return Semantics(
      label: 'Contenido incrustado de ${embed.label}',
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () => openEmbedUrl(context, embed.url),
        child: Container(
          decoration: BoxDecoration(
            color: colorScheme.surfaceContainerLow,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: colorScheme.outlineVariant),
          ),
          clipBehavior: Clip.antiAlias,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              if (embed.thumbnailUrl != null)
                Stack(
                  alignment: Alignment.center,
                  children: [
                    Image.network(
                      embed.thumbnailUrl!,
                      height: compact ? 140 : 190,
                      width: double.infinity,
                      fit: BoxFit.cover,
                      errorBuilder: (_, __, ___) => SizedBox(
                        height: compact ? 140 : 190,
                        child: Icon(embed.icon, size: 48, color: colorScheme.primary),
                      ),
                    ),
                    Container(
                      decoration: const BoxDecoration(shape: BoxShape.circle, color: Colors.black54),
                      padding: const EdgeInsets.all(8),
                      child: const Icon(Icons.play_arrow, color: Colors.white, size: 32),
                    ),
                  ],
                )
              else
                Container(
                  height: compact ? 72 : 88,
                  color: colorScheme.primaryContainer.withAlpha(80),
                  child: Icon(embed.icon, size: 40, color: colorScheme.primary),
                ),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                child: Row(
                  children: [
                    Chip(
                      avatar: Icon(embed.icon, size: 16, color: colorScheme.primary),
                      label: Text(embed.label),
                      visualDensity: VisualDensity.compact,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        embed.url,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: theme.textTheme.bodySmall?.copyWith(color: colorScheme.onSurfaceVariant),
                      ),
                    ),
                    Icon(Icons.open_in_new, size: 18, color: colorScheme.primary),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
