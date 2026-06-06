# Screenshot Manifest

## Capture Summary

- Source app: `ru.poryadok5.app`.
- Device: Android 15/16 AVD. Latest Result screenshot refresh used Android 16/API 36 on `Medium_Phone_API_36`.
- Output directory: `screenshots/play-store`.
- Resolution: 1080x2400 px, phone portrait.
- Status: RC screenshots captured from the real app UI.

Before public production rollout, recapture from the signed release build if the visual design changes.

## Files

| File | Screen | Purpose | Resolution | Status |
|---|---|---|---:|---|
| `screenshots/play-store/01-onboarding.png` | Onboarding | First-run value, starting-area choice, unframed `Первые 5 минут` summary and start action | 1080x2400 | RC_READY |
| `screenshots/play-store/02-home.png` | Home | Compact icon header actions, quick task, non-interactive status pill, selection-quality hint, compact result preview, action icons, launch action, task-skip action, aligned progress metrics and unframed whole-row collapsed filter summary with chevron indicator | 1080x2400 | RC_READY |
| `screenshots/play-store/03-timer.png` | Timer | Session goal `Цель: 5 мин`, countdown, steps, compact `После` outcome preview, icon-supported task controls, `ProgressLine` timer track and pinned `Готово` bottom action dock | 1080x2400 | RC_READY |
| `screenshots/play-store/04-result.png` | Result | Completed-task identity `Сделано: …`, task-specific result text, aligned progress metrics, next-task preview with compact `После` outcome, non-interactive status pill, details-first `Посмотреть следующую`, timer shortcut and icon-supported home/progress peer action row | 1080x2400 | RC_READY |
| `screenshots/play-store/05-progress.png` | Progress | Catalog percent, completed-count copy, `ProgressLine` per-area bars, unframed `Серия` / `Счётчик` rhythm summary and continue action | 1080x2400 | RC_READY |
| `screenshots/play-store/06-settings.png` | Settings | Unframed offline/privacy facts, compact `Версия` / `Каталог` / `Данные` about summary and clean lower edge without reset-card sliver | 1080x2400 | RC_READY |

## QA Notes

- Screenshots were captured after removing unrelated old emulator test packages that were stealing focus.
- Onboarding screenshot was refreshed after replacing the framed `Как это работает` card with the unframed `Первые 5 минут` summary.
- Settings screenshot was refreshed after adding the “О приложении” version/about block.
- Settings screenshot was refreshed after adding `PrivacyBadgeGrid` facts for `Без интернета`, `Без аккаунта`, `Без рекламы` and `Без аналитики`.
- Settings screenshot was refreshed after removing nested badge cards from `PrivacyBadgeGrid`; the four privacy notes now render as unframed facts inside one sage section.
- Settings screenshot was refreshed after adding short privacy fact explanations: `работает офлайн`, `вход не нужен`, `нет баннеров`, `нет трекеров`.
- Settings screenshot was refreshed after replacing the paragraph-heavy `О приложении` block with compact `Версия` / `Каталог` / `Данные` facts.
- Settings screenshot was refreshed after widening the `Данные` fact and adding reset-section spacing so `на устройстве` stays on one line and the first viewport ends cleanly.
- Home and Result screenshots were refreshed after the quick-task-first Home and Result next-task preview changes.
- Home screenshot was refreshed after aligning the Home metric label to `выполнено`.
- Home screenshot was refreshed after replacing the technical selection-quality hint with user-facing copy such as `Совпадает с выбором`.
- Home screenshot was refreshed after replacing text header actions with compact icon actions and Russian accessibility labels.
- Home screenshot was refreshed after replacing the `Итоги` completion-check icon with the dedicated `StatsIcon` bar-chart vector.
- Home screenshot was refreshed after adding the `Другая задача` task-skip action.
- Home screenshot was refreshed after the collapsed `Настроить подбор` filter disclosure polish and shows the summary before filter controls are expanded.
- Home screenshot was refreshed after making the collapsed `Настроить подбор` summary a whole-row 56dp toggle.
- Home screenshot was refreshed after adding the `Изменить`/`Скрыть` chevron indicator to the whole-row filter summary.
- Home screenshot was refreshed after replacing the collapsed `Настроить подбор` raised card with an unframed divider-row summary.
- Home screenshot was refreshed after replacing the old inline `После: ...` result sentence with a compact result preview using a separate `После` label.
- Home screenshot was refreshed after adding decorative vector icons to the primary and secondary Home task actions.
- Home screenshot was refreshed after compacting the secondary steps action from `Посмотреть шаги` to `Все шаги`.
- Onboarding, Home, Timer, Result and Progress screenshots were refreshed after extending decorative CTA icons across the main flow.
- Onboarding, Home, Timer and Result screenshots were refreshed after the primary CTA contrast fix; labels now render in `onPrimary` on sage buttons.
- Progress screenshot was refreshed after adding the catalog-percent metric and neutral completed-count copy.
- Progress screenshot was refreshed after adding “Продолжить с задачей” and was captured from Android 15 `emulator-5566`.
- Timer and Progress screenshots were refreshed after the shared `ProgressLine` change to remove false end-dot markers from zero-progress rows.
- Progress screenshot was refreshed after replacing the paragraph-style `Ритм` note with compact `Серия` / `Счётчик` rhythm facts.
- Progress screenshot was refreshed after removing nested fact cards from `Ритм`; `Серия` / `Счётчик` now render as unframed facts inside one blue section.
- Timer screenshot was refreshed after pinning `Готово` in the bottom action dock.
- Timer screenshot was refreshed after adding the Timer session goal `Цель: 5 мин` above the progress line and countdown.
- Timer screenshot was refreshed after adding the compact Timer outcome preview `После` under the active step list.
- Timer screenshot was refreshed after adding decorative icons to `Пауза`/`Продолжить` and `Сброс` controls on Android 16.
- Result screenshot was refreshed after aligning the result metric label to `выполнено`.
- Result screenshot was refreshed after adding `Посмотреть шаги` for the next-task preview.
- Result screenshot was refreshed after changing the next-task primary action to details-first `Посмотреть следующую`.
- Result screenshot was refreshed after compacting `На главный экран` and `Посмотреть итоги` into one visible peer row.
- Result screenshot was refreshed again from Android 15 evidence after verifying `Посмотреть следующую` opens Details and `Запустить таймер` remains a shortcut.
- Result screenshot was refreshed from Android 16 after removing the generic amber `Что изменилось` card; the task-specific result text now leads directly into metrics, next-task preview and actions.
- Result screenshot was refreshed after adding `Сделано: …` with the completed task title under `Готово`.
- Result screenshot was refreshed after adding compact `После` outcome preview to the next-task card.
- Result screenshot was refreshed after adding decorative `HomeIcon` / `StatsIcon` cues to `На главный экран` and `Посмотреть итоги`.
- Home and Result screenshots were refreshed after replacing the button-like task status chip with non-interactive `TaskStatusPill`.
- No other app, debug overlay, notification shade, permission prompt or keyboard appears in the frames.
- `sips` reported all six PNG files as 1080x2400.
- `scripts/check_store_asset_pixels.py` validates dimensions, PNG structure, opacity, nonblank sampled pixels and uniqueness for the screenshot set.
