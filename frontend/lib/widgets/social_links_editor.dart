import 'package:flutter/material.dart';

class SocialLinksEditor extends StatefulWidget {
  final Map<String, String> initial;
  final ValueChanged<Map<String, String>> onChanged;

  const SocialLinksEditor({
    super.key,
    this.initial = const {},
    required this.onChanged,
  });

  @override
  State<SocialLinksEditor> createState() => _SocialLinksEditorState();
}

class _SocialLinksEditorState extends State<SocialLinksEditor> {
  static const _known = ['website', 'instagram', 'x', 'youtube', 'facebook'];
  late Map<String, TextEditingController> _controllers;
  late List<String> _order;
  final TextEditingController _customKeyController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _order = [
      for (final k in _known) k,
      for (final k in widget.initial.keys)
        if (!_known.contains(k)) k,
    ];
    _controllers = {
      for (final k in _order)
        k: TextEditingController(text: widget.initial[k] ?? ''),
    };
    for (final c in _controllers.values) {
      c.addListener(_emit);
    }
  }

  void _emit() {
    final result = <String, String>{};
    for (final entry in _controllers.entries) {
      final v = entry.value.text.trim();
      if (v.isNotEmpty) result[entry.key] = v;
    }
    widget.onChanged(result);
  }

  void _addCustom() {
    final key = _customKeyController.text.trim().toLowerCase();
    if (key.isEmpty || _controllers.containsKey(key)) return;
    final controller = TextEditingController();
    controller.addListener(_emit);
    setState(() {
      _order.add(key);
      _controllers[key] = controller;
      _customKeyController.clear();
    });
  }

  void _remove(String key) {
    setState(() {
      _controllers[key]?.dispose();
      _controllers.remove(key);
      _order.remove(key);
    });
    _emit();
  }

  @override
  void dispose() {
    for (final c in _controllers.values) {
      c.dispose();
    }
    _customKeyController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Semantics(
      container: true,
      label: 'Enlaces sociales',
      child: Column(
        children: [
          for (final key in _order)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 4),
              child: Row(
                children: [
                  Expanded(
                    child: Semantics(
                      textField: true,
                      label: key,
                      child: TextField(
                        controller: _controllers[key],
                        decoration: InputDecoration(
                          labelText: key,
                          border: const OutlineInputBorder(),
                        ),
                        keyboardType: TextInputType.url,
                        textInputAction: TextInputAction.next,
                      ),
                    ),
                  ),
                  if (!_known.contains(key))
                    IconButton(
                      tooltip: 'Delete',
                      icon: const Icon(Icons.delete_outline),
                      onPressed: () => _remove(key),
                    ),
                ],
              ),
            ),
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _customKeyController,
                  decoration: const InputDecoration(
                    labelText: 'custom',
                    border: OutlineInputBorder(),
                  ),
                  textInputAction: TextInputAction.done,
                  onSubmitted: (_) => _addCustom(),
                ),
              ),
              const SizedBox(width: 8),
              FilledButton.icon(
                onPressed: _addCustom,
                icon: const Icon(Icons.add_outlined),
                label: const Text('add'),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
