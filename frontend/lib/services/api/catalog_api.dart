part of '../api_service.dart';

/// Llamadas de catalog_.
extension CatalogApi on ApiService {
  /// Obtiene la lista paginada de cortometrajes, con filtros opcionales.
  Future<PaginatedResult<ShortFilm>> getShortFilms({
    int page = 1,
    int size = 20,
    int? festivalId,
    bool? isPublic,
  }) async {
    final params = <String, String>{'page': '$page', 'size': '$size'};
    if (festivalId != null) params['festival_id'] = '$festivalId';
    if (isPublic != null) params['is_public'] = '$isPublic';
    final data = await _get('/shortfilms/', params);
    return _paginated(data, ShortFilm.fromJson);
  }

  /// Crea un cortometraje y devuelve el [ShortFilm] creado.
  Future<ShortFilm> createShortFilm(ShortFilm shortFilm) async {
    final data = await create('/shortfilms/', shortFilm.toJson());
    return ShortFilm.fromJson(data);
  }

  /// Obtiene un cortometraje por su id.
  Future<ShortFilm> getShortFilm(int id) async {
    final data = await request('GET', '/shortfilms/$id');
    return ShortFilm.fromJson(data);
  }

  /// Actualiza los campos indicados de un cortometraje.
  Future<ShortFilm> updateShortFilm(int id, Map<String, dynamic> fields) async {
    final data = await _put('/shortfilms/$id', fields);
    return ShortFilm.fromJson(data);
  }

  /// Elimina un cortometraje por su id.
  Future<void> deleteShortFilm(int id) async {
    await request('DELETE', '/shortfilms/$id');
  }

  /// Obtiene los premios paginados de un festival, con filtros opcionales.
  Future<PaginatedResult<Award>> getAwards(int festivalId,
      {int page = 1, int size = 20, int? userId, int? shortfilmId}) async {
    final params = <String, String>{'page': '$page', 'size': '$size'};
    if (userId != null) params['user_id'] = '$userId';
    if (shortfilmId != null) params['shortfilm_id'] = '$shortfilmId';
    final data = await _get('/festivals/$festivalId/awards/', params);
    return _paginated(data, Award.fromJson);
  }

  /// Crea un premio en un festival y devuelve el [Award] creado.
  Future<Award> createAward(int festivalId, Award a) async {
    final data = await create('/festivals/$festivalId/awards/', a.toJson());
    return Award.fromJson(data);
  }

  /// Elimina un premio por su id.
  Future<void> deleteAward(int awardId) async {
    await request('DELETE', '/awards/$awardId');
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
  Future<FestivalRulebook> uploadRulebook(int festivalId, String filePath,
      {required String title,
      String? description,
      String category = 'official_section',
      int? eventId,
      String? externalUrl}) async {
    final uri = Uri.parse('$baseUrl/festivals/$festivalId/rulebooks/upload');
    final token = await _auth.getToken();
    final req = http.MultipartRequest('POST', uri);
    if (token != null) req.headers['Authorization'] = 'Bearer $token';
    req.fields['title'] = title;
    if (description != null && description.isNotEmpty) {
      req.fields['description'] = description;
    }
    req.fields['category'] = category;
    if (eventId != null) {
      req.fields['event_id'] = '$eventId';
    }
    if (externalUrl != null && externalUrl.isNotEmpty) {
      req.fields['external_url'] = externalUrl;
    }
    req.files.add(await http.MultipartFile.fromPath('file', filePath));
    late http.Response response;
    try {
      final streamed = await req.send();
      response = await http.Response.fromStream(streamed);
    } catch (_) {
      throw ApiException('Network error (upload)');
    }
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return FestivalRulebook.fromJson(json.decode(response.body));
    }
    throw ApiException('Rulebook upload failed (${response.statusCode})',
        statusCode: response.statusCode);
  }
}
