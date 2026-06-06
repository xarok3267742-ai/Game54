#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app/src/main/java/ru/poryadok5/app/ui/PoryadokApp.kt"
UI_AUDIT = ROOT / "docs/ui_audit.md"
QA_PLAN = ROOT / "docs/qa_test_plan.md"

FORBIDDEN_COPY: tuple[str, ...] = (
    "Что изменилось",
    "Вы закрыли маленькую задачу",
)

REQUIRED_MARKERS: tuple[str, ...] = (
    'Text("Готово", style = MaterialTheme.typography.displaySmall)',
    "Text(task.resultText, style = MaterialTheme.typography.bodyLarge, color = MutedText)",
    'MetricPill("выполнено"',
    "TaskCard(",
    'label = if (hasFreshNextTask) "Дальше без повтора" else "Каталог пройден"',
    "showResult = true",
    "PrimaryAction(",
    'text = "Посмотреть следующую"',
    "onClick = onOpenNext",
)

DOC_REQUIRED_MARKERS: tuple[tuple[Path, tuple[str, ...]], ...] = (
    (UI_AUDIT, ("Экран результата", "task-specific result", "без generic amber", "После")),
    (QA_PLAN, ("check_result_content_focus.py", "Что изменилось", "next-task preview", "showResult")),
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


def result_content_focus_failures(
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
    result_body = function_body(app_source, "ResultScreen")
    if not result_body:
        failures.append("ResultScreen body was not found")
        return failures

    for marker in REQUIRED_MARKERS:
        if marker not in result_body:
            failures.append(f"Result content focus is missing marker: {marker}")

    for marker in FORBIDDEN_COPY:
        if marker in result_body:
            failures.append(f"Result content focus must not keep generic completion copy: {marker}")

    if "AmberSoft" in result_body:
        failures.append("Result content focus must not use the generic amber completion card")

    order_markers = (
        "Text(task.resultText",
        'MetricPill("выполнено"',
        "TaskCard(",
        'text = "Посмотреть следующую"',
    )
    indexes = [result_body.find(marker) for marker in order_markers]
    if any(index == -1 for index in indexes) or indexes != sorted(indexes):
        failures.append("Result content order should be task result, metrics, next-task preview, then primary action")

    if re.search(r"AppCard\(containerColor\s*=\s*AmberSoft\)", result_body):
        failures.append("Result content focus must not render the old amber explanatory card")

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
    failures = result_content_focus_failures()
    if failures:
        print("Result content-focus check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: Result screen keeps task-specific completion content focused on the next action")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
