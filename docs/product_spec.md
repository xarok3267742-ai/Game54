# Product Spec

## Название

`Порядок 5`

## Тип

Приложение, productivity/lifestyle.

## Pitch

Короткие задачи на 3, 5 и 10 минут, чтобы вернуть порядок без большой уборки.

## Elevator Pitch

`Порядок 5` помогает выбрать одну маленькую задачу по дому, рабочему месту, кухне, личным вещам или цифровому порядку. Пользователь задаёт зону, энергию и время, запускает таймер и получает понятный результат без регистрации и интернета.

## Целевая аудитория

Русскоязычные Android-пользователи casual-сегмента, которым нужны быстрые бытовые улучшения в коротких сессиях.

## Потребность

Пользователь хочет навести порядок, но задача кажется большой и неопределённой. Приложение даёт маленький следующий шаг.

## Core Loop

Выбрать зону → выбрать энергию → выбрать время → получить задачу → при необходимости запросить другую задачу → выполнить по шагам → отметить результат → увидеть прогресс → при желании перейти к следующей задаче без немедленного повтора.

## Экраны

- Onboarding: выбор зоны по умолчанию и краткий unframed `Первые 5 минут` flow summary.
- Home: задача на сейчас, короткая подсказка качества подбора, compact result preview `После`, быстрый запуск, decorative action icons for “Запустить таймер” / “Другая задача” / “Все шаги”, действие “Другая задача” без записи прогресса, объяснение `Других задач по этому подбору сейчас нет` при исчерпании альтернатив, метрики “выполнено/серия/каталог” и компактный текущий подбор ниже основного действия; пользователь раскрывает зону/энергию/время whole-row нажатием на summary с текстом `Изменить`/`Скрыть` и шевроном только при желании изменить фильтр.
- Task details: краткое summary задачи, предстартовый briefing с unframed зона/энергия/время facts и compact `После` outcome preview, полный список шагов без дублирования первого шага и Task details start dock с закреплённым `Начать` для compact screens.
- Timer: обратный отсчёт по wall-clock времени, Timer session goal `Цель: 5 мин`, pause/resume/reset, список шагов, compact Timer outcome preview `После` и закреплённый bottom action dock с `Готово`.
- Result: подтверждение `Сделано: …` с названием выполненной задачи, task-specific result text, метрики “выполнено/серия/каталог”, preview следующей задачи без немедленного повтора с первым шагом и compact `После` outcome preview, быстрый просмотр её шагов перед запуском; если каталог уже закрыт, экран честно предлагает повтор вместо новой задачи.
- Progress: общий счётчик, серия, числовой процент каталога, нейтральный счётчик “отмечено задач”, next focus area `Следующая зона` / `Каталог закрыт`, прогресс по каждой зоне, компактное unframed пояснение ритма `Серия` / `Счётчик` и основное действие “Продолжить с задачей” для возврата в рабочий поток.
- Settings: preferred area, haptics, privacy, compact about summary with `Версия` / `Каталог` / `Данные`, reset progress with inline confirmation.
- Startup error: if the bundled catalog cannot be loaded, the app shows a generic Russian message and `Повторить загрузку` instead of exposing technical details.
- System Back: с внутренних экранов возвращает пользователя в ожидаемый предыдущий контекст, а не закрывает приложение.
- Activity recreation: текущий внутренний экран сохраняется через saveable state, чтобы details/timer/result/progress/settings не сбрасывались на Home при пересоздании Activity. Task-bound routes восстанавливаются только для route-safe catalog-shaped ids; повреждённый route возвращает пользователя на Home.
- Large screens: основной контент остаётся в центрированной колонке, чтобы карточки и строки текста не растягивались чрезмерно.

## Non-goals

Нет социальных функций, аккаунтов, backend, напоминаний, рекламы, аналитики, платежей и пользовательского контента.

## UI Style

Спокойный mobile utility: светлая база, sage primary, muted blue secondary, amber accent, строгие карточки с radius 8dp, readable typography, мягкие состояния.

## Tone of Voice

Русский, спокойный, конкретный, без давления и “мотивационных” клише.

