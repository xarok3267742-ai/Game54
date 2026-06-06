#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app/src/main/java/ru/poryadok5/app/ui/PoryadokApp.kt"
UI_AUDIT = ROOT / "docs/ui_audit.md"
QA_PLAN = ROOT / "docs/qa_test_plan.md"

APP_REQUIRED_MARKERS: tuple[str, ...] = (
    "onHome = { screen = AppScreen.Home }",
    "onHome: () -> Unit",
)

PROGRESS_REQUIRED_MARKERS: tuple[str, ...] = (
    "PrimaryAction(",
    'text = "Продолжить с задачей"',
    "onClick = onHome",
    "icon = Icons.AutoMirrored.Filled.ArrowForward",
)

APP_FORBIDDEN_MARKERS: tuple[str, ...] = (
    "onClick = onBack",
    "onClick = onSettings",
    "onClick = onStart",
)

DOC_REQUIRED_MARKERS: tuple[tuple[Path, tuple[str, ...]], ...] = (
    (UI_AUDIT, ("Продолжить с задачей", "Итоги")),
    (QA_PLAN, ("Продолжить с задачей", "Итоги")),
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


def progress_continue_failures(
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
    progress = function_body(app_source, "ProgressScreen")
    for marker in APP_REQUIRED_MARKERS:
        if marker not in app_source:
            failures.append(f"Progress continue action is missing marker: {marker}")

    if not progress:
        failures.append("ProgressScreen body was not found")
    else:
        for marker in PROGRESS_REQUIRED_MARKERS:
            if marker not in progress:
                failures.append(f"Progress continue action is missing marker: {marker}")

        for marker in APP_FORBIDDEN_MARKERS:
            if marker in progress:
                failures.append(f"Progress continue action uses an unsafe callback: {marker}")

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
    failures = progress_continue_failures()
    if failures:
        print("Progress continue-action check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: Progress screen has a primary continue action back to the task flow")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
