# Push / recordatorios — decisión: nativo, sen Firebase

[ES](PUSH.md) · [EN](PUSH.en.md) · [FR](PUSH.fr.md) · [DE](PUSH.de.md) · [IT](PUSH.it.md) · [CA](PUSH.ca.md) · [EU](PUSH.eu.md) · [GL](PUSH.gl.md) · [OC](PUSH.oc.md)

Sen Firebase nin provedores externos. Estratexia por plataforma:

| Plataforma | Mecanismo | Estado |
|---|---|---|
| Escritorio (Windows/macOS/Linux) | `flutter_local_notifications` (`zonedSchedule`, 30 min antes) + permiso macOS al iniciar | Funcional con la app instalada |
| Web | Notification API nativa (`notification_web.dart` vía `package:web`, sin deps nuevas) con temporizadores; pide permiso en `init` | Funcional con pestaña abierta |
| Android/iOS | No soportado por decisión de producto (`_supported = false` en `init`) | No-op documentado |

## Detalles de implementación

- `lib/services/notification_platform.dart`: export condicional
  (`notification_web.dart` se `dart.library.js_interop`, se non
  `notification_stub.dart`) — mesmo patrón que `file_downloader.dart`.
- `NotificationService._supported`: true en escritorio/web, false en móbil;
  `resetForTesting` fórzao a true para non romper os tests (a plataforma
  de `flutter_test` é Android).
- Web: `scheduleWebNotification` reprograma por id, ignora horas pasadas e
  limpa ao cancelar; ao pechar a pestana os pendentes pérdense
  (sen Service Worker a propósito: requiriría servidor push).
- `flutter build web` verificado (58 s, sen erros de `js_interop`).

## Se algún día se quere fondo real en web/móbil

Require servidor push propio (VAPID + Service Worker) ou provedor externo;
ver historial deste documento para o roadmap Firebase descartado.
