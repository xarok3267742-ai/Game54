#!/usr/bin/env python3
from __future__ import annotations

import tempfile
from pathlib import Path

from check_lifecycle_state_collection import lifecycle_state_collection_failures

VALID_MAIN = """
package ru.poryadok5.app

import androidx.lifecycle.compose.collectAsStateWithLifecycle

class MainActivity {
    fun render() {
        val preferences = preferencesRepository.preferences.collectAsStateWithLifecycle(
            initialValue = null,
        )
    }
}
"""

VALID_GRADLE = """
dependencies {
    implementation("androidx.lifecycle:lifecycle-runtime-compose:2.9.2")
}
"""


def failures_for(main_source: str = VALID_MAIN, gradle_source: str = VALID_GRADLE) -> list[str]:
    with tempfile.TemporaryDirectory(prefix="poryadok5-lifecycle-state.") as tmp_dir:
        root = Path(tmp_dir)
        main = root / "MainActivity.kt"
        gradle = root / "build.gradle.kts"
        main.write_text(main_source, encoding="utf-8")
        gradle.write_text(gradle_source, encoding="utf-8")
        return lifecycle_state_collection_failures(main, gradle)


def assert_passes(failures: list[str]) -> None:
    assert failures == [], failures


def assert_fails(failures: list[str], expected: str) -> None:
    assert any(expected in failure for failure in failures), failures


def test_valid_fixture_passes() -> None:
    assert_passes(failures_for())


def test_plain_collect_as_state_import_fails() -> None:
    broken = VALID_MAIN.replace(
        "import androidx.lifecycle.compose.collectAsStateWithLifecycle",
        "import androidx.compose.runtime.collectAsState",
    )
    assert_fails(failures_for(main_source=broken), "androidx.compose.runtime.collectAsState")


def test_plain_collect_as_state_call_fails() -> None:
    broken = VALID_MAIN.replace(
        "preferencesRepository.preferences.collectAsStateWithLifecycle(",
        "preferencesRepository.preferences.collectAsState(",
    )
    assert_fails(failures_for(main_source=broken), "collectAsStateWithLifecycle")
    assert_fails(failures_for(main_source=broken), "preferencesRepository.preferences.collectAsState(")


def test_missing_lifecycle_dependency_fails() -> None:
    assert_fails(failures_for(gradle_source="dependencies {}\n"), "lifecycle-runtime-compose")


def main() -> int:
    test_valid_fixture_passes()
    test_plain_collect_as_state_import_fails()
    test_plain_collect_as_state_call_fails()
    test_missing_lifecycle_dependency_fails()
    print("PASS: lifecycle state collection checker self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
