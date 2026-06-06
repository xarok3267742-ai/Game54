# Packaged Task Catalog Audit

## Status

`LOCAL_PROVEN`.

## Purpose

This audit documents the local gate that proves the task catalog shipped inside the built Android artifacts is the same catalog reviewed in source control.

## Automated Gate

`scripts/check_packaged_task_catalog.py` validates:

- source catalog exists at `app/src/main/res/raw/tasks_ru.json`;
- source catalog is valid UTF-8 JSON with 80 tasks;
- debug APK contains `res/raw/tasks_ru.json`;
- release AAB contains `base/res/raw/tasks_ru.json`;
- packaged catalog bytes match the source catalog bytes exactly;
- packaged catalog JSON equals the source JSON structure;
- no extra task-like JSON resource is packaged alongside the expected catalog.

Current local result:

```text
PASS: packaged task catalog matches source in debug APK and release AAB (80 tasks)
```

## Release Impact

This gate complements `scripts/check_task_catalog_quality.py`. The quality gate validates the source catalog text and distribution; this packaged gate verifies that the same reviewed catalog is present in both app artifacts.
