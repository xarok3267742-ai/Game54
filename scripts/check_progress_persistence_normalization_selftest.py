#!/usr/bin/env python3
from __future__ import annotations

import tempfile
from pathlib import Path

from check_progress_persistence_normalization import progress_persistence_normalization_failures

VALID_PROGRESS_RULES = """
package ru.poryadok5.app.domain

internal fun normalizedCompletedTaskIds(ids: Set<String>): Set<String> {
    return ids.mapNotNullTo(mutableSetOf()) { rawId ->
        rawId.trim().takeIf(String::isNotEmpty)
    }
}

internal fun normalizedLastDoneDate(rawDate: String?): String? {
    return rawDate
        ?.trim()
        ?.takeIf(String::isNotEmpty)
        ?.let { candidate ->
            runCatching { LocalDate.parse(candidate) }.getOrNull()?.toString()
        }
}

fun UserProgress.withCompletedTask(taskId: String): UserProgress {
    val normalizedTaskId = taskId.trim()
    val normalizedCompletedTaskIds = normalizedCompletedTaskIds(completedTaskIds)
    val safeLastDoneDate = normalizedLastDoneDate(lastDoneDate)
    return copy(
        lastDoneDate = safeLastDoneDate,
        completedTaskIds = normalizedCompletedTaskIds + normalizedTaskId,
    )
}
"""

VALID_USER_PREFERENCES = """
package ru.poryadok5.app.data

import ru.poryadok5.app.domain.normalizedCompletedTaskIds
import ru.poryadok5.app.domain.normalizedLastDoneDate

internal fun Preferences.toAppPreferences(): AppPreferences {
    return AppPreferences(
        progress = UserProgress(
            lastDoneDate = normalizedLastDoneDate(this[UserPreferencesKeys.LastDoneDate]),
            completedTaskIds = this[UserPreferencesKeys.CompletedTaskIds]
                ?.let(::normalizedCompletedTaskIds)
                ?: emptySet(),
        ),
    )
}

internal fun MutablePreferences.writeProgress(progress: UserProgress) {
    normalizedLastDoneDate(progress.lastDoneDate)?.let { lastDoneDate ->
        this[UserPreferencesKeys.LastDoneDate] = lastDoneDate
    } ?: remove(UserPreferencesKeys.LastDoneDate)
    this[UserPreferencesKeys.CompletedTaskIds] = normalizedCompletedTaskIds(progress.completedTaskIds)
}
"""

VALID_PROGRESS_TEST = """
class ProgressRulesTest {
    fun blankCompletionDoesNotIncrementProgress() = Unit
    fun blankCompletionClearsMalformedStoredDate() {
        UserProgress(lastDoneDate = "bad-date").withCompletedTask(" ")
    }
    fun completionTaskIdIsTrimmedBeforeStorage() {
        UserProgress().withCompletedTask(" home_001 ")
    }
    fun existingCompletedTaskIdsAreTrimmedOnCompletion() {
        UserProgress(completedTaskIds = setOf(" home_001 ", " ")).withCompletedTask(" home_002 ")
    }
}
"""

VALID_USER_PREFERENCES_TEST = """
class UserPreferencesRepositoryTest {
    fun corruptedStoredProgressIsNormalizedForUi() {
        preferencesOf(
            UserPreferencesKeys.LastDoneDate to "bad-date",
            UserPreferencesKeys.CompletedTaskIds to setOf("", " home_001 ", " "),
        )
    }
    fun storedLastDoneDateIsTrimmedForUi() {
        preferencesOf(UserPreferencesKeys.LastDoneDate to " 2026-05-27 ")
    }
    fun writeProgressNormalizesLastDoneDateBeforeStorage() {
        UserProgress(lastDoneDate = " 2026-05-27 ")
    }
    fun writeProgressRemovesMalformedLastDoneDate() {
        UserProgress(lastDoneDate = "bad-date")
    }
    fun writeProgressNormalizesInvalidProgressBeforeStorage() {
        UserProgress(completedTaskIds = setOf("", "home_001", " work_002 ", " "))
    }
}
"""


