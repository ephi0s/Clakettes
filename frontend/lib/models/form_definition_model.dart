import 'package:hive/hive.dart';

part 'form_definition_model.g.dart';

/// Valores permitidos para [FormDefinition.formType] como constantes de tipo string.
class FormType {
  static const userCreation = 'user_creation';
  static const festivalRegistration = 'festival_registration';
  static const internal = 'internal';
  final String value;
  const FormType(this.value);
}

/// Valores permitidos para [FormField.fieldType] como constantes de tipo string.
class FormFieldType {
  static const string = 'string';
  static const email = 'email';
  static const phone = 'phone';
  static const url = 'url';
  static const date = 'date';
  static const number = 'number';
  static const boolean = 'boolean';
  static const select = 'select';
  static const multiselect = 'multiselect';
  static const file = 'file';
  static const alias = 'alias';
  static const roleSelector = 'roleSelector';
  static const tagSelector = 'tagSelector';
  static const sectionBreak = 'sectionBreak';
  static const staticText = 'staticText';
  final String value;
  const FormFieldType(this.value);
}

/// Valores permitidos para [FormAccessRule.accessLevel] como constantes de tipo string.
class FormAccessLevel {
  static const view = 'view';
  static const submit = 'submit';
  static const manage = 'manage';
  final String value;
  const FormAccessLevel(this.value);
}

/// Valores permitidos para [FormResponse.status] como constantes de tipo string.
class SubmissionStatus {
  static const draft = 'draft';
  static const submitted = 'submitted';
  static const approved = 'approved';
  static const rejected = 'rejected';
  final String value;
  const SubmissionStatus(this.value);
}

/// Modelo de datos de una opción seleccionable de un [FormField].
///
/// Mapea entre el JSON snake_case del backend y los campos camelCase de Dart.
@HiveType(typeId: 31)
class FormFieldOption {
  @HiveField(0)
  final int? id;
  @HiveField(1)
  final String value;
  @HiveField(2)
  final String label;
  @HiveField(3)
  final int sortOrder;
  @HiveField(4)
  final DateTime? createdAt;
  @HiveField(5)
  final DateTime? updatedAt;

  FormFieldOption({
    this.id,
    required this.value,
    required this.label,
    this.sortOrder = 0,
    this.createdAt,
    this.updatedAt,
  });

  /// Crea un [FormFieldOption] a partir de un mapa JSON (claves snake_case del backend).
  factory FormFieldOption.fromJson(Map<String, dynamic> json) {
    return FormFieldOption(
      id: json['id'],
      value: json['value'],
      label: json['label'],
      sortOrder: json['sort_order'] ?? 0,
      createdAt: json['created_at'] != null ? DateTime.parse(json['created_at']) : null,
      updatedAt: json['updated_at'] != null ? DateTime.parse(json['updated_at']) : null,
    );
  }

  /// Serializa este [FormFieldOption] a un mapa JSON (claves snake_case).
  Map<String, dynamic> toJson() => {
    'value': value,
    'label': label,
    'sort_order': sortOrder,
  };
}

/// Modelo de datos de un campo de entrada dentro de una página de formulario.
///
/// Mapea entre el JSON snake_case del backend y los campos camelCase de Dart.
@HiveType(typeId: 32)
class FormField {
  @HiveField(0)
  final int? id;
  @HiveField(1)
  final int pageId;
  /// Tipo de entrada; ver [FormFieldType].
  @HiveField(2)
  final String fieldType;
  @HiveField(3)
  final String label;
  @HiveField(4)
  final String? helpText;
  @HiveField(5)
  final String? placeholder;
  @HiveField(6)
  final bool isRequired;
  @HiveField(7)
  final bool isVisible;
  @HiveField(8)
  final bool isReadOnly;
  @HiveField(9)
  final int sortOrder;
  @HiveField(10)
  final String? defaultValue;
  @HiveField(11)
  final int? minLength;
  @HiveField(12)
  final int? maxLength;
  @HiveField(13)
  final num? minValue;
  @HiveField(14)
  final num? maxValue;
  /// Patrón de expresión regular aplicado al valor del campo para su validación.
  @HiveField(15)
  final String? regexPattern;
  /// Mensaje personalizado que se muestra cuando falla la validación.
  @HiveField(16)
  final String? errorMessage;
  /// Conjunto fijo de valores permitidos para campos tipo select.
  @HiveField(17)
  final List<String>? allowedValues;
  /// ID del campo del que depende este para su visualización condicional.
  @HiveField(18)
  final int? dependsOnFieldId;
  /// Valor de [dependsOnFieldId] requerido para mostrar este campo.
  @HiveField(19)
  final String? dependsOnValue;
  /// IDs de rol con permiso para ver o rellenar este campo.
  @HiveField(20)
  final List<int>? roleFilter;
  /// Configuración adicional específica del backend para este campo.
  @HiveField(21)
  final Map<String, dynamic>? settings;
  /// Clase de ancho del diseño responsive (p. ej. ``full`` o ``half``).
  @HiveField(22)
  final String? widthClass;
  @HiveField(23)
  final List<FormFieldOption> options;
  @HiveField(24)
  final DateTime? createdAt;
  @HiveField(25)
  final DateTime? updatedAt;

