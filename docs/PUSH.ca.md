# Push / recordatoris — decisió: natiu, sense Firebase

[ES](PUSH.md) · [EN](PUSH.en.md) · [FR](PUSH.fr.md) · [DE](PUSH.de.md) · [IT](PUSH.it.md) · [CA](PUSH.ca.md) · [EU](PUSH.eu.md) · [GL](PUSH.gl.md) · [OC](PUSH.oc.md)

Sense Firebase ni proveïdors externs. Estratègia per plataforma:

| Plataforma | Mecanismo | Estado |
|---|---|---|
| Escritorio (Windows/macOS/Linux) | `flutter_local_notifications` (`zonedSchedule`, 30 min antes) + permiso macOS al iniciar | Funcional con la app instalada |
| Web | Notification API nativa (`notification_web.dart` vía `package:web`, sin deps nuevas) con temporizadores; pide permiso en `init` | Funcional con pestaña abierta |
| Android/iOS | No soportado por decisión de producto (`_supported = false` en `init`) | No-op documentado |

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
