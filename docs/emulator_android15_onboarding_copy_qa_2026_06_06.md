# Android 15 Onboarding Copy QA

## Environment

- Device: Android 15 AVD `Medium_Phone_API_35_Default`.
- Serial: `emulator-5566`.
- App package: `ru.poryadok5.app`.
- Build: current debug APK from `app/build/outputs/apk/debug/app-debug.apk`.
- Evidence directory: `qa/emulator-android15-onboarding-copy-qa-2026-06-06`.

## Flow

1. Started an owned Android 15 AVD on port `5566`.
2. Set the QA viewport to `1080x2400`, density `420`, font scale `1.0` and disabled animations.
3. Installed the current debug APK, cleared app data and cleared logcat.
4. Launched `ru.poryadok5.app/.MainActivity`.
5. Captured the fresh first-run onboarding UI tree and screenshot.
6. Refreshed `screenshots/play-store/01-onboarding.png` from the real onboarding frame after the copy alignment change.

## Result

Passed. The onboarding “Как это работает” copy now says `Выбираете стартовую зону.`, `Получаете задачу и при желании уточняете подбор.` and `Запускаете таймер и отмечаете результат.` The first-run screen no longer promises energy selection before the Home filter controls are visible.

The primary action `Начать` remained visible on the 1080x2400 frame. Final focus stayed on `ru.poryadok5.app/.MainActivity`. Crash buffer and app-specific fatal/ANR match files contained 0 lines. The zero-match gate files are `04-crash-buffer.txt` and `05-app-fatal-anr-matches.txt`.

## Evidence Files

- `qa/emulator-android15-onboarding-copy-qa-2026-06-06/01-onboarding.xml`
- `qa/emulator-android15-onboarding-copy-qa-2026-06-06/01-onboarding.png`
- `qa/emulator-android15-onboarding-copy-qa-2026-06-06/01-onboarding-summary.txt`
- `qa/emulator-android15-onboarding-copy-qa-2026-06-06/02-focus.txt`
- `qa/emulator-android15-onboarding-copy-qa-2026-06-06/03-logcat.txt`
- `qa/emulator-android15-onboarding-copy-qa-2026-06-06/04-crash-buffer.txt`
- `qa/emulator-android15-onboarding-copy-qa-2026-06-06/05-app-fatal-anr-matches.txt`
- `qa/emulator-android15-onboarding-copy-qa-2026-06-06/06-screenshot-size.txt`
- `qa/emulator-android15-onboarding-copy-qa-2026-06-06/wm-size.txt`
- `qa/emulator-android15-onboarding-copy-qa-2026-06-06/wm-density.txt`
- `qa/emulator-android15-onboarding-copy-qa-2026-06-06/android-release.txt`
- `qa/emulator-android15-onboarding-copy-qa-2026-06-06/resolve-activity.txt`
