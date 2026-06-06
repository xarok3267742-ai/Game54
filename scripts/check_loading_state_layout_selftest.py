#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from check_loading_state_layout import loading_state_layout_failures


DOCS = {
    "docs/ui_audit.md": "Loading states full-screen centered",
    "docs/qa_test_plan.md": "check_loading_state_layout.py Loading state layout",
    "docs/accessibility_notes.md": "Loading state centered",
}


def valid_source() -> str:
    return textwrap.dedent(
        '''
        @Composable
        fun LoadingState(message: String) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(32.dp),
                contentAlignment = Alignment.Center,
            ) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(16.dp),
                ) {
                    CircularProgressIndicator(color = Sage)
                    Text(message, style = MaterialTheme.typography.bodyMedium)
                }
            }
        }

        @Composable
        fun TopBar() {}
        '''
    )


class LoadingStateLayoutCheckTest(unittest.TestCase):
    def test_valid_fixture_passes(self) -> None:
        self.assertEqual(loading_state_layout_failures(valid_source(), DOCS), [])

    def test_width_only_loading_fails(self) -> None:
        source = valid_source().replace(".fillMaxSize()", ".fillMaxWidth()")

        failures = loading_state_layout_failures(source, DOCS)

        self.assertTrue(any(".fillMaxSize()" in failure for failure in failures))

    def test_missing_center_alignment_fails(self) -> None:
        source = valid_source().replace("contentAlignment = Alignment.Center,", "")

        failures = loading_state_layout_failures(source, DOCS)

        self.assertTrue(any("Alignment.Center" in failure for failure in failures))

    def test_old_spacer_spacing_fails(self) -> None:
        source = valid_source().replace(
            "verticalArrangement = Arrangement.spacedBy(16.dp),",
            "Spacer(Modifier.height(16.dp))",
        )

        failures = loading_state_layout_failures(source, DOCS)

        self.assertTrue(any("Spacer(Modifier.height(16.dp))" in failure for failure in failures))

    def test_missing_docs_fail(self) -> None:
        docs = dict(DOCS)
        docs["docs/ui_audit.md"] = "Loading states"

        failures = loading_state_layout_failures(valid_source(), docs)

        self.assertTrue(any("docs/ui_audit.md" in failure for failure in failures))

    def test_missing_components_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            missing = root / "missing.kt"

            failures = loading_state_layout_failures(components_path=missing, root=root)

        self.assertTrue(any("missing components file" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main()
