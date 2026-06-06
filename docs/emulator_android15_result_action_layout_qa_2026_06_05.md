# Android 15 Result Action Layout QA

## Environment

- Device: Android 15 AVD `Medium_Phone_API_35_Default`.
- Serial: `emulator-5566`.
- App package: `ru.poryadok5.app`.
- Build: current debug APK from `app/build/outputs/apk/debug/app-debug.apk`.
- Evidence directory: `qa/emulator-android15-result-action-layout-qa-2026-06-05`.

## Flow

1. Started an owned read-only Android 15 AVD on port `5566`; the base AVD was already in use by `emulator-5554`.
2. Set the QA viewport to `1080x2400`, density `420`, font scale `1.0` and disabled animations.
3. Installed the current debug APK, cleared app data and cleared logcat.
4. Launched `ru.poryadok5.app/.MainActivity`.
5. Captured onboarding, pressed `Начать`, captured Home and pressed `Запустить таймер`.
6. Captured Timer, pressed `Готово`, captured Result and refreshed `screenshots/play-store/04-result.png` from that real app UI frame.

## Result

Passed for the 2026-06-05 layout scope. The Result screen kept the then-current primary next action, the details action `Посмотреть шаги`, and the peer secondary navigation actions `На главный экран` and `Посмотреть итоги` visible above the Android navigation bar at 1080x2400. The current 2026-06-06 Result flow is covered by the newer details-first Result QA.

The UI tree shows the compact peer row:

- `На главный экран`: bounds `[53,2136][527,2273]`.
- `Посмотреть итоги`: bounds `[553,2136][1027,2273]`.
- Android navigation bar starts at `[0,2274][1080,2400]`.

Final focus stayed on `ru.poryadok5.app/.MainActivity`. Crash buffer and app-specific fatal/ANR match files contained 0 lines. The zero-match gate files are `07-crash-buffer.txt` and `08-app-fatal-anr-matches.txt`.

## Evidence Files

- `qa/emulator-android15-result-action-layout-qa-2026-06-05/01-onboarding.xml`
- `qa/emulator-android15-result-action-layout-qa-2026-06-05/01-onboarding.png`
- `qa/emulator-android15-result-action-layout-qa-2026-06-05/02-home.xml`
- `qa/emulator-android15-result-action-layout-qa-2026-06-05/02-home.png`
- `qa/emulator-android15-result-action-layout-qa-2026-06-05/03-timer.xml`
- `qa/emulator-android15-result-action-layout-qa-2026-06-05/03-timer.png`
- `qa/emulator-android15-result-action-layout-qa-2026-06-05/04-result.xml`
- `qa/emulator-android15-result-action-layout-qa-2026-06-05/04-result.png`
- `qa/emulator-android15-result-action-layout-qa-2026-06-05/04-result-summary.txt`
- `qa/emulator-android15-result-action-layout-qa-2026-06-05/05-focus.txt`
- `qa/emulator-android15-result-action-layout-qa-2026-06-05/06-logcat.txt`
- `qa/emulator-android15-result-action-layout-qa-2026-06-05/07-crash-buffer.txt`
- `qa/emulator-android15-result-action-layout-qa-2026-06-05/08-app-fatal-anr-matches.txt`
