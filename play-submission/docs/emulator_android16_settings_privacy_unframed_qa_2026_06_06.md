# Android 16 Settings Privacy Unframed QA

## Status

`PASSED`.

## Device

- AVD: Android 16/API 36 on `emulator-5556`.
- Package: `ru.poryadok5.app`.
- Viewport: `1080x2400`, density `420`.
- Build: clean debug APK install from `app/build/outputs/apk/debug/app-debug.apk`.

## Scope

Validate the Settings privacy polish after removing nested badge cards from the `Приватность` section and adding compact explanations to the privacy facts. The section should keep all four no-data/no-ads facts readable as non-interactive unframed 56dp+ facts inside one calm sage block.

## Steps

1. Removed stale `com.fiftyfive.seconds` from the AVD to avoid foreground focus contamination.
2. Built and installed a clean debug APK for `ru.poryadok5.app`.
3. Cleared app data and launched `ru.poryadok5.app`.
4. Completed onboarding from the real app UI.
5. Opened Settings through the Home `Опции` action.
6. Captured Settings XML and PNG after the unframed privacy readability change.
7. Replaced `screenshots/play-store/06-settings.png` with the real Settings frame from this run.
8. Captured focus, activity focus, crash buffer, app-specific fatal/ANR gate, screenshot sizes and UI marker evidence.

## Result

Passed. Settings showed `Настройки`, `Приватность`, `Прогресс хранится только на устройстве`, `Без интернета` / `работает офлайн`, `Без аккаунта` / `вход не нужен`, `Без рекламы` / `нет баннеров`, `Без аналитики` / `нет трекеров` and `О приложении`. The refreshed `screenshots/play-store/06-settings.png` is 1080x2400 and reflects the current unframed privacy readability UI.

`09-app-fatal-anr-matches.txt` is empty.

## Evidence

- `qa/emulator-android16-settings-privacy-unframed-qa-2026-06-06/01-onboarding.xml`
- `qa/emulator-android16-settings-privacy-unframed-qa-2026-06-06/01-onboarding.png`
- `qa/emulator-android16-settings-privacy-unframed-qa-2026-06-06/02-home.xml`
- `qa/emulator-android16-settings-privacy-unframed-qa-2026-06-06/02-home.png`
- `qa/emulator-android16-settings-privacy-unframed-qa-2026-06-06/03-settings-privacy-unframed.xml`
- `qa/emulator-android16-settings-privacy-unframed-qa-2026-06-06/03-settings-privacy-unframed.png`
- `qa/emulator-android16-settings-privacy-unframed-qa-2026-06-06/focus.txt`
- `qa/emulator-android16-settings-privacy-unframed-qa-2026-06-06/activity-focus.txt`
- `qa/emulator-android16-settings-privacy-unframed-qa-2026-06-06/07-crash-buffer.txt`
- `qa/emulator-android16-settings-privacy-unframed-qa-2026-06-06/09-app-fatal-anr-matches.txt`
- `qa/emulator-android16-settings-privacy-unframed-qa-2026-06-06/10-screenshot-sizes.txt`
- `qa/emulator-android16-settings-privacy-unframed-qa-2026-06-06/11-ui-marker-check.txt`

## Release Impact

This QA proves the Settings privacy readability simplification and refreshes the Play Store Settings screenshot from the current app UI. It does not remove the external Play blockers: upload signing, public privacy URL, support email, Play Console form confirmation and final feature graphic preview approval.
