import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:clakettes/services/connectivity_monitor.dart';
import 'package:clakettes/services/api_service.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  group('ConnectivityMonitor', () {
    test('singleton returns same instance', () {
      final a = ConnectivityMonitor.instance;
      final b = ConnectivityMonitor.instance;
      expect(identical(a, b), isTrue);
    });

    test('isOnline defaults to true', () {
      final monitor = ConnectivityMonitor.instance;
      expect(monitor.isOnline, isTrue);
    });

    test('onStatusChanged stream is not null', () {
      final monitor = ConnectivityMonitor.instance;
      expect(monitor.onStatusChanged, isNotNull);
    });

    test('factory constructor ignores parameters', () {
      final a = ConnectivityMonitor();
      final b = ConnectivityMonitor(api: ApiService());
      expect(identical(a, b), isTrue);
    });
  });
}
