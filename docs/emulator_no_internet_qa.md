# Emulator QA: No-Internet Flow

## Scope

Validate that `Порядок 5` works without an active default network. This covers the product requirement that the MVP is offline-first and does not depend on backend, accounts, ads, analytics or network-loaded content.

## Environment

- Device serial: `emulator-5554`.
- Android: 15, API 35.
- Model: Android SDK built for arm64.
- App package: `ru.poryadok5.app`.
- Build: debug APK installed with `./gradlew :app:installDebug --console=plain`.
- App data: cleared before the run with `adb shell pm clear ru.poryadok5.app`.
- Network setup: `adb shell svc wifi disable` and `adb shell svc data disable`.
- `dumpsys connectivity` evidence showed `Active default network: none`.
- The Android 15 shell was not allowed to broadcast `android.intent.action.AIRPLANE_MODE`; this did not block the test because wifi/data were disabled and active default network was none.

## Evidence Directory

`qa/emulator-android15-no-internet`

Key files:

- `connectivity-disabled.txt`
- `connectivity-summary-before.txt`
- `01-onboarding.xml`, `01-onboarding.png`
- `02-home.xml`, `02-home.png`
- `03-timer.xml`, `03-timer.png`
- `04-result.xml`, `04-result.png`
- `connectivity-summary-after-flow.txt`
- `crash-logcat.txt`

## Flow Result

| Step | Evidence | Result |
|---|---|---|
| Network disabled | `connectivity-summary-before.txt` | `Active default network: none`. |
| Fresh launch | `01-onboarding.xml` | Onboarding rendered from local app state. |
| Enter app | `02-home.xml` | Home rendered with filters, metrics and suggested task. |
| Start timer | `03-timer.xml` | Timer screen rendered for task `Сложить плед`; visible time `2:58`. |
| Complete task | `04-result.xml` | Result screen rendered with `1` completed task, `1 дн.` streak and `1%` catalog progress. |
| Crash buffer | `crash-logcat.txt` | 0 crash log lines. |

## Verdict

Passed for Android 15 debug smoke QA. Core onboarding, task selection, timer and completion flow work while the device has no active default network.
