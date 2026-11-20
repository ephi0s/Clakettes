/// Modelos de datos del Clakettes Schema v1 para federación.
library;

class Festival {
  final String id;
  final String name;
  final String? edition;
  final DateTime createdAt;
  final String ownerNode;

  Festival({
    required this.id,
    required this.name,
    this.edition,
    required this.createdAt,
    required this.ownerNode,
  });

  factory Festival.fromJson(Map<String, dynamic> j) => Festival(
        id: j['id'] as String,
        name: j['name'] as String,
        edition: j['edition'] as String?,
        createdAt: DateTime.parse(j['created_at'] as String),
        ownerNode: j['owner_node'] as String,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'edition': edition,
        'created_at': createdAt.toIso8601String(),
        'owner_node': ownerNode,
      };
}

class User {
  final String id;
  final String? uuid;
  final String? did;
  final String? handle;
  final String username;
  final String nodeOrigin;

  User({
    required this.id,
    this.uuid,
    this.did,
    this.handle,
    required this.username,
    required this.nodeOrigin,
  });

  factory User.fromJson(Map<String, dynamic> j) => User(
        id: j['id'] as String,
        uuid: j['uuid'] as String?,
        did: j['did'] as String?,
        handle: j['handle'] as String?,
        username: j['username'] as String,
        nodeOrigin: j['node_origin'] as String,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'uuid': uuid,
        'did': did,
        'handle': handle,
        'username': username,
        'node_origin': nodeOrigin,
      };
}

class Message {
  final String id;
  final String sender;
  final String? recipient;
  final String body;
  final DateTime createdAt;
  final String nodeOrigin;

  Message({
    required this.id,
    required this.sender,
    this.recipient,
    required this.body,
    required this.createdAt,
    required this.nodeOrigin,
  });

  factory Message.fromJson(Map<String, dynamic> j) => Message(
        id: j['id'] as String,
        sender: j['sender'] as String,
        recipient: j['recipient'] as String?,
        body: j['body'] as String,
        createdAt: DateTime.parse(j['created_at'] as String),
        nodeOrigin: j['node_origin'] as String,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'sender': sender,
        'recipient': recipient,
        'body': body,
        'created_at': createdAt.toIso8601String(),
        'node_origin': nodeOrigin,
      };
}

class ModerationReport {
  final String? id;
  final String reporterNode;
  final String targetNode;
  final String? targetUserRef;
  final String reason;
  final String status;

  ModerationReport({
    this.id,
    required this.reporterNode,
    required this.targetNode,
    this.targetUserRef,
    required this.reason,
    this.status = 'pending',
  });

  factory ModerationReport.fromJson(Map<String, dynamic> j) => ModerationReport(
        id: j['id'] as String?,
        reporterNode: j['reporter_node'] as String,
        targetNode: j['target_node'] as String,
        targetUserRef: j['target_user_ref'] as String?,
        reason: j['reason'] as String,
        status: j['status'] as String? ?? 'pending',
      );

  Map<String, dynamic> toJson() => {
        if (id != null) 'id': id,
        'reporter_node': reporterNode,
        'target_node': targetNode,
        'target_user_ref': targetUserRef,
        'reason': reason,
        'status': status,
      };
}

class Manifest {
  final String schemaVersion;
  final String node;
  final String version;
  final List<String> capabilities;
  final DateTime? issuedAt;
  final DateTime? expiresAt;
  final String? signature;
  final List<String> certificateChain;

  Manifest({
    this.schemaVersion = '1',
    required this.node,
    this.version = '1.0.0',
    this.capabilities = const [],
    this.issuedAt,
    this.expiresAt,
    this.signature,
    this.certificateChain = const [],
  });

  factory Manifest.fromJson(Map<String, dynamic> j) => Manifest(
        schemaVersion: j['schema_version'] as String? ?? '1',
        node: j['node'] as String,
        version: j['version'] as String? ?? '1.0.0',
        capabilities: (j['capabilities'] as List? ?? const [])
            .cast<String>()
            .toList(),
        issuedAt: j['issued_at'] != null
            ? DateTime.parse(j['issued_at'] as String)
            : null,
        expiresAt: j['expires_at'] != null
            ? DateTime.parse(j['expires_at'] as String)
            : null,
        signature: j['signature'] as String?,
        certificateChain: (j['certificate_chain'] as List? ?? const [])
            .cast<String>()
            .toList(),
      );

