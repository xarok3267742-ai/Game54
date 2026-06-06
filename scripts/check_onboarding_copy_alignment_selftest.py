#!/usr/bin/env python3
from __future__ import annotations

from check_onboarding_copy_alignment import onboarding_copy_failures

VALID_APP = """
@Composable
private fun OnboardingScreen() {
    OnboardingFlowSummary()
}

@Composable
private fun OnboardingFlowSummary() {
    Text("Первые 5 минут", style = MaterialTheme.typography.titleMedium)
    OnboardingFlowFact("Сначала", "Выбираете стартовую зону.")
    OnboardingFlowFact("Затем", "Получаете задачу и при желании уточняете подбор.")
    OnboardingFlowFact("После", "Запускаете таймер и отмечаете результат.")
}

@Composable
private fun OnboardingFlowFact(label: String, text: String) {
    Row(modifier = Modifier.defaultMinSize(minHeight = 48.dp)) {
        Text(label)
        Text(text)
    }
}

@Composable
private fun HomeScreen() {
    HomeFilterDisclosure()
}

@Composable
private fun HomeFilterDisclosure() {
    Text("Энергия", style = MaterialTheme.typography.titleMedium)
    Text("Время", style = MaterialTheme.typography.titleMedium)
}

@Composable
private fun HomeFilterSummaryRow() {
    Text("Настроить подбор", style = MaterialTheme.typography.titleMedium)
}
"""

VALID_DOCS = {
    "docs/product_spec.md": "Пользователь выбирает стартовую зону, а энергию и время уточняет на Home.",
    "docs/ui_audit.md": "Onboarding copy и Onboarding flow summary говорят про стартовую зону; энергию и время пользователь уточняет позже.",
    "docs/qa_test_plan.md": "check_onboarding_copy_alignment.py проверяет onboarding copy и блок Первые 5 минут.",
}


def failures_for(app: str = VALID_APP, docs: dict[str, str] = VALID_DOCS) -> list[str]:
    return onboarding_copy_failures(app_source=app, docs=docs)


def assert_passes(failures: list[str]) -> None:
    assert failures == [], failures


def assert_fails(failures: list[str], expected: str) -> None:
    assert any(expected in failure for failure in failures), failures


def test_valid_fixture_passes() -> None:
    assert_passes(failures_for())


def test_old_energy_promise_fails() -> None:
    broken = VALID_APP.replace("Выбираете стартовую зону.", "Выбираете зону и уровень энергии.")
    assert_fails(failures_for(app=broken), "energy selection")


def test_old_step_rows_on_onboarding_fail() -> None:
    broken = VALID_APP.replace(
        "OnboardingFlowSummary()",
        'StepRow(1, "Выбираете стартовую зону.")',
    )
    assert_fails(failures_for(app=broken), "unframed")


def test_missing_flow_heading_fails() -> None:
    broken = VALID_APP.replace('Text("Первые 5 минут", style = MaterialTheme.typography.titleMedium)', "")
    assert_fails(failures_for(app=broken), "Onboarding flow summary")


def test_missing_flow_fact_min_height_fails() -> None:
    broken = VALID_APP.replace("modifier = Modifier.defaultMinSize(minHeight = 48.dp)", "modifier = Modifier")
    assert_fails(failures_for(app=broken), "Onboarding flow summary")


def test_missing_home_energy_filter_fails() -> None:
    broken = VALID_APP.replace('Text("Энергия", style = MaterialTheme.typography.titleMedium)', "")
    assert_fails(failures_for(app=broken), "Home filter controls")


def test_missing_home_time_filter_fails() -> None:
    broken = VALID_APP.replace('Text("Время", style = MaterialTheme.typography.titleMedium)', "")
    assert_fails(failures_for(app=broken), "Home filter controls")


def test_missing_docs_fails() -> None:
    docs = dict(VALID_DOCS)
    docs["docs/ui_audit.md"] = "Onboarding copy."
    assert_fails(failures_for(docs=docs), "docs/ui_audit.md")


def test_missing_product_spec_marker_fails() -> None:
    docs = dict(VALID_DOCS)
    docs["docs/product_spec.md"] = "Пользователь выбирает стартовую зону."
    assert_fails(failures_for(docs=docs), "docs/product_spec.md")


def test_missing_qa_plan_marker_fails() -> None:
    docs = dict(VALID_DOCS)
    docs["docs/qa_test_plan.md"] = "onboarding copy."
    assert_fails(failures_for(docs=docs), "docs/qa_test_plan.md")


def main() -> int:
    test_valid_fixture_passes()
    test_old_energy_promise_fails()
    test_old_step_rows_on_onboarding_fail()
    test_missing_flow_heading_fails()
    test_missing_flow_fact_min_height_fails()
    test_missing_home_energy_filter_fails()
    test_missing_home_time_filter_fails()
    test_missing_docs_fails()
    test_missing_product_spec_marker_fails()
    test_missing_qa_plan_marker_fails()
    print("PASS: onboarding copy alignment checker self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
