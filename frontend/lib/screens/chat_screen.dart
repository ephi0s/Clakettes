import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:geolocator/geolocator.dart';
import '../l10n/app_localizations.dart';
import '../services/offline_cache_service.dart';
import '../services/sync_queue_service.dart';
import '../models/message_model.dart';
import '../models/user_model.dart';
import '../models/channel_model.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import '../services/channel_service.dart';
import '../services/chat_backend/chat_service.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/crypto_utils.dart';
import '../widgets/chat_bubble.dart';
import '../widgets/chat_input_bar.dart';
import '../widgets/emoji_picker.dart';

/// Pantalla de chat con contexto de canal, compresión, E2EE y contenido enriquecido.
class ChatScreen extends StatefulWidget {
  final User? currentUser;
  final Channel? channel;

  const ChatScreen({super.key, this.currentUser, this.channel});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

/// Mantiene las burbujas de chat, las claves E2EE y el estado de conexión; se
/// suscribe al stream del servicio de chat al iniciar y carga el historial de
/// mensajes en el primer build.
class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final List<ChatBubble> _bubbles = [];
  final ChatService _chatService = ChatService(api: ApiService(), auth: AuthService());
  final ImagePicker _imagePicker = ImagePicker();

  // E2EE state
  final Map<int, Uint8List> _sharedKeys = {};
  Uint8List? _senderKey;
  bool _e2eeEnabled = false;

  bool _isLoading = true;
  bool _isSending = false;
  bool _isOfflineData = false;
  bool _isReconnecting = false;
  bool _initialized = false;
  bool _offlineNotified = false;
  late AppLocalizations l10n;
  StreamSubscription<Message>? _streamSub;
  StreamSubscription<bool>? _reconnectingSub;

  @override
  void initState() {
    super.initState();
    _initChat();
  }

  // ---------------------------------------------------------------------------
  // Initialisation
  // ---------------------------------------------------------------------------

  /// Inicializa el servicio de chat y se suscribe a los streams de mensajes entrantes.
  Future<void> _initChat() async {
    await _chatService.init();
    _streamSub = _chatService.onMessage.listen(_onIncomingMessage);
    _reconnectingSub = _chatService.onReconnecting.listen((reconnecting) {
      if (mounted) setState(() => _isReconnecting = reconnecting);
    });
    await _setupE2ee();
  }

  /// Restaura la clave de remitente del canal o deriva una clave E2EE por destinatario.
  Future<void> _setupE2ee() async {
    final auth = AuthService();
    final myPrivKey = await auth.getPrivateKey();
    if (myPrivKey == null) return;

    if (_isChannelChat) {
      final channelId = widget.channel!.id;
      if (channelId == null) return;
      final prefs = await SharedPreferences.getInstance();
      final stored = prefs.getString('sender_key_$channelId');
      if (stored != null) {
        _senderKey = base64Url.decode(stored);
        if (mounted) setState(() => _e2eeEnabled = true);
      }
      return;
    }

    final recipientId = widget.currentUser?.id;
    if (recipientId == null) return;
    final theirPubKey = await ChannelApiService().getPublicKey(recipientId);
    if (theirPubKey == null) return;
    final sharedKey = ChatCrypto.deriveSharedKey(myPrivKey, theirPubKey);
    if (mounted) {
      setState(() {
        _sharedKeys[recipientId] = sharedKey;
        _e2eeEnabled = true;
      });
    }
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    l10n = AppLocalizations.of(context)!;
    if (!_initialized) {
      _initialized = true;
      _loadMessages();
    }
  }

  @override
  void dispose() {
    _streamSub?.cancel();
    _reconnectingSub?.cancel();
    _chatService.dispose();
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  bool get _isChannelChat => widget.channel != null;

  // ---------------------------------------------------------------------------
  // Message processing pipeline (compression → E2EE → send)
  // ---------------------------------------------------------------------------

  Uint8List? _e2eeKey(int targetId) {
    if (_isChannelChat) return _senderKey;
    return _sharedKeys[targetId];
  }

  /// Comprime y opcionalmente cifra el contenido plano para un usuario destino.
  ///
  /// El cifrado AES-GCM corre en un isolate ([ChatCrypto.encryptAsync]) para
  /// no bloquear el UI thread con mensajes grandes.
  Future<String> _prepareContent(String plainContent, int targetId) async {
    final compressed = ChatCrypto.compress(Uint8List.fromList(utf8.encode(plainContent)));
    final key = _e2eeKey(targetId);
    if (key != null && _e2eeEnabled) {
      return ChatCrypto.encryptAsync(base64Url.encode(compressed), key);
    }
    return base64Url.encode(compressed);
  }

  /// Descifra y descomprime el payload empaquetado de un mensaje recibido.
  ///
  /// El descifrado AES-GCM corre en un isolate ([ChatCrypto.decryptAsync]).
  Future<String> _unpackContent(String packedContent, int senderId) async {
    try {
      Uint8List compressed;
      final key = _e2eeKey(senderId);
      if (key != null && _e2eeEnabled) {
        final decrypted = await ChatCrypto.decryptAsync(packedContent, key);
        compressed = base64Url.decode(decrypted);
      } else {
        compressed = base64Url.decode(packedContent);
      }
      return utf8.decode(ChatCrypto.decompress(compressed));
    } catch (e) {
      debugPrint('Error: $e');
      return packedContent;
    }
  }

  // ---------------------------------------------------------------------------
  // Incoming messages
  // ---------------------------------------------------------------------------

  /// Gestiona un mensaje entrante en directo, desempaquetando el contenido y
  /// añadiendo una burbuja.
  void _onIncomingMessage(Message msg) async {
    if (!mounted) return;

    if (msg.messageType == 'e2ee_key' && ChatCrypto.isSenderKeyMessage(msg.content) && _isChannelChat) {
      await _handleSenderKeyMessage(msg);
      return;
    }

    final unpacked = await _unpackContent(msg.content, msg.senderId);
    final displayMsg = Message(
      id: msg.id,
      content: unpacked,
      senderId: msg.senderId,
      receiverId: msg.receiverId,
      channelId: msg.channelId,
      isRead: msg.isRead,
      createdAt: msg.createdAt,
      messageType: msg.messageType,
      mediaUrl: msg.mediaUrl,
      latitude: msg.latitude,
      longitude: msg.longitude,
      vcardData: msg.vcardData,
      icalData: msg.icalData,
    );

    setState(() {
      final exists = _bubbles.any((b) => b.message.id != null && b.message.id == displayMsg.id);
      if (!exists) {
        _bubbles.add(ChatBubble(message: displayMsg, isMe: displayMsg.senderId == widget.currentUser?.id, l10n: l10n));
      }
    });
    _scrollToBottom();
  }

  /// Descifra la clave de remitente del canal entrante y la persiste para uso posterior.
  Future<void> _handleSenderKeyMessage(Message msg) async {
    final channelId = msg.channelId;
    if (channelId == null) return;
    final auth = AuthService();
    final myPrivKey = await auth.getPrivateKey();
    final myPubKey = await auth.getPublicKey();
    if (myPrivKey == null || myPubKey == null) return;

    final encrypted = ChatCrypto.unwrapSenderKey(msg.content);
    try {
      final senderPubKey = await ChannelApiService().getPublicKey(msg.senderId);
      if (senderPubKey == null) return;
      final senderKey = await ChatCrypto.decryptSenderKeyAsync(encrypted, myPrivKey, senderPubKey);
      _senderKey = senderKey;
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('sender_key_$channelId', base64Url.encode(senderKey));
      if (mounted) setState(() => _e2eeEnabled = true);
    } catch (e) { debugPrint('Error: $e'); }
  }

  /// Carga los mensajes recientes, recurriendo a la caché offline cuando no
  /// hay conexión.
  Future<void> _loadMessages() async {
    try {
      final items = await _chatService.loadMessages(
        size: 50,
        channelId: widget.channel?.id,
        receiverId: _isChannelChat ? null : widget.currentUser?.id,
      );
      // Process sender key messages, skip from display
      for (final m in items) {
        if (m.messageType == 'e2ee_key' && ChatCrypto.isSenderKeyMessage(m.content) && _isChannelChat) {
          await _handleSenderKeyMessage(m);
        }
      }
      // Unpack messages (secuencial: cada descifrado puede usar un isolate)
      final unpacked = <Message>[];
      for (final m in items.where((m) => m.messageType != 'e2ee_key')) {
        final unpackedContent = await _unpackContent(m.content, m.senderId);
        unpacked.add(Message(
          id: m.id,
          content: unpackedContent,
          senderId: m.senderId,
          receiverId: m.receiverId,
          channelId: m.channelId,
          isRead: m.isRead,
          createdAt: m.createdAt,
          messageType: m.messageType,
          mediaUrl: m.mediaUrl,
          latitude: m.latitude,
          longitude: m.longitude,
          vcardData: m.vcardData,
          icalData: m.icalData,
        ));
      }

      await OfflineCacheService.instance.put('message_list', unpacked.map((m) => m.toJson()).toList());
      if (mounted) {
        setState(() {
          _bubbles.clear();
          for (final msg in unpacked) {
            _bubbles.add(ChatBubble(message: msg, isMe: msg.senderId == widget.currentUser?.id, l10n: l10n));
          }
          _isLoading = false;
          _isOfflineData = false;
        });
        _scrollToBottom();
      }
    } catch (e) {
      debugPrint('Error: $e');
      final cached = OfflineCacheService.instance.get('message_list');
      if (cached != null && mounted) {
        final items = (cached as List).map((j) => Message.fromJson(Map<String, dynamic>.from(j))).toList();
        setState(() {
          _bubbles.clear();
          for (final msg in items) {
            _bubbles.add(ChatBubble(message: msg, isMe: msg.senderId == widget.currentUser?.id, l10n: l10n));
          }
          _isLoading = false;
          _isOfflineData = true;
        });
        _scrollToBottom();
        if (!_offlineNotified) {
          _offlineNotified = true;
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(l10n.offline), behavior: SnackBarBehavior.floating),
          );
        }
      } else if (mounted) {
        setState(() {
          _bubbles.clear();
          _bubbles.add(ChatBubble(message: Message(content: l10n.welcomeChat, senderId: 0), isMe: false, senderName: l10n.systemSender));
          _isLoading = false;
        });
      }
    }
  }

  // ---------------------------------------------------------------------------
  // Sending
  // ---------------------------------------------------------------------------

  Future<void> _sendText() async {
    final text = _messageController.text.trim();
    if (text.isEmpty || widget.currentUser == null) return;
    _messageController.clear();
    await _doSend(content: text);
  }

  Future<void> _sendEmoji(String emoji) async {
    if (widget.currentUser == null) return;
    await _doSend(content: emoji);
  }

  Future<void> _pickAndSendImage() async {
    final source = await showDialog<ImageSource>(
      context: context,
      builder: (ctx) => SimpleDialog(
        title: Text(l10n.attachFile),
        children: [
          SimpleDialogOption(
            onPressed: () => Navigator.pop(ctx, ImageSource.camera),
            child: ListTile(leading: const Icon(Icons.camera_alt), title: Text(l10n.camera)),
          ),
          SimpleDialogOption(
            onPressed: () => Navigator.pop(ctx, ImageSource.gallery),
            child: ListTile(leading: const Icon(Icons.photo_library), title: Text(l10n.gallery)),
          ),
        ],
      ),
    );
    if (source == null || widget.currentUser == null) return;
    try {
      final XFile? picked = await _imagePicker.pickImage(source: source, maxWidth: 1200);
      if (picked == null) return;
      setState(() => _isSending = true);
      final url = await _chatService.api.uploadChatImage(picked.path);
      await _doSend(content: '', messageType: 'image', mediaUrl: url);
    } catch (e) {
      debugPrint('Error: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.imageSendError), behavior: SnackBarBehavior.floating),
        );
      }
    } finally {
      if (mounted) setState(() => _isSending = false);
    }
  }

  Future<void> _pickAndSendLocation() async {
    if (widget.currentUser == null) return;
    try {
      setState(() => _isSending = true);
      final pos = await Geolocator.getCurrentPosition();
      await _doSend(
        content: '${pos.latitude.toStringAsFixed(6)}, ${pos.longitude.toStringAsFixed(6)}',
        messageType: 'location',
        latitude: pos.latitude,
        longitude: pos.longitude,
      );
    } catch (e) {
      debugPrint('Error: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.locationFetchError), behavior: SnackBarBehavior.floating),
        );
      }
    } finally {
      if (mounted) setState(() => _isSending = false);
    }
  }

  Future<void> _pickAndSendVcard() async {
    if (widget.currentUser == null) return;
    final result = await showDialog<Map<String, String>>(
      context: context,
      builder: (ctx) => _VcardDialog(),
    );
    if (result == null) return;
    await _doSend(content: result['name'] ?? '', messageType: 'vcard', vcardData: json.encode(result));
  }

  Future<void> _pickAndSendIcal() async {
    if (widget.currentUser == null) return;
    final result = await showDialog<Map<String, String>>(
      context: context,
      builder: (ctx) => _IcalDialog(),
    );
    if (result == null) return;
    await _doSend(content: result['title'] ?? '', messageType: 'ical', icalData: json.encode(result));
  }

  /// Genera, persiste y difunde una nueva clave de remitente para un canal.
  Future<void> _ensureSenderKey() async {
    if (!_isChannelChat || _senderKey != null) return;
    final channelId = widget.channel!.id;
    if (channelId == null) return;
    final auth = AuthService();
    final myPrivKey = await auth.getPrivateKey();
    final myPubKey = await auth.getPublicKey();
    if (myPrivKey == null || myPubKey == null) return;

    _senderKey = ChatCrypto.generateSenderKey();
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('sender_key_$channelId', base64Url.encode(_senderKey!));

    _broadcastSenderKey(channelId, myPrivKey);
  }

  /// Envía la clave de remitente del canal a cada miembro, cifrada con su clave.
  Future<void> _broadcastSenderKey(int channelId, String myPrivKey) async {
    try {
      final senderKey = _senderKey;
      final myId = widget.currentUser?.id;
      if (senderKey == null || myId == null) return;
      final members = await ChannelApiService().getChannelMembers(channelId);
      for (final member in members) {
        if (member.userId == myId) continue;
        final theirPubKey = await ChannelApiService().getPublicKey(member.userId);
        if (theirPubKey == null) continue;
        final encrypted = await ChatCrypto.encryptSenderKeyAsync(senderKey, myPrivKey, theirPubKey);
        await _chatService.sendMessage(
          senderId: myId,
          content: ChatCrypto.wrapSenderKey(encrypted),
          channelId: channelId,
          messageType: 'e2ee_key',
        );
      }
    } catch (e) { debugPrint('Error: $e'); }
  }

  /// Prepara y envía un mensaje, encolándolo offline si el envío falla.
  Future<void> _doSend({
    required String content,
    String messageType = 'text',
    String? mediaUrl,
    double? latitude,
    double? longitude,
    String? vcardData,
    String? icalData,
  }) async {
    if (widget.currentUser == null) return;
    setState(() => _isSending = true);

    await _ensureSenderKey();

    String packedContent;
    if (messageType == 'text') {
      packedContent = await _prepareContent(content, widget.channel?.id ?? 0);
    } else {
      packedContent = content;
    }

    try {
      final msg = await _chatService.sendMessage(
        senderId: widget.currentUser!.id!,
        content: packedContent,
        channelId: widget.channel?.id,
        messageType: messageType,
        mediaUrl: mediaUrl,
        latitude: latitude,
        longitude: longitude,
        vcardData: vcardData,
        icalData: icalData,
      );
      if (mounted) {
        setState(() {
          _bubbles.add(ChatBubble(
            message: Message(
              id: msg.id,
              content: content,
              senderId: msg.senderId,
              channelId: msg.channelId,
              messageType: msg.messageType,
              mediaUrl: msg.mediaUrl,
              latitude: msg.latitude,
              longitude: msg.longitude,
              vcardData: msg.vcardData,
              icalData: msg.icalData,
              createdAt: msg.createdAt,
            ),
            isMe: true,
          ));
        });
        _scrollToBottom();
      }
    } catch (e) {
      debugPrint('Error: $e');
      if (mounted) {
        final localMsg = Message(
          content: content,
          senderId: widget.currentUser!.id!,
          channelId: widget.channel?.id,
          messageType: messageType,
          mediaUrl: mediaUrl,
          latitude: latitude,
          longitude: longitude,
          vcardData: vcardData,
          icalData: icalData,
        );
        setState(() {
          _bubbles.add(ChatBubble(message: localMsg, isMe: true));
          _isOfflineData = true;
        });
        _scrollToBottom();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.messageQueuedOffline), behavior: SnackBarBehavior.floating),
        );
        await SyncQueueService.instance.enqueue(entityType: 'message', operation: 'create', payload: localMsg.toJson());
      }
    } finally {
      if (mounted) setState(() => _isSending = false);
    }
  }

  void _showAttachmentSheet() {
    final cs = Theme.of(context).colorScheme;
    showModalBottomSheet(
      context: context,
      builder: (ctx) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const SizedBox(height: 8),
            Container(
              width: 32, height: 4,
              decoration: BoxDecoration(color: cs.onSurfaceVariant.withAlpha(60), borderRadius: BorderRadius.circular(2)),
            ),
            const SizedBox(height: 8),
            _attachmentTile(Icons.image_rounded, l10n.image, () { Navigator.pop(ctx); _pickAndSendImage(); }, cs),
            _attachmentTile(Icons.location_on_rounded, l10n.location, () { Navigator.pop(ctx); _pickAndSendLocation(); }, cs),
            _attachmentTile(Icons.contact_page_rounded, l10n.vcard, () { Navigator.pop(ctx); _pickAndSendVcard(); }, cs),
            _attachmentTile(Icons.calendar_today_rounded, l10n.ical, () { Navigator.pop(ctx); _pickAndSendIcal(); }, cs),
            const SizedBox(height: 8),
          ],
        ),
      ),
    );
  }

  Widget _attachmentTile(IconData icon, String label, VoidCallback onTap, ColorScheme cs) {
    return ListTile(
      leading: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(color: cs.primaryContainer.withAlpha(100), borderRadius: BorderRadius.circular(10)),
        child: Icon(icon, size: 20, color: cs.primary),
      ),
      title: Text(label),
      onTap: onTap,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
    );
  }

  void _showEmojiPicker() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      useSafeArea: true,
      builder: (ctx) => EmojiPicker(
        onEmojiSelected: (emoji) {
          Navigator.pop(ctx);
          _sendEmoji(emoji);
        },
      ),
    );
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300), curve: Curves.easeOut,
        );
      }
    });
  }

  // ---------------------------------------------------------------------------
  // Build
  // ---------------------------------------------------------------------------

  @override
  Widget build(BuildContext context) {
    l10n = AppLocalizations.of(context)!;
    return Scaffold(
      appBar: widget.channel != null
          ? AppBar(
              title: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(widget.channel!.name, style: const TextStyle(fontSize: 16)),
                  Text(widget.channel!.channelType == 'private' ? l10n.privateRoom : l10n.communityChannel,
                      style: const TextStyle(fontSize: 11, fontWeight: FontWeight.normal)),
                ],
              ),
            )
          : null,
      body: Column(
        children: [
          if (_isOfflineData)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              color: Theme.of(context).colorScheme.surfaceContainerHigh,
              child: Row(
                children: [
                  Icon(Icons.wifi_off, size: 16, color: Theme.of(context).colorScheme.onSurfaceVariant),
                  const SizedBox(width: 8),
                  Text(l10n.cacheData, style: TextStyle(fontSize: 12, color: Theme.of(context).colorScheme.onSurfaceVariant)),
                ],
              ),
            ),
          if (_isReconnecting)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              color: Theme.of(context).colorScheme.errorContainer,
              child: Row(
                children: [
                  SizedBox(
                    width: 14,
                    height: 14,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: Theme.of(context).colorScheme.onErrorContainer,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Text(l10n.reconnecting, style: TextStyle(fontSize: 12, color: Theme.of(context).colorScheme.onErrorContainer)),
                ],
              ),
            ),
          Expanded(
            child: _isLoading
                ? Center(child: Text(l10n.loading))
                : RefreshIndicator(
                    onRefresh: _loadMessages,
                    child: ListView.builder(
                      controller: _scrollController,
                      padding: const EdgeInsets.all(8),
                      itemCount: _bubbles.length,
                      itemBuilder: (context, index) => ChatBubbleWidget(bubble: _bubbles[index], l10n: l10n),
                    ),
                  ),
          ),
          ChatInputBar(
            controller: _messageController,
            isSending: _isSending,
            l10n: l10n,
            onSend: _sendText,
            onEmoji: _showEmojiPicker,
            onAttach: _showAttachmentSheet,
          ),
        ],
      ),
    );
  }
}

// -- Dialogs ------------------------------------------------------------------

/// Diálogo para componer un contacto vCard y enviarlo como mensaje.
class _VcardDialog extends StatefulWidget {
  @override
  State<_VcardDialog> createState() => _VcardDialogState();
}

class _VcardDialogState extends State<_VcardDialog> {
  final _nameCtrl = TextEditingController();
  final _phoneCtrl = TextEditingController();
  final _emailCtrl = TextEditingController();
  late AppLocalizations l10n;

  @override
  void didChangeDependencies() { super.didChangeDependencies(); l10n = AppLocalizations.of(context)!; }

  @override
  void dispose() { _nameCtrl.dispose(); _phoneCtrl.dispose(); _emailCtrl.dispose(); super.dispose(); }

  @override
  Widget build(BuildContext context) {
    l10n = AppLocalizations.of(context)!;
    return AlertDialog(
      title: Row(children: [const Icon(Icons.contact_page), const SizedBox(width: 8), Text(l10n.sendContact)]),
      content: Column(mainAxisSize: MainAxisSize.min, children: [
        TextField(controller: _nameCtrl, decoration: InputDecoration(labelText: l10n.name)),
        const SizedBox(height: 8),
        TextField(controller: _phoneCtrl, decoration: InputDecoration(labelText: l10n.phone), keyboardType: TextInputType.phone),
        const SizedBox(height: 8),
        TextField(controller: _emailCtrl, decoration: InputDecoration(labelText: l10n.email), keyboardType: TextInputType.emailAddress),
      ]),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context), child: Text(l10n.cancel)),
        FilledButton(onPressed: () {
          if (_nameCtrl.text.trim().isEmpty) return;
          Navigator.pop(context, {'name': _nameCtrl.text.trim(), 'phone': _phoneCtrl.text.trim(), 'email': _emailCtrl.text.trim()});
        }, child: Text(l10n.send)),
      ],
    );
  }
}

