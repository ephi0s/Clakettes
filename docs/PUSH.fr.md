# Push / rappels — décision : natif, sans Firebase

[ES](PUSH.md) · [EN](PUSH.en.md) · [FR](PUSH.fr.md) · [DE](PUSH.de.md) · [IT](PUSH.it.md) · [CA](PUSH.ca.md) · [EU](PUSH.eu.md) · [GL](PUSH.gl.md) · [OC](PUSH.oc.md)

Sans Firebase ni fournisseurs externes. Stratégie par plateforme :

| Plataforma | Mecanismo | Estado |
|---|---|---|
| Escritorio (Windows/macOS/Linux) | `flutter_local_notifications` (`zonedSchedule`, 30 min antes) + permiso macOS al iniciar | Funcional con la app instalada |
| Web | Notification API nativa (`notification_web.dart` vía `package:web`, sin deps nuevas) con temporizadores; pide permiso en `init` | Funcional con pestaña abierta |
| Android/iOS | No soportado por decisión de producto (`_supported = false` en `init`) | No-op documentado |

## Détails d'implémentation

- `lib/services/notification_platform.dart` : export conditionnel
  (`notification_web.dart` si `dart.library.js_interop`, sinon
  `notification_stub.dart`) — même motif que `file_downloader.dart`.
- `NotificationService._supported` : true en bureau/web, false en mobile ;
  `resetForTesting` le force à true pour ne pas casser les tests (la plateforme
  de `flutter_test` est Android).
- Web : `scheduleWebNotification` reprogramme par id, ignore heures passées et
  nettoie à l'annulation ; à la fermeture de l'onglet les pendants se perdent
  (sans Service Worker à dessein : requerrait serveur push).
- `flutter build web` vérifié (58 s, sans erreurs de `js_interop`).

## Si un jour on veut du vrai fond en web/mobile

Requiert serveur push propre (VAPID + Service Worker) ou fournisseur externe ;
voir historique de ce document pour le roadmap Firebase écarté.
