// Resumen de un rol, usado para los selectores de la interfaz.
//
// El backend expone los roles de un festival en `GET /festivals/{id}/roles/`,
// donde cada elemento envuelve el rol real bajo la clave `role`; por eso este
// modelo no se persiste en Hive y solo conserva lo necesario para mostrarlo.

/// Un rol asignable dentro de un festival.
class RoleSummary {
  final int id;
  final String name;
  final String displayName;
  final String? description;
  final String scope;
  final bool isActive;

  const RoleSummary({
    required this.id,
    required this.name,
    required this.displayName,
    this.description,
    this.scope = 'festival',
    this.isActive = true,
  });

  /// Acepta tanto el objeto `role` anidado como el elemento plano del festival.
  factory RoleSummary.fromJson(Map<String, dynamic> json) {
    final nested = json['role'];
    final source = nested is Map
        ? Map<String, dynamic>.from(nested)
        : json;
    final name = (source['name'] as String?) ?? '';
    return RoleSummary(
      id: source['id'] as int,
      name: name,
      displayName: (source['display_name'] as String?)?.trim().isNotEmpty == true
          ? source['display_name'] as String
          : name,
      description: source['description'],
      scope: source['scope'] as String? ?? 'festival',
      isActive: source['is_active'] ?? true,
    );
  }
}