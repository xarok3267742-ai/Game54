# Android 15 Progress Continue QA - 2026-06-04

## Scope

Проверка обновлённого экрана “Итоги” после добавления primary action “Продолжить с задачей”.

## Environment

- AVD: `Medium_Phone_API_35_Default`
- Serial: `emulator-5566`
- Android: API 35 / Android 15
- APK: `app/build/outputs/apk/debug/app-debug.apk`
- Package: `ru.poryadok5.app`
- Viewport: `1080x2400`, density `420`
- Evidence: `qa/emulator-android15-progress-continue-qa-2026-06-04`

## Steps

1. Installed the fresh debug APK.
2. Cleared app data and logcat.
3. Completed onboarding.
4. Started the suggested Home task.
5. Completed the timer with “Готово”.
6. Opened “Посмотреть итоги” from Result after scrolling the Result actions into view.
7. Verified Progress shows “Итоги”, `выполнено`, `серия`, `каталог`, `Отмечено задач: 1 из 80.` and “Продолжить с задачей”.
8. Captured the refreshed Play screenshot `screenshots/play-store/05-progress.png` from the real app UI.
9. Tapped “Продолжить с задачей”.
10. Verified Home reopened with `Порядок 5`, `Запустить таймер`, `1 дн.` and `1%`, without recording a second completion.
11. Captured focus and log evidence.

## Result

`PASSED`.

- “Продолжить с задачей” is visible above the Android navigation bar on the Progress screen.
- Tapping it returns to the Home task flow.
- Progress remains at one completed task after returning to Home.
- `07-focus.txt` shows focus stayed on `ru.poryadok5.app/.MainActivity`.
- `08-crash-buffer.txt` was empty.
- `09-app-fatal-anr-matches.txt` was empty.

