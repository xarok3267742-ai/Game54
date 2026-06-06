#!/usr/bin/env python3
from __future__ import annotations

import unittest

from check_task_details_start_dock import task_details_start_dock_failures

VALID_APP = """
@Composable
private fun TaskDetailsScreen() {
    Column(modifier = Modifier.fillMaxSize()) {
        TopBar(title = "Задача", onBack = onBack)
        Box(modifier = Modifier.weight(1f)) {
            ScreenColumn(includeTopPadding = false) {
                TaskResultPreview(task.resultText)
                Text("Шаги", style = MaterialTheme.typography.titleLarge)
                Spacer(Modifier.height(88.dp))
            }
            BottomActionDock(modifier = Modifier.align(Alignment.BottomCenter)) {
                PrimaryAction(
                    text = "Начать ${task.minutes} мин",
                    onClick = onStart,
                )
            }
        }
    }
}

@Composable
private fun DetailBriefingFact() {}
"""

VALID_DOCS = {
    "docs/product_spec.md": "Task details start dock keeps Начать visible on compact screens.",
    "docs/ui_audit.md": "Task details start dock keeps Начать reachable on compact screens.",
    "docs/qa_test_plan.md": "check_task_details_start_dock.py covers Task details start dock.",
    "docs/accessibility_notes.md": "Task details start dock keeps Начать as the primary action.",
}


def assert_passes(failures: list[str]) -> None:
    if failures:
        raise AssertionError("expected no failures, got: " + "; ".join(failures))


def assert_fails(failures: list[str], marker: str) -> None:
    if not any(marker in failure for failure in failures):
        raise AssertionError(f"expected failure containing {marker!r}, got: {failures!r}")


class TaskDetailsStartDockSelfTest(unittest.TestCase):
    def test_valid_fixture_passes(self) -> None:
        assert_passes(task_details_start_dock_failures(app_source=VALID_APP, docs=VALID_DOCS))

    def test_missing_dock_fails(self) -> None:
        broken = VALID_APP.replace("BottomActionDock(modifier = Modifier.align(Alignment.BottomCenter))", "Column")
        assert_fails(task_details_start_dock_failures(app_source=broken, docs=VALID_DOCS), "BottomActionDock")

    def test_start_inside_scroll_fails(self) -> None:
        broken = VALID_APP.replace(
            "Spacer(Modifier.height(88.dp))",
            'PrimaryAction(text = "Начать ${task.minutes} мин", onClick = onStart)\n                Spacer(Modifier.height(88.dp))',
        ).replace(
            'PrimaryAction(\n                    text = "Начать ${task.minutes} мин",\n                    onClick = onStart,\n                )',
            "",
        )
        assert_fails(task_details_start_dock_failures(app_source=broken, docs=VALID_DOCS), "inside BottomActionDock")

    def test_spacer_before_content_fails(self) -> None:
        broken = VALID_APP.replace(
            'Text("Шаги", style = MaterialTheme.typography.titleLarge)\n                Spacer(Modifier.height(88.dp))',
            'Spacer(Modifier.height(88.dp))\n                Text("Шаги", style = MaterialTheme.typography.titleLarge)',
        )
        assert_fails(task_details_start_dock_failures(app_source=broken, docs=VALID_DOCS), "after scroll content")

    def test_missing_docs_fail(self) -> None:
        docs = dict(VALID_DOCS)
        docs["docs/ui_audit.md"] = "Task details start dock."
        assert_fails(task_details_start_dock_failures(app_source=VALID_APP, docs=docs), "docs/ui_audit.md")


if __name__ == "__main__":
    unittest.main(verbosity=2)
