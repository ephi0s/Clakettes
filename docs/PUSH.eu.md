# Push / gogorarazleak — erabakia: natiboa, Firebase gabe

[ES](PUSH.md) · [EN](PUSH.en.md) · [FR](PUSH.fr.md) · [DE](PUSH.de.md) · [IT](PUSH.it.md) · [CA](PUSH.ca.md) · [EU](PUSH.eu.md) · [GL](PUSH.gl.md) · [OC](PUSH.oc.md)

Firebase-rik ez kanpo-hornitzailerik ez. Plataformako estrategia:

| Plataforma | Mecanismo | Estado |
|---|---|---|
| Escritorio (Windows/macOS/Linux) | `flutter_local_notifications` (`zonedSchedule`, 30 min antes) + permiso macOS al iniciar | Funcional con la app instalada |
| Web | Notification API nativa (`notification_web.dart` vía `package:web`, sin deps nuevas) con temporizadores; pide permiso en `init` | Funcional con pestaña abierta |
| Android/iOS | No soportado por decisión de producto (`_supported = false` en `init`) | No-op documentado |

## Inplementazio-xehetasunak

- `lib/services/notification_platform.dart`: esportazio baldintzatua
  (`notification_web.dart` `dart.library.js_interop` bada, bestela
  `notification_stub.dart`) — `file_downloader.dart`-ren eredu bera.
- `NotificationService._supported`: true escritorioan/web-ean, false mugikorrean;
  `resetForTesting`-ek true-ra behartzen du test-ak ez hausteko (`flutter_test`-eko plataforma
  Android da).
- Web-a: `scheduleWebNotification`-ek id-z birprogramatzen du, iragandako orduak ez ikusi egiten ditu eta
  ezeztatzean garbitzen du; fitxa ixtean pendiente-ak galdu egiten dira
  (Service Worker gabe nahita: push zerbitzari propioa beharko luke).
- `flutter build web` egiaztatuta (58 s, `js_interop` errorerik gabe).

## Benetako atzeko planoa web/mugikorrean noizbait nahi bada

Push zerbitzari propioa behar du (VAPID + Service Worker) edo kanpo-hornitzailea;
ikusi dokumentu honen historia baztertutako Firebase roadmap-erako.
