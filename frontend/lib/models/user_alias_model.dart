import 'package:hive/hive.dart';

part 'user_alias_model.g.dart';

/// Modelo de datos de una identidad pública alternativa de un usuario.
///
/// Mapea entre el JSON snake_case del backend y los campos camelCase de Dart.
@HiveType(typeId: 21)
class UserAlias {
  @HiveField(0)
  final int? id;
  @HiveField(1)
  final int userId;
  @HiveField(2)
  final String alias;
  /// Ámbito donde se aplica el alias, p. ej. ``global`` o ``festival``.
  @HiveField(3)
  final String context;
  /// ID de la entidad identificada por [context] (p. ej. el festival).
  @HiveField(4)
  final int? contextId;
  /// Indica si este es el alias principal del usuario.
  @HiveField(5)
  final bool isPrimary;
  @HiveField(6)
  final bool isPublic;
  /// Indica si los premios se muestran bajo este alias.
  @HiveField(7)
  final bool showAwards;
  /// Token opaco usado para compartir el perfil público del alias.
  @HiveField(8)
  final String? profileToken;
  /// Quién puede ver este alias, p. ej. ``festival_only`` o ``public``.
  @HiveField(9)
  final String visibilityScope;
  @HiveField(10)
  final String? notes;

  UserAlias({
    this.id,
    required this.userId,
    required this.alias,
    this.context = 'global',
    this.contextId,
    this.isPrimary = false,
    this.isPublic = true,
    this.showAwards = false,
    this.profileToken,
    this.visibilityScope = 'festival_only',
    this.notes,
  });

  /// Crea un [UserAlias] a partir de un mapa JSON (claves snake_case del backend).
  factory UserAlias.fromJson(Map<String, dynamic> json) {
    return UserAlias(
      id: json['id'],
      userId: json['user_id'],
      alias: json['alias'],
      context: json['context'] ?? 'global',
      contextId: json['context_id'],
      isPrimary: json['is_primary'] ?? false,
      isPublic: json['is_public'] ?? true,
      showAwards: json['show_awards'] ?? false,
      profileToken: json['profile_token'],
      visibilityScope: json['visibility_scope'] ?? 'festival_only',
      notes: json['notes'],
    );
  }

  /// Serializa este [UserAlias] a un mapa JSON (claves snake_case).
  Map<String, dynamic> toJson() => {
    'user_id': userId,
    'alias': alias,
    'context': context,
    'context_id': contextId,
    'is_primary': isPrimary,
    'is_public': isPublic,
    'show_awards': showAwards,
    'visibility_scope': visibilityScope,
    'notes': notes,
  };
}

