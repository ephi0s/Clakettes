# Push / rappels — décision : natif, sans Firebase

[ES](../es/PUSH.md) · [EN](../en/PUSH.md) · [FR](PUSH.md) · [DE](../de/PUSH.md) · [IT](../it/PUSH.md) · [CA](../ca/PUSH.md) · [EU](../eu/PUSH.md) · [GL](../gl/PUSH.md) · [OC](../oc/PUSH.md)

Pas de Firebase ni de fournisseurs externes. Stratégie par plateforme :

| Plateforme | Mécanisme | État |
|---|---|---|
| Bureau (Windows/macOS/Linux) | `flutter_local_notifications` (`zonedSchedule`, 30 min avant) + permission macOS au démarrage | Fonctionnel avec l'app installée |
| Web | Notification API native (`notification_web.dart` via `package:web`, sans nouvelles dépendances) avec minuteries ; demande la permission à `init` | Fonctionnel avec l'onglet ouvert |
| Android/iOS | Non supporté par décision produit (`_supported = false` dans `init`) | No-op documenté |

## Détails d'implémentation

- `lib/services/notification_platform.dart` : export conditionnel (`notification_web.dart` si `dart.library.js_interop`, sinon `notification_stub.dart`) — même schéma que `file_downloader.dart`.
- `NotificationService._supported` : vrai sur bureau/web, faux sur mobile ; `resetForTesting` le force à vrai pour ne pas casser les tests (la plateforme de `flutter_test` est Android).
- Web : `scheduleWebNotification` reprogramme par id, ignore les heures passées et nettoie à l'annulation ; à la fermeture de l'onglet les notifications en attente sont perdues (pas de Service Worker volontairement : nécessiterait un serveur push).
- `flutter build web` vérifié (58 s, sans erreurs de `js_interop`).

## Si un jour on veut un vrai arrière-plan sur web/mobile

Nécessite un serveur push propre (VAPID + Service Worker) ou un fournisseur externe ; voir l'historique de ce document pour la feuille de route Firebase écartée.