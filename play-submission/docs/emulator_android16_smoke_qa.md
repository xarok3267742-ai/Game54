# Android 16 Smoke QA

## Scope

Validate the current debug build on an Android 16 emulator, covering first launch, the primary task loop, timer controls, system Back navigation, settings and local persistence after restart.

## Environment

| Field | Value |
|---|---|
| AVD | `Medium_Phone_API_36` |
| Serial | `emulator-5560` |
| Android release | `16` |
| API | `36` |
| Package | `ru.poryadok5.app` |
| Activity | `ru.poryadok5.app/.MainActivity` |
| Evidence directory | `qa/emulator-android16-smoke` |
| Screen evidence | `1080x2400` physical size, `1080x2160` override size, density `420` |

## Flow Checked

1. Installed fresh `app/build/outputs/apk/debug/app-debug.apk`.
2. Cleared app data and crash logs.
3. Launched first-run onboarding.
4. Completed onboarding with “Начать”.
5. Changed timer duration to `3 мин`.
6. Started timer.
7. Checked pause and resume controls.
8. Completed the task with “Готово”.
9. Opened “Итоги”.
10. Pressed system Back from “Итоги”; app returned to Home instead of closing.
11. Opened “Настройки”.
12. Force-stopped and relaunched the app; onboarding stayed complete and progress remained visible.

## Evidence

| Step | Evidence |
|---|---|
| Onboarding | `qa/emulator-android16-smoke/01-onboarding.xml`, `.png` |
| Home first run | `qa/emulator-android16-smoke/02-home.xml`, `.png` |
| 3-minute selection | `qa/emulator-android16-smoke/03-home-3min.xml`, `.png` |
| Timer started | `qa/emulator-android16-smoke/04-timer-start.xml`, `.png` |
| Timer paused | `qa/emulator-android16-smoke/05-timer-paused.xml`, `.png` |
| Timer resumed | `qa/emulator-android16-smoke/06-timer-resumed.xml`, `.png` |
| Result | `qa/emulator-android16-smoke/07-result.xml`, `.png` |
| Progress | `qa/emulator-android16-smoke/08-progress.xml`, `.png` |
| Home after system Back | `qa/emulator-android16-smoke/09-home-after-system-back.xml`, `.png` |
| Settings | `qa/emulator-android16-smoke/10-settings.xml`, `.png` |
| Restart persistence | `qa/emulator-android16-smoke/11-restart-home-persisted.xml`, `.png` |
| Crash buffer | `qa/emulator-android16-smoke/crash.log` |

## Results

- Onboarding, Home, Timer, Result, Progress and Settings rendered on Android 16/API 36.
- Timer controls changed from `Пауза` to `Продолжить` and back to `Пауза`.
- Completion recorded `1` task, `1 дн.` streak and `1%` catalog progress.
- System Back from Progress returned to Home after adding Compose `BackHandler` coverage.
- Force-stop/restart opened Home, not onboarding, with persisted `1 дн.` and `1%` progress.
- Crash buffer contained 0 lines.

## Notes

- The Android 16 emulator was run headless from the installed SDK path because `emulator` was not present in shell `PATH`.
- The emulator was shut down after evidence capture.
