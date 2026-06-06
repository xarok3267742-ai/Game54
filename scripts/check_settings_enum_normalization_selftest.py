#!/usr/bin/env python3
from __future__ import annotations

import tempfile
from pathlib import Path

from check_settings_enum_normalization import settings_enum_normalization_failures

VALID_MODELS = """
enum class TaskArea {
    Home, Digital;

    companion object {
        fun fromRaw(value: String): TaskArea {
            val normalized = value.trim()
            return entries.firstOrNull { it.name.equals(normalized, ignoreCase = true) } ?: Home
        }
    }
}

enum class EnergyLevel {
    Light, Medium;

    companion object {
        fun fromRaw(value: String): EnergyLevel {
            val normalized = value.trim()
            return entries.firstOrNull { it.name.equals(normalized, ignoreCase = true) } ?: Light
        }
    }
}
"""

VALID_MODELS_TEST = """
class ModelsTest {
    fun taskAreaFromRawTrimsAndIgnoresCase() {
        TaskArea.fromRaw(" digital ")
    }
    fun taskAreaFromRawFallsBackToHomeForUnknownValues() {
        TaskArea.fromRaw("ArchivedArea")
    }
    fun energyLevelFromRawTrimsAndIgnoresCase() {
        EnergyLevel.fromRaw(" medium ")
    }
    fun energyLevelFromRawFallsBackToLightForUnknownValues() {
        EnergyLevel.fromRaw("ArchivedEnergy")
    }
}
"""

VALID_USER_PREFERENCES_TEST = """
class UserPreferencesRepositoryTest {
    fun storedPreferredAreaIsTrimmedForUi() {
        preferencesOf(UserPreferencesKeys.PreferredArea to " digital ")
    }
}
"""


def failures_for(
    models_source: str = VALID_MODELS,
    models_test_source: str = VALID_MODELS_TEST,
    user_preferences_test_source: str = VALID_USER_PREFERENCES_TEST,
) -> list[str]:
    with tempfile.TemporaryDirectory(prefix="poryadok5-settings-enum.") as tmp_dir:
        root = Path(tmp_dir)
        models = root / "Models.kt"
        models_test = root / "ModelsTest.kt"
        user_preferences_test = root / "UserPreferencesRepositoryTest.kt"
        models.write_text(models_source, encoding="utf-8")
        models_test.write_text(models_test_source, encoding="utf-8")
        user_preferences_test.write_text(user_preferences_test_source, encoding="utf-8")
        return settings_enum_normalization_failures(
            required_snippets=(
                (
                    models,
                    (
                        "fun fromRaw(value: String): TaskArea",
                        "val normalized = value.trim()",
                        "it.name.equals(normalized, ignoreCase = true)",
                        "fun fromRaw(value: String): EnergyLevel",
                    ),
                ),
                (
                    models_test,
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
                    user_preferences_test,
                    (
                        "storedPreferredAreaIsTrimmedForUi",
                        'UserPreferencesKeys.PreferredArea to " digital "',
                    ),
                ),
            ),
            forbidden_snippets=(
                (
                    models,
                    (
                        "it.name.equals(value, ignoreCase = true)",
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


def test_missing_trim_fails() -> None:
    broken = VALID_MODELS.replace("val normalized = value.trim()", "val normalized = value")
    assert_fails(failures_for(models_source=broken), "value.trim()")


def test_raw_value_matching_fails() -> None:
    broken = VALID_MODELS.replace("it.name.equals(normalized, ignoreCase = true)", "it.name.equals(value, ignoreCase = true)")
    failures = failures_for(models_source=broken)
    assert_fails(failures, "normalized")
    assert_fails(failures, "raw enum value matching")


def test_missing_task_area_trim_test_fails() -> None:
    broken = VALID_MODELS_TEST.replace("taskAreaFromRawTrimsAndIgnoresCase", "taskAreaFromRawIgnoresCase")
    assert_fails(failures_for(models_test_source=broken), "taskAreaFromRawTrimsAndIgnoresCase")


def test_missing_preference_trim_test_fails() -> None:
    broken = VALID_USER_PREFERENCES_TEST.replace('" digital "', '"digital"')
    assert_fails(failures_for(user_preferences_test_source=broken), '" digital "')


def main() -> int:
    test_valid_fixture_passes()
    test_missing_trim_fails()
    test_raw_value_matching_fails()
    test_missing_task_area_trim_test_fails()
    test_missing_preference_trim_test_fails()
    print("PASS: settings enum normalization checker self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
