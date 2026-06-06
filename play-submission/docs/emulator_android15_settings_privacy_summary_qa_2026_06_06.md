# Android 15 Settings Privacy Summary QA 2026-06-06

## Status

`PASSED`.

## Scope

Validated the Settings privacy card after replacing one dense privacy paragraph with a scannable `PrivacyBadgeGrid`. The screen must keep the local-only/no-data model visible in the real app UI and refresh the Play Store Settings screenshot from the app, not from a mock.

## Environment

- AVD: `Medium_Phone_API_35_Default`
- Android release: `15`
- Android SDK: `35`
- Screen: `1080x2400`, density `420`
- Package: `ru.poryadok5.app`
- Evidence: `qa/emulator-android15-settings-privacy-summary-qa-2026-06-06`

## Flow

1. Installed the current debug APK on Android 15 and launched `ru.poryadok5.app/.MainActivity`.
2. Cleared app data and completed onboarding with `Начать`.
3. Opened Home, then Settings through the `Опции` header action.
4. Captured Settings with the updated privacy card as `screenshots/play-store/06-settings.png`.
5. Verified the privacy card shows the local-only copy and four visible badges: `Без интернета`, `Без аккаунта`, `Без рекламы`, `Без аналитики`.

## Evidence Markers

- `03-settings-privacy-summary.xml`: contains `Настройки`, `Приватность`, `Прогресс хранится только на устройстве`, `Без интернета`, `Без аккаунта`, `Без рекламы`, `Без аналитики` and `О приложении`.
- `03-settings-privacy-summary-summary.txt`: shows all four privacy badges in the visible UI tree.
- `screenshot-sizes.txt`: refreshed Settings Play screenshot is `1080x2400`.
- `focus.txt`: current focus remains on `ru.poryadok5.app/.MainActivity`.
- `crash-logcat-package-matches.txt`: zero app-specific crash lines.

## Result

Passed. Settings now presents the no-account/no-ads/no-analytics/offline model as visible badges while preserving the Russian about/version block and refreshing the real Play Store Settings screenshot.
