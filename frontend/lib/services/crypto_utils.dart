import 'dart:convert';
import 'dart:math';
import 'package:archive/archive.dart';
import 'package:crypto/crypto.dart';
import 'package:flutter/foundation.dart';
import 'package:pointycastle/export.dart';

// =============================================================================
// Compression strategies (pluggable, hot-swappable)
// =============================================================================

/// Constantes de byte de cabecera para el protocolo wire.
///
/// Se anteponen al payload comprimido para que el receptor identifique qué
/// algoritmo se usó, permitiendo el hot-swap sin romper mensajes existentes.
abstract final class CompressionHeaders {
  static const int none = 0x00;
  static const int zlib = 0x01;
  static const int gzip = 0x02;
  // Reserve 0x03-0x0F for future algorithms (brotli, lz4, zstd, …)
}

/// Estrategia de compresión abstracta.
///
/// Implementa esta interfaz para añadir un nuevo algoritmo.
/// El método [encode] debe anteponer el byte [CompressionHeaders] apropiado.
abstract class CompressionStrategy {
  String get name;
  int get headerByte;
  Uint8List encode(Uint8List data);
  Uint8List decode(Uint8List data);
}

/// Passthrough — sin compresión alguna.
///
/// Ideal para mensajes < 100 bytes donde la sobrecarga de la compresión supera
/// sus ventajas, o cuando el ahorro de energía es la prioridad máxima.
class NoCompression extends CompressionStrategy {
  @override
  String get name => 'none';

  @override
  int get headerByte => CompressionHeaders.none;

  @override
  Uint8List encode(Uint8List data) {
    return Uint8List.fromList([headerByte, ...data]);
  }

  @override
  Uint8List decode(Uint8List data) {
    // data is the payload after the header has been stripped
    return data;
  }
}

/// Compresión zlib (formato RFC 1950, con cabecera y checksum Adler-32).
///
/// [level] va de 1 (más rápido) a 9 (mejor ratio).
/// El valor por defecto 6 ofrece un buen equilibrio para payloads de chat.
class ZlibCompression extends CompressionStrategy {
  final int level;
  ZlibCompression({this.level = 6})
      : assert(level >= 1 && level <= 9, 'Zlib level must be 1–9');

  @override
  String get name => 'zlib:$level';

  @override
  int get headerByte => CompressionHeaders.zlib;

  @override
  Uint8List encode(Uint8List data) {
    final compressed = const ZLibEncoder().encodeBytes(data, level: level);
    return Uint8List.fromList([headerByte, ...compressed]);
  }

  @override
  Uint8List decode(Uint8List data) {
    return Uint8List.fromList(const ZLibDecoder().decodeBytes(data));
  }
}

/// Compresión GZip (deflate con cabecera y pie gzip).
///
/// Más interoperable; [level] igual que en Zlib (1–9).
class GZipCompression extends CompressionStrategy {
  final int level;
  GZipCompression({this.level = 6})
      : assert(level >= 1 && level <= 9, 'GZip level must be 1–9');

  @override
  String get name => 'gzip:$level';

  @override
  int get headerByte => CompressionHeaders.gzip;

  @override
  Uint8List encode(Uint8List data) {
    final compressed = const GZipEncoder().encodeBytes(data, level: level);
    return Uint8List.fromList([headerByte, ...compressed]);
  }

  @override
  Uint8List decode(Uint8List data) {
    return Uint8List.fromList(const GZipDecoder().decodeBytes(data));
  }
}

// =============================================================================
// Adaptive selector — chooses strategy transparently based on context
// =============================================================================

/// Pistas de contexto para el selector adaptativo.
class CompressionContext {
  /// Longitud del texto plano del mensaje en bytes.
  final int messageBytes;

  /// Indica si el dispositivo está en modo ahorro de energía.
  final bool energySaver;

  /// Indica si el usuario ha solicitado el modo de baja latencia (omite la compresión pesada).
  final bool lowLatency;

  const CompressionContext({
    required this.messageBytes,
    this.energySaver = false,
    this.lowLatency = false,
  });
}

/// Selector de algoritmo que elige la mejor estrategia de compresión en runtime.
///
/// Reglas (todos los umbrales son empíricos y ajustables):
///   - < 100 bytes       → NoCompression   (sobrecarga > beneficio de ratio)
///   - 100–500 bytes     → Zlib level 1    (rápido, decente en payloads pequeños)
///   - > 500 bytes       → Zlib level 6    (mejor ratio, sigue siendo rápido)
///   - Ahorro de energía → Zlib level 1 para todo ≥ 100 bytes
///   - Baja latencia     → NoCompression para < 500 bytes
class AdaptiveSelector {
  final NoCompression _none = NoCompression();
  final ZlibCompression _zlibFast = ZlibCompression(level: 1);
  final ZlibCompression _zlibBalanced = ZlibCompression(level: 6);
  final ZlibCompression _zlibMax = ZlibCompression(level: 9);

