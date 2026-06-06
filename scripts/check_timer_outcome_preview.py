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

TIMER_REQUIRED_MARKERS: tuple[str, ...] = (
    'Text("План", style = MaterialTheme.typography.titleMedium)',
    "task.steps.forEachIndexed",
    "TaskResultPreview(task.resultText)",
)

DOC_REQUIRED_MARKERS: tuple[tuple[Path, tuple[str, ...]], ...] = (
    (PRODUCT_SPEC, ("Timer outcome preview", "После")),
    (UI_AUDIT, ("Timer outcome preview", "После")),
    (QA_PLAN, ("check_timer_outcome_preview.py", "Timer outcome preview")),
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


def timer_outcome_preview_failures(
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
        for marker in TIMER_REQUIRED_MARKERS:
            if marker not in timer:
                failures.append(f"Timer outcome preview is missing marker: {marker}")

        plan_index = timer.find('Text("План", style = MaterialTheme.typography.titleMedium)')
        steps_index = timer.find("task.steps.forEachIndexed")
        preview_index = timer.find("TaskResultPreview(task.resultText)")
        controls_index = timer.find("SecondaryAction(")
        if -1 not in (plan_index, steps_index, preview_index, controls_index):
            if not (plan_index < steps_index < preview_index < controls_index):
                failures.append("Timer outcome preview must stay after the step list and before timer controls")

        if "После: ${task.resultText}" in timer or "После:" in timer:
            failures.append("Timer must reuse compact TaskResultPreview instead of the old inline 'После: ...' sentence")

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
    failures = timer_outcome_preview_failures()
    if failures:
        print("Timer outcome-preview check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: Timer shows the compact outcome preview after the plan")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
