import 'package:hive/hive.dart';

part 'registration_form_model.g.dart';

/// Modelo de datos de un formulario de inscripción a un festival y sus secciones.
///
/// Mapea entre el JSON snake_case del backend y los campos camelCase de Dart.
@HiveType(typeId: 12)
class RegistrationForm {
  @HiveField(0)
  final int? id;
  @HiveField(1)
  final int festivalId;
  @HiveField(2)
  final String title;
  @HiveField(3)
  final String? description;
  @HiveField(4)
  final bool isActive;
  /// Indica si solo pueden inscribirse cuentas ya existentes.
  @HiveField(5)
  final bool requireExistingAccount;
  @HiveField(6)
  final DateTime? startsAt;
  @HiveField(7)
  final DateTime? endsAt;
  @HiveField(8)
  final int? maxRegistrations;
  /// Indica si los solicitantes pueden elegir su propio rol.
  @HiveField(9)
  final bool allowRoleSelection;
  /// Indica si los solicitantes pueden elegir sus propias etiquetas.
  @HiveField(10)
  final bool allowTagSelection;
  @HiveField(11)
  final List<RegistrationFormSection> sections;
  @HiveField(12)
  final DateTime? createdAt;
  /// Cuota de inscripción en la divisa indicada por [currency]; `null` significa sin cuota.
  @HiveField(13)
  final double? feeAmount;
  /// Divisa de la cuota (código ISO 4217 de 3 letras, p. ej. ``EUR``).
  @HiveField(14)
  final String currency;

  RegistrationForm({
    this.id,
    required this.festivalId,
    required this.title,
    this.description,
    this.isActive = true,
    this.requireExistingAccount = true,
    this.startsAt,
    this.endsAt,
    this.maxRegistrations,
    this.allowRoleSelection = true,
    this.allowTagSelection = true,
    this.sections = const [],
    this.createdAt,
    this.feeAmount,
    this.currency = 'EUR',
  });

  /// Crea un [RegistrationForm] a partir de un mapa JSON (claves snake_case del backend).
  factory RegistrationForm.fromJson(Map<String, dynamic> json) {
    return RegistrationForm(
      id: json['id'],
      festivalId: json['festival_id'],
      title: json['title'],
      description: json['description'],
      isActive: json['is_active'] ?? true,
      requireExistingAccount: json['require_existing_account'] ?? true,
      startsAt: json['starts_at'] != null ? DateTime.parse(json['starts_at']) : null,
      endsAt: json['ends_at'] != null ? DateTime.parse(json['ends_at']) : null,
      maxRegistrations: json['max_registrations'],
      allowRoleSelection: json['allow_role_selection'] ?? true,
      allowTagSelection: json['allow_tag_selection'] ?? true,
      sections: json['sections'] != null
          ? (json['sections'] as List).map((s) => RegistrationFormSection.fromJson(s)).toList()
          : [],
      createdAt: json['created_at'] != null ? DateTime.parse(json['created_at']) : null,
      feeAmount: (json['fee_amount'] as num?)?.toDouble(),
      currency: json['currency'] ?? 'EUR',
    );
  }

  /// Serializa este [RegistrationForm] a un mapa JSON (claves snake_case).
  Map<String, dynamic> toJson() => {
    'festival_id': festivalId,
    'title': title,
    'description': description,
    'is_active': isActive,
    'require_existing_account': requireExistingAccount,
    'starts_at': startsAt?.toIso8601String(),
    'ends_at': endsAt?.toIso8601String(),
    'max_registrations': maxRegistrations,
    'allow_role_selection': allowRoleSelection,
    'allow_tag_selection': allowTagSelection,
    'fee_amount': feeAmount,
    'currency': currency,
  };
}


