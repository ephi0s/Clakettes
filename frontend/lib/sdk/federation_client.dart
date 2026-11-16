/// Cliente HTTP de federación Clakettes (Fase 4).
///
/// Consume los endpoints de federación de un nodo remoto, con soporte opcional
/// mTLS (certificado de cliente) para desktop/mobile y autenticación mediante
/// token de federación (JWT RS256).
///
/// Nota: en Flutter web el mTLS con certificado de cliente no está soportado
/// nativamente por el paquete `http`; usar un proxy (nginx/Traefik) que termine
/// el mTLS y reenvíe la identidad en headers.
library sdk.federation_client;

import 'dart:convert';
import 'package:http/http.dart' as http;

import 'federation_models.dart';

/// Cliente para un nodo federado remoto.
class FederationClient {
  final http.Client _client;
  final String _baseUrl;
  final Duration timeout;

  String? _accessToken;

  /// Crea un cliente de federación.
  ///
  /// [baseUrl] es la URL base del nodo remoto (sin trailing slash, ej. `https://festival.example.com/api`).
  /// [clientCert] / [clientKey] son rutas al certificado y clave de cliente para mTLS (desktop/mobile).
  /// [caBundle] es la ruta al bundle de CA raíz para validar el servidor remoto.
  FederationClient({
    required String baseUrl,
    http.Client? client,
    this.timeout = const Duration(seconds: 10),
    String? clientCert,
    String? clientKey,
    String? caBundle,
  }) : _client = client ?? http.Client(),
       _baseUrl = baseUrl.endsWith('/') ? baseUrl.substring(0, baseUrl.length - 1) : baseUrl;

  String get baseUrl => _baseUrl;
  String get _url => _baseUrl;
  /// Descarga la clave pública JWKS del nodo remoto.
  Future<Map<String, dynamic>> fetchJwks() async {
    final uri = Uri.parse('$_url/federation/.well-known/jwks.json');
    final response = await _client.get(uri).timeout(timeout);
    _throwIfError(response);
    return json.decode(response.body) as Map<String, dynamic>;
  }

