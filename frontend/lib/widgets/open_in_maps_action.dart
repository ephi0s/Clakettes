import 'package:flutter/foundation.dart';
import 'package:url_launcher/url_launcher.dart';

Future<void> openInMaps(double lat, double lng, {String? label}) async {
  final encodedLabel = label != null ? Uri.encodeComponent(label) : null;
  final geoQuery = encodedLabel != null ? '$lat,$lng($encodedLabel)' : '$lat,$lng';
  final geoUri = Uri.parse('geo:0,0?q=$geoQuery');
  if (await canLaunchUrl(geoUri)) {
    await launchUrl(geoUri);
    return;
  }
  final osmUri = Uri.parse('https://www.openstreetmap.org/?mlat=$lat&mlon=$lng');
  if (await canLaunchUrl(osmUri)) {
    if (kIsWeb) {
      await launchUrl(osmUri, webOnlyWindowName: '_blank');
    } else {
      await launchUrl(osmUri, mode: LaunchMode.externalApplication);
    }
  }
}
