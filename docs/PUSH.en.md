# Push / reminders — decision: native, no Firebase

[ES](PUSH.md) · [EN](PUSH.en.md) · [FR](PUSH.fr.md) · [DE](PUSH.de.md) · [IT](PUSH.it.md) · [CA](PUSH.ca.md) · [EU](PUSH.eu.md) · [GL](PUSH.gl.md) · [OC](PUSH.oc.md)

No Firebase or external providers. Strategy per platform:

| Platform | Mechanism | Status |
|---|---|---|
| Desktop (Windows/macOS/Linux) | `flutter_local_notifications` (`zonedSchedule`, 30 min before) + macOS permission at startup | Working with the app installed |
| Web | Native Notification API (`notification_web.dart` via `package:web`, no new deps) with timers; asks permission in `init` | Working with the tab open |
| Android/iOS | Not supported by product decision (`_supported = false` in `init`) | Documented no-op |

## Implementation details

- `lib/services/notification_platform.dart`: conditional export
  (`notification_web.dart` if `dart.library.js_interop`, otherwise
  `notification_stub.dart`) — same pattern as `file_downloader.dart`.
- `NotificationService._supported`: true on desktop/web, false on mobile;
  `resetForTesting` forces it to true so tests do not break (the
  `flutter_test` platform is Android).
- Web: `scheduleWebNotification` reschedules by id, ignores past times and
  cleans up on cancel; when the tab closes, pending ones are lost
  (no Service Worker on purpose: it would require a push server).
- `flutter build web` verified (58 s, no `js_interop` errors).

## If background support is ever wanted on web/mobile

It requires a dedicated push server (VAPID + Service Worker) or an external provider;
see this document history for the discarded Firebase roadmap.
