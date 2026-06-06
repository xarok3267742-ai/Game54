# Android 15 Onboarding Flow Summary QA

## Environment

- Device: Android 15 AVD.
- Serial: `emulator-5554`.
- App package: `ru.poryadok5.app`.
- Build: current debug APK from `app/build/outputs/apk/debug/app-debug.apk`.
- Evidence directory: `qa/emulator-android15-onboarding-flow-summary-qa-2026-06-06`.

## Scope

Validate the first-run onboarding after replacing the framed `Как это работает` card with the lighter unframed `Первые 5 минут` flow summary. The screen should keep the starting-area choice, concise flow facts and primary `Начать` action visible on a normal phone viewport.

## Flow

1. Used the owned AVD at `1080x2400`, density `420`, font scale `1.0` and disabled animations.
2. Installed the current debug APK, cleared `ru.poryadok5.app` data and cleared logcat.
3. Launched `ru.poryadok5.app/.MainActivity`.
4. Captured the fresh onboarding UI tree and screenshot.
5. Refreshed `screenshots/play-store/01-onboarding.png` from the real app UI.
6. Checked crash buffer and app-specific fatal/ANR matches.

## Result

Status: `PASSED`.

Passed. Onboarding showed `Порядок 5`, the starting-area choice, `Первые 5 минут`, `Сначала`, `Выбираете стартовую зону.`, `Затем`, `Получаете задачу и при желании уточняете подбор.`, `После`, `Запускаете таймер и отмечаете результат.` and `Начать`. The old framed copy `Как это работает` and the old energy-selection promise were absent.

The refreshed Play screenshot stayed at `1080x2400`. Crash buffer and app-specific fatal/ANR match files contained 0 lines.

## Evidence Files

- `qa/emulator-android15-onboarding-flow-summary-qa-2026-06-06/01-onboarding.xml`
- `qa/emulator-android15-onboarding-flow-summary-qa-2026-06-06/01-onboarding.png`
- `qa/emulator-android15-onboarding-flow-summary-qa-2026-06-06/01-onboarding-summary.txt`
- `qa/emulator-android15-onboarding-flow-summary-qa-2026-06-06/02-focus.txt`
- `qa/emulator-android15-onboarding-flow-summary-qa-2026-06-06/03-logcat.txt`
- `qa/emulator-android15-onboarding-flow-summary-qa-2026-06-06/04-crash-buffer.txt`
- `qa/emulator-android15-onboarding-flow-summary-qa-2026-06-06/05-app-fatal-anr-matches.txt`
- `qa/emulator-android15-onboarding-flow-summary-qa-2026-06-06/06-screenshot-size.txt`
- `qa/emulator-android15-onboarding-flow-summary-qa-2026-06-06/07-ui-marker-check.txt`
- `qa/emulator-android15-onboarding-flow-summary-qa-2026-06-06/wm-size.txt`
- `qa/emulator-android15-onboarding-flow-summary-qa-2026-06-06/wm-density.txt`
- `qa/emulator-android15-onboarding-flow-summary-qa-2026-06-06/android-release.txt`
- `qa/emulator-android15-onboarding-flow-summary-qa-2026-06-06/android-sdk.txt`
- `qa/emulator-android15-onboarding-flow-summary-qa-2026-06-06/resolve-activity.txt`
