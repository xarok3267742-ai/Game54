#!/usr/bin/env python3
from __future__ import annotations

from check_progress_continue_action import progress_continue_failures

VALID_APP = """
fun PoryadokApp() {
    ProgressScreen(
        onBack = { screen = AppScreen.Home },
        onHome = { screen = AppScreen.Home },
        onSettings = { screen = AppScreen.Settings },
    )
}

private fun ProgressScreen(
    onBack: () -> Unit,
    onHome: () -> Unit,
    onSettings: () -> Unit,
) {
    PrimaryAction(
        text = "Продолжить с задачей",
        onClick = onHome,
        icon = Icons.AutoMirrored.Filled.ArrowForward,
    )
}
"""

VALID_DOCS = {
    "docs/ui_audit.md": "Итоги содержат действие Продолжить с задачей.",
    "docs/qa_test_plan.md": "На экране Итоги нажать Продолжить с задачей.",
}


def assert_passes(failures: list[str]) -> None:
    assert failures == [], failures


def assert_fails(failures: list[str], expected: str) -> None:
    assert any(expected in failure for failure in failures), failures


def test_valid_fixture_passes() -> None:
    assert_passes(progress_continue_failures(app_source=VALID_APP, docs=VALID_DOCS))


def test_missing_route_to_home_fails() -> None:
    broken = VALID_APP.replace("        onHome = { screen = AppScreen.Home },\n", "")
    assert_fails(
        progress_continue_failures(app_source=broken, docs=VALID_DOCS),
        "onHome = { screen = AppScreen.Home }",
    )


def test_missing_callback_parameter_fails() -> None:
    broken = VALID_APP.replace("    onHome: () -> Unit,\n", "")
    assert_fails(progress_continue_failures(app_source=broken, docs=VALID_DOCS), "onHome: () -> Unit")


def test_missing_primary_action_fails() -> None:
    broken = VALID_APP.replace('        text = "Продолжить с задачей",\n', "")
    assert_fails(
        progress_continue_failures(app_source=broken, docs=VALID_DOCS),
        'text = "Продолжить с задачей"',
    )


def test_unsafe_callback_fails() -> None:
    broken = VALID_APP.replace(
        "onClick = onHome",
        "onClick = onSettings",
    )
    assert_fails(progress_continue_failures(app_source=broken, docs=VALID_DOCS), "unsafe callback")


def test_missing_icon_fails() -> None:
    broken = VALID_APP.replace("        icon = Icons.AutoMirrored.Filled.ArrowForward,\n", "")
    assert_fails(progress_continue_failures(app_source=broken, docs=VALID_DOCS), "ArrowForward")


def test_missing_docs_fails() -> None:
    broken_docs = dict(VALID_DOCS)
    broken_docs["docs/qa_test_plan.md"] = "На экране Итоги проверить метрики."
    assert_fails(progress_continue_failures(app_source=VALID_APP, docs=broken_docs), "docs/qa_test_plan.md")


def main() -> int:
    test_valid_fixture_passes()
    test_missing_route_to_home_fails()
    test_missing_callback_parameter_fails()
    test_missing_primary_action_fails()
    test_unsafe_callback_fails()
    test_missing_icon_fails()
    test_missing_docs_fails()
    print("PASS: Progress continue-action checker self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
