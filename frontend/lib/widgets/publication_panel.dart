import 'package:flutter/material.dart';
import '../models/post_model.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import 'confirm_dialog.dart';
import 'embed_preview.dart';
import 'loading_skeleton.dart';
import 'error_state_widget.dart';
import 'markdown_text.dart';
import 'reusable_widgets.dart';

class PublicationPanel extends StatefulWidget {
  final int? scopeUserId;
  final int? scopeFestivalId;
  final bool canModerate;
  final int? currentUserId;

  const PublicationPanel({
    super.key,
    this.scopeUserId,
    this.scopeFestivalId,
    this.canModerate = false,
    this.currentUserId,
  });

  @override
  State<PublicationPanel> createState() => _PublicationPanelState();
}

class _PublicationPanelState extends State<PublicationPanel> {
  final ApiService _api = ApiService();
  List<Post> _posts = [];
  bool _loading = true;
  bool _hasError = false;
  bool _loggedIn = false;
  bool _publishing = false;
  bool _showUrlField = false;
  bool _allowReplies = true;
  final _contentCtl = TextEditingController();
  final _urlCtl = TextEditingController();
  final Set<int> _expanded = {};
  final Map<int, List<Post>> _replies = {};
  final Map<int, bool> _repliesLoading = {};
  final Map<int, TextEditingController> _replyCtls = {};

  @override
  void initState() {
    super.initState();
    _checkAuth();
    _load();
  }

  @override
  void dispose() {
    _contentCtl.dispose();
    _urlCtl.dispose();
    for (final c in _replyCtls.values) {
      c.dispose();
    }
    super.dispose();
  }

  Future<void> _checkAuth() async {
    final loggedIn = await AuthService().isLoggedIn();
    if (mounted) setState(() => _loggedIn = loggedIn);
  }

  Future<void> _load() async {
    if (!mounted) return;
    setState(() {
      _loading = true;
      _hasError = false;
    });
    try {
      final PaginatedResult<Post> result;
      if (widget.scopeFestivalId != null) {
        result = await _api.getFestivalPosts(widget.scopeFestivalId!, size: 50);
      } else {
        result = await _api.getUserPosts(widget.scopeUserId!, size: 50);
      }
      if (!mounted) return;
      setState(() {
        _posts = result.items;
        _loading = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _hasError = true;
      });
    }
  }

  String? _embedTypeFor(String url) {
    final info = detectEmbed(url);
    if (info == null) return null;
    return info.platform;
  }

  Future<void> _publish() async {
    final content = _contentCtl.text.trim();
    final url = _urlCtl.text.trim();
    if (content.isEmpty || _publishing) return;
    setState(() => _publishing = true);
    try {
      final draft = Post(
        authorId: widget.currentUserId ?? 0,
        content: content,
        embedUrl: url.isNotEmpty ? (url.contains('://') ? url : 'https://$url') : null,
        embedType: url.isNotEmpty ? _embedTypeFor(url) : null,
        allowReplies: _allowReplies,
      );
      final Post created;
      if (widget.scopeFestivalId != null) {
        created = await _api.createFestivalPost(widget.scopeFestivalId!, draft);
      } else {
        created = await _api.createUserPost(widget.scopeUserId!, draft);
      }
      if (!mounted) return;
      setState(() {
        _posts = [created, ..._posts];
        _contentCtl.clear();
        _urlCtl.clear();
        _showUrlField = false;
        _allowReplies = true;
      });
    } catch (e) {
      if (mounted) showAppSnack(context, 'No se pudo publicar');
    } finally {
      if (mounted) setState(() => _publishing = false);
    }
  }

  Future<void> _deletePost(Post post) async {
    if (post.id == null) return;
    final confirmed = await showConfirmDialog(context, title: 'Eliminar', message: '¿Eliminar esta publicación?');
    if (confirmed != true) return;
    try {
      await _api.deletePost(post.id!);
      if (mounted) setState(() => _posts = _posts.where((p) => p.id != post.id).toList());
    } catch (_) {
      if (mounted) showAppSnack(context, 'No se pudo eliminar');
    }
  }

  Future<void> _editPost(Post post) async {
    if (post.id == null) return;
    final ctl = TextEditingController(text: post.content);
    final saved = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Editar publicación'),
        content: TextField(controller: ctl, maxLines: 5, decoration: const InputDecoration(hintText: 'Markdown: **negrita**, [enlace](url)')),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancelar')),
          FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Guardar')),
        ],
      ),
    );
    if (saved == true && ctl.text.trim().isNotEmpty) {
      try {
        final updated = await _api.updatePost(post.id!, {'content': ctl.text.trim()});
        if (mounted) {
          setState(() => _posts = _posts.map((p) => p.id == post.id ? updated : p).toList());
        }
      } catch (_) {
        if (mounted) showAppSnack(context, 'No se pudo guardar');
      }
    }
  }

  Future<void> _moderate(Post post, Map<String, dynamic> fields) async {
    if (post.id == null) return;
    try {
      final updated = await _api.moderatePost(post.id!, fields);
      if (!mounted) return;
      if (updated.isHidden && !_canSeeHidden()) {
        setState(() => _posts = _posts.where((p) => p.id != post.id).toList());
      } else {
        setState(() => _posts = _posts.map((p) => p.id == post.id ? updated : p).toList());
      }
    } catch (_) {
      if (mounted) showAppSnack(context, 'Acción no permitida');
    }
  }

  bool _canSeeHidden() => widget.canModerate;

  bool _isOwn(Post post) => widget.currentUserId != null && post.authorId == widget.currentUserId;

  Future<void> _toggleExpanded(Post post) async {
    if (post.id == null) return;
    if (_expanded.contains(post.id)) {
      setState(() => _expanded.remove(post.id));
      return;
    }
    setState(() => _expanded.add(post.id!));
    if (_replies.containsKey(post.id)) return;
    setState(() => _repliesLoading[post.id!] = true);
    try {
      final result = await _api.getReplies(post.id!, size: 100);
      if (mounted) {
        setState(() {
          _replies[post.id!] = result.items;
          _repliesLoading[post.id!] = false;
        });
      }
    } catch (_) {
      if (mounted) setState(() => _repliesLoading[post.id!] = false);
    }
  }

  Future<void> _sendReply(Post post) async {
    if (post.id == null) return;
    final ctl = _replyCtls.putIfAbsent(post.id!, () => TextEditingController());
    if (ctl.text.trim().isEmpty) return;
    try {
      final created = await _api.createReply(
        post.id!,
        Post(authorId: widget.currentUserId ?? 0, content: ctl.text.trim()),
      );
      if (!mounted) return;
      setState(() {
        _replies[post.id!] = [...(_replies[post.id!] ?? []), created];
        _posts = _posts.map((p) => p.id == post.id ? p.copyWith(replyCount: p.replyCount + 1) : p).toList();
        ctl.clear();
      });
    } catch (_) {
      if (mounted) showAppSnack(context, 'No se pudo responder');
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const SizedBox(height: 320, child: ListSkeleton());
    if (_hasError) return ErrorStateWidget(onRetry: _load);
    if (_posts.isEmpty && !_loggedIn) return const SizedBox.shrink();
    return RefreshIndicator(
      onRefresh: _load,
      child: ListView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: _posts.length + (_loggedIn ? 1 : 0),
              itemBuilder: (ctx, i) {
                if (_loggedIn && i == 0) return _buildComposer(Theme.of(context));
                final post = _posts[_loggedIn ? i - 1 : i];
                return _buildPostCard(post, Theme.of(context), 0);
              },
            ),
    );
  }

  Widget _buildComposer(ThemeData theme) {
    final colorScheme = theme.colorScheme;
    final urlText = _urlCtl.text.trim();
    final embed = urlText.isNotEmpty ? detectEmbed(urlText) : null;
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            TextField(
              controller: _contentCtl,
              minLines: 2,
              maxLines: 6,
              textInputAction: TextInputAction.newline,
              decoration: const InputDecoration(
                hintText: 'Escribe una publicación… (Markdown: **negrita**, *cursiva*, [enlace](url), # título)',
                border: OutlineInputBorder(),
              ),
            ),
            if (_showUrlField) ...[
              const SizedBox(height: 8),
              TextField(
                controller: _urlCtl,
                keyboardType: TextInputType.url,
                decoration: const InputDecoration(
                  hintText: 'Pega un enlace de YouTube, Vimeo, Odysee, iVoox…',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.link),
                ),
                onChanged: (_) => setState(() {}),
              ),
              if (embed != null) ...[
                const SizedBox(height: 8),
                EmbedPreview(embed: embed, compact: true),
              ],
            ],
            const SizedBox(height: 8),
            Row(
              children: [
                Tooltip(
                  message: 'Añadir enlace multimedia',
                  child: IconButton(
                    icon: Icon(Icons.link, color: _showUrlField ? colorScheme.primary : null),
                    onPressed: () => setState(() => _showUrlField = !_showUrlField),
                  ),
                ),
                const Tooltip(
                  message: 'Imágenes próximamente',
                  child: IconButton(icon: Icon(Icons.image_outlined), onPressed: null),
                ),
                Expanded(
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.reply, size: 18),
                      const SizedBox(width: 4),
                      const Flexible(child: Text('Respuestas', overflow: TextOverflow.ellipsis)),
                      Switch(
                        value: _allowReplies,
                        onChanged: (v) => setState(() => _allowReplies = v),
                        materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                      ),
                    ],
                  ),
                ),
                FilledButton.icon(
                  onPressed: _publishing ? null : _publish,
                  icon: _publishing
                      ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                      : const Icon(Icons.send, size: 18),
                  label: const Text('Publicar'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  (String title, String body) _splitTitle(String content) {
    final lines = content.split('\n');
    final idx = lines.indexWhere((l) => l.trim().isNotEmpty);
    if (idx == -1) return ('Sin título', '');
    var first = lines[idx].trim();
    final header = RegExp(r'^#{1,3}\s+').firstMatch(first);
    if (header != null) first = first.substring(header.end).trim();
    var title = first.replaceAll(RegExp(r'\*\*|__|`'), '');
    final link = RegExp(r'\[(.+?)\]\(.+?\)').firstMatch(title);
    if (link != null) title = title.replaceAll(link.group(0)!, link.group(1)!);
    if (title.length > 90) title = '${title.substring(0, 90)}…';
    final rest = [...lines]..removeAt(idx);
    return (title.isEmpty ? 'Sin título' : title, rest.join('\n').trimLeft());
  }

  int _readingMinutes(String content) {
    final words = content.trim().split(RegExp(r'\s+')).where((w) => w.isNotEmpty).length;
    return (words / 200).ceil().clamp(1, 99);
  }

  Widget _moderationMenu(Post post, bool canMod, bool own) {
    return PopupMenuButton<String>(
      tooltip: 'Opciones',
      onSelected: (v) {
        if (v == 'edit') {
          _editPost(post);
        } else if (v == 'delete') {
          _deletePost(post);
        } else if (v == 'pin') {
          _moderate(post, {'is_pinned': !post.isPinned});
        } else if (v == 'hide') {
          _moderate(post, {'is_hidden': !post.isHidden});
        } else if (v == 'lock') {
          _moderate(post, {'allow_replies': !post.allowReplies});
        }
      },
      itemBuilder: (_) => [
        if (own || canMod) const PopupMenuItem(value: 'edit', child: Text('Editar')),
        if (canMod) PopupMenuItem(value: 'pin', child: Text(post.isPinned ? 'Desfijar' : 'Fijar')),
        if (canMod) PopupMenuItem(value: 'hide', child: Text(post.isHidden ? 'Mostrar' : 'Ocultar')),
        if (canMod) PopupMenuItem(value: 'lock', child: Text(post.allowReplies ? 'Bloquear respuestas' : 'Permitir respuestas')),
        if (own || canMod) const PopupMenuItem(value: 'delete', child: Text('Eliminar')),
      ],
    );
  }

  Widget _buildPostCard(Post post, ThemeData theme, int depth) {
    if (depth > 0) return _buildReplyTile(post, theme);
    final colorScheme = theme.colorScheme;
    final canMod = widget.canModerate;
    final own = _isOwn(post);
    final embed = (post.embedUrl != null && post.embedUrl!.isNotEmpty) ? detectEmbed(post.embedUrl!) : null;
    final replies = _replies[post.id] ?? [];
    final expanded = post.id != null && _expanded.contains(post.id);
    final titleBody = _splitTitle(post.content);
    final date = post.createdAt != null ? post.createdAt!.toLocal().toString().substring(0, 16) : '';
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      color: post.isHidden ? colorScheme.surfaceContainerHighest : null,
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: Semantics(
                    header: true,
                    child: Text(titleBody.$1, style: theme.textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w700)),
                  ),
                ),
                if (canMod || own) _moderationMenu(post, canMod, own),
              ],
            ),
            const SizedBox(height: 8),
            Wrap(
              crossAxisAlignment: WrapCrossAlignment.center,
              spacing: 8,
              runSpacing: 4,
              children: [
                CircleAvatar(
                  radius: 14,
                  backgroundColor: colorScheme.primaryContainer,
                  child: Text(
                    'U${post.authorId}',
                    style: TextStyle(fontSize: 8, color: colorScheme.onPrimaryContainer, fontWeight: FontWeight.w700),
                  ),
                ),
                Text('Usuario ${post.authorId}', style: theme.textTheme.bodySmall?.copyWith(fontWeight: FontWeight.w600)),
                if (date.isNotEmpty) Text(date, style: theme.textTheme.bodySmall?.copyWith(color: colorScheme.onSurfaceVariant)),
                Text('${_readingMinutes(post.content)} min de lectura', style: theme.textTheme.bodySmall?.copyWith(color: colorScheme.onSurfaceVariant)),
                if (post.isPinned) const Chip(label: Text('Destacada'), avatar: Icon(Icons.push_pin, size: 14), visualDensity: VisualDensity.compact),
                if (post.isHidden) const Chip(label: Text('Oculta'), visualDensity: VisualDensity.compact),
                if (!post.allowReplies) Icon(Icons.comments_disabled_outlined, size: 16, color: colorScheme.onSurfaceVariant),
              ],
            ),
            const Divider(height: 24),
            if (titleBody.$2.isNotEmpty) MarkdownText(data: titleBody.$2),
            if (embed != null) ...[
              const SizedBox(height: 12),
              EmbedPreview(embed: embed),
            ],
            const SizedBox(height: 8),
            Row(
              children: [
                if (post.allowReplies || post.replyCount > 0 || canMod)
                  TextButton.icon(
                    onPressed: () => _toggleExpanded(post),
                    icon: Icon(expanded ? Icons.expand_less : Icons.expand_more, size: 18),
                    label: Text(post.replyCount > 0 ? 'Respuestas (${post.replyCount})' : 'Responder'),
                  ),
                if (!post.allowReplies)
                  Text('Respuestas desactivadas', style: theme.textTheme.bodySmall?.copyWith(color: colorScheme.onSurfaceVariant)),
              ],
            ),
            if (expanded) _buildReplies(post, theme, replies),
          ],
        ),
      ),
    );
  }

  Widget _buildReplyTile(Post post, ThemeData theme) {
    final colorScheme = theme.colorScheme;
    final canMod = widget.canModerate;
    final own = _isOwn(post);
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      color: colorScheme.surfaceContainerLow,
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    'Usuario ${post.authorId}',
                    style: theme.textTheme.bodySmall?.copyWith(fontWeight: FontWeight.w700),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                if (canMod || own) _moderationMenu(post, canMod, own),
              ],
            ),
            const SizedBox(height: 4),
            MarkdownText(data: post.content, style: theme.textTheme.bodyMedium),
          ],
        ),
      ),
    );
  }

  Widget _buildReplies(Post post, ThemeData theme, List<Post> replies) {
    final loading = post.id != null && (_repliesLoading[post.id] ?? false);
    final canReply = post.allowReplies || widget.canModerate;
    return Padding(
      padding: const EdgeInsets.only(left: 12, top: 4),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Divider(height: 8),
          if (loading)
            const Padding(padding: EdgeInsets.all(8), child: Center(child: CircularProgressIndicator(strokeWidth: 2)))
          else
            ...replies.map((r) => _buildPostCard(r, theme, 1)),
          if (_loggedIn && canReply)
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _replyCtls.putIfAbsent(post.id!, () => TextEditingController()),
                    decoration: const InputDecoration(hintText: 'Escribe una respuesta…', border: OutlineInputBorder(), isDense: true),
                    minLines: 1,
                    maxLines: 4,
                    textInputAction: TextInputAction.send,
                    onSubmitted: (_) => _sendReply(post),
                  ),
                ),
                const SizedBox(width: 8),
                IconButton.filled(onPressed: () => _sendReply(post), icon: const Icon(Icons.send, size: 18), tooltip: 'Responder'),
              ],
            ),
        ],
      ),
    );
  }
}
