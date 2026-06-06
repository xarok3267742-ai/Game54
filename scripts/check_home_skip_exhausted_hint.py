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

HOME_REQUIRED_MARKERS: tuple[str, ...] = (
    'text = "Другая задача"',
    "enabled = canSkipTask",
    "AnimatedVisibility(visible = !canSkipTask)",
    '"Других задач по этому подбору сейчас нет. Измените подбор или выполните текущую."',
    "color = MutedText",
)

FORBIDDEN_MARKERS: tuple[str, ...] = (
    "AnimatedVisibility(visible = canSkipTask)",
    'Text("Других задач по этому подбору сейчас нет. Измените подбор или выполните текущую.")',
)

DOC_REQUIRED_MARKERS: tuple[tuple[Path, tuple[str, ...]], ...] = (
    (PRODUCT_SPEC, ("Другая задача", "Других задач по этому подбору сейчас нет")),
    (UI_AUDIT, ("Home skip exhausted hint", "Других задач по этому подбору сейчас нет")),
    (QA_PLAN, ("check_home_skip_exhausted_hint.py", "Home skip exhausted hint")),
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


def home_skip_exhausted_hint_failures(
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
    home = function_body(app_source, "HomeScreen")
    if not home:
        failures.append("HomeScreen body was not found")
    else:
        for marker in HOME_REQUIRED_MARKERS:
            if marker not in home:
                failures.append(f"Home skip exhausted hint is missing marker: {marker}")

        for marker in FORBIDDEN_MARKERS:
            if marker in home:
                failures.append(f"Home skip exhausted hint contains forbidden marker: {marker}")

        skip_index = home.find('text = "Другая задача"')
        hint_index = home.find("AnimatedVisibility(visible = !canSkipTask)")
        metrics_index = home.find('MetricPill("выполнено"')
        if skip_index >= 0 and hint_index >= 0 and hint_index < skip_index:
            failures.append("Home skip exhausted hint must appear after the skip action")
        if hint_index >= 0 and metrics_index >= 0 and hint_index > metrics_index:
            failures.append("Home skip exhausted hint must appear before the metrics row")

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
    failures = home_skip_exhausted_hint_failures()
    if failures:
        print("Home skip exhausted-hint check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: Home explains when no alternative task is available for the current selection")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
