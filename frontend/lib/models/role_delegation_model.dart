import 'package:hive/hive.dart';

part 'role_delegation_model.g.dart';

/// Modelo de datos de la delegación temporal de un rol a otro usuario.
///
/// Mapea entre el JSON snake_case del backend y los campos camelCase de Dart.
/// Los objetos anidados ``delegator``, ``delegate`` y ``role`` se aplanan en
/// los campos correspondientes ``*Name``.
@HiveType(typeId: 15)
class RoleDelegation {
  @HiveField(0)
  final int? id;
  @HiveField(1)
  final int delegatorId;
  @HiveField(2)
  final int delegateId;
  @HiveField(3)
  final int roleId;
  @HiveField(4)
  final int? festivalId;
  /// Estado de la delegación, p. ej. ``active``, ``pending`` o ``revoked``.
  @HiveField(5)
  final String status;
  @HiveField(6)
  final String? reason;
  /// Descripción en texto libre de lo que el delegado puede o no puede hacer.
  @HiveField(7)
  final String? scopeLimitations;
  @HiveField(8)
  final int? revokedBy;
  @HiveField(9)
  final String? revokedReason;
  @HiveField(10)
  final String? delegatorName;
  @HiveField(11)
  final String? delegateName;
  @HiveField(12)
  final String? roleName;

  RoleDelegation({
    this.id,
    required this.delegatorId,
    required this.delegateId,
    required this.roleId,
    this.festivalId,
    this.status = 'active',
    this.reason,
    this.scopeLimitations,
    this.revokedBy,
    this.revokedReason,
    this.delegatorName,
    this.delegateName,
    this.roleName,
  });

  /// Crea un [RoleDelegation] a partir de un mapa JSON (claves snake_case del backend).
  factory RoleDelegation.fromJson(Map<String, dynamic> json) {
    return RoleDelegation(
      id: json['id'],
      delegatorId: json['delegator_id'],
      delegateId: json['delegate_id'],
      roleId: json['role_id'],
      festivalId: json['festival_id'],
      status: json['status'] ?? 'active',
      reason: json['reason'],
      scopeLimitations: json['scope_limitations'],
      revokedBy: json['revoked_by'],
      revokedReason: json['revoked_reason'],
      delegatorName: json['delegator']?['full_name'] ?? json['delegator']?['username'],
      delegateName: json['delegate']?['full_name'] ?? json['delegate']?['username'],
      roleName: json['role']?['display_name'],
    );
  }

  /// Serializa este [RoleDelegation] a un mapa JSON (claves snake_case).
  Map<String, dynamic> toJson() => {
    'delegator_id': delegatorId,
    'delegate_id': delegateId,
    'role_id': roleId,
    'festival_id': festivalId,
    'reason': reason,
    'scope_limitations': scopeLimitations,
  };
}
