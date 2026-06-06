#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app/src/main/java/ru/poryadok5/app/ui/PoryadokApp.kt"
ENGINE = ROOT / "app/src/main/java/ru/poryadok5/app/domain/PoryadokEngine.kt"
PRODUCT_SPEC = ROOT / "docs/product_spec.md"
UI_AUDIT = ROOT / "docs/ui_audit.md"
ACCESSIBILITY = ROOT / "docs/accessibility_notes.md"
QA_PLAN = ROOT / "docs/qa_test_plan.md"

APP_REQUIRED_MARKERS: tuple[str, ...] = (
    "val nextFocusArea = engine.nextFocusArea(preferences.progress.completedTaskIds)",
    "ProgressFocusSummary(",
    "area = nextFocusArea",
    "engine.completedCountByArea(it, preferences.progress.completedTaskIds)",
    "total = nextFocusArea?.let(engine::countByArea) ?: totalCatalogCount",
)

ENGINE_REQUIRED_MARKERS: tuple[str, ...] = (
    "fun nextFocusArea(completedIds: Set<String>): TaskArea?",
    "normalizedCompletedTaskIds(completedIds)",
    ".filter { it.completed < it.total }",
    ".minWithOrNull(",
    "compareBy<AreaProgress> { it.completed.toFloat() / it.total.toFloat() }",
    "private data class AreaProgress(",
)

SUMMARY_REQUIRED_MARKERS: tuple[str, ...] = (
    "private fun ProgressFocusSummary(area: TaskArea?, completed: Int, total: Int)",
    ".defaultMinSize(minHeight = 56.dp)",
    ".padding(horizontal = 4.dp, vertical = 4.dp)",
    'text = if (area == null) "Каталог закрыт" else "Следующая зона"',
    "Все $total задач отмечены",
    "${area.label}: $completed из $total. Хорошая точка для следующей 5-минутки.",
    "MaterialTheme.colorScheme.secondary",
    "color = MutedText",
)

DOC_REQUIRED_MARKERS: tuple[tuple[Path, tuple[str, ...]], ...] = (
    (PRODUCT_SPEC, ("Progress", "next focus area", "Следующая зона")),
    (UI_AUDIT, ("Progress focus summary", "Следующая зона", "Каталог закрыт")),
    (ACCESSIBILITY, ("Progress focus summary", "non-interactive", "Следующая зона")),
    (QA_PLAN, ("check_progress_focus_summary.py", "nextFocusArea")),
)


def function_body(source: str, name: str) -> str:
    marker = f"private fun {name}("
    start = source.find(marker)
    if start < 0:
        marker = f"fun {name}("
        start = source.find(marker)
    if start < 0:
        return ""
    next_match = re.search(r"\n@Composable\n(?:private\s+)?fun\s+|\n\s{4}fun\s+", source[start + len(marker):])
    if next_match is None:
        return source[start:]
    return source[start:start + len(marker) + next_match.start()]


def read_text(path: Path, root: Path) -> str | None:
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def display_path(path: Path, root: Path) -> str:
    for base in (root, ROOT):
        try:
            return str(path.relative_to(base))
        except ValueError:
            continue
    return str(path)


def progress_focus_summary_failures(
    app_source: str | None = None,
    engine_source: str | None = None,
    docs: dict[str, str] | None = None,
    app_path: Path = APP,
    engine_path: Path = ENGINE,
    root: Path = ROOT,
) -> list[str]:
    failures: list[str] = []
    if app_source is None:
        app_source = read_text(app_path, root)
        if app_source is None:
            failures.append(f"missing app file: {app_path.relative_to(root)}")
            app_source = ""
    if engine_source is None:
        engine_source = read_text(engine_path, root)
        if engine_source is None:
            failures.append(f"missing engine file: {engine_path.relative_to(root)}")
            engine_source = ""

    progress = function_body(app_source, "ProgressScreen")
    summary = function_body(app_source, "ProgressFocusSummary")
    engine_method = function_body(engine_source, "nextFocusArea")

    if not progress:
        failures.append("ProgressScreen body was not found")
    else:
        for marker in APP_REQUIRED_MARKERS:
            if marker not in progress:
                failures.append(f"Progress focus summary is missing marker: {marker}")

    if not summary:
        failures.append("ProgressFocusSummary body was not found")
    else:
        for marker in SUMMARY_REQUIRED_MARKERS:
            if marker not in summary:
                failures.append(f"ProgressFocusSummary is missing marker: {marker}")
        for marker in ("AppCard(", "Surface(", "BorderStroke(", ".clickable(", "Role.Button", "onClick"):
            if marker in summary:
                failures.append(f"ProgressFocusSummary must stay unframed and non-interactive: {marker}")

    if not engine_method:
        failures.append("PoryadokEngine.nextFocusArea body was not found")
    else:
        for marker in ENGINE_REQUIRED_MARKERS:
            if marker not in engine_source:
                failures.append(f"nextFocusArea is missing marker: {marker}")

    for path, markers in DOC_REQUIRED_MARKERS:
        doc_key = display_path(path, root)
        if docs is None:
            text = read_text(path, root)
            if text is None:
                failures.append(f"missing documentation file: {doc_key}")
                continue
        else:
            text = docs.get(doc_key, "")
        for marker in markers:
            if marker not in text:
                failures.append(f"{doc_key} is missing marker: {marker}")

    return failures


def main() -> int:
    failures = progress_focus_summary_failures()
    if failures:
        print("Progress focus-summary check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: Progress screen recommends the next unfinished focus area")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
