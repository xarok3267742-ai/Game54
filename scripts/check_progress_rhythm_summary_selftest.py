#!/usr/bin/env python3
from __future__ import annotations

import unittest

from check_progress_rhythm_summary import progress_rhythm_summary_failures

VALID_APP = """
@Composable
private fun ProgressScreen() {
    AppCard(containerColor = BlueSoft) {
        Text("Ритм", style = MaterialTheme.typography.titleMedium)
        ProgressRhythmSummary()
    }
}

@Composable
private fun ProgressRhythmSummary() {
    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        ProgressRhythmItem(
            label = "Серия",
            value = "1 раз в день",
            modifier = Modifier.weight(1f),
        )
        ProgressRhythmItem(
            label = "Счётчик",
            value = "каждая задача",
            modifier = Modifier.weight(1f),
        )
    }
}

@Composable
private fun ProgressRhythmItem(label: String, value: String, modifier: Modifier = Modifier) {
    Column(
        modifier = modifier
            .defaultMinSize(minHeight = 56.dp)
            .padding(horizontal = 4.dp, vertical = 6.dp),
        verticalArrangement = Arrangement.spacedBy(2.dp),
    ) {
        Text(label)
        Text(value)
    }
}
"""

VALID_DOCS = {
    "docs/ui_audit.md": "Progress rhythm summary shows Серия and Счётчик.",
    "docs/qa_test_plan.md": "Progress rhythm summary must show Серия and Счётчик.",
}


def assert_fails(failures: list[str], marker: str) -> None:
    assert any(marker in failure for failure in failures), failures


class ProgressRhythmSummarySelfTest(unittest.TestCase):
    def test_valid_source_passes(self) -> None:
        self.assertEqual(progress_rhythm_summary_failures(app_source=VALID_APP, docs=VALID_DOCS), [])

    def test_old_paragraph_fails(self) -> None:
        broken = VALID_APP.replace(
            "ProgressRhythmSummary()",
            'Text("Серия растёт один раз в день. Несколько задач за день увеличивают общий счётчик, но не накручивают серию.")',
        )
        assert_fails(progress_rhythm_summary_failures(app_source=broken, docs=VALID_DOCS), "old paragraph")

    def test_missing_counter_fact_fails(self) -> None:
        broken = VALID_APP.replace('value = "каждая задача"', 'value = "общий прогресс"')
        assert_fails(progress_rhythm_summary_failures(app_source=broken, docs=VALID_DOCS), "каждая задача")

    def test_interactive_fact_fails(self) -> None:
        broken = VALID_APP.replace(
            "verticalArrangement = Arrangement.spacedBy(2.dp),",
            "verticalArrangement = Arrangement.spacedBy(2.dp),\n        modifier = Modifier.clickable(onClick = {}),",
        )
        assert_fails(progress_rhythm_summary_failures(app_source=broken, docs=VALID_DOCS), ".clickable(")

    def test_framed_fact_fails(self) -> None:
        broken = VALID_APP.replace(
            "Column(\n        modifier = modifier",
            "Surface(\n        border = BorderStroke(1.dp, MaterialTheme.colorScheme.surfaceVariant),\n        modifier = modifier",
        )
        assert_fails(progress_rhythm_summary_failures(app_source=broken, docs=VALID_DOCS), "unframed")

    def test_short_fact_height_fails(self) -> None:
        broken = VALID_APP.replace("defaultMinSize(minHeight = 56.dp)", "defaultMinSize(minHeight = 40.dp)")
        assert_fails(progress_rhythm_summary_failures(app_source=broken, docs=VALID_DOCS), "56.dp")

    def test_missing_docs_fail(self) -> None:
        broken_docs = dict(VALID_DOCS)
        broken_docs["docs/ui_audit.md"] = "Progress screen notes."
        assert_fails(progress_rhythm_summary_failures(app_source=VALID_APP, docs=broken_docs), "docs/ui_audit.md")


if __name__ == "__main__":
    unittest.main(verbosity=2)
