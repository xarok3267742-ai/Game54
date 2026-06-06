# Android 15 Result Next Details QA - 2026-06-03

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
4. Completed onboarding with `Начать`.
5. Started the Home task timer with `Запустить таймер`.
6. Tapped `Готово` on Timer to reach Result.
7. Captured Result and refreshed `screenshots/play-store/04-result.png` from this real UI frame.
8. Verified Result contained `Дальше без повтора`, `Запустить следующую`, `Посмотреть шаги` and the `выполнено` metric.
9. Tapped `Посмотреть шаги` from UI-tree bounds center `540,2025`.
10. Verified the Details screen opened for the previewed next task.
11. Captured focused window and crash/logcat evidence.

## Result

- Result next-task title: `Навести порядок на диване`.
- Details opened for the same title: passed.
- Details screen showed `Выбранная задача` and `Шаги`: passed.
- Progress was not recorded by opening next-task details: no completion action was triggered.
- Final focus remained inside `ru.poryadok5.app/.MainActivity`.
- Crash buffer contained 0 lines.
- Fatal/ANR match file contained 0 lines.

## Evidence

- `qa/emulator-android15-result-next-details-qa-2026-06-03/01-onboarding.png`
- `qa/emulator-android15-result-next-details-qa-2026-06-03/01-onboarding.xml`
- `qa/emulator-android15-result-next-details-qa-2026-06-03/02-home.png`
- `qa/emulator-android15-result-next-details-qa-2026-06-03/02-home.xml`
- `qa/emulator-android15-result-next-details-qa-2026-06-03/03-timer.png`
- `qa/emulator-android15-result-next-details-qa-2026-06-03/03-timer.xml`
- `qa/emulator-android15-result-next-details-qa-2026-06-03/04-result.png`
- `qa/emulator-android15-result-next-details-qa-2026-06-03/04-result.xml`
- `qa/emulator-android15-result-next-details-qa-2026-06-03/05-next-details.png`
- `qa/emulator-android15-result-next-details-qa-2026-06-03/05-next-details.xml`
- `qa/emulator-android15-result-next-details-qa-2026-06-03/06-focus.txt`
- `qa/emulator-android15-result-next-details-qa-2026-06-03/07-crash-buffer.txt`
- `qa/emulator-android15-result-next-details-qa-2026-06-03/08-logcat.txt`
- `qa/emulator-android15-result-next-details-qa-2026-06-03/09-app-fatal-anr-matches.txt`

## Notes

The emulator was started with cold boot and `swiftshader_indirect` so `screencap` produced nonblank PNG evidence.
