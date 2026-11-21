import 'dart:convert';

import 'package:crypto/crypto.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hive/hive.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:clakettes/services/offline_cache_service.dart';

void main() {
  setUp(() async {
    SharedPreferences.setMockInitialValues({});
    Hive.init('.');
    await Hive.deleteBoxFromDisk('offline_cache');
    await Hive.deleteBoxFromDisk('cache_meta');
  });

  group('OfflineCacheService', () {
    test('singleton returns same instance', () {
      final a = OfflineCacheService.instance;
      final b = OfflineCacheService.instance;
      expect(identical(a, b), isTrue);
    });

    test('init opens boxes and generates HMAC secret', () async {
      final cache = OfflineCacheService.instance;
      await cache.init();
      final prefs = await SharedPreferences.getInstance();
      final secret = prefs.getString('cache_hmac_secret');
      expect(secret, isNotNull);
      expect(secret!.length, greaterThanOrEqualTo(16));
    });

    test('put and get round-trip', () async {
      final cache = OfflineCacheService.instance;
      await cache.init();
      final data = {'name': 'Test Festival', 'id': 1};
      await cache.put('festival', data);
      final result = cache.get('festival');
      expect(result, isNotNull);
      expect(result['name'], 'Test Festival');
      expect(result['id'], 1);
    });

    test('get returns null for missing key', () async {
      final cache = OfflineCacheService.instance;
      await cache.init();
      final result = cache.get('nonexistent');
      expect(result, isNull);
    });

    test('detects tampered data', () async {
      final cache = OfflineCacheService.instance;
      await cache.init();
      await cache.put('festival', {'name': 'Original', 'id': 1});
      final box = await Hive.openBox('offline_cache');
      final raw = box.get('festival');
      raw['data'] = '{"name":"Tampered","id":1}';
      await box.put('festival', raw);
      final result = cache.get('festival');
      expect(result, isNull);
    });

    test('remove deletes entry', () async {
      final cache = OfflineCacheService.instance;
      await cache.init();
      await cache.put('festival', {'name': 'Test', 'id': 1});
      await cache.remove('festival');
      expect(cache.get('festival'), isNull);
    });

    test('has returns true when entry exists', () async {
      final cache = OfflineCacheService.instance;
      await cache.init();
      await cache.put('festival', {'name': 'Test', 'id': 1});
      expect(cache.has('festival'), isTrue);
    });

    test('has returns false when entry missing', () async {
      final cache = OfflineCacheService.instance;
      await cache.init();
      expect(cache.has('ghost'), isFalse);
    });

    test('getTimestamp returns milliseconds', () async {
      final cache = OfflineCacheService.instance;
      await cache.init();
      await cache.put('festival', {'name': 'Test', 'id': 1});
      final ts = cache.getTimestamp('festival');
      expect(ts, isNotNull);
      expect(ts, greaterThan(0));
    });

    test('getTimestamp returns null for missing entry', () async {
      final cache = OfflineCacheService.instance;
      await cache.init();
      expect(cache.getTimestamp('ghost'), isNull);
    });

    test('clear wipes all boxes', () async {
      final cache = OfflineCacheService.instance;
      await cache.init();
      await cache.put('festival', {'name': 'F1', 'id': 1});
      await cache.put('user', {'username': 'u', 'email': 'u@t.com', 'id': 1});
      await cache.clear();
      expect(cache.has('festival'), isFalse);
      expect(cache.has('user'), isFalse);
    });

    test('validates festival schema', () async {
      final cache = OfflineCacheService.instance;
      await cache.init();
      await cache.put('festival', {'id': 1});
      final result = cache.get('festival');
      expect(result, isNull);
    });

    test('validates user role against whitelist', () async {
      final cache = OfflineCacheService.instance;
      await cache.init();
      await cache.put('user', {
        'id': 1,
        'username': 'hacker',
        'email': 'h@t.com',
        'role': 'superadmin',
      });
      final result = cache.get('user');
      expect(result, isNull);
    });

    test('rejects negative id', () async {
      final cache = OfflineCacheService.instance;
      await cache.init();
      await cache.put('festival', {'id': -1, 'name': 'Bad'});
      final result = cache.get('festival');
      expect(result, isNull);
    });

    test('validates message schema', () async {
      final cache = OfflineCacheService.instance;
      await cache.init();
      await cache.put('message', {'id': 1});
      final result = cache.get('message');
      expect(result, isNull);
    });

    test('validates shortfilm schema', () async {
      final cache = OfflineCacheService.instance;
      await cache.init();
      await cache.put('shortfilm', {'id': 1, 'title': 'Film'});
      final result = cache.get('shortfilm');
      expect(result, isNull);
    });

    test('rejects unknown entity type', () async {
      final cache = OfflineCacheService.instance;
      await cache.init();
      await cache.put('unknown', {'id': 1});
      final result = cache.get('unknown');
      expect(result, isNull);
    });

    test('validates list of entities', () async {
      final cache = OfflineCacheService.instance;
      await cache.init();
      await cache.put('festival', [
        {'id': 1, 'name': 'Good'},
        {'id': 2},
        {'id': 3, 'name': 'Also Good'},
      ]);
      final result = cache.get('festival');
      expect(result, isNull);
    });

    test('valid valid list passes', () async {
      final cache = OfflineCacheService.instance;
      await cache.init();
      final festivals = [
        {'id': 1, 'name': 'F1'},
        {'id': 2, 'name': 'F2'},
      ];
      await cache.put('festival', festivals);
      final result = cache.get('festival');
      expect(result, isNotNull);
      expect(result.length, 2);
    });

    test('putWithOrigin tags entry and exposes origin APIs', () async {
      final cache = OfflineCacheService.instance;
      await cache.init();
      await cache.putWithOrigin('festival', {'id': 1, 'name': 'Node F'}, 'node-a');
      expect(cache.getOrigin('festival'), 'node-a');
      final envelope = cache.getEnvelope('festival');
      expect(envelope, isNotNull);
      expect(envelope!['node_origin'], 'node-a');
      expect(envelope['timestamp'], isA<int>());
      expect(envelope['data'], {'id': 1, 'name': 'Node F'});
      expect(cache.listOrigins(), {'festival': 'node-a'});
    });

    test('put uses empty origin', () async {
      final cache = OfflineCacheService.instance;
      await cache.init();
      await cache.put('festival', {'id': 1, 'name': 'Local'});
      expect(cache.getOrigin('festival'), '');
      expect(cache.listOrigins(), {'festival': ''});
    });

    test('detects node_origin tampering', () async {
      final cache = OfflineCacheService.instance;
      await cache.init();
      await cache.putWithOrigin('festival', {'id': 1, 'name': 'Original'}, 'node-a');
      final box = await Hive.openBox('offline_cache');
      final raw = box.get('festival');
      raw['node_origin'] = 'attacker';
      await box.put('festival', raw);
      expect(cache.get('festival'), isNull);
      expect(cache.getOrigin('festival'), isNull);
    });

    test('legacy entry without node origin stays readable', () async {
      final cache = OfflineCacheService.instance;
      await cache.init();
      final prefs = await SharedPreferences.getInstance();
      final secret = prefs.getString('cache_hmac_secret')!;
      final data = {'id': 1, 'name': 'Legacy'};
      final jsonStr = json.encode(data);
      final signature = base64Url.encode(
        Hmac(sha256, utf8.encode(secret)).convert(utf8.encode(jsonStr)).bytes,
      );
      final box = await Hive.openBox('offline_cache');
      await box.put('festival', {
        'data': jsonStr,
        'signature': signature,
        'timestamp': DateTime.now().millisecondsSinceEpoch,
      });
      expect(cache.get('festival')['name'], 'Legacy');
      expect(cache.getOrigin('festival'), isNull);
    });

    test('clearOrigin removes only entries from that node', () async {
      final cache = OfflineCacheService.instance;
      await cache.init();
      await cache.putWithOrigin('festival', {'id': 1, 'name': 'A'}, 'node-a');
      await cache.putWithOrigin('user', {'id': 1, 'username': 'u', 'email': 'u@t.com'}, 'node-b');
      await cache.clearOrigin('node-a');
      expect(cache.get('festival'), isNull);
      expect(cache.get('user'), isNotNull);
      expect(cache.listOrigins(), {'user': 'node-b'});
    });

    test('reconcile uses remote when no local entry', () async {
      final cache = OfflineCacheService.instance;
      await cache.init();
      final remote = {'id': 1, 'name': 'Remote'};
      final result = cache.reconcile('festival', remote, 'node-b');
      expect(result['action'], 'use_remote');
      expect(result['data'], remote);
      expect(result['origin'], 'node-b');
    });

    test('reconcile same origin keeps newer timestamp', () async {
      final cache = OfflineCacheService.instance;
      await cache.init();
      final local = {'id': 1, 'name': 'Local'};
      final remote = {'id': 1, 'name': 'Remote'};
      await cache.putWithOrigin('festival', local, 'node-a');
      final localTs = cache.getTimestamp('festival')!;

      final localWins =
          cache.reconcile('festival', remote, 'node-a', remoteTimestamp: localTs - 1000);
      expect(localWins['action'], 'use_local');
      expect(localWins['data'], local);

      final remoteWins =
          cache.reconcile('festival', remote, 'node-a', remoteTimestamp: localTs + 1000);
      expect(remoteWins['action'], 'use_remote');
      expect(remoteWins['data'], remote);
    });

    test('reconcile converged data from different origins', () async {
      final cache = OfflineCacheService.instance;
      await cache.init();
      await cache.putWithOrigin('festival', {'id': 1, 'name': 'Same'}, 'node-a');
      final result = cache.reconcile('festival', {'id': 1, 'name': 'Same'}, 'node-b');
      expect(result['action'], 'use_remote');
      expect(result['note'], 'converged');
      expect(result['origin'], 'node-b');
    });

    test('reconcile reports conflict for divergent data', () async {
      final cache = OfflineCacheService.instance;
      await cache.init();
      final local = {'id': 1, 'name': 'Local'};
      final remote = {'id': 1, 'name': 'Remote'};
      await cache.putWithOrigin('festival', local, 'node-a');
      final result = cache.reconcile('festival', remote, 'node-b');
      expect(result['action'], 'conflict');
      expect(result['local'], local);
      expect(result['remote'], remote);
      expect(result['origins'], ['node-a', 'node-b']);
    });
  });
}
