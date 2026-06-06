#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN_ACTIVITY = ROOT / "app/src/main/java/ru/poryadok5/app/MainActivity.kt"
APP_GRADLE = ROOT / "app/build.gradle.kts"

REQUIRED_MAIN_SNIPPETS = (
    "import androidx.lifecycle.compose.collectAsStateWithLifecycle",
    "preferencesRepository.preferences.collectAsStateWithLifecycle(",
    "initialValue = null",
)

FORBIDDEN_MAIN_SNIPPETS = (
    ("import androidx.compose.runtime.collectAsState", "preferences Flow must be lifecycle-aware"),
    ("preferencesRepository.preferences.collectAsState(", "preferences Flow must be lifecycle-aware"),
)


def display_path(path: Path, root: Path = ROOT) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def lifecycle_state_collection_failures(
    main_activity: Path = MAIN_ACTIVITY,
    app_gradle: Path = APP_GRADLE,
) -> list[str]:
    failures: list[str] = []

    if not main_activity.exists():
        return [f"missing MainActivity file: {display_path(main_activity)}"]
    if not app_gradle.exists():
        return [f"missing Gradle file: {display_path(app_gradle)}"]

    main_source = main_activity.read_text(encoding="utf-8")
    gradle_source = app_gradle.read_text(encoding="utf-8")

    for snippet in REQUIRED_MAIN_SNIPPETS:
        if snippet not in main_source:
            failures.append(f"{display_path(main_activity)} is missing lifecycle state snippet: {snippet}")

    for snippet, reason in FORBIDDEN_MAIN_SNIPPETS:
        if snippet in main_source:
            failures.append(f"{display_path(main_activity)} contains forbidden snippet {snippet!r}: {reason}")

    if "androidx.lifecycle:lifecycle-runtime-compose" not in gradle_source:
        failures.append(f"{display_path(app_gradle)} must keep lifecycle-runtime-compose dependency")

    return failures


def main() -> int:
    failures = lifecycle_state_collection_failures()
    if failures:
        print("Lifecycle state collection check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: preferences Flow collection is lifecycle-aware")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
