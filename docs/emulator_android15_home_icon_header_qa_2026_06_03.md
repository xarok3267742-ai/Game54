# Android 15 Home Icon Header QA 2026-06-03

## Scope

Проверка главного экрана после замены текстовых header actions на компактные icon actions с русскими accessibility labels.

## Environment

- Device: Android 15 AVD `Medium_Phone_API_35_Default`.
- Serial: `emulator-5566`.
- Resolution: 1080x2400 px.
- Package: `ru.poryadok5.app`.
- Build: debug APK from current workspace.
- Evidence: `qa/emulator-android15-home-icon-header-qa-2026-06-03`.

## Flow

1. Started a separate headless AVD on port `5566`.
2. Installed the current debug build with `ANDROID_SERIAL=emulator-5566 ./gradlew :app:installDebug --console=plain`.
3. Cleared app data with `adb shell pm clear ru.poryadok5.app`.
4. Completed onboarding from the default Home area.
5. Dumped Home UI tree and verified header actions appear as clickable/focusable buttons with `Итоги` and `Опции` content descriptions.
6. Refreshed `screenshots/play-store/02-home.png` from real app UI.

## Result

- Home header uses compact icon buttons while preserving 48dp+ tap targets.
- UI tree summary shows `Button desc="Итоги"` and `Button desc="Опции"`.
- Main Home flow remains visible: selection-quality hint, launch action, details action, metrics and filter card.
- Refreshed screenshot dimensions: 1080x2400 px.
- Crash-buffer match file contained 0 lines for app-specific fatal/crash markers.

Status: passed.
