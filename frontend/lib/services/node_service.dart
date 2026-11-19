import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

import 'node_info_model.dart';

/// Gestión de la lista de nodos federados conocidos por la app.
///
/// Persiste los nodos en SharedPreferences y expone el nodo activo plus una
/// lista ordenada para fallback (activo primero, luego el resto habilitados).
/// Singleton al estilo del resto de servicios de la app.
class NodeService {
  static final NodeService _instance = NodeService._internal();
  factory NodeService() => _instance;

  static const String _key = 'backend_nodes';

  List<NodeInfo> _nodes = [];
  NodeInfo? _active;

  NodeService._internal();

  bool get isEmpty => _nodes.isEmpty;
  List<NodeInfo> get nodes => List.unmodifiable(_nodes);
  NodeInfo? get activeNode => _active;

  /// Carga los nodos desde SharedPreferences. Llama una vez al arranque.
  Future<void> load() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getStringList(_key) ?? <String>[];
    _nodes = <NodeInfo>[];
    for (final e in raw) {
      try {
        _nodes.add(NodeInfo.fromJson(jsonDecode(e) as Map<String, dynamic>));
      } catch (_) {}
    }
    _active = null;
    for (final n in _nodes) {
      if (n.isActive) { _active = n; break; }
    }
    if (_active == null && _nodes.isNotEmpty) _active = _nodes.first;
  }

  /// Guarda la lista actual en SharedPreferences.
  Future<void> _save() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setStringList(
      _key,
      _nodes.map((n) => jsonEncode(n.toJson())).toList(),
    );
  }

  /// Añade o actualiza un nodo. Si [markActive] lo marca como el activo (desactiva
  /// los demás). Retorna el nodo activo actual.
  Future<NodeInfo> upsert(NodeInfo node, {bool markActive = false}) async {
    final existing = _nodes.indexWhere((n) => n.domain == node.domain);
    final now = DateTime.now();
    final entry = node.copyWith(lastSeen: now);
    if (existing >= 0) {
      _nodes[existing] = entry;
    } else {
      _nodes.add(entry);
    }
    if (markActive) {
      await setActive(entry.id);
    } else if (_active == null || _nodes.length == 1) {
      await setActive(entry.id);
    }
    await _save();
    return _active!;
  }

  /// Elimina un nodo por dominio.
  Future<bool> remove(String domain) async {
    final before = _nodes.length;
    _nodes.removeWhere((n) => n.domain == domain);
    if (_nodes.length < before) {
      if (_active?.domain == domain) {
        _active = _nodes.isNotEmpty ? _nodes.first : null;
        if (_active != null) {
          _active = _active!.copyWith(isActive: true);
        }
      }
      await _save();
      return true;
    }
    return false;
  }

  /// Establece el nodo activo por id. Devuelve el nodo activo o null.
  Future<NodeInfo?> setActive(String id) async {
    _nodes = _nodes.map((n) => n.copyWith(isActive: n.id == id)).toList();
    _active = null;
    for (final n in _nodes) {
      if (n.id == id) { _active = n; break; }
    }
    await _save();
    return _active;
  }

  /// Lista ordenada para peticiones con fallback: activo primero, luego el resto
  /// de nodos habilitados (sin repetir el activo).
  List<NodeInfo> fallbackOrder() {
    final result = <NodeInfo>[];
    if (_active != null && _active!.enabled) result.add(_active!);
    result.addAll(_nodes.where((n) => n.id != _active?.id && n.enabled));
    return result;
  }

  /// Marca el nodo como visto (actualiza lastSeen).
  Future<void> markSeen(String domain) async {
    final idx = _nodes.indexWhere((n) => n.domain == domain);
    if (idx >= 0) {
      _nodes[idx] = _nodes[idx].copyWith(lastSeen: DateTime.now());
      await _save();
    }
  }
}

extension NodeInfoCopy on NodeInfo {
  NodeInfo copyWith({
    String? id,
    String? domain,
    String? baseUrl,
    String? displayName,
    List<String>? capabilities,
    bool? trusted,
    bool? enabled,
    DateTime? lastSeen,
    bool? isActive,
  }) {
    return NodeInfo(
      id: id ?? this.id,
      domain: domain ?? this.domain,
      baseUrl: baseUrl ?? this.baseUrl,
      displayName: displayName ?? this.displayName,
      capabilities: capabilities ?? this.capabilities,
      trusted: trusted ?? this.trusted,
      enabled: enabled ?? this.enabled,
      lastSeen: lastSeen ?? this.lastSeen,
      isActive: isActive ?? this.isActive,
    );
  }
}
