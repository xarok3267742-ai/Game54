# Android 15 Result Metric Label QA 2026-06-03

## Scope

Проверка экрана результата после выравнивания первой метрики с Progress: `выполнено` вместо старой формулировки.

## Environment

- Device: Android 15 AVD `Medium_Phone_API_35_Default`.
- Serial: `emulator-5554`.
- Resolution: 1080x2400 px.
- Package: `ru.poryadok5.app`.
- Build: debug APK from current workspace.
- Evidence: `qa/emulator-android15-result-metric-label-qa-2026-06-03`.

## Flow

1. Started headless AVD with fixed port `5554`.
2. Installed `app/build/outputs/apk/debug/app-debug.apk`.
3. Cleared app data with `adb shell pm clear ru.poryadok5.app`.
4. Completed onboarding.
5. Started the suggested task timer.
6. Completed one task.
7. Verified Result screen metrics and next-task preview.
8. Captured refreshed Play screenshot `screenshots/play-store/04-result.png`.

## Result

- Result screen showed `1 выполнено`, `1 дн.` and `1% каталог`.
- Next-task preview showed `Дальше без повтора` and a fresh next task.
- Primary actions remained visible and tappable.
- Refreshed screenshot dimensions: 1080x2400 px.
- App-filtered crash and fatal/ANR log match files contained 0 lines.

Status: passed.
