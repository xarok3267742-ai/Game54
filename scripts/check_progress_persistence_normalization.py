#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROGRESS_RULES = ROOT / "app/src/main/java/ru/poryadok5/app/domain/ProgressRules.kt"
USER_PREFERENCES = ROOT / "app/src/main/java/ru/poryadok5/app/data/UserPreferencesRepository.kt"
PROGRESS_TEST = ROOT / "app/src/test/java/ru/poryadok5/app/ProgressRulesTest.kt"
USER_PREFERENCES_TEST = ROOT / "app/src/test/java/ru/poryadok5/app/UserPreferencesRepositoryTest.kt"

REQUIRED_SNIPPETS: tuple[tuple[Path, tuple[str, ...]], ...] = (
    (
        PROGRESS_RULES,
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
        USER_PREFERENCES,
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
        PROGRESS_TEST,
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
        USER_PREFERENCES_TEST,
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
)

FORBIDDEN_SNIPPETS: tuple[tuple[Path, tuple[str, ...]], ...] = (
    (
        PROGRESS_RULES,
        (
            "completedTaskIds.filterTo(mutableSetOf(), String::isNotBlank)",
            "completedTaskIds.filter(String::isNotBlank)",
        ),
    ),
    (
        USER_PREFERENCES,
        (
            "progress.completedTaskIds.filterTo(mutableSetOf(), String::isNotBlank)",
            "progress.completedTaskIds.filter(String::isNotBlank)",
            "?.filterTo(mutableSetOf(), String::isNotBlank)",
        ),
    ),
)


def display_path(path: Path, root: Path = ROOT) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def progress_persistence_normalization_failures(
    required_snippets: tuple[tuple[Path, tuple[str, ...]], ...] = REQUIRED_SNIPPETS,
    forbidden_snippets: tuple[tuple[Path, tuple[str, ...]], ...] = FORBIDDEN_SNIPPETS,
    root: Path = ROOT,
) -> list[str]:
    failures: list[str] = []

    for path, snippets in required_snippets:
        if not path.exists():
            failures.append(f"missing progress persistence evidence file: {display_path(path, root)}")
            continue
        text = path.read_text(encoding="utf-8")
        for snippet in snippets:
            if snippet not in text:
                failures.append(f"{display_path(path, root)} is missing required snippet: {snippet}")

    for path, snippets in forbidden_snippets:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for snippet in snippets:
            if snippet in text:
                failures.append(f"{display_path(path, root)} contains forbidden blank-only id filter: {snippet}")

    return failures


def main() -> int:
    failures = progress_persistence_normalization_failures()
    if failures:
        print("Progress persistence normalization check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: progress persistence normalizes completed-task ids and last-done dates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
