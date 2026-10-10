import 'dart:convert';
import 'dart:math';
import 'package:hive_flutter/hive_flutter.dart';
import 'api_service.dart';

/// Estados posibles para una operación de sincronización en cola.
enum SyncStatus { pending, syncing, failed }

/// Una mutación realizada sin conexión que debe reproducirse en el backend.
class SyncOperation {
  final String id;
  final String entityType; // festival, user, shortfilm, message
  final String operation; // create, update, delete
  final int? entityId;
  final Map<String, dynamic> payload;
  final DateTime createdAt;
  SyncStatus status;
  String? errorMessage;
  int attempts;

  SyncOperation({
    required this.id,
    required this.entityType,
    required this.operation,
    this.entityId,
    required this.payload,
    required this.createdAt,
    this.status = SyncStatus.pending,
    this.errorMessage,
    this.attempts = 0,
  });

  Map<String, dynamic> toJson() => {
        'id': id,
        'entity_type': entityType,
        'operation': operation,
        'entity_id': entityId,
        'payload': payload,
        'created_at': createdAt.toIso8601String(),
        'status': status.name,
        'error_message': errorMessage,
        'attempts': attempts,
      };

  factory SyncOperation.fromJson(Map<String, dynamic> json) => SyncOperation(
        id: json['id'] as String,
        entityType: json['entity_type'] as String,
        operation: json['operation'] as String,
        entityId: json['entity_id'] as int?,
        payload: Map<String, dynamic>.from(json['payload']),
        createdAt: DateTime.parse(json['created_at'] as String),
        status: SyncStatus.values.firstWhere(
          (s) => s.name == json['status'],
          orElse: () => SyncStatus.pending,
        ),
        errorMessage: json['error_message'] as String?,
        attempts: json['attempts'] as int? ?? 0,
      );
}

/// Cola de mutaciones sin conexión que se reproducen contra el backend cuando
/// se restaura la conectividad.
///
/// Las operaciones se almacenan en una caja de Hive dedicada para sobrevivir
/// a los reinicios de la app. Al reconectarse se avisa al usuario y, al
/// confirmarlo, la cola se vacía en orden FIFO.
class SyncQueueService {
  /// Singleton compartido del servicio.
  static final SyncQueueService instance = SyncQueueService._internal();

  factory SyncQueueService({ApiService? api}) {
    if (api != null) instance._apiOverride = api;
    return instance;
  }

  SyncQueueService._internal([ApiService? api]) : _api = api ?? ApiService();

  ApiService? _apiOverride;
  ApiService get _effectiveApi => _apiOverride ?? _api;

  static const String _boxName = 'sync_queue';
  static const String _queueKey = 'operations';
  /// Número máximo de reintentos por operación.
  static const int maxAttempts = 3;

  late Box _box;
  final ApiService _api;
  bool _syncing = false;

  /// Inicializa la caja de la cola.
  Future<void> init() async {
    _box = await Hive.openBox(_boxName);
  }

  static String _newId() {
    final bytes = List<int>.generate(16, (_) => _random.nextInt(256));
    bytes[6] = (bytes[6] & 0x0f) | 0x40;
    bytes[8] = (bytes[8] & 0x3f) | 0x80;
    final hex = bytes.map((b) => b.toRadixString(16).padLeft(2, '0')).join();
    return '${hex.substring(0, 8)}-${hex.substring(8, 12)}-${hex.substring(12, 16)}-${hex.substring(16, 20)}-${hex.substring(20)}';
  }

  static final Random _random = Random.secure();

  List<SyncOperation> _loadQueue() {
    final raw = _box.get(_queueKey);
    if (raw == null) return [];
    final list = List<Map<String, dynamic>>.from(raw);
    return list.map((j) => SyncOperation.fromJson(j)).toList();
  }

  Future<void> _saveQueue(List<SyncOperation> queue) async {
    await _box.put(_queueKey, queue.map((op) => op.toJson()).toList());
  }

  /// Añade una nueva operación de sincronización a la cola.
  Future<void> enqueue({
    required String entityType,
    required String operation,
    int? entityId,
    required Map<String, dynamic> payload,
  }) async {
    final queue = _loadQueue();
    queue.add(SyncOperation(
      id: _newId(),
      entityType: entityType,
      operation: operation,
      entityId: entityId,
      payload: payload,
      createdAt: DateTime.now(),
    ));
    await _saveQueue(queue);
  }

