#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from check_task_repository_parser import task_repository_parser_failures


class TaskRepositoryParserSelfTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="poryadok5-task-parser.")
        root = Path(self.tmp.name)
        self.repository = root / "TaskRepository.kt"
        self.main_activity = root / "MainActivity.kt"
        self.test = root / "TaskCatalogTest.kt"
        self.required = (
            (
                self.repository,
                (
                    "internal fun parseTaskCatalog",
                    "import ru.poryadok5.app.domain.SupportedTaskMinutes",
                    "import ru.poryadok5.app.domain.isRouteSafeTaskId",
                    "require(tasks.isNotEmpty())",
                    "val ids = mutableSetOf<String>()",
                    "parseTaskId(item.getString(\"id\"))",
                    "val area = parseCatalogArea(item.getString(\"area\"), id)",
                    "validateTaskIdArea(id, area)",
                    "require(ids.add(id))",
                    "area = area",
                    "parseCatalogEnergy(item.getString(\"energy\"), id)",
                    "parseTaskMinutes(item.getInt(\"minutes\"), id)",
                    "parseRequiredText(item.getString(\"title\"), id, \"название\")",
                    "parseTaskSteps(item.getJSONArray(\"steps\"), id)",
                    "parseRequiredText(item.getString(\"resultText\"), id, \"результат\")",
                    "Задача должна содержать id",
                    "isRouteSafeTaskId(id)",
                    "неподдерживаемый id",
                    "private fun validateTaskIdArea(id: String, area: TaskArea)",
                    "area.catalogIdPrefix()",
                    "не соответствует зоне",
                    "Повторяющийся id задачи",
                    "require(value in SupportedTaskMinutes)",
                    "неподдерживаемое время",
                    "require(stepsJson.length() == 3)",
                    "Неизвестная зона задачи",
                    "Неизвестный уровень энергии задачи",
                    "содержит пустой шаг",
                ),
            ),
            (self.main_activity, ("loadError = \"Не удалось прочитать локальный список задач.\"",)),
            (
                self.test,
                (
                    "taskParserRejectsEmptyCatalog",
                    "taskParserRejectsUnknownAreaInsteadOfFallingBack",
                    "taskParserRejectsUnknownEnergyInsteadOfFallingBack",
                    "taskParserRejectsBlankId",
                    "taskParserRejectsRouteUnsafeId",
                    "taskParserRejectsIdAreaMismatch",
                    "taskParserRejectsDuplicateIds",
                    "taskParserRejectsUnsupportedMinutes",
                    "taskParserRejectsBlankTitle",
                    "taskParserRejectsWrongStepCountBeforeUiCanReadFirstStep",
                    "taskParserRejectsBlankStep",
                    "taskParserRejectsBlankResultText",
                ),
            ),
        )
        self.forbidden = (
            (self.repository, "TaskArea.fromRaw", "area fallback"),
            (self.repository, "EnergyLevel.fromRaw", "energy fallback"),
            (self.repository, "require(value in setOf(3, 5, 10))", "hardcoded duration set"),
            (self.repository, "val area = TaskArea.fromRaw", "permissive area derivation"),
            (self.repository, "TaskIdPattern.matches(id)", "local task-id pattern"),
            (self.main_activity, "loadError = it.message", "technical error leak"),
        )
        self.write_valid_fixture()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    @staticmethod
    def write(path: Path, text: str) -> None:
        path.write_text(text, encoding="utf-8")

    def write_valid_fixture(self) -> None:
        self.write(
            self.repository,
            """
                internal fun parseTaskCatalog(json: String) {
                    import ru.poryadok5.app.domain.SupportedTaskMinutes
                    import ru.poryadok5.app.domain.isRouteSafeTaskId
                    require(tasks.isNotEmpty()) { "Локальный список задач пуст." }
                    val ids = mutableSetOf<String>()
                    parseTaskId(item.getString("id"))
                    val area = parseCatalogArea(item.getString("area"), id)
                    validateTaskIdArea(id, area)
                    require(ids.add(id)) { "Повторяющийся id задачи" }
                    area = area
                    parseCatalogEnergy(item.getString("energy"), id)
                    parseTaskMinutes(item.getInt("minutes"), id)
                    parseRequiredText(item.getString("title"), id, "название")
                    parseTaskSteps(item.getJSONArray("steps"), id)
                    parseRequiredText(item.getString("resultText"), id, "результат")
                    error("Задача должна содержать id")
                    isRouteSafeTaskId(id)
                    error("неподдерживаемый id")
                    private fun validateTaskIdArea(id: String, area: TaskArea)
                    area.catalogIdPrefix()
                    error("не соответствует зоне")
                    require(value in SupportedTaskMinutes)
                    error("неподдерживаемое время")
                    require(stepsJson.length() == 3)
                    error("Неизвестная зона задачи")
                    error("Неизвестный уровень энергии задачи")
                error("содержит пустой шаг")
            }
            """,
        )
        self.write(self.main_activity, 'loadError = "Не удалось прочитать локальный список задач."\n')
        self.write(
            self.test,
            """
            fun taskParserRejectsEmptyCatalog() {}
            fun taskParserRejectsUnknownAreaInsteadOfFallingBack() {}
            fun taskParserRejectsUnknownEnergyInsteadOfFallingBack() {}
            fun taskParserRejectsBlankId() {}
            fun taskParserRejectsRouteUnsafeId() {}
            fun taskParserRejectsIdAreaMismatch() {}
            fun taskParserRejectsDuplicateIds() {}
            fun taskParserRejectsUnsupportedMinutes() {}
            fun taskParserRejectsBlankTitle() {}
            fun taskParserRejectsWrongStepCountBeforeUiCanReadFirstStep() {}
            fun taskParserRejectsBlankStep() {}
            fun taskParserRejectsBlankResultText() {}
            """,
        )

    def failures(self) -> list[str]:
        return task_repository_parser_failures(self.required, self.forbidden)

    def test_valid_fixture_passes(self) -> None:
        self.assertEqual([], self.failures())

    def test_area_fallback_fails(self) -> None:
        self.write(self.repository, self.repository.read_text(encoding="utf-8") + "\nTaskArea.fromRaw(value)\n")
        self.assertTrue(any("TaskArea.fromRaw" in failure for failure in self.failures()))

    def test_energy_fallback_fails(self) -> None:
        self.write(self.repository, self.repository.read_text(encoding="utf-8") + "\nEnergyLevel.fromRaw(value)\n")
        self.assertTrue(any("EnergyLevel.fromRaw" in failure for failure in self.failures()))

    def test_technical_error_leak_fails(self) -> None:
        self.write(self.main_activity, "loadError = it.message\n")
        self.assertTrue(any("technical error leak" in failure for failure in self.failures()))

    def test_missing_parser_test_fails(self) -> None:
        self.write(self.test, "fun taskParserRejectsEmptyCatalog() {}\n")
        self.assertTrue(
            any("taskParserRejectsUnknownAreaInsteadOfFallingBack" in failure for failure in self.failures())
        )

    def test_missing_task_id_validator_fails(self) -> None:
        self.write(
            self.repository,
            self.repository.read_text(encoding="utf-8").replace(
                "isRouteSafeTaskId(id)",
                "",
            ),
        )
        self.assertTrue(any("isRouteSafeTaskId(id)" in failure for failure in self.failures()))

    def test_local_task_id_pattern_fails(self) -> None:
        self.write(
            self.repository,
            self.repository.read_text(encoding="utf-8").replace(
                "isRouteSafeTaskId(id)",
                "TaskIdPattern.matches(id)",
            ),
        )
        self.assertTrue(any("isRouteSafeTaskId(id)" in failure for failure in self.failures()))
        self.assertTrue(any("local task-id pattern" in failure for failure in self.failures()))

    def test_missing_task_id_area_validation_fails(self) -> None:
        self.write(
            self.repository,
            self.repository.read_text(encoding="utf-8").replace("validateTaskIdArea(id, area)", ""),
        )
        self.assertTrue(any("validateTaskIdArea(id, area)" in failure for failure in self.failures()))

    def test_missing_step_count_validation_fails(self) -> None:
        self.write(
            self.repository,
            self.repository.read_text(encoding="utf-8").replace("require(stepsJson.length() == 3)", ""),
        )
        self.assertTrue(any("require(stepsJson.length() == 3)" in failure for failure in self.failures()))

    def test_missing_duration_validation_fails(self) -> None:
        self.write(
            self.repository,
            self.repository.read_text(encoding="utf-8").replace("require(value in SupportedTaskMinutes)", ""),
        )
        self.assertTrue(any("require(value in SupportedTaskMinutes)" in failure for failure in self.failures()))

    def test_hardcoded_duration_set_fails(self) -> None:
        self.write(
            self.repository,
            self.repository.read_text(encoding="utf-8").replace(
                "require(value in SupportedTaskMinutes)",
                "require(value in setOf(3, 5, 10))",
            ),
        )
        self.assertTrue(any("SupportedTaskMinutes" in failure for failure in self.failures()))
        self.assertTrue(any("hardcoded duration set" in failure for failure in self.failures()))

    def test_missing_duplicate_id_parser_test_fails(self) -> None:
        self.write(
            self.test,
            self.test.read_text(encoding="utf-8").replace("fun taskParserRejectsDuplicateIds() {}\n", ""),
        )
        self.assertTrue(any("taskParserRejectsDuplicateIds" in failure for failure in self.failures()))

    def test_missing_blank_step_parser_test_fails(self) -> None:
        self.write(
            self.test,
            self.test.read_text(encoding="utf-8").replace("fun taskParserRejectsBlankStep() {}\n", ""),
        )
        self.assertTrue(any("taskParserRejectsBlankStep" in failure for failure in self.failures()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
