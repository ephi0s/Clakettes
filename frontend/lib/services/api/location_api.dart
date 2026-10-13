part of '../api_service.dart';

/// Llamadas de location_.
extension LocationApi on ApiService {
  /// Obtiene las localizaciones paginadas, con filtros opcionales de búsqueda y etiqueta.
  Future<PaginatedResult<Location>> getLocations({
    int page = 1,
    int size = 20,
    String? search,
    String? tag,
    bool? isActive,
  }) async {
    final params = <String, String>{'page': '$page', 'size': '$size'};
    if (search != null && search.isNotEmpty) params['search'] = search;
    if (tag != null) params['tag'] = tag;
    if (isActive != null) params['is_active'] = '$isActive';
    final data = await _get('/locations/', params);
    return _paginated(data, Location.fromJson);
  }

  /// Crea una localización y devuelve la [Location] creada.
  Future<Location> createLocation(Location location) async {
    final data = await create('/locations/', location.toJson());
    return Location.fromJson(data);
  }

  /// Obtiene una localización por su id.
  Future<Location> getLocation(int id) async {
    final data = await request('GET', '/locations/$id');
    return Location.fromJson(data);
  }

  /// Actualiza los campos indicados de una localización.
  Future<Location> updateLocation(int id, Map<String, dynamic> fields) async {
    final data = await _put('/locations/$id', fields);
    return Location.fromJson(data);
  }

  /// Elimina una localización por su id.
  Future<void> deleteLocation(int id) async {
    await request('DELETE', '/locations/$id');
  }

  /// Obtiene las localizaciones asociadas a un festival.
  Future<List<Location>> getFestivalLocations(int festivalId) async {
    final data = await request('GET', '/festivals/$festivalId/locations');
    return (data as List).map((j) => Location.fromJson(j)).toList();
  }

  /// Asocia una localización a un festival.
  Future<Location> addFestivalLocation(int festivalId, int locationId) async {
    final data = await create(
        '/festivals/$festivalId/locations', {'location_id': locationId});
    return Location.fromJson(data);
  }

  /// Desasocia una localización de un festival.
  Future<void> removeFestivalLocation(int festivalId, int locationId) async {
    await request('DELETE', '/festivals/$festivalId/locations/$locationId');
  }

  /// Sube una imagen para una localización.
  Future<LocationImage> uploadLocationImage(
      int locationId, String filePath) async {
    final data = await _uploadFile('/locations/$locationId/images/upload',
        filePath,
        errorLabel: 'Location image');
    return LocationImage.fromJson(data);
  }

  /// Obtiene las etiquetas de una localización.
  Future<List<LocationTag>> getLocationTags(int locationId) async {
    final data = await request('GET', '/locations/$locationId/tags/');
    return (data as List).map((j) => LocationTag.fromJson(j)).toList();
  }

  /// Propone una etiqueta para una localización.
  Future<LocationTag> proposeLocationTag(int locationId, String tag) async {
    final data = await create('/locations/$locationId/tags/', {'tag': tag});
    return LocationTag.fromJson(data);
  }

  /// Revoca una etiqueta de una localización.
  Future<void> revokeLocationTag(int locationId, int tagId) async {
    await request('DELETE', '/locations/$locationId/tags/$tagId');
  }

  /// Obtiene las localizaciones de rodaje de un cortometraje.
  Future<List<FilmLocation>> getFilmLocations(int shortfilmId) async {
    final data = await request('GET', '/shortfilms/$shortfilmId/locations/');
    return (data as List).map((j) => FilmLocation.fromJson(j)).toList();
  }

  /// Añade una localización de rodaje a un cortometraje.
  Future<FilmLocation> addFilmLocation(
      int shortfilmId, Map<String, dynamic> fields) async {
    final data = await create('/shortfilms/$shortfilmId/locations/', fields);
    return FilmLocation.fromJson(data);
  }

  /// Actualiza una localización de rodaje de un cortometraje.
  Future<FilmLocation> updateFilmLocation(
      int shortfilmId, int sflocId, Map<String, dynamic> fields) async {
    final data =
        await _put('/shortfilms/$shortfilmId/locations/$sflocId', fields);
    return FilmLocation.fromJson(data);
  }

  /// Elimina una localización de rodaje de un cortometraje.
  Future<void> removeFilmLocation(int shortfilmId, int sflocId) async {
    await request('DELETE', '/shortfilms/$shortfilmId/locations/$sflocId');
  }

  /// Obtiene las imágenes estructuradas de una localización.
  Future<List<LocationImage>> getLocationImages(int locationId) async {
    final data = await request('GET', '/locations/$locationId/images/');
    return (data as List).map((j) => LocationImage.fromJson(j)).toList();
  }

  /// Añade una imagen de una localización mediante su URL.
  Future<LocationImage> addLocationImageUrl(int locationId, String url) async {
    final data =
        await create('/locations/$locationId/images/url', {'url': url});
    return LocationImage.fromJson(data);
  }

  /// Elimina una imagen de una localización.
  Future<void> removeLocationImage(int locationId, int imageId) async {
    await request('DELETE', '/locations/$locationId/images/$imageId');
  }

  /// Obtiene las relaciones de una localización con otras.
  Future<List<Map<String, dynamic>>> getLocationRelations(
      int locationId) async {
    final data = await request('GET', '/locations/$locationId/relations/');
    return (data as List).map((j) => Map<String, dynamic>.from(j)).toList();
  }

  /// Añade una relación entre dos localizaciones con un tipo dado.
  Future<Map<String, dynamic>> addLocationRelation(
      int locationId, int relatedLocationId, String relationType) async {
    final data = await create('/locations/$locationId/relations/', {
      'related_location_id': relatedLocationId,
      'relation_type': relationType,
    });
    return Map<String, dynamic>.from(data);
  }

  /// Elimina una relación de una localización.
  Future<void> removeLocationRelation(int locationId, int relationId) async {
    await request('DELETE', '/locations/$locationId/relations/$relationId');
  }

  /// Sugiere relaciones de una localización en un radio dado (en km).
  Future<Map<String, dynamic>> suggestLocationRelations(int locationId,
      {double radiusKm = 1.0}) async {
    final data = await request(
        'POST', '/locations/$locationId/relations/suggest?radius_km=$radiusKm');
    return Map<String, dynamic>.from(data);
  }

  /// Actualiza el badge de una localización, o lo elimina si [badge] es `null`.
  Future<Location> updateLocationBadge(int locationId, String? badge) async {
    final params = badge != null ? '?badge=${Uri.encodeComponent(badge)}' : '';
    final data = await request('PUT', '/locations/$locationId/badge$params');
    return Location.fromJson(data);
  }
}

/// Se lanza cuando el backend devuelve 401 Unauthorized.
class UnauthorizedException implements Exception {
  @override
  String toString() => 'Session expired. Please log in again.';
}

/// Error genérico de la API, con código HTTP cuando lo hay.
class ApiException implements Exception {
  final String message;
  final int? statusCode;
  final bool timedOut;
  ApiException(this.message, {this.statusCode, this.timedOut = false});
  @override
  String toString() => message;
}
