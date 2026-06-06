# Android 15 Main-Flow Action Icons QA 2026-06-06

## Status

`PASSED`.

## Scope

Validated main-flow CTA icons after extending decorative Material vector icons beyond Home to onboarding, task details, timer completion, result next/repeat actions and Progress return. The flow must keep Russian text labels as the accessible action names, preserve readable button layout on a normal phone viewport and avoid app-specific crash/fatal/ANR logs.

## Environment

- AVD: `Medium_Phone_API_35_Default`
- Android release: `15`
- Android SDK: `35`
- Screen: `1080x2400`, density `420`
- Package: `ru.poryadok5.app`
- Evidence: `qa/emulator-android15-main-flow-action-icons-qa-2026-06-06`

## Flow

1. Installed the current debug APK on the Android 15 AVD, cleared `ru.poryadok5.app` data and launched `ru.poryadok5.app/.MainActivity`.
2. Captured onboarding and tapped `Начать`.
3. Captured Home with `Совпадает с выбором` plus the iconized `Запустить таймер`, `Другая задача` and `Все шаги` actions.
4. Opened task details through `Все шаги`, captured Details and started the timer through the pinned `Начать 5 мин` dock action.
5. Captured Timer with `Готово`, completed the task and captured Result with `Посмотреть следующую`, `Запустить таймер` and `Посмотреть итоги`.
6. Opened Progress through `Посмотреть итоги`, captured `Итоги` with `Продолжить с задачей` and refreshed Play screenshots `01-onboarding.png` through `05-progress.png` from the real app UI.
7. Checked current focus, screenshot dimensions and app-specific crash/fatal/ANR gates.

## Evidence Markers

- `01-onboarding.xml`: shows `Порядок 5`, `Начать` and package `ru.poryadok5.app`.
- `02-home.xml`: shows `Порядок 5`, `Совпадает с выбором`, `Запустить таймер`, `Все шаги` and package `ru.poryadok5.app`.
- `03-details.xml`: shows `Перед стартом`, `Начать 5 мин` and package `ru.poryadok5.app`.
- `04-timer.xml`: shows `Таймер`, `Готово` and package `ru.poryadok5.app`.
- `05-result.xml`: shows `Готово`, `Посмотреть следующую`, `Посмотреть итоги` and package `ru.poryadok5.app`.
- `06-progress.xml`: shows `Итоги`, `1 из 80`, `Продолжить с задачей` and package `ru.poryadok5.app`.
- `08-screenshot-sizes.txt`: all six evidence screenshots are `1080x2400`.
- `09-app-crash-package-matches.txt` and `10-app-fatal-anr-matches.txt`: zero app-specific crash/fatal/ANR lines.
- `11-ui-marker-check.txt`: marker check passed for all six main-flow screens.

## Result

Passed. Main-flow CTAs now use consistent decorative icons while retaining full Russian text labels. The refreshed Onboarding, Home, Timer, Result and Progress Play screenshots are real app captures at `1080x2400`, including `screenshots/play-store/05-progress.png`.

This QA does not remove external Play upload blockers: upload signing, hosted privacy policy URL, support email, Play Console form confirmation, internal testing confirmation and final feature graphic approval.
