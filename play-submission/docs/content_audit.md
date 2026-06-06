# Content Audit

## Content Blocks

- Onboarding copy: implemented in Russian, including the unframed `Первые 5 минут` first-run flow summary.
- Home/action copy: implemented in Russian.
- Settings/privacy copy: implemented in Russian.
- Task catalog: 80 original Russian tasks.
- Error/loading copy: implemented in Russian.

## Task Catalog Status

- 5 zones: Дом, Рабочее место, Цифровой порядок, Кухня, Личные вещи.
- 16 tasks per zone.
- Durations: 3, 5, 10 minutes.
- Energy: Лёгкая, Средняя, Бодрая.
- Each task has title, exactly 3 non-empty steps, result text. Runtime parsing rejects malformed text or steps before UI rendering.
- Release gate: `scripts/check_task_catalog_quality.py`.
- Audit: `docs/task_catalog_quality_audit.md`.
- Policy content risk gate: `scripts/check_policy_content_risk.py`.

## Removed / Avoided

- No lorem ipsum.
- No English draft filler.
- No technical user-facing strings in main flow.
- No copied brands, characters, store UI or copyrighted content.

## Remaining Risks

Некоторые задачи могут быть субъективно полезнее других; после закрытого тестирования стоит улучшить каталог на основе наблюдений, не добавляя analytics SDK.
