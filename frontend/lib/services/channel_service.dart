import 'package:flutter/foundation.dart';
import '../models/channel_model.dart';
import 'api_service.dart';

/// Wrapper de la API del frontend para los endpoints de canales y claves E2EE.
class ChannelApiService {
  final ApiService _api;

  /// Crea un wrapper alrededor de [api]; por defecto usa un [ApiService] nuevo.
  ChannelApiService({ApiService? api}) : _api = api ?? ApiService();

  // -- Channels ---------------------------------------------------------------

  /// Obtiene los canales del usuario actual con paginación estilo cursor.
  ///
  /// [page] es el número de página (empezando en 1) y [size] el tamaño de página.
  /// Devuelve la lista de [Channel] parseada; admite respuestas paginadas y
  /// listas planas de la API.
  Future<List<Channel>> getMyChannels({int page = 1, int size = 20}) async {
    final data = await _api.request('GET', '/channels/?page=$page&size=$size');
    final items = (data is Map && data.containsKey('items')) ? List<dynamic>.from(data['items']) : (data is List ? data : []);
    return items.map((j) => Channel.fromJson(Map<String, dynamic>.from(j))).toList();
  }

  /// Crea un canal y devuelve el [Channel] creado.
  ///
  /// [name] es obligatorio; [description], [channelType] (por defecto `community`)
  /// y [maxMembers] son opcionales.
  Future<Channel> createChannel({
    required String name,
    String? description,
    String channelType = 'community',
    int? maxMembers,
  }) async {
    final body = <String, dynamic>{
      'name': name,
      'channel_type': channelType,
    };
    if (description != null) body['description'] = description;
    if (maxMembers != null) body['max_members'] = maxMembers;
    final data = await _api.create('/channels/', body);
    return Channel.fromJson(data);
  }

  /// Obtiene un único canal por su id.
  Future<Channel> getChannel(int channelId) async {
    final data = await _api.request('GET', '/channels/$channelId');
    return Channel.fromJson(data);
  }

  /// Obtiene los miembros de [channelId].
  Future<List<ChannelMember>> getChannelMembers(int channelId) async {
    final data = await _api.request('GET', '/channels/$channelId/members');
    return (data as List).map((j) => ChannelMember.fromJson(Map<String, dynamic>.from(j))).toList();
  }

  /// Añade a [userId] como miembro de [channelId] con un [role] opcional.
  Future<void> addMember(int channelId, int userId, {String role = 'member'}) async {
    await _api.create('/channels/$channelId/members', {'user_id': userId, 'role': role});
  }

  /// Elimina a [userId] de [channelId].
  Future<void> removeMember(int channelId, int userId) async {
    await _api.request('DELETE', '/channels/$channelId/members/$userId');
  }

  // -- E2EE keys --------------------------------------------------------------

  /// Sube la clave pública X25519 (base64) del llamante para E2EE.
  Future<void> uploadPublicKey(String publicKeyBase64) async {
    await _api.create('/users/me/public-key', {'public_key_x25519': publicKeyBase64});
  }

  /// Obtiene la clave pública X25519 (base64) de [userId].
  ///
  /// Devuelve `null` si la petición falla o el usuario no tiene clave.
  Future<String?> getPublicKey(int userId) async {
    try {
      final data = await _api.request('GET', '/users/$userId/public-key');
      return data['public_key_x25519'] as String?;
    } catch (e) {
      debugPrint('Error: $e');
      return null;
    }
  }
}
