# Android 16 Home Filter Disclosure QA

## Status

`PASSED`.

## Device

- AVD: Android 16/API 36 on `emulator-5556`.
- Package: `ru.poryadok5.app`.
- Viewport: `1080x2400`, density `420`, font scale `1.0`.
- Build: fresh debug APK install from `app/build/outputs/apk/debug/app-debug.apk`.

## Scope

Validate the collapsed Home filter disclosure after the Home polish pass. The first Home viewport must prioritize the current task, show only the compact `Настроить подбор` summary by default, and reveal zone/energy/time controls through the explicit `Изменить` action.

## Steps

1. Uninstalled any previous `ru.poryadok5.app` package state and installed the current debug APK.
2. Launched `ru.poryadok5.app/.MainActivity`.
3. Captured onboarding.
4. Tapped `Начать`.
5. Captured collapsed Home and refreshed `screenshots/play-store/02-home.png` from this real app frame.
6. Tapped `Изменить`.
7. Captured expanded Home, then scrolled within the page to capture the lower energy/time controls.
8. Captured focus, logcat, crash buffer and app-specific fatal/ANR match evidence.

## Result

Passed. The collapsed Home filter disclosure shows `Настроить подбор`, current selection summary and `Изменить`, while zone/energy/time controls are hidden from the first viewport. After tapping `Изменить`, Home shows `Скрыть`, zone choices and, after scrolling, `Энергия`, `Лёгкая`, `Средняя`, `Бодрая`, `Время`, `3 мин`, `5 мин` and `10 мин`.

`07-app-fatal-anr-matches.txt` and `06-crash-buffer.txt` are empty.

## Evidence

- `qa/emulator-android16-home-filter-disclosure-qa-2026-06-06/01-onboarding.xml`
- `qa/emulator-android16-home-filter-disclosure-qa-2026-06-06/01-onboarding.png`
- `qa/emulator-android16-home-filter-disclosure-qa-2026-06-06/02-home-collapsed.xml`
- `qa/emulator-android16-home-filter-disclosure-qa-2026-06-06/02-home-collapsed.png`
- `qa/emulator-android16-home-filter-disclosure-qa-2026-06-06/03-home-expanded.xml`
- `qa/emulator-android16-home-filter-disclosure-qa-2026-06-06/03-home-expanded.png`
- `qa/emulator-android16-home-filter-disclosure-qa-2026-06-06/03b-home-expanded-lower.xml`
- `qa/emulator-android16-home-filter-disclosure-qa-2026-06-06/03b-home-expanded-lower.png`
- `qa/emulator-android16-home-filter-disclosure-qa-2026-06-06/04-focus.txt`
- `qa/emulator-android16-home-filter-disclosure-qa-2026-06-06/05-logcat.txt`
- `qa/emulator-android16-home-filter-disclosure-qa-2026-06-06/06-crash-buffer.txt`
- `qa/emulator-android16-home-filter-disclosure-qa-2026-06-06/07-app-fatal-anr-matches.txt`
- `qa/emulator-android16-home-filter-disclosure-qa-2026-06-06/08-screenshot-sizes.txt`

## Release Impact

The Home Play screenshot now reflects the current collapsed disclosure UI. This QA is covered by `scripts/check_qa_evidence.py` and does not remove the external Play blockers: upload signing, public privacy URL, support email, Play Console form confirmation and final feature graphic preview approval.
