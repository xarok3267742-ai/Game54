# Android 15 Timer Session Goal QA

## Status

`PASSED`.

## Device

- AVD: Android 15/API 35 on `emulator-5554`.
- Package: `ru.poryadok5.app`.
- Viewport: `1080x2400`, density `420`.
- Build: fresh debug APK install from `app/build/outputs/apk/debug/app-debug.apk`.

## Scope

Validate the Timer session goal polish. The user should be able to complete onboarding, start the timer from Home and see the original task duration as `Цель: 5 мин` above the progress line and countdown after the timer starts.

## Steps

1. Installed the current debug APK and cleared app data.
2. Launched `ru.poryadok5.app` from the resolved `MainActivity`.
3. Completed onboarding from the real app UI.
4. Started the timer from Home through `Запустить таймер`.
5. Captured Timer XML and PNG after the session-goal change.
6. Replaced `screenshots/play-store/03-timer.png` with the real Timer frame from this run.
7. Captured focus, crash buffer, app-specific fatal/ANR gate, screenshot sizes and UI marker evidence.

## Result

Passed. Timer showed `Таймер`, `Цель: 5 мин`, `Пауза`, `Сброс`, `План` and the pinned `Готово` action. The refreshed `screenshots/play-store/03-timer.png` is 1080x2400 and reflects the current Timer UI.

`07-app-fatal-anr-matches.txt` is empty.

## Evidence

- `qa/emulator-android15-timer-session-goal-qa-2026-06-06/01-onboarding.xml`
- `qa/emulator-android15-timer-session-goal-qa-2026-06-06/01-onboarding.png`
- `qa/emulator-android15-timer-session-goal-qa-2026-06-06/02-home.xml`
- `qa/emulator-android15-timer-session-goal-qa-2026-06-06/02-home.png`
- `qa/emulator-android15-timer-session-goal-qa-2026-06-06/03-timer.xml`
- `qa/emulator-android15-timer-session-goal-qa-2026-06-06/03-timer.png`
- `qa/emulator-android15-timer-session-goal-qa-2026-06-06/04-focus.txt`
- `qa/emulator-android15-timer-session-goal-qa-2026-06-06/05-crash-buffer.txt`
- `qa/emulator-android15-timer-session-goal-qa-2026-06-06/07-app-fatal-anr-matches.txt`
- `qa/emulator-android15-timer-session-goal-qa-2026-06-06/08-screenshot-sizes.txt`
- `qa/emulator-android15-timer-session-goal-qa-2026-06-06/09-ui-marker-check.txt`

## Release Impact

This QA proves the Timer session goal polish and refreshes the Play Store Timer screenshot from the current app UI. It does not remove the external Play blockers: upload signing, public privacy URL, support email, Play Console form confirmation and final feature graphic preview approval.
