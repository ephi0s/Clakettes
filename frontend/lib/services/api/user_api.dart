part of '../api_service.dart';

extension UserApi on ApiService {
  Future<PaginatedResult<User>> getUsers({
    int page = 1,
    int size = 20,
    bool? isActive,
    String? role,
  }) async {
    final params = <String, String>{'page': '$page', 'size': '$size'};
    if (isActive != null) params['is_active'] = '$isActive';
    if (role != null) params['role'] = role;
    final data = await _get('/users/', params);
    return _paginated(data, User.fromJson);
  }

  Future<User> createUser(User user, String password) async {
    final data = await create('/users/', {
      ...user.toJson(),
      'password': password,
    });
    return User.fromJson(data);
  }

  Future<User> getUser(int id) async {
    final data = await request('GET', '/users/$id');
    return User.fromJson(data);
  }

  Future<User> updateUser(int id, Map<String, dynamic> fields) async {
    final data = await _put('/users/$id', fields);
    return User.fromJson(data);
  }

  Future<void> deleteUser(int id) async {
    await request('DELETE', '/users/$id');
  }

  /// Lista todas las sesiones del usuario actual.
  Future<PaginatedResult<UserSession>> getSessions(
      {int page = 1, int size = 20}) async {
    final params = <String, String>{'page': '$page', 'size': '$size'};
    final data = await _get('/auth/sessions', params);
    return _paginated(data, UserSession.fromJson);
  }

  /// Revoca una sesión específica.
  Future<void> revokeSession(int sessionId) async {
    await request('DELETE', '/auth/sessions/$sessionId');
  }

  /// Revoca todas las sesiones (cierra sesión en todos los dispositivos).
  Future<void> revokeAllSessions() async {
    await request('POST', '/auth/sessions/revoke-all');
  }

  /// Obtiene la lista paginada de notificaciones, con filtro opcional de leídas.
  Future<PaginatedResult<AppNotification>> getNotifications({
    int page = 1,
    int size = 20,
    bool? isRead,
  }) async {
    final params = <String, String>{'page': '$page', 'size': '$size'};
    if (isRead != null) params['is_read'] = '$isRead';
    final data = await _get('/notifications/', params);
    return _paginated(data, AppNotification.fromJson);
  }

  /// Obtiene el número de notificaciones no leídas.
  Future<int> getUnreadNotificationCount() async {
    final data = await request('GET', '/notifications/unread-count');
    final c = data['count'];
    if (c is int) return c;
    if (c is num) return c.toInt();
    return int.tryParse(c?.toString() ?? '') ?? 0;
  }

  /// Marca una notificación como leída.
  Future<void> markNotificationRead(int notificationId) async {
    await request('PUT', '/notifications/$notificationId/read');
  }

  /// Marca todas las notificaciones como leídas.
  Future<void> markAllNotificationsRead() async {
    await request('PUT', '/notifications/read-all');
  }

  /// Elimina una notificación.
  Future<void> deleteNotification(int notificationId) async {
    await request('DELETE', '/notifications/$notificationId');
  }

  /// Obtiene el perfil público (consciente de alias) de un usuario en un festival.
  Future<Map<String, dynamic>> getFestivalUserProfile(
      int festivalId, int userId) async {
    return await request('GET', '/festivals/$festivalId/users/$userId/profile',
        withAuth: false);
  }
}
