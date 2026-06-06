# Android 16 Result Peer Icons QA

## Environment

- Device: Android 16 AVD `Medium_Phone_API_36`.
- Serial: `emulator-5554`.
- App package: `ru.poryadok5.app`.
- Viewport: `1080x2400`, density `420`.
- Build: current debug APK from `app/build/outputs/apk/debug/app-debug.apk`.
- Evidence directory: `qa/emulator-android16-result-peer-icons-qa-2026-06-06`.

## Scope

Validate the Result peer-action icon polish. `На главный экран` and `Посмотреть итоги` should remain equal-width peer actions in one row, keep Russian text labels, and gain decorative `HomeIcon` / `StatsIcon` cues without crowding the layout.

## Flow

1. Installed the current debug APK on Android 16.
2. Cleared `ru.poryadok5.app`, force-stopped stale foreground apps and cleared logcat.
3. Launched `ru.poryadok5.app/.MainActivity`.
4. Captured onboarding and tapped `Начать`.
5. Captured Home and tapped `Запустить таймер`.
6. Captured Timer and tapped `Готово`.
7. Captured Result and refreshed `screenshots/play-store/04-result.png` from the real app UI.
8. Checked focus, screenshot sizes, crash buffer and app-specific fatal/ANR matches.

## Result

Status: `PASSED`.

Result kept `На главный экран` and `Посмотреть итоги` in one equal-width peer row. The refreshed Play screenshot shows the new decorative home and stats icons, while the text labels remain visible and readable. The screenshot stayed at `1080x2400`.

Crash buffer and app-specific fatal/ANR match files contained 0 lines.

## Evidence Files

- `qa/emulator-android16-result-peer-icons-qa-2026-06-06/01-onboarding.xml`
- `qa/emulator-android16-result-peer-icons-qa-2026-06-06/01-onboarding.png`
- `qa/emulator-android16-result-peer-icons-qa-2026-06-06/02-home.xml`
- `qa/emulator-android16-result-peer-icons-qa-2026-06-06/02-home.png`
- `qa/emulator-android16-result-peer-icons-qa-2026-06-06/03-timer.xml`
- `qa/emulator-android16-result-peer-icons-qa-2026-06-06/03-timer.png`
- `qa/emulator-android16-result-peer-icons-qa-2026-06-06/04-result.xml`
- `qa/emulator-android16-result-peer-icons-qa-2026-06-06/04-result.png`
- `qa/emulator-android16-result-peer-icons-qa-2026-06-06/05-crash-buffer.txt`
- `qa/emulator-android16-result-peer-icons-qa-2026-06-06/06-logcat.txt`
- `qa/emulator-android16-result-peer-icons-qa-2026-06-06/07-app-fatal-anr-matches.txt`
- `qa/emulator-android16-result-peer-icons-qa-2026-06-06/08-screenshot-sizes.txt`
- `qa/emulator-android16-result-peer-icons-qa-2026-06-06/09-ui-marker-check.txt`
- `qa/emulator-android16-result-peer-icons-qa-2026-06-06/10-focus.txt`
- `qa/emulator-android16-result-peer-icons-qa-2026-06-06/wm-size.txt`
- `qa/emulator-android16-result-peer-icons-qa-2026-06-06/wm-density.txt`
- `qa/emulator-android16-result-peer-icons-qa-2026-06-06/android-release.txt`
- `qa/emulator-android16-result-peer-icons-qa-2026-06-06/android-sdk.txt`
- `qa/emulator-android16-result-peer-icons-qa-2026-06-06/resolve-activity.txt`

## Notes

This QA proves the Result peer-action icon polish and refreshed Result Play screenshot. It does not remove external Play blockers: upload signing, public privacy URL, support email, Play Console form confirmation, internal testing confirmation and final feature graphic approval.
