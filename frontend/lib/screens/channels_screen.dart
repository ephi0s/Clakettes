import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../models/channel_model.dart';
import '../models/user_model.dart';
import '../services/channel_service.dart';
import 'chat_screen.dart';
import 'create_channel_screen.dart';

/// Pantalla que lista los canales de chat del usuario (comunidades y salas privadas).
class ChannelsScreen extends StatefulWidget {
  final User? currentUser;

  const ChannelsScreen({super.key, this.currentUser});

  @override
  State<ChannelsScreen> createState() => _ChannelsScreenState();
}

/// Mantiene los canales del usuario cargados de la API al iniciar.
class _ChannelsScreenState extends State<ChannelsScreen> {
  final ChannelApiService _channelApi = ChannelApiService();
  List<Channel> _channels = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadChannels();
  }

  /// Carga los canales del usuario actual, conservando la lista previa en caso de error.
  Future<void> _loadChannels() async {
    try {
      final channels = await _channelApi.getMyChannels();
      if (mounted) {
        setState(() {
          _channels = channels;
          _isLoading = false;
        });
      }
    } catch (e) {
      debugPrint('Error: $e');
      if (mounted) setState(() => _isLoading = false);
    }
  }

  /// Abre la pantalla de creación de canal y antepone el canal devuelto.
  Future<void> _createChannel() async {
    final result = await Navigator.push<Channel>(
      context,
      MaterialPageRoute(builder: (_) => CreateChannelScreen(currentUser: widget.currentUser)),
    );
    if (result != null) {
      setState(() => _channels.insert(0, result));
    }
  }

  void _openChannel(Channel channel) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => ChatScreen(
          currentUser: widget.currentUser,
          channel: channel,
        ),
      ),
    );
  }

  IconData _channelIcon(Channel ch) {
    return ch.channelType == 'private' ? Icons.lock : Icons.forum;
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return Scaffold(
      appBar: AppBar(title: Semantics(header: true, child: Text(l10n.chat))),
      floatingActionButton: Semantics(
        label: l10n.createChannel,
        child: Tooltip(
          message: l10n.createChannel,
          child: FloatingActionButton(
            onPressed: _createChannel,
            child: const Icon(Icons.add),
          ),
        ),
      ),
      body: _isLoading
          ? Center(child: Text(l10n.loading))
              : _channels.isEmpty
                  ? Center(
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          ExcludeSemantics(child: Icon(Icons.chat_bubble_outline, size: 64, color: Colors.grey.shade400)),
                          const SizedBox(height: 16),
                          Semantics(
                            label: l10n.noMessages,
                            child: Text(l10n.noMessages, style: TextStyle(color: Colors.grey.shade600)),
                          ),
                          const SizedBox(height: 16),
                          Semantics(
                            label: l10n.createFirstChannel,
                            button: true,
                            child: FilledButton.icon(
                              icon: const Icon(Icons.add),
                              label: Text(l10n.createFirstChannel),
                              onPressed: _createChannel,
                            ),
                          ),
                        ],
                      ),
                    )
              : RefreshIndicator(
                  onRefresh: _loadChannels,
                  child: ListView.builder(
                    padding: const EdgeInsets.only(top: 8, bottom: 80),
                    itemCount: _channels.length,
                    itemBuilder: (ctx, i) {
                      final ch = _channels[i];
                      return Semantics(
                        label: l10n.channelLabel.replaceAll('{name}', ch.name),
                        child: Card(
                          child: ListTile(
                            leading: ExcludeSemantics(
                              child: CircleAvatar(
                                backgroundColor: ch.channelType == 'private'
                                    ? Colors.amber.shade100
                                    : Colors.green.shade100,
                                child: Icon(_channelIcon(ch), color: ch.channelType == 'private' ? Colors.amber.shade700 : Colors.green.shade700),
                              ),
                            ),
                            title: Text(ch.name, style: const TextStyle(fontWeight: FontWeight.w600)),
                            subtitle: Text(ch.description ?? (ch.channelType == 'private' ? l10n.channelPrivate : l10n.channelCommunity),
                                maxLines: 1, overflow: TextOverflow.ellipsis),
                            trailing: ch.channelType == 'private'
                                ? Chip(label: Text('≤${ch.maxMembers ?? 20}', style: const TextStyle(fontSize: 11)))
                                : null,
                            onTap: () => _openChannel(ch),
                          ),
                        ),
                      );
                    },
                  ),
                ),
    );
  }
}
