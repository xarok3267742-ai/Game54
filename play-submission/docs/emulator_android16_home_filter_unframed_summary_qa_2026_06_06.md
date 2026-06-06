# Android 16 Home Filter Unframed Summary QA

## Environment

- Device: Android 16 AVD `Medium_Phone_API_36`.
- Serial: `emulator-5554`.
- App package: `ru.poryadok5.app`.
- Viewport: `1080x2400`, density `420`.
- Build: current debug APK from `app/build/outputs/apk/debug/app-debug.apk`.
- Evidence directory: `qa/emulator-android16-home-filter-unframed-summary-qa-2026-06-06`.

## Scope

Validate the Home filter disclosure after replacing the collapsed raised card with an unframed summary row. The first Home viewport must still prioritize the current task and actions, the collapsed filter row must keep the whole-row tap target, and expanded controls must still be reachable.

## Flow

1. Installed the current debug APK after clearing `ru.poryadok5.app`, resetting wm size/density and clearing logcat.
2. Launched `ru.poryadok5.app/.MainActivity`.
3. Captured onboarding and completed it with `Начать`.
4. Captured collapsed Home and refreshed `screenshots/play-store/02-home.png` from the real app UI.
5. Confirmed collapsed Home showed `Настроить подбор`, current selection summary and `Изменить`, while `Энергия` and `Время` were not present in the collapsed XML.
6. Tapped the whole summary row from XML bounds `[53,1799][1027,1946]`.
7. Captured expanded Home with `Скрыть` and `Зона`, then scrolled inside Home and captured `Энергия`, `Лёгкая`, `Средняя`, `Бодрая`, `Время`, `3 мин`, `5 мин` and `10 мин`.
8. Checked focus, screenshot sizes, crash buffer and app-specific fatal/ANR matches.

## Result

Status: `PASSED`.

Collapsed Home now uses an unframed divider row for `Настроить подбор`, so the task card and main actions keep visual priority. The row remains a whole-row toggle and expands to the same filter controls. The refreshed Play screenshot stayed at `1080x2400`.

Crash buffer and app-specific fatal/ANR match files contained 0 lines.

## Evidence Files

- `qa/emulator-android16-home-filter-unframed-summary-qa-2026-06-06/01-onboarding.xml`
- `qa/emulator-android16-home-filter-unframed-summary-qa-2026-06-06/01-onboarding.png`
- `qa/emulator-android16-home-filter-unframed-summary-qa-2026-06-06/02-home-collapsed.xml`
- `qa/emulator-android16-home-filter-unframed-summary-qa-2026-06-06/02-home-collapsed.png`
- `qa/emulator-android16-home-filter-unframed-summary-qa-2026-06-06/03-home-expanded.xml`
- `qa/emulator-android16-home-filter-unframed-summary-qa-2026-06-06/03-home-expanded.png`
- `qa/emulator-android16-home-filter-unframed-summary-qa-2026-06-06/04-home-expanded-scrolled.xml`
- `qa/emulator-android16-home-filter-unframed-summary-qa-2026-06-06/04-home-expanded-scrolled.png`
- `qa/emulator-android16-home-filter-unframed-summary-qa-2026-06-06/05-crash-buffer.txt`
- `qa/emulator-android16-home-filter-unframed-summary-qa-2026-06-06/06-logcat.txt`
- `qa/emulator-android16-home-filter-unframed-summary-qa-2026-06-06/07-app-fatal-anr-matches.txt`
- `qa/emulator-android16-home-filter-unframed-summary-qa-2026-06-06/08-screenshot-sizes.txt`
- `qa/emulator-android16-home-filter-unframed-summary-qa-2026-06-06/09-ui-marker-check.txt`
- `qa/emulator-android16-home-filter-unframed-summary-qa-2026-06-06/10-focus.txt`
- `qa/emulator-android16-home-filter-unframed-summary-qa-2026-06-06/wm-size.txt`
- `qa/emulator-android16-home-filter-unframed-summary-qa-2026-06-06/wm-density.txt`
- `qa/emulator-android16-home-filter-unframed-summary-qa-2026-06-06/android-release.txt`
- `qa/emulator-android16-home-filter-unframed-summary-qa-2026-06-06/android-sdk.txt`
- `qa/emulator-android16-home-filter-unframed-summary-qa-2026-06-06/resolve-activity.txt`

## Notes

This QA proves the current Home screenshot and unframed collapsed filter summary only. It does not remove the external Play blockers: upload signing, public privacy URL, support email, Play Console form confirmation, internal testing confirmation and final feature graphic approval.
