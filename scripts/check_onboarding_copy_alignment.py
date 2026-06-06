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

FORBIDDEN_COPY = "Выбираете зону и уровень энергии."
ONBOARDING_REQUIRED_MARKERS: tuple[str, ...] = (
    "OnboardingFlowSummary()",
)
ONBOARDING_FLOW_REQUIRED_MARKERS: tuple[str, ...] = (
    'Text("Первые 5 минут", style = MaterialTheme.typography.titleMedium)',
    'OnboardingFlowFact("Сначала", "Выбираете стартовую зону.")',
    'OnboardingFlowFact("Затем", "Получаете задачу и при желании уточняете подбор.")',
    'OnboardingFlowFact("После", "Запускаете таймер и отмечаете результат.")',
    "modifier = Modifier.defaultMinSize(minHeight = 48.dp)",
)
ONBOARDING_FORBIDDEN_MARKERS: tuple[str, ...] = (
    'Text("Как это работает", style = MaterialTheme.typography.titleMedium)',
    "StepRow(",
)
HOME_REQUIRED_MARKERS: tuple[str, ...] = (
    "HomeFilterDisclosure(",
    'Text("Настроить подбор", style = MaterialTheme.typography.titleMedium)',
    'Text("Энергия", style = MaterialTheme.typography.titleMedium)',
    'Text("Время", style = MaterialTheme.typography.titleMedium)',
)
DOC_REQUIRED_MARKERS: tuple[tuple[Path, tuple[str, ...]], ...] = (
    (PRODUCT_SPEC, ("выбирает стартовую зону", "энергию и время уточняет на Home")),
    (UI_AUDIT, ("Onboarding copy", "Onboarding flow summary", "стартовую зону", "энергию и время")),
    (QA_PLAN, ("check_onboarding_copy_alignment.py", "onboarding copy", "Первые 5 минут")),
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


def onboarding_copy_failures(
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
    onboarding = function_body(app_source, "OnboardingScreen")
    onboarding_flow = function_body(app_source, "OnboardingFlowSummary")
    onboarding_fact = function_body(app_source, "OnboardingFlowFact")
    home = function_body(app_source, "HomeScreen")
    home_filter = function_body(app_source, "HomeFilterDisclosure")
    home_filter_summary = function_body(app_source, "HomeFilterSummaryRow")

    if FORBIDDEN_COPY in app_source:
        failures.append("Onboarding must not promise energy selection before that control is visible")

    if not onboarding:
        failures.append("OnboardingScreen body was not found")
    else:
        for marker in ONBOARDING_REQUIRED_MARKERS:
            if marker not in onboarding:
                failures.append(f"Onboarding copy is missing marker: {marker}")
        for marker in ONBOARDING_FORBIDDEN_MARKERS:
            if marker in onboarding:
                failures.append(f"Onboarding must keep the first-run flow summary unframed, not {marker}")

    if not onboarding_flow:
        failures.append("OnboardingFlowSummary body was not found")
    else:
        for marker in ONBOARDING_FLOW_REQUIRED_MARKERS:
            if marker not in onboarding_flow and marker not in onboarding_fact:
                failures.append(f"Onboarding flow summary is missing marker: {marker}")

    if not home:
        failures.append("HomeScreen body was not found")
    else:
        if "HomeFilterDisclosure(" not in home:
            failures.append("Home filter controls are missing marker: HomeFilterDisclosure(")

    for marker in HOME_REQUIRED_MARKERS[1:]:
        if marker == 'Text("Настроить подбор", style = MaterialTheme.typography.titleMedium)':
            source_section = home_filter_summary
            section_name = "HomeFilterSummaryRow"
        else:
            source_section = home_filter
            section_name = "HomeFilterDisclosure"
        if not source_section:
            failures.append(f"{section_name} body was not found")
        elif marker not in source_section:
            failures.append(f"Home filter controls are missing marker: {marker}")

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
    failures = onboarding_copy_failures()
    if failures:
        print("Onboarding copy alignment check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: onboarding copy matches the first-run controls and Home filter flow")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
