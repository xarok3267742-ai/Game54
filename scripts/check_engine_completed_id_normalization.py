#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "app/src/main/java/ru/poryadok5/app/domain/PoryadokEngine.kt"
ENGINE_TEST = ROOT / "app/src/test/java/ru/poryadok5/app/PoryadokEngineTest.kt"

REQUIRED_SNIPPETS: tuple[tuple[Path, tuple[str, ...]], ...] = (
    (
        ENGINE,
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
        ENGINE_TEST,
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
)

FORBIDDEN_SNIPPETS: tuple[tuple[Path, tuple[str, ...]], ...] = (
    (
        ENGINE,
        (
            "filterNot { it.id in completedIds }",
            "completedIds.count { it in taskIds }",
            "it.id in completedIds",
            "it.id !in completedIds",
            "suggestTask(filter, completedIds + completedTaskId, day = day)",
        ),
    ),
)


def display_path(path: Path, root: Path = ROOT) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def engine_completed_id_normalization_failures(
    required_snippets: tuple[tuple[Path, tuple[str, ...]], ...] = REQUIRED_SNIPPETS,
    forbidden_snippets: tuple[tuple[Path, tuple[str, ...]], ...] = FORBIDDEN_SNIPPETS,
    root: Path = ROOT,
) -> list[str]:
    failures: list[str] = []

    for path, snippets in required_snippets:
        if not path.exists():
            failures.append(f"missing engine completed-id evidence file: {display_path(path, root)}")
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
                failures.append(f"{display_path(path, root)} contains raw completed-id usage: {snippet}")

    return failures


def main() -> int:
    failures = engine_completed_id_normalization_failures()
    if failures:
        print("Engine completed-id normalization check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: engine normalizes completed ids before suggestions and progress counts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
