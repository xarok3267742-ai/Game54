# Android 15 Home Task Skip QA - 2026-06-03

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
4. Captured onboarding UI and tapped `Начать`.
5. Captured Home before skip and refreshed `screenshots/play-store/02-home.png` from this real UI frame.
6. Verified Home contained `Другая задача`, `Посмотреть шаги`, `Запустить таймер` and the `выполнено` metric.
7. Tapped `Другая задача` from UI-tree bounds center `290,1357`.
8. Captured Home after skip and compared task title/progress values.
9. Captured focused window and crash/logcat evidence.

## Result

- Before skip task title: `Подготовить спокойный угол`.
- After skip task title: `Навести порядок на диване`.
- Task title changed after skip: passed.
- Progress remained at `0` completed tasks before and after skip: passed.
- `Другая задача` remained available after the first skip: passed.
- Final focus remained `ru.poryadok5.app/.MainActivity`.
- Crash buffer contained 0 lines.
- Fatal/ANR match file contained 0 lines.

## Evidence

- `qa/emulator-android15-home-task-skip-qa-2026-06-03/01-onboarding.png`
- `qa/emulator-android15-home-task-skip-qa-2026-06-03/01-onboarding.xml`
- `qa/emulator-android15-home-task-skip-qa-2026-06-03/02-home-before-skip.png`
- `qa/emulator-android15-home-task-skip-qa-2026-06-03/02-home-before-skip.xml`
- `qa/emulator-android15-home-task-skip-qa-2026-06-03/03-home-after-skip.png`
- `qa/emulator-android15-home-task-skip-qa-2026-06-03/03-home-after-skip.xml`
- `qa/emulator-android15-home-task-skip-qa-2026-06-03/04-focus.txt`
- `qa/emulator-android15-home-task-skip-qa-2026-06-03/05-crash-buffer.txt`
- `qa/emulator-android15-home-task-skip-qa-2026-06-03/06-logcat.txt`
- `qa/emulator-android15-home-task-skip-qa-2026-06-03/07-app-fatal-anr-matches.txt`

## Notes

The emulator reported disabled DNS during startup, but this scenario is fully offline and does not require network access.
Final PNG evidence was captured after restarting the owned `emulator-5566` session with cold boot and `swiftshader_indirect`; the earlier snapshot-restored session produced black `screencap` frames despite a valid UI tree, so those temporary files were discarded.
