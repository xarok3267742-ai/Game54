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
ACCESSIBILITY_NOTES = ROOT / "docs/accessibility_notes.md"

DETAILS_DOCK_MARKERS: tuple[str, ...] = (
    "Box(modifier = Modifier.weight(1f))",
    "ScreenColumn(includeTopPadding = false)",
    "Spacer(Modifier.height(88.dp))",
    "BottomActionDock(modifier = Modifier.align(Alignment.BottomCenter))",
    'text = "Начать ${task.minutes} мин"',
    "onClick = onStart",
)

DOC_REQUIRED_MARKERS: tuple[tuple[Path, tuple[str, ...]], ...] = (
    (PRODUCT_SPEC, ("Task details start dock", "Начать", "compact")),
    (UI_AUDIT, ("Task details start dock", "Начать", "compact")),
    (QA_PLAN, ("check_task_details_start_dock.py", "Task details start dock")),
    (ACCESSIBILITY_NOTES, ("Task details start dock", "Начать")),
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
    key = str(path.relative_to(root))
    if docs is not None:
        return docs.get(key, "")
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def task_details_start_dock_failures(
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
    details = function_body(app_source, "TaskDetailsScreen")
    if not details:
        failures.append("TaskDetailsScreen body was not found")
    else:
        for marker in DETAILS_DOCK_MARKERS:
            if marker not in details:
                failures.append(f"Task details start dock is missing marker: {marker}")

        start_index = details.find('text = "Начать ${task.minutes} мин"')
        dock_index = details.find("BottomActionDock(modifier = Modifier.align(Alignment.BottomCenter))")
        clearance_index = details.find("Spacer(Modifier.height(88.dp))")
        result_index = details.find("TaskResultPreview(task.resultText)")

        if start_index >= 0 and dock_index >= 0 and start_index < dock_index:
            failures.append("Task details start action must live inside BottomActionDock")
        steps_index = details.find('Text("Шаги", style = MaterialTheme.typography.titleLarge)')
        if clearance_index >= 0 and steps_index >= 0 and clearance_index < steps_index:
            failures.append("Task details bottom spacer must come after scroll content")
        if dock_index >= 0 and result_index >= 0 and dock_index < result_index:
            failures.append("Task details dock must be layered after scroll content")

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
    failures = task_details_start_dock_failures()
    if failures:
        print("Task details start dock check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: Task details keeps the start action in a pinned bottom dock")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
