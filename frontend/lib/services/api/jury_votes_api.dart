part of '../api_service.dart';

extension JuryVotesApi on ApiService {
  /// Emite un voto de jurado para un cortometraje en un festival.
  ///
  /// [score] debe estar entre 0 y 10. [comment] es opcional. [anonymous]
  /// oculta la identidad del jurante en los resultados públicos.
  Future<Map<String, dynamic>> castVote({
    required int festivalId,
    required int shortfilmId,
    required double score,
    String? comment,
    bool anonymous = false,
  }) async {
    final data = await create(
      '/jury-votes/',
      {
        'festival_id': festivalId,
        'shortfilm_id': shortfilmId,
        'score': score,
        'comment': comment,
        'anonymous': anonymous,
      },
    );
    return Map<String, dynamic>.from(data as Map);
  }

  /// Lista los votos emitidos en un festival.
  Future<List<Map<String, dynamic>>> getVotes(int festivalId) async {
    final data = await request('GET', '/jury-votes/$festivalId');
    return List<Map<String, dynamic>>.from(data as List);
  }

  /// Devuelve la agregación de votos por cortometraje (promedio, conteo, scores).
  Future<Map<String, dynamic>> getAggregate(int festivalId) async {
    final data = await request('GET', '/jury-votes/aggregate/$festivalId');
    return Map<String, dynamic>.from(data as Map);
  }

  /// Devuelve los votos anónimos de un festival (solo administrador).
  Future<List<Map<String, dynamic>>> getAnonymousVotes(int festivalId) async {
    final data = await request('GET', '/jury-votes/anonymous/$festivalId');
    return List<Map<String, dynamic>>.from(data as List);
  }
}
