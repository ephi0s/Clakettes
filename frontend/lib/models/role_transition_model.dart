import 'package:hive/hive.dart';

part 'role_transition_model.g.dart';

/// Modelo de datos de un cambio de rol de un usuario dentro de la plataforma.
///
/// Mapea entre el JSON snake_case del backend y los campos camelCase de Dart.
/// Los objetos anidados ``from_role`` y ``to_role`` se aplanan en los campos
/// correspondientes ``*Name``.
@HiveType(typeId: 18)
class RoleTransition {
  @HiveField(0)
  final int? id;
  @HiveField(1)
  final int userId;
  @HiveField(2)
  final int? fromRoleId;
  @HiveField(3)
  final int toRoleId;
  @HiveField(4)
  final int? fromFestivalId;
  @HiveField(5)
  final int? toFestivalId;
  /// Tipo de transición, p. ej. ``promotion``, ``demotion`` o ``transfer``.
  @HiveField(6)
  final String transitionType;
  @HiveField(7)
  final int changedBy;
  @HiveField(8)
  final String? reason;
  @HiveField(9)
  final String? fromRoleName;
  @HiveField(10)
  final String? toRoleName;

  RoleTransition({
    this.id,
    required this.userId,
    this.fromRoleId,
    required this.toRoleId,
    this.fromFestivalId,
    this.toFestivalId,
    required this.transitionType,
    required this.changedBy,
    this.reason,
    this.fromRoleName,
    this.toRoleName,
  });

  /// Crea un [RoleTransition] a partir de un mapa JSON (claves snake_case del backend).
  factory RoleTransition.fromJson(Map<String, dynamic> json) {
    return RoleTransition(
      id: json['id'],
      userId: json['user_id'],
      fromRoleId: json['from_role_id'],
      toRoleId: json['to_role_id'],
      fromFestivalId: json['from_festival_id'],
      toFestivalId: json['to_festival_id'],
      transitionType: json['transition_type'],
      changedBy: json['changed_by'],
      reason: json['reason'],
      fromRoleName: json['from_role']?['display_name'],
      toRoleName: json['to_role']?['display_name'],
    );
  }

  /// Serializa este [RoleTransition] a un mapa JSON (claves snake_case).
  Map<String, dynamic> toJson() => {
    'user_id': userId,
    'from_role_id': fromRoleId,
    'to_role_id': toRoleId,
    'from_festival_id': fromFestivalId,
    'to_festival_id': toFestivalId,
    'transition_type': transitionType,
    'changed_by': changedBy,
    'reason': reason,
  };
}
