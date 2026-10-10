import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter_test/flutter_test.dart';
import 'package:clakettes/services/crypto_utils.dart';

void main() {
  group('CompressionStrategy', () {
    test('NoCompression encode prepends header byte', () {
      final comp = NoCompression();
      final data = Uint8List.fromList([72, 101, 108, 108, 111]);
      final result = comp.encode(data);
      expect(result[0], CompressionHeaders.none);
      expect(result.sublist(1), data);
    });

    test('NoCompression decode returns data as-is', () {
      final comp = NoCompression();
      final data = Uint8List.fromList([72, 101, 108, 108, 111]);
      expect(comp.decode(data), data);
    });

    test('ZlibCompression round-trip', () {
      final comp = ZlibCompression(level: 6);
      final original = Uint8List.fromList(utf8.encode('Hello, World!'));
      final encoded = comp.encode(original);
      expect(encoded[0], CompressionHeaders.zlib);
      final decoded = comp.decode(encoded.sublist(1));
      expect(decoded, original);
    });

    test('ZlibCompression rejects invalid level', () {
      expect(() => ZlibCompression(level: 0), throwsA(isA<AssertionError>()));
      expect(() => ZlibCompression(level: 10), throwsA(isA<AssertionError>()));
    });

    test('GZipCompression round-trip', () {
      final comp = GZipCompression(level: 6);
      final original = Uint8List.fromList(utf8.encode('Compress me!'));
      final encoded = comp.encode(original);
      expect(encoded[0], CompressionHeaders.gzip);
      final decoded = comp.decode(encoded.sublist(1));
      expect(decoded, original);
    });

    test('GZipCompression rejects invalid level', () {
      expect(() => GZipCompression(level: 0), throwsA(isA<AssertionError>()));
      expect(() => GZipCompression(level: 10), throwsA(isA<AssertionError>()));
    });
  });

  group('AdaptiveSelector', () {
    late AdaptiveSelector selector;

    setUp(() {
      selector = AdaptiveSelector.instance;
    });

    test('returns NoCompression for messages under 100 bytes', () {
      final strategy = selector.selectFor(const CompressionContext(messageBytes: 50));
      expect(strategy, isA<NoCompression>());
    });

    test('returns Zlib level 1 for 100-500 bytes', () {
      final strategy = selector.selectFor(const CompressionContext(messageBytes: 200));
      expect(strategy.name, 'zlib:1');
    });

    test('returns Zlib level 6 for 500-2000 bytes', () {
      final strategy = selector.selectFor(const CompressionContext(messageBytes: 1000));
      expect(strategy.name, 'zlib:6');
    });

    test('returns Zlib level 9 for over 2000 bytes', () {
      final strategy = selector.selectFor(const CompressionContext(messageBytes: 3000));
      expect(strategy.name, 'zlib:9');
    });

    test('energy saver uses NoCompression for under 500', () {
      const ctx = CompressionContext(messageBytes: 200, energySaver: true);
      expect(selector.selectFor(ctx), isA<NoCompression>());
    });

    test('energy saver uses Zlib level 1 for 500+', () {
      const ctx = CompressionContext(messageBytes: 1000, energySaver: true);
      expect(selector.selectFor(ctx).name, 'zlib:1');
    });

    test('low latency skips compression under 1000', () {
      const ctx = CompressionContext(messageBytes: 600, lowLatency: true);
      expect(selector.selectFor(ctx), isA<NoCompression>());
    });

    test('low latency uses Zlib level 1 for 1000+', () {
      const ctx = CompressionContext(messageBytes: 1500, lowLatency: true);
      expect(selector.selectFor(ctx).name, 'zlib:1');
    });
  });

  group('ChatCrypto', () {
    setUp(() {
      ChatCrypto.setGlobalStrategy(null);
      ChatCrypto.setAdaptiveMode(true);
      ChatCrypto.setEnergySaver(false);
      ChatCrypto.setLowLatencyMode(false);
    });

    test('compress and decompress round-trip with small data', () {
      final original = Uint8List.fromList(utf8.encode('Hello, World!'));
      final compressed = ChatCrypto.compress(original);
      final decompressed = ChatCrypto.decompress(compressed);
      expect(decompressed, original);
    });

    test('compress and decompress round-trip with large data', () {
      final large = utf8.encode('A' * 1000);
      final original = Uint8List.fromList(large);
      final compressed = ChatCrypto.compress(original);
      final decompressed = ChatCrypto.decompress(compressed);
      expect(decompressed, original);
    });

    test('compressJson and decompressJson round-trip', () {
      final original = {'type': 'text', 'content': 'Hello!', 'sender': 42};
      final compressed = ChatCrypto.compressJson(original);
      final decompressed = ChatCrypto.decompressJson(compressed);
      expect(decompressed, original);
    });

    test('setGlobalStrategy overrides adaptive selection', () {
      ChatCrypto.setGlobalStrategy(NoCompression());
      final data = Uint8List.fromList(utf8.encode('A' * 500));
      final compressed = ChatCrypto.compress(data);
      expect(compressed[0], CompressionHeaders.none);
    });

    test('setGlobalStrategy with null reverts to adaptive', () {
      ChatCrypto.setGlobalStrategy(NoCompression());
      ChatCrypto.setGlobalStrategy(null);
      final strategy = ChatCrypto.selectStrategyFor(200);
      expect(strategy.name, 'zlib:1');
    });

    test('setAdaptiveMode false locks current strategy', () {
      ChatCrypto.setAdaptiveMode(false);
      final strategy = ChatCrypto.selectStrategyFor(50);
      expect(strategy, isA<NoCompression>());
    });

    test('strategyForHeader resolves known headers', () {
      expect(ChatCrypto.strategyForHeader(CompressionHeaders.none), isA<NoCompression>());
      expect(ChatCrypto.strategyForHeader(CompressionHeaders.zlib), isA<ZlibCompression>());
      expect(ChatCrypto.strategyForHeader(CompressionHeaders.gzip), isA<GZipCompression>());
    });

    test('strategyForHeader falls back to NoCompression for unknown header', () {
      expect(ChatCrypto.strategyForHeader(0xFF), isA<NoCompression>());
    });

    test('decompress with empty data returns empty', () {
      final result = ChatCrypto.decompress(Uint8List(0));
      expect(result, Uint8List(0));
    });

    test('setEnergySaver affects strategy selection', () {
      ChatCrypto.setEnergySaver(true);
      final strategy = ChatCrypto.selectStrategyFor(1000);
      expect(strategy.name, 'zlib:1');
    });

    test('setLowLatencyMode affects strategy selection', () {
      ChatCrypto.setLowLatencyMode(true);
      final strategy = ChatCrypto.selectStrategyFor(600);
      expect(strategy, isA<NoCompression>());
    });
  });

  group('ChatCrypto async (isolate)', () {
    test('encryptAsync and decryptAsync round-trip', () async {
      final keys = ChatCrypto.generateKeyPair();
      final shared = ChatCrypto.deriveSharedKey(keys[0], keys[1]);
      const plain = 'hola chat async';
      final encrypted = await ChatCrypto.encryptAsync(plain, shared);
      expect(await ChatCrypto.decryptAsync(encrypted, shared), plain);
    });

    test('encryptSenderKeyAsync and decryptSenderKeyAsync round-trip', () async {
      final alice = ChatCrypto.generateKeyPair();
      final bob = ChatCrypto.generateKeyPair();
      final senderKey = ChatCrypto.generateSenderKey();
      final encrypted = await ChatCrypto.encryptSenderKeyAsync(senderKey, alice[0], bob[1]);
      final decrypted = await ChatCrypto.decryptSenderKeyAsync(encrypted, bob[0], alice[1]);
      expect(decrypted, senderKey);
    });
  });
}