  FormField({
    this.id,
    required this.pageId,
    required this.fieldType,
    required this.label,
    this.helpText,
    this.placeholder,
    this.isRequired = false,
    this.isVisible = true,
    this.isReadOnly = false,
    this.sortOrder = 0,
    this.defaultValue,
    this.minLength,
    this.maxLength,
    this.minValue,
    this.maxValue,
    this.regexPattern,
    this.errorMessage,
    this.allowedValues,
    this.dependsOnFieldId,
    this.dependsOnValue,
    this.roleFilter,
    this.settings,
    this.widthClass,
    this.options = const [],
    this.createdAt,
    this.updatedAt,
  });

  /// Crea un [FormField] a partir de un mapa JSON (claves snake_case del backend).
  factory FormField.fromJson(Map<String, dynamic> json) {
    return FormField(
      id: json['id'],
      pageId: json['page_id'],
      fieldType: json['field_type'],
      label: json['label'],
      helpText: json['help_text'],
      placeholder: json['placeholder'],
      isRequired: json['is_required'] ?? false,
      isVisible: json['is_visible'] ?? true,
      isReadOnly: json['is_read_only'] ?? false,
      sortOrder: json['sort_order'] ?? 0,
      defaultValue: json['default_value'],
      minLength: json['min_length'],
      maxLength: json['max_length'],
      minValue: json['min_value'],
      maxValue: json['max_value'],
      regexPattern: json['regex_pattern'],
      errorMessage: json['error_message'],
      allowedValues: json['allowed_values'] != null
          ? (json['allowed_values'] as List).cast<String>()
          : null,
      dependsOnFieldId: json['depends_on_field_id'],
      dependsOnValue: json['depends_on_value'],
      roleFilter: json['role_filter'] != null
          ? (json['role_filter'] as List).cast<int>()
          : null,
      settings: json['settings'] as Map<String, dynamic>?,
      widthClass: json['width_class'],
      options: json['options'] != null
          ? (json['options'] as List).map((o) => FormFieldOption.fromJson(o)).toList()
          : [],
      createdAt: json['created_at'] != null ? DateTime.parse(json['created_at']) : null,
      updatedAt: json['updated_at'] != null ? DateTime.parse(json['updated_at']) : null,
    );
  }

  /// Serializa este [FormField] a un mapa JSON (claves snake_case).
  Map<String, dynamic> toJson() => {
    'page_id': pageId,
    'field_type': fieldType,
    'label': label,
    'help_text': helpText,
    'placeholder': placeholder,
    'is_required': isRequired,
    'is_visible': isVisible,
    'is_read_only': isReadOnly,
    'sort_order': sortOrder,
    'default_value': defaultValue,
    'min_length': minLength,
    'max_length': maxLength,
    'min_value': minValue,
    'max_value': maxValue,
    'regex_pattern': regexPattern,
    'error_message': errorMessage,
    'allowed_values': allowedValues,
    'depends_on_field_id': dependsOnFieldId,
    'depends_on_value': dependsOnValue,
    'role_filter': roleFilter,
    'settings': settings,
    'width_class': widthClass,
    'options': options.map((o) => o.toJson()).toList(),
  };
}

/// Modelo de datos de una página (sección) de un [FormDefinition].
///
/// Mapea entre el JSON snake_case del backend y los campos camelCase de Dart.
@HiveType(typeId: 33)
class FormPage {
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
  /// Indica si la página puede rellenarse varias veces.
  @HiveField(5)
  final bool isRepeatable;
  @HiveField(6)
  final List<FormField> fields;
  @HiveField(7)
  final DateTime? createdAt;
  @HiveField(8)
  final DateTime? updatedAt;

