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

DETAILS_REQUIRED_MARKERS: tuple[str, ...] = (
    'Text("Перед стартом", style = MaterialTheme.typography.titleMedium)',
    '"Выполните шаги сверху вниз. Достаточно заметного улучшения, не идеального порядка."',
    'DetailBriefingFact(',
    'label = "зона"',
    'label = "энергия"',
    'label = "время"',
    "TaskResultPreview(task.resultText)",
    'Text("Шаги", style = MaterialTheme.typography.titleLarge)',
    'statusText = "выбрана"',
    'text = "Начать ${task.minutes} мин"',
    "onClick = onStart",
)

FACT_REQUIRED_MARKERS: tuple[str, ...] = (
    "private fun DetailBriefingFact(",
    ".defaultMinSize(minHeight = 56.dp)",
    ".padding(horizontal = 4.dp, vertical = 6.dp)",
    "MaterialTheme.typography.bodyMedium",
    "MaterialTheme.typography.labelLarge",
    "color = MutedText",
    "color = Sage",
)

DOC_REQUIRED_MARKERS: tuple[tuple[Path, tuple[str, ...]], ...] = (
    (PRODUCT_SPEC, ("Task details", "предстартовый briefing", "зона/энергия/время")),
    (UI_AUDIT, ("Task details briefing", "56dp", "Перед стартом", "unframed")),
    (QA_PLAN, ("check_task_details_briefing.py", "Task details briefing")),
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


def task_details_briefing_failures(
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
    fact = function_body(app_source, "DetailBriefingFact")

    if not details:
        failures.append("TaskDetailsScreen body was not found")
    else:
        for marker in DETAILS_REQUIRED_MARKERS:
            if marker not in details:
                failures.append(f"Task details briefing is missing marker: {marker}")

        before_start = details.find('Text("Перед стартом", style = MaterialTheme.typography.titleMedium)')
        result_preview = details.find("TaskResultPreview(task.resultText)")
        steps = details.find('Text("Шаги", style = MaterialTheme.typography.titleLarge)')
        if before_start >= 0 and steps >= 0 and before_start > steps:
            failures.append("Task details briefing must appear before the full step list")
        if min(before_start, result_preview, steps) >= 0 and not (before_start < result_preview < steps):
            failures.append("Task details result preview must appear inside briefing before the full step list")

    if not fact:
        failures.append("DetailBriefingFact body was not found")
    else:
        for marker in FACT_REQUIRED_MARKERS:
            if marker not in fact:
                failures.append(f"DetailBriefingFact is missing marker: {marker}")
        for marker in ("Surface(", "BorderStroke(", "MaterialTheme.shapes.small"):
            if marker in fact:
                failures.append(f"DetailBriefingFact must stay unframed, found: {marker}")

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
    failures = task_details_briefing_failures()
    if failures:
        print("Task details briefing check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: Task details keeps a clear pre-start briefing before the step list")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
