# Android 16 Large Screen QA

## Scope

Validate that the app remains readable and focused on a large viewport after adding centered max-width constraints for screen content and top bars.

## Environment

| Field | Value |
|---|---|
| AVD | `Medium_Phone_API_36` |
| Serial | `emulator-5560` |
| Android release | `16` |
| API | `36` |
| Package | `ru.poryadok5.app` |
| Baseline size | `1080x2400`, density `420` |
| Large override | `2000x2560`, density `320` |
| Evidence directory | `qa/emulator-android16-large-screen` |

The emulator display override was reset to the baseline size and density after capture.

## Flow Checked

1. Installed fresh `app/build/outputs/apk/debug/app-debug.apk`.
2. Cleared app data and logcat.
3. Applied large viewport override: `wm size 2000x2560`, `wm density 320`.
4. Launched onboarding.
5. Completed onboarding with “Начать”.
6. Verified Home, selected `3 мин`, and started timer.
7. Completed timer with “Готово”.
8. Returned to Home from result.
9. Opened Settings.

## Evidence

| Step | Evidence |
|---|---|
| Onboarding | `qa/emulator-android16-large-screen/01-onboarding.xml`, `.png` |
| Home | `qa/emulator-android16-large-screen/02-home.xml`, `.png` |
| Home 3-minute selection | `qa/emulator-android16-large-screen/03-home-3min.xml`, `.png` |
| Timer | `qa/emulator-android16-large-screen/04-timer.xml`, `.png` |
| Result | `qa/emulator-android16-large-screen/05-result.xml`, `.png` |
| Home after result | `qa/emulator-android16-large-screen/06-home-after-result.xml`, `.png` |
| Settings | `qa/emulator-android16-large-screen/07-settings.xml`, `.png` |
| App filtered crash matches | `qa/emulator-android16-large-screen/app_crash_package_matches.txt` |
| App filtered logcat errors | `qa/emulator-android16-large-screen/app_logcat_error_matches.txt` |

## Results

- Content and top bars are centered on the large canvas instead of stretching edge-to-edge.
- Bounds evidence on the `2000x2560` viewport:
  - Home title `Порядок 5`: `[320,92][578,156]`.
  - Home metric label `сделано`: `[348,320][462,362]`.
  - Settings title `Настройки`: `[432,93][1680,147]`.
- The main flow completed: onboarding, Home, timer, result, return to Home and Settings.
- Crash buffer contained 0 lines.
- `app_crash_package_matches.txt` contains 0 lines for `ru.poryadok5.app`.
- `app_logcat_error_matches.txt` contains 0 lines.

## Implementation Note

The UI now uses centered max-width constraints for main screen content and top bars so phone layouts remain unchanged while larger viewports avoid over-wide reading lines and oversized cards.