  FormPage({
    this.id,
    required this.formId,
    required this.title,
    this.description,
    this.sortOrder = 0,
    this.isRepeatable = false,
    this.fields = const [],
    this.createdAt,
    this.updatedAt,
  });

  /// Crea un [FormPage] a partir de un mapa JSON (claves snake_case del backend).
  factory FormPage.fromJson(Map<String, dynamic> json) {
    return FormPage(
      id: json['id'],
      formId: json['form_id'],
      title: json['title'],
      description: json['description'],
      sortOrder: json['sort_order'] ?? 0,
      isRepeatable: json['is_repeatable'] ?? false,
      fields: json['fields'] != null
          ? (json['fields'] as List).map((f) => FormField.fromJson(f)).toList()
          : [],
      createdAt: json['created_at'] != null ? DateTime.parse(json['created_at']) : null,
      updatedAt: json['updated_at'] != null ? DateTime.parse(json['updated_at']) : null,
    );
  }

  /// Serializa este [FormPage] a un mapa JSON (claves snake_case).
  Map<String, dynamic> toJson() => {
    'title': title,
    'description': description,
    'sort_order': sortOrder,
    'is_repeatable': isRepeatable,
    'fields': fields.map((f) => f.toJson()).toList(),
  };
}

/// Modelo de datos de una definición de formulario dinámico reutilizable.
///
/// Mapea entre el JSON snake_case del backend y los campos camelCase de Dart.
@HiveType(typeId: 34)
class FormDefinition {
  @HiveField(0)
  final int? id;
  @HiveField(1)
  final String title;
  @HiveField(2)
  final String? description;
  /// Finalidad del formulario; ver [FormType].
  @HiveField(3)
  final String formType;
  @HiveField(4)
  final int? festivalId;
  @HiveField(5)
  final bool isActive;
  @HiveField(6)
  final bool isPublic;
  @HiveField(7)
  final DateTime? startsAt;
  @HiveField(8)
  final DateTime? endsAt;
  /// Número máximo de envíos aceptados.
  @HiveField(9)
  final int? maxSubmissions;
  /// Indica si el formulario requiere un usuario autenticado.
  @HiveField(10)
  final bool requireAuth;
  /// Indica si los envíos necesitan la aprobación del personal.
  @HiveField(11)
  final bool requiresApproval;
  @HiveField(12)
  final String? successMessage;
  @HiveField(13)
  final String? submitButtonText;
  @HiveField(14)
  final int? createdBy;
  /// Configuración adicional específica del backend para el formulario.
  @HiveField(15)
  final Map<String, dynamic>? settings;
  @HiveField(16)
  final int sortOrder;
  @HiveField(17)
  final List<FormPage> pages;
  @HiveField(18)
  final DateTime? createdAt;
  @HiveField(19)
  final DateTime? updatedAt;

  FormDefinition({
    this.id,
    required this.title,
    this.description,
    required this.formType,
    this.festivalId,
    this.isActive = true,
    this.isPublic = true,
    this.startsAt,
    this.endsAt,
    this.maxSubmissions,
    this.requireAuth = false,
    this.requiresApproval = false,
    this.successMessage,
    this.submitButtonText,
    this.createdBy,
    this.settings,
    this.sortOrder = 0,
    this.pages = const [],
    this.createdAt,
    this.updatedAt,
  });

  /// Crea un [FormDefinition] a partir de un mapa JSON (claves snake_case del backend).
  factory FormDefinition.fromJson(Map<String, dynamic> json) {
    return FormDefinition(
      id: json['id'],
      title: json['title'],
      description: json['description'],
      formType: json['form_type'],
      festivalId: json['festival_id'],
      isActive: json['is_active'] ?? true,
      isPublic: json['is_public'] ?? true,
      startsAt: json['starts_at'] != null ? DateTime.parse(json['starts_at']) : null,
      endsAt: json['ends_at'] != null ? DateTime.parse(json['ends_at']) : null,
      maxSubmissions: json['max_submissions'],
      requireAuth: json['require_auth'] ?? false,
      requiresApproval: json['requires_approval'] ?? false,
      successMessage: json['success_message'],
      submitButtonText: json['submit_button_text'],
      createdBy: json['created_by'],
      settings: json['settings'] as Map<String, dynamic>?,
      sortOrder: json['sort_order'] ?? 0,
      pages: json['pages'] != null
          ? (json['pages'] as List).map((p) => FormPage.fromJson(p)).toList()
          : [],
      createdAt: json['created_at'] != null ? DateTime.parse(json['created_at']) : null,
      updatedAt: json['updated_at'] != null ? DateTime.parse(json['updated_at']) : null,
    );
  }

