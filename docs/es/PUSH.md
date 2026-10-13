# Push / recordatorios — decisión: nativo, sin Firebase

[ES](PUSH.md) · [EN](../en/PUSH.md) · [FR](../fr/PUSH.md) · [DE](../de/PUSH.md) · [IT](../it/PUSH.md) · [CA](../ca/PUSH.md) · [EU](../eu/PUSH.md) · [GL](../gl/PUSH.md) · [OC](../oc/PUSH.md)

Sin Firebase ni proveedores externos. Estrategia por plataforma:

| Plataforma | Mecanismo | Estado |
|---|---|---|
| Escritorio (Windows/macOS/Linux) | `flutter_local_notifications` (`zonedSchedule`, 30 min antes) + permiso macOS al iniciar | Funcional con la app instalada |
| Web | Notification API nativa (`notification_web.dart` vía `package:web`, sin deps nuevas) con temporizadores; pide permiso en `init` | Funcional con pestaña abierta |
| Android/iOS | No soportado por decisión de producto (`_supported = false` en `init`) | No-op documentado |

## Detalles de implementación

- `lib/services/notification_platform.dart`: export condicional
  (`notification_web.dart` si `dart.library.js_interop`, si no
  `notification_stub.dart`) — mismo patrón que `file_downloader.dart`.
- `NotificationService._supported`: true en escritorio/web, false en móvil;
  `resetForTesting` lo fuerza a true para no romper los tests (la plataforma
  de `flutter_test` es Android).
- Web: `scheduleWebNotification` reprograma por id, ignora horas pasadas y
  limpia al cancelar; al cerrar la pestaña los pendientes se pierden
  (sin Service Worker a propósito: requeriría servidor push).
- `flutter build web` verificado (58 s, sin errores de `js_interop`).

## Si algún día se quiere fondo real en web/móvil

Requiere servidor push propio (VAPID + Service Worker) o proveedor externo;
ver historial de este documento para el roadmap Firebase descartado.
