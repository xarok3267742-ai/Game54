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

SETTINGS_REQUIRED_MARKERS: tuple[str, ...] = (
    'Text("О приложении", style = MaterialTheme.typography.titleLarge)',
    'Text("Порядок 5", style = MaterialTheme.typography.titleMedium)',
    "SettingsAboutSummary(catalogSize = catalogSize)",
    "Spacer(modifier = Modifier.height(32.dp))",
)

SUMMARY_REQUIRED_MARKERS: tuple[str, ...] = (
    "private fun SettingsAboutSummary(catalogSize: Int)",
    "Row(horizontalArrangement = Arrangement.spacedBy(8.dp))",
    'label = "Версия"',
    "value = BuildConfig.VERSION_NAME",
    "Modifier.weight(0.85f)",
    'label = "Каталог"',
    'value = "$catalogSize задач"',
    'label = "Данные"',
    'value = "на устройстве"',
    "Modifier.weight(1.35f)",
)

FACT_REQUIRED_MARKERS: tuple[str, ...] = (
    "private fun SettingsAboutFact(",
    ".defaultMinSize(minHeight = 56.dp)",
    ".padding(horizontal = 4.dp, vertical = 6.dp)",
    "MaterialTheme.typography.bodyMedium",
    "MaterialTheme.typography.labelLarge",
    "color = MutedText",
    "color = Sage",
)

DOC_REQUIRED_MARKERS: tuple[tuple[Path, tuple[str, ...]], ...] = (
    (PRODUCT_SPEC, ("Settings", "compact about summary", "Версия", "Каталог", "Данные")),
    (UI_AUDIT, ("Settings about summary", "Версия", "Каталог", "Данные")),
    (QA_PLAN, ("check_settings_about_summary.py", "Settings about summary")),
)

FORBIDDEN_SETTINGS_MARKERS: tuple[str, ...] = (
    "Локальный каталог из $catalogSize микрозадач",
    "для дома, рабочего места, кухни, личных вещей и цифрового порядка",
    "Порядок 5 ${BuildConfig.VERSION_NAME}",
)


def function_body(source: str, name: str) -> str:
    marker = f"private fun {name}("
    start = source.find(marker)
    if start < 0:
        marker = f"fun {name}("
        start = source.find(marker)
    if start < 0:
        return ""
    next_match = re.search(r"\n@Composable\n(?:private\s+)?fun\s+", source[start + len(marker):])
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


def settings_about_summary_failures(
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
    settings = function_body(app_source, "SettingsScreen")
    summary = function_body(app_source, "SettingsAboutSummary")
    fact = function_body(app_source, "SettingsAboutFact")

    if not settings:
        failures.append("SettingsScreen body was not found")
    else:
        for marker in SETTINGS_REQUIRED_MARKERS:
            if marker not in settings:
                failures.append(f"Settings about summary is missing marker: {marker}")
        for marker in FORBIDDEN_SETTINGS_MARKERS:
            if marker in settings:
                failures.append(f"Settings about summary must not return to the long paragraph: {marker}")

    if not summary:
        failures.append("SettingsAboutSummary body was not found")
    else:
        for marker in SUMMARY_REQUIRED_MARKERS:
            if marker not in summary:
                failures.append(f"SettingsAboutSummary is missing marker: {marker}")

    if not fact:
        failures.append("SettingsAboutFact body was not found")
    else:
        for marker in FACT_REQUIRED_MARKERS:
            if marker not in fact:
                failures.append(f"SettingsAboutFact is missing marker: {marker}")
        for marker in ("Surface(", "AppCard(", "BorderStroke(", ".clickable(", "Role.Button", "onClick"):
            if marker in fact:
                failures.append(f"SettingsAboutFact must stay compact, unframed and non-interactive: {marker}")

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
    failures = settings_about_summary_failures()
    if failures:
        print("Settings about-summary check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: Settings about summary is compact and scannable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
