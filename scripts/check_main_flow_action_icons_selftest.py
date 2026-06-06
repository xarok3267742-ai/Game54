#!/usr/bin/env python3
from __future__ import annotations

import unittest

from check_main_flow_action_icons import main_flow_action_icon_failures

VALID_APP = """
import androidx.compose.material.icons.automirrored.filled.ArrowForward
import androidx.compose.material.icons.automirrored.filled.List
import androidx.compose.material.icons.filled.Done
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Refresh

private val PauseIcon: ImageVector = ImageVector.Builder(
    name = "Pause",
).build()

@Composable
private fun HomeScreen() {
    SecondaryAction(text = "Все шаги", icon = Icons.AutoMirrored.Filled.List)
}

@Composable
private fun OnboardingScreen() {
    PrimaryAction(text = "Начать", icon = Icons.Filled.PlayArrow)
}

@Composable
private fun TaskDetailsScreen() {
    PrimaryAction(text = "Начать ${task.minutes} мин", icon = Icons.Filled.PlayArrow)
}

@Composable
private fun TimerScreen() {
    SecondaryAction(
        text = if (running) "Пауза" else "Продолжить",
        icon = if (running) PauseIcon else Icons.Filled.PlayArrow,
    )
    SecondaryAction(text = "Сброс", icon = Icons.Filled.Refresh)
    PrimaryAction(text = "Готово", icon = Icons.Filled.Done)
}

@Composable
private fun ResultScreen() {
    PrimaryAction(text = "Посмотреть следующую", icon = Icons.AutoMirrored.Filled.List)
    SecondaryAction(text = "Запустить таймер", icon = Icons.Filled.PlayArrow)
    PrimaryAction(text = "Повторить задачу", icon = Icons.Filled.Refresh)
    SecondaryAction(text = "Посмотреть шаги", icon = Icons.AutoMirrored.Filled.List)
}

@Composable
private fun ProgressScreen() {
    PrimaryAction(text = "Продолжить с задачей", icon = Icons.AutoMirrored.Filled.ArrowForward)
}
"""

VALID_DOCS = {
    "docs/product_spec.md": "main-flow CTA icons include Готово and Продолжить с задачей.",
    "docs/ui_audit.md": "Main-flow CTA icons use Done, ArrowForward and PauseIcon.",
    "docs/accessibility_notes.md": "Main-flow CTA icons are decorative timer controls and keep text labels.",
    "docs/qa_test_plan.md": "check_main_flow_action_icons.py covers main-flow CTA icons.",
}


def assert_passes(failures: list[str]) -> None:
    if failures:
        raise AssertionError("expected no failures, got: " + "; ".join(failures))


def assert_fails(failures: list[str], marker: str) -> None:
    if not any(marker in failure for failure in failures):
        raise AssertionError(f"expected failure containing {marker!r}, got: {failures!r}")


class MainFlowActionIconsSelfTest(unittest.TestCase):
    def test_valid_fixture_passes(self) -> None:
        assert_passes(main_flow_action_icon_failures(app_source=VALID_APP, docs=VALID_DOCS))

    def test_missing_timer_done_icon_fails(self) -> None:
        broken = VALID_APP.replace("icon = Icons.Filled.Done", "icon = null")
        assert_fails(main_flow_action_icon_failures(app_source=broken, docs=VALID_DOCS), "Done")

    def test_missing_timer_pause_resume_icon_fails(self) -> None:
        broken = VALID_APP.replace(
            "icon = if (running) PauseIcon else Icons.Filled.PlayArrow",
            "icon = null",
        )
        assert_fails(main_flow_action_icon_failures(app_source=broken, docs=VALID_DOCS), "PauseIcon")

    def test_missing_timer_reset_icon_fails(self) -> None:
        timer_reset = 'SecondaryAction(text = "Сброс", icon = Icons.Filled.Refresh)'
        broken = VALID_APP.replace(timer_reset, 'SecondaryAction(text = "Сброс")')
        assert_fails(main_flow_action_icon_failures(app_source=broken, docs=VALID_DOCS), "Refresh")

    def test_missing_progress_icon_fails(self) -> None:
        broken = VALID_APP.replace("icon = Icons.AutoMirrored.Filled.ArrowForward", "icon = null")
        assert_fails(main_flow_action_icon_failures(app_source=broken, docs=VALID_DOCS), "ArrowForward")

    def test_missing_result_repeat_icon_fails(self) -> None:
        broken = VALID_APP.replace("icon = Icons.Filled.Refresh", "icon = null")
        assert_fails(main_flow_action_icon_failures(app_source=broken, docs=VALID_DOCS), "Refresh")

    def test_heavy_icon_dependency_fails(self) -> None:
        broken = VALID_APP + '\nimplementation("androidx.compose.material:material-icons-extended")'
        assert_fails(main_flow_action_icon_failures(app_source=broken, docs=VALID_DOCS), "material-icons-core")

    def test_missing_docs_fail(self) -> None:
        docs = dict(VALID_DOCS)
        docs["docs/ui_audit.md"] = "Main-flow CTA icons."
        assert_fails(main_flow_action_icon_failures(app_source=VALID_APP, docs=docs), "docs/ui_audit.md")


if __name__ == "__main__":
    unittest.main(verbosity=2)
