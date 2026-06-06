#!/usr/bin/env python3
from __future__ import annotations

from check_result_action_layout import result_action_layout_failures

VALID_APP = """
private fun ResultScreen(
    onHome: () -> Unit,
    onProgress: () -> Unit,
) {
    PrimaryAction("Запустить следующую", onNext)
    SecondaryAction("Посмотреть шаги", onOpenNext)
    Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
        SecondaryAction(
            text = "На главный экран",
            onClick = onHome,
            icon = HomeIcon,
            modifier = Modifier.weight(1f),
        )
        SecondaryAction(
            text = "Посмотреть итоги",
            onClick = onProgress,
            icon = StatsIcon,
            modifier = Modifier.weight(1f),
        )
    }
}
"""

VALID_DOCS = {
    "docs/ui_audit.md": "Экран результата ставит На главный экран и Посмотреть итоги в одну строку with HomeIcon and StatsIcon.",
    "docs/qa_test_plan.md": "Result action layout проверяет На главный экран и Посмотреть итоги with HomeIcon and StatsIcon.",
}


def assert_passes(failures: list[str]) -> None:
    assert failures == [], failures


def assert_fails(failures: list[str], expected: str) -> None:
    assert any(expected in failure for failure in failures), failures


def test_valid_fixture_passes() -> None:
    assert_passes(result_action_layout_failures(app_source=VALID_APP, docs=VALID_DOCS))


def test_missing_home_weight_fails() -> None:
    broken = VALID_APP.replace("            modifier = Modifier.weight(1f),\n", "", 1)
    assert_fails(result_action_layout_failures(app_source=broken, docs=VALID_DOCS), "Modifier.weight")


def test_stacked_home_action_fails() -> None:
    broken = VALID_APP.replace(
        """SecondaryAction(
            text = "На главный экран",
            onClick = onHome,
            icon = HomeIcon,
            modifier = Modifier.weight(1f),
        )""",
        'SecondaryAction("На главный экран", onHome)',
    )
    assert_fails(result_action_layout_failures(app_source=broken, docs=VALID_DOCS), "stacked full-width")


def test_missing_home_icon_fails() -> None:
    broken = VALID_APP.replace("            icon = HomeIcon,\n", "")
    assert_fails(result_action_layout_failures(app_source=broken, docs=VALID_DOCS), "HomeIcon")


def test_missing_progress_icon_fails() -> None:
    broken = VALID_APP.replace("            icon = StatsIcon,\n", "")
    assert_fails(result_action_layout_failures(app_source=broken, docs=VALID_DOCS), "StatsIcon")


def test_stacked_progress_action_fails() -> None:
    broken = VALID_APP.replace(
        """SecondaryAction(
            text = "Посмотреть итоги",
            onClick = onProgress,
            icon = StatsIcon,
            modifier = Modifier.weight(1f),
        )""",
        'SecondaryAction("Посмотреть итоги", onProgress)',
    )
    assert_fails(result_action_layout_failures(app_source=broken, docs=VALID_DOCS), "stacked full-width")


def test_missing_docs_fails() -> None:
    broken_docs = dict(VALID_DOCS)
    broken_docs["docs/ui_audit.md"] = "Экран результата содержит действия."
    assert_fails(result_action_layout_failures(app_source=VALID_APP, docs=broken_docs), "docs/ui_audit.md")


def main() -> int:
    test_valid_fixture_passes()
    test_missing_home_weight_fails()
    test_stacked_home_action_fails()
    test_missing_home_icon_fails()
    test_missing_progress_icon_fails()
    test_stacked_progress_action_fails()
    test_missing_docs_fails()
    print("PASS: Result action-layout checker self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
