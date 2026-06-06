#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from check_timer_session_goal import timer_session_goal_failures


DOCS = {
    "docs/product_spec.md": "Timer session goal Цель: 5 мин",
    "docs/ui_audit.md": "Timer session goal Цель: 5 мин",
    "docs/qa_test_plan.md": "check_timer_session_goal.py Timer session goal",
}


def valid_source() -> str:
    return textwrap.dedent(
        '''
        @Composable
        private fun TimerScreen() {
            AppCard(containerColor = SageSoft) {
                Text(task.title, style = MaterialTheme.typography.titleLarge)
                Text("${task.area.label} · ${task.energy.label}", style = MaterialTheme.typography.bodyMedium)
                Text(
                    text = "Цель: ${task.minutes} мин",
                    style = MaterialTheme.typography.labelLarge,
                    color = MaterialTheme.colorScheme.primary,
                )
                ProgressLine(progress = progress)
                Text(text = formatTime(remainingSeconds))
            }
        }

        @Composable
        private fun ResultScreen() {}
        '''
    )


def goal_after_progress_source() -> str:
    return textwrap.dedent(
        '''
        @Composable
        private fun TimerScreen() {
            AppCard(containerColor = SageSoft) {
                Text(task.title, style = MaterialTheme.typography.titleLarge)
                Text("${task.area.label} · ${task.energy.label}", style = MaterialTheme.typography.bodyMedium)
                ProgressLine(progress = progress)
                Text(
                    text = "Цель: ${task.minutes} мин",
                    style = MaterialTheme.typography.labelLarge,
                    color = MaterialTheme.colorScheme.primary,
                )
                Text(text = formatTime(remainingSeconds))
            }
        }

        @Composable
        private fun ResultScreen() {}
        '''
    )


class TimerSessionGoalCheckTest(unittest.TestCase):
    def test_valid_fixture_passes(self) -> None:
        self.assertEqual(timer_session_goal_failures(valid_source(), DOCS), [])

    def test_missing_goal_fails(self) -> None:
        source = valid_source().replace('text = "Цель: ${task.minutes} мин"', 'text = "Осталось"')

        failures = timer_session_goal_failures(source, DOCS)

        self.assertTrue(any("Цель" in failure for failure in failures))

    def test_goal_after_progress_fails(self) -> None:
        failures = timer_session_goal_failures(goal_after_progress_source(), DOCS)

        self.assertTrue(any("between task metadata" in failure for failure in failures))

    def test_missing_docs_fail(self) -> None:
        docs = dict(DOCS)
        docs["docs/product_spec.md"] = "Timer"

        failures = timer_session_goal_failures(valid_source(), docs)

        self.assertTrue(any("docs/product_spec.md" in failure for failure in failures))

    def test_missing_app_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            missing = root / "missing.kt"

            failures = timer_session_goal_failures(app_path=missing, root=root)

        self.assertTrue(any("missing app file" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main()
