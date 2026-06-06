# Android 15 Primary Action Contrast QA

## Scope

- Date: 2026-06-03.
- Device: Android 15 AVD `Medium_Phone_API_35_Default`, serial `emulator-5566`.
- Package: `ru.poryadok5.app`.
- Build: current debug APK after the primary CTA contrast fix.

## Flow

1. Installed the fresh debug build with `./gradlew :app:installDebug --console=plain`.
2. Cleared app data with `adb shell pm clear ru.poryadok5.app`.
3. Launched `ru.poryadok5.app/.MainActivity`.
4. Captured Onboarding before tapping `Начать`.
5. Tapped `Начать`, captured Home, tapped `Запустить таймер`.
6. Captured Timer, tapped `Готово`.
7. Captured Result.

## Evidence

- `qa/emulator-android15-primary-action-contrast-qa-2026-06-03/01-onboarding.png`
- `qa/emulator-android15-primary-action-contrast-qa-2026-06-03/02-home.png`
- `qa/emulator-android15-primary-action-contrast-qa-2026-06-03/03-timer.png`
- `qa/emulator-android15-primary-action-contrast-qa-2026-06-03/04-result.png`
- Matching UI dumps and summaries are stored next to each PNG.
- App-specific fatal/ANR match file: `crash-matches.txt`, 0 lines.

## Result

Passed. Primary action labels on `Начать`, `Запустить таймер`, `Готово` and `Запустить следующую` render in `onPrimary` on sage buttons and are visually readable. The 1080x2400 Play screenshots `01-onboarding.png` through `04-result.png` were refreshed from the real app UI.
