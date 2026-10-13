import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../models/user_model.dart';
import '../services/channel_service.dart';

/// Pantalla para crear un nuevo canal de chat (comunidad o sala privada).
class CreateChannelScreen extends StatefulWidget {
  final User? currentUser;

  const CreateChannelScreen({super.key, this.currentUser});

  @override
  State<CreateChannelScreen> createState() => _CreateChannelScreenState();
}

/// Mantiene los campos del formulario y el tipo de canal/límite de miembros
/// seleccionados.
class _CreateChannelScreenState extends State<CreateChannelScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameCtrl = TextEditingController();
  final _descCtrl = TextEditingController();
  final ChannelApiService _channelApi = ChannelApiService();
  late AppLocalizations l10n;

  String _channelType = 'community';
  int _maxMembers = 20;
  bool _isCreating = false;

  @override
  void dispose() {
    _nameCtrl.dispose();
    _descCtrl.dispose();
    super.dispose();
  }

  /// Valida el formulario y crea el canal, cerrando con el resultado.
  Future<void> _create() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _isCreating = true);

    try {
      final channel = await _channelApi.createChannel(
        name: _nameCtrl.text.trim(),
        description: _descCtrl.text.trim().isEmpty ? null : _descCtrl.text.trim(),
        channelType: _channelType,
        maxMembers: _channelType == 'private' ? _maxMembers : null,
      );
      if (mounted) Navigator.pop(context, channel);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.errorFor(e)), behavior: SnackBarBehavior.floating),
        );
        setState(() => _isCreating = false);
      }
    }
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    l10n = AppLocalizations.of(context)!;
  }

  @override
  Widget build(BuildContext context) {
    l10n = AppLocalizations.of(context)!;
    return Scaffold(
      appBar: AppBar(title: Text(l10n.createChannel)),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            TextFormField(
              controller: _nameCtrl,
              decoration: InputDecoration(labelText: l10n.channelName, border: const OutlineInputBorder()),
              validator: (v) => (v == null || v.trim().isEmpty) ? l10n.channelRequired : null,
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _descCtrl,
              decoration: InputDecoration(labelText: l10n.channelDescriptionOptional, border: const OutlineInputBorder()),
              maxLines: 2,
            ),
            const SizedBox(height: 16),
            Text(l10n.channelType, style: Theme.of(context).textTheme.titleSmall),
            const SizedBox(height: 8),
            SegmentedButton<String>(
              segments: [
                ButtonSegment(value: 'community', label: Text(l10n.channelCommunity), icon: const Icon(Icons.forum)),
                ButtonSegment(value: 'private', label: Text(l10n.channelPrivate), icon: const Icon(Icons.lock)),
              ],
              selected: {_channelType},
              onSelectionChanged: (v) => setState(() => _channelType = v.first),
            ),
            if (_channelType == 'private') ...[
              const SizedBox(height: 16),
              Text(l10n.maxMembers.replaceAll('{count}', '$_maxMembers'), style: Theme.of(context).textTheme.titleSmall),
              Slider(
                value: _maxMembers.toDouble(),
                min: 2,
                max: 20,
                divisions: 18,
                label: '$_maxMembers',
                onChanged: (v) => setState(() => _maxMembers = v.round()),
              ),
            ],
            const SizedBox(height: 24),
            FilledButton.icon(
              icon: _isCreating
                  ? const SizedBox(height: 18, width: 18, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                  : const Icon(Icons.add),
              label: Text(l10n.createChannel),
              onPressed: _isCreating ? null : _create,
            ),
          ],
        ),
      ),
    );
  }
}