  /// Selecciona una estrategia según [ctx].
  CompressionStrategy selectFor(CompressionContext ctx) {
    // No compression at all for very short payloads
    if (ctx.messageBytes < 100) return _none;

    // Energy-saver: always use fastest compression
    if (ctx.energySaver) {
      return ctx.messageBytes < 500 ? _none : _zlibFast;
    }

    // Low-latency: prefer speed over ratio
    if (ctx.lowLatency) {
      return ctx.messageBytes < 1000 ? _none : _zlibFast;
    }

    // Default adaptive
    if (ctx.messageBytes < 500) return _zlibFast;
    if (ctx.messageBytes < 2000) return _zlibBalanced;
    return _zlibMax;
  }

  /// Singleton integrado.
  static final AdaptiveSelector instance = AdaptiveSelector._();
  AdaptiveSelector._();
}

// =============================================================================
// ChatCrypto — main API used by the rest of the app
// =============================================================================

/// Utilidades de compresión sin pérdida y E2EE para mensajes de chat.
///
/// Características:
///   - **Compresión pluggable** con hot-swap en runtime
///   - **Auto-selector adaptativo** que considera el tamaño del mensaje, la batería y la latencia
///   - **Acuerdo de clave X25519** + **AES-256-GCM** para cifrado de extremo a extremo
class ChatCrypto {
  // ---------------------------------------------------------------------------
  // Compression strategy management (hot-swappable)
  // ---------------------------------------------------------------------------

  static CompressionStrategy? _globalStrategy;
  static bool _energySaver = false;
  static bool _lowLatency = false;

  static final AdaptiveSelector _selector = AdaptiveSelector.instance;
  static final NoCompression _fallback = NoCompression();

  /// Sobrescribe la estrategia globalmente. Pasa `null` para volver al modo adaptativo.
  static void setGlobalStrategy(CompressionStrategy? strategy) {
    _globalStrategy = strategy;
  }

  /// Activa / desactiva el modo adaptativo.
  static void setAdaptiveMode(bool enabled) {
    if (enabled) _globalStrategy = null;
  }

  /// Pista: el dispositivo está en ahorro de batería → priorizar velocidad sobre ratio.
  static void setEnergySaver(bool on) => _energySaver = on;

  /// Pista: el usuario prefiere baja latencia → omitir la compresión pesada.
  static void setLowLatencyMode(bool on) => _lowLatency = on;

  /// Selecciona la estrategia de forma adaptativa para una longitud de texto plano dada.
  static CompressionStrategy selectStrategyFor(int plaintextBytes) {
    if (_globalStrategy != null) return _globalStrategy!;
    return _selector.selectFor(CompressionContext(
      messageBytes: plaintextBytes,
      energySaver: _energySaver,
      lowLatency: _lowLatency,
    ));
  }

  /// Resuelve manualmente una estrategia a partir de un byte de cabecera (lado receptor).
  static CompressionStrategy strategyForHeader(int header) {
    return _strategyForHeader(header);
  }

  // ---------------------------------------------------------------------------
  // Compress / decompress (use current strategy)
  // ---------------------------------------------------------------------------

  /// Comprime [data] con la estrategia actualmente activa.
  ///
  /// Los bytes devueltos incluyen una cabecera de un byte que identifica el
  /// algoritmo, para que el receptor pueda decodificar de forma transparente.
  static Uint8List compress(Uint8List data) {
    final strategy = selectStrategyFor(data.length);
    return strategy.encode(data);
  }

  /// Descomprime [data] usando el byte de cabecera para seleccionar el algoritmo.
  ///
  /// Gestiona automáticamente cualquier estrategia registrada.
  static Uint8List decompress(Uint8List data) {
    if (data.isEmpty) return data;
    final header = data[0];
    final payload = data.sublist(1);
    final strategy = _strategyForHeader(header);
    return strategy.decode(payload);
  }

  /// Resuelve una estrategia a partir de su byte de cabecera.
  static CompressionStrategy _strategyForHeader(int header) {
    switch (header) {
      case CompressionHeaders.none:
        return _fallback;
      case CompressionHeaders.zlib:
        return ZlibCompression();
      case CompressionHeaders.gzip:
        return GZipCompression();
      default:
        // Unknown header — treat as uncompressed (forward compat)
        return _fallback;
    }
  }

