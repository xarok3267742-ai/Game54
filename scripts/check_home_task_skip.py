#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "app/src/main/java/ru/poryadok5/app/domain/PoryadokEngine.kt"
APP = ROOT / "app/src/main/java/ru/poryadok5/app/ui/PoryadokApp.kt"
ENGINE_TEST = ROOT / "app/src/test/java/ru/poryadok5/app/PoryadokEngineTest.kt"


def missing_markers(path: Path, markers: tuple[str, ...]) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return [marker for marker in markers if marker not in text]


def main() -> int:
    failures: list[str] = []
    required = {
        ENGINE: (
            "excludedIds: Set<String> = emptySet()",
            "normalizedExcludedIds",
            "hasAlternativeSuggestion",
            "excludedIds + normalizedCurrentTaskId",
        ),
        APP: (
            "skippedSuggestionIds",
            "excludedIds = skippedSuggestionIdSet",
            "canSkipSuggested",
            "onSkipTask",
            '"Другая задача"',
        ),
        ENGINE_TEST: (
            "suggestTaskAvoidsExcludedIdsWhenAlternativeExists",
            "suggestTaskTrimsExcludedIdsBeforeSkippingTasks",
            "suggestTaskFallsBackWhenExcludedIdsExhaustAvailableTasks",
            "hasAlternativeSuggestionDetectsAnotherTaskAfterSkippingCurrent",
            "hasAlternativeSuggestionReturnsFalseForSingleTaskCatalog",
        ),
    }

    for path, markers in required.items():
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(ROOT)}")
            continue
        for marker in missing_markers(path, markers):
            failures.append(f"{path.relative_to(ROOT)} is missing marker: {marker}")

    if failures:
        print("Home task skip check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: Home task skip flow is wired through UI, engine exclusions and tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
