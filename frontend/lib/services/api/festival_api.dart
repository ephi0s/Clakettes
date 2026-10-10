part of '../api_service.dart';

extension FestivalApi on ApiService {
  Future<PaginatedResult<Festival>> getFestivals({
    int page = 1,
    int size = 20,
    bool? isActive,
  }) async {
    final params = <String, String>{'page': '$page', 'size': '$size'};
    if (isActive != null) params['is_active'] = '$isActive';
    final data = await _get('/festivals/', params);
    return _paginated(data, Festival.fromJson);
  }

  /// Lista los roles asignables del festival, para los selectores de la interfaz.
  Future<List<RoleSummary>> getFestivalRoles(int festivalId,
      {int size = 100}) async {
    final data = await _get(
        '/festivals/$festivalId/roles/', {'page': '1', 'size': '$size'});
    final items = (data as Map)['items'] as List? ?? const [];
    return items
        .map((j) => RoleSummary.fromJson(Map<String, dynamic>.from(j as Map)))
        .where((role) => role.isActive)
        .toList();
  }

  Future<Festival> createFestival(Festival festival) async {
    final data = await create('/festivals/', festival.toJson());
    return Festival.fromJson(data);
  }

  Future<Festival> getFestival(int id) async {
    final data = await request('GET', '/festivals/$id');
    return Festival.fromJson(data);
  }

  Future<Festival> updateFestival(int id, Map<String, dynamic> fields) async {
    final data = await _put('/festivals/$id', fields);
    return Festival.fromJson(data);
  }

  Future<void> deleteFestival(int id) async {
    await request('DELETE', '/festivals/$id');
  }

  Future<Festival> uploadFestivalImage(int festivalId, String filePath) async {
    final data = await _uploadFile('/festivals/$festivalId/images', filePath,
        errorLabel: 'Festival image');
    return Festival.fromJson(data);
  }

  Future<Festival> deleteFestivalImage(int festivalId, String imageUrl) async {
    final data = await request('DELETE',
        '/festivals/$festivalId/images?url=${Uri.encodeComponent(imageUrl)}');
    return Festival.fromJson(data);
  }
}
