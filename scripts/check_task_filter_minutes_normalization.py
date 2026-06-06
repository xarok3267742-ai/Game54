#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / "app/src/main/java/ru/poryadok5/app/domain/Models.kt"
ENGINE = ROOT / "app/src/main/java/ru/poryadok5/app/domain/PoryadokEngine.kt"
APP = ROOT / "app/src/main/java/ru/poryadok5/app/ui/PoryadokApp.kt"
MODELS_TEST = ROOT / "app/src/test/java/ru/poryadok5/app/ModelsTest.kt"
ENGINE_TEST = ROOT / "app/src/test/java/ru/poryadok5/app/PoryadokEngineTest.kt"

REQUIRED_SNIPPETS: tuple[tuple[Path, tuple[str, ...]], ...] = (
    (
        MODELS,
        (
            "val SupportedTaskMinutes = setOf(3, 5, 10)",
            "fun normalizedTaskMinutes(value: Int): Int",
            "return if (value in SupportedTaskMinutes) value else 5",
        ),
    ),
    (
        ENGINE,
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
        APP,
        (
            "import ru.poryadok5.app.domain.SupportedTaskMinutes",
            "import ru.poryadok5.app.domain.normalizedTaskMinutes",
            "val selectedDuration = normalizedTaskMinutes(selectedMinutes)",
            "TaskFilter(selectedArea, selectedEnergy, selectedDuration)",
            "SupportedTaskMinutes.forEach",
        ),
    ),
    (
        MODELS_TEST,
        (
            "taskMinutesNormalizeToAllowedValues",
            "SupportedTaskMinutes",
            "normalizedTaskMinutes(7)",
            "normalizedTaskMinutes(-1)",
        ),
    ),
    (
        ENGINE_TEST,
        (
            "suggestTaskNormalizesUnsupportedFilterMinutes",
            "TaskFilter(TaskArea.Home, EnergyLevel.Active, 7)",
            '"home_active_5"',
        ),
    ),
)

FORBIDDEN_SNIPPETS: tuple[tuple[Path, tuple[str, ...]], ...] = (
    (
        ENGINE,
        (
            "it.area == filter.area",
            "it.energy == filter.energy",
            "it.minutes == filter.minutes",
            "+ filter.minutes",
            "\n            filter.minutes",
        ),
    ),
    (
        APP,
        (
            "TaskFilter(selectedArea, selectedEnergy, selectedMinutes)",
            "listOf(3, 5, 10).forEach",
        ),
    ),
)


def display_path(path: Path, root: Path = ROOT) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def task_filter_minutes_normalization_failures(
    required_snippets: tuple[tuple[Path, tuple[str, ...]], ...] = REQUIRED_SNIPPETS,
    forbidden_snippets: tuple[tuple[Path, tuple[str, ...]], ...] = FORBIDDEN_SNIPPETS,
    root: Path = ROOT,
) -> list[str]:
    failures: list[str] = []

    for path, snippets in required_snippets:
        if not path.exists():
            failures.append(f"missing task-filter minute evidence file: {display_path(path, root)}")
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
                failures.append(f"{display_path(path, root)} contains raw task-filter minutes usage: {snippet}")

    return failures


def main() -> int:
    failures = task_filter_minutes_normalization_failures()
    if failures:
        print("Task filter minute normalization check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: task filter minutes are normalized for UI and engine suggestions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
