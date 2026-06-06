#!/usr/bin/env python3
from __future__ import annotations

from check_settings_danger_action import ACCESSIBILITY_NOTES, QA_PLAN, UI_AUDIT, settings_danger_action_failures

VALID_COMPONENTS = """
@Composable
fun DangerAction(text: String, onClick: () -> Unit) {
    OutlinedButton(
        modifier = Modifier.defaultMinSize(minHeight = 52.dp),
        onClick = onClick,
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.error),
        colors = ButtonDefaults.outlinedButtonColors(
            contentColor = MaterialTheme.colorScheme.error,
        ),
    ) {
        Text(text)
    }
}
"""

VALID_APP = """
import ru.poryadok5.app.ui.components.DangerAction

@Composable
private fun SettingsScreen() {
    if (confirmReset) {
        Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            SecondaryAction(text = "Отмена", onClick = onCancel)
            DangerAction(
                text = "Сбросить прогресс",
                onClick = onResetProgress,
            )
        }
    }
}

@Composable
private fun TaskCard() {}
"""

VALID_DOCS = {
    UI_AUDIT: "Сброс прогресса использует DangerAction с error цветом.",
    ACCESSIBILITY_NOTES: "DangerAction для Сбросить прогресс сохраняет 52dp target.",
    QA_PLAN: "check_settings_danger_action.py проверяет DangerAction.",
}


def failures_for(
    components: str = VALID_COMPONENTS,
    app: str = VALID_APP,
    docs: dict = VALID_DOCS,
) -> list[str]:
    return settings_danger_action_failures(components_source=components, app_source=app, docs=docs)


def assert_passes(failures: list[str]) -> None:
    assert failures == [], failures


def assert_fails(failures: list[str], expected: str) -> None:
    assert any(expected in failure for failure in failures), failures


def test_valid_fixture_passes() -> None:
    assert_passes(failures_for())


def test_missing_component_fails() -> None:
    assert_fails(failures_for(components=""), "DangerAction component is missing")


def test_missing_error_border_fails() -> None:
    broken = VALID_COMPONENTS.replace(
        "BorderStroke(1.dp, MaterialTheme.colorScheme.error)",
        "BorderStroke(1.dp, MaterialTheme.colorScheme.surfaceVariant)",
    )
    assert_fails(failures_for(components=broken), "MaterialTheme.colorScheme.error")


def test_missing_52dp_target_fails() -> None:
    broken = VALID_COMPONENTS.replace(".defaultMinSize(minHeight = 52.dp)", ".defaultMinSize(minHeight = 44.dp)")
    assert_fails(failures_for(components=broken), "52.dp")


def test_neutral_reset_action_fails() -> None:
    broken = VALID_APP.replace("DangerAction(", "SecondaryAction(")
    assert_fails(failures_for(app=broken), "DangerAction")


def test_missing_docs_fails() -> None:
    docs = dict(VALID_DOCS)
    docs[ACCESSIBILITY_NOTES] = "Сбросить прогресс имеет большой target."
    assert_fails(failures_for(docs=docs), "docs/accessibility_notes.md")


def main() -> int:
    test_valid_fixture_passes()
    test_missing_component_fails()
    test_missing_error_border_fails()
    test_missing_52dp_target_fails()
    test_neutral_reset_action_fails()
    test_missing_docs_fails()
    print("PASS: Settings danger-action checker self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
