#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPONENTS = ROOT / "app/src/main/java/ru/poryadok5/app/ui/components/AppComponents.kt"
APP = ROOT / "app/src/main/java/ru/poryadok5/app/ui/PoryadokApp.kt"
ACCESSIBILITY_NOTES = ROOT / "docs/accessibility_notes.md"
UI_AUDIT = ROOT / "docs/ui_audit.md"


def fail(message: str) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def function_body(source: str, name: str) -> str:
    marker = f"fun {name}("
    start = source.find(marker)
    if start < 0:
        return ""
    next_match = re.search(r"\n@Composable\n(?:private\s+)?fun\s+", source[start + len(marker):])
    if next_match is None:
        return source[start:]
    return source[start:start + len(marker) + next_match.start()]


def main() -> int:
    failures: list[str] = []

    if not COMPONENTS.exists():
        return fail(f"missing component file: {display_path(COMPONENTS)}")
    if not APP.exists():
        return fail(f"missing app UI file: {display_path(APP)}")

    components_source = COMPONENTS.read_text(encoding="utf-8")
    app_source = APP.read_text(encoding="utf-8")
    choice_chip = function_body(components_source, "ChoiceChip")
    top_bar = function_body(components_source, "TopBar")
    primary_action = function_body(components_source, "PrimaryAction")
    secondary_action = function_body(components_source, "SecondaryAction")
    header_action = function_body(app_source, "HeaderAction")
    settings_screen = function_body(app_source, "SettingsScreen")
    timer_screen = function_body(app_source, "TimerScreen")

    if ".defaultMinSize(minHeight = 52.dp)" not in primary_action:
        failures.append("PrimaryAction must keep a minimum 52dp tap target")
    if "contentColor = MaterialTheme.colorScheme.onPrimary" not in primary_action:
        failures.append("PrimaryAction must set Material button content color to onPrimary for sage buttons")
    if not re.search(r"Text\(\s*text\s*,\s*color\s*=\s*MaterialTheme\.colorScheme\.onPrimary", primary_action):
        failures.append("PrimaryAction must explicitly render label text in onPrimary for contrast on sage buttons")
    if ".defaultMinSize(minHeight = 52.dp)" not in secondary_action:
        failures.append("SecondaryAction must keep a minimum 52dp tap target")
    if "enabled: Boolean = true" not in secondary_action or "enabled = enabled" not in secondary_action:
        failures.append("SecondaryAction must expose enabled state for disabled timer controls")
    if ".defaultMinSize(minHeight = 48.dp)" not in choice_chip:
        failures.append("ChoiceChip must keep a minimum 48dp tap target")
    if ".clickable(role = Role.Button" not in choice_chip:
        failures.append("ChoiceChip must expose button role semantics")
    if "this.selected = selected" not in choice_chip:
        failures.append("ChoiceChip must expose selected state semantics")
    if 'stateDescription = if (selected) "Выбрано" else "Не выбрано"' not in choice_chip:
        failures.append("ChoiceChip must expose Russian selected/unselected state descriptions")
    if ".size(48.dp)" not in top_bar:
        failures.append("TopBar back action must keep a 48dp square tap target")
    if 'contentDescription = "Назад"' not in top_bar:
        failures.append("TopBar back action must expose a Russian content description")
    if ".clickable(role = Role.Button" not in top_bar:
        failures.append("TopBar back action must expose button role semantics")
    if ".defaultMinSize(minWidth = 48.dp, minHeight = 48.dp)" not in header_action:
        failures.append("HeaderAction must keep a minimum 48dp tap target")
    if ".clickable(role = Role.Button" not in header_action or "onClick = onAction" not in header_action:
        failures.append("HeaderAction must remain an explicit clickable top action with button role")
    if ".clearAndSetSemantics" not in header_action or "contentDescription = label" not in header_action:
        failures.append("HeaderAction must expose its Russian label as a content description")
    if "onClick(label)" not in header_action:
        failures.append("HeaderAction must expose an accessible click action label")
    if ".toggleable(" not in settings_screen or "role = Role.Switch" not in settings_screen:
        failures.append("Settings haptics row must expose a full-row switch toggle target")
    if ".defaultMinSize(minHeight = 56.dp)" not in settings_screen:
        failures.append("Settings haptics row must keep at least a 56dp toggle target")
    if "onValueChange = onHaptics" not in settings_screen:
        failures.append("Settings haptics row must route full-row toggle changes through onHaptics")
    if "onCheckedChange = null" not in settings_screen:
        failures.append("Settings haptics Switch must be display-only so the row owns toggle semantics")
    if "val timerExpired = remainingSeconds == 0" not in timer_screen:
        failures.append("TimerScreen must derive an explicit expired state from remainingSeconds")
    if 'timerExpired -> "Время вышло"' not in timer_screen:
        failures.append("TimerScreen pause/resume control must show a clear expired label at zero")
    if "enabled = !timerExpired" not in timer_screen:
        failures.append("TimerScreen pause/resume control must be disabled after time expires")

    combined_source = components_source + "\n" + app_source
    if re.search(r"(?:defaultMinSize\(minHeight =|size\()44\.dp", combined_source):
        failures.append("44dp interactive targets are not allowed in shared components")

    for doc in (ACCESSIBILITY_NOTES, UI_AUDIT):
        if not doc.exists():
            failures.append(f"missing accessibility doc: {display_path(doc)}")
            continue
        text = doc.read_text(encoding="utf-8")
        if "48dp" not in text:
            failures.append(f"{display_path(doc)} must document 48dp minimum tap targets")

    if failures:
        print("Accessibility target check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: accessibility tap targets and back-action semantics match RC requirements")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
