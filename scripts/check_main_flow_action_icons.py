#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app/src/main/java/ru/poryadok5/app/ui/PoryadokApp.kt"
PRODUCT_SPEC = ROOT / "docs/product_spec.md"
UI_AUDIT = ROOT / "docs/ui_audit.md"
ACCESSIBILITY = ROOT / "docs/accessibility_notes.md"
QA_PLAN = ROOT / "docs/qa_test_plan.md"

REQUIRED_APP_MARKERS: tuple[str, ...] = (
    "import androidx.compose.material.icons.automirrored.filled.ArrowForward",
    "import androidx.compose.material.icons.automirrored.filled.List",
    "import androidx.compose.material.icons.filled.Done",
    "import androidx.compose.material.icons.filled.PlayArrow",
    "import androidx.compose.material.icons.filled.Refresh",
    'name = "Pause"',
    'text = "Начать",',
    'text = "Начать ${task.minutes} мин"',
    'text = "Готово"',
    'text = "Посмотреть следующую"',
    'text = "Запустить таймер"',
    'text = "Все шаги"',
    'text = "Повторить задачу"',
    'text = "Посмотреть шаги"',
    'text = "Продолжить с задачей"',
    "icon = Icons.Filled.PlayArrow",
    "icon = Icons.Filled.Done",
    "icon = Icons.Filled.Refresh",
    "icon = Icons.AutoMirrored.Filled.List",
    "icon = Icons.AutoMirrored.Filled.ArrowForward",
    "icon = if (running) PauseIcon else Icons.Filled.PlayArrow",
)

DOC_REQUIRED_MARKERS: tuple[tuple[Path, tuple[str, ...]], ...] = (
    (PRODUCT_SPEC, ("main-flow CTA icons", "Готово", "Продолжить с задачей")),
    (UI_AUDIT, ("Main-flow CTA icons", "Done", "ArrowForward", "PauseIcon")),
    (ACCESSIBILITY, ("Main-flow CTA icons", "decorative", "text labels", "timer controls")),
    (QA_PLAN, ("check_main_flow_action_icons.py", "main-flow CTA icons")),
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


def main_flow_action_icon_failures(
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
    for marker in REQUIRED_APP_MARKERS:
        if marker not in app_source:
            failures.append(f"main-flow CTA icons are missing marker: {marker}")

    result = function_body(app_source, "ResultScreen")
    progress = function_body(app_source, "ProgressScreen")
    timer = function_body(app_source, "TimerScreen")
    details = function_body(app_source, "TaskDetailsScreen")

    required_in_bodies = (
        (details, "TaskDetailsScreen", "icon = Icons.Filled.PlayArrow"),
        (timer, "TimerScreen", "icon = Icons.Filled.Done"),
        (timer, "TimerScreen", "icon = if (running) PauseIcon else Icons.Filled.PlayArrow"),
        (timer, "TimerScreen", "icon = Icons.Filled.Refresh"),
        (result, "ResultScreen", "icon = Icons.AutoMirrored.Filled.List"),
        (result, "ResultScreen", "icon = Icons.Filled.Refresh"),
        (progress, "ProgressScreen", "icon = Icons.AutoMirrored.Filled.ArrowForward"),
    )
    for body, name, marker in required_in_bodies:
        if not body:
            failures.append(f"{name} body was not found")
        elif marker not in body:
            failures.append(f"{name} is missing main-flow icon marker: {marker}")

    forbidden_heavy_dependency = "material-icons-extended"
    if forbidden_heavy_dependency in app_source:
        failures.append("main-flow CTA icons must use material-icons-core, not material-icons-extended")

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
    failures = main_flow_action_icon_failures()
    if failures:
        print("Main-flow action-icons check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: main-flow CTA actions use decorative vector icons while keeping text labels")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
