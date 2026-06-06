# Android 15 Task Status Pill QA 2026-06-06

## Status

`PASSED`.

## Scope

Validated the shared `TaskStatusPill` polish after changing task status from a bordered filled chip to a non-interactive dot label. The task status values `новая`, `повтор` and `выполнено` must read as state, not as tappable actions. The Home and Result Play Store screenshots were refreshed from the real app UI.

## Environment

- AVD: `Medium_Phone_API_35_Default`
- Android release: `15`
- Android SDK: `35`
- Screen: `1080x2400`, density `420`
- Package: `ru.poryadok5.app`
- Evidence: `qa/emulator-android15-task-status-pill-qa-2026-06-06`

## Flow

1. Installed the current debug APK and cleared `ru.poryadok5.app` data.
2. Launched `MainActivity` and completed onboarding with `Начать`.
3. Captured Home after the `TaskStatusPill` change as `screenshots/play-store/02-home.png`.
4. Started the timer with `Запустить таймер`.
5. Completed the timer with `Готово`.
6. Captured Result after the `TaskStatusPill` change as `screenshots/play-store/04-result.png`.

## Evidence Markers

- `02-home-status-pill.xml`: Home shows `Задача на сейчас`, `новая`, `Запустить таймер`, `Другая задача` and `Посмотреть шаги`.
- `04-result-status-pill.xml`: Result shows `Готово`, `Дальше без повтора`, `новая`, `Посмотреть следующую` and `Запустить таймер`.
- `screenshot-sizes.txt`: refreshed Home and Result Play screenshots are `1080x2400`.
- `focus.txt`: current focus remains on `ru.poryadok5.app/.MainActivity`.
- `crash-logcat-package-matches.txt`: zero app-specific crash lines.

## Result

Passed. Home and Result now use the non-interactive `TaskStatusPill`, and the refreshed Play screenshots no longer show the status as a button-like filled chip.
