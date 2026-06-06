#!/usr/bin/env python3
from __future__ import annotations

import tempfile
from pathlib import Path

from check_engine_completed_id_normalization import engine_completed_id_normalization_failures

VALID_ENGINE = """
class PoryadokEngine {
    private val taskIds: Set<String> = tasks.mapTo(mutableSetOf()) { it.id }

    fun suggestTask(filter: TaskFilter, completedIds: Set<String>): MicroTask {
        val normalizedCompletedIds = normalizedCompletedTaskIds(completedIds)
        val source = pools.asSequence()
            .map { pool -> pool.filterNot { it.id in normalizedCompletedIds } }
            .first()
        return source[0]
    }

    fun suggestAfterCompletion(
        filter: TaskFilter,
        completedIds: Set<String>,
        completedTaskId: String,
    ): MicroTask {
        return suggestTask(filter, normalizedCompletedTaskIds(completedIds + completedTaskId), day = day)
    }

    fun completedCount(completedIds: Set<String>): Int = normalizedCompletedTaskIds(completedIds).count { it in taskIds }

    fun hasUncompletedTasksAfterCompletion(completedIds: Set<String>, completedTaskId: String): Boolean {
        val normalizedCompletedIds = normalizedCompletedTaskIds(completedIds + completedTaskId)
        return tasks.any { it.id !in normalizedCompletedIds }
    }

    fun completedCountByArea(area: TaskArea, completedIds: Set<String>): Int {
        val normalizedCompletedIds = normalizedCompletedTaskIds(completedIds)
        return tasks.count { it.area == area && it.id in normalizedCompletedIds }
    }
}
"""

VALID_ENGINE_TEST = """
class PoryadokEngineTest {
    fun suggestTaskTrimsCompletedIdsBeforeExcludingTasks() {
        engine.suggestTask(filter, completedIds = setOf(" home_light_3 "))
    }
    fun suggestAfterCompletionTrimsJustCompletedTaskId() {
        engine.suggestAfterCompletion(filter, completedIds = emptySet(), completedTaskId = " home_light_3 ")
    }
    fun progressCountTrimsCompletedIdsBeforeCatalogMatch() {
        engine.completedCount(setOf(" home_light_3 ", " missing_999 ", "work_light_3"))
    }
    fun completedCountByAreaUsesKnownTrimmedCatalogIds() {
        engine.completedCountByArea(TaskArea.Home, setOf(" home_light_3 ", " missing_999 "))
    }
    fun hasUncompletedTasksAfterCompletionUsesKnownTrimmedCatalogIds() {
        engine.hasUncompletedTasksAfterCompletion(setOf(" home_light_3 ", " missing_999 "), " work_light_3 ")
    }
}
"""


