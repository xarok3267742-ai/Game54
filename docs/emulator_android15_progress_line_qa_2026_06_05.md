# Android 15 ProgressLine QA

## Environment

- Device: Android 15 AVD `Medium_Phone_API_35_Default`.
- Serial: `emulator-5566`.
- App package: `ru.poryadok5.app`.
- Build: current debug APK from `app/build/outputs/apk/debug/app-debug.apk`.
- Evidence directory: `qa/emulator-android15-progress-line-qa-2026-06-05`.

## Flow

1. Started an owned Android 15 AVD on port `5566`.
2. Set the QA viewport to `1080x2400`, density `420`, font scale `1.0` and disabled animations.
3. Installed the current debug APK, cleared app data and cleared logcat.
4. Launched `ru.poryadok5.app/.MainActivity`.
5. Completed onboarding, opened Home, started the first timer and captured Timer.
6. Refreshed `screenshots/play-store/03-timer.png` from the real Timer frame after the `ProgressLine` change.
7. Completed the task, opened Result, tapped `Посмотреть итоги` and captured Progress.
8. Refreshed `screenshots/play-store/05-progress.png` from the real Progress frame after the `ProgressLine` change.

## Result

Passed. Timer, catalog and zone progress bars render through `ProgressLine`. The Progress screenshot no longer shows a false end-dot on rows with `0 из 16`; only the `Дом` row with `1 из 16` has a visible filled segment. The Timer screenshot no longer shows a right-edge stop marker on the track.

Final focus stayed on `ru.poryadok5.app/.MainActivity`. Crash buffer and app-specific fatal/ANR match files contained 0 lines. The zero-match gate files are `08-crash-buffer.txt` and `09-app-fatal-anr-matches.txt`.

## Evidence Files

- `qa/emulator-android15-progress-line-qa-2026-06-05/01-onboarding.xml`
- `qa/emulator-android15-progress-line-qa-2026-06-05/01-onboarding.png`
- `qa/emulator-android15-progress-line-qa-2026-06-05/02-home.xml`
- `qa/emulator-android15-progress-line-qa-2026-06-05/02-home.png`
- `qa/emulator-android15-progress-line-qa-2026-06-05/03-timer.xml`
- `qa/emulator-android15-progress-line-qa-2026-06-05/03-timer.png`
- `qa/emulator-android15-progress-line-qa-2026-06-05/04-result.xml`
- `qa/emulator-android15-progress-line-qa-2026-06-05/04-result.png`
- `qa/emulator-android15-progress-line-qa-2026-06-05/05-progress.xml`
- `qa/emulator-android15-progress-line-qa-2026-06-05/05-progress.png`
- `qa/emulator-android15-progress-line-qa-2026-06-05/06-focus.txt`
- `qa/emulator-android15-progress-line-qa-2026-06-05/07-logcat.txt`
- `qa/emulator-android15-progress-line-qa-2026-06-05/08-crash-buffer.txt`
- `qa/emulator-android15-progress-line-qa-2026-06-05/09-app-fatal-anr-matches.txt`
