# Android 15 Home Stats Icon QA - 2026-06-06

## Scope

Проверка главного экрана после замены header action `Итоги` с completion-check на отдельный `StatsIcon` bar-chart vector.

## Environment

- Device: Android 15 AVD `Medium_Phone_API_35_Default`.
- Serial: `emulator-5554`.
- Resolution: 1080x2400 px.
- Density: 420 dpi.
- Package: `ru.poryadok5.app`.
- Build: debug APK from current workspace.
- Evidence: `qa/emulator-android15-home-stats-icon-qa-2026-06-06`.

## Flow

1. Installed the current debug build with `./gradlew :app:installDebug --console=plain --no-daemon --max-workers=1`.
2. Cleared app data with `adb shell pm clear ru.poryadok5.app`.
3. Launched `ru.poryadok5.app/.MainActivity`.
4. Completed onboarding from the default `Дом` area.
5. Captured Home UI XML, summary and screenshot.
6. Refreshed `screenshots/play-store/02-home.png` from the real Home frame.
7. Captured focus and app-specific crash-buffer evidence.

## Result

- Home header shows the `StatsIcon` visual for `Итоги` and the Material settings icon for `Опции`.
- UI tree preserves accessible labels: `Button desc="Итоги"` and `Button desc="Опции"`.
- Main Home flow remains visible: suggested task, `Подбор: точно по фильтру`, `Запустить таймер`, `Другая задача`, `Посмотреть шаги`, progress metrics and collapsed `Настроить подбор`.
- Refreshed screenshot dimensions: 1080x2400 px.
- Focus stayed on `ru.poryadok5.app/.MainActivity`.
- `crash-logcat-package-matches.txt` contained 0 lines for app-specific crash markers.

Status: passed. This QA is covered by `scripts/check_qa_evidence.py` and keeps the Home Play screenshot synchronized with the current UI.
