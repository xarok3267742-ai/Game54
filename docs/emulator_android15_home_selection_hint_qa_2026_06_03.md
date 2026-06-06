# Android 15 Home Selection Hint QA 2026-06-03

## Scope

Проверка главного экрана после добавления подсказки качества подбора задачи.

## Environment

- Device: Android 15 AVD `Medium_Phone_API_35_Default`.
- Serial: `emulator-5566`.
- Resolution: 1080x2400 px.
- Package: `ru.poryadok5.app`.
- Build: debug APK from current workspace.
- Evidence: `qa/emulator-android15-home-selection-hint-qa-2026-06-03`.

## Flow

1. Started a separate headless AVD on port `5566`.
2. Installed the current debug build with `ANDROID_SERIAL=emulator-5566 ./gradlew :app:installDebug --console=plain`.
3. Cleared app data with `adb shell pm clear ru.poryadok5.app`.
4. Completed onboarding from the default Home area.
5. Verified Home UI tree includes `Подбор: точно по фильтру`, quick launch actions and metrics.
6. Refreshed `screenshots/play-store/02-home.png` from real app UI.

## Result

- Home screen showed the selection-quality hint below the task metadata.
- The hint fit inside the task card without overlapping the status chip, primary action or progress metrics.
- Refreshed screenshot dimensions: 1080x2400 px.
- Crash-buffer match file contained 0 lines for app-specific fatal/crash markers.

Status: passed.
