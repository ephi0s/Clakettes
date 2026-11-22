part of '../api_service.dart';

/// Llamadas de catalog_.
extension CatalogApi on ApiService {
  /// Obtiene la lista paginada de cortometrajes, con filtros opcionales.
  Future<PaginatedResult<ShortFilm>> getShortFilms({
    int page = 1,
    int size = 20,
    required int festivalId,
    String? contestType,
    bool? isPublic,
  }) async {
    final params = <String, String>{'page': '$page', 'size': '$size'};
    if (contestType != null) params['contest_type'] = contestType;
    if (isPublic != null) params['is_public'] = '$isPublic';
    final data = await _get('/festivals/$festivalId/shortfilms', params);
    return _paginated(data, ShortFilm.fromJson);
  }

  /// Total global de cortometrajes (el listado plano sigue disponible).
  Future<int> getShortFilmsCount() async {
    final data = await _get('/shortfilms/', {'page': '1', 'size': '1'});
    return _extractTotal(data);
  }

  /// Crea un cortometraje dentro de su festival.
  Future<ShortFilm> createShortFilm(ShortFilm shortFilm) async {
    final data = await create('/festivals/${shortFilm.festivalId}/shortfilms', shortFilm.toJson());
    return ShortFilm.fromJson(data);
  }

  /// Obtiene un cortometraje por su id dentro de un festival.
  Future<ShortFilm> getShortFilm(int festivalId, int id) async {
    final data = await request('GET', '/festivals/$festivalId/shortfilms/$id');
    return ShortFilm.fromJson(data);
  }

  /// Actualiza los campos indicados de un cortometraje.
  Future<ShortFilm> updateShortFilm(int festivalId, int id, Map<String, dynamic> fields) async {
    final data = await _put('/festivals/$festivalId/shortfilms/$id', fields);
    return ShortFilm.fromJson(data);
  }

  /// Elimina un cortometraje por su id.
  Future<void> deleteShortFilm(int festivalId, int id) async {
    await request('DELETE', '/festivals/$festivalId/shortfilms/$id');
  }

  /// Obtiene los premios paginados de un festival, con filtros opcionales.
  Future<PaginatedResult<Award>> getAwards(int festivalId,
      {int page = 1,
      int size = 20,
      int? userId,
      int? shortfilmId,
      String? eligibilityTag,
      bool? recipientVerified}) async {
    final params = <String, String>{'page': '$page', 'size': '$size'};
    if (userId != null) params['user_id'] = '$userId';
    if (shortfilmId != null) params['shortfilm_id'] = '$shortfilmId';
    if (eligibilityTag != null) params['eligibility_tag'] = eligibilityTag;
    if (recipientVerified != null) {
      params['recipient_verified'] = '$recipientVerified';
    }
    final data = await _get('/festivals/$festivalId/awards/', params);
    return _paginated(data, Award.fromJson);
  }

  /// Crea un premio en un festival y devuelve el [Award] creado.
  Future<Award> createAward(int festivalId, Award a) async {
    final data = await create('/festivals/$festivalId/awards/', a.toJson());
    return Award.fromJson(data);
  }

  Future<Award> updateAward(int id, Map<String, dynamic> fields) async {
    final data = await _put('/awards/$id', fields);
    return Award.fromJson(data);
  }

  /// Elimina un premio por su id.
  Future<void> deleteAward(int awardId) async {
    await request('DELETE', '/awards/$awardId');
  }

  Future<Award> verifyAward(int id, bool verified) async {
    final data = await _put('/awards/$id', {'is_verified': verified});
    return Award.fromJson(Map<String, dynamic>.from(data as Map));
  }

  /// Verifica o desmarca al receptor de un premio.
  Future<Award> verifyAwardRecipient(int id, bool verified, {String? notes}) async {
    final data = await request('PATCH', '/awards/$id/recipient-verification',
        body: json.encode({'verified': verified, 'notes': notes}));
    return Award.fromJson(Map<String, dynamic>.from(data as Map));
  }

  Future<PaginatedResult<Award>> getUserAwards(int userId,
      {int page = 1, int size = 20}) async {
    final data = await _get('/users/$userId/awards/', {
      'page': '$page',
      'size': '$size',
    });
    return _paginated(
        data, (j) => Award.fromJson(Map<String, dynamic>.from(j as Map)));
  }

  /// Obtiene las bases paginadas de un festival, con filtro opcional de categoría.
  Future<PaginatedResult<FestivalRulebook>> getRulebooks(int festivalId,
      {int page = 1, int size = 20, String? category}) async {
    final params = <String, String>{'page': '$page', 'size': '$size'};
    if (category != null) params['category'] = category;
    final data = await _get('/festivals/$festivalId/rulebooks/', params);
    return _paginated(data, FestivalRulebook.fromJson);
  }

  /// Crea unas bases con documento externo (URL) y devuelve el objeto creado.
  Future<FestivalRulebook> createRulebook(
      int festivalId, FestivalRulebook r) async {
    final data = await create('/festivals/$festivalId/rulebooks/', r.toJson());
    return FestivalRulebook.fromJson(data);
  }

  /// Actualiza los campos indicados de unas bases.
  Future<FestivalRulebook> updateRulebook(
      int festivalId, int rulebookId, Map<String, dynamic> fields) async {
    final data =
        await _put('/festivals/$festivalId/rulebooks/$rulebookId', fields);
    return FestivalRulebook.fromJson(data);
  }

  /// Elimina unas bases por su id.
  Future<void> deleteRulebook(int festivalId, int rulebookId) async {
    await request('DELETE', '/festivals/$festivalId/rulebooks/$rulebookId');
  }

  /// Sube un PDF de bases con sus metadatos mediante multipart.
  Future<FestivalRulebook> uploadRulebook(int festivalId, XFile file,
      {required String title,
      String? description,
      String category = 'official_section',
      int? eventId,
      String? externalUrl}) async {
    final fields = <String, String>{
      'title': title,
      'category': category,
      if (description != null && description.isNotEmpty) 'description': description,
      if (eventId != null) 'event_id': '$eventId',
      if (externalUrl != null && externalUrl.isNotEmpty) 'external_url': externalUrl,
    };
    final data = await uploadFile(
      '/festivals/$festivalId/rulebooks/upload',
      file,
      errorLabel: 'Rulebook upload',
      fields: fields,
    );
    return FestivalRulebook.fromJson(data);
  }
}
