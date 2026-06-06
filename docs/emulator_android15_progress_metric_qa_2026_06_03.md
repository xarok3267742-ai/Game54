# Android 15 Progress Metric QA 2026-06-03

## Scope

Проверка обновлённого экрана “Итоги” после добавления числовой метрики каталога и нейтральной строки completed-count.

## Environment

- Device: Android 15 AVD `emulator-5554`.
- Resolution: 1080x2400 px.
- Package: `ru.poryadok5.app`.
- Build: debug APK from current workspace.
- Evidence: `qa/emulator-android15-progress-metric-qa-2026-06-03`.

## Flow

1. Installed `app/build/outputs/apk/debug/app-debug.apk`.
2. Cleared app data with `adb shell pm clear ru.poryadok5.app`.
3. Completed onboarding.
4. Started the suggested task timer.
5. Completed one task.
6. Opened “Посмотреть итоги”.
7. Captured the refreshed Play screenshot `screenshots/play-store/05-progress.png`.

## Result

- Progress metrics showed `1`, `1 дн.` and `1% каталог`.
- Catalog card showed `Отмечено задач: 1 из 80.`
- Per-area rows showed `Дом 1 из 16` and other areas `0 из 16`.
- Text was visible without truncation on 1080x2400.
- Screenshot dimensions: 1080x2400 px.

Status: passed.
