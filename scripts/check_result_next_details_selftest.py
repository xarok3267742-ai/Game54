#!/usr/bin/env python3
from __future__ import annotations

from check_result_next_details import result_next_details_failures

VALID_APP = """
fun PoryadokApp() {
    ResultScreen(
        onNext = { screen = AppScreen.Timer(nextTask.id) },
        onOpenNext = { screen = AppScreen.Details(nextTask.id) },
    )
}

private fun ResultScreen(
    onNext: () -> Unit,
    onOpenNext: () -> Unit,
) {
    if (hasFreshNextTask) {
        PrimaryAction(
            text = "Посмотреть следующую",
            onClick = onOpenNext,
        )
        SecondaryAction(
            text = "Запустить таймер",
            onClick = onNext,
        )
    } else {
        PrimaryAction("Повторить задачу", onNext)
        SecondaryAction(
            text = "Посмотреть шаги",
            onClick = onOpenNext,
        )
    }
}
"""


def assert_passes(failures: list[str]) -> None:
    assert failures == [], failures


def assert_fails(failures: list[str], expected: str) -> None:
    assert any(expected in failure for failure in failures), failures


def test_valid_fixture_passes() -> None:
    assert_passes(result_next_details_failures(app_source=VALID_APP))


def test_missing_route_to_details_fails() -> None:
    broken = VALID_APP.replace("onOpenNext = { screen = AppScreen.Details(nextTask.id) },", "")
    assert_fails(result_next_details_failures(app_source=broken), "AppScreen.Details(nextTask.id)")


def test_missing_callback_parameter_fails() -> None:
    broken = VALID_APP.replace("    onOpenNext: () -> Unit,\n", "")
    assert_fails(result_next_details_failures(app_source=broken), "onOpenNext: () -> Unit")


def test_missing_secondary_action_fails() -> None:
    broken = VALID_APP.replace('            text = "Посмотреть шаги",\n', "")
    assert_fails(result_next_details_failures(app_source=broken), 'text = "Посмотреть шаги"')


def test_old_primary_start_next_fails() -> None:
    broken = VALID_APP.replace('text = "Посмотреть следующую"', 'text = "Запустить следующую"')
    assert_fails(result_next_details_failures(app_source=broken), "unsafe destination")


def test_open_next_to_timer_fails() -> None:
    broken = VALID_APP.replace(
        "onOpenNext = { screen = AppScreen.Details(nextTask.id) }",
        "onOpenNext = { screen = AppScreen.Timer(nextTask.id) }",
    )
    assert_fails(result_next_details_failures(app_source=broken), "unsafe destination")


def main() -> int:
    test_valid_fixture_passes()
    test_missing_route_to_details_fails()
    test_missing_callback_parameter_fails()
    test_missing_secondary_action_fails()
    test_old_primary_start_next_fails()
    test_open_next_to_timer_fails()
    print("PASS: Result next-details checker self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
