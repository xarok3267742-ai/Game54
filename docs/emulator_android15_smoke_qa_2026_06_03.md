# Android 15 Smoke QA — 2026-06-03

## Scope

- App: `Порядок 5`
- Package: `ru.poryadok5.app`
- Build: debug APK installed from the current workspace
- Device: `emulator-5554`, AVD reported by Gradle as `project_betano_emulator`, Android 15
- Evidence directory: `qa/emulator-android-smoke-2026-06-03/step-debug`

## Flow Checked

1. Cleared app data with `adb shell pm clear ru.poryadok5.app`.
2. Launched `ru.poryadok5.app/.MainActivity`.
3. Completed onboarding after selecting `Дом`.
4. Verified Home is quick-task-first: task card appears before metrics and filter controls.
5. Started the timer from `Запустить таймер`.
6. Pressed `Пауза`; focus stayed on `ru.poryadok5.app` and the control changed to `Продолжить`.
7. Pressed `Продолжить`, then `Готово`.
8. Verified Result screen: total tasks `1`, streak `1 дн.`, catalog progress `1%`.
9. Opened `Итоги`; verified per-area progress shows `Дом — 1 из 16` and all other zones `0 из 16`.
10. Opened `Опции`; verified privacy copy, version `1.0.0-rc1`, local catalog size `80`, haptics switch and reset section.

## Evidence Files

- `00-start-summary.txt`: onboarding.
- `02-after-start-summary.txt`: quick-task-first Home.
- `03-after-timer-start-summary.txt`: running timer.
- `04-after-pause-summary.txt`: paused timer with `Продолжить`.
- `05-result-summary.txt`: completion result.
- `06-progress-summary.txt`: per-area progress.
- `07-settings-summary.txt`: settings/privacy/version.
- `poryadok-fatal-anr-matches.txt`: 0 lines.

## Notes

An earlier fast retry on the same AVD brought `com.fiftyfive.seconds` to the foreground. Logcat showed that app was started by a shell-driven event, and `Порядок 5` stayed alive. The controlled step-by-step rerun kept focus on `ru.poryadok5.app` through pause, completion, progress and settings. Crash buffer noise from `com.android.commands.uiautomator` is not an app crash.

## Result

Pass for the checked Android 15 smoke flow. No app-specific fatal exception or ANR was found for `ru.poryadok5.app`.