## Контентная структура

80 задач: 16 задач на каждую из 5 зон. Каждая задача содержит id, area, energy, minutes, title, 3 шага и resultText.

Runtime UI reads the loaded catalog size from the engine for progress/about copy instead of duplicating a hardcoded count.
Runtime catalog parsing rejects blank ids, route-unsafe ids, duplicate ids, id/area mismatches, unknown area/energy values, unsupported durations and malformed text/steps instead of silently assigning defaults. Task id validation is shared with task-bound screen route restore, and duration validation uses the same supported 3/5/10-minute domain set as the UI and suggestion engine.
Runtime duration filters are normalized to the supported 3/5/10-minute set before task suggestion, so corrupted restored UI state falls back to a valid 5-minute selection.
Home shows whether the suggested task matches the current choice, shares the same area/time, or uses the nearest free catalog task. The visible hint uses user-facing copy: `Совпадает с выбором`, `Зона и время совпали` or `Ближайшая свободная задача`, so fallback selection is transparent without exposing technical filter language.
Home lets the user skip the current suggestion without marking progress. The engine excludes skipped ids while an alternative exists, then falls back to the normal completed-task rules when the matching pool is exhausted.
Home explains the exhausted skip state with `Других задач по этому подбору сейчас нет`, so a disabled “Другая задача” action is not a silent dead end.
Home keeps filter tuning behind an explicit disclosure: the user always sees a compact current selection summary as лёгкой строкой, then reveals area, energy and duration controls only when they want to adjust the suggestion.
Home task cards show the expected outcome as a compact result preview with a separate `После` label, so the first step and result do not merge into one inline sentence.
Result next-task cards reuse the same compact `После` preview, so the user can evaluate the next suggested task's expected outcome before opening details or starting another timer.
The main-flow CTA icons are decorative and applied to the primary progression actions from onboarding through `Готово` and `Продолжить с задачей`, plus the timer `Пауза`/`Продолжить`/`Сброс` controls, keeping text labels as the source of meaning.
Progress uses the engine-provided next focus area to highlight the least-completed unfinished zone as `Следующая зона`; when the catalog is complete, the same compact summary switches to `Каталог закрыт`.
Task details keeps a pre-start briefing before the full step list, so the user can confirm scope, effort, duration and expected `После` outcome before committing to the timer. Task details start dock keeps `Начать` reachable on compact screens while the briefing and steps remain scrollable.
Timer keeps the original session target visible as `Цель: 5 мин` above the countdown, so the user still sees the intended scope after the remaining time starts changing. Timer outcome preview keeps the compact `После` result under the step list, so the user can check what “done enough” means without leaving the active session. Timer keeps the completion action in a bottom action dock, so `Готово` stays reachable while the plan remains scrollable on compact screens.
Startup error handling keeps catalog load failures generic Russian and retryable, so a transient local read failure is not a dead end.

## Первый запуск

Пользователь видит название, короткое объяснение, выбирает стартовую зону и нажимает “Начать”. Onboarding не обещает выбор энергии до появления этого контрола: энергию и время уточняет на Home в компактном блоке “Настроить подбор”. Collapsed Home показывает текущий подбор лёгкой строкой без карточного elevation, а expanded-состояние раскрывает зону/энергию/время. Вместо framed `Как это работает` card первый запуск использует лёгкий `Первые 5 минут` summary с фактами `Сначала`, `Затем`, `После`.

Progress/settings state is collected with lifecycle-aware Compose APIs, so DataStore observation follows the Activity lifecycle instead of collecting while the app is stopped.

## Обычная сессия

Пользователь открывает приложение, выбирает фильтр, запускает таймер, выполняет шаги и отмечает задачу. Сессия занимает 3-10 минут.

## Критерии успешного MVP

- Каталог содержит 80 валидных задач без временного наполнения.
- Прогресс сохраняется между запусками.
- Основной сценарий работает без интернета.
- UI читается на телефонах Android 15/16.
- System Back navigation проверена на Android 16.
- Large-screen max-width behavior проверен на Android 16.
- Release bundle собирается или причина честно описана.
