import 'dart:io';
import 'dart:typed_data';
import 'package:path_provider/path_provider.dart';
import 'package:url_launcher/url_launcher.dart';

/// Descarga [bytes] como un archivo llamado [filename] en escritorio/móvil.
///
/// Escribe el archivo en el directorio temporal de la aplicación y lo abre
/// con la aplicación asociada mediante [launchUrl].
Future<void> downloadFile(Uint8List bytes, String filename) async {
  final dir = await getTemporaryDirectory();
  final file = File('${dir.path}${Platform.pathSeparator}$filename');
  await file.writeAsBytes(bytes, flush: true);
  await launchUrl(file.uri);
}
