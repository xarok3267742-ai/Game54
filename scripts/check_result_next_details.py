#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app/src/main/java/ru/poryadok5/app/ui/PoryadokApp.kt"

REQUIRED_MARKERS: tuple[str, ...] = (
    "onOpenNext = { screen = AppScreen.Details(nextTask.id) }",
    "onOpenNext: () -> Unit",
    'text = "Посмотреть следующую"',
    'text = "Запустить таймер"',
    'text = "Посмотреть шаги"',
)

FORBIDDEN_MARKERS: tuple[str, ...] = (
    "onOpenNext = { screen = AppScreen.Timer(nextTask.id) }",
    "onOpenNext = { screen = AppScreen.Home }",
    'PrimaryAction("Запустить следующую", onNext)',
    'text = "Запустить следующую"',
)


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


def result_next_details_failures(
    app_source: str | None = None,
    required_markers: tuple[str, ...] = REQUIRED_MARKERS,
    forbidden_markers: tuple[str, ...] = FORBIDDEN_MARKERS,
    app_path: Path = APP,
    root: Path = ROOT,
) -> list[str]:
    if app_source is None:
        if not app_path.exists():
            return [f"missing app file: {app_path.relative_to(root)}"]
        app_source = app_path.read_text(encoding="utf-8")

    failures: list[str] = []
    result_body = function_body(app_source, "ResultScreen")
    if not result_body:
        failures.append("ResultScreen body was not found")

    route_markers = required_markers[:2]
    result_markers = required_markers[2:]
    for marker in route_markers:
        if marker not in app_source:
            failures.append(f"Result next-details flow is missing marker: {marker}")
    for marker in result_markers:
        if marker not in result_body:
            failures.append(f"Result next-details flow is missing marker: {marker}")

    if 'text = "Посмотреть следующую"' in result_body and "onClick = onOpenNext" not in result_body:
        failures.append("Result next-details primary action must use onOpenNext")
    if 'text = "Запустить таймер"' in result_body and "onClick = onNext" not in result_body:
        failures.append("Result next-details timer shortcut must use onNext")

    for marker in forbidden_markers:
        if marker in app_source:
            failures.append(f"Result next-details flow has an unsafe destination: {marker}")

    return failures


def main() -> int:
    failures = result_next_details_failures()
    if failures:
        print("Result next-details check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: Result next-task details flow opens task details before starting the timer")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
