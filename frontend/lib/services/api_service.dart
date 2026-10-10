import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../models/festival_model.dart';
import '../models/user_model.dart';
import '../models/shortfilm_model.dart';
import '../models/message_model.dart';
import '../models/notification_model.dart';
import '../models/role_group_model.dart';
import '../models/committee_model.dart';
import '../models/role_delegation_model.dart';
import '../models/role_transition_model.dart';
import '../models/registration_form_model.dart';
import '../models/event_model.dart';
import '../models/award_model.dart';
import '../models/user_alias_model.dart';
import '../models/session_model.dart';
import '../models/location_model.dart';
import '../models/location_tag_model.dart';
import '../models/location_image_model.dart';
import '../models/film_location_model.dart';
import '../models/form_definition_model.dart';
import '../models/calendar_model.dart';
import '../models/payment_model.dart';
import '../models/role_model.dart';
import '../models/festival_rulebook_model.dart';
import 'backend_config.dart';
import 'auth_service.dart';

part 'api/festival_api.dart';
part 'api/user_api.dart';
part 'api/channel_api.dart';
part 'api/form_api.dart';
part 'api/calendar_api.dart';
part 'api/catalog_api.dart';
part 'api/org_api.dart';
part 'api/event_api.dart';
part 'api/location_api.dart';

/// Envoltorio de respuesta paginada que coincide con el envelope del backend.
class PaginatedResult<T> {
  final List<T> items;
  final int total;
  final int pages;

  PaginatedResult(
      {required this.items, required this.total, required this.pages});
}

