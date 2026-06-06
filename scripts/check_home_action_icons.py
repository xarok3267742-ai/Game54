#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app/src/main/java/ru/poryadok5/app/ui/PoryadokApp.kt"
COMPONENTS = ROOT / "app/src/main/java/ru/poryadok5/app/ui/components/AppComponents.kt"
PRODUCT_SPEC = ROOT / "docs/product_spec.md"
UI_AUDIT = ROOT / "docs/ui_audit.md"
ACCESSIBILITY = ROOT / "docs/accessibility_notes.md"
QA_PLAN = ROOT / "docs/qa_test_plan.md"

APP_REQUIRED_MARKERS: tuple[str, ...] = (
    "import androidx.compose.material.icons.automirrored.filled.List",
    "import androidx.compose.material.icons.filled.PlayArrow",
    "import androidx.compose.material.icons.filled.Refresh",
    "icon = Icons.Filled.PlayArrow",
    "icon = Icons.Filled.Refresh",
    "icon = Icons.AutoMirrored.Filled.List",
)

COMPONENT_REQUIRED_MARKERS: tuple[str, ...] = (
    "icon: ImageVector? = null",
    "Icon(",
    "contentDescription = null",
    "Modifier.size(20.dp)",
    "Spacer(Modifier.width(8.dp))",
)

DOC_REQUIRED_MARKERS: tuple[tuple[Path, tuple[str, ...]], ...] = (
    (PRODUCT_SPEC, ("Home", "decorative action icons", "Запустить таймер")),
    (UI_AUDIT, ("Home action icons", "PlayArrow", "Refresh", "List")),
    (ACCESSIBILITY, ("Home action icons", "decorative", "text labels")),
    (QA_PLAN, ("check_home_action_icons.py", "Home action icons")),
)


def function_body(source: str, name: str) -> str:
    marker = f"fun {name}("
    start = source.find(marker)
    if start < 0:
        marker = f"private fun {name}("
        start = source.find(marker)
    if start < 0:
        return ""
    next_match = re.search(r"\n@Composable\n(?:private\s+)?fun\s+", source[start + len(marker) :])
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


def home_action_icon_failures(
    app_source: str | None = None,
    components_source: str | None = None,
    docs: dict[str, str] | None = None,
    app_path: Path = APP,
    components_path: Path = COMPONENTS,
    root: Path = ROOT,
) -> list[str]:
    if app_source is None:
        if not app_path.exists():
            return [f"missing app file: {app_path.relative_to(root)}"]
        app_source = app_path.read_text(encoding="utf-8")
    if components_source is None:
        if not components_path.exists():
            return [f"missing components file: {components_path.relative_to(root)}"]
        components_source = components_path.read_text(encoding="utf-8")

    failures: list[str] = []
    home = function_body(app_source, "HomeScreen")
    primary = function_body(components_source, "PrimaryAction")
    secondary = function_body(components_source, "SecondaryAction")

    if not home:
        failures.append("HomeScreen body was not found")
    else:
        for marker in APP_REQUIRED_MARKERS:
            if marker not in app_source:
                failures.append(f"Home action icons are missing marker: {marker}")
        for text in ("Запустить таймер", "Другая задача", "Все шаги"):
            if text not in home:
                failures.append(f"Home action text label disappeared: {text}")

    for name, body in (("PrimaryAction", primary), ("SecondaryAction", secondary)):
        if not body:
            failures.append(f"{name} body was not found")
            continue
        for marker in COMPONENT_REQUIRED_MARKERS:
            if marker not in body:
                failures.append(f"{name} icon support is missing marker: {marker}")
        if 'contentDescription = ""' in body or "contentDescription = text" in body:
            failures.append(f"{name} icons must remain decorative because the button text is the accessible label")

    if "material-icons-extended" in app_source or "material-icons-extended" in components_source:
        failures.append("Home action icons must use the existing material-icons-core dependency, not material-icons-extended")

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
    failures = home_action_icon_failures()
    if failures:
        print("Home action-icons check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: Home primary and secondary actions keep text labels with decorative vector icons")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
