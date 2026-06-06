# Android 15 Home Action Icons QA 2026-06-06

## Status

`PASSED`.

## Scope

Validated Home action icons after adding decorative Material vector icons to `Запустить таймер`, `Другая задача` and compact `Все шаги`. The refreshed evidence also verifies the user-facing selection hint `Совпадает с выбором`. The buttons must keep their Russian text labels, stay readable on a normal phone viewport and avoid app-specific crashes or fatal/ANR logs.

## Environment

- AVD: `Medium_Phone_API_35_Default`
- Android release: `15`
- Android SDK: `35`
- Screen: `1080x2400`, density `420`
- Package: `ru.poryadok5.app`
- Evidence: `qa/emulator-android15-home-action-icons-qa-2026-06-06`

## Flow

1. Installed the current debug APK and cleared `ru.poryadok5.app` data.
2. Launched `ru.poryadok5.app/.MainActivity`.
3. Captured onboarding, used the UI tree to locate the `Начать` target, and completed onboarding.
4. Captured Home after adding action icons and refreshed `screenshots/play-store/02-home.png` from the real app UI.
5. Confirmed Home showed `Совпадает с выбором`, `Запустить таймер`, `Другая задача`, `Все шаги` and `Настроить подбор`.
6. Checked current focus, screenshot dimensions, crash buffer and app-specific fatal/ANR matches.

## Evidence Markers

- `02-home-action-icons.xml`: shows `Совпадает с выбором`, `Запустить таймер`, `Другая задача`, `Все шаги`, `Настроить подбор` and package `ru.poryadok5.app`.
- `04-screenshot-sizes.txt`: onboarding, Home evidence and refreshed Play Home screenshot are `1080x2400`.
- `03-focus-home.txt`: current focus remains on `ru.poryadok5.app/.MainActivity`.
- `05-crash-buffer.txt` and `06-app-fatal-anr-matches.txt`: zero crash/fatal/ANR lines.
- `07-ui-marker-check.txt`: marker check passed for visible Home action labels and Home selection copy.

## Result

Passed. Home actions now scan faster with icons while preserving text labels and tap targets. `Все шаги` keeps the secondary row on one line on the normal phone viewport, and `Совпадает с выбором` removes the previous technical filter wording from the task card.

This QA does not remove external Play upload blockers: upload signing, hosted privacy policy URL, support email, Play Console form confirmation, internal testing confirmation and final feature graphic approval.