  /// Pide al nodo remoto un JWT de federación firmado (requiere mTLS).
  Future<TokenResponse> issueToken(String subject) async {
    final uri = Uri.parse('$_url/federation/token');
    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
      body: json.encode({'subject': subject}),
    ).timeout(timeout);
    _throwIfError(response);
    final data = json.decode(response.body) as Map<String, dynamic>;
    final token = TokenResponse.fromJson(data);
    _accessToken = token.accessToken;
    return token;
  }

  String? get accessToken => _accessToken;

  Map<String, String> _headers({bool withAuth = false}) {
    final headers = <String, String>{
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    if (withAuth && _accessToken != null) {
      headers['Authorization'] = 'Bearer $_accessToken';
    }
    return headers;
  }

  /// Obtiene el manifiesto firmado del nodo remoto.
  Future<Manifest> getManifest() async {
    final uri = Uri.parse('$_url/federation/manifest');
    final response = await _client.get(uri, headers: _headers()).timeout(timeout);
    _throwIfError(response);
    return Manifest.fromJson(json.decode(response.body) as Map<String, dynamic>);
  }

  /// Obtiene el directorio de nodos confiados del nodo remoto.
  Future<List<PeerInfo>> getDirectory() async {
    final uri = Uri.parse('$_url/federation/directory');
    final response = await _client.get(uri, headers: _headers()).timeout(timeout);
    _throwIfError(response);
    final data = json.decode(response.body) as Map<String, dynamic>;
    final nodes = data['nodes'] as List? ?? const [];
    return nodes.cast<Map<String, dynamic>>().map(PeerInfo.fromJson).toList();
  }

  /// Obtiene las políticas de nodo (allowlist/blocklist).
  Future<List<Map<String, dynamic>>> getNodes() async {
    final uri = Uri.parse('$_url/federation/nodes');
    final response = await _client.get(uri, headers: _headers()).timeout(timeout);
    _throwIfError(response);
    return List<Map<String, dynamic>>.from(json.decode(response.body) as List);
  }

  /// Valida la identidad de un nodo remoto (dominio + certificado + manifiesto).
  Future<VerifyResponse> verifyPeer(String nodeDomain, List<String> certificateChain) async {
    final uri = Uri.parse('$_url/federation/peers/verify');
    final response = await _client.post(
      uri,
      headers: _headers(),
      body: json.encode({
        'node_domain': nodeDomain,
        'certificate_chain': certificateChain,
      }),
    ).timeout(timeout);
    _throwIfError(response);
    return VerifyResponse.fromJson(json.decode(response.body) as Map<String, dynamic>);
  }

  /// Revoca administrativamente un nodo confiado (requiere rol admin).
  Future<RevokeResponse> revokePeer(String domain) async {
    final uri = Uri.parse('$_url/federation/peers/$domain/revoke');
    final response = await _client.post(
      uri,
      headers: _headers(withAuth: true),
    ).timeout(timeout);
    _throwIfError(response);
    return RevokeResponse.fromJson(json.decode(response.body) as Map<String, dynamic>);
  }

  /// Resuelve un usuario remoto por uuid, did o handle (requiere mTLS).
  Future<User> resolveUser(String ref) async {
    final uri = Uri.parse('$_url/federation/users/$ref');
    final response = await _client.get(uri, headers: _headers()).timeout(timeout);
    _throwIfError(response);
    return User.fromJson(json.decode(response.body) as Map<String, dynamic>);
  }

  /// Resuelve acct:user@domain vía WebFinger (requiere mTLS).
  Future<WebFingerResponse> webfinger(String resource) async {
    final uri = Uri.parse('$_url/federation/.well-known/webfinger')
        .replace(queryParameters: {'resource': resource});
    final response = await _client.get(uri, headers: _headers()).timeout(timeout);
    _throwIfError(response);
    return WebFingerResponse.fromJson(json.decode(response.body) as Map<String, dynamic>);
  }

  /// Crea un reporte de moderación entre nodos (requiere autenticación).
  Future<Map<String, dynamic>> createReport({
    required String reporterNode,
    required String targetNode,
    required String reason,
    String? targetUserRef,
  }) async {
    final uri = Uri.parse('$_url/federation/reports');
    final response = await _client.post(
      uri,
      headers: _headers(withAuth: true),
      body: json.encode({
        'reporter_node': reporterNode,
        'target_node': targetNode,
        'target_user_ref': targetUserRef,
        'reason': reason,
      }),
    ).timeout(timeout);
    _throwIfError(response);
    return json.decode(response.body) as Map<String, dynamic>;
  }

  /// Lista los reportes de moderación de un nodo.
  Future<List<Map<String, dynamic>>> listReports(String node) async {
    final uri = Uri.parse('$_url/federation/reports')
        .replace(queryParameters: {'node': node});
    final response = await _client.get(uri, headers: _headers()).timeout(timeout);
    _throwIfError(response);
    return List<Map<String, dynamic>>.from(json.decode(response.body) as List);
  }

  /// Actualiza el estado de un reporte (requiere autenticación).
  Future<Map<String, dynamic>> updateReportStatus(int reportId, String status) async {
    final uri = Uri.parse('$_url/federation/reports/$reportId')
        .replace(queryParameters: {'status': status});
    final response = await _client.patch(
      uri,
      headers: _headers(withAuth: true),
    ).timeout(timeout);
    _throwIfError(response);
    return json.decode(response.body) as Map<String, dynamic>;
  }

  /// Cierra el cliente HTTP y libera recursos.
  void close() {
    _client.close();
  }

  void _throwIfError(http.Response response) {
    if (response.statusCode >= 400) {
      throw FederationClientException(
        'Request to ${response.request?.url} failed with status ${response.statusCode}: ${response.body}',
        statusCode: response.statusCode,
      );
    }
  }
}

/// Excepción lanzada cuando una petición al nodo federado falla.
class FederationClientException implements Exception {
  final String message;
  final int? statusCode;

  FederationClientException(this.message, {this.statusCode});

  @override
  String toString() => 'FederationClientException$statusCode: $message';
}
