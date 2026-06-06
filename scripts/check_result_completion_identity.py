#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app/src/main/java/ru/poryadok5/app/ui/PoryadokApp.kt"
PRODUCT_SPEC = ROOT / "docs/product_spec.md"
UI_AUDIT = ROOT / "docs/ui_audit.md"
QA_PLAN = ROOT / "docs/qa_test_plan.md"

REQUIRED_MARKERS: tuple[str, ...] = (
    'Text("Готово", style = MaterialTheme.typography.displaySmall)',
    'Text("Сделано: ${task.title}", style = MaterialTheme.typography.titleMedium, color = Sage)',
    "Text(task.resultText, style = MaterialTheme.typography.bodyLarge, color = MutedText)",
)

DOC_REQUIRED_MARKERS: tuple[tuple[Path, tuple[str, ...]], ...] = (
    (PRODUCT_SPEC, ("Result", "Сделано")),
    (UI_AUDIT, ("Экран результата", "Сделано")),
    (QA_PLAN, ("check_result_completion_identity.py", "Сделано")),
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


def result_completion_identity_failures(
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
            failures.append(f"Result completion identity is missing marker: {marker}")

    title_index = result_body.find('Text("Готово"')
    done_index = result_body.find('Text("Сделано: ${task.title}"')
    result_index = result_body.find("Text(task.resultText")
    if min(title_index, done_index, result_index) == -1 or not (title_index < done_index < result_index):
        failures.append("Result completion identity should appear between the title and task result text")

    if "Сделано: ${nextTask.title}" in result_body:
        failures.append("Result completion identity must use the completed task title, not nextTask")

    if docs is None:
        docs = {}
        for path, _ in DOC_REQUIRED_MARKERS:
            if not path.exists():
                failures.append(f"missing documentation file: {path.relative_to(root)}")
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
    failures = result_completion_identity_failures()
    if failures:
        print("Result completion-identity check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: Result screen names the completed task before the task-specific outcome")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
