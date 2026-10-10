import 'dart:convert';
import 'dart:math';
import 'package:crypto/crypto.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Entrada almacenada en una caja de caché con firma HMAC de integridad.
class _CacheEntry {
  final String data; // JSON-encoded payload
  final String signature; // HMAC-SHA256 of data
  final int timestamp;

  _CacheEntry({
    required this.data,
    required this.signature,
    required this.timestamp,
  });

  Map<String, dynamic> toJson() => {
        'data': data,
        'signature': signature,
        'timestamp': timestamp,
      };

  factory _CacheEntry.fromJson(Map<String, dynamic> json) => _CacheEntry(
        data: json['data'] as String,
        signature: json['signature'] as String,
        timestamp: json['timestamp'] as int,
      );
}

/// Roles válidos conocidos por el sistema (previene la escalada de privilegios desde la caché).
const Set<String> _validRoles = {'admin', 'organizer', 'user', 'jury', 'moderator'};

/// Capa de caché offline-first con validación de integridad HMAC-SHA256.
///
/// Cada valor cacheado se firma con un secreto derivado del dispositivo para
/// que la manipulación del almacén local Hive se detecte al leer. También se
/// realiza validación a nivel de esquema para rechazar datos malformados o
/// con escalada de privilegios.
class OfflineCacheService {
  /// Singleton compartido del servicio.
  static final OfflineCacheService instance = OfflineCacheService._internal();
  OfflineCacheService._internal();

  static const String _secretKey = 'cache_hmac_secret';

  // Box names for cached API responses
  static const String _cacheBoxName = 'offline_cache';
  static const String _metaBoxName = 'cache_meta';

  late Box _cacheBox;
  late Box _metaBox;
  late String _hmacSecret;

  // ---------------------------------------------------------------------------
  // Initialisation
  // ---------------------------------------------------------------------------

  /// Inicializa el servicio: abre las cajas de Hive y carga o genera el secreto HMAC.
  Future<void> init() async {
    _cacheBox = await Hive.openBox(_cacheBoxName);
    _metaBox = await Hive.openBox(_metaBoxName);
    _hmacSecret = await _loadOrGenerateSecret();
  }

  Future<String> _loadOrGenerateSecret() async {
    final prefs = await SharedPreferences.getInstance();
    var secret = prefs.getString(_secretKey);
    if (secret == null || secret.length < 16) {
      secret = _generateSecret();
      await prefs.setString(_secretKey, secret);
    }
    return secret;
  }

  String _generateSecret() {
    final random = Random.secure();
    final bytes = List<int>.generate(32, (_) => random.nextInt(256));
    return base64Url.encode(bytes);
  }

  // ---------------------------------------------------------------------------
  // HMAC signing / verification
  // ---------------------------------------------------------------------------

  String _sign(String data) {
    final hmac = Hmac(sha256, utf8.encode(_hmacSecret));
    return base64Url.encode(hmac.convert(utf8.encode(data)).bytes);
  }

  bool _verify(String data, String signature) {
    final expected = _sign(data);
    // Constant-time comparison to prevent timing attacks.
    if (expected.length != signature.length) return false;
    int result = 0;
    for (int i = 0; i < expected.length; i++) {
      result |= expected.codeUnitAt(i) ^ signature.codeUnitAt(i);
    }
    return result == 0;
  }

  // ---------------------------------------------------------------------------
  // Schema / integrity validation
  // ---------------------------------------------------------------------------

  /// Valida que [json] cumpla el esquema esperado para [entityType].
  ///
  /// Devuelve `null` si es válido, o un mensaje de error si no lo es.
  String? _validateEntitySchema(String entityType, Map<String, dynamic> json) {
    if (json case {'id': int? id} when id != null && id < 0) {
      return 'Negative id';
    }

    switch (entityType) {
      case 'festival':
        if (json['name'] is! String) return 'Missing or invalid "name"';
        break;

      case 'user':
        if (json['username'] is! String) return 'Missing or invalid "username"';
        if (json['email'] is! String) return 'Missing or invalid "email"';
        if (json['role'] is String && !_validRoles.contains(json['role'])) {
          return 'Invalid role "${json['role']}" (privilege escalation)';
        }
        break;

      case 'shortfilm':
        if (json['title'] is! String) return 'Missing or invalid "title"';
        if (json['user_id'] is! int) return 'Missing or invalid "user_id"';
        break;

      case 'message':
        if (json['content'] is! String) return 'Missing or invalid "content"';
        if (json['sender_id'] is! int) return 'Missing or invalid "sender_id"';
        break;

      default:
        return 'Unknown entity type "$entityType"';
    }
    return null;
  }

  // ---------------------------------------------------------------------------
  // Public API
  // ---------------------------------------------------------------------------

  /// Cachea una respuesta de la API para [entityType].
  ///
  /// [data] se codifica en JSON, se firma con HMAC-SHA256 y se almacena en Hive.
  /// [entityType] es uno de `festival`, `user`, `shortfilm`, `message` o
  /// una clave compuesta como `festival_list`.
  Future<void> put(String entityType, dynamic data) async {
    final jsonStr = json.encode(data);
    final entry = _CacheEntry(
      data: jsonStr,
      signature: _sign(jsonStr),
      timestamp: DateTime.now().millisecondsSinceEpoch,
    );
    await _cacheBox.put(entityType, entry.toJson());
  }

  /// Lee los datos cacheados para [entityType].
  ///
  /// Devuelve los datos decodificados si la firma HMAC es válida y las comprobaciones
  /// de esquema pasan. Devuelve `null` si la caché falta, fue manipulada o es inválida.
  dynamic get(String entityType) {
    final raw = _cacheBox.get(entityType);
    if (raw == null) return null;

    final entry = _CacheEntry.fromJson(Map<String, dynamic>.from(raw));

    // Integrity check: HMAC must match.
    if (!_verify(entry.data, entry.signature)) {
      _cacheBox.delete(entityType);
      return null;
    }

    final decoded = json.decode(entry.data);

    // Schema validation for single entities.
    if (decoded is Map<String, dynamic>) {
      final error = _validateEntitySchema(entityType, decoded);
      if (error != null) {
        _cacheBox.delete(entityType);
        return null;
      }
    }

    // Schema validation for lists.
    if (decoded is List) {
      for (final item in decoded) {
        if (item is Map<String, dynamic>) {
          final error = _validateEntitySchema(entityType, item);
          if (error != null) {
            _cacheBox.delete(entityType);
            return null;
          }
        }
      }
    }

    return decoded;
  }

  /// Elimina una entrada de la caché.
  Future<void> remove(String entityType) async {
    await _cacheBox.delete(entityType);
  }

  /// Elimina todos los datos cacheados (p. ej., al cerrar sesión).
  Future<void> clear() async {
    await _cacheBox.clear();
    await _metaBox.clear();
  }

  /// Devuelve el timestamp (millis desde la época) en que [entityType] se cacheó,
  /// o `null` si no está presente.
  int? getTimestamp(String entityType) {
    final raw = _cacheBox.get(entityType);
    if (raw == null) return null;
    final entry = _CacheEntry.fromJson(Map<String, dynamic>.from(raw));
    return entry.timestamp;
  }

  /// Devuelve `true` si existe una entrada de caché válida para [entityType].
  bool has(String entityType) => get(entityType) != null;
}
