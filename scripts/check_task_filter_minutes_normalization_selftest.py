#!/usr/bin/env python3
from __future__ import annotations

import tempfile
from pathlib import Path

from check_task_filter_minutes_normalization import task_filter_minutes_normalization_failures

VALID_MODELS = """
val SupportedTaskMinutes = setOf(3, 5, 10)

fun normalizedTaskMinutes(value: Int): Int {
    return if (value in SupportedTaskMinutes) value else 5
}
"""

VALID_ENGINE = """
class PoryadokEngine {
    fun suggestTask(filter: TaskFilter, completedIds: Set<String>): MicroTask {
        val normalizedFilter = filter.copy(minutes = normalizedTaskMinutes(filter.minutes))
        val exact = tasks.filter {
            it.area == normalizedFilter.area &&
                it.energy == normalizedFilter.energy &&
                it.minutes == normalizedFilter.minutes
        }
        val relaxed = tasks.filter {
            it.area == normalizedFilter.area && it.minutes == normalizedFilter.minutes
        }
        val stableIndex = day.toEpochDay() +
            normalizedFilter.area.ordinal * 17L +
            normalizedFilter.energy.ordinal * 31L +
            normalizedFilter.minutes
        return source[0]
    }
}
"""

VALID_APP = """
import ru.poryadok5.app.domain.SupportedTaskMinutes
import ru.poryadok5.app.domain.normalizedTaskMinutes

fun PoryadokApp() {
    val selectedDuration = normalizedTaskMinutes(selectedMinutes)
    val filter = TaskFilter(selectedArea, selectedEnergy, selectedDuration)
    SupportedTaskMinutes.forEach { minutes -> println(minutes) }
}
"""

VALID_MODELS_TEST = """
class ModelsTest {
    fun taskMinutesNormalizeToAllowedValues() {
        assertEquals(setOf(3, 5, 10), SupportedTaskMinutes)
        assertEquals(5, normalizedTaskMinutes(7))
        assertEquals(5, normalizedTaskMinutes(-1))
    }
}
"""

VALID_ENGINE_TEST = """
class PoryadokEngineTest {
    fun suggestTaskNormalizesUnsupportedFilterMinutes() {
        val filter = TaskFilter(TaskArea.Home, EnergyLevel.Active, 7)
        assertEquals("home_active_5", suggestion.id)
    }
}
"""


