part of '../api_service.dart';

/// Llamadas de participant_tags y user_roles (etiquetas de participante).
extension ParticipantTagApi on ApiService {
  /// Obtiene el catálogo paginado de etiquetas de participante.
  Future<PaginatedResult<ParticipantTag>> getParticipantTags(
      {int page = 1, int size = 50, String? category}) async {
    final params = <String, String>{'page': '$page', 'size': '$size'};
    if (category != null) params['category'] = category;
    final data = await _get('/participant-tags/', params);
    return _paginated(
        data, (j) => ParticipantTag.fromJson(Map<String, dynamic>.from(j as Map)));
  }

  /// Obtiene las etiquetas asignadas a un usuario, con filtros opcionales.
  Future<PaginatedResult<UserParticipantTag>> getUserParticipantTags(int userId,
      {int page = 1,
      int size = 50,
      int? festivalId,
      String? verificationStatus}) async {
    final params = <String, String>{'page': '$page', 'size': '$size'};
    if (festivalId != null) params['festival_id'] = '$festivalId';
    if (verificationStatus != null) {
      params['verification_status'] = verificationStatus;
    }
    final data = await _get('/users/$userId/participant-tags/', params);
    return _paginated(data,
        (j) => UserParticipantTag.fromJson(Map<String, dynamic>.from(j as Map)));
  }

  /// Asigna una etiqueta de participante a un usuario.
  Future<UserParticipantTag> assignParticipantTag(int userId, int tagId,
      {int? festivalId, bool isPrimary = false, String? notes}) async {
    final data = await create('/users/$userId/participant-tags/', {
      'tag_id': tagId,
      'festival_id': festivalId,
      'is_primary': isPrimary,
      'notes': notes,
    });
    return UserParticipantTag.fromJson(Map<String, dynamic>.from(data as Map));
  }

  /// Solicita la verificación de una etiqueta propia.
  Future<UserParticipantTag> requestTagVerification(
      int userId, int uptId, String method,
      {String? documentUrl, String? notes}) async {
    final data = await request(
        'POST', '/users/$userId/participant-tags/$uptId/request-verification',
        body: json.encode({
          'method': method,
          'document_url': documentUrl,
          'notes': notes,
        }));
    return UserParticipantTag.fromJson(Map<String, dynamic>.from(data as Map));
  }

  /// Aprueba o rechaza la verificación de una etiqueta de un usuario.
  Future<UserParticipantTag> verifyParticipantTag(
      int userId, int uptId, String status,
      {String? method, String? notes}) async {
    final data =
        await request('PATCH', '/users/$userId/participant-tags/$uptId/verify',
            body: json.encode({
              'status': status,
              'method': method,
              'notes': notes,
            }));
    return UserParticipantTag.fromJson(Map<String, dynamic>.from(data as Map));
  }

  /// Elimina una etiqueta asignada a un usuario.
  Future<void> removeParticipantTag(int userId, int uptId) async {
    await request('DELETE', '/users/$userId/participant-tags/$uptId');
  }

  /// Sube un documento (PDF) y devuelve su URL.
  Future<String> uploadDocument(String filePath) async {
    final data =
        await _uploadFile('/uploads/document', filePath, errorLabel: 'Document');
    return Map<String, dynamic>.from(data as Map)['url'] as String;
  }
}
