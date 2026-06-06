#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from check_timer_completion_dock import timer_completion_dock_failures


DOCS = {
    "docs/product_spec.md": "Timer bottom action dock Готово",
    "docs/ui_audit.md": "Timer completion dock Готово компактных экранах",
    "docs/qa_test_plan.md": "check_timer_completion_dock.py Timer completion dock",
}


def valid_source() -> str:
    return textwrap.dedent(
        '''
        @Composable
        private fun TimerScreen() {
            Box(modifier = Modifier.weight(1f)) {
                ScreenColumn(includeTopPadding = false) {
                    Text("План")
                    Spacer(Modifier.height(88.dp))
                }
                BottomActionDock(modifier = Modifier.align(Alignment.BottomCenter)) {
                    PrimaryAction(
                        text = "Готово",
                        onClick = {},
                    )
                }
            }
        }

        @Composable
        private fun BottomActionDock() {
            Surface(
                shadowElevation = 4.dp,
            ) {
                Column(
                    modifier = Modifier
                        .widthIn(max = ContentMaxWidth)
                        .padding(horizontal = 20.dp, vertical = 12.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                ) {}
            }
        }

        @Composable
        private fun ResultScreen() {}
        '''
    )


class TimerCompletionDockCheckTest(unittest.TestCase):
    def test_valid_fixture_passes(self) -> None:
        self.assertEqual(timer_completion_dock_failures(valid_source(), DOCS), [])

    def test_missing_dock_fails(self) -> None:
        source = valid_source().replace(
            "BottomActionDock(modifier = Modifier.align(Alignment.BottomCenter))",
            "Column",
        )

        failures = timer_completion_dock_failures(source, DOCS)

        self.assertTrue(any("BottomActionDock(modifier" in failure for failure in failures))

    def test_scrolled_complete_action_fails(self) -> None:
        source = valid_source().replace(
            'Text("План")',
            'Text("План")\n                PrimaryAction(text = "Готово", onClick = {})',
        )

        failures = timer_completion_dock_failures(source, DOCS)

        self.assertTrue(any("must live in BottomActionDock" in failure for failure in failures))

    def test_missing_scroll_spacer_fails(self) -> None:
        source = valid_source().replace("Spacer(Modifier.height(88.dp))", "Spacer(Modifier.height(16.dp))")

        failures = timer_completion_dock_failures(source, DOCS)

        self.assertTrue(any("Spacer(Modifier.height(88.dp))" in failure for failure in failures))

    def test_missing_docs_fail(self) -> None:
        docs = dict(DOCS)
        docs["docs/ui_audit.md"] = "Timer completion dock"

        failures = timer_completion_dock_failures(valid_source(), docs)

        self.assertTrue(any("docs/ui_audit.md" in failure for failure in failures))

    def test_missing_app_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            missing = root / "missing.kt"

            failures = timer_completion_dock_failures(app_path=missing, root=root)

        self.assertTrue(any("missing app file" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main()
