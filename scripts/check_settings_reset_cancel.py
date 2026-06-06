#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app/src/main/java/ru/poryadok5/app/ui/PoryadokApp.kt"
UI_AUDIT = ROOT / "docs/ui_audit.md"
QA_PLAN = ROOT / "docs/qa_test_plan.md"

REQUIRED_APP_MARKERS: tuple[str, ...] = (
    "if (confirmReset) {",
    "Row(horizontalArrangement = Arrangement.spacedBy(10.dp))",
    'text = "Отмена"',
    "confirmReset = false",
    "resetNoticeVisible = false",
    'text = "Сбросить прогресс"',
    "onResetProgress()",
    'text = "Подготовить сброс"',
)

REQUIRED_DOC_MARKERS: tuple[tuple[Path, tuple[str, ...]], ...] = (
    (UI_AUDIT, ("отмен", "Сброс прогресса")),
    (QA_PLAN, ("Отмена", "Сбросить прогресс")),
)


def function_body(source: str, name: str) -> str:
    marker = f"fun {name}("
    start = source.find(marker)
    if start < 0:
        return ""
    next_match = re.search(r"\n@Composable\n(?:private\s+)?fun\s+", source[start + len(marker):])
    if next_match is None:
        return source[start:]
    return source[start:start + len(marker) + next_match.start()]


def settings_reset_cancel_failures(
    app_source: str | None = None,
    doc_sources: dict[Path, str] | None = None,
) -> list[str]:
    failures: list[str] = []

    if app_source is None:
        if not APP.exists():
            return [f"missing app file: {APP.relative_to(ROOT)}"]
        app_source = APP.read_text(encoding="utf-8")

    settings_screen = function_body(app_source, "SettingsScreen")
    if not settings_screen:
        failures.append("SettingsScreen body was not found")
    for marker in REQUIRED_APP_MARKERS:
        if marker not in settings_screen:
            failures.append(f"Settings reset cancel flow is missing marker: {marker}")

    if settings_screen.count('text = "Отмена"') != 1:
        failures.append("Settings reset cancel flow must expose exactly one visible Отмена action")
    cancel_index = settings_screen.find('text = "Отмена"')
    reset_index = settings_screen.find('text = "Сбросить прогресс"')
    if cancel_index > reset_index:
        failures.append("Settings reset cancel flow should show Отмена before the destructive reset action")
    if cancel_index >= 0 and reset_index > cancel_index:
        cancel_block = settings_screen[cancel_index:reset_index]
        if "confirmReset = false" not in cancel_block:
            failures.append("Settings reset cancel action must close the confirmation state")
        if "resetNoticeVisible = false" not in cancel_block:
            failures.append("Settings reset cancel action must not leave reset completion feedback visible")

    doc_sources = doc_sources or {}
    for path, markers in REQUIRED_DOC_MARKERS:
        if path in doc_sources:
            text = doc_sources[path]
        elif path.exists():
            text = path.read_text(encoding="utf-8")
        else:
            failures.append(f"missing documentation file: {path.relative_to(ROOT)}")
            continue
        for marker in markers:
            if marker not in text:
                failures.append(f"{path.relative_to(ROOT)} is missing reset-cancel documentation marker: {marker}")

    return failures


def main() -> int:
    failures = settings_reset_cancel_failures()
    if failures:
        print("Settings reset cancel check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: Settings reset confirmation includes an explicit cancel path")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
