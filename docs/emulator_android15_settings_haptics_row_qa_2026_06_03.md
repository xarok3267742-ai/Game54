# Android 15 Settings Haptics Row QA

## Scope

- Date: 2026-06-03.
- Device: Android 15 AVD `Medium_Phone_API_35_Default`, serial `emulator-5566`.
- Package: `ru.poryadok5.app`.
- Build: current debug APK after the settings haptics row target change.

## Flow

1. Installed the fresh debug build with `./gradlew :app:installDebug --console=plain`.
2. Cleared app data with `adb shell pm clear ru.poryadok5.app`.
3. Launched `ru.poryadok5.app/.MainActivity`.
4. Completed onboarding, opened Home, then opened Settings via the `Опции` header action.
5. Captured Settings before the interaction.
6. Tapped the text label `Тактильный отклик`, not the switch knob.
7. Captured Settings after the interaction.

## Evidence

- `qa/emulator-android15-settings-haptics-row-qa-2026-06-03/03-settings-before-ui.xml`
- `qa/emulator-android15-settings-haptics-row-qa-2026-06-03/04-settings-after-label-tap-ui.xml`
- `qa/emulator-android15-settings-haptics-row-qa-2026-06-03/03-settings-before.png`
- `qa/emulator-android15-settings-haptics-row-qa-2026-06-03/04-settings-after-label-tap.png`
- Matching UI summaries are stored next to each XML file.
- App-specific fatal/ANR match file: `app-crash-matches.txt`, 0 lines.

## Result

Passed. The haptics setting row exposed `checkable=true`, `clickable=true`, `checked=true` on bounds `[100,822][980,995]` before the tap. A tap on the text label changed the same full-row target to `checked=false`, proving the setting is no longer limited to the small switch control.
