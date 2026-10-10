import 'dart:async';
import 'package:flutter_test/flutter_test.dart';
import 'package:hive/hive.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:clakettes/services/api_service.dart';
import 'package:clakettes/services/sync_queue_service.dart';

class _FakeApi implements ApiService {
  int calls = 0;
  bool throwError = false;
  Completer<void>? gate;

  @override
  Future<dynamic> create(String path, Object body) async {
    calls++;
    if (gate != null) await gate!.future;
    if (throwError) throw Exception('boom');
    return <String, dynamic>{};
  }

  @override
  dynamic noSuchMethod(Invocation invocation) => null;
}

void main() {
  setUp(() async {
    SharedPreferences.setMockInitialValues({});
    Hive.init('.');
    await Hive.deleteBoxFromDisk('sync_queue');
  });

  group('SyncQueueService', () {
    test('init opens the sync queue box', () async {
      final sync = SyncQueueService();
      await sync.init();
      expect(sync.hasPending, isFalse);
    });

    test('enqueue adds a pending operation', () async {
      final sync = SyncQueueService();
      await sync.init();
      await sync.enqueue(
        entityType: 'festival',
        operation: 'create',
        payload: {'name': 'Test Festival'},
      );
      expect(sync.hasPending, isTrue);
      expect(sync.pendingCount, 1);
    });

    test('multiple enqueues increment pending count', () async {
      final sync = SyncQueueService();
      await sync.init();
      await sync.enqueue(
        entityType: 'festival',
        operation: 'create',
        payload: {'name': 'F1'},
      );
      await sync.enqueue(
        entityType: 'user',
        operation: 'update',
        entityId: 1,
        payload: {'username': 'u1'},
      );
      expect(sync.pendingCount, 2);
    });

    test('operations persist across service instances', () async {
      final sync1 = SyncQueueService();
      await sync1.init();
      await sync1.enqueue(
        entityType: 'message',
        operation: 'delete',
        entityId: 42,
        payload: {},
      );

      final sync2 = SyncQueueService();
      await sync2.init();
      expect(sync2.pendingCount, 1);
    });

    test('clear removes all queued operations', () async {
      final sync = SyncQueueService();
      await sync.init();
      await sync.enqueue(
        entityType: 'festival',
        operation: 'create',
        payload: {'name': 'F1'},
      );
      await sync.clear();
      expect(sync.hasPending, isFalse);
      expect(sync.pendingCount, 0);
    });

    test('enqueue with entityId stores it correctly', () async {
      final sync = SyncQueueService();
      await sync.init();
      await sync.enqueue(
        entityType: 'shortfilm',
        operation: 'update',
        entityId: 99,
        payload: {'title': 'Updated'},
      );

      final box = await Hive.openBox('sync_queue');
      final raw = box.get('operations');
      expect(raw, isNotNull);
      final ops = List<Map<String, dynamic>>.from(raw);
      expect(ops.length, 1);
      expect(ops[0]['entity_id'], 99);
      expect(ops[0]['entity_type'], 'shortfilm');
      expect(ops[0]['operation'], 'update');
    });

    test('enqueue with empty payload is valid', () async {
      final sync = SyncQueueService();
      await sync.init();
      await sync.enqueue(
        entityType: 'festival',
        operation: 'create',
        payload: {},
      );
      expect(sync.pendingCount, 1);
    });

    test('pendingCount is 0 after init with empty queue', () async {
      final sync = SyncQueueService();
      await sync.init();
      expect(sync.pendingCount, 0);
    });

    test('failed op is retried and marked failed after max attempts', () async {
      final fake = _FakeApi()..throwError = true;
      final sync = SyncQueueService(api: fake);
      await sync.init();
      await sync.enqueue(
        entityType: 'festival',
        operation: 'create',
        payload: {'name': 'F1'},
      );
      expect(sync.pendingCount, 1);

      final first = await sync.syncAll();
      expect(first['failed'], 1);
      expect(fake.calls, 1);
      expect(sync.pendingCount, 1, reason: 'failed op should be retryable');

      final second = await sync.syncAll();
      expect(second['failed'], 1);
      expect(fake.calls, 2);
      expect(sync.pendingCount, 1);

      final third = await sync.syncAll();
      expect(third['failed'], 1);
      expect(fake.calls, 3);

      expect(sync.pendingCount, 0, reason: 'exhausted attempts not counted');
      expect(sync.hasPending, isFalse);

      final box = await Hive.openBox('sync_queue');
      final raw = box.get('operations') as List;
      expect(raw.length, 1);
      final op = SyncOperation.fromJson(Map<String, dynamic>.from(raw[0]));
      expect(op.status, SyncStatus.failed);
      expect(op.attempts, SyncQueueService.maxAttempts);
    });

    test('syncAll is not reentrant', () async {
      final fake = _FakeApi();
      final sync = SyncQueueService(api: fake);
      await sync.init();
      await sync.enqueue(
        entityType: 'festival',
        operation: 'create',
        payload: {'name': 'A'},
      );
      await sync.enqueue(
        entityType: 'festival',
        operation: 'create',
        payload: {'name': 'B'},
      );

      final gate = Completer<void>();
      fake.gate = gate;

      final first = sync.syncAll();
      await Future<void>.delayed(Duration.zero);
      final second = await sync.syncAll();
      expect(second['synced'], 0);
      expect(fake.calls, 0, reason: 'second call must not drain');

      gate.complete();
      final result = await first;
      expect(result['synced'], 2);
      expect(fake.calls, 2);
    });

    test('clear resets queue and pendingCount', () async {
      final fake = _FakeApi()..throwError = true;
      final sync = SyncQueueService(api: fake);
      await sync.init();
      await sync.enqueue(
        entityType: 'festival',
        operation: 'create',
        payload: {'name': 'F1'},
      );
      await sync.syncAll();
      expect(sync.pendingCount, 1);

      await sync.clear();
      expect(sync.pendingCount, 0);
      expect(sync.hasPending, isFalse);
      expect(sync.pendingCount, 0);
    });
  });
}
