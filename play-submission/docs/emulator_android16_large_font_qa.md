# Android 16 Large Font QA

## Scope

Validate that the main app flow remains usable with Android system text scaling enabled.

## Environment

| Field | Value |
|---|---|
| AVD | `Medium_Phone_API_36` |
| Serial | `emulator-5560` |
| Android release | `16` |
| API | `36` |
| Package | `ru.poryadok5.app` |
| Viewport | `1080x2400`, density `420` |
| Baseline font scale | `1.0` |
| Test font scale | `1.3` |
| Evidence directory | `qa/emulator-android16-large-font` |

The emulator font scale was restored to `1.0` after capture.

## Flow Checked

1. Reset viewport to `1080x2400`, density `420`.
2. Installed fresh `app/build/outputs/apk/debug/app-debug.apk`.
3. Cleared app data and logcat.
4. Applied `settings put system font_scale 1.3`.
5. Launched onboarding.
6. Completed onboarding with “Начать”.
7. Verified Home, selected `3 мин`, and started timer.
8. Checked timer pause/resume and completed with “Готово”.
9. Opened “Итоги”.
10. Pressed system Back to return Home.
11. Opened Settings and verified reset confirmation state.

## Evidence

| Step | Evidence |
|---|---|
| Onboarding | `qa/emulator-android16-large-font/01-onboarding-top.xml`, `.png` |
| Home | `qa/emulator-android16-large-font/03-home-top.xml`, `.png` |
| Home start timer | `qa/emulator-android16-large-font/06-home-find-start-timer-1.xml`, `.png` |
| Timer | `qa/emulator-android16-large-font/07-timer-top.xml`, `.png` |
| Timer paused | `qa/emulator-android16-large-font/09-timer-paused.xml`, `.png` |
| Timer done | `qa/emulator-android16-large-font/12-timer-find-done-1.xml`, `.png` |
| Result | `qa/emulator-android16-large-font/13-result-top.xml`, `.png` |
| Progress | `qa/emulator-android16-large-font/15-progress-top.xml`, `.png` |
| Home after Back | `qa/emulator-android16-large-font/16-home-after-back.xml`, `.png` |
| Settings | `qa/emulator-android16-large-font/18-settings-top.xml`, `.png` |
| Reset confirmation | `qa/emulator-android16-large-font/20-settings-reset-confirm-visible.xml`, `.png` |
| App filtered crash matches | `qa/emulator-android16-large-font/app_crash_package_matches.txt` |
| App filtered logcat errors | `qa/emulator-android16-large-font/app_logcat_error_matches.txt` |

## Results

- Onboarding, Home, Timer, Result, Progress and Settings remained usable at `font_scale=1.3`.
- Primary actions remained reachable on the normal phone viewport; no action required an impossible tap target.
- Timer controls changed from `Пауза` to `Продолжить` and back to `Пауза`.
- Completion recorded `1` task, `1 дн.` streak and `1%` catalog progress.
- Settings reset confirmation changed from `Подготовить сброс` to `Сбросить прогресс`.
- Crash buffer contained 0 lines.
- `app_crash_package_matches.txt` contains 0 lines for `ru.poryadok5.app`.
- `app_logcat_error_matches.txt` contains 0 lines.
