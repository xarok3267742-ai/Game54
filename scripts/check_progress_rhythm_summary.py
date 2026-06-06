#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app/src/main/java/ru/poryadok5/app/ui/PoryadokApp.kt"
UI_AUDIT = ROOT / "docs/ui_audit.md"
QA_PLAN = ROOT / "docs/qa_test_plan.md"

OLD_PARAGRAPH = (
    "Серия растёт один раз в день. Несколько задач за день увеличивают общий счётчик, "
    "но не накручивают серию."
)

APP_REQUIRED_MARKERS: tuple[str, ...] = (
    "ProgressRhythmSummary()",
    "private fun ProgressRhythmSummary()",
    "private fun ProgressRhythmItem(",
    'label = "Серия"',
    'value = "1 раз в день"',
    'label = "Счётчик"',
    'value = "каждая задача"',
    "defaultMinSize(minHeight = 56.dp)",
    "padding(horizontal = 4.dp, vertical = 6.dp)",
)

APP_FORBIDDEN_MARKERS: tuple[str, ...] = (
    OLD_PARAGRAPH,
    "ProgressRhythmItem(\n            label = \"Серия\",\n            value = \"растёт один раз в день\"",
)

DOC_REQUIRED_MARKERS: tuple[tuple[Path, tuple[str, ...]], ...] = (
    (UI_AUDIT, ("Progress rhythm summary", "Серия", "Счётчик")),
    (QA_PLAN, ("Progress rhythm summary", "Серия", "Счётчик")),
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


def progress_rhythm_summary_failures(
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
    for marker in APP_REQUIRED_MARKERS:
        if marker not in app_source:
            failures.append(f"Progress rhythm summary is missing marker: {marker}")

    for marker in APP_FORBIDDEN_MARKERS:
        if marker in app_source:
            failures.append(f"Progress rhythm summary kept old paragraph-style copy: {marker}")

    summary_body = function_body(app_source, "ProgressRhythmSummary")
    item_body = function_body(app_source, "ProgressRhythmItem")
    if "ProgressRhythmItem(" not in summary_body:
        failures.append("ProgressRhythmSummary must render rhythm facts through ProgressRhythmItem")
    for marker in (".clickable(", "Role.Button", "onClick"):
        if marker in item_body:
            failures.append(f"ProgressRhythmItem must stay non-interactive: {marker}")
    for marker in ("Surface(", "border =", "MaterialTheme.shapes.small", "MaterialTheme.colorScheme.surface"):
        if marker in item_body:
            failures.append(f"ProgressRhythmItem must stay unframed inside the rhythm card: {marker}")

    if docs is None:
        docs = {}
        for path, _ in DOC_REQUIRED_MARKERS:
            if not path.exists():
                failures.append(f"missing doc file: {path.relative_to(root)}")
                continue
            docs[str(path.relative_to(root))] = path.read_text(encoding="utf-8")

    for path, markers in DOC_REQUIRED_MARKERS:
        doc_key = str(path.relative_to(root))
        doc_source = docs.get(doc_key, "")
        for marker in markers:
            if marker not in doc_source:
                failures.append(f"{doc_key} is missing marker: {marker}")

    return failures


def main() -> int:
    failures = progress_rhythm_summary_failures()
    if failures:
        print("Progress rhythm-summary check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: Progress rhythm summary is compact, scannable and non-interactive")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
