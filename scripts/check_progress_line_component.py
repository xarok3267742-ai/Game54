#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPONENTS = ROOT / "app/src/main/java/ru/poryadok5/app/ui/components/AppComponents.kt"
APP = ROOT / "app/src/main/java/ru/poryadok5/app/ui/PoryadokApp.kt"
UI_AUDIT = ROOT / "docs/ui_audit.md"
ACCESSIBILITY_NOTES = ROOT / "docs/accessibility_notes.md"
QA_PLAN = ROOT / "docs/qa_test_plan.md"


def function_body(source: str, name: str) -> str:
    marker = f"fun {name}("
    start = source.find(marker)
    if start < 0:
        return ""
    next_match = re.search(r"\n@Composable\n(?:private\s+)?fun\s+", source[start + len(marker):])
    if next_match is None:
        return source[start:]
    return source[start:start + len(marker) + next_match.start()]


def progress_line_failures(
    components_source: str | None = None,
    app_source: str | None = None,
    docs: dict[Path, str] | None = None,
) -> list[str]:
    failures: list[str] = []

    if components_source is None:
        if not COMPONENTS.exists():
            return [f"missing components file: {COMPONENTS.relative_to(ROOT)}"]
        components_source = COMPONENTS.read_text(encoding="utf-8")
    if app_source is None:
        if not APP.exists():
            return [f"missing app file: {APP.relative_to(ROOT)}"]
        app_source = APP.read_text(encoding="utf-8")

    progress_line = function_body(components_source, "ProgressLine")
    timer_screen = function_body(app_source, "TimerScreen")
    progress_screen = function_body(app_source, "ProgressScreen")
    area_progress_row = function_body(app_source, "AreaProgressRow")

    if "LinearProgressIndicator" in app_source + components_source:
        failures.append("Use ProgressLine instead of Material LinearProgressIndicator to avoid false end-dot progress markers")

    if not progress_line:
        failures.append("ProgressLine component is missing")
    else:
        for marker in (
            "val normalized = progress.coerceIn(0f, 1f)",
            ".clip(MaterialTheme.shapes.extraSmall)",
            "ProgressBarRangeInfo(normalized, 0f..1f)",
            "if (normalized > 0f)",
            ".fillMaxWidth(normalized)",
        ):
            if marker not in progress_line:
                failures.append(f"ProgressLine is missing marker: {marker}")

    for name, body, marker in (
        ("TimerScreen", timer_screen, "trackColor = MaterialTheme.colorScheme.surface"),
        ("ProgressScreen", progress_screen, "ProgressLine(progress = catalogPercent / 100f)"),
        ("AreaProgressRow", area_progress_row, "ProgressLine(progress = progress, height = 6.dp)"),
    ):
        if not body:
            failures.append(f"{name} body was not found")
        elif "ProgressLine(" not in body:
            failures.append(f"{name} must use ProgressLine")
        elif marker not in body:
            failures.append(f"{name} ProgressLine usage is missing marker: {marker}")

    if "import ru.poryadok5.app.ui.components.ProgressLine" not in app_source:
        failures.append("PoryadokApp must import ProgressLine explicitly")

    docs = docs or {}
    for path, markers in (
        (UI_AUDIT, ("ProgressLine", "нулев", "end-dot")),
        (ACCESSIBILITY_NOTES, ("ProgressLine", "ProgressBarRangeInfo")),
        (QA_PLAN, ("check_progress_line_component.py", "ProgressLine")),
    ):
        if path in docs:
            text = docs[path]
        elif path.exists():
            text = path.read_text(encoding="utf-8")
        else:
            failures.append(f"missing documentation file: {path.relative_to(ROOT)}")
            continue
        for marker in markers:
            if marker not in text:
                failures.append(f"{path.relative_to(ROOT)} is missing marker: {marker}")

    return failures


def main() -> int:
    failures = progress_line_failures()
    if failures:
        print("ProgressLine check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: progress bars use ProgressLine without false end-dot markers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
