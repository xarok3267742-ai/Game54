#!/usr/bin/env python3
from __future__ import annotations

import unittest

from check_task_result_preview import task_result_preview_failures

VALID_APP = """
@Composable
private fun TaskCard(showResult: Boolean = false) {
    if (showResult) {
        TaskResultPreview(task.resultText)
    }
}

@Composable
private fun TaskResultPreview(resultText: String) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .defaultMinSize(minHeight = 48.dp),
        verticalArrangement = Arrangement.spacedBy(2.dp),
    ) {
        Text("После", style = MaterialTheme.typography.labelLarge, color = Sage)
        Text(resultText, style = MaterialTheme.typography.bodyMedium, color = MutedText)
    }
}

@Composable
private fun TaskStatusPill() {}
"""

VALID_DOCS = {
    "docs/product_spec.md": "Home includes a compact result preview with После.",
    "docs/ui_audit.md": "Home task result preview uses compact result preview and После.",
    "docs/qa_test_plan.md": "check_task_result_preview.py covers Home task result preview.",
}


def assert_passes(failures: list[str]) -> None:
    if failures:
        raise AssertionError("expected no failures, got: " + "; ".join(failures))


def assert_fails(failures: list[str], marker: str) -> None:
    if not any(marker in failure for failure in failures):
        raise AssertionError(f"expected failure containing {marker!r}, got: {failures!r}")


class TaskResultPreviewSelfTest(unittest.TestCase):
    def test_valid_fixture_passes(self) -> None:
        assert_passes(task_result_preview_failures(app_source=VALID_APP, docs=VALID_DOCS))

    def test_old_inline_result_fails(self) -> None:
        broken = VALID_APP.replace("TaskResultPreview(task.resultText)", 'Text("После: ${task.resultText}")')
        assert_fails(task_result_preview_failures(app_source=broken, docs=VALID_DOCS), "old inline")

    def test_missing_preview_composable_fails(self) -> None:
        broken = VALID_APP.replace("private fun TaskResultPreview", "private fun OldTaskResultPreview")
        assert_fails(task_result_preview_failures(app_source=broken, docs=VALID_DOCS), "TaskResultPreview body")

    def test_short_preview_height_fails(self) -> None:
        broken = VALID_APP.replace(".defaultMinSize(minHeight = 48.dp)", ".defaultMinSize(minHeight = 32.dp)")
        assert_fails(task_result_preview_failures(app_source=broken, docs=VALID_DOCS), "48.dp")

    def test_framed_preview_fails(self) -> None:
        broken = VALID_APP.replace(
            "Column(\n        modifier = Modifier",
            "Surface(\n        border = BorderStroke(1.dp, Sage),\n    ) {\n    Column(\n        modifier = Modifier",
        )
        assert_fails(task_result_preview_failures(app_source=broken, docs=VALID_DOCS), "unframed")

    def test_interactive_preview_fails(self) -> None:
        broken = VALID_APP.replace(".fillMaxWidth()", ".fillMaxWidth().clickable(onClick = {})")
        assert_fails(task_result_preview_failures(app_source=broken, docs=VALID_DOCS), ".clickable(")

    def test_missing_docs_fail(self) -> None:
        docs = dict(VALID_DOCS)
        docs["docs/ui_audit.md"] = "Home task result preview."
        assert_fails(task_result_preview_failures(app_source=VALID_APP, docs=docs), "docs/ui_audit.md")


if __name__ == "__main__":
    unittest.main(verbosity=2)
