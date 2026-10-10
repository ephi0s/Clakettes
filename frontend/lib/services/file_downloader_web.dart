import 'dart:js_interop';
import 'dart:typed_data';
import 'package:web/web.dart' as web;

/// Descarga [bytes] como un archivo llamado [filename] en el navegador.
///
/// Crea un Blob, dispara la descarga con un enlace anclado y libera la URL.
Future<void> downloadFile(Uint8List bytes, String filename) async {
  final blob = web.Blob(
    <web.BlobPart>[bytes.toJS].toJS,
    web.BlobPropertyBag(type: 'application/octet-stream'),
  );
  final url = web.URL.createObjectURL(blob);
  final anchor = web.HTMLAnchorElement()
    ..href = url
    ..download = filename;
  anchor.click();
  web.URL.revokeObjectURL(url);
  anchor.remove();
}