def failures_for(
    progress_rules: str = VALID_PROGRESS_RULES,
    user_preferences: str = VALID_USER_PREFERENCES,
    progress_test: str = VALID_PROGRESS_TEST,
    user_preferences_test: str = VALID_USER_PREFERENCES_TEST,
) -> list[str]:
    with tempfile.TemporaryDirectory(prefix="poryadok5-progress-persistence.") as tmp_dir:
        root = Path(tmp_dir)
        progress_rules_path = root / "ProgressRules.kt"
        user_preferences_path = root / "UserPreferencesRepository.kt"
        progress_test_path = root / "ProgressRulesTest.kt"
        user_preferences_test_path = root / "UserPreferencesRepositoryTest.kt"

        progress_rules_path.write_text(progress_rules, encoding="utf-8")
        user_preferences_path.write_text(user_preferences, encoding="utf-8")
        progress_test_path.write_text(progress_test, encoding="utf-8")
        user_preferences_test_path.write_text(user_preferences_test, encoding="utf-8")

        return progress_persistence_normalization_failures(
            required_snippets=(
                (
                    progress_rules_path,
                    (
                        "internal fun normalizedCompletedTaskIds(ids: Set<String>): Set<String>",
                        "rawId.trim().takeIf(String::isNotEmpty)",
                        "internal fun normalizedLastDoneDate(rawDate: String?): String?",
                        "runCatching { LocalDate.parse(candidate) }.getOrNull()?.toString()",
                        "val normalizedTaskId = taskId.trim()",
                        "val normalizedCompletedTaskIds = normalizedCompletedTaskIds(completedTaskIds)",
                        "val safeLastDoneDate = normalizedLastDoneDate(lastDoneDate)",
                        "lastDoneDate = safeLastDoneDate",
                        "completedTaskIds = normalizedCompletedTaskIds + normalizedTaskId",
                    ),
                ),
                (
                    user_preferences_path,
                    (
                        "import ru.poryadok5.app.domain.normalizedCompletedTaskIds",
                        "import ru.poryadok5.app.domain.normalizedLastDoneDate",
                        "lastDoneDate = normalizedLastDoneDate(this[UserPreferencesKeys.LastDoneDate])",
                        "?.let(::normalizedCompletedTaskIds)",
                        "normalizedLastDoneDate(progress.lastDoneDate)?.let",
                        "this[UserPreferencesKeys.CompletedTaskIds] = normalizedCompletedTaskIds(progress.completedTaskIds)",
                    ),
                ),
                (
                    progress_test_path,
                    (
                        "blankCompletionDoesNotIncrementProgress",
                        "blankCompletionClearsMalformedStoredDate",
                        "completionTaskIdIsTrimmedBeforeStorage",
                        "existingCompletedTaskIdsAreTrimmedOnCompletion",
                        '"bad-date"',
                        '" home_002 "',
                    ),
                ),
                (
                    user_preferences_test_path,
                    (
                        "corruptedStoredProgressIsNormalizedForUi",
                        "storedLastDoneDateIsTrimmedForUi",
                        "writeProgressNormalizesLastDoneDateBeforeStorage",
                        "writeProgressRemovesMalformedLastDoneDate",
                        "writeProgressNormalizesInvalidProgressBeforeStorage",
                        '" 2026-05-27 "',
                        '"bad-date"',
                        '" home_001 "',
                        '" work_002 "',
                    ),
                ),
            ),
            forbidden_snippets=(
                (
                    progress_rules_path,
                    (
                        "completedTaskIds.filterTo(mutableSetOf(), String::isNotBlank)",
                        "completedTaskIds.filter(String::isNotBlank)",
                    ),
                ),
                (
                    user_preferences_path,
                    (
                        "progress.completedTaskIds.filterTo(mutableSetOf(), String::isNotBlank)",
                        "progress.completedTaskIds.filter(String::isNotBlank)",
                        "?.filterTo(mutableSetOf(), String::isNotBlank)",
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


def test_missing_normalizer_function_fails() -> None:
    broken = VALID_PROGRESS_RULES.replace(
        "internal fun normalizedCompletedTaskIds(ids: Set<String>): Set<String>",
        "internal fun cleanedCompletedTaskIds(ids: Set<String>): Set<String>",
    )
    assert_fails(failures_for(progress_rules=broken), "normalizedCompletedTaskIds")


def test_completion_task_id_without_trim_fails() -> None:
    broken = VALID_PROGRESS_RULES.replace(
        "val normalizedTaskId = taskId.trim()",
        "val normalizedTaskId = taskId",
    )
    assert_fails(failures_for(progress_rules=broken), "taskId.trim()")


def test_missing_last_done_date_normalizer_fails() -> None:
    broken = VALID_PROGRESS_RULES.replace(
        "internal fun normalizedLastDoneDate(rawDate: String?): String?",
        "internal fun cleanLastDoneDate(rawDate: String?): String?",
    )
    assert_fails(failures_for(progress_rules=broken), "normalizedLastDoneDate")


def test_preference_read_raw_last_done_date_fails() -> None:
    broken = VALID_USER_PREFERENCES.replace(
        "lastDoneDate = normalizedLastDoneDate(this[UserPreferencesKeys.LastDoneDate])",
        "lastDoneDate = this[UserPreferencesKeys.LastDoneDate]",
    )
    assert_fails(failures_for(user_preferences=broken), "normalizedLastDoneDate(this[UserPreferencesKeys.LastDoneDate])")


def test_preference_read_raw_blank_filter_fails() -> None:
    broken = VALID_USER_PREFERENCES.replace(
        "?.let(::normalizedCompletedTaskIds)",
        "?.filterTo(mutableSetOf(), String::isNotBlank)",
    )
    failures = failures_for(user_preferences=broken)
    assert_fails(failures, "normalizedCompletedTaskIds")
    assert_fails(failures, "forbidden blank-only id filter")


def test_missing_progress_whitespace_test_fails() -> None:
    broken = VALID_PROGRESS_TEST.replace("existingCompletedTaskIdsAreTrimmedOnCompletion", "existingIdsArePreserved")
    assert_fails(failures_for(progress_test=broken), "existingCompletedTaskIdsAreTrimmedOnCompletion")


def test_missing_malformed_date_test_fails() -> None:
    broken = VALID_PROGRESS_TEST.replace("blankCompletionClearsMalformedStoredDate", "blankCompletionKeepsDate")
    assert_fails(failures_for(progress_test=broken), "blankCompletionClearsMalformedStoredDate")


def test_missing_preference_write_whitespace_evidence_fails() -> None:
    broken = VALID_USER_PREFERENCES_TEST.replace('" work_002 "', '"work_002"')
    assert_fails(failures_for(user_preferences_test=broken), '" work_002 "')


def main() -> int:
    test_valid_fixture_passes()
    test_missing_normalizer_function_fails()
    test_completion_task_id_without_trim_fails()
    test_missing_last_done_date_normalizer_fails()
    test_preference_read_raw_last_done_date_fails()
    test_preference_read_raw_blank_filter_fails()
    test_missing_progress_whitespace_test_fails()
    test_missing_malformed_date_test_fails()
    test_missing_preference_write_whitespace_evidence_fails()
    print("PASS: progress persistence normalization checker self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
