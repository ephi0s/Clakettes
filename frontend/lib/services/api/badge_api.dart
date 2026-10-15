part of '../api_service.dart';

extension BadgeApi on ApiService {
  Future<bool> getBadgesEnabled() async {
    final data = await request('GET', '/badges/status', withAuth: false);
    return (data as Map<String, dynamic>)['enabled'] == true;
  }

  Future<bool> setBadgesEnabled(bool enabled) async {
    final data = await _put('/badges/settings', {'enabled': enabled});
    return (data as Map<String, dynamic>)['enabled'] == true;
  }

  Future<PaginatedResult<ProfileBadge>> getBadges({int page = 1, int size = 50, String? scope}) async {
    final params = <String, String>{'page': '$page', 'size': '$size'};
    if (scope != null) params['scope'] = scope;
    final data = await _get('/badges/', params);
    return _paginated(data, ProfileBadge.fromJson);
  }

  Future<ProfileBadge> createBadge(Map<String, dynamic> fields) async {
    final data = await create('/badges/', fields);
    return ProfileBadge.fromJson(data);
  }

  Future<ProfileBadge> updateBadge(int id, Map<String, dynamic> fields) async {
    final data = await _put('/badges/$id', fields);
    return ProfileBadge.fromJson(data);
  }

  Future<void> deleteBadge(int id) async {
    await request('DELETE', '/badges/$id');
  }

  Future<ProfileBadge> uploadBadgeImage(int id, String filePath) async {
    final uri = Uri.parse('$baseUrl/badges/$id/image');
    final token = await _auth.getToken();
    final req = http.MultipartRequest('POST', uri);
    if (token != null) req.headers['Authorization'] = 'Bearer $token';
    req.files.add(await http.MultipartFile.fromPath('file', filePath));
    late http.Response response;
    try {
      final streamed = await req.send();
      response = await http.Response.fromStream(streamed);
    } catch (_) {
      throw ApiException('Network error (upload)');
    }
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return ProfileBadge.fromJson(json.decode(response.body));
    }
    throw ApiException('Badge image upload failed (${response.statusCode})', statusCode: response.statusCode);
  }

  Future<BadgeAssignment> assignBadge(int badgeId, Map<String, dynamic> fields) async {
    final data = await create('/badges/$badgeId/assign', fields);
    return BadgeAssignment.fromJson(data);
  }

  Future<Map<String, dynamic>> checkBadgeEligibility(int badgeId, int userId) async {
    final data = await _get('/badges/$badgeId/eligibility', {'user_id': '$userId'});
    return Map<String, dynamic>.from(data as Map);
  }

  Future<void> deleteBadgeAssignment(int assignmentId) async {
    await request('DELETE', '/badge-assignments/$assignmentId');
  }

  Future<PaginatedResult<BadgeAssignment>> getUserBadges(int userId, {int page = 1, int size = 50}) async {
    final data = await _get('/users/$userId/badges/', {'page': '$page', 'size': '$size'});
    return _paginated(data, BadgeAssignment.fromJson);
  }

  Future<PaginatedResult<BadgeAssignment>> getFestivalBadges(int festivalId,
      {int page = 1, int size = 50}) async {
    final data = await _get('/festivals/$festivalId/badges/', {'page': '$page', 'size': '$size'});
    return _paginated(data, BadgeAssignment.fromJson);
  }
}
