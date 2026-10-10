import 'package:hive/hive.dart';

part 'committee_model.g.dart';

/// Modelo de datos de un comité de festival (grupo de miembros con un rol compartido).
///
/// Mapea entre el JSON snake_case del backend y los campos camelCase de Dart.
@HiveType(typeId: 3)
class Committee {
  @HiveField(0)
  final int? id;
  @HiveField(1)
  final int festivalId;
  @HiveField(2)
  final String name;
  @HiveField(3)
  final String? description;
  @HiveField(4)
  final int? roleId;
  @HiveField(5)
  final bool isActive;
  @HiveField(6)
  final int? maxMembers;
  /// Indica si el comité se muestra a usuarios externos.
  @HiveField(7)
  final bool externalVisible;
  /// Número de miembros activos (derivado del backend).
  @HiveField(8)
  final int memberCount;

  Committee({
    this.id,
    required this.festivalId,
    required this.name,
    this.description,
    this.roleId,
    this.isActive = true,
    this.maxMembers,
    this.externalVisible = false,
    this.memberCount = 0,
  });

  /// Crea un [Committee] a partir de un mapa JSON (claves snake_case del backend).
  factory Committee.fromJson(Map<String, dynamic> json) {
    return Committee(
      id: json['id'],
      festivalId: json['festival_id'],
      name: json['name'],
      description: json['description'],
      roleId: json['role_id'],
      isActive: json['is_active'] ?? true,
      maxMembers: json['max_members'],
      externalVisible: json['external_visible'] ?? false,
      memberCount: json['member_count'] ?? 0,
    );
  }

  /// Serializa este [Committee] a un mapa JSON (claves snake_case).
  Map<String, dynamic> toJson() => {
    'festival_id': festivalId,
    'name': name,
    'description': description,
    'role_id': roleId,
    'is_active': isActive,
    'max_members': maxMembers,
    'external_visible': externalVisible,
  };
}


/// Modelo de datos de la pertenencia de un usuario a un [Committee].
///
/// Mapea entre el JSON snake_case del backend y los campos camelCase de Dart.
/// El objeto anidado ``user`` del backend se aplana en [userName] y [userAvatar].
@HiveType(typeId: 4)
class CommitteeMember {
  @HiveField(0)
  final int? id;
  @HiveField(1)
  final int committeeId;
  @HiveField(2)
  final int userId;
  /// Rol dentro del comité; ver [committeeRoles].
  @HiveField(3)
  final String roleInCommittee;
  @HiveField(4)
  final int? assignedBy;
  @HiveField(5)
  final bool isActive;
  @HiveField(6)
  final String? notes;
  @HiveField(7)
  final String? userName;
  @HiveField(8)
  final String? userAvatar;

  CommitteeMember({
    this.id,
    required this.committeeId,
    required this.userId,
    this.roleInCommittee = 'member',
    this.assignedBy,
    this.isActive = true,
    this.notes,
    this.userName,
    this.userAvatar,
  });

  /// Crea un [CommitteeMember] a partir de un mapa JSON (claves snake_case del backend).
  factory CommitteeMember.fromJson(Map<String, dynamic> json) {
    return CommitteeMember(
      id: json['id'],
      committeeId: json['committee_id'],
      userId: json['user_id'],
      roleInCommittee: json['role_in_committee'] ?? 'member',
      assignedBy: json['assigned_by'],
      isActive: json['is_active'] ?? true,
      notes: json['notes'],
      userName: json['user']?['full_name'] ?? json['user']?['username'],
      userAvatar: json['user']?['avatar_url'],
    );
  }

  /// Serializa este [CommitteeMember] a un mapa JSON (claves snake_case).
  Map<String, dynamic> toJson() => {
    'committee_id': committeeId,
    'user_id': userId,
    'role_in_committee': roleInCommittee,
    'assigned_by': assignedBy,
    'notes': notes,
  };
}


/// Valores permitidos para [CommitteeMember.roleInCommittee].
const List<String> committeeRoles = [
  'chair', 'vice_chair', 'member', 'secretary', 'advisor',
];
