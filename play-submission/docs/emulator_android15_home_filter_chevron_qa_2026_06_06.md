# Android 15 Home Filter Chevron QA

## Environment

- Device: Android 15 AVD.
- Serial: `emulator-5554`.
- App package: `ru.poryadok5.app`.
- Viewport: `1080x2400`, density `420`, font scale `1.0`.
- Build: current debug APK from `app/build/outputs/apk/debug/app-debug.apk`.
- Evidence directory: `qa/emulator-android15-home-filter-chevron-qa-2026-06-06`.

## Scope

Validate the Home filter disclosure after adding the `Изменить` / `Скрыть` chevron indicator. The row must remain a whole-row 56dp toggle, collapsed Home must keep the first viewport focused on the current task, and tapping the `Настроить подбор` summary text must still open the filter controls.

## Flow

1. Installed the current debug APK after clearing `ru.poryadok5.app` and logcat.
2. Launched `ru.poryadok5.app/.MainActivity`.
3. Captured onboarding and completed it with `Начать`.
4. Captured collapsed Home and refreshed `screenshots/play-store/02-home.png` from the real app UI.
5. Confirmed collapsed Home showed `Настроить подбор`, current selection summary and `Изменить` with the down chevron while lower filter sections stayed hidden.
6. Tapped the `Настроить подбор` summary text, not the right-side indicator.
7. Captured expanded Home with `Скрыть`, the up chevron and `Зона` controls.
8. Checked focus, screenshot sizes, crash buffer and app-specific fatal/ANR matches.

## Result

Status: `PASSED`.

Collapsed Home showed `Настроить подбор`, `Изменить`, `Запустить таймер`, `Другая задача` and did not expose `Энергия` / `Время`. Tapping the summary text opened the expanded state with `Скрыть`, `Зона`, `Работа` and `Цифра`. The refreshed Play screenshot stayed at `1080x2400`.

Crash buffer and app-specific fatal/ANR match files contained 0 lines.

## Evidence Files

- `qa/emulator-android15-home-filter-chevron-qa-2026-06-06/01-onboarding.xml`
- `qa/emulator-android15-home-filter-chevron-qa-2026-06-06/01-onboarding.png`
- `qa/emulator-android15-home-filter-chevron-qa-2026-06-06/02-home-collapsed.xml`
- `qa/emulator-android15-home-filter-chevron-qa-2026-06-06/02-home-collapsed.png`
- `qa/emulator-android15-home-filter-chevron-qa-2026-06-06/03-home-expanded-by-summary.xml`
- `qa/emulator-android15-home-filter-chevron-qa-2026-06-06/03-home-expanded-by-summary.png`
- `qa/emulator-android15-home-filter-chevron-qa-2026-06-06/06-focus.txt`
- `qa/emulator-android15-home-filter-chevron-qa-2026-06-06/07-crash-buffer.txt`
- `qa/emulator-android15-home-filter-chevron-qa-2026-06-06/08-app-fatal-anr-matches.txt`
- `qa/emulator-android15-home-filter-chevron-qa-2026-06-06/09-screenshot-sizes.txt`
- `qa/emulator-android15-home-filter-chevron-qa-2026-06-06/10-ui-marker-check.txt`

## Notes

This QA proves the current Home screenshot and disclosure indicator only. It does not remove the external Play blockers: upload signing, public privacy URL, support email, Play Console form confirmation, internal testing confirmation and final feature graphic approval.