/// Modelo de datos de una sección de un [RegistrationForm].
///
/// Mapea entre el JSON snake_case del backend y los campos camelCase de Dart.
@HiveType(typeId: 13)
class RegistrationFormSection {
  @HiveField(0)
  final int? id;
  @HiveField(1)
  final int formId;
  @HiveField(2)
  final String title;
  @HiveField(3)
  final String? description;
  @HiveField(4)
  final int sortOrder;
  /// Indica si se puede seleccionar más de un rol en esta sección.
  @HiveField(5)
  final bool allowMultipleRoles;
  @HiveField(6)
  final int? maxSelections;
  @HiveField(7)
  final bool isRequired;
  /// IDs de rol ofrecidos en esta sección (aplanados desde ``role_assignments``).
  @HiveField(8)
  final List<int> roleIds;
  /// IDs de etiqueta ofrecidos en esta sección (aplanados desde ``tag_assignments``).
  @HiveField(9)
  final List<int> tagIds;

  RegistrationFormSection({
    this.id,
    required this.formId,
    required this.title,
    this.description,
    this.sortOrder = 0,
    this.allowMultipleRoles = false,
    this.maxSelections,
    this.isRequired = true,
    this.roleIds = const [],
    this.tagIds = const [],
  });

  /// Crea un [RegistrationFormSection] a partir de un mapa JSON (claves snake_case del backend).
  factory RegistrationFormSection.fromJson(Map<String, dynamic> json) {
    return RegistrationFormSection(
      id: json['id'],
      formId: json['form_id'],
      title: json['title'],
      description: json['description'],
      sortOrder: json['sort_order'] ?? 0,
      allowMultipleRoles: json['allow_multiple_roles'] ?? false,
      maxSelections: json['max_selections'],
      isRequired: json['is_required'] ?? false,
      roleIds: (json['role_assignments'] as List?)
              ?.map((r) => r['role_id'] as int).toList() ??
          [],
      tagIds: (json['tag_assignments'] as List?)
              ?.map((t) => t['tag_id'] as int).toList() ??
          [],
    );
  }

  /// Serializa este [RegistrationFormSection] a un mapa JSON (claves snake_case).
  Map<String, dynamic> toJson() => {
    'form_id': formId,
    'title': title,
    'description': description,
    'sort_order': sortOrder,
    'allow_multiple_roles': allowMultipleRoles,
    'max_selections': maxSelections,
    'is_required': isRequired,
    'role_ids': roleIds,
    'tag_ids': tagIds,
  };
}


/// Modelo de datos de la solicitud de un usuario a un festival mediante un formulario de inscripción.
///
/// Mapea entre el JSON snake_case del backend y los campos camelCase de Dart.
/// El objeto anidado ``user`` del backend se aplana en [userName] y [userEmail].
@HiveType(typeId: 14)
class FestivalRegistration {
  @HiveField(0)
  final int? id;
  @HiveField(1)
  final int formId;
  @HiveField(2)
  final int userId;
  @HiveField(3)
  final int? festivalId;
  /// Estado de la solicitud, p. ej. ``pending``, ``approved`` o ``rejected``.
  @HiveField(4)
  final String status;
  @HiveField(5)
  final int? assignedBy;
  @HiveField(6)
  final int? approvedBy;
  @HiveField(7)
  final String? notes;
  @HiveField(8)
  final String? userName;
  @HiveField(9)
  final String? userEmail;
  /// Estado de pago: ``unpaid``, ``pending``, ``paid``, ``refunded`` o ``cancelled``.
  @HiveField(10)
  final String? paymentStatus;
  @HiveField(11)
  final DateTime? paidAt;
  @HiveField(12)
  final String? paymentMethod;
  @HiveField(13)
  final String? transactionId;

  FestivalRegistration({
    this.id,
    required this.formId,
    required this.userId,
    this.festivalId,
    this.status = 'pending',
    this.assignedBy,
    this.approvedBy,
    this.notes,
    this.userName,
    this.userEmail,
    this.paymentStatus,
    this.paidAt,
    this.paymentMethod,
    this.transactionId,
  });

