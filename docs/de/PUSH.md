# Push / Erinnerungen — Entscheidung: nativ, ohne Firebase

[ES](../es/PUSH.md) · [EN](../en/PUSH.md) · [FR](../fr/PUSH.md) · [DE](PUSH.md) · [IT](../it/PUSH.md) · [CA](../ca/PUSH.md) · [EU](../eu/PUSH.md) · [GL](../gl/PUSH.md) · [OC](../oc/PUSH.md)

Ohne Firebase noch externe Anbieter. Strategie je Plattform:

| Plataforma | Mecanismo | Estado |
|---|---|---|
| Escritorio (Windows/macOS/Linux) | `flutter_local_notifications` (`zonedSchedule`, 30 min antes) + permiso macOS al iniciar | Funcional con la app instalada |
| Web | Notification API nativa (`notification_web.dart` vía `package:web`, sin deps nuevas) con temporizadores; pide permiso en `init` | Funcional con pestaña abierta |
| Android/iOS | No soportado por decisión de producto (`_supported = false` en `init`) | No-op documentado |

## Implementierungsdetails

- `lib/services/notification_platform.dart`: konditionaler Export
  (`notification_web.dart` wenn `dart.library.js_interop`, sonst
  `notification_stub.dart`) — gleiches Muster wie `file_downloader.dart`.
- `NotificationService._supported`: true auf Desktop/Web, false auf Mobil;
  `resetForTesting` zwingt es auf true, um Tests nicht zu brechen (die Plattform
  von `flutter_test` ist Android).
- Web: `scheduleWebNotification` plant per ID neu um, ignoriert vergangene Zeiten und
  räumt beim Abbrechen auf; beim Schließen des Tabs gehen Ausstehende verloren
  (absichtlich ohne Service Worker: bräuchte Push-Server).
- `flutter build web` verifiziert (58 s, ohne `js_interop`-Fehler).

## Falls eines Tages echtes Hintergrundverhalten auf Web/Mobil gewünscht wird

Erfordert eigenen Push-Server (VAPID + Service Worker) oder externen Anbieter;
siehe Historie dieses Dokuments für die verworfene Firebase-Roadmap.
