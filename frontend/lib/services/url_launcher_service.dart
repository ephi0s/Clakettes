import 'package:url_launcher/url_launcher.dart';

/// Esquemas que pueden abrirse desde contenido no confiable.
const Set<String> allowedUrlSchemes = {'http', 'https', 'mailto', 'tel', 'geo'};

/// Normaliza la entrada y abre solo esquemas permitidos.
///
/// Las URLs sin esquema se interpretan como https. Devuelve `false` para
/// javascript:, file:, data: y cualquier otro esquema, sin lanzar nada.
Future<bool> openUrl(String raw, {Future<bool> Function(Uri uri)? launcher}) async {
  final value = raw.trim();
  if (value.isEmpty) return false;

  var uri = Uri.tryParse(value);
  if (uri == null || !uri.hasScheme) uri = Uri.tryParse('https://$value');
  if (uri == null) return false;

  final scheme = uri.scheme.toLowerCase();
  if (!allowedUrlSchemes.contains(scheme)) return false;
  if ((scheme == 'http' || scheme == 'https') && uri.host.isEmpty) return false;

  final handler = launcher ?? _launchExternal;
  return handler(uri);
}

Future<bool> _launchExternal(Uri uri) async {
  if (!await canLaunchUrl(uri)) return false;
  return launchUrl(uri, mode: LaunchMode.externalApplication);
}
