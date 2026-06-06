#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app/src/main/java/ru/poryadok5/app/ui/PoryadokApp.kt"
COMPONENTS = ROOT / "app/src/main/java/ru/poryadok5/app/ui/components/AppComponents.kt"
GRADLE = ROOT / "app/build.gradle.kts"
UI_AUDIT = ROOT / "docs/ui_audit.md"
ACCESSIBILITY_NOTES = ROOT / "docs/accessibility_notes.md"
QA_PLAN = ROOT / "docs/qa_test_plan.md"

FORBIDDEN_GLYPHS: tuple[str, ...] = (
    'icon = "✓"',
    'icon = "⚙"',
    'Text("‹"',
)


def function_body(source: str, name: str) -> str:
    marker = f"fun {name}("
    start = source.find(marker)
    if start < 0:
        marker = f"private fun {name}("
        start = source.find(marker)
    if start < 0:
        return ""
    next_match = re.search(r"\n@Composable\n(?:private\s+)?fun\s+", source[start + len(marker):])
    if next_match is None:
        return source[start:]
    return source[start:start + len(marker) + next_match.start()]


def header_icon_failures(
    app_source: str | None = None,
    components_source: str | None = None,
    gradle_source: str | None = None,
    docs: dict[str, str] | None = None,
    root: Path = ROOT,
) -> list[str]:
    failures: list[str] = []

    if app_source is None:
        if not APP.exists():
            return [f"missing app file: {APP.relative_to(root)}"]
        app_source = APP.read_text(encoding="utf-8")
    if components_source is None:
        if not COMPONENTS.exists():
            return [f"missing components file: {COMPONENTS.relative_to(root)}"]
        components_source = COMPONENTS.read_text(encoding="utf-8")
    if gradle_source is None:
        if not GRADLE.exists():
            return [f"missing Gradle file: {GRADLE.relative_to(root)}"]
        gradle_source = GRADLE.read_text(encoding="utf-8")

    combined = app_source + "\n" + components_source
    for marker in FORBIDDEN_GLYPHS:
        if marker in combined:
            failures.append(f"Header/back controls must use ImageVector icons, not text glyph: {marker}")

    header_action = function_body(app_source, "HeaderAction")
    top_bar = function_body(components_source, "TopBar")

    if "androidx.compose.material:material-icons-core" not in gradle_source:
        failures.append("Compose Material icon vectors dependency is missing")

    for forbidden in (
        "import androidx.compose.material.icons.filled.Check",
        "HeaderAction(label = \"Итоги\", icon = Icons.Filled.Check",
    ):
        if forbidden in app_source:
            failures.append(f"Итоги header must use the stats vector, not the completion check icon: {forbidden}")

    for marker in (
        "import androidx.compose.material.icons.Icons",
        "import androidx.compose.material.icons.filled.Settings",
        "import androidx.compose.ui.graphics.vector.ImageVector",
        "import androidx.compose.ui.graphics.vector.path",
        "private val StatsIcon: ImageVector = ImageVector.Builder(",
        "name = \"StatsBars\"",
        "HeaderAction(label = \"Итоги\", icon = StatsIcon",
        "HeaderAction(label = \"Опции\", icon = Icons.Filled.Settings",
    ):
        if marker not in app_source:
            failures.append(f"PoryadokApp is missing vector icon marker: {marker}")

    if not header_action:
        failures.append("HeaderAction body was not found")
    else:
        for marker in (
            "icon: ImageVector",
            "Icon(",
            "imageVector = icon",
            "contentDescription = null",
            "contentDescription = label",
            "onClick(label)",
        ):
            if marker not in header_action:
                failures.append(f"HeaderAction is missing marker: {marker}")
        if "Text(" in header_action:
            failures.append("HeaderAction should render Icon, not Text")

    if not top_bar:
        failures.append("TopBar body was not found")
    else:
        for marker in (
            "Icons.AutoMirrored.Filled.ArrowBack",
            "Icon(",
            "contentDescription = \"Назад\"",
            "contentDescription = null",
        ):
            if marker not in top_bar:
                failures.append(f"TopBar back action is missing marker: {marker}")

    doc_sources = docs or {}
    for path, markers in (
        (UI_AUDIT, ("StatsIcon", "HeaderAction", "Назад")),
        (ACCESSIBILITY_NOTES, ("StatsIcon", "content descriptions")),
        (QA_PLAN, ("check_header_icon_vectors.py", "StatsIcon")),
    ):
        key = str(path.relative_to(root))
        text = doc_sources.get(key)
        if text is None:
            if not path.exists():
                failures.append(f"missing documentation file: {key}")
                continue
            text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                failures.append(f"{key} is missing marker: {marker}")

    return failures


def main() -> int:
    failures = header_icon_failures()
    if failures:
        print("Header icon vector check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: header and back controls use semantic vector icons")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
