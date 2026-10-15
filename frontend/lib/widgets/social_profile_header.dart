import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'reusable_widgets.dart';

class SocialProfileHeader extends StatelessWidget {
  final String? bannerUrl;
  final String? avatarUrl;
  final String displayName;
  final String username;
  final String? tagline;
  final Map<String, String>? socialLinks;
  final List<ProfileStat> stats;
  final bool isOwnProfile;
  final bool isFollowing;
  final VoidCallback? onFollow;
  final VoidCallback? onMessage;
  final VoidCallback? onEdit;
  final ValueChanged<String>? onOpenLink;

  const SocialProfileHeader({
    super.key,
    this.bannerUrl,
    this.avatarUrl,
    required this.displayName,
    required this.username,
    this.tagline,
    this.socialLinks,
    this.stats = const [],
    this.isOwnProfile = false,
    this.isFollowing = false,
    this.onFollow,
    this.onMessage,
    this.onEdit,
    this.onOpenLink,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return Semantics(
      header: true,
      label: displayName,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Semantics(
            image: true,
            label: displayName,
            child: Container(
              height: 180,
              width: double.infinity,
              decoration: BoxDecoration(
                gradient: bannerUrl == null
                    ? LinearGradient(
                        colors: [
                          colorScheme.primaryContainer,
                          colorScheme.secondaryContainer,
                        ],
                      )
                    : null,
                image: bannerUrl != null
                    ? DecorationImage(
                        image: NetworkImage(bannerUrl!),
                        fit: BoxFit.cover,
                      )
                    : null,
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Transform.translate(
                  offset: const Offset(0, -40),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      ProfileAvatar(
                        imageUrl: avatarUrl,
                        fallbackText: displayName,
                        radius: 40,
                        semanticLabel: displayName,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        displayName,
                        style: Theme.of(context).textTheme.headlineSmall,
                      ),
                      Text(
                        '@$username',
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              color: colorScheme.onSurfaceVariant,
                            ),
                      ),
                      if (tagline != null && tagline!.isNotEmpty) ...[
                        const SizedBox(height: 4),
                        Text(
                          tagline!,
                          style: Theme.of(context).textTheme.bodyMedium,
                        ),
                      ],
                    ],
                  ),
                ),
                if (stats.isNotEmpty) ProfileStatsRow(stats: stats),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    if (isOwnProfile)
                      FilledButton.icon(
                        onPressed: onEdit,
                        icon: const Icon(Icons.edit_outlined),
                        label: const Text('Editar'),
                      )
                    else ...[
                      FilledButton(
                        onPressed: onFollow,
                        child: Text(isFollowing ? 'Siguiendo' : 'Seguir'),
                      ),
                      OutlinedButton(
                        onPressed: onMessage,
                        child: const Text('Mensaje'),
                      ),
                    ],
                  ],
                ),
                if (socialLinks != null && socialLinks!.isNotEmpty) ...[
                  const SizedBox(height: 8),
                  SocialLinksRow(
                    links: socialLinks!,
                    onOpen: onOpenLink,
                  ),
                ],
                const SizedBox(height: 8),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class ProfileStat {
  final String label;
  final String value;
  final VoidCallback? onTap;

  const ProfileStat({required this.label, required this.value, this.onTap});
}

class ProfileStatsRow extends StatelessWidget {
  final List<ProfileStat> stats;

  const ProfileStatsRow({super.key, required this.stats});

  @override
  Widget build(BuildContext context) {
    return Semantics(
      container: true,
      label: stats.map((s) => '${s.value} ${s.label}').join(', '),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: [
          for (final stat in stats)
            Expanded(
              child: InkWell(
                onTap: stat.onTap,
                borderRadius: BorderRadius.circular(8),
                child: Padding(
                  padding: const EdgeInsets.symmetric(vertical: 8),
                  child: Column(
                    children: [
                      Text(
                        stat.value,
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                      ),
                      Text(
                        stat.label,
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ],
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}

class SocialLinksRow extends StatelessWidget {
  final Map<String, String> links;
  final ValueChanged<String>? onOpen;

  const SocialLinksRow({super.key, required this.links, this.onOpen});

  static const _order = [
    'website',
    'instagram',
    'x',
    'youtube',
    'facebook',
    'linkedin',
  ];

  static IconData iconFor(String key) {
    switch (key.toLowerCase()) {
      case 'website':
        return Icons.language_outlined;
      case 'instagram':
        return Icons.camera_alt_outlined;
      case 'x':
        return Icons.alternate_email_outlined;
      case 'youtube':
        return Icons.play_circle_outline;
      case 'facebook':
        return Icons.thumb_up_outlined;
      case 'linkedin':
        return Icons.work_outline;
      default:
        return Icons.link_outlined;
    }
  }

  Future<void> _open(String url, ValueChanged<String>? cb) async {
    if (cb != null) {
      cb(url);
      return;
    }
    final uri = Uri.tryParse(url);
    if (uri == null) return;
    final fixed = uri.scheme.isEmpty ? Uri.parse('https://$url') : uri;
    await launchUrl(fixed, mode: LaunchMode.externalApplication);
  }

  @override
  Widget build(BuildContext context) {
    final keys = [
      for (final k in _order)
        if (links.containsKey(k)) k,
      for (final k in links.keys)
        if (!_order.contains(k)) k,
    ];
    return Semantics(
      container: true,
      label: 'Enlaces sociales',
      child: Wrap(
        spacing: 4,
        children: [
          for (final key in keys)
            IconButton(
              tooltip: key,
              icon: Icon(iconFor(key)),
              onPressed: links[key] == null || links[key]!.isEmpty
                  ? null
                  : () => _open(links[key]!, onOpen),
            ),
        ],
      ),
    );
  }
}
