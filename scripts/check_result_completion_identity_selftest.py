#!/usr/bin/env python3
from __future__ import annotations

import unittest

from check_result_completion_identity import result_completion_identity_failures

VALID_APP = """
@Composable
private fun ResultScreen() {
    ScreenColumn {
        Text("Готово", style = MaterialTheme.typography.displaySmall)
        Text("Сделано: ${task.title}", style = MaterialTheme.typography.titleMedium, color = Sage)
        Text(task.resultText, style = MaterialTheme.typography.bodyLarge, color = MutedText)
    }
}
"""

VALID_DOCS = {
    "docs/product_spec.md": "Result shows Сделано before the outcome.",
    "docs/ui_audit.md": "Экран результата confirms Сделано.",
    "docs/qa_test_plan.md": "check_result_completion_identity.py verifies Сделано.",
}


def assert_fails(failures: list[str], marker: str) -> None:
    if not any(marker in failure for failure in failures):
        raise AssertionError(f"expected failure containing {marker!r}, got: {failures!r}")


class ResultCompletionIdentitySelfTest(unittest.TestCase):
    def test_valid_fixture_passes(self) -> None:
        self.assertEqual(result_completion_identity_failures(app_source=VALID_APP, docs=VALID_DOCS), [])

    def test_missing_completed_title_fails(self) -> None:
        broken = VALID_APP.replace(
            '        Text("Сделано: ${task.title}", style = MaterialTheme.typography.titleMedium, color = Sage)\n',
            "",
        )
        assert_fails(result_completion_identity_failures(app_source=broken, docs=VALID_DOCS), "Сделано")

    def test_next_task_title_fails(self) -> None:
        broken = VALID_APP.replace("${task.title}", "${nextTask.title}")
        assert_fails(result_completion_identity_failures(app_source=broken, docs=VALID_DOCS), "completed task")

    def test_wrong_order_fails(self) -> None:
        broken = VALID_APP.replace(
            '        Text("Сделано: ${task.title}", style = MaterialTheme.typography.titleMedium, color = Sage)\n        Text(task.resultText, style = MaterialTheme.typography.bodyLarge, color = MutedText)\n',
            '        Text(task.resultText, style = MaterialTheme.typography.bodyLarge, color = MutedText)\n        Text("Сделано: ${task.title}", style = MaterialTheme.typography.titleMedium, color = Sage)\n',
        )
        assert_fails(result_completion_identity_failures(app_source=broken, docs=VALID_DOCS), "between")

    def test_missing_docs_fail(self) -> None:
        docs = dict(VALID_DOCS)
        docs["docs/qa_test_plan.md"] = "Result checks."
        assert_fails(result_completion_identity_failures(app_source=VALID_APP, docs=docs), "docs/qa_test_plan.md")


if __name__ == "__main__":
    unittest.main(verbosity=2)
