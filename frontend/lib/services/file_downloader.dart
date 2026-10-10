import 'dart:typed_data';
import 'file_downloader_web.dart' if (dart.library.io) 'file_downloader_io.dart' as impl;

/// Descarga [bytes] como un archivo llamado [filename] usando el mecanismo
/// nativo de la plataforma.
///
/// En web crea un Blob y dispara la descarga del navegador; en escritorio y
/// móvil escribe el archivo en el directorio temporal y lo abre con la
/// aplicación asociada. Lanza una excepción si la descarga no se puede
/// completar.
Future<void> downloadFile(Uint8List bytes, String filename) {
  return impl.downloadFile(bytes, filename);
}
