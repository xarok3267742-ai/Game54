#!/usr/bin/env python3
from __future__ import annotations

import unittest

from check_task_details_briefing import task_details_briefing_failures

VALID_APP = """
@Composable
private fun TaskDetailsScreen() {
    TaskCard(label = "Выбранная задача", statusText = "выбрана")
    AppCard(containerColor = SageSoft) {
        Text("Перед стартом", style = MaterialTheme.typography.titleMedium)
        Text("Выполните шаги сверху вниз. Достаточно заметного улучшения, не идеального порядка.")
        Row {
            DetailBriefingFact(label = "зона", value = task.area.label)
            DetailBriefingFact(label = "энергия", value = task.energy.label)
            DetailBriefingFact(label = "время", value = "${task.minutes} мин")
        }
        TaskResultPreview(task.resultText)
    }
    AppCard {
        Text("Шаги", style = MaterialTheme.typography.titleLarge)
    }
    PrimaryAction(
        text = "Начать ${task.minutes} мин",
        onClick = onStart,
    )
}

@Composable
private fun DetailBriefingFact() {
    Column(
        modifier = modifier
            .defaultMinSize(minHeight = 56.dp)
            .padding(horizontal = 4.dp, vertical = 6.dp),
    ) {
        Text(style = MaterialTheme.typography.bodyMedium, color = MutedText, text = label)
        Text(style = MaterialTheme.typography.labelLarge, color = Sage, text = value)
    }
}

@Composable
private fun TimerScreen() {}
"""

VALID_DOCS = {
    "docs/product_spec.md": "Task details includes a предстартовый briefing with зона/энергия/время.",
    "docs/ui_audit.md": "Task details briefing uses Перед стартом and keeps unframed 56dp targets.",
    "docs/qa_test_plan.md": "check_task_details_briefing.py covers Task details briefing.",
}


def assert_passes(failures: list[str]) -> None:
    if failures:
        raise AssertionError("expected no failures, got: " + "; ".join(failures))


def assert_fails(failures: list[str], marker: str) -> None:
    if not any(marker in failure for failure in failures):
        raise AssertionError(f"expected failure containing {marker!r}, got: {failures!r}")


class TaskDetailsBriefingSelfTest(unittest.TestCase):
    def test_valid_fixture_passes(self) -> None:
        assert_passes(task_details_briefing_failures(app_source=VALID_APP, docs=VALID_DOCS))

    def test_missing_before_start_copy_fails(self) -> None:
        broken = VALID_APP.replace('Text("Перед стартом", style = MaterialTheme.typography.titleMedium)', "")
        assert_fails(task_details_briefing_failures(app_source=broken, docs=VALID_DOCS), "Перед стартом")

    def test_briefing_after_steps_fails(self) -> None:
        before = 'Text("Перед стартом", style = MaterialTheme.typography.titleMedium)'
        steps = 'Text("Шаги", style = MaterialTheme.typography.titleLarge)'
        broken = VALID_APP.replace(before, "__TEMP__").replace(steps, before).replace("__TEMP__", steps)
        assert_fails(task_details_briefing_failures(app_source=broken, docs=VALID_DOCS), "before the full step list")

    def test_result_preview_after_steps_fails(self) -> None:
        preview = "        TaskResultPreview(task.resultText)"
        steps = '        Text("Шаги", style = MaterialTheme.typography.titleLarge)'
        broken = VALID_APP.replace(preview, "__PREVIEW__").replace(steps, preview).replace("__PREVIEW__", steps)
        assert_fails(task_details_briefing_failures(app_source=broken, docs=VALID_DOCS), "result preview")

    def test_missing_chip_target_fails(self) -> None:
        broken = VALID_APP.replace(".defaultMinSize(minHeight = 56.dp)", "")
        assert_fails(task_details_briefing_failures(app_source=broken, docs=VALID_DOCS), "56.dp")

    def test_framed_fact_fails(self) -> None:
        broken = VALID_APP.replace(
            "Column(\n        modifier = modifier",
            "Surface(\n        modifier = modifier,\n        shape = MaterialTheme.shapes.small,\n        border = BorderStroke(1.dp, MaterialTheme.colorScheme.surfaceVariant),\n    ) {\n    Column(\n        modifier = modifier",
        )
        assert_fails(task_details_briefing_failures(app_source=broken, docs=VALID_DOCS), "unframed")

    def test_missing_selected_status_fails(self) -> None:
        broken = VALID_APP.replace(', statusText = "выбрана"', "")
        assert_fails(task_details_briefing_failures(app_source=broken, docs=VALID_DOCS), "выбрана")

    def test_missing_docs_fail(self) -> None:
        docs = dict(VALID_DOCS)
        docs["docs/ui_audit.md"] = "Task details briefing only."
        assert_fails(task_details_briefing_failures(app_source=VALID_APP, docs=docs), "docs/ui_audit.md")


if __name__ == "__main__":
    unittest.main(verbosity=2)
