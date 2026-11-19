/// Nodo federado conocido por la app: dominio, URL base y capacidades.
///
/// Se persiste como JSON en SharedPreferences (clave `backend_nodes`) para que
/// sobreviva a los reinicios sin depender de code generation de Hive.
class NodeInfo {
  final String id;
  final String domain;
  final String baseUrl;
  final String? displayName;
  final List<String> capabilities;
  final bool trusted;
  final bool enabled;
  final DateTime? lastSeen;
  final bool isActive;

  const NodeInfo({
    required this.id,
    required this.domain,
    required this.baseUrl,
    this.displayName,
    this.capabilities = const [],
    this.trusted = false,
    this.enabled = true,
    this.lastSeen,
    this.isActive = false,
  });

  String get effectiveUrl => baseUrl.endsWith('/')
      ? baseUrl.substring(0, baseUrl.length - 1)
      : baseUrl;

  Map<String, dynamic> toJson() => {
        'id': id,
        'domain': domain,
        'baseUrl': effectiveUrl,
        'displayName': displayName,
        'capabilities': capabilities,
        'trusted': trusted,
        'enabled': enabled,
        'lastSeen': lastSeen?.toIso8601String(),
        'isActive': isActive,
      };

  factory NodeInfo.fromJson(Map<String, dynamic> json) => NodeInfo(
        id: json['id'] as String,
        domain: json['domain'] as String,
        baseUrl: json['baseUrl'] as String,
        displayName: json['displayName'] as String?,
        capabilities: (json['capabilities'] as List<dynamic>?)
            ?.cast<String>()
            .toList() ??
            const [],
        trusted: json['trusted'] as bool? ?? false,
        enabled: json['enabled'] as bool? ?? true,
        lastSeen: json['lastSeen'] != null
            ? DateTime.tryParse(json['lastSeen'] as String)
            : null,
        isActive: json['isActive'] as bool? ?? false,
      );
}
