import 'package:material_ui/material_ui.dart';
import '../l10n/app_localizations.dart';

import '../services/connectivity_monitor.dart';
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
  AppLocalizations get l10n => AppLocalizations.of(context)!;
  bool _loading = false;
  String? _status;
  bool _allNodesDown = false;
  @override
  void initState() {
    super.initState();
    _refresh();
  }

  Future<void> _refresh() async {
    setState(() => _loading = true);
    await _nodes.load();
    if (!mounted) return;
    await _testAll();
    if (!mounted) return;
    setState(() => _loading = false);
  }

  Future<void> _testAll() async {
    final monitor = ConnectivityMonitor.instance;
    final ok = await monitor.checkNow();
    _allNodesDown = !ok;
    _status = ok ? l10n.nodeAnyOnline : l10n.nodeNoneOnline;
    if (mounted) setState(() {});
  }

  Future<void> _retryNode(NodeInfo node) async {
    await ConnectivityMonitor.instance.checkNow();
    await _nodes.markSeen(node.domain);
    if (mounted) setState(() {});
  }

  Future<void> _addNode() async {
    final domainCtrl = TextEditingController();
    final urlCtrl = TextEditingController();
    final nameCtrl = TextEditingController();
    final ok = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: Text(l10n.nodeAddFederated),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: domainCtrl,
              decoration: InputDecoration(labelText: l10n.nodeDomainHint),
            ),
            TextField(
              controller: urlCtrl,
              decoration: InputDecoration(labelText: l10n.nodeBaseUrlHint),
            ),
            TextField(
              controller: nameCtrl,
              decoration: InputDecoration(labelText: l10n.nodeDisplayNameOptional),
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: Text(l10n.cancel)),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: Text(l10n.save),
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
        title: Text(l10n.nodeDelete),
        content: Text(l10n.deleteEntityMessage(node.displayName ?? node.domain)),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: Text(l10n.no)),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: Text(l10n.yes),
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
              Text('${l10n.active}: ${isActive ? l10n.yes : l10n.no}', style: const TextStyle(fontSize: 12)),
            ],
          ),
          const SizedBox(height: 2),
          NodeHealthRow(
            health: ConnectivityMonitor.instance.nodeHealth[n.domain],
            onlineLabel: l10n.nodeOnline,
            offlineLabel: l10n.nodeOffline,
            retryTooltip: l10n.nodeTestConnection,
            onRetry: () => _retryNode(n),
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
            tooltip: l10n.nodeMarkActive,
          ),
          IconButton(
            icon: const Icon(Icons.delete_outline, color: Colors.red),
            onPressed: () => _remove(n),
            tooltip: l10n.nodeDelete,
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
        title: Text(l10n.nodeTitle),
        actions: [
          IconButton(
            icon: const Icon(Icons.fact_check),
            onPressed: _loading ? null : _testAll,
            tooltip: l10n.nodeTestConnection,
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loading ? null : _refresh,
            tooltip: l10n.nodeReload,
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
                    color: _allNodesDown ? Colors.red.withAlpha(26) : Colors.green.withAlpha(26),
                    child: Row(
                      children: [
                        Icon(_allNodesDown ? Icons.error : Icons.check_circle,
                            color: _allNodesDown ? Colors.red : Colors.green, size: 20),
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
                                l10n.nodeEmptyTitle,
                                style: Theme.of(context).textTheme.titleMedium,
                              ),
                              const SizedBox(height: 8),
                              Text(
                                l10n.nodeEmptyHint,
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
        tooltip: l10n.nodeAddShort,
        child: const Icon(Icons.add),
      ),
    );
  }
}

class NodeHealthRow extends StatelessWidget {
  final NodeHealth? health;
  final String onlineLabel;
  final String offlineLabel;
  final String retryTooltip;
  final VoidCallback onRetry;

  const NodeHealthRow({
    super.key,
    this.health,
    required this.onlineLabel,
    required this.offlineLabel,
    required this.retryTooltip,
    required this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    final ok = health?.online ?? false;
    final details = health == null
        ? ''
        : '${_formatTime(health!.lastCheck)} · ${health!.latencyMs} ms';
    return Row(
      children: [
        Icon(ok ? Icons.wifi : Icons.wifi_off, color: ok ? Colors.green : Colors.red, size: 16),
        const SizedBox(width: 6),
        Text(ok ? onlineLabel : offlineLabel,
            style: TextStyle(fontSize: 12, color: ok ? Colors.green : Colors.red)),
        if (details.isNotEmpty) ...[
          const SizedBox(width: 8),
          Text(details, style: const TextStyle(fontSize: 11)),
        ],
        const Spacer(),
        SizedBox(
          width: 32,
          height: 32,
          child: IconButton(
            icon: const Icon(Icons.refresh, size: 18),
            onPressed: onRetry,
            tooltip: retryTooltip,
            padding: EdgeInsets.zero,
          ),
        ),
      ],
    );
  }

  String _formatTime(DateTime value) =>
      '${value.hour.toString().padLeft(2, '0')}:${value.minute.toString().padLeft(2, '0')}:${value.second.toString().padLeft(2, '0')}';
}
