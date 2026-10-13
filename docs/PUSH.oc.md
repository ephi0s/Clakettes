# Push / rapèls — decision: natiu, sens Firebase

Sens Firebase ni fornidors extèrnes. Estrategia per plataforma:

| Plataforma | Mecanismo | Estado |
|---|---|---|
| Escritorio (Windows/macOS/Linux) | `flutter_local_notifications` (`zonedSchedule`, 30 min antes) + permiso macOS al iniciar | Funcional con la app instalada |
| Web | Notification API nativa (`notification_web.dart` vía `package:web`, sin deps nuevas) con temporizadores; pide permiso en `init` | Funcional con pestaña abierta |
| Android/iOS | No soportado por decisión de producto (`_supported = false` en `init`) | No-op documentado |

## Detalhs d'implementacion

- `lib/services/notification_platform.dart`: export condicionau
  (`notification_web.dart` se `dart.library.js_interop`, se non
  `notification_stub.dart`) — meteis patron que `file_downloader.dart`.
- `NotificationService._supported`: true en escritòri/web, false en mobil;
  `resetForTesting` lo fòrça a true per non rompre los tèsts (la plataforma
  de `flutter_test` es Android).
- Web: `scheduleWebNotification` reprograma per id, ignòra oras passadas e
  neteja en anullar; en tampar la pestanha los pendents se pèrdon
  (sens Service Worker a propaus: requeririá servidor push).
- `flutter build web` verificat (58 s, sens errors de `js_interop`).

## S'un jorn se vòl fons vertadièr en web/mobil

Requerís servidor push pròpri (VAPID + Service Worker) o fornidor extèrne;
veire istoric d'aqueste document per lo roadmap Firebase escartat.
