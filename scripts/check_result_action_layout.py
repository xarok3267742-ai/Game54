#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app/src/main/java/ru/poryadok5/app/ui/PoryadokApp.kt"
UI_AUDIT = ROOT / "docs/ui_audit.md"
QA_PLAN = ROOT / "docs/qa_test_plan.md"

APP_REQUIRED_MARKERS: tuple[str, ...] = (
    "Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {",
    'text = "На главный экран"',
    "onClick = onHome",
    "icon = HomeIcon",
    'text = "Посмотреть итоги"',
    "onClick = onProgress",
    "icon = StatsIcon",
)

APP_FORBIDDEN_MARKERS: tuple[str, ...] = (
    'SecondaryAction("На главный экран", onHome)',
    'SecondaryAction("Посмотреть итоги", onProgress)',
)

DOC_REQUIRED_MARKERS: tuple[tuple[Path, tuple[str, ...]], ...] = (
    (UI_AUDIT, ("Экран результата", "На главный экран", "Посмотреть итоги", "HomeIcon", "StatsIcon")),
    (QA_PLAN, ("Result action layout", "На главный экран", "Посмотреть итоги", "HomeIcon", "StatsIcon")),
)


def result_action_layout_failures(
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
            failures.append(f"Result action layout is missing marker: {marker}")

    if app_source.count("modifier = Modifier.weight(1f)") < 2:
        failures.append("Result action layout must give both peer actions Modifier.weight(1f)")

    for marker in APP_FORBIDDEN_MARKERS:
        if marker in app_source:
            failures.append(f"Result action layout has a stacked full-width action: {marker}")

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
    failures = result_action_layout_failures()
    if failures:
        print("Result action-layout check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: Result screen keeps home/progress actions in a compact icon-supported peer row")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
