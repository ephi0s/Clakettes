import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hive/hive.dart';
import 'package:clakettes/services/database_service.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() async {
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(
      const MethodChannel('plugins.flutter.io/path_provider'),
      (MethodCall methodCall) async {
        if (methodCall.method == 'getApplicationDocumentsDirectory') {
          return '.';
        }
        return null;
      },
    );

    Hive.init('.');
    await Hive.deleteBoxFromDisk('festivals');
    await Hive.deleteBoxFromDisk('users');
    await Hive.deleteBoxFromDisk('shortfilms');
    await Hive.deleteBoxFromDisk('messages');
  });

  tearDown(() {
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(
      const MethodChannel('plugins.flutter.io/path_provider'),
      null,
    );
  });

  group('DatabaseService', () {
    test('init registers adapters and opens all boxes', () async {
      await DatabaseService.init();

      final festivals = await Hive.openBox('festivals');
      final users = await Hive.openBox('users');
      final shortfilms = await Hive.openBox('shortfilms');
      final messages = await Hive.openBox('messages');

      expect(festivals.isOpen, isTrue);
      expect(users.isOpen, isTrue);
      expect(shortfilms.isOpen, isTrue);
      expect(messages.isOpen, isTrue);

      expect(festivals.length, 0);
      expect(users.length, 0);
      expect(shortfilms.length, 0);
      expect(messages.length, 0);

      await festivals.close();
      await users.close();
      await shortfilms.close();
      await messages.close();
    });

    test('boxes can store and retrieve data', () async {
      final box = await Hive.openBox('festivals');
      await box.put('test_key', {'name': 'Test Festival', 'id': 1});
      final result = box.get('test_key');
      expect(result['name'], 'Test Festival');
      expect(result['id'], 1);
      await box.close();
    });

    test('all four boxes are empty on fresh start', () async {
      final festivals = await Hive.openBox('festivals');
      final users = await Hive.openBox('users');
      final shortfilms = await Hive.openBox('shortfilms');
      final messages = await Hive.openBox('messages');

      expect(festivals.length, 0);
      expect(users.length, 0);
      expect(shortfilms.length, 0);
      expect(messages.length, 0);

      await festivals.close();
      await users.close();
      await shortfilms.close();
      await messages.close();
    });
  });
}