  /// Indica si ya existe una operación equivalente en cola.
  bool contains({
    required String entityType,
    required String operation,
    int? entityId,
    Map<String, dynamic>? payload,
  }) {
    final queue = _loadQueue();
    return queue.any((op) {
      if (op.entityType != entityType) return false;
      if (op.operation != operation) return false;
      if (op.status == SyncStatus.syncing) return false;
      if (entityId != null && op.entityId != entityId) return false;
      if (payload != null &&
          payload['content'] != null &&
          op.payload['content'] != payload['content']) {
        return false;
      }
      return true;
    });
  }

  /// Número de operaciones pendientes (y reintentables).
  int get pendingCount => _loadQueue()
      .where((op) =>
          op.status == SyncStatus.pending ||
          (op.status == SyncStatus.failed && op.attempts < maxAttempts))
      .length;

  /// Indica si hay operaciones pendientes de sincronizar.
  bool get hasPending => pendingCount > 0;

  /// Vacía la cola: reproduce todas las operaciones pendientes y reintentables en orden FIFO.
  ///
  /// No reentrante: si ya hay un vaciado en curso, retorna inmediatamente.
  /// Las operaciones que fallan se reintentan en vaciados posteriores hasta [maxAttempts]
  /// intentos, tras los cuales se marcan como `failed` y quedan para inspección.
  /// Devuelve un mapa resumen con `synced` (count), `failed` (count) y
  /// `errors` (lista de mensajes de error).
  Future<Map<String, dynamic>> syncAll() async {
    if (_syncing) {
      return {'synced': 0, 'failed': 0, 'errors': <String>[]};
    }
    _syncing = true;
    try {
      final queue = _loadQueue();
      int synced = 0;
      int failed = 0;
      final List<String> errors = [];

      for (final op in queue) {
        if (op.status == SyncStatus.syncing) continue;
        if (op.status == SyncStatus.failed && op.attempts >= maxAttempts) {
          continue;
        }
        op.status = SyncStatus.syncing;
        await _saveQueue(queue);

        try {
          if (op.attempts > 0) {
            final delayMs = 300 * (1 << (op.attempts - 1));
            await Future.delayed(
                Duration(milliseconds: delayMs > 5000 ? 5000 : delayMs));
          }
          await _executeOperation(op);
          synced++;
        } catch (e) {
          op.attempts++;
          op.errorMessage = e.toString();
          op.status = op.attempts >= maxAttempts
              ? SyncStatus.failed
              : SyncStatus.pending;
          failed++;
          errors.add('${op.entityType}/${op.operation}: ${e.toString()}');
        }
      }

      // Remove successfully synced operations.
      queue.removeWhere(
          (op) => op.status == SyncStatus.syncing && op.errorMessage == null);
      // Keep failed operations for inspection/retry.

      await _saveQueue(queue);

      return {
        'synced': synced,
        'failed': failed,
        'errors': errors,
      };
    } finally {
      _syncing = false;
    }
  }

  Future<void> _executeOperation(SyncOperation op) async {
    final api = _effectiveApi;
    final path = '/${_pluralize(op.entityType)}/'
        '${op.entityId != null ? '${op.entityId}' : ''}';

    switch (op.operation) {
      case 'create':
        await api.create(path, op.payload);
        break;
      case 'update':
        if (op.entityId == null) throw Exception('entityId required for update');
        await api.request('PUT', path, body: json.encode(op.payload));
        break;
      case 'delete':
        if (op.entityId == null) throw Exception('entityId required for delete');
        await api.request('DELETE', path);
        break;
    }
  }

  String _pluralize(String entity) {
    switch (entity) {
      case 'festival':
        return 'festivals';
      case 'user':
        return 'users';
      case 'shortfilm':
        return 'shortfilms';
      case 'message':
        return 'chat/messages';
      default:
        return '${entity}s';
    }
  }

  /// Elimina todas las operaciones en cola.
  Future<void> clear() async {
    await _box.clear();
  }
}