/// Cliente HTTP que envuelve todas las llamadas a la API del backend (patrón singleton).
///
/// Responsabilidades:
/// - Inyección del header de autenticación JWT mediante AuthService
/// - Gestión de parámetros de paginación (page, size)
/// - Serialización/deserialización JSON
/// - Gestión de errores y timeouts
/// - Configuración de la URL base (compile-time + override en runtime mediante setBaseUrl)
///
/// Uso: ApiService().getFestivals(page: 1, size: 20)
///
/// Nota: 1285 líneas — considera dividirlo en clientes específicos por dominio
/// (UserApi, FestivalApi, ChannelApi, etc.) para mantenerlo.
/// TODO(E26): deuda modularizacion — plan en lib/services/api/README.md; ref. lib/services/api/festival_api.dart
class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;

  /// Cliente HTTP subyacente.
  http.Client client;
  String? _rootUrl;
  String? _baseUrl;
  final AuthService _auth;

  ApiService._internal()
      : client = http.Client(),
        _auth = AuthService() {
    _rootUrl = BackendConfig.compileTimeUrl != BackendConfig.defaultUrl
        ? BackendConfig.compileTimeUrl
        : BackendConfig.platformDefaultUrl;
    _baseUrl = '$_rootUrl/api';
  }

  /// URL raíz del backend (sin el prefijo `/api`).
  String get rootUrl => _rootUrl ?? BackendConfig.platformDefaultUrl;

  /// URL base del backend con el prefijo `/api`.
  String get baseUrl => _baseUrl ?? '${BackendConfig.platformDefaultUrl}/api';

  /// Sustituye el cliente HTTP (útil para tests).
  void setClient(http.Client newClient) {
    client = newClient;
  }

  /// Cierra el cliente actual y crea uno nuevo.
  void reset() {
    client.close();
    client = http.Client();
  }

  /// Actualiza la URL base en runtime (p. ej., desde la pantalla de configuración del backend).
  void setBaseUrl(String url) {
    _rootUrl = url;
    _baseUrl = '$url/api';
  }

  Map<String, String> get _jsonHeaders => {
        'Content-Type': 'application/json',
      };

  Future<Map<String, String>> get _authHeaders async {
    final token = await _auth.getToken();
    if (token == null) return _jsonHeaders;
    return {
      ..._jsonHeaders,
      'Authorization': 'Bearer $token',
    };
  }

  /// Devuelve `true` si el backend es accesible.
  Future<bool> healthCheck() async {
    try {
      final uri = Uri.parse('$rootUrl/health');
      final response =
          await client.get(uri).timeout(const Duration(seconds: 5));
      return response.statusCode == 200;
    } catch (e) {
      debugPrint('Error: $e');
      return false;
    }
  }

  /// Libera el cliente HTTP para liberar recursos.
  void dispose() {
    client.close();
  }

  /// Decodifica el cuerpo de la respuesta y extrae la lista de items paginados.
  List<dynamic> _extractItems(dynamic decoded) {
    if (decoded is List) return decoded;
    if (decoded is Map && decoded.containsKey('items')) {
      return List<dynamic>.from(decoded['items']);
    }
    return [];
  }

  int _extractTotal(dynamic decoded) {
    if (decoded is Map && decoded.containsKey('total')) {
      final v = decoded['total'];
      if (v is int) return v;
      if (v is num) return v.toInt();
      return int.tryParse(v?.toString() ?? '') ?? 0;
    }
    return 0;
  }

  int _extractPages(dynamic decoded) {
    if (decoded is Map && decoded.containsKey('pages')) {
      final v = decoded['pages'];
      if (v is int) return v;
      if (v is num) return v.toInt();
      return int.tryParse(v?.toString() ?? '') ?? 0;
    }
    return 0;
  }

  /// Construye una cadena de consulta a partir de [params], o '' cuando está vacía.
  String _buildQuery([Map<String, String>? params]) {
    if (params == null || params.isEmpty) return '';
    return Uri(queryParameters: params).query;
  }

  /// GET [path] (relativo a [baseUrl]) con [params] de consulta opcionales.
  Future<dynamic> _get(String path, [Map<String, String>? params]) {
    final query = _buildQuery(params);
    return request('GET', query.isEmpty ? path : '$path?$query');
  }

  /// PUT de [fields] (codificados en JSON) a [path].
  Future<dynamic> _put(String path, Map<String, dynamic> fields) {
    return request('PUT', path, body: json.encode(fields));
  }

  /// Construye un [PaginatedResult] a partir de una respuesta paginada decodificada.
  PaginatedResult<T> _paginated<T>(
      dynamic data, T Function(Map<String, dynamic>) fromJson) {
    return PaginatedResult<T>(
      items: _extractItems(data).map((j) => fromJson(j)).toList(),
      total: _extractTotal(data),
      pages: _extractPages(data),
    );
  }

  /// Sube [filePath] mediante multipart POST a [path]; devuelve el cuerpo JSON
  /// decodificado y lanza [ApiException] en respuestas no 2xx.
  Future<dynamic> _uploadFile(String path, String filePath,
      {String? errorLabel}) async {
    final uri = Uri.parse('$baseUrl$path');
    final token = await _auth.getToken();
    final request = http.MultipartRequest('POST', uri);
    if (token != null) {
      request.headers['Authorization'] = 'Bearer $token';
    }
    request.files.add(await http.MultipartFile.fromPath('file', filePath));
    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return json.decode(response.body);
    }
    throw ApiException(
        '${errorLabel ?? 'Upload'} failed (${response.statusCode})');
  }

  /// Ejecuta una petición HTTP contra el backend.
  ///
  /// [method] es GET, POST, PUT o DELETE. [path] es relativo a [baseUrl]
  /// (p. ej. `/festivals/`). Devuelve el cuerpo JSON decodificado, o `null` para 204.
  /// Ante un 401, intenta automáticamente un refresh de token una vez antes de fallar.
  Future<dynamic> request(
    String method,
    String path, {
    Object? body,
    bool withAuth = true,
  }) async {
    final uri = Uri.parse('$baseUrl$path');

    for (int attempt = 0; attempt < 2; attempt++) {
      final headers = withAuth ? await _authHeaders : _jsonHeaders;
      late http.Response response;

      try {
        switch (method) {
          case 'GET':
            response = await client
                .get(uri, headers: withAuth ? headers : null)
                .timeout(const Duration(seconds: 10));
            break;
          case 'POST':
            response = await client
                .post(uri, headers: headers, body: body)
                .timeout(const Duration(seconds: 10));
            break;
          case 'PUT':
            response = await client
                .put(uri, headers: headers, body: body)
                .timeout(const Duration(seconds: 10));
            break;
          case 'DELETE':
            response = await client
                .delete(uri, headers: withAuth ? headers : null)
                .timeout(const Duration(seconds: 10));
            break;
        }
      } on TimeoutException {
        throw ApiException('$method $path timed out');
      }

      if (response.statusCode == 401 && attempt == 0 && withAuth) {
        final refreshed = await refreshToken();
        if (refreshed) continue;
        await _auth.clear();
        throw UnauthorizedException();
      }

      if (response.statusCode >= 200 && response.statusCode < 300) {
        if (response.body.isEmpty) return null;
        return json.decode(response.body);
      }

      throw ApiException('$method $path failed (${response.statusCode})');
    }

    throw ApiException('$method $path failed (unexpected)');
  }

  /// Descarga los bytes de una respuesta autenticada sin decodificar JSON.
  ///
  /// [path] es relativo a [baseUrl] (p. ej. `/festivals/1/events/export/ics`),
  /// opcionalmente con [params] de consulta. Devuelve los bytes crudos de la
  /// respuesta. Ante un 401 intenta refrescar el token una vez antes de fallar.
  Future<Uint8List> getBytes(String path, [Map<String, String>? params]) async {
    final query = _buildQuery(params);
    final uri = Uri.parse('$baseUrl${query.isEmpty ? path : '$path?$query'}');

    for (int attempt = 0; attempt < 2; attempt++) {
      final token = await _auth.getToken();
      final headers = token != null ? {'Authorization': 'Bearer $token'} : null;
      late http.Response response;

      try {
        response = await client
            .get(uri, headers: headers)
            .timeout(const Duration(seconds: 30));
      } on TimeoutException {
        throw ApiException('GET $path timed out');
      }

      if (response.statusCode == 401 && attempt == 0) {
        final refreshed = await refreshToken();
        if (refreshed) continue;
        await _auth.clear();
        throw UnauthorizedException();
      }

      if (response.statusCode >= 200 && response.statusCode < 300) {
        return response.bodyBytes;
      }

      throw ApiException('GET $path failed (${response.statusCode})');
    }

    throw ApiException('GET $path failed (unexpected)');
  }

  /// Envía una petición POST a [path] con [body], devolviendo el JSON decodificado.
  Future<dynamic> create(String path, Object body) async {
    return request('POST', path, body: json.encode(body));
  }

  // ---------------------------------------------------------------------------
  // Auth
  // ---------------------------------------------------------------------------

  /// Inicia sesión con [username] y [password], guardando los tokens y el [User] autenticado.
  Future<User> login(String username, String password,
      {String? deviceName}) async {
    final data = await request(
      'POST',
      '/users/login',
      body: json.encode({
        'username': username,
        'password': password,
        'device_name': deviceName ?? 'Clakettes App',
      }),
      withAuth: false,
    );
    await _auth.saveToken(data['access_token']);
    if (data['refresh_token'] != null) {
      await _auth.saveRefreshToken(data['refresh_token']);
    }
    final user = User.fromJson(data['user']);
    await _auth.saveUser(user);
    return user;
  }

  Future<bool>? _refreshInFlight;

  /// Renueva el token de acceso usando el refresh token almacenado.
  ///
  /// Single-flight: los 401 concurrentes comparten un único refresh para que la
  /// rotación de tokens del backend nunca termine en un falso "sesión expirada".
  Future<bool> refreshToken() {
    return _refreshInFlight ??= _performRefresh().whenComplete(() {
      _refreshInFlight = null;
    });
  }

  Future<bool> _performRefresh() async {
    final refreshToken = await _auth.getRefreshToken();
    if (refreshToken == null) return false;
    try {
      final data = await request(
        'POST',
        '/auth/refresh',
        body: json.encode({'refresh_token': refreshToken}),
        withAuth: false,
      );
      await _auth.saveToken(data['access_token']);
      if (data['refresh_token'] != null) {
        await _auth.saveRefreshToken(data['refresh_token']);
      }
      return true;
    } catch (e) {
      debugPrint('Error: $e');
      return false;
    }
  }

  // ---------------------------------------------------------------------------
  // Short Films
  // ---------------------------------------------------------------------------

  // ---------------------------------------------------------------------------
  // Search
  // ---------------------------------------------------------------------------

  /// Realiza una búsqueda global en el backend.
  Future<Map<String, dynamic>> search(String query,
      {String type = 'all'}) async {
    final params = <String, String>{'q': query, 'type': type};
    return await request('GET', '/search/?${_buildQuery(params)}',
        withAuth: false);
  }

  // ---------------------------------------------------------------------------
  // Admin
  // ---------------------------------------------------------------------------

  /// Obtiene estadísticas globales para el panel de administración.
  Future<Map<String, dynamic>> getAdminStats() async {
    return await request('GET', '/admin/stats');
  }

  /// Obtiene el recuento de filas de las tablas para el panel de administración.
  Future<Map<String, dynamic>> getAdminTables() async {
    return await request('GET', '/admin/tables');
  }

  // ---------------------------------------------------------------------------
  // Notifications
  // ---------------------------------------------------------------------------

  // ---------------------------------------------------------------------------
  // Role Groups
  // ---------------------------------------------------------------------------

  // ---------------------------------------------------------------------------
  // Committees
  // ---------------------------------------------------------------------------

  // ---------------------------------------------------------------------------
  // Delegations
  // ---------------------------------------------------------------------------

  // ---------------------------------------------------------------------------
  // Role Transitions
  // ---------------------------------------------------------------------------

  // ---------------------------------------------------------------------------
  // Events
  // ---------------------------------------------------------------------------

  // ---------------------------------------------------------------------------
  // Event Tickets
  // ---------------------------------------------------------------------------

  // ---------------------------------------------------------------------------
  // Event Seats
  // ---------------------------------------------------------------------------

  // ---------------------------------------------------------------------------
  // Event Reservations
  // ---------------------------------------------------------------------------

  // ---------------------------------------------------------------------------
  // Awards
  // ---------------------------------------------------------------------------

  // ---------------------------------------------------------------------------
  // Festival rulebooks (bases)
  // ---------------------------------------------------------------------------

  // ---------------------------------------------------------------------------
  // Aliases
  // ---------------------------------------------------------------------------

  /// Obtiene los alias paginados de un usuario, con filtro opcional de contexto.
  Future<PaginatedResult<UserAlias>> getUserAliases(int userId,
      {int page = 1, int size = 20, String? context}) async {
    final params = <String, String>{'page': '$page', 'size': '$size'};
    if (context != null) params['context'] = context;
    final data = await _get('/users/$userId/aliases/', params);
    return _paginated(data, UserAlias.fromJson);
  }

  /// Crea un alias para un usuario y devuelve el [UserAlias] creado.
  Future<UserAlias> createUserAlias(int userId, UserAlias a) async {
    final data = await create('/users/$userId/aliases/', a.toJson());
    return UserAlias.fromJson(data);
  }

  /// Actualiza los campos indicados de un alias de usuario.
  Future<UserAlias> updateUserAlias(
      int userId, int aliasId, Map<String, dynamic> fields) async {
    final data = await _put('/users/$userId/aliases/$aliasId', fields);
    return UserAlias.fromJson(data);
  }

  /// Elimina un alias de usuario.
  Future<void> deleteUserAlias(int userId, int aliasId) async {
    await request('DELETE', '/users/$userId/aliases/$aliasId');
  }

  // ---------------------------------------------------------------------------
  // Festival User Profile (public alias-aware)
  // ---------------------------------------------------------------------------

  // ---------------------------------------------------------------------------
  // Locations
  // ---------------------------------------------------------------------------

  // ---------------------------------------------------------------------------
  // Location Tags
  // ---------------------------------------------------------------------------

  // ---------------------------------------------------------------------------
  // Film Locations
  // ---------------------------------------------------------------------------

  // ---------------------------------------------------------------------------
  // Location Images (structured)
  // ---------------------------------------------------------------------------

  // ---------------------------------------------------------------------------
  // Location Relations
  // ---------------------------------------------------------------------------

  // ---------------------------------------------------------------------------
  // Location Badge
  // ---------------------------------------------------------------------------
}
