# Push / reminders — decision: native, without Firebase

[ES](../es/PUSH.md) · [EN](PUSH.md) · [FR](../fr/PUSH.md) · [DE](../de/PUSH.md) · [IT](../it/PUSH.md) · [CA](../ca/PUSH.md) · [EU](../eu/PUSH.md) · [GL](../gl/PUSH.md) · [OC](../oc/PUSH.md)

No Firebase or external providers. Strategy by platform:

| Platform | Mechanism | Status |
|---|---|---|
| Desktop (Windows/macOS/Linux) | `flutter_local_notifications` (`zonedSchedule`, 30 min before) + macOS permission on start | Functional with app installed |
| Web | Native Notification API (`notification_web.dart` via `package:web`, no new deps) with timers; requests permission on `init` | Functional with tab open |
| Android/iOS | Not supported by product decision (`_supported = false` in `init`) | Documented no-op |

## Implementation details

- `lib/services/notification_platform.dart`: conditional export (`notification_web.dart` if `dart.library.js_interop`, otherwise `notification_stub.dart`) — same pattern as `file_downloader.dart`.
- `NotificationService._supported`: true on desktop/web, false on mobile; `resetForTesting` forces it to true to avoid breaking tests (the `flutter_test` platform is Android).
- Web: `scheduleWebNotification` reprograms by id, ignores past times and clears on cancel; when the tab closes pending ones are lost (no Service Worker on purpose: would require a push server).
- `flutter build web` verified (58 s, no `js_interop` errors).

## If real background on web/mobile is wanted someday

Requires a self-hosted push server (VAPID + Service Worker) or external provider; see document history for the discarded Firebase roadmap.