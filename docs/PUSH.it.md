# Push / promemoria — decisione: nativo, senza Firebase

Senza Firebase né provider esterni. Strategia per piattaforma:

| Plataforma | Mecanismo | Estado |
|---|---|---|
| Escritorio (Windows/macOS/Linux) | `flutter_local_notifications` (`zonedSchedule`, 30 min antes) + permiso macOS al iniciar | Funcional con la app instalada |
| Web | Notification API nativa (`notification_web.dart` vía `package:web`, sin deps nuevas) con temporizadores; pide permiso en `init` | Funcional con pestaña abierta |
| Android/iOS | No soportado por decisión de producto (`_supported = false` en `init`) | No-op documentado |

## Dettagli di implementazione

- `lib/services/notification_platform.dart`: export condizionale
  (`notification_web.dart` se `dart.library.js_interop`, se no
  `notification_stub.dart`) — stesso pattern di `file_downloader.dart`.
- `NotificationService._supported`: true su desktop/web, false su mobile;
  `resetForTesting` lo forza a true per non rompere i test (la piattaforma
  di `flutter_test` è Android).
- Web: `scheduleWebNotification` riprogramma per id, ignora ore passate e
  pulisce alla cancellazione; chiudendo la scheda i pendenti si perdono
  (senza Service Worker di proposito: richiederebbe un server push).
- `flutter build web` verificato (58 s, senza errori di `js_interop`).

## Se un giorno si vorrà sfondo reale su web/mobile

Richiede un server push proprio (VAPID + Service Worker) o un provider esterno;
vedi storia di questo documento per la roadmap Firebase scartata.
