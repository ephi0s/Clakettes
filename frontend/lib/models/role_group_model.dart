import 'package:hive/hive.dart';

part 'role_group_model.g.dart';

/// Modelo de datos de un grupo de roles con nombre.
///
/// Mapea entre el JSON snake_case del backend y los campos camelCase de Dart.
@HiveType(typeId: 16)
class RoleGroup {
  @HiveField(0)
  final int? id;
  @HiveField(1)
  final String name;
  @HiveField(2)
  final String displayName;
  @HiveField(3)
  final String? description;
  @HiveField(4)
  final int sortOrder;
  @HiveField(5)
  final bool isActive;

  RoleGroup({
    this.id,
    required this.name,
    required this.displayName,
    this.description,
    this.sortOrder = 0,
    this.isActive = true,
  });

  /// Crea un [RoleGroup] a partir de un mapa JSON (claves snake_case del backend).
  factory RoleGroup.fromJson(Map<String, dynamic> json) {
    return RoleGroup(
      id: json['id'],
      name: json['name'],
      displayName: json['display_name'],
      description: json['description'],
      sortOrder: json['sort_order'] ?? 0,
      isActive: json['is_active'] ?? true,
    );
  }

  /// Serializa este [RoleGroup] a un mapa JSON (claves snake_case).
  Map<String, dynamic> toJson() => {
    'name': name,
    'display_name': displayName,
    'description': description,
    'sort_order': sortOrder,
    'is_active': isActive,
  };
}


/// Modelo de datos de la pertenencia de un rol a un [RoleGroup].
///
/// Mapea entre el JSON snake_case del backend y los campos camelCase de Dart.
@HiveType(typeId: 17)
class RoleGroupMembership {
  @HiveField(0)
  final int? id;
  @HiveField(1)
  final int groupId;
  @HiveField(2)
  final int roleId;
  /// Nivel jerárquico del rol dentro del grupo.
  @HiveField(3)
  final int level;
  /// Indica si este rol lidera el grupo.
  @HiveField(4)
  final bool isLeader;
  @HiveField(5)
  final bool isActive;
  @HiveField(6)
  final String? roleName;

  RoleGroupMembership({
    this.id,
    required this.groupId,
    required this.roleId,
    this.level = 0,
    this.isLeader = false,
    this.isActive = true,
    this.roleName,
  });

  /// Crea un [RoleGroupMembership] a partir de un mapa JSON (claves snake_case del backend).
  factory RoleGroupMembership.fromJson(Map<String, dynamic> json) {
    return RoleGroupMembership(
      id: json['id'],
      groupId: json['group_id'],
      roleId: json['role_id'],
      level: json['level'] ?? 0,
      isLeader: json['is_leader'] ?? false,
      isActive: json['is_active'] ?? true,
      roleName: json['role']?['display_name'],
    );
  }

  /// Serializa este [RoleGroupMembership] a un mapa JSON (claves snake_case).
  Map<String, dynamic> toJson() => {
    'group_id': groupId,
    'role_id': roleId,
    'level': level,
    'is_leader': isLeader,
  };
}