def failures_for(
    models_source: str = VALID_MODELS,
    engine_source: str = VALID_ENGINE,
    app_source: str = VALID_APP,
    models_test_source: str = VALID_MODELS_TEST,
    engine_test_source: str = VALID_ENGINE_TEST,
) -> list[str]:
    with tempfile.TemporaryDirectory(prefix="poryadok5-task-minutes.") as tmp_dir:
        root = Path(tmp_dir)
        models = root / "Models.kt"
        engine = root / "PoryadokEngine.kt"
        app = root / "PoryadokApp.kt"
        models_test = root / "ModelsTest.kt"
        engine_test = root / "PoryadokEngineTest.kt"
        models.write_text(models_source, encoding="utf-8")
        engine.write_text(engine_source, encoding="utf-8")
        app.write_text(app_source, encoding="utf-8")
        models_test.write_text(models_test_source, encoding="utf-8")
        engine_test.write_text(engine_test_source, encoding="utf-8")
        return task_filter_minutes_normalization_failures(
            required_snippets=(
                (
                    models,
                    (
                        "val SupportedTaskMinutes = setOf(3, 5, 10)",
                        "fun normalizedTaskMinutes(value: Int): Int",
                        "return if (value in SupportedTaskMinutes) value else 5",
                    ),
                ),
                (
                    engine,
                    (
                        "val normalizedFilter = filter.copy(minutes = normalizedTaskMinutes(filter.minutes))",
                        "it.area == normalizedFilter.area",
                        "it.energy == normalizedFilter.energy",
                        "it.minutes == normalizedFilter.minutes",
                        "normalizedFilter.area.ordinal * 17L",
                        "normalizedFilter.energy.ordinal * 31L",
                        "            normalizedFilter.minutes",
                    ),
                ),
                (
                    app,
                    (
                        "import ru.poryadok5.app.domain.SupportedTaskMinutes",
                        "import ru.poryadok5.app.domain.normalizedTaskMinutes",
                        "val selectedDuration = normalizedTaskMinutes(selectedMinutes)",
                        "TaskFilter(selectedArea, selectedEnergy, selectedDuration)",
                        "SupportedTaskMinutes.forEach",
                    ),
                ),
                (
                    models_test,
                    (
                        "taskMinutesNormalizeToAllowedValues",
                        "SupportedTaskMinutes",
                        "normalizedTaskMinutes(7)",
                        "normalizedTaskMinutes(-1)",
                    ),
                ),
                (
                    engine_test,
                    (
                        "suggestTaskNormalizesUnsupportedFilterMinutes",
                        "TaskFilter(TaskArea.Home, EnergyLevel.Active, 7)",
                        '"home_active_5"',
                    ),
                ),
            ),
            forbidden_snippets=(
                (
                    engine,
                    (
                        "it.area == filter.area",
                        "it.energy == filter.energy",
                        "it.minutes == filter.minutes",
                        "+ filter.minutes",
                        "\n            filter.minutes",
                    ),
                ),
                (
                    app,
                    (
                        "TaskFilter(selectedArea, selectedEnergy, selectedMinutes)",
                        "listOf(3, 5, 10).forEach",
                    ),
                ),
            ),
            root=root,
        )


def assert_passes(failures: list[str]) -> None:
    assert failures == [], failures


def assert_fails(failures: list[str], expected: str) -> None:
    assert any(expected in failure for failure in failures), failures


def test_valid_fixture_passes() -> None:
    assert_passes(failures_for())


def test_missing_model_normalizer_fails() -> None:
    broken = VALID_MODELS.replace("return if (value in SupportedTaskMinutes) value else 5", "return value")
    assert_fails(failures_for(models_source=broken), "value in SupportedTaskMinutes")


def test_raw_engine_filter_minutes_fail() -> None:
    broken = VALID_ENGINE.replace("it.minutes == normalizedFilter.minutes", "it.minutes == filter.minutes")
    failures = failures_for(engine_source=broken)
    assert_fails(failures, "normalizedFilter.minutes")
    assert_fails(failures, "raw task-filter minutes usage")


def test_raw_engine_stable_index_fails() -> None:
    broken = VALID_ENGINE.replace("            normalizedFilter.minutes", "            filter.minutes")
    failures = failures_for(engine_source=broken)
    assert_fails(failures, "normalizedFilter.minutes")
    assert_fails(failures, "raw task-filter minutes usage")


def test_raw_app_filter_minutes_fail() -> None:
    broken = VALID_APP.replace(
        "TaskFilter(selectedArea, selectedEnergy, selectedDuration)",
        "TaskFilter(selectedArea, selectedEnergy, selectedMinutes)",
    )
    failures = failures_for(app_source=broken)
    assert_fails(failures, "selectedDuration")
    assert_fails(failures, "raw task-filter minutes usage")


def test_missing_unit_test_evidence_fails() -> None:
    broken = VALID_ENGINE_TEST.replace("suggestTaskNormalizesUnsupportedFilterMinutes", "suggestTaskUsesMinutes")
    assert_fails(failures_for(engine_test_source=broken), "suggestTaskNormalizesUnsupportedFilterMinutes")


def main() -> int:
    test_valid_fixture_passes()
    test_missing_model_normalizer_fails()
    test_raw_engine_filter_minutes_fail()
    test_raw_engine_stable_index_fails()
    test_raw_app_filter_minutes_fail()
    test_missing_unit_test_evidence_fails()
    print("PASS: task filter minute normalization checker self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