  /// Serializa este [FormDefinition] a un mapa JSON (claves snake_case).
  Map<String, dynamic> toJson() => {
    'title': title,
    'description': description,
    'form_type': formType,
    'festival_id': festivalId,
    'is_active': isActive,
    'is_public': isPublic,
    'starts_at': startsAt?.toIso8601String(),
    'ends_at': endsAt?.toIso8601String(),
    'max_submissions': maxSubmissions,
    'require_auth': requireAuth,
    'requires_approval': requiresApproval,
    'success_message': successMessage,
    'submit_button_text': submitButtonText,
    'settings': settings,
    'sort_order': sortOrder,
    'pages': pages.map((p) => p.toJson()).toList(),
  };
}

/// Modelo de datos de un enlace compartible a un [FormDefinition].
///
/// Mapea entre el JSON snake_case del backend y los campos camelCase de Dart.
@HiveType(typeId: 35)
class FormLink {
  @HiveField(0)
  final int? id;
  @HiveField(1)
  final int formId;
  /// Token opaco incluido en la URL compartible.
  @HiveField(2)
  final String token;
  /// Indica si el enlace es de un solo uso (un envío por enlace).
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
  @HiveField(12)
  final DateTime? updatedAt;

  FormLink({
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
    this.updatedAt,
  });

  /// Crea un [FormLink] a partir de un mapa JSON (claves snake_case del backend).
  factory FormLink.fromJson(Map<String, dynamic> json) {
    return FormLink(
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
      updatedAt: json['updated_at'] != null ? DateTime.parse(json['updated_at']) : null,
    );
  }

  /// Serializa este [FormLink] a un mapa JSON (claves snake_case).
  Map<String, dynamic> toJson() => {
    'is_unique': isUnique,
    'is_public': isPublic,
    'expires_at': expiresAt?.toIso8601String(),
    'max_uses': maxUses,
    'assigned_user_id': assignedUserId,
    'notes': notes,
  };
}

/// Modelo de datos del valor enviado de un [FormField] individual.
///
/// Mapea entre el JSON snake_case del backend y los campos camelCase de Dart.
@HiveType(typeId: 36)
class FormFieldResponse {
  @HiveField(0)
  final int? id;
  @HiveField(1)
  final int responseId;
  @HiveField(2)
  final int fieldId;
  /// Valor enviado; el tipo depende del tipo de campo (string, number, list, ...).
  @HiveField(3)
  final dynamic value;
  /// URL del archivo subido para los campos ``file``.
  @HiveField(4)
  final String? fileUrl;
  @HiveField(5)
  final DateTime? createdAt;
  @HiveField(6)
  final DateTime? updatedAt;

  FormFieldResponse({
    this.id,
    required this.responseId,
    required this.fieldId,
    this.value,
    this.fileUrl,
    this.createdAt,
    this.updatedAt,
  });

  /// Crea un [FormFieldResponse] a partir de un mapa JSON (claves snake_case del backend).
  factory FormFieldResponse.fromJson(Map<String, dynamic> json) {
    return FormFieldResponse(
      id: json['id'],
      responseId: json['response_id'],
      fieldId: json['field_id'],
      value: json['value'],
      fileUrl: json['file_url'],
      createdAt: json['created_at'] != null ? DateTime.parse(json['created_at']) : null,
      updatedAt: json['updated_at'] != null ? DateTime.parse(json['updated_at']) : null,
    );
  }

  /// Serializa este [FormFieldResponse] a un mapa JSON (claves snake_case).
  Map<String, dynamic> toJson() => {
    'field_id': fieldId,
    'value': value,
    'file_url': fileUrl,
  };
}

