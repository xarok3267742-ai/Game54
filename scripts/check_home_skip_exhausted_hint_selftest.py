#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from check_home_skip_exhausted_hint import home_skip_exhausted_hint_failures


DOCS = {
    "docs/product_spec.md": "Другая задача Других задач по этому подбору сейчас нет",
    "docs/ui_audit.md": "Home skip exhausted hint Других задач по этому подбору сейчас нет",
    "docs/qa_test_plan.md": "check_home_skip_exhausted_hint.py Home skip exhausted hint",
}


def valid_source() -> str:
    return textwrap.dedent(
        '''
        @Composable
        private fun HomeScreen() {
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                SecondaryAction(
                    text = "Другая задача",
                    onClick = onSkipTask,
                    enabled = canSkipTask,
                    modifier = Modifier.weight(1f),
                )
            }
            AnimatedVisibility(visible = !canSkipTask) {
                Text(
                    text = "Других задач по этому подбору сейчас нет. Измените подбор или выполните текущую.",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MutedText,
                )
            }
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                MetricPill("выполнено", "0", MetricTone.Sage, Modifier.weight(1f))
            }
        }

        @Composable
        private fun TaskDetailsScreen() {}
        '''
    )


class HomeSkipExhaustedHintCheckTest(unittest.TestCase):
    def test_valid_fixture_passes(self) -> None:
        self.assertEqual(home_skip_exhausted_hint_failures(valid_source(), DOCS), [])

    def test_missing_hint_fails(self) -> None:
        source = valid_source().replace("AnimatedVisibility(visible = !canSkipTask)", "Column")

        failures = home_skip_exhausted_hint_failures(source, DOCS)

        self.assertTrue(any("AnimatedVisibility(visible = !canSkipTask)" in failure for failure in failures))

    def test_always_visible_hint_fails(self) -> None:
        source = valid_source().replace(
            "AnimatedVisibility(visible = !canSkipTask) {",
            'Text("Других задач по этому подбору сейчас нет. Измените подбор или выполните текущую.")\nColumn {',
        )

        failures = home_skip_exhausted_hint_failures(source, DOCS)

        self.assertTrue(any("forbidden marker" in failure for failure in failures))

    def test_hint_before_skip_fails(self) -> None:
        hint = textwrap.dedent(
            '''
            AnimatedVisibility(visible = !canSkipTask) {
                Text(
                    text = "Других задач по этому подбору сейчас нет. Измените подбор или выполните текущую.",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MutedText,
                )
            }
            '''
        )
        source = valid_source().replace(hint, "").replace("Row(horizontalArrangement", hint + "\nRow(horizontalArrangement", 1)

        failures = home_skip_exhausted_hint_failures(source, DOCS)

        self.assertTrue(any("after the skip action" in failure for failure in failures))

    def test_missing_docs_fail(self) -> None:
        docs = dict(DOCS)
        docs["docs/ui_audit.md"] = "Home skip exhausted hint"

        failures = home_skip_exhausted_hint_failures(valid_source(), docs)

        self.assertTrue(any("docs/ui_audit.md" in failure for failure in failures))

    def test_missing_app_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            missing = root / "missing.kt"

            failures = home_skip_exhausted_hint_failures(app_path=missing, root=root)

        self.assertTrue(any("missing app file" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main()
