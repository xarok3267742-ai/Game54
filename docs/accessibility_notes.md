# Accessibility Notes

## Text And Contrast

- Основной текст charcoal на cream/white background.
- Secondary text muted but readable.
- Primary action text uses `onPrimary` on sage buttons; white on `#496B5A` is about 5.94:1 contrast.
- UI does not rely only on color; selected filter chips use borders/background changes, semantic selected state and Russian state descriptions.

## Touch Targets

- Primary/secondary actions: minimum 52dp height.
- DangerAction for `Сбросить прогресс`: minimum 52dp height and explicit destructive label.
- Chips: minimum 48dp height, with selected/unselected state exposed to accessibility services.
- Top actions, including compact header icon actions: minimum 48dp.
- Onboarding `Первые 5 минут` facts: minimum 48dp rows, non-interactive text markers and no framed nested controls.
- Settings switches use a full-row toggle target of at least 56dp, with one switch semantic action for the row.
- Settings about summary uses non-interactive 56dp+ facts for `Версия`, `Каталог` and `Данные`, with extra width for `на устройстве`, so app metadata is readable without adding another interactive control.
- Progress focus summary is a non-interactive 56dp+ row: `Следующая зона` and `Каталог закрыт` remain plain text, not a hidden button.

## Labels And Semantics

Compose text buttons and switches expose readable labels. The settings haptics switch is controlled by its full row, so TalkBack users get one clear toggle target instead of a small duplicated control. The top back action uses Material icon vectors and exposes the Russian content description “Назад”. Compact header icon actions use vector icons and expose Russian content descriptions such as “Итоги” and “Опции”; “Итоги” uses `StatsIcon` instead of a completion checkmark. The app does not use unlabeled image-only controls.

Loading state uses a centered full-screen spinner and a Russian message so startup/progress waiting states remain readable without adding a misleading action.

Home filter summary uses an unframed whole-row 56dp button target with `Подбор раскрыт` / `Подбор скрыт` state descriptions and a visible `Изменить`/`Скрыть` + chevron indicator, so users do not need to hit only the small text.

Home selection copy avoids technical filter language. The visible hint stays short (`Совпадает с выбором`, `Зона и время совпали`, `Ближайшая свободная задача`) so it remains readable before the primary action row.

Home action icons are decorative and keep text labels as the accessible names. `Запустить таймер`, `Другая задача` and compact `Все шаги` therefore remain readable and screen-reader friendly while scanning faster visually.

Main-flow CTA icons are decorative as well. Start, finish, next-task, continue and timer controls keep text labels as the accessible names, so the icon never becomes the only cue.

Result peer-action icons are decorative: `На главный экран` and `Посмотреть итоги` keep their Russian text labels while using `HomeIcon` and `StatsIcon` for faster visual scanning.

ProgressLine exposes `ProgressBarRangeInfo`, so timer, catalog and per-area progress remain available to accessibility services after replacing the default Material progress bar visuals.

Progress focus summary uses text, not color alone, to explain the next unfinished zone after the catalog progress line. The small marker is decorative and the visible Russian copy carries the meaning.

Task details start dock keeps `Начать` as a full-width primary action reachable on compact screens after the user has reviewed the briefing, expected `После` result and steps.

## Dynamic Text

UI uses standard Compose text scaling. Android 16 large-font QA passed at `font_scale=1.3`; evidence is documented in `docs/emulator_android16_large_font_qa.md`.

## Permissions

No runtime permission flows, so no denied-permission accessibility branch is needed.
