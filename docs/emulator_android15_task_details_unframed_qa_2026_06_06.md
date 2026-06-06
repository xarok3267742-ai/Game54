# Android 15 Task Details Unframed Briefing QA

## Environment

- Device: Android 15 AVD.
- Serial: `emulator-5554`.
- App package: `ru.poryadok5.app`.
- Viewport: `1080x2400`, density `420`, font scale `1.0`.
- Build: current debug APK from `app/build/outputs/apk/debug/app-debug.apk`.
- Evidence directory: `qa/emulator-android15-task-details-unframed-qa-2026-06-06`.

## Scope

Validate the Task details screen after replacing framed briefing chips with unframed 56dp зона/энергия/время facts and moving the expected outcome into the briefing. Details must still show selected-task context, `Перед стартом`, compact `После` outcome preview, the full step list and a pinned `Начать 5 мин` action that opens Timer.

## Flow

1. Installed the current debug APK after clearing `ru.poryadok5.app` and logcat.
2. Launched `ru.poryadok5.app/.MainActivity`.
3. Completed onboarding with `Начать`.
4. Opened Details from Home through `Все шаги`.
5. Captured the top Details viewport with `Выбранная задача`, `выбрана`, `Перед стартом`, unframed зона/энергия/время facts, compact `После` outcome preview and `Шаги`.
6. Captured the lower Details viewport with `После`, `Шаги` and the pinned `Начать 5 мин`.
7. Tapped `Начать 5 мин` and verified Timer opened with `Цель: 5 мин`, `Пауза` and `Готово`.
8. Checked focus, screenshot sizes, crash buffer and app-specific fatal/ANR matches.

## Result

Status: `PASSED`.

Details showed `Выбранная задача`, `выбрана`, `Перед стартом`, `зона`, `энергия`, `время`, `Дом`, `Лёгкая`, `5 мин`, `После`, `Шаги` and `Начать 5 мин`. The briefing facts rendered unframed inside the sage section instead of nested white chips, and the expected outcome appeared before the full step list instead of in a separate lower `Результат` card. The start action opened Timer with `Цель: 5 мин`, `Пауза` and `Готово`.

Crash buffer and app-specific fatal/ANR match files contained 0 lines.

## Evidence Files

- `qa/emulator-android15-task-details-unframed-qa-2026-06-06/01-onboarding.xml`
- `qa/emulator-android15-task-details-unframed-qa-2026-06-06/01-onboarding.png`
- `qa/emulator-android15-task-details-unframed-qa-2026-06-06/02-home.xml`
- `qa/emulator-android15-task-details-unframed-qa-2026-06-06/02-home.png`
- `qa/emulator-android15-task-details-unframed-qa-2026-06-06/03-details-top.xml`
- `qa/emulator-android15-task-details-unframed-qa-2026-06-06/03-details-top.png`
- `qa/emulator-android15-task-details-unframed-qa-2026-06-06/03b-details-lower.xml`
- `qa/emulator-android15-task-details-unframed-qa-2026-06-06/03b-details-lower.png`
- `qa/emulator-android15-task-details-unframed-qa-2026-06-06/04-timer.xml`
- `qa/emulator-android15-task-details-unframed-qa-2026-06-06/04-timer.png`
- `qa/emulator-android15-task-details-unframed-qa-2026-06-06/05-focus.txt`
- `qa/emulator-android15-task-details-unframed-qa-2026-06-06/06-crash-buffer.txt`
- `qa/emulator-android15-task-details-unframed-qa-2026-06-06/07-app-fatal-anr-matches.txt`
- `qa/emulator-android15-task-details-unframed-qa-2026-06-06/08-screenshot-sizes.txt`
- `qa/emulator-android15-task-details-unframed-qa-2026-06-06/09-ui-marker-check.txt`

## Notes

This QA proves the Details visual polish and Home-to-Details-to-Timer path. It does not remove the external Play blockers: upload signing, public privacy URL, support email, Play Console form confirmation, internal testing confirmation and final feature graphic approval.
