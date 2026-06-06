#!/usr/bin/env python3
from __future__ import annotations

import unittest

from check_result_content_focus import result_content_focus_failures

VALID_APP = """
@Composable
private fun ResultScreen() {
    ScreenColumn {
        Text("Готово", style = MaterialTheme.typography.displaySmall)
        Text(task.resultText, style = MaterialTheme.typography.bodyLarge, color = MutedText)
        Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            MetricPill("выполнено", "1", MetricTone.Sage, Modifier.weight(1f))
        }
        TaskCard(
            task = nextTask,
            completed = !hasFreshNextTask,
            label = if (hasFreshNextTask) "Дальше без повтора" else "Каталог пройден",
            showResult = true,
        )
        PrimaryAction(
            text = "Посмотреть следующую",
            onClick = onOpenNext,
        )
    }
}
"""

VALID_DOCS = {
    "docs/ui_audit.md": "Экран результата uses task-specific result text без generic amber card and После preview.",
    "docs/qa_test_plan.md": "check_result_content_focus.py rejects Что изменилось and keeps next-task preview with showResult before actions.",
}


def assert_fails(failures: list[str], marker: str) -> None:
    assert any(marker in failure for failure in failures), failures


class ResultContentFocusSelfTest(unittest.TestCase):
    def test_valid_fixture_passes(self) -> None:
        self.assertEqual(result_content_focus_failures(app_source=VALID_APP, docs=VALID_DOCS), [])

    def test_generic_completion_copy_fails(self) -> None:
        broken = VALID_APP.replace(
            "TaskCard(",
            'AppCard(containerColor = AmberSoft) { Text("Что изменилось"); Text("Вы закрыли маленькую задачу") }\n        TaskCard(',
        )
        failures = result_content_focus_failures(app_source=broken, docs=VALID_DOCS)
        assert_fails(failures, "generic completion copy")
        assert_fails(failures, "amber")

    def test_missing_task_result_fails(self) -> None:
        broken = VALID_APP.replace("        Text(task.resultText, style = MaterialTheme.typography.bodyLarge, color = MutedText)\n", "")
        assert_fails(result_content_focus_failures(app_source=broken, docs=VALID_DOCS), "task.resultText")

    def test_next_preview_after_action_fails(self) -> None:
        broken = VALID_APP.replace(
            "        TaskCard(",
            '        PrimaryAction(\n            text = "Посмотреть следующую",\n            onClick = onOpenNext,\n        )\n        TaskCard(',
        )
        assert_fails(result_content_focus_failures(app_source=broken, docs=VALID_DOCS), "order")

    def test_missing_next_result_preview_fails(self) -> None:
        broken = VALID_APP.replace("            showResult = true,\n", "")
        assert_fails(result_content_focus_failures(app_source=broken, docs=VALID_DOCS), "showResult")

    def test_missing_docs_fail(self) -> None:
        broken_docs = dict(VALID_DOCS)
        broken_docs["docs/ui_audit.md"] = "Result screen notes."
        assert_fails(result_content_focus_failures(app_source=VALID_APP, docs=broken_docs), "docs/ui_audit.md")


if __name__ == "__main__":
    unittest.main(verbosity=2)