/// Modelo de datos de un [FormDefinition] enviado.
///
/// Mapea entre el JSON snake_case del backend y los campos camelCase de Dart.
@HiveType(typeId: 37)
class FormResponse {
  @HiveField(0)
  final int? id;
  @HiveField(1)
  final int formId;
  @HiveField(2)
  final int? userId;
  @HiveField(3)
  final int? festivalId;
  /// Estado del envío; ver [SubmissionStatus].
  @HiveField(4)
  final String status;
  @HiveField(5)
  final DateTime? submittedAt;
  @HiveField(6)
  final int? reviewerId;
  @HiveField(7)
  final DateTime? reviewedAt;
  @HiveField(8)
  final String? reviewNotes;
  @HiveField(9)
  final String? linkToken;
  @HiveField(10)
  final List<FormFieldResponse> fieldResponses;
  @HiveField(11)
  final DateTime? createdAt;
  @HiveField(12)
  final DateTime? updatedAt;

  FormResponse({
    this.id,
    required this.formId,
    this.userId,
    this.festivalId,
    this.status = 'draft',
    this.submittedAt,
    this.reviewerId,
    this.reviewedAt,
    this.reviewNotes,
    this.linkToken,
    this.fieldResponses = const [],
    this.createdAt,
    this.updatedAt,
  });

  /// Crea un [FormResponse] a partir de un mapa JSON (claves snake_case del backend).
  factory FormResponse.fromJson(Map<String, dynamic> json) {
    return FormResponse(
      id: json['id'],
      formId: json['form_id'],
      userId: json['user_id'],
      festivalId: json['festival_id'],
      status: json['status'] ?? 'draft',
      submittedAt: json['submitted_at'] != null ? DateTime.parse(json['submitted_at']) : null,
      reviewerId: json['reviewer_id'],
      reviewedAt: json['reviewed_at'] != null ? DateTime.parse(json['reviewed_at']) : null,
      reviewNotes: json['review_notes'],
      linkToken: json['link_token'],
      fieldResponses: json['field_responses'] != null
          ? (json['field_responses'] as List).map((r) => FormFieldResponse.fromJson(r)).toList()
          : [],
      createdAt: json['created_at'] != null ? DateTime.parse(json['created_at']) : null,
      updatedAt: json['updated_at'] != null ? DateTime.parse(json['updated_at']) : null,
    );
  }

  /// Serializa este [FormResponse] a un mapa JSON (claves snake_case).
  Map<String, dynamic> toJson() => {
    'form_id': formId,
    'user_id': userId,
    'festival_id': festivalId,
    'status': status,
    'submitted_at': submittedAt?.toIso8601String(),
    'review_notes': reviewNotes,
    'link_token': linkToken,
    'field_responses': fieldResponses.map((r) => r.toJson()).toList(),
  };
}

/// Modelo de datos de una regla de acceso basada en roles sobre un [FormDefinition].
///
/// Mapea entre el JSON snake_case del backend y los campos camelCase de Dart.
@HiveType(typeId: 38)
class FormAccessRule {
  @HiveField(0)
  final int? id;
  @HiveField(1)
  final int formId;
  @HiveField(2)
  final int roleId;
  /// Nivel de acceso concedido o denegado; ver [FormAccessLevel].
  @HiveField(3)
  final String accessLevel;
  /// Indica si esta regla deniega (true) en lugar de conceder el acceso.
  @HiveField(4)
  final bool isDeny;
  @HiveField(5)
  final DateTime? createdAt;
  @HiveField(6)
  final DateTime? updatedAt;

  FormAccessRule({
    this.id,
    required this.formId,
    required this.roleId,
    required this.accessLevel,
    this.isDeny = false,
    this.createdAt,
    this.updatedAt,
  });

  /// Crea un [FormAccessRule] a partir de un mapa JSON (claves snake_case del backend).
  factory FormAccessRule.fromJson(Map<String, dynamic> json) {
    return FormAccessRule(
      id: json['id'],
      formId: json['form_id'],
      roleId: json['role_id'],
      accessLevel: json['access_level'],
      isDeny: json['is_deny'] ?? false,
      createdAt: json['created_at'] != null ? DateTime.parse(json['created_at']) : null,
      updatedAt: json['updated_at'] != null ? DateTime.parse(json['updated_at']) : null,
    );
  }

  /// Serializa este [FormAccessRule] a un mapa JSON (claves snake_case).
  Map<String, dynamic> toJson() => {
    'role_id': roleId,
    'access_level': accessLevel,
    'is_deny': isDeny,
  };
}
