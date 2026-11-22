# Push / recordatoris — decisió: natiu, sense Firebase

[ES](../es/PUSH.md) · [EN](../en/PUSH.md) · [FR](../fr/PUSH.md) · [DE](../de/PUSH.md) · [IT](../it/PUSH.md) · [CA](PUSH.md) · [EU](../eu/PUSH.md) · [GL](../gl/PUSH.md) · [OC](../oc/PUSH.md)

Sense Firebase ni proveïdors externs. Estratègia per plataforma:

| Plataforma | Mecanisme | Estat |
|---|---|---|
| Escriptori (Windows/macOS/Linux) | `flutter_local_notifications` (`zonedSchedule`, 30 min abans) + permís macOS en iniciar | Funcional amb l'app instal·lada |
| Web | Notification API nativa (`notification_web.dart` via `package:web`, sense deps noves) amb temporitzadors; demana permís a `init` | Funcional amb la pestanya oberta |
| Android/iOS | No compatible per decisió de producte (`_supported = false` a `init`) | No-op documentat |

## Detalls d'implementació

- `lib/services/notification_platform.dart`: export condicional
  (`notification_web.dart` si `dart.library.js_interop`, si no
  `notification_stub.dart`) — mateix patró que `file_downloader.dart`.
- `NotificationService._supported`: true en escriptori/web, false en mòbil;
  `resetForTesting` el força a true per no trencar els tests (la plataforma
  de `flutter_test` és Android).
- Web: `scheduleWebNotification` reprograma per id, ignora hores passades i
  neteja en cancel·lar; en tancar la pestanya els pendents es perden
  (sense Service Worker a propòsit: requeriria servidor push).
- `flutter build web` verificat (58 s, sense errors de `js_interop`).

## Si algun dia es vol fons real en web/mòbil

Requereix servidor push propi (VAPID + Service Worker) o proveïdor extern;
vegeu historial d'aquest document per al roadmap Firebase descartat.
