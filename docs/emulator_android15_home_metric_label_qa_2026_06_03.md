# Android 15 Home Metric Label QA 2026-06-03

## Scope

Проверка главного экрана после выравнивания первой метрики с Result/Progress: `выполнено` вместо старой формулировки.

## Environment

- Device: Android 15 AVD `Medium_Phone_API_35_Default`.
- Serial: `emulator-5554`.
- Resolution: 1080x2400 px.
- Package: `ru.poryadok5.app`.
- Build: debug APK from current workspace.
- Evidence: `qa/emulator-android15-home-metric-label-qa-2026-06-03`.

## Flow

1. Started headless AVD with fixed port `5554`.
2. Installed `app/build/outputs/apk/debug/app-debug.apk`.
3. Cleared app data with `adb shell pm clear ru.poryadok5.app`.
4. Completed onboarding.
5. Verified Home screen metrics and quick-task-first layout.
6. Captured refreshed Play screenshot `screenshots/play-store/02-home.png`.

## Result

- Home screen showed `0 выполнено`, `0 дн.` and `0% каталог`.
- Suggested task, primary launch action and filter controls remained visible in the expected order.
- Refreshed screenshot dimensions: 1080x2400 px.
- App-filtered crash and fatal/ANR log match files contained 0 lines.

Status: passed.
