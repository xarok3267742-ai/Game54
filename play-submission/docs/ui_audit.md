# UI Audit

## Design System

- Colors: cream background `#FBFAF7`, charcoal text `#232824`, sage primary `#496B5A`, muted blue secondary `#4D6575`, amber accent `#E6B84E`.
- Typography: display 34sp, headline 26sp, title 21/17sp, body 16/14sp.
- Spacing: 8dp chip gaps, 10dp metric gaps, 16dp screen gaps, 18-20dp content padding.
- Radii: 6-8dp, no large rounded card-heavy look.
- Elevation: low 1dp cards only.
- Button states: Material enabled/disabled states, minimum height 52dp; primary action text uses `onPrimary` for readable contrast on sage buttons; destructive confirmation uses `DangerAction` with Material `error` color.
- Input states: chip selected/unselected visually and semantically, full-row haptics switch checked/unchecked.
- Icon states: `HeaderAction` and the top `Назад` control render vector icons instead of text glyphs, while semantics keep the Russian action labels. Home uses a dedicated `StatsIcon` for “Итоги” so progress navigation does not look like a task-completion checkmark.
- Progress states: shared `ProgressLine` uses a clipped custom track without the Material end-dot, so нулевой progress does not look partially complete.
- Loading states: full-screen centered spinner for tasks/progress loading, so startup waits feel intentional instead of top-heavy.
- Empty/error states: Startup error retry uses generic Russian copy and `Повторить загрузку`; catalog is bundled so empty state should not occur.
- Animation: chip color animation, content size animation, timer progress.

## Проверенные сценарии для реализации

- Первый запуск и onboarding. Onboarding copy обещает только стартовую зону; энергию и время пользователь уточняет на главном экране в блоке подбора. Onboarding flow summary `Первые 5 минут` заменяет прежнюю framed explanation card на три unframed факта `Сначала` / `Затем` / `После`.
- Главный экран с compact vector `HeaderAction` controls, отдельным `StatsIcon` для “Итоги”, quick-task-first, подсказкой качества подбора, Home task result preview с отдельной меткой `После`, Home action icons (`PlayArrow`, `Refresh`, auto-mirrored `List`) on the main action row, действием “Другая задача” рядом с просмотром шагов, Home skip exhausted hint `Других задач по этому подбору сейчас нет`, неинтерактивным `TaskStatusPill`, согласованными метриками “выполнено/серия/каталог” и Home filter disclosure: компактный summary текущего подбора виден всегда, а выбор фильтров раскрывается только через whole-row 56dp toggle с шеврон-индикатором.
- Детали задачи: summary карточка не повторяет первый шаг и показывает статус `выбрана`, Task details briefing `Перед стартом` показывает unframed зона/энергия/время facts, compact `После` outcome preview и коротко задаёт критерий “достаточно заметного улучшения”; полный план остаётся в отдельном блоке, а Task details start dock держит `Начать` доступным на compact screens.
- Таймер, пауза, сброс, завершение; Timer session goal показывает `Цель: 5 мин` над прогрессом и обратным отсчётом, Timer controls use decorative `PauseIcon`, `PlayArrow` and `Refresh` icons with Russian text labels, Timer outcome preview показывает compact `После` под шагами, а Timer completion dock держит `Готово` закреплённым внизу, пока план прокручивается на компактных экранах.
- Timer expired state: pause/resume control changes to disabled `Время вышло`, while `Сброс` and `Готово` remain clear next actions.
- Экран результата с `Сделано: …` для названия выполненной задачи, task-specific result text без generic amber поясняющей карточки, согласованными метриками “выполнено/серия/каталог”, preview следующей задачи с first step и compact `После` outcome preview, details-first primary action `Посмотреть следующую`, shortcut `Запустить таймер`, icon-supported peer actions `На главный экран` / `Посмотреть итоги` в одну строку и отдельным состоянием закрытого каталога.
- Итоги и настройки.
- Progress screen shows a numeric catalog percent, neutral completed-catalog copy, compact Progress focus summary `Следующая зона` / `Каталог закрыт`, per-area completion bars, a compact unframed Progress rhythm summary with `Серия` / `Счётчик`, and the primary action “Продолжить с задачей”, so users can see where порядок уже продвинулся, which unfinished zone is next, and return to the task flow without relying on Back.
- Timer/catalog/zone progress bars use `ProgressLine` to avoid a false end-dot marker on zero-progress rows.
- Сброс прогресса с подтверждением, явной отменой, `DangerAction` для финального destructive action и inline feedback после выполнения.
- Settings includes a scannable unframed `PrivacyBadgeGrid` with `Без интернета` / `работает офлайн`, `Без аккаунта` / `вход не нужен`, `Без рекламы` / `нет баннеров`, `Без аналитики` / `нет трекеров` plus a compact Settings about summary with `Версия`, `Каталог` and `Данные`.
- Activity recreation keeps the current internal screen route instead of resetting details/timer/result/progress/settings to Home.
- Compact viewport 720x1280: ключевые действия ниже fold доступны через вертикальный scroll.
- Large viewport 2000x2560: контент и top bars центрируются с max-width constraints.
- Large font `font_scale=1.3`: ключевые действия доступны на normal phone viewport.
- Startup error retry: каталог-load failure shows a calm generic Russian explanation and a 52dp `Повторить загрузку` action instead of a dead-end technical message.

## Accessibility Notes From UI Review

