#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from check_progress_focus_summary import progress_focus_summary_failures


VALID_APP = textwrap.dedent(
    '''
    @Composable
    private fun ProgressScreen(preferences: AppPreferences, engine: PoryadokEngine) {
        val completedCatalogCount = engine.completedCount(preferences.progress.completedTaskIds)
        val totalCatalogCount = engine.totalTasks()
        val nextFocusArea = engine.nextFocusArea(preferences.progress.completedTaskIds)
        ProgressFocusSummary(
            area = nextFocusArea,
            completed = nextFocusArea?.let { engine.completedCountByArea(it, preferences.progress.completedTaskIds) } ?: completedCatalogCount,
            total = nextFocusArea?.let(engine::countByArea) ?: totalCatalogCount,
        )
    }

    @Composable
    private fun ProgressFocusSummary(area: TaskArea?, completed: Int, total: Int) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .defaultMinSize(minHeight = 56.dp)
                .padding(horizontal = 4.dp, vertical = 4.dp),
        ) {
            Box(
                modifier = Modifier.background(if (area == null) Sage else MaterialTheme.colorScheme.secondary, CircleShape),
            )
            Column {
                Text(text = if (area == null) "Каталог закрыт" else "Следующая зона")
                Text(
                    text = if (area == null) {
                        "Все $total задач отмечены. Можно повторять любимые задачи или начать каталог заново."
                    } else {
                        "${area.label}: $completed из $total. Хорошая точка для следующей 5-минутки."
                    },
                    color = MutedText,
                )
            }
        }
    }
    '''
)

VALID_ENGINE = textwrap.dedent(
    '''
    class PoryadokEngine(private val tasks: List<MicroTask>) {
        fun nextFocusArea(completedIds: Set<String>): TaskArea? {
            val normalizedCompletedIds = normalizedCompletedTaskIds(completedIds)
            return TaskArea.entries
                .mapNotNull { area ->
                    val total = countByArea(area)
                    if (total == 0) {
                        null
                    } else {
                        val completed = tasks.count { it.area == area && it.id in normalizedCompletedIds }
                        AreaProgress(area = area, completed = completed, total = total)
                    }
                }
                .filter { it.completed < it.total }
                .minWithOrNull(
                    compareBy<AreaProgress> { it.completed.toFloat() / it.total.toFloat() }
                        .thenBy { it.completed }
                        .thenBy { it.area.ordinal },
                )
                ?.area
        }

        fun countByArea(area: TaskArea): Int = tasks.count { it.area == area }

        private data class AreaProgress(
            val area: TaskArea,
            val completed: Int,
            val total: Int,
        )
    }
    '''
)

DOCS = {
    "docs/product_spec.md": "Progress next focus area Следующая зона",
    "docs/ui_audit.md": "Progress focus summary Следующая зона Каталог закрыт",
    "docs/accessibility_notes.md": "Progress focus summary non-interactive Следующая зона",
    "docs/qa_test_plan.md": "check_progress_focus_summary.py nextFocusArea",
}


class ProgressFocusSummarySelfTest(unittest.TestCase):
    def call(self, app: str = VALID_APP, engine: str = VALID_ENGINE, docs: dict[str, str] | None = None) -> list[str]:
        return progress_focus_summary_failures(app_source=app, engine_source=engine, docs=docs or DOCS)

    def test_valid_fixture_passes(self) -> None:
        self.assertEqual(self.call(), [])

    def test_missing_summary_call_fails(self) -> None:
        broken = VALID_APP.replace("ProgressFocusSummary(", "ProgressRhythmSummary(")

        failures = self.call(app=broken)

        self.assertTrue(any("ProgressFocusSummary(" in failure for failure in failures))

    def test_missing_engine_method_fails(self) -> None:
        broken = VALID_ENGINE.replace("fun nextFocusArea(completedIds: Set<String>): TaskArea?", "fun weakestArea(completedIds: Set<String>): TaskArea?")

        failures = self.call(engine=broken)

        self.assertTrue(any("nextFocusArea" in failure for failure in failures))

    def test_missing_complete_state_copy_fails(self) -> None:
        broken = VALID_APP.replace('"Каталог закрыт" else "Следующая зона"', '"Готово" else "Следующая зона"')

        failures = self.call(app=broken)

        self.assertTrue(any("Каталог закрыт" in failure for failure in failures))

    def test_interactive_or_framed_summary_fails(self) -> None:
        broken = VALID_APP.replace("Row(", "Surface(\n        Row(", 1)

        failures = self.call(app=broken)

        self.assertTrue(any("unframed" in failure for failure in failures))

    def test_missing_docs_fail(self) -> None:
        docs = dict(DOCS)
        docs["docs/ui_audit.md"] = "Progress screen notes."

        failures = self.call(docs=docs)

        self.assertTrue(any("docs/ui_audit.md" in failure for failure in failures))

    def test_missing_files_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            failures = progress_focus_summary_failures(
                app_path=root / "missing.kt",
                engine_path=root / "missing-engine.kt",
                docs=DOCS,
                root=root,
            )

        self.assertTrue(any("missing app file" in failure for failure in failures))
        self.assertTrue(any("missing engine file" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main()
