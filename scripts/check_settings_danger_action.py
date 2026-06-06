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


def settings_danger_action_failures(
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

    danger_action = function_body(components_source, "DangerAction")
    settings_screen = function_body(app_source, "SettingsScreen")

    if not danger_action:
        failures.append("DangerAction component is missing")
    else:
        for marker in (
            "OutlinedButton(",
            ".defaultMinSize(minHeight = 52.dp)",
            "BorderStroke(1.dp, MaterialTheme.colorScheme.error)",
            "ButtonDefaults.outlinedButtonColors(",
            "contentColor = MaterialTheme.colorScheme.error",
        ):
            if marker not in danger_action:
                failures.append(f"DangerAction is missing marker: {marker}")

    if not settings_screen:
        failures.append("SettingsScreen body was not found")
    else:
        reset_index = settings_screen.find('text = "Сбросить прогресс"')
        if reset_index < 0:
            failures.append("Settings reset confirmation is missing Сбросить прогресс")
        else:
            danger_index = settings_screen.rfind("DangerAction(", 0, reset_index)
            secondary_index = settings_screen.rfind("SecondaryAction(", 0, reset_index)
            if danger_index < 0:
                failures.append("Settings destructive reset must use DangerAction")
            if secondary_index > danger_index:
                failures.append("Settings destructive reset must not use the neutral SecondaryAction")
        if "import ru.poryadok5.app.ui.components.DangerAction" not in app_source:
            failures.append("PoryadokApp must import DangerAction explicitly")

    docs = docs or {}
    for path, markers in (
        (UI_AUDIT, ("DangerAction", "Сброс прогресса", "error")),
        (ACCESSIBILITY_NOTES, ("DangerAction", "52dp", "Сбросить прогресс")),
        (QA_PLAN, ("check_settings_danger_action.py", "DangerAction")),
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
    failures = settings_danger_action_failures()
    if failures:
        print("Settings danger-action check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: Settings destructive reset uses the guarded danger action")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
