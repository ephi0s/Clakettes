import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:clakettes/services/api_service.dart';
import 'package:clakettes/services/backend_config.dart';

class _CapturingClient extends http.BaseClient {
  http.MultipartRequest? captured;
  final String body;
  final int statusCode;

  _CapturingClient(this.body, this.statusCode);

  @override
  Future<http.StreamedResponse> send(http.BaseRequest request) async {
    captured = request as http.MultipartRequest;
    return http.StreamedResponse(Stream.value(utf8.encode(body)), statusCode);
  }
}

void main() {
  group('PaginatedResult', () {
    test('creates with items, total, and pages', () {
      final result = PaginatedResult<int>(
        items: [1, 2, 3],
        total: 100,
        pages: 5,
      );
      expect(result.items, [1, 2, 3]);
      expect(result.total, 100);
      expect(result.pages, 5);
    });

    test('supports empty items list', () {
      final result = PaginatedResult<String>(
        items: [],
        total: 0,
        pages: 0,
      );
      expect(result.items, isEmpty);
      expect(result.total, 0);
      expect(result.pages, 0);
    });

    test('supports custom object type', () {
      final result = PaginatedResult<Map<String, dynamic>>(
        items: [{'key': 'value'}],
        total: 1,
        pages: 1,
      );
      expect(result.items.first['key'], 'value');
      expect(result.total, 1);
      expect(result.pages, 1);
    });
  });

  group('ApiService singleton', () {
    setUp(() {
      SharedPreferences.setMockInitialValues({});
    });

    test('factory constructor returns same instance', () {
      final a = ApiService();
      final b = ApiService();
      expect(identical(a, b), isTrue);
    });

    test('setClient replaces http client', () {
      final api = ApiService();
      final original = api.client;
      api.setClient(http.Client());
      expect(identical(api.client, original), isFalse);
    });

    test('reset restores default client', () {
      final api = ApiService();
      api.setClient(http.Client());
      api.reset();
      expect(api.client, isNotNull);
    });

    test('has default baseUrl', () {
      final api = ApiService();
      expect(api.baseUrl, '${BackendConfig.platformDefaultUrl}/api');
    });

    test('client is not null', () {
      final api = ApiService();
      expect(api.client, isNotNull);
    });

    test('rootUrl returns default before setBaseUrl', () {
      final api = ApiService();
      expect(api.rootUrl, BackendConfig.platformDefaultUrl);
      expect(api.baseUrl, '${BackendConfig.platformDefaultUrl}/api');
    });

    test('setBaseUrl after first use does not throw LateInitializationError', () {
      final api = ApiService();
      expect(api.rootUrl, isNotEmpty);
      expect(api.baseUrl, isNotEmpty);
      expect(() => api.setBaseUrl('http://192.168.1.100:8000'), returnsNormally);
      expect(api.rootUrl, 'http://192.168.1.100:8000');
      expect(api.baseUrl, 'http://192.168.1.100:8000/api');
      api.setBaseUrl(BackendConfig.platformDefaultUrl);
    });
  });

  group('media URLs', () {
    test('resolveMediaUrl keeps absolute URLs and prefixes relative paths', () {
      expect(resolveMediaUrl('https://example.com/a.png'), 'https://example.com/a.png');
      final resolved = resolveMediaUrl('/uploads/a.png');
      expect(resolved, endsWith('/uploads/a.png'));
      expect(resolved.startsWith('http'), isTrue);
      expect(resolveMediaUrl(null), '');
    });

    test('uploadFile sends the MIME type matching the file extension', () async {
      SharedPreferences.setMockInitialValues({});
      final api = ApiService();
      final client = _CapturingClient('{"url":"/uploads/avatars/a.png"}', 200);
      api.setClient(client);
      final file = XFile.fromData(Uint8List.fromList([1, 2, 3]), path: '/tmp/pixel.png');
      final data = await api.uploadFile('/uploads/avatar', file);
      expect(data['url'], '/uploads/avatars/a.png');
      expect(client.captured!.files.single.contentType.mimeType, 'image/png');
      expect(client.captured!.files.single.filename, 'pixel.png');
      api.reset();
    });

    test('uploadFile propagates the server error detail', () async {
      SharedPreferences.setMockInitialValues({});
      final api = ApiService();
      final client = _CapturingClient('{"detail":"File type not allowed"}', 400);
      api.setClient(client);
      final file = XFile.fromData(Uint8List.fromList([1, 2, 3]), path: '/tmp/pixel.png');
      await expectLater(
        api.uploadFile('/uploads/avatar', file),
        throwsA(isA<ApiException>().having((e) => e.detail, 'detail', 'File type not allowed')),
      );
      api.reset();
    });
  });

  group('UnauthorizedException', () {
    test('toString returns expected message', () {
      final ex = UnauthorizedException();
      expect(ex.toString(), 'Session expired. Please log in again.');
    });

    test('implements Exception', () {
      final ex = UnauthorizedException();
      expect(ex, isA<Exception>());
    });
  });

  group('ApiException', () {
    test('stores message', () {
      final ex = ApiException('Something went wrong');
      expect(ex.message, 'Something went wrong');
    });

    test('toString returns message', () {
      final ex = ApiException('Not found');
      expect(ex.toString(), 'Not found');
    });

    test('supports empty message', () {
      final ex = ApiException('');
      expect(ex.message, '');
      expect(ex.toString(), '');
    });

    test('implements Exception', () {
      final ex = ApiException('error');
      expect(ex, isA<Exception>());
    });
  });
}