- Tap targets: buttons 52dp, chips 48dp minimum, top/back/header actions 48dp.
- Important actions do not rely only on color.
- Filter chips expose semantic selected state and Russian `Выбрано` / `Не выбрано` descriptions.
- Task status uses `TaskStatusPill` with a small dot indicator instead of a bordered filled chip, so `новая`, `повтор` and `выполнено` do not look like tappable buttons.
- Back action uses a Material icon vector, button semantics and Russian content description `Назад`.
- Header icon actions use vector icons, including `StatsIcon` for `Итоги`, and keep Russian content descriptions for `Итоги` and `Опции`.
- Home selection copy uses `Совпадает с выбором`, `Зона и время совпали` and `Ближайшая свободная задача`, keeping the quality hint short and без слова `фильтр`.
- Home secondary actions keep equal width so “Другая задача” and compact “Все шаги” scan as peer choices without wrapping or shifting the primary timer action.
- Home action icons are decorative Material vector icons: `PlayArrow` for timer start, `Refresh` for another task and auto-mirrored `List` for viewing steps. Text labels remain the accessible action names.
- Main-flow CTA icons use `Done`, `ArrowForward`, `PauseIcon`, `PlayArrow`, `Refresh` and auto-mirrored `List` as decorative cues while Russian text remains the accessible action name.
- Main-flow CTA icons extend the same pattern beyond Home: `PlayArrow` for start actions, `Done` for timer completion, auto-mirrored `List` for details-first next task and `ArrowForward` for continuing from Progress.
- Home skip exhausted hint explains `Других задач по этому подбору сейчас нет` only when the skip action is disabled, reducing ambiguity without adding noise to the normal first-run Home.
- Home task result preview keeps `После` as a compact result preview below the first step instead of the old inline `После: ...` sentence, so expected outcome scans as its own state without adding another framed card.
- Home filter disclosure keeps a компактный summary with a whole-row 56dp toggle target, `Подбор раскрыт` / `Подбор скрыт` semantics and a text + шеврон indicator. The collapsed state is unframed with divider rhythm instead of a raised card, while expanded controls stay in a clear tool card so the first screen does not become a full settings form.
- Onboarding flow summary keeps the first-run explanation unframed with 48dp+ facts, so `Начать` stays visible on a normal phone viewport without the old `Как это работает` card.
- Task details briefing keeps unframed 56dp meta facts for зона/энергия/время and a compact `После` outcome preview before the full step list, so the expected result is visible before the user starts.
- Task details status uses `выбрана`, not the generic `новая`, because the user is already inspecting the selected task.
- Task details start dock keeps the primary `Начать` action pinned while the briefing and steps scroll underneath with bottom clearance.
- Timer session goal keeps `Цель: 5 мин` near task metadata, so the original session target remains scannable after the countdown starts.
- Timer outcome preview reuses the compact non-interactive `После` pattern under the active step list, so the finish criterion stays visible during the session without adding another card.
- Timer completion dock keeps the primary `Готово` action reachable on компактных экранах without hiding pause/reset controls inside the timer content.
- Progress focus summary uses a non-interactive 56dp row after the catalog progress line. It highlights the engine-selected least-completed unfinished zone as `Следующая зона`, then switches to `Каталог закрыт` when all catalog tasks are done.
- Progress rhythm summary uses two non-interactive unframed 56dp facts, `Серия` and `Счётчик`, instead of paragraph-heavy help copy or nested cards.
- Startup error retry keeps the `Повторить загрузку` action as a full-width primary button and avoids exposing exception text.
- Result content keeps the task-specific result text and moves directly from metrics to next-task preview with compact `После`, without the old generic amber completion card.
- Result completion identity shows `Сделано: …` between `Готово` and the outcome text, so the user can confirm which task was just marked complete before choosing the next action.
- Result secondary navigation keeps `На главный экран` and `Посмотреть итоги` as equal-width peer actions in one row with decorative `HomeIcon` and `StatsIcon`, reducing below-fold action stacking while preserving 52dp targets.
- Settings haptics row owns the switch semantics and keeps a 56dp full-row toggle target.
- Settings privacy summary uses non-interactive unframed 56dp+ facts with small sage markers and short explanations (`работает офлайн`, `вход не нужен`, `нет баннеров`, `нет трекеров`), so the no-data model is readable without opening policy text or adding cards inside the privacy card.
- Settings about summary uses compact non-interactive 56dp+ facts for `Версия`, `Каталог` and `Данные`; the `Данные` column is wider so `на устройстве` stays on one line, and the reset section is spaced away from the first viewport edge.
- Settings destructive reset keeps the explicit `Сбросить прогресс` label and 52dp `DangerAction`; the risk is communicated by text and control styling, not color alone.
- ProgressLine exposes progress semantics while avoiding decorative end-dot markers that can misread as nonzero progress.
- Text uses readable sizes and clear contrast.
- Primary CTA contrast is explicitly guarded so sage buttons do not inherit dark body text.
- Timer controls avoid false affordances after expiry by disabling the impossible continue action.
- Copy is Russian and action-oriented.
- Scrollable screens preserve access to primary actions on compact phones.
- Large screens avoid over-wide reading lines and edge-to-edge cards.
- Dynamic text scaling at `font_scale=1.3` keeps the primary flow usable.

## Remaining Visual Work

Реальные RC screenshots captured in `screenshots/play-store`. Feature graphic candidate saved at `store-assets/feature-graphic/feature-graphic-candidate-03.png`; перед production upload нужен финальный preview approval. Кодовые баннеры не используются.
