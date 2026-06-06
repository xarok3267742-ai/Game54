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

TASK_CARD_REQUIRED_MARKERS: tuple[str, ...] = (
    "showResult: Boolean = false",
    "TaskResultPreview(task.resultText)",
)

PREVIEW_REQUIRED_MARKERS: tuple[str, ...] = (
    "private fun TaskResultPreview(",
    ".fillMaxWidth()",
    ".defaultMinSize(minHeight = 48.dp)",
    "verticalArrangement = Arrangement.spacedBy(2.dp)",
    'Text("После", style = MaterialTheme.typography.labelLarge, color = Sage)',
    "Text(resultText, style = MaterialTheme.typography.bodyMedium, color = MutedText)",
)

DOC_REQUIRED_MARKERS: tuple[tuple[Path, tuple[str, ...]], ...] = (
    (PRODUCT_SPEC, ("Home", "compact result preview", "После")),
    (UI_AUDIT, ("Home task result preview", "compact result preview", "После")),
    (QA_PLAN, ("check_task_result_preview.py", "Home task result preview")),
)


def function_body(source: str, name: str) -> str:
    marker = f"private fun {name}("
    start = source.find(marker)
    if start < 0:
        return ""
    next_match = re.search(r"\n@Composable\nprivate fun\s+", source[start + len(marker) :])
    if next_match is None:
        return source[start:]
    return source[start : start + len(marker) + next_match.start()]


def read_doc(path: Path, docs: dict[str, str] | None, root: Path) -> str | None:
    doc_key = str(path.relative_to(root))
    if docs is not None:
        return docs.get(doc_key, "")
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def task_result_preview_failures(
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
    task_card = function_body(app_source, "TaskCard")
    preview = function_body(app_source, "TaskResultPreview")

    if not task_card:
        failures.append("TaskCard body was not found")
    else:
        for marker in TASK_CARD_REQUIRED_MARKERS:
            if marker not in task_card:
                failures.append(f"TaskCard result preview is missing marker: {marker}")
        if "После: ${task.resultText}" in task_card or "После:" in task_card:
            failures.append("TaskCard must not render the result as the old inline 'После: ...' sentence")

    if not preview:
        failures.append("TaskResultPreview body was not found")
    else:
        for marker in PREVIEW_REQUIRED_MARKERS:
            if marker not in preview:
                failures.append(f"TaskResultPreview is missing marker: {marker}")
        for marker in ("Surface(", "AppCard(", "BorderStroke(", ".clickable(", "Role.Button", "onClick"):
            if marker in preview:
                failures.append(f"TaskResultPreview must stay compact, unframed and non-interactive, found: {marker}")

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
    failures = task_result_preview_failures()
    if failures:
        print("Task result-preview check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: Home task result preview is compact, scannable and non-interactive")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