  /// Crea un [FestivalRegistration] a partir de un mapa JSON (claves snake_case del backend).
  factory FestivalRegistration.fromJson(Map<String, dynamic> json) {
    return FestivalRegistration(
      id: json['id'],
      formId: json['form_id'],
      userId: json['user_id'],
      festivalId: json['festival_id'],
      status: json['status'] ?? 'pending',
      assignedBy: json['assigned_by'],
      approvedBy: json['approved_by'],
      notes: json['notes'],
      userName: json['user']?['full_name'] ?? json['user']?['username'],
      userEmail: json['user']?['email'],
      paymentStatus: json['payment_status'],
      paidAt: json['paid_at'] != null ? DateTime.parse(json['paid_at']) : null,
      paymentMethod: json['payment_method'],
      transactionId: json['transaction_id'],
    );
  }

  /// Serializa este [FestivalRegistration] a un mapa JSON (claves snake_case).
  Map<String, dynamic> toJson() => {
    'form_id': formId,
    'user_id': userId,
    'festival_id': festivalId,
    'status': status,
    'notes': notes,
    if (paymentStatus != null) 'payment_status': paymentStatus,
    if (paidAt != null) 'paid_at': paidAt!.toIso8601String(),
    if (paymentMethod != null) 'payment_method': paymentMethod,
    if (transactionId != null) 'transaction_id': transactionId,
  };
}


/// Modelo de datos de un enlace compartible a un [RegistrationForm].
///
/// Mapea entre el JSON snake_case del backend y los campos camelCase de Dart.
@HiveType(typeId: 26)
class RegistrationFormLink {
  @HiveField(0)
  final int? id;
  @HiveField(1)
  final int formId;
  /// Token opaco incluido en la URL compartible.
  @HiveField(2)
  final String token;
  /// Indica si el enlace es de un solo uso (una inscripción por enlace).
  @HiveField(3)
  final bool isUnique;
  @HiveField(4)
  final bool isPublic;
  @HiveField(5)
  final bool isActive;
  @HiveField(6)
  final DateTime? expiresAt;
  @HiveField(7)
  final int? maxUses;
  @HiveField(8)
  final int useCount;
  @HiveField(9)
  final int? assignedUserId;
  @HiveField(10)
  final String? notes;
  @HiveField(11)
  final DateTime? createdAt;

  RegistrationFormLink({
    this.id,
    required this.formId,
    required this.token,
    this.isUnique = false,
    this.isPublic = true,
    this.isActive = true,
    this.expiresAt,
    this.maxUses,
    this.useCount = 0,
    this.assignedUserId,
    this.notes,
    this.createdAt,
  });

  /// Crea un [RegistrationFormLink] a partir de un mapa JSON (claves snake_case del backend).
  factory RegistrationFormLink.fromJson(Map<String, dynamic> json) {
    return RegistrationFormLink(
      id: json['id'],
      formId: json['form_id'],
      token: json['token'],
      isUnique: json['is_unique'] ?? false,
      isPublic: json['is_public'] ?? true,
      isActive: json['is_active'] ?? true,
      expiresAt: json['expires_at'] != null ? DateTime.parse(json['expires_at']) : null,
      maxUses: json['max_uses'],
      useCount: json['use_count'] ?? 0,
      assignedUserId: json['assigned_user_id'],
      notes: json['notes'],
      createdAt: json['created_at'] != null ? DateTime.parse(json['created_at']) : null,
    );
  }

  /// Serializa este [RegistrationFormLink] a un mapa JSON (claves snake_case).
  Map<String, dynamic> toJson() => {
    'form_id': formId,
    'is_unique': isUnique,
    'is_public': isPublic,
    'expires_at': expiresAt?.toIso8601String(),
    'max_uses': maxUses,
    'assigned_user_id': assignedUserId,
    'notes': notes,
  };
}