  Map<String, dynamic> toJson() => {
        'schema_version': schemaVersion,
        'node': node,
        'version': version,
        'capabilities': capabilities,
        'issued_at': issuedAt?.toIso8601String(),
        'expires_at': expiresAt?.toIso8601String(),
        'signature': signature,
        'certificate_chain': certificateChain,
      };
}

class PeerInfo {
  final String domain;
  final String schemaVersion;
  final String status;
  final String version;
  final String? lastSeen;
  final String? certFingerprintSha256;
  final List<String> capabilities;
  final bool consentRequired;
  final bool minimizeData;

  PeerInfo({
    required this.domain,
    this.schemaVersion = '1',
    this.status = 'unknown',
    this.version = '1.0.0',
    this.lastSeen,
    this.certFingerprintSha256,
    this.capabilities = const [],
    this.consentRequired = true,
    this.minimizeData = true,
  });

  factory PeerInfo.fromJson(Map<String, dynamic> j) => PeerInfo(
        domain: j['domain'] as String,
        schemaVersion: j['schema_version'] as String? ?? '1',
        status: j['status'] as String? ?? 'unknown',
        version: j['version'] as String? ?? '1.0.0',
        lastSeen: j['last_seen'] as String?,
        certFingerprintSha256: j['cert_fingerprint_sha256'] as String?,
        capabilities: (j['capabilities'] as List? ?? const [])
            .cast<String>()
            .toList(),
        consentRequired: j['consent_required'] as bool? ?? true,
        minimizeData: j['minimize_data'] as bool? ?? true,
      );

  Map<String, dynamic> toJson() => {
        'domain': domain,
        'schema_version': schemaVersion,
        'status': status,
        'version': version,
        'last_seen': lastSeen,
        'cert_fingerprint_sha256': certFingerprintSha256,
        'capabilities': capabilities,
        'consent_required': consentRequired,
        'minimize_data': minimizeData,
      };
}

class TokenResponse {
  final String accessToken;
  final String tokenType;
  final int expiresIn;

  TokenResponse({
    required this.accessToken,
    this.tokenType = 'Bearer',
    this.expiresIn = 3600,
  });

  factory TokenResponse.fromJson(Map<String, dynamic> j) => TokenResponse(
        accessToken: j['access_token'] as String,
        tokenType: j['token_type'] as String? ?? 'Bearer',
        expiresIn: j['expires_in'] as int? ?? 3600,
      );
}

class VerifyResponse {
  final bool trusted;
  final String? domain;
  final String? fingerprint;
  final String? reason;

  VerifyResponse({
    required this.trusted,
    this.domain,
    this.fingerprint,
    this.reason,
  });

  factory VerifyResponse.fromJson(Map<String, dynamic> j) => VerifyResponse(
        trusted: j['trusted'] as bool,
        domain: j['domain'] as String?,
        fingerprint: j['fingerprint'] as String?,
        reason: j['reason'] as String?,
      );
}

class WebFingerResponse {
  final String subject;
  final List<Map<String, dynamic>> links;

  WebFingerResponse({
    required this.subject,
    this.links = const [],
  });

  factory WebFingerResponse.fromJson(Map<String, dynamic> j) => WebFingerResponse(
        subject: j['subject'] as String,
        links: (j['links'] as List? ?? const [])
            .cast<Map<String, dynamic>>()
            .toList(),
      );
}

class RevokeResponse {
  final String domain;
  final bool revoked;

  RevokeResponse({
    required this.domain,
    required this.revoked,
  });

  factory RevokeResponse.fromJson(Map<String, dynamic> j) => RevokeResponse(
        domain: j['domain'] as String,
        revoked: j['revoked'] as bool,
      );
}
