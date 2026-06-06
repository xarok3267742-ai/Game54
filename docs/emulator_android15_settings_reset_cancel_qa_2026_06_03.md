# Android 15 Settings Reset Cancel QA - 2026-06-03

## Scope

- App: `Порядок 5`
- Package: `ru.poryadok5.app`
- Device: Android 15 AVD `Medium_Phone_API_35_Default`
- Serial: `emulator-5566`
- Viewport: 1080x2400, density 420
- Build: current debug APK from `app/build/outputs/apk/debug/app-debug.apk`

## Steps

1. Installed the current debug APK.
2. Cleared app data with `adb shell pm clear ru.poryadok5.app`.
3. Launched `ru.poryadok5.app/.MainActivity`.
4. Completed onboarding and opened Settings through `Опции`.
5. Scrolled to `Сброс прогресса`.
6. Tapped `Подготовить сброс`.
7. Verified the confirmation state showed `Отмена` before `Сбросить прогресс`.
8. Tapped `Отмена`.
9. Verified the confirmation state closed, `Подготовить сброс` returned, `Сбросить прогресс` disappeared and the reset success notice was not shown.
10. Repeated `Подготовить сброс`, tapped `Сбросить прогресс` and verified the success notice.
11. Captured focus and log evidence.

## Result

- `Отмена` and `Сбросить прогресс` were visible in the confirmation state: passed.
- `Отмена` closed the confirmation state without showing `Готово. Прогресс сброшен, можно начать заново.`: passed.
- A second confirmation followed by `Сбросить прогресс` showed `Готово. Прогресс сброшен, можно начать заново.`: passed.
- Final focus remained inside `ru.poryadok5.app/.MainActivity`.
- App-specific fatal/ANR match file contained 0 lines.
- The crash buffer contained an unrelated `com.android.bluetooth` / `droid.bluetooth` system crash. No `ru.poryadok5.app` crash was present, and the app remained focused.

## Evidence

- `qa/emulator-android15-settings-reset-cancel-qa-2026-06-03/01-onboarding.png`
- `qa/emulator-android15-settings-reset-cancel-qa-2026-06-03/01-onboarding.xml`
- `qa/emulator-android15-settings-reset-cancel-qa-2026-06-03/02-home.png`
- `qa/emulator-android15-settings-reset-cancel-qa-2026-06-03/02-home.xml`
- `qa/emulator-android15-settings-reset-cancel-qa-2026-06-03/03-settings-reset-before.png`
- `qa/emulator-android15-settings-reset-cancel-qa-2026-06-03/03-settings-reset-before.xml`
- `qa/emulator-android15-settings-reset-cancel-qa-2026-06-03/04-reset-confirm.png`
- `qa/emulator-android15-settings-reset-cancel-qa-2026-06-03/04-reset-confirm.xml`
- `qa/emulator-android15-settings-reset-cancel-qa-2026-06-03/05-reset-after-cancel.png`
- `qa/emulator-android15-settings-reset-cancel-qa-2026-06-03/05-reset-after-cancel.xml`
- `qa/emulator-android15-settings-reset-cancel-qa-2026-06-03/06-reset-confirm-second.png`
- `qa/emulator-android15-settings-reset-cancel-qa-2026-06-03/06-reset-confirm-second.xml`
- `qa/emulator-android15-settings-reset-cancel-qa-2026-06-03/07-reset-after-confirm.png`
- `qa/emulator-android15-settings-reset-cancel-qa-2026-06-03/07-reset-after-confirm.xml`
- `qa/emulator-android15-settings-reset-cancel-qa-2026-06-03/08-focus.txt`
- `qa/emulator-android15-settings-reset-cancel-qa-2026-06-03/crash.log`
- `qa/emulator-android15-settings-reset-cancel-qa-2026-06-03/10-logcat.txt`
- `qa/emulator-android15-settings-reset-cancel-qa-2026-06-03/11-app-fatal-anr-matches.txt`
- `qa/emulator-android15-settings-reset-cancel-qa-2026-06-03/12-crash-context-filter.txt`

## Notes

The emulator was started as an owned `emulator-5566` session with cold boot and `swiftshader_indirect`.