/// Diálogo para componer un evento iCal y enviarlo como mensaje.
class _IcalDialog extends StatefulWidget {
  @override
  State<_IcalDialog> createState() => _IcalDialogState();
}

class _IcalDialogState extends State<_IcalDialog> {
  final _titleCtrl = TextEditingController();
  final _startCtrl = TextEditingController();
  final _endCtrl = TextEditingController();
  final _descCtrl = TextEditingController();
  late AppLocalizations l10n;

  @override
  void didChangeDependencies() { super.didChangeDependencies(); l10n = AppLocalizations.of(context)!; }

  @override
  void dispose() { _titleCtrl.dispose(); _startCtrl.dispose(); _endCtrl.dispose(); _descCtrl.dispose(); super.dispose(); }

  @override
  Widget build(BuildContext context) {
    l10n = AppLocalizations.of(context)!;
    return AlertDialog(
      title: Row(children: [const Icon(Icons.calendar_today), const SizedBox(width: 8), Text(l10n.sendEvent)]),
      content: Column(mainAxisSize: MainAxisSize.min, children: [
        TextField(controller: _titleCtrl, decoration: InputDecoration(labelText: l10n.title)),
        const SizedBox(height: 8),
        TextField(controller: _startCtrl, decoration: InputDecoration(labelText: l10n.startDateHint)),
        const SizedBox(height: 8),
        TextField(controller: _endCtrl, decoration: InputDecoration(labelText: l10n.endDateHint)),
        const SizedBox(height: 8),
        TextField(controller: _descCtrl, decoration: InputDecoration(labelText: l10n.description), maxLines: 2),
      ]),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context), child: Text(l10n.cancel)),
        FilledButton(onPressed: () {
          if (_titleCtrl.text.trim().isEmpty) return;
          Navigator.pop(context, {'title': _titleCtrl.text.trim(), 'start': _startCtrl.text.trim(), 'end': _endCtrl.text.trim(), 'description': _descCtrl.text.trim()});
        }, child: Text(l10n.send)),
      ],
    );
  }
}