  // ---------------------------------------------------------------------------
  // Convenience: JSON in / JSON out (uses current strategy)
  // ---------------------------------------------------------------------------

  /// Serializa [json], comprime con la estrategia activa y codifica en base64.
  static String compressJson(Map<String, dynamic> json) {
    final encoded = utf8.encode(jsonEncode(json));
    final compressed = compress(Uint8List.fromList(encoded));
    return base64Url.encode(compressed);
  }

  /// Decodifica base64, descomprime y deserializa JSON.
  static Map<String, dynamic> decompressJson(String compressedBase64) {
    final compressed = base64Url.decode(compressedBase64);
    final decompressed = decompress(Uint8List.fromList(compressed));
    return jsonDecode(utf8.decode(decompressed)) as Map<String, dynamic>;
  }

  // ---------------------------------------------------------------------------
  // E2EE: ECDH (P-256) + AES-256-GCM
  // ---------------------------------------------------------------------------

  /// Genera un nuevo par de claves ECDH P-256.
  /// Devuelve (privateKeyBase64, publicKeyBase64).
  /// La clave privada se serializa como el escalar `d` (32 bytes) y la pública
  /// como la codificación del punto sin comprimir (65 bytes).
  static List<String> generateKeyPair() {
    final domain = ECDomainParameters('prime256v1');
    final keyGen = ECKeyGenerator();
    keyGen.init(ParametersWithRandom(
      ECKeyGeneratorParameters(domain),
      _secureRandom(),
    ));
    final pair = keyGen.generateKeyPair();
    final privKey = pair.privateKey as ECPrivateKey;
    final pubKey = pair.publicKey as ECPublicKey;
    final privBigInt = privKey.d;
    final privBytes = _bigIntToBytes(privBigInt!, 32);
    final pubBytes = pubKey.Q!.getEncoded(false); // uncompressed (65 bytes)
    return [
      base64Url.encode(privBytes),
      base64Url.encode(pubBytes),
    ];
  }

  /// Deriva una clave AES compartida de 256 bits a partir de nuestro [privateKeyBase64]
  /// (escalar d) y su [publicKeyBase64] (punto sin comprimir).
  static Uint8List deriveSharedKey(String privateKeyBase64, String publicKeyBase64) {
    final privBytes = base64Url.decode(privateKeyBase64);
    final pubBytes = base64Url.decode(publicKeyBase64);
    final domain = ECDomainParameters('prime256v1');
    final privKey = ECPrivateKey(_bytesToBigInt(privBytes), domain);
    final pubKey = ECPublicKey(domain.curve.decodePoint(pubBytes), domain);
    final agreement = ECDHBasicAgreement();
    agreement.init(privKey);
    final sharedBigInt = agreement.calculateAgreement(pubKey);
    final sharedBytes = _bigIntToBytes(sharedBigInt, 32);
    return sha256.convert(sharedBytes).bytes as Uint8List;
  }

  /// Convierte un [BigInt] positivo a un [Uint8List] de ancho fijo (big-endian).
  static Uint8List _bigIntToBytes(BigInt n, int width) {
    final result = Uint8List(width);
    for (var i = width - 1; i >= 0; i--) {
      result[i] = n.toUnsigned(8).toInt();
      n = n >> 8;
    }
    return result;
  }

  /// Convierte una lista de bytes big-endian a [BigInt].
  static BigInt _bytesToBigInt(Uint8List bytes) {
    var result = BigInt.zero;
    for (final b in bytes) {
      result = (result << 8) | BigInt.from(b);
    }
    return result;
  }

  /// Cifra [plaintext] (UTF-8) con AES-256-GCM usando [key].
  /// Devuelve "nonce||ciphertext||tag" codificado en base64.
  static String encrypt(String plaintext, Uint8List key) {
    final nonce = _randomBytes(12);
    final cipher = GCMBlockCipher(AESEngine())
      ..init(true, AEADParameters(
        KeyParameter(key),
        128,
        nonce,
        Uint8List(0),
      ));
    final ciphertext = cipher.process(Uint8List.fromList(utf8.encode(plaintext)));
    final totalLen = nonce.length + ciphertext.length;
    final combined = Uint8List(totalLen)
      ..setRange(0, nonce.length, nonce)
      ..setRange(nonce.length, totalLen, ciphertext);
    return base64Url.encode(combined);
  }

