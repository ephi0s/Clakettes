# Push / Erinnerungen — Entscheidung: nativ, ohne Firebase

[ES](../es/PUSH.md) · [EN](../en/PUSH.md) · [FR](../fr/PUSH.md) · [DE](PUSH.md) · [IT](../it/PUSH.md) · [CA](../ca/PUSH.md) · [EU](../eu/PUSH.md) · [GL](../gl/PUSH.md) · [OC](../oc/PUSH.md)

Kein Firebase oder externe Anbieter. Strategie pro Plattform:

| Plattform | Mechanismus | Status |
|-----------|-------------|--------|
| Desktop (Windows/macOS/Linux) | `flutter_local_notifications` (`zonedSchedule`, 30 Min vorher) + macOS-Berechtigung beim Start | Funktional mit installierter App |
| Web | Native Notification API (`notification_web.dart` via `package:web`, keine neuen Deps) mit Timern; fragt Berechtigung bei `init` ab | Funktional mit offenem Tab |
| Android/iOS | Nicht unterstützt durch Produktentscheidung (`_supported = false` in `init`) | Dokumentierter No-op |

## Implementierungsdetails

- `lib/services/notification_platform.dart`: bedingter Export (`notification_web.dart` wenn `dart.library.js_interop`, sonst `notification_stub.dart`) — gleiches Muster wie `file_downloader.dart`.
- `NotificationService._supported`: wahr auf Desktop/Web, falsch auf Mobil; `resetForTesting` zwingt es auf wahr, um Tests nicht zu brechen (die `flutter_test`-Plattform ist Android).
- Web: `scheduleWebNotification` reprogrammiert nach ID, ignoriert vergangene Zeiten und löscht bei Abbruch; bei Tab-Schluss gehen ausstehende verloren (absichtlich kein Service Worker: erfordert Push-Server).
- `flutter build web` verifiziert (58 s, keine `js_interop`-Fehler).

## Falls irgendwann echter Hintergrund auf Web/Mobil gewünscht

Erfordert eigenen Push-Server (VAPID + Service Worker) oder externen Anbieter; siehe Dokument-Historie für verworfene Firebase-Roadmap.