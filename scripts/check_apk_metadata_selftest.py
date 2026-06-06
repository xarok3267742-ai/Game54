#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "scripts/check_apk_metadata.py"

spec = importlib.util.spec_from_file_location("apk_metadata_checker", CHECKER_PATH)
assert spec is not None and spec.loader is not None
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

VALID_BADGING = """package: name='ru.poryadok5.app' versionCode='1' versionName='1.0.0-rc1' compileSdkVersion='35'
sdkVersion:'26'
targetSdkVersion:'35'
application-label:'Порядок 5'
"""
CUSTOM_IDENTITY = {
    "appId": "com.example.custom",
    "versionCode": 7,
    "versionName": "2.3.0",
}


def assert_equal(actual: object, expected: object) -> None:
    assert actual == expected, f"expected {expected!r}, got {actual!r}"


def assert_failure_contains(failures: list[str], expected: str) -> None:
    assert any(expected in failure for failure in failures), failures


def test_valid_badging_passes() -> None:
    metadata = checker.parse_badging(VALID_BADGING)
    assert_equal(metadata["package"], "ru.poryadok5.app")
    assert_equal(metadata["versionCode"], "1")
    assert_equal(metadata["versionName"], "1.0.0-rc1")
    assert_equal(metadata["compileSdkVersion"], "35")
    assert_equal(metadata["sdkVersion"], "26")
    assert_equal(metadata["targetSdkVersion"], "35")
    assert_equal(metadata["application-label"], "Порядок 5")
    assert_equal(checker.metadata_failures(metadata), [])


def test_metadata_uses_gradle_release_identity() -> None:
    custom_badging = (
        VALID_BADGING.replace("ru.poryadok5.app", "com.example.custom")
        .replace("versionCode='1'", "versionCode='7'")
        .replace("versionName='1.0.0-rc1'", "versionName='2.3.0'")
    )
    assert_equal(checker.metadata_failures(checker.parse_badging(custom_badging), CUSTOM_IDENTITY), [])
    assert_failure_contains(checker.metadata_failures(checker.parse_badging(VALID_BADGING), CUSTOM_IDENTITY), "package:")


def test_wrong_package_fails() -> None:
    metadata = checker.parse_badging(VALID_BADGING.replace("ru.poryadok5.app", "com.example.other"))
    assert_failure_contains(checker.metadata_failures(metadata), "package:")


def test_wrong_version_name_fails() -> None:
    metadata = checker.parse_badging(VALID_BADGING.replace("versionName='1.0.0-rc1'", "versionName='1.0.0'"))
    assert_failure_contains(checker.metadata_failures(metadata), "versionName:")


def test_wrong_target_sdk_fails() -> None:
    metadata = checker.parse_badging(VALID_BADGING.replace("targetSdkVersion:'35'", "targetSdkVersion:'34'"))
    assert_failure_contains(checker.metadata_failures(metadata), "targetSdkVersion:")


def test_missing_application_label_fails() -> None:
    metadata = checker.parse_badging(VALID_BADGING.replace("application-label:'Порядок 5'\n", ""))
    assert_failure_contains(checker.metadata_failures(metadata), "application-label:")


def main() -> int:
    tests = [
        test_valid_badging_passes,
        test_metadata_uses_gradle_release_identity,
        test_wrong_package_fails,
        test_wrong_version_name_fails,
        test_wrong_target_sdk_fails,
        test_missing_application_label_fails,
    ]
    for test in tests:
        test()
    print("PASS: APK metadata checker self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
