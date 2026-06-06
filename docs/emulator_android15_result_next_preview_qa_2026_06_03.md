# Android 15 Result Next Preview QA — 2026-06-03

## Scope

- App: `Порядок 5`
- Package: `ru.poryadok5.app`
- Device: `emulator-5554`, Android 15
- Build: current debug APK installed via `adb install -r`
- Evidence directory: `qa/emulator-android-result-next-preview-2026-06-03`

## Flow Checked

1. Installed the current debug APK.
2. Cleared app data with `adb shell pm clear ru.poryadok5.app`.
3. Completed onboarding and verified the quick-task-first Home screen.
4. Captured refreshed Home screenshot to `screenshots/play-store/02-home.png`.
5. Started the first timer for `Подготовить спокойный угол`.
6. Completed the task and verified Result screen metrics: `1`, `1 дн.`, `1%`.
7. Verified Result screen shows next-task preview with `Дальше без повтора`.
8. Verified the preview task is `Навести порядок на диване`, not the just-completed task.
9. Captured refreshed Result screenshot to `screenshots/play-store/04-result.png`.
10. Pressed `Запустить следующую` and verified the Timer opened for `Навести порядок на диване`.

## Evidence Files

- `01-home-summary.txt`: quick-task-first Home.
- `02-timer-summary.txt`: first timer.
- `03-result-summary.txt`: Result with next-task preview.
- `04-next-timer-summary.txt`: Timer for the preview task.
- `poryadok-fatal-anr-matches.txt`: 0 lines.

## Result

Pass. Result now makes the next action visible before repeating the flow, and the next-task launch does not immediately repeat the completed task.
