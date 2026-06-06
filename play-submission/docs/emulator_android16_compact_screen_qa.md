# Android 16 Compact Screen QA

## Scope

Validate that the main app flow remains usable on a compact phone viewport where vertical scrolling is required. This covers first launch, Home filters, timer controls, completion, return to Home and Settings reset confirmation.

## Environment

| Field | Value |
|---|---|
| AVD | `Medium_Phone_API_36` |
| Serial | `emulator-5560` |
| Android release | `16` |
| API | `36` |
| Package | `ru.poryadok5.app` |
| Baseline size | `1080x2400`, density `420` |
| Compact override | `720x1280`, density `320` |
| Evidence directory | `qa/emulator-android16-compact-screen` |

The emulator display override was reset to the baseline size and density after capture.

## Flow Checked

1. Installed fresh `app/build/outputs/apk/debug/app-debug.apk`.
2. Cleared app data and logcat.
3. Applied compact viewport override: `wm size 720x1280`, `wm density 320`.
4. Launched onboarding.
5. Scrolled to and tapped “Начать”.
6. Verified Home top content, selected `3 мин`, scrolled to and tapped “Запустить таймер”.
7. Verified timer top content, pause, resume and scrolled to “Готово”.
8. Completed the task and returned to Home from result.
9. Opened Settings and scrolled to “Подготовить сброс”.
10. Tapped “Подготовить сброс” and verified “Сбросить прогресс” confirmation state.

## Evidence

| Step | Evidence |
|---|---|
| Onboarding top | `qa/emulator-android16-compact-screen/01-onboarding-top.xml`, `.png` |
| Onboarding start button after scroll | `qa/emulator-android16-compact-screen/02-onboarding-find-start-2.xml`, `.png` |
| Home top | `qa/emulator-android16-compact-screen/03-home-top.xml`, `.png` |
| Home start timer after scroll | `qa/emulator-android16-compact-screen/06-home-find-start-timer-2.xml`, `.png` |
| Timer top | `qa/emulator-android16-compact-screen/07-timer-top.xml`, `.png` |
| Timer paused | `qa/emulator-android16-compact-screen/09-timer-paused.xml`, `.png` |
| Timer done button after scroll | `qa/emulator-android16-compact-screen/12-timer-find-done-2.xml`, `.png` |
| Result | `qa/emulator-android16-compact-screen/13-result-top.xml`, `.png` |
| Home after result | `qa/emulator-android16-compact-screen/15-home-after-result.xml`, `.png` |
| Settings top | `qa/emulator-android16-compact-screen/17-settings-top.xml`, `.png` |
| Settings reset confirmation | `qa/emulator-android16-compact-screen/19-settings-reset-confirm-visible.xml`, `.png` |
| App filtered crash matches | `qa/emulator-android16-compact-screen/app_crash_package_matches.txt` |
| App filtered logcat errors | `qa/emulator-android16-compact-screen/app_logcat_error_matches.txt` |

## Results

- Onboarding, Home, Timer, Result and Settings remain reachable at `720x1280`.
- Primary actions that are below the fold remain reachable by vertical scroll.
- Timer controls changed from `Пауза` to `Продолжить` and back to `Пауза`.
- Completion recorded `1` task, `1 дн.` streak and `1%` catalog progress.
- Settings reset confirmation changed from `Подготовить сброс` to `Сбросить прогресс`.
- `app_crash_package_matches.txt` contains 0 lines for `ru.poryadok5.app`.
- `app_logcat_error_matches.txt` contains 0 lines.

## Notes

- The crash buffer also contained an unrelated `com.google.android.dialer` `FinalizerWatchdogDaemon` entry from emulator system state. No `ru.poryadok5.app` crash was present, and the app process remained alive.
- A contaminated Android 15 AVD was not used for compact evidence because launcher focus could switch to unrelated pre-existing apps. The clean Android 16 AVD was used instead.
