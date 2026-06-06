# Task Catalog Quality Audit

## Scope

This audit covers `app/src/main/res/raw/tasks_ru.json`, the offline MVP task catalog used by `Порядок 5`.

## Automated Gate

`scripts/check_task_catalog_quality.py` verifies:

- exactly 80 task objects;
- exactly 16 tasks in each area: `Home`, `Work`, `Digital`, `Kitchen`, `Personal`;
- sequential ids per area, from `home_001` through `personal_016`;
- allowed energy values: `Light`, `Medium`, `Active`;
- allowed durations: 3, 5 and 10 minutes;
- minimum coverage for every energy level and duration;
- exact schema keys: `id`, `area`, `energy`, `minutes`, `title`, `steps`, `resultText`;
- exactly 3 steps per task;
- Cyrillic visible text for titles, steps and result text;
- no Latin letters in user-facing task text;
- no draft markers in task text;
- no duplicate ids, titles or step text;
- compact text lengths that fit the current task detail and timer UI.

## Current Evidence

- Total tasks: 80.
- Area distribution: 16 per area.
- Energy distribution: `Light` 30, `Medium` 30, `Active` 20.
- Duration distribution: 3 minutes: 25, 5 minutes: 35, 10 minutes: 20.
- Longest title: 35 characters.
- Longest step: 69 characters.
- Longest result text: 56 characters.

## Release Status

Status: `LOCAL_PROVEN`.

The catalog is original Russian offline content and is covered by the Kotlin unit test `TaskCatalogTest`, the source-quality release script `scripts/check_task_catalog_quality.py` and the packaged equality gate `scripts/check_packaged_task_catalog.py`.

Runtime parser coverage in `TaskCatalogTest` also rejects blank ids, duplicate ids, unsupported durations, blank title/result text, wrong step counts and blank step text before `MicroTask` reaches UI code that displays the first step.
