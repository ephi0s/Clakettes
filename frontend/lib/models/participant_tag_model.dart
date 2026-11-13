/// Modelo de datos de una etiqueta de participante (p. ej. residente, estudiante).
///
/// Mapea entre el JSON snake_case del backend y los campos camelCase de Dart.
class ParticipantTag {
  final int? id;
  final String name;
  final String displayName;
  final String? description;
  final String category;
  final bool isGlobal;
  final bool isActive;
  final int sortOrder;
  final DateTime? createdAt;
  final DateTime? updatedAt;

  ParticipantTag({
    this.id,
    required this.name,
    required this.displayName,
    this.description,
    this.category = 'other',
    this.isGlobal = true,
    this.isActive = true,
    this.sortOrder = 0,
    this.createdAt,
    this.updatedAt,
  });

  /// Crea un [ParticipantTag] a partir de un mapa JSON (claves snake_case).
  factory ParticipantTag.fromJson(Map<String, dynamic> json) {
    return ParticipantTag(
      id: json['id'],
      name: json['name'],
      displayName: json['display_name'] ?? json['name'],
      description: json['description'],
      category: json['category'] ?? 'other',
      isGlobal: json['is_global'] ?? true,
      isActive: json['is_active'] ?? true,
      sortOrder: json['sort_order'] ?? 0,
      createdAt:
          json['created_at'] != null ? DateTime.parse(json['created_at']) : null,
      updatedAt:
          json['updated_at'] != null ? DateTime.parse(json['updated_at']) : null,
    );
  }
}

/// Etiqueta de participante asignada a un usuario, con su verificación.
class UserParticipantTag {
  final int? id;
  final int userId;
  final int tagId;
  final int? festivalId;
  final bool isPrimary;
  final int? assignedBy;
  final String? notes;
  final bool isHidden;
  /// Estado de verificación: `unverified`, `pending`, `verified` o `rejected`.
  final String verificationStatus;
  /// Método de verificación: `self_declared`, `document`, `external` u `other`.
  final String? verificationMethod;
  final String? verificationNotes;
  final String? verificationDocumentUrl;
  final DateTime? verificationRequestedAt;
  final int? verifiedBy;
  final DateTime? verifiedAt;
  final ParticipantTag? tag;

  UserParticipantTag({
    this.id,
    required this.userId,
    required this.tagId,
    this.festivalId,
    this.isPrimary = false,
    this.assignedBy,
    this.notes,
    this.isHidden = false,
    this.verificationStatus = 'unverified',
    this.verificationMethod,
    this.verificationNotes,
    this.verificationDocumentUrl,
    this.verificationRequestedAt,
    this.verifiedBy,
    this.verifiedAt,
    this.tag,
  });

  /// Crea un [UserParticipantTag] a partir de un mapa JSON (claves snake_case).
  factory UserParticipantTag.fromJson(Map<String, dynamic> json) {
    final rawTag = json['tag'];
    return UserParticipantTag(
      id: json['id'],
      userId: json['user_id'],
      tagId: json['tag_id'],
      festivalId: json['festival_id'],
      isPrimary: json['is_primary'] ?? false,
      assignedBy: json['assigned_by'],
      notes: json['notes'],
      isHidden: json['is_hidden'] ?? false,
      verificationStatus: json['verification_status'] ?? 'unverified',
      verificationMethod: json['verification_method'],
      verificationNotes: json['verification_notes'],
      verificationDocumentUrl: json['verification_document_url'],
      verificationRequestedAt: json['verification_requested_at'] != null
          ? DateTime.parse(json['verification_requested_at'])
          : null,
      verifiedBy: json['verified_by'],
      verifiedAt: json['verified_at'] != null
          ? DateTime.parse(json['verified_at'])
          : null,
      tag: rawTag is Map
          ? ParticipantTag.fromJson(Map<String, dynamic>.from(rawTag))
          : null,
    );
  }

  bool get isVerified => verificationStatus == 'verified';
  bool get isPending => verificationStatus == 'pending';
  bool get isRejected => verificationStatus == 'rejected';

  String get label => tag?.displayName ?? tag?.name ?? '$tagId';
}