def failures_for(
    engine_source: str = VALID_ENGINE,
    engine_test_source: str = VALID_ENGINE_TEST,
) -> list[str]:
    with tempfile.TemporaryDirectory(prefix="poryadok5-engine-completed-id.") as tmp_dir:
        root = Path(tmp_dir)
        engine = root / "PoryadokEngine.kt"
        test = root / "PoryadokEngineTest.kt"
        engine.write_text(engine_source, encoding="utf-8")
        test.write_text(engine_test_source, encoding="utf-8")
        return engine_completed_id_normalization_failures(
            required_snippets=(
                (
                    engine,
                    (
                        "val normalizedCompletedIds = normalizedCompletedTaskIds(completedIds)",
                        "filterNot { it.id in normalizedCompletedIds }",
                        "suggestTask(filter, normalizedCompletedTaskIds(completedIds + completedTaskId), day = day)",
                        "normalizedCompletedTaskIds(completedIds).count { it in taskIds }",
                        "fun hasUncompletedTasksAfterCompletion(completedIds: Set<String>, completedTaskId: String): Boolean",
                        "return tasks.any { it.id !in normalizedCompletedIds }",
                        "fun completedCountByArea(area: TaskArea, completedIds: Set<String>): Int",
                        "return tasks.count { it.area == area && it.id in normalizedCompletedIds }",
                    ),
                ),
                (
                    test,
                    (
                        "suggestTaskTrimsCompletedIdsBeforeExcludingTasks",
                        "suggestAfterCompletionTrimsJustCompletedTaskId",
                        "progressCountTrimsCompletedIdsBeforeCatalogMatch",
                        "completedCountByAreaUsesKnownTrimmedCatalogIds",
                        "hasUncompletedTasksAfterCompletionUsesKnownTrimmedCatalogIds",
                        '" home_light_3 "',
                        '" missing_999 "',
                    ),
                ),
            ),
            forbidden_snippets=(
                (
                    engine,
                    (
                        "filterNot { it.id in completedIds }",
                        "completedIds.count { it in taskIds }",
                        "it.id in completedIds",
                        "it.id !in completedIds",
                        "suggestTask(filter, completedIds + completedTaskId, day = day)",
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


def test_raw_suggestion_completed_ids_fail() -> None:
    broken = VALID_ENGINE.replace("filterNot { it.id in normalizedCompletedIds }", "filterNot { it.id in completedIds }")
    failures = failures_for(engine_source=broken)
    assert_fails(failures, "normalizedCompletedIds")
    assert_fails(failures, "raw completed-id usage")


def test_raw_completion_id_merge_fails() -> None:
    broken = VALID_ENGINE.replace(
        "suggestTask(filter, normalizedCompletedTaskIds(completedIds + completedTaskId), day = day)",
        "suggestTask(filter, completedIds + completedTaskId, day = day)",
    )
    failures = failures_for(engine_source=broken)
    assert_fails(failures, "normalizedCompletedTaskIds(completedIds + completedTaskId)")
    assert_fails(failures, "raw completed-id usage")


def test_raw_progress_count_fails() -> None:
    broken = VALID_ENGINE.replace(
        "normalizedCompletedTaskIds(completedIds).count { it in taskIds }",
        "completedIds.count { it in taskIds }",
    )
    failures = failures_for(engine_source=broken)
    assert_fails(failures, "normalizedCompletedTaskIds(completedIds).count")
    assert_fails(failures, "raw completed-id usage")


def test_raw_area_progress_count_fails() -> None:
    broken = VALID_ENGINE.replace(
        "return tasks.count { it.area == area && it.id in normalizedCompletedIds }",
        "return tasks.count { it.area == area && it.id in completedIds }",
    )
    failures = failures_for(engine_source=broken)
    assert_fails(failures, "it.id in normalizedCompletedIds")
    assert_fails(failures, "raw completed-id usage")


def test_raw_completed_catalog_state_fails() -> None:
    broken = VALID_ENGINE.replace(
        "return tasks.any { it.id !in normalizedCompletedIds }",
        "return tasks.any { it.id !in completedIds }",
    )
    failures = failures_for(engine_source=broken)
    assert_fails(failures, "it.id !in normalizedCompletedIds")
    assert_fails(failures, "raw completed-id usage")


def test_missing_whitespace_suggestion_test_fails() -> None:
    broken = VALID_ENGINE_TEST.replace("suggestTaskTrimsCompletedIdsBeforeExcludingTasks", "suggestTaskSkipsCompleted")
    assert_fails(failures_for(engine_test_source=broken), "suggestTaskTrimsCompletedIdsBeforeExcludingTasks")


def test_missing_whitespace_progress_test_fails() -> None:
    broken = VALID_ENGINE_TEST.replace('" missing_999 "', '"missing_999"')
    assert_fails(failures_for(engine_test_source=broken), '" missing_999 "')


def test_missing_area_progress_test_fails() -> None:
    broken = VALID_ENGINE_TEST.replace("completedCountByAreaUsesKnownTrimmedCatalogIds", "areaProgressCountsCompleted")
    assert_fails(failures_for(engine_test_source=broken), "completedCountByAreaUsesKnownTrimmedCatalogIds")


def test_missing_completed_catalog_state_test_fails() -> None:
    broken = VALID_ENGINE_TEST.replace(
        "hasUncompletedTasksAfterCompletionUsesKnownTrimmedCatalogIds",
        "completedCatalogStateUsesKnownIds",
    )
    assert_fails(failures_for(engine_test_source=broken), "hasUncompletedTasksAfterCompletionUsesKnownTrimmedCatalogIds")


def main() -> int:
    test_valid_fixture_passes()
    test_raw_suggestion_completed_ids_fail()
    test_raw_completion_id_merge_fails()
    test_raw_progress_count_fails()
    test_raw_area_progress_count_fails()
    test_raw_completed_catalog_state_fails()
    test_missing_whitespace_suggestion_test_fails()
    test_missing_whitespace_progress_test_fails()
    test_missing_area_progress_test_fails()
    test_missing_completed_catalog_state_test_fails()
    print("PASS: engine completed-id normalization checker self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
