import 'package:flutter/material.dart';

import '../services/api_service.dart';
import '../services/node_info_model.dart';
import '../services/node_service.dart';

/// Pantalla para gestionar los nodos federados conocidos por la app.
///
/// Permite ver la lista de nodos, marcar uno como activo, probar la
/// conectividad de cada uno, agregar nuevos nodos y eliminar los que ya no
/// se usen. El nodo activo se usa por defecto en las peticiones API; si cae,
/// se hace fallback automático al siguiente nodo habilitado.
class NodeManagementScreen extends StatefulWidget {
  const NodeManagementScreen({super.key});

  @override
  State<NodeManagementScreen> createState() => _NodeManagementScreenState();
}

class _NodeManagementScreenState extends State<NodeManagementScreen> {
  final NodeService _nodes = NodeService();
  final ApiService _api = ApiService();
  bool _loading = false;
  String? _status;
  final _nodeOk = <String, bool>{};
  @override
  void initState() {
    super.initState();
    _refresh();
  }

  Future<void> _refresh() async {
    setState(() => _loading = true);
    await _nodes.load();
    await _testAll();
    setState(() => _loading = false);
  }

  Future<void> _testAll() async {
    final ok = await _api.healthCheck();
    _status = ok ? 'Al menos un nodo responde' : 'Ningún nodo responde';
    for (final n in _nodes.nodes) {
      _nodeOk[n.domain] = await _api.testNode(n.effectiveUrl);
    }
    if (mounted) setState(() {});
  }

  Future<void> _addNode() async {
    final domainCtrl = TextEditingController();
    final urlCtrl = TextEditingController();
    final nameCtrl = TextEditingController();
    final ok = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Agregar nodo federado'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: domainCtrl,
              decoration: const InputDecoration(labelText: 'Dominio (ej. festival.example.com)'),
            ),
            TextField(
              controller: urlCtrl,
              decoration: const InputDecoration(labelText: 'URL base (sin /api)'),
            ),
            TextField(
              controller: nameCtrl,
              decoration: const InputDecoration(labelText: 'Nombre para mostrar (opcional)'),
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancelar')),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Guardar'),
          ),
        ],
      ),
    );
    if (ok != true) return;
    final domain = domainCtrl.text.trim();
    final url = urlCtrl.text.trim();
    if (domain.isEmpty || url.isEmpty) return;
    await _nodes.upsert(
      NodeInfo(
        id: domain,
        domain: domain,
        baseUrl: url,
        displayName: nameCtrl.text.trim().isEmpty ? domain : nameCtrl.text.trim(),
        trusted: false,
        enabled: true,
      ),
    );
    await _refresh();
  }

  Future<void> _setActive(NodeInfo node) async {
    await _nodes.setActive(node.id);
    await _refresh();
  }

  Future<void> _remove(NodeInfo node) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Eliminar nodo'),
        content: Text('¿Eliminar "${node.displayName ?? node.domain}"?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('No')),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Sí'),
          ),
        ],
      ),
    );
    if (confirm != true) return;
    await _nodes.remove(node.domain);
    await _refresh();
  }

  Widget _buildNodeTile(NodeInfo n) {
    final isActive = _nodes.activeNode?.id == n.id;
    final ok = _nodeOk[n.domain] ?? false;
    return ListTile(
      leading: CircleAvatar(
        child: Text((n.displayName ?? n.domain).isNotEmpty
            ? (n.displayName ?? n.domain)[0].toUpperCase()
            : '?'),
      ),
      title: Text(
        n.displayName ?? n.domain,
        style: TextStyle(fontWeight: isActive ? FontWeight.bold : FontWeight.normal),
      ),
      subtitle: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(n.effectiveUrl),
          const SizedBox(height: 4),
          Row(
            children: [
              Icon(
                isActive ? Icons.check_circle : Icons.radio_button_unchecked,
                color: isActive ? Colors.green : Colors.grey,
                size: 16,
              ),
              const SizedBox(width: 6),
              Text('Activo: ${isActive ? 'sí' : 'no'}', style: const TextStyle(fontSize: 12)),
              const SizedBox(width: 12),
              Icon(
                ok ? Icons.wifi : Icons.wifi_off,
                color: ok ? Colors.green : Colors.red,
                size: 16,
              ),
              const SizedBox(width: 6),
              Text(ok ? 'en línea' : 'sin respuesta', style: TextStyle(fontSize: 12, color: ok ? Colors.green : Colors.red)),
            ],
          ),
        ],
      ),
      trailing: Wrap(
        spacing: 8,
        children: [
          IconButton(
            icon: Icon(isActive ? Icons.check : Icons.radio_button_unchecked,
                color: isActive ? Colors.green : null),
            onPressed: () => _setActive(n),
            tooltip: 'Marcar como activo',
          ),
          IconButton(
            icon: const Icon(Icons.refresh, size: 20),
            onPressed: () async {
              _nodeOk[n.domain] = await _api.testNode(n.effectiveUrl);
              await _nodes.markSeen(n.domain);
              setState(() {});
            },
            tooltip: 'Probar conectividad',
          ),
          IconButton(
            icon: const Icon(Icons.delete_outline, color: Colors.red),
            onPressed: () => _remove(n),
            tooltip: 'Eliminar nodo',
          ),
        ],
      ),
      onTap: () => _setActive(n),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Nodos federados'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loading ? null : _refresh,
            tooltip: 'Recargar',
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                if (_status != null)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    color: _status!.contains('Ningún') ? Colors.red.withAlpha(26) : Colors.green.withAlpha(26),
                    child: Row(
                      children: [
                        Icon(_status!.contains('Ningún') ? Icons.error : Icons.check_circle,
                            color: _status!.contains('Ningún') ? Colors.red : Colors.green, size: 20),
                        const SizedBox(width: 8),
                        Expanded(child: Text(_status!)),
                      ],
                    ),
                  ),
                Expanded(
                  child: _nodes.nodes.isEmpty
                      ? Center(
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              const Icon(Icons.cloud_off, size: 64, color: Colors.grey),
                              const SizedBox(height: 16),
                              Text(
                                'No hay nodos configurados',
                                style: Theme.of(context).textTheme.titleMedium,
                              ),
                              const SizedBox(height: 8),
                              Text(
                                'Agrega al menos un nodo para poder usar la app con varios backends.',
                                textAlign: TextAlign.center,
                                style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: Colors.grey),
                              ),
                            ],
                          ),
                        )
                      : ListView.builder(
                          itemCount: _nodes.nodes.length,
                          itemBuilder: (_, i) => _buildNodeTile(_nodes.nodes[i]),
                        ),
                ),
              ],
            ),
      floatingActionButton: FloatingActionButton(
        onPressed: _loading ? null : _addNode,
        tooltip: 'Agregar nodo',
        child: const Icon(Icons.add),
      ),
    );
  }
}