  /// Descifra un "nonce||ciphertext||tag" codificado en base64 con AES-256-GCM usando [key].
  static String decrypt(String encryptedBase64, Uint8List key) {
    final combined = base64Url.decode(encryptedBase64);
    final nonce = combined.sublist(0, 12);
    final ciphertext = combined.sublist(12);
    final cipher = GCMBlockCipher(AESEngine())
      ..init(false, AEADParameters(
        KeyParameter(key),
        128,
        nonce,
        Uint8List(0),
      ));
    return utf8.decode(cipher.process(ciphertext));
  }

  static Future<String> encryptAsync(String plaintext, Uint8List key) {
    if (plaintext.length <= 1024) return Future.value(encrypt(plaintext, key));
    return compute(_encryptIsolateEntry, (plaintext: plaintext, key: key));
  }

  static Future<String> decryptAsync(String encryptedBase64, Uint8List key) {
    if (encryptedBase64.length <= 1365) return Future.value(decrypt(encryptedBase64, key));
    return compute(_decryptIsolateEntry, (encryptedBase64: encryptedBase64, key: key));
  }

  // ---------------------------------------------------------------------------
  // Sender keys for group E2EE
  // ---------------------------------------------------------------------------

  /// Genera una clave de emisor (sender key) aleatoria de 256 bits para cifrado de grupo.
  static Uint8List generateSenderKey() {
    return _randomBytes(32);
  }

  /// Cifra [senderKey] con la clave compartida ECDH derivada de [myPrivateKey]
  /// y [theirPublicKey]. Devuelve el ciphertext codificado en base64.
  static String encryptSenderKey(Uint8List senderKey, String myPrivateKey, String theirPublicKey) {
    final sharedKey = deriveSharedKey(myPrivateKey, theirPublicKey);
    return encrypt(base64Url.encode(senderKey), sharedKey);
  }

  /// Descifra una sender key cifrada usando la clave compartida ECDH derivada de
  /// [myPrivateKey] y [theirPublicKey]. Devuelve la sender key cruda de 32 bytes.
  static Uint8List decryptSenderKey(String encryptedSenderKey, String myPrivateKey, String theirPublicKey) {
    final sharedKey = deriveSharedKey(myPrivateKey, theirPublicKey);
    final decrypted = decrypt(encryptedSenderKey, sharedKey);
    return base64Url.decode(decrypted);
  }

  /// Versiones en isolate de las operaciones con sender keys (ver
  /// [encryptAsync]/[decryptAsync]). La derivación ECDH es rápida y se queda
  /// en el UI thread; solo el AES-GCM se desplaza al isolate.
  static Future<String> encryptSenderKeyAsync(Uint8List senderKey, String myPrivateKey, String theirPublicKey) {
    final sharedKey = deriveSharedKey(myPrivateKey, theirPublicKey);
    return encryptAsync(base64Url.encode(senderKey), sharedKey);
  }

  static Future<Uint8List> decryptSenderKeyAsync(String encryptedSenderKey, String myPrivateKey, String theirPublicKey) async {
    final sharedKey = deriveSharedKey(myPrivateKey, theirPublicKey);
    final decrypted = await decryptAsync(encryptedSenderKey, sharedKey);
    return base64Url.decode(decrypted);
  }

  /// Comprueba si un contenido de mensaje es una difusión de sender key cifrada.
  static bool isSenderKeyMessage(String content) {
    return content.startsWith('skey:');
  }

  /// Envuelve una sender key cifrada en un payload de transferencia.
  static String wrapSenderKey(String encryptedKey) {
    return 'skey:$encryptedKey';
  }

  /// Desenvuelve un payload de sender key.
  static String unwrapSenderKey(String content) {
    if (!isSenderKeyMessage(content)) return content;
    return content.substring(5);
  }

  // ---------------------------------------------------------------------------
  // Helpers
  // ---------------------------------------------------------------------------

  static Uint8List _randomBytes(int count) {
    final rand = FortunaRandom();
    final seed = _secureSeed();
    rand.seed(KeyParameter(seed));
    final bytes = Uint8List(count);
    for (var i = 0; i < count; i++) {
      bytes[i] = rand.nextUint8();
    }
    return bytes;
  }

  static SecureRandom _secureRandom() {
    final secure = FortunaRandom();
    secure.seed(KeyParameter(_secureSeed()));
    return secure;
  }

  static Uint8List _secureSeed() {
    final r = Random.secure();
    return Uint8List.fromList(List<int>.generate(32, (_) => r.nextInt(256)));
  }
}

String _encryptIsolateEntry(({String plaintext, Uint8List key}) p) => ChatCrypto.encrypt(p.plaintext, p.key);
String _decryptIsolateEntry(({String encryptedBase64, Uint8List key}) p) => ChatCrypto.decrypt(p.encryptedBase64, p.key);
