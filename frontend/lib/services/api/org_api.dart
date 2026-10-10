part of '../api_service.dart';

/// Llamadas de org_.
extension OrgApi on ApiService {
  /// Obtiene la lista paginada de grupos de roles, con filtro opcional de activos.
  Future<PaginatedResult<RoleGroup>> getRoleGroups(
      {int page = 1, int size = 20, bool? isActive}) async {
    final params = <String, String>{'page': '$page', 'size': '$size'};
    if (isActive != null) params['is_active'] = '$isActive';
    final data = await _get('/role-groups/', params);
    return _paginated(data, RoleGroup.fromJson);
  }

  /// Crea un grupo de roles y devuelve el [RoleGroup] creado.
  Future<RoleGroup> createRoleGroup(RoleGroup g) async {
    final data = await create('/role-groups/', g.toJson());
    return RoleGroup.fromJson(data);
  }

  /// Obtiene un grupo de roles por su id.
  Future<RoleGroup> getRoleGroup(int id) async {
    final data = await request('GET', '/role-groups/$id');
    return RoleGroup.fromJson(data);
  }

  /// Actualiza los campos indicados de un grupo de roles.
  Future<RoleGroup> updateRoleGroup(int id, Map<String, dynamic> fields) async {
    final data = await _put('/role-groups/$id', fields);
    return RoleGroup.fromJson(data);
  }

  /// Elimina un grupo de roles por su id.
  Future<void> deleteRoleGroup(int id) async {
    await request('DELETE', '/role-groups/$id');
  }

  /// Obtiene los comités paginados de un festival.
  Future<PaginatedResult<Committee>> getCommittees(int festivalId,
      {int page = 1, int size = 20}) async {
    final params = <String, String>{'page': '$page', 'size': '$size'};
    final data = await _get('/festivals/$festivalId/committees/', params);
    return _paginated(data, Committee.fromJson);
  }

  /// Crea un comité en un festival y devuelve el [Committee] creado.
  Future<Committee> createCommittee(int festivalId, Committee c) async {
    final data = await create('/festivals/$festivalId/committees/', c.toJson());
    return Committee.fromJson(data);
  }

  /// Obtiene un comité por su id.
  Future<Committee> getCommittee(int id) async {
    final data = await request('GET', '/committees/$id');
    return Committee.fromJson(data);
  }

  /// Actualiza los campos indicados de un comité.
  Future<Committee> updateCommittee(int id, Map<String, dynamic> fields) async {
    final data = await _put('/committees/$id', fields);
    return Committee.fromJson(data);
  }

  /// Elimina un comité por su id.
  Future<void> deleteCommittee(int id) async {
    await request('DELETE', '/committees/$id');
  }

  /// Obtiene los miembros paginados de un comité.
  Future<PaginatedResult<CommitteeMember>> getCommitteeMembers(int committeeId,
      {int page = 1, int size = 20}) async {
    final params = <String, String>{'page': '$page', 'size': '$size'};
    final data = await _get('/committees/$committeeId/members/', params);
    return _paginated(data, CommitteeMember.fromJson);
  }

  /// Añade un miembro a un comité y devuelve el [CommitteeMember] creado.
  Future<CommitteeMember> addCommitteeMember(
      int committeeId, CommitteeMember m) async {
    final data = await create('/committees/$committeeId/members/', m.toJson());
    return CommitteeMember.fromJson(data);
  }

  /// Elimina a un miembro de un comité.
  Future<void> removeCommitteeMember(int memberId) async {
    await request('DELETE', '/committee-members/$memberId');
  }

  /// Obtiene las delegaciones paginadas, con filtros opcionales.
  Future<PaginatedResult<RoleDelegation>> getDelegations({
    int page = 1,
    int size = 20,
    int? delegatorId,
    int? delegateId,
    String? status,
  }) async {
    final params = <String, String>{'page': '$page', 'size': '$size'};
    if (delegatorId != null) params['delegator_id'] = '$delegatorId';
    if (delegateId != null) params['delegate_id'] = '$delegateId';
    if (status != null) params['status'] = status;
    final data = await _get('/delegations/', params);
    return _paginated(data, RoleDelegation.fromJson);
  }

  /// Crea una delegación de rol y devuelve la [RoleDelegation] creada.
  Future<RoleDelegation> createDelegation(RoleDelegation d) async {
    final data = await create('/delegations/', d.toJson());
    return RoleDelegation.fromJson(data);
  }

  /// Revoca una delegación, con motivo opcional.
  Future<void> revokeDelegation(int delegationId, {String? reason}) async {
    final body = reason != null ? json.encode({'reason': reason}) : null;
    await request('POST', '/delegations/$delegationId/revoke', body: body);
  }

  /// Obtiene las transiciones de rol paginadas, con filtros opcionales.
  Future<PaginatedResult<RoleTransition>> getRoleTransitions({
    int page = 1,
    int size = 20,
    int? userId,
    String? transitionType,
  }) async {
    final params = <String, String>{'page': '$page', 'size': '$size'};
    if (userId != null) params['user_id'] = '$userId';
    if (transitionType != null) params['transition_type'] = transitionType;
    final data = await _get('/role-transitions/', params);
    return _paginated(data, RoleTransition.fromJson);
  }
}
