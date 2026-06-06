#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "scripts/check_stack_versions.py"

spec = importlib.util.spec_from_file_location("stack_versions_checker", CHECKER_PATH)
assert spec is not None and spec.loader is not None
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def assert_equal(actual: object, expected: object) -> None:
    assert actual == expected, f"expected {expected!r}, got {actual!r}"


def assert_failure_contains(failures: list[str], expected: str) -> None:
    assert any(expected in failure for failure in failures), failures


def valid_inputs() -> dict[str, str]:
    return {
        "wrapper": "distributionUrl=https\\://services.gradle.org/distributions/gradle-8.11.1-bin.zip\n",
        "root_gradle": """
plugins {
    id("com.android.application") version "8.9.1" apply false
    id("org.jetbrains.kotlin.android") version "2.0.21" apply false
    id("org.jetbrains.kotlin.plugin.compose") version "2.0.21" apply false
}
""",
        "app_gradle": """
android {
    namespace = "ru.poryadok5.app"
    compileSdk = 35

    defaultConfig {
        applicationId = "ru.poryadok5.app"
        minSdk = 26
        targetSdk = 35
        versionCode = 1
        versionName = "1.0.0-rc1"
    }
}

dependencies {
    implementation(platform("androidx.compose:compose-bom:2026.04.01"))
    implementation("androidx.datastore:datastore-preferences:1.1.7")
}
""",
        "tech_stack": "AGP 8.9.1 Kotlin 2.0.21 Compose BOM 2026.04.01 minSdk 26 compileSdk 35 targetSdk 35",
        "tech_decision": "Android Gradle Plugin 8.9.1 Kotlin 2.0.21 Compose BOM 2026.04.01 SDK 26 35 35",
    }


def failures_for(overrides: dict[str, str]) -> list[str]:
    values = valid_inputs()
    values.update(overrides)
    return checker.stack_version_failures(**values)


def test_valid_stack_passes() -> None:
    assert_equal(failures_for({}), [])


def test_wrong_gradle_wrapper_fails() -> None:
    failures = failures_for({"wrapper": "distributionUrl=https\\://services.gradle.org/distributions/gradle-8.10-bin.zip\n"})
    assert_failure_contains(failures, "Gradle wrapper: expected 8.11.1")


def test_wrong_agp_fails() -> None:
    values = valid_inputs()
    values["root_gradle"] = values["root_gradle"].replace('version "8.9.1"', 'version "8.8.0"', 1)
    assert_failure_contains(checker.stack_version_failures(**values), "Android Gradle Plugin")


def test_missing_kotlin_compose_plugin_fails() -> None:
    values = valid_inputs()
    values["root_gradle"] = values["root_gradle"].replace('    id("org.jetbrains.kotlin.plugin.compose") version "2.0.21" apply false\n', "")
    assert_failure_contains(checker.stack_version_failures(**values), "Kotlin Compose plugin: value not found")


def test_wrong_application_id_fails() -> None:
    values = valid_inputs()
    values["app_gradle"] = values["app_gradle"].replace('applicationId = "ru.poryadok5.app"', 'applicationId = "com.example.other"')
    assert_failure_contains(checker.stack_version_failures(**values), "applicationId")


def test_missing_target_sdk_fails_when_compile_sdk_35() -> None:
    values = valid_inputs()
    values["app_gradle"] = values["app_gradle"].replace("        targetSdk = 35\n", "")
    failures = checker.stack_version_failures(**values)
    assert_failure_contains(failures, "targetSdk: value not found")
    assert_failure_contains(failures, "compileSdk is 35 but targetSdk is not explicitly 35")


def test_wrong_compose_bom_fails() -> None:
    values = valid_inputs()
    values["app_gradle"] = values["app_gradle"].replace("compose-bom:2026.04.01", "compose-bom:2025.12.00")
    assert_failure_contains(checker.stack_version_failures(**values), "Compose BOM")


def test_missing_datastore_dependency_fails() -> None:
    values = valid_inputs()
    values["app_gradle"] = values["app_gradle"].replace('    implementation("androidx.datastore:datastore-preferences:1.1.7")\n', "")
    assert_failure_contains(checker.stack_version_failures(**values), "DataStore Preferences")


def test_docs_missing_stack_marker_fails() -> None:
    values = valid_inputs()
    values["tech_stack"] = values["tech_stack"].replace("2026.04.01", "missing")
    assert_failure_contains(checker.stack_version_failures(**values), "docs/tech_stack.md: missing 2026.04.01")


def main() -> int:
    tests = [
        test_valid_stack_passes,
        test_wrong_gradle_wrapper_fails,
        test_wrong_agp_fails,
        test_missing_kotlin_compose_plugin_fails,
        test_wrong_application_id_fails,
        test_missing_target_sdk_fails_when_compile_sdk_35,
        test_wrong_compose_bom_fails,
        test_missing_datastore_dependency_fails,
        test_docs_missing_stack_marker_fails,
    ]
    for test in tests:
        test()
    print("PASS: stack versions checker self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
