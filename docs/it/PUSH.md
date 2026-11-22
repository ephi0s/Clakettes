# Push / promemoria — decisione: nativo, senza Firebase

[ES](../es/PUSH.md) · [EN](../en/PUSH.md) · [FR](../fr/PUSH.md) · [DE](../de/PUSH.md) · [IT](PUSH.md) · [CA](../ca/PUSH.md) · [EU](../eu/PUSH.md) · [GL](../gl/PUSH.md) · [OC](../oc/PUSH.md)

Senza Firebase né provider esterni. Strategia per piattaforma:

| Piattaforma | Meccanismo | Stato |
|---|---|---|
| Desktop (Windows/macOS/Linux) | `flutter_local_notifications` (`zonedSchedule`, 30 min prima) + permesso macOS all'avvio | Funzionale con l'app installata |
| Web | Notification API nativa (`notification_web.dart` via `package:web`, senza nuove dipendenze) con timer; chiede il permesso in `init` | Funzionale con la scheda aperta |
| Android/iOS | Non supportato per decisione di prodotto (`_supported = false` in `init`) | No-op documentato |

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
