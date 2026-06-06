#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UI_SOURCE = ROOT / "app/src/main/java/ru/poryadok5/app/ui/PoryadokApp.kt"


def function_body(source: str, name: str) -> str:
    marker = f"private fun {name}"
    start = source.find(marker)
    if start == -1:
        return ""

    brace_start = source.find("{", start)
    if brace_start == -1:
        return ""

    depth = 0
    for index in range(brace_start, len(source)):
        char = source[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[brace_start + 1 : index]
    return ""


def main() -> int:
    source = UI_SOURCE.read_text(encoding="utf-8")
    failures: list[str] = []

    metric_count = source.count('MetricPill("выполнено"')
    if metric_count != 3:
        failures.append(f"expected 3 aligned 'выполнено' metric labels, found {metric_count}")

    forbidden_markers = (
        'MetricPill("сделано"',
        'if (completed) "сделано"',
        'statusText ?: if (completed) "сделано"',
    )
    for marker in forbidden_markers:
        if marker in source:
            failures.append(f"outdated active UI label remains: {marker}")

    if 'statusText ?: if (completed) "выполнено" else "новая"' not in source:
        failures.append("TaskCard completed status chip must use 'выполнено'")

    task_card = function_body(source, "TaskCard")
    status_pill = function_body(source, "TaskStatusPill")
    if not status_pill:
        failures.append("TaskStatusPill must exist for non-interactive task status")
    if "TaskStatusPill(" not in task_card:
        failures.append("TaskCard must render status through TaskStatusPill")
    if status_pill:
        forbidden_status_affordance = (
            "BorderStroke(",
            "secondaryContainer",
            ".clickable(",
            "Role.Button",
            "onClick",
        )
        for marker in forbidden_status_affordance:
            if marker in status_pill:
                failures.append(f"TaskStatusPill must not look or behave like a button: {marker}")
        if "CircleShape" not in status_pill or "Modifier.size(8.dp)" not in status_pill:
            failures.append("TaskStatusPill must use a small dot indicator instead of a filled button chip")

    if failures:
        print("UI label consistency check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: active UI metric/status labels are aligned and task status is non-interactive")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
