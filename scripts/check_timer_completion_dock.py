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

TIMER_REQUIRED_MARKERS: tuple[str, ...] = (
    "Box(modifier = Modifier.weight(1f))",
    "BottomActionDock(modifier = Modifier.align(Alignment.BottomCenter))",
    'text = "Готово"',
    "Spacer(Modifier.height(88.dp))",
)

DOCK_REQUIRED_MARKERS: tuple[str, ...] = (
    "private fun BottomActionDock(",
    "shadowElevation = 4.dp",
    "widthIn(max = ContentMaxWidth)",
    "padding(horizontal = 20.dp, vertical = 12.dp)",
    "verticalArrangement = Arrangement.spacedBy(8.dp)",
)

DOC_REQUIRED_MARKERS: tuple[tuple[Path, tuple[str, ...]], ...] = (
    (PRODUCT_SPEC, ("Timer", "bottom action dock", "Готово")),
    (UI_AUDIT, ("Timer completion dock", "Готово", "компактных экранах")),
    (QA_PLAN, ("check_timer_completion_dock.py", "Timer completion dock")),
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


def timer_completion_dock_failures(
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
    timer = function_body(app_source, "TimerScreen")
    dock = function_body(app_source, "BottomActionDock")

    if not timer:
        failures.append("TimerScreen body was not found")
    else:
        for marker in TIMER_REQUIRED_MARKERS:
            if marker not in timer:
                failures.append(f"Timer completion dock is missing marker: {marker}")

        dock_call = timer.find("BottomActionDock(modifier = Modifier.align(Alignment.BottomCenter))")
        complete_action = timer.find('text = "Готово"')
        if dock_call >= 0 and complete_action >= 0 and complete_action < dock_call:
            failures.append("Timer completion action must live in BottomActionDock, not in the scroll content")

    if not dock:
        failures.append("BottomActionDock body was not found")
    else:
        for marker in DOCK_REQUIRED_MARKERS:
            if marker not in dock:
                failures.append(f"BottomActionDock is missing marker: {marker}")

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
    failures = timer_completion_dock_failures()
    if failures:
        print("Timer completion-dock check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: Timer keeps the completion action pinned in a bottom action dock")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
