#!/usr/bin/env python3
from __future__ import annotations

from check_settings_reset_cancel import QA_PLAN, UI_AUDIT, settings_reset_cancel_failures

VALID_APP = """
@Composable
private fun SettingsScreen() {
    var confirmReset by rememberSaveable { mutableStateOf(false) }
    var resetNoticeVisible by rememberSaveable { mutableStateOf(false) }
    if (confirmReset) {
        Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            SecondaryAction(
                text = "Отмена",
                onClick = {
                    confirmReset = false
                    resetNoticeVisible = false
                },
                modifier = Modifier.weight(1f),
            )
            SecondaryAction(
                text = "Сбросить прогресс",
                onClick = {
                    onResetProgress()
                    confirmReset = false
                    resetNoticeVisible = true
                },
                modifier = Modifier.weight(1f),
            )
        }
    } else {
        SecondaryAction(
            text = "Подготовить сброс",
            onClick = {
                resetNoticeVisible = false
                confirmReset = true
            },
        )
    }
}

@Composable
private fun TaskCard() {}
"""

VALID_DOCS = {
    UI_AUDIT: "Сброс прогресса показывает подтверждение и отмену.",
    QA_PLAN: "Проверить Отмена и Сбросить прогресс.",
}


def failures_for(app_source: str = VALID_APP, docs: dict = VALID_DOCS) -> list[str]:
    return settings_reset_cancel_failures(app_source=app_source, doc_sources=docs)


def assert_passes(failures: list[str]) -> None:
    assert failures == [], failures


def assert_fails(failures: list[str], expected: str) -> None:
    assert any(expected in failure for failure in failures), failures


def test_valid_fixture_passes() -> None:
    assert_passes(failures_for())


def test_missing_cancel_button_fails() -> None:
    broken = VALID_APP.replace('            SecondaryAction(\n                text = "Отмена",', '            SecondaryAction(\n                text = "Назад",')
    assert_fails(failures_for(app_source=broken), 'text = "Отмена"')


def test_missing_cancel_state_reset_fails() -> None:
    broken = VALID_APP.replace("resetNoticeVisible = false", "resetNoticeVisible = true", 1)
    assert_fails(failures_for(app_source=broken), "completion feedback")


def test_cancel_after_destructive_action_fails() -> None:
    broken = VALID_APP.replace(
        'text = "Отмена"',
        'text = "TEMP_CANCEL"',
    ).replace(
        'text = "Сбросить прогресс"',
        'text = "Отмена"',
    ).replace(
        'text = "TEMP_CANCEL"',
        'text = "Сбросить прогресс"',
    )
    assert_fails(failures_for(app_source=broken), "before the destructive")


def test_missing_doc_marker_fails() -> None:
    docs = dict(VALID_DOCS)
    docs[QA_PLAN] = "Проверить Сбросить прогресс."
    assert_fails(failures_for(docs=docs), "Отмена")


def main() -> int:
    test_valid_fixture_passes()
    test_missing_cancel_button_fails()
    test_missing_cancel_state_reset_fails()
    test_cancel_after_destructive_action_fails()
    test_missing_doc_marker_fails()
    print("PASS: Settings reset cancel checker self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
