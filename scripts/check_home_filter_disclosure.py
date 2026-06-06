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

HOME_REQUIRED_MARKERS: tuple[str, ...] = (
    "var filtersExpanded by rememberSaveable { mutableStateOf(false) }",
    "HomeFilterDisclosure(",
    "expanded = filtersExpanded",
    "onToggle = { filtersExpanded = !filtersExpanded }",
)

DISCLOSURE_REQUIRED_MARKERS: tuple[str, ...] = (
    "private fun HomeFilterDisclosure(",
    "if (expanded) {",
    "AppCard {",
    "HomeFilterSummaryRow(filter = filter, expanded = true, onToggle = onToggle)",
    "AnimatedVisibility(visible = expanded)",
    'Text("Зона", style = MaterialTheme.typography.titleMedium)',
    'Text("Энергия", style = MaterialTheme.typography.titleMedium)',
    'Text("Время", style = MaterialTheme.typography.titleMedium)',
    "AreaSelector(filter.area, onAreaSelected)",
    "SupportedTaskMinutes.forEach",
    "} else {",
    "HorizontalDivider(color = MaterialTheme.colorScheme.surfaceVariant)",
    "expanded = false",
    ".padding(vertical = 6.dp)",
)

SUMMARY_ROW_REQUIRED_MARKERS: tuple[str, ...] = (
    "private fun HomeFilterSummaryRow(",
    'Text("Настроить подбор", style = MaterialTheme.typography.titleMedium)',
    ".defaultMinSize(minHeight = 56.dp)",
    ".clickable(",
    "role = Role.Button",
    "onClick = onToggle",
    'stateDescription = if (expanded) "Подбор раскрыт" else "Подбор скрыт"',
    "FilterDisclosureIndicator(expanded = expanded)",
)

INDICATOR_REQUIRED_MARKERS: tuple[str, ...] = (
    "private fun FilterDisclosureIndicator(",
    "modifier = Modifier\n            .defaultMinSize(minHeight = 48.dp)",
    'text = if (expanded) "Скрыть" else "Изменить"',
    "imageVector = if (expanded) ChevronUpIcon else ChevronDownIcon",
    "contentDescription = null",
)

DOC_REQUIRED_MARKERS: tuple[tuple[Path, tuple[str, ...]], ...] = (
    (PRODUCT_SPEC, ("компактный текущий подбор", "раскрывает зону/энергию/время", "лёгкой строкой")),
    (UI_AUDIT, ("Home filter disclosure", "компактный summary", "56dp", "whole-row", "шеврон", "unframed")),
    (QA_PLAN, ("check_home_filter_disclosure.py", "Home filter disclosure")),
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


def home_filter_disclosure_failures(
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
    home = function_body(app_source, "HomeScreen")
    disclosure = function_body(app_source, "HomeFilterDisclosure")
    summary_row = function_body(app_source, "HomeFilterSummaryRow")
    indicator = function_body(app_source, "FilterDisclosureIndicator")
    if not home:
        failures.append("HomeScreen body was not found")
    else:
        for marker in HOME_REQUIRED_MARKERS:
            if marker not in home:
                failures.append(f"Home filter disclosure is missing marker: {marker}")

        if "TextButton(" in home:
            failures.append("Home filter disclosure summary should be a whole-row toggle, not a small TextButton")

    if not disclosure:
        failures.append("HomeFilterDisclosure body was not found")
    else:
        for marker in DISCLOSURE_REQUIRED_MARKERS:
            if marker not in disclosure:
                failures.append(f"Home filter disclosure is missing marker: {marker}")

        if "TextButton(" in disclosure:
            failures.append("Home filter disclosure summary should be a whole-row toggle, not a small TextButton")

        expanded_index = disclosure.find("if (expanded) {")
        collapsed_index = disclosure.find("} else {", expanded_index)
        if expanded_index < 0 or collapsed_index < 0:
            failures.append("Home filter disclosure must keep separate expanded and collapsed branches")
        else:
            expanded_section = disclosure[expanded_index:collapsed_index]
            collapsed_section = disclosure[collapsed_index:]
            if "AppCard {" not in expanded_section:
                failures.append("Expanded Home filter controls should stay in AppCard")
            if "AppCard {" in collapsed_section:
                failures.append("Collapsed Home filter summary should be unframed, not AppCard")

        disclosure_index = disclosure.find("AnimatedVisibility(visible = expanded)")
        if disclosure_index < 0:
            failures.append("Home filter controls must be wrapped in AnimatedVisibility")
        else:
            for marker in (
                'Text("Зона", style = MaterialTheme.typography.titleMedium)',
                'Text("Энергия", style = MaterialTheme.typography.titleMedium)',
                'Text("Время", style = MaterialTheme.typography.titleMedium)',
            ):
                marker_index = disclosure.find(marker)
                if marker_index >= 0 and marker_index < disclosure_index:
                    failures.append(f"Home filter control appears before disclosure: {marker}")

    if not summary_row:
        failures.append("HomeFilterSummaryRow body was not found")
    else:
        if "TextButton(" in summary_row:
            failures.append("Home filter disclosure summary should be a whole-row toggle, not a small TextButton")
        for marker in SUMMARY_ROW_REQUIRED_MARKERS:
            if marker not in summary_row:
                failures.append(f"Home filter summary row is missing marker: {marker}")

    if not indicator:
        failures.append("FilterDisclosureIndicator body was not found")
    else:
        for marker in INDICATOR_REQUIRED_MARKERS:
            if marker not in indicator:
                failures.append(f"Home filter disclosure indicator is missing marker: {marker}")

    for marker in ("private val ChevronDownIcon", "private val ChevronUpIcon"):
        if marker not in app_source:
            failures.append(f"Home filter disclosure is missing icon vector: {marker}")

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
    failures = home_filter_disclosure_failures()
    if failures:
        print("Home filter disclosure check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: Home filter tuning stays behind an explicit disclosure")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
