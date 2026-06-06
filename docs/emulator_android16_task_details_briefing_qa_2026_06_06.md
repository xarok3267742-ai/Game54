# Android 16 Task Details Briefing QA

## Status

`PASSED`.

## Device

- AVD: Android 16/API 36 `Medium_Phone_API_36` on `emulator-5554`.
- Package: `ru.poryadok5.app`.
- Viewport: `1080x2400`, density `420`, font scale `1.0`.
- Build: fresh debug APK install from `app/build/outputs/apk/debug/app-debug.apk`.

## Scope

Validate the Task details pre-start briefing after the Details polish pass. The user should be able to open Details from Home, see `Перед стартом` with зона/энергия/время before the full step list, scroll to the start action and launch Timer without crashes.

## Steps

1. Removed unrelated emulator packages that were stealing focus.
2. Installed the current debug APK fresh.
3. Launched `ru.poryadok5.app/.MainActivity`.
4. Completed onboarding.
5. Opened Details from Home through `Посмотреть шаги`.
6. Captured the top Details viewport with `Перед стартом`, зона/энергия/время and `Шаги`.
7. Scrolled Details to the lower viewport and confirmed `Начать 5 мин` remained reachable.
8. Tapped the start action and confirmed Timer opened.
9. Captured focus, logcat, crash buffer and app-specific fatal/ANR match evidence.

## Result

Passed. Details showed `Выбранная задача`, `Перед стартом`, `зона`, `энергия`, `время`, `Шаги` and `Результат`. After scrolling, `Начать 5 мин` was visible and opened `Таймер` with `Пауза`.

`07-crash-buffer.txt` and `08-app-fatal-anr-matches.txt` are empty.

## Evidence

- `qa/emulator-android16-task-details-briefing-qa-2026-06-06/01-onboarding.xml`
- `qa/emulator-android16-task-details-briefing-qa-2026-06-06/01-onboarding.png`
- `qa/emulator-android16-task-details-briefing-qa-2026-06-06/02-home.xml`
- `qa/emulator-android16-task-details-briefing-qa-2026-06-06/02-home.png`
- `qa/emulator-android16-task-details-briefing-qa-2026-06-06/03-details.xml`
- `qa/emulator-android16-task-details-briefing-qa-2026-06-06/03-details.png`
- `qa/emulator-android16-task-details-briefing-qa-2026-06-06/03b-details-lower.xml`
- `qa/emulator-android16-task-details-briefing-qa-2026-06-06/03b-details-lower.png`
- `qa/emulator-android16-task-details-briefing-qa-2026-06-06/04-timer.xml`
- `qa/emulator-android16-task-details-briefing-qa-2026-06-06/04-timer.png`
- `qa/emulator-android16-task-details-briefing-qa-2026-06-06/05-focus.txt`
- `qa/emulator-android16-task-details-briefing-qa-2026-06-06/06-logcat.txt`
- `qa/emulator-android16-task-details-briefing-qa-2026-06-06/07-crash-buffer.txt`
- `qa/emulator-android16-task-details-briefing-qa-2026-06-06/08-app-fatal-anr-matches.txt`
- `qa/emulator-android16-task-details-briefing-qa-2026-06-06/09-screenshot-sizes.txt`

## Release Impact

This QA proves the Details polish in the primary Home-to-Timer path. It does not remove the external Play blockers: upload signing, public privacy URL, support email, Play Console form confirmation and final feature graphic preview approval.
