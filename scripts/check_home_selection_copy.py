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

EXPECTED_COPY: tuple[str, ...] = (
    "Совпадает с выбором",
    "Зона и время совпали",
    "Ближайшая свободная задача",
)

FORBIDDEN_COPY: tuple[str, ...] = (
    "Подбор: точно по фильтру",
    "Подбор: зона и время совпали",
    "Подбор: ближайшая свободная задача",
)

DOC_REQUIRED_MARKERS: tuple[tuple[Path, tuple[str, ...]], ...] = (
    (PRODUCT_SPEC, ("Home", "Совпадает с выбором", "Ближайшая свободная задача")),
    (UI_AUDIT, ("Home selection copy", "без слова `фильтр`")),
    (QA_PLAN, ("check_home_selection_copy.py", "Home selection copy")),
)


def function_body(source: str, name: str) -> str:
    marker = f"fun {name}("
    start = source.find(marker)
    if start < 0:
        marker = f"private fun {name}("
        start = source.find(marker)
    if start < 0:
        return ""
    next_match = re.search(r"\n(?:@Composable\n)?(?:private\s+)?fun\s+", source[start + len(marker) :])
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


def home_selection_copy_failures(
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
    body = function_body(app_source, "TaskSuggestionQuality.homeSelectionNote")
    if not body:
        failures.append("TaskSuggestionQuality.homeSelectionNote body was not found")
    else:
        for expected in EXPECTED_COPY:
            if expected not in body:
                failures.append(f"Home selection copy is missing: {expected}")
        for forbidden in FORBIDDEN_COPY:
            if forbidden in body:
                failures.append(f"Home selection copy still uses technical wording: {forbidden}")

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
    failures = home_selection_copy_failures()
    if failures:
        print("Home selection copy check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: Home selection-quality hints use user-facing Russian copy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
