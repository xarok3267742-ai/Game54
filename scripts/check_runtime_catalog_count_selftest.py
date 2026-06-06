#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from check_runtime_catalog_count import runtime_catalog_count_failures


class RuntimeCatalogCountSelfTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="poryadok5-runtime-count.")
        self.root = Path(self.tmp.name)
        self.main = self.root / "app/src/main/java"
        self.engine = self.main / "ru/poryadok5/app/domain/PoryadokEngine.kt"
        self.ui = self.main / "ru/poryadok5/app/ui/PoryadokApp.kt"
        self.test = self.root / "app/src/test/java/ru/poryadok5/app/TaskCatalogTest.kt"
        self.required = (
            (self.engine, ("fun totalTasks(): Int = tasks.size",)),
            (self.ui, ("engine.totalTasks()", "catalogSize: Int", "$catalogSize задач")),
            (self.test, ("engineReportsCatalogSizeForRuntimeUi", "assertEquals(3, engine.totalTasks())")),
        )
        self.write(self.engine, "class PoryadokEngine { fun totalTasks(): Int = tasks.size }\n")
        self.write(
            self.ui,
            'fun ProgressScreen() { "${engine.totalTasks()}"; "$catalogSize задач" }\n'
            "fun SettingsScreen(catalogSize: Int) {}\n",
        )
        self.write(self.test, "fun engineReportsCatalogSizeForRuntimeUi() { assertEquals(3, engine.totalTasks()) }\n")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    @staticmethod
    def write(path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def failures(self) -> list[str]:
        return runtime_catalog_count_failures(self.root, self.main, self.required)

    def test_valid_fixture_passes(self) -> None:
        self.assertEqual([], self.failures())

    def test_hardcoded_progress_denominator_fails(self) -> None:
        self.write(self.ui, 'Text("1 из 80 уникальных задач")\n')
        self.assertTrue(any("hardcoded progress denominator" in failure for failure in self.failures()))

    def test_hardcoded_about_count_fails(self) -> None:
        self.write(self.ui, 'Text("Локальный каталог из 80 микрозадач")\n')
        self.assertTrue(any("hardcoded catalog microtask count" in failure for failure in self.failures()))

    def test_missing_engine_total_tasks_snippet_fails(self) -> None:
        self.write(self.engine, "class PoryadokEngine\n")
        self.assertTrue(any("fun totalTasks(): Int = tasks.size" in failure for failure in self.failures()))

    def test_missing_runtime_ui_usage_fails(self) -> None:
        self.write(self.ui, "fun SettingsScreen(catalogSize: Int) {}\n")
        self.assertTrue(any("engine.totalTasks()" in failure for failure in self.failures()))

    def test_missing_unit_test_evidence_fails(self) -> None:
        self.write(self.test, "class TaskCatalogTest\n")
        self.assertTrue(any("engineReportsCatalogSizeForRuntimeUi" in failure for failure in self.failures()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
