# Android 15 Home Filter Whole-Row QA

## Environment

- Device: Android 15 AVD.
- Serial: `emulator-5554`.
- App package: `ru.poryadok5.app`.
- Viewport: `1080x2400`, density `420`, font scale `1.0`.
- Build: current debug APK from `app/build/outputs/apk/debug/app-debug.apk`.
- Evidence directory: `qa/emulator-android15-home-filter-whole-row-qa-2026-06-06`.

## Scope

Validate the Home filter disclosure after replacing the small `Изменить` text button with a whole-row 56dp summary toggle. The collapsed Home screen should still prioritize the current task, while tapping the `Настроить подбор` summary text opens zone/energy/time controls.

## Flow

1. Installed the current debug APK, cleared `ru.poryadok5.app` data and cleared logcat.
2. Launched `ru.poryadok5.app/.MainActivity`.
3. Captured onboarding and completed it with `Начать`.
4. Captured collapsed Home and refreshed `screenshots/play-store/02-home.png` from the real app UI.
5. Tapped the `Настроить подбор` text inside the summary row, not the `Изменить` label.
6. Captured expanded Home and lower expanded controls after scroll.
7. Checked focus, screenshot sizes, crash buffer and app-specific fatal/ANR matches.

## Result

Status: `PASSED`.

Passed. Collapsed Home showed `Настроить подбор`, current selection summary, `Изменить`, `Запустить таймер` and `Другая задача`, while `Энергия`, `Время` and `Скрыть` were hidden. Tapping the summary text opened the expanded state with `Скрыть`, `Зона`, zone choices, and after scroll `Энергия`, `Лёгкая`, `Средняя`, `Бодрая`, `Время`, `3 мин`, `5 мин` and `10 мин`.

The refreshed Play screenshot stayed at `1080x2400`. Crash buffer and app-specific fatal/ANR match files contained 0 lines.

## Evidence Files

- `qa/emulator-android15-home-filter-whole-row-qa-2026-06-06/01-onboarding.xml`
- `qa/emulator-android15-home-filter-whole-row-qa-2026-06-06/01-onboarding.png`
- `qa/emulator-android15-home-filter-whole-row-qa-2026-06-06/02-home-collapsed.xml`
- `qa/emulator-android15-home-filter-whole-row-qa-2026-06-06/02-home-collapsed.png`
- `qa/emulator-android15-home-filter-whole-row-qa-2026-06-06/03-home-expanded-by-summary.xml`
- `qa/emulator-android15-home-filter-whole-row-qa-2026-06-06/03-home-expanded-by-summary.png`
- `qa/emulator-android15-home-filter-whole-row-qa-2026-06-06/04-home-expanded-lower.xml`
- `qa/emulator-android15-home-filter-whole-row-qa-2026-06-06/04-home-expanded-lower.png`
- `qa/emulator-android15-home-filter-whole-row-qa-2026-06-06/05-focus.txt`
- `qa/emulator-android15-home-filter-whole-row-qa-2026-06-06/06-logcat.txt`
- `qa/emulator-android15-home-filter-whole-row-qa-2026-06-06/07-crash-buffer.txt`
- `qa/emulator-android15-home-filter-whole-row-qa-2026-06-06/08-app-fatal-anr-matches.txt`
- `qa/emulator-android15-home-filter-whole-row-qa-2026-06-06/09-screenshot-sizes.txt`
- `qa/emulator-android15-home-filter-whole-row-qa-2026-06-06/10-ui-marker-check.txt`
