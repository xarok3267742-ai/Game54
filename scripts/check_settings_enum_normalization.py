#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / "app/src/main/java/ru/poryadok5/app/domain/Models.kt"
MODELS_TEST = ROOT / "app/src/test/java/ru/poryadok5/app/ModelsTest.kt"
USER_PREFERENCES_TEST = ROOT / "app/src/test/java/ru/poryadok5/app/UserPreferencesRepositoryTest.kt"

REQUIRED_SNIPPETS: tuple[tuple[Path, tuple[str, ...]], ...] = (
    (
        MODELS,
        (
            "fun fromRaw(value: String): TaskArea",
            "val normalized = value.trim()",
            "it.name.equals(normalized, ignoreCase = true)",
            "fun fromRaw(value: String): EnergyLevel",
        ),
    ),
    (
        MODELS_TEST,
        (
            "taskAreaFromRawTrimsAndIgnoresCase",
            "energyLevelFromRawTrimsAndIgnoresCase",
            '" digital "',
            '" medium "',
            "taskAreaFromRawFallsBackToHomeForUnknownValues",
            "energyLevelFromRawFallsBackToLightForUnknownValues",
        ),
    ),
    (
        USER_PREFERENCES_TEST,
        (
            "storedPreferredAreaIsTrimmedForUi",
            'UserPreferencesKeys.PreferredArea to " digital "',
        ),
    ),
)

FORBIDDEN_SNIPPETS: tuple[tuple[Path, tuple[str, ...]], ...] = (
    (
        MODELS,
        (
            "it.name.equals(value, ignoreCase = true)",
        ),
    ),
)


def display_path(path: Path, root: Path = ROOT) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def settings_enum_normalization_failures(
    required_snippets: tuple[tuple[Path, tuple[str, ...]], ...] = REQUIRED_SNIPPETS,
    forbidden_snippets: tuple[tuple[Path, tuple[str, ...]], ...] = FORBIDDEN_SNIPPETS,
    root: Path = ROOT,
) -> list[str]:
    failures: list[str] = []

    for path, snippets in required_snippets:
        if not path.exists():
            failures.append(f"missing settings enum normalization evidence file: {display_path(path, root)}")
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
                failures.append(f"{display_path(path, root)} contains raw enum value matching: {snippet}")

    return failures


def main() -> int:
    failures = settings_enum_normalization_failures()
    if failures:
        print("Settings enum normalization check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: settings enum raw values are trimmed before fallback")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
