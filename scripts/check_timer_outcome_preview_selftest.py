#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from check_timer_outcome_preview import timer_outcome_preview_failures


DOCS = {
    "docs/product_spec.md": "Timer outcome preview После",
    "docs/ui_audit.md": "Timer outcome preview После",
    "docs/qa_test_plan.md": "check_timer_outcome_preview.py Timer outcome preview",
}


def valid_source() -> str:
    return textwrap.dedent(
        '''
        @Composable
        private fun TimerScreen() {
            AppCard {
                Text("План", style = MaterialTheme.typography.titleMedium)
                task.steps.forEachIndexed { index, step -> StepRow(index + 1, step) }
                TaskResultPreview(task.resultText)
            }
            Row {
                SecondaryAction(text = "Пауза", onClick = {})
            }
        }

        @Composable
        private fun ResultScreen() {}
        '''
    )


def preview_before_steps_source() -> str:
    return textwrap.dedent(
        '''
        @Composable
        private fun TimerScreen() {
            AppCard {
                Text("План", style = MaterialTheme.typography.titleMedium)
                TaskResultPreview(task.resultText)
                task.steps.forEachIndexed { index, step -> StepRow(index + 1, step) }
            }
            Row {
                SecondaryAction(text = "Пауза", onClick = {})
            }
        }

        @Composable
        private fun ResultScreen() {}
        '''
    )


class TimerOutcomePreviewCheckTest(unittest.TestCase):
    def test_valid_fixture_passes(self) -> None:
        self.assertEqual(timer_outcome_preview_failures(valid_source(), DOCS), [])

    def test_missing_preview_fails(self) -> None:
        source = valid_source().replace("TaskResultPreview(task.resultText)", "")

        failures = timer_outcome_preview_failures(source, DOCS)

        self.assertTrue(any("TaskResultPreview" in failure for failure in failures))

    def test_preview_before_steps_fails(self) -> None:
        failures = timer_outcome_preview_failures(preview_before_steps_source(), DOCS)

        self.assertTrue(any("after the step list" in failure for failure in failures))

    def test_inline_old_preview_fails(self) -> None:
        source = valid_source().replace(
            "TaskResultPreview(task.resultText)",
            'Text("После: ${task.resultText}")',
        )

        failures = timer_outcome_preview_failures(source, DOCS)

        self.assertTrue(any("old inline" in failure for failure in failures))

    def test_missing_docs_fail(self) -> None:
        docs = dict(DOCS)
        docs["docs/ui_audit.md"] = "Timer"

        failures = timer_outcome_preview_failures(valid_source(), docs)

        self.assertTrue(any("docs/ui_audit.md" in failure for failure in failures))

    def test_missing_app_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            missing = root / "missing.kt"

            failures = timer_outcome_preview_failures(app_path=missing, root=root)

        self.assertTrue(any("missing app file" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main()
