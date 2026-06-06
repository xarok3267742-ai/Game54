#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app/src/main/java/ru/poryadok5/app/ui/PoryadokApp.kt"
PRODUCT_SPEC = ROOT / "docs/product_spec.md"
UI_AUDIT = ROOT / "docs/ui_audit.md"
QA_PLAN = ROOT / "docs/qa_test_plan.md"

APP_REQUIRED_MARKERS: tuple[str, ...] = (
    'text = "Цель: ${task.minutes} мин"',
    "MaterialTheme.typography.labelLarge",
    "MaterialTheme.colorScheme.primary",
)

DOC_REQUIRED_MARKERS: tuple[tuple[Path, tuple[str, ...]], ...] = (
    (PRODUCT_SPEC, ("Timer session goal", "Цель: 5 мин")),
    (UI_AUDIT, ("Timer session goal", "Цель: 5 мин")),
    (QA_PLAN, ("check_timer_session_goal.py", "Timer session goal")),
)


def function_body(source: str, name: str) -> str:
    marker = f"private fun {name}("
    start = source.find(marker)
    if start < 0:
        return ""
    next_match = re.search(r"\n@Composable\nprivate fun\s+", source[start + len(marker):])
    if next_match is None:
        return source[start:]
    return source[start:start + len(marker) + next_match.start()]


def read_doc(path: Path, docs: dict[str, str] | None, root: Path) -> str | None:
    doc_key = str(path.relative_to(root))
    if docs is not None:
        return docs.get(doc_key, "")
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def timer_session_goal_failures(
    app_source: str | None = None,
    docs: dict[str, str] | None = None,
    app_path: Path = APP,
    root: Path = ROOT,
) -> list[str]:
    if app_source is None:
        if not app_path.exists():
            return [f"missing app file: {app_path.relative_to(root)}"]
        app_source = app_path.read_text(encoding="utf-8")

    failures: list[str] = []
    timer = function_body(app_source, "TimerScreen")
    if not timer:
        failures.append("TimerScreen body was not found")
    else:
        for marker in APP_REQUIRED_MARKERS:
            if marker not in timer:
                failures.append(f"Timer session goal is missing marker: {marker}")

        meta_index = timer.find('Text("${task.area.label} · ${task.energy.label}"')
        goal_index = timer.find('text = "Цель: ${task.minutes} мин"')
        progress_index = timer.find("ProgressLine(")
        clock_index = timer.find("formatTime(remainingSeconds)")
        if -1 not in (meta_index, goal_index, progress_index, clock_index):
            if not (meta_index < goal_index < progress_index < clock_index):
                failures.append("Timer session goal must stay between task metadata and timer progress/time")

    for path, markers in DOC_REQUIRED_MARKERS:
        text = read_doc(path, docs, root)
        if text is None:
            failures.append(f"missing documentation file: {path.relative_to(root)}")
            continue
        for marker in markers:
            if marker not in text:
                failures.append(f"{path.relative_to(root)} is missing marker: {marker}")

    return failures


def main() -> int:
    failures = timer_session_goal_failures()
    if failures:
        print("Timer session-goal check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: Timer shows the original session goal above the countdown")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
