#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "scripts/check_aab_universal_apk.py"

spec = importlib.util.spec_from_file_location("aab_universal_apk_checker", CHECKER_PATH)
assert spec is not None and spec.loader is not None
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

ALLOWED = checker.allowed_app_permission()

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


def failures_for_badging(output: str) -> list[str]:
    metadata, permissions = checker.parse_badging(output)
    return checker.metadata_failures(metadata, permissions)


def write_apks(path: Path, entries: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        for name, content in entries.items():
            archive.writestr(name, content)


def test_valid_badging_passes() -> None:
    metadata, permissions = checker.parse_badging(VALID_BADGING)
    assert_equal(metadata["package"], "ru.poryadok5.app")
    assert_equal(metadata["versionCode"], "1")
    assert_equal(metadata["versionName"], "1.0.0-rc1")
    assert_equal(metadata["compileSdkVersion"], "35")
    assert_equal(metadata["sdkVersion"], "26")
    assert_equal(metadata["targetSdkVersion"], "35")
    assert_equal(metadata["application-label"], "Порядок 5")
    assert_equal(permissions, [])
    assert_equal(checker.metadata_failures(metadata, permissions), [])


def test_allowed_permission_passes() -> None:
    badging = VALID_BADGING + f"uses-permission: name='{ALLOWED}'\n"
    assert_equal(failures_for_badging(badging), [])


def test_metadata_uses_gradle_release_identity() -> None:
    custom_badging = (
        VALID_BADGING.replace("ru.poryadok5.app", "com.example.custom")
        .replace("versionCode='1'", "versionCode='7'")
        .replace("versionName='1.0.0-rc1'", "versionName='2.3.0'")
        + "uses-permission: name='com.example.custom.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION'\n"
    )
    metadata, permissions = checker.parse_badging(custom_badging)

    assert_equal(checker.metadata_failures(metadata, permissions, CUSTOM_IDENTITY), [])
    assert_failure_contains(
        checker.metadata_failures(*checker.parse_badging(VALID_BADGING), CUSTOM_IDENTITY),
        "package:",
    )


def test_wrong_target_sdk_fails() -> None:
    badging = VALID_BADGING.replace("targetSdkVersion:'35'", "targetSdkVersion:'34'")
    assert_failure_contains(failures_for_badging(badging), "targetSdkVersion:")


def test_missing_application_label_fails() -> None:
    badging = VALID_BADGING.replace("application-label:'Порядок 5'\n", "")
    assert_failure_contains(failures_for_badging(badging), "application-label:")


def test_disallowed_platform_permission_fails() -> None:
    badging = VALID_BADGING + "uses-permission: name='android.permission.INTERNET'\n"
    assert_failure_contains(failures_for_badging(badging), "disallowed uses-permission")


def test_valid_apks_archive_extracts_universal_apk() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        temp_dir = Path(tmp)
        apks = temp_dir / "valid.apks"
        write_apks(apks, {"toc.pb": b"toc", "universal.apk": b"apk-bytes"})

        extracted, failures = checker.extract_universal_apk(apks, temp_dir / "out")

        assert_equal(failures, [])
        assert extracted is not None
        assert_equal(extracted.read_bytes(), b"apk-bytes")


def test_missing_toc_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        temp_dir = Path(tmp)
        apks = temp_dir / "missing-toc.apks"
        write_apks(apks, {"universal.apk": b"apk-bytes"})

        extracted, failures = checker.extract_universal_apk(apks, temp_dir / "out")

        assert_equal(extracted, None)
        assert_failure_contains(failures, "toc.pb")


def test_missing_universal_apk_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        temp_dir = Path(tmp)
        apks = temp_dir / "missing-universal.apks"
        write_apks(apks, {"toc.pb": b"toc"})

        extracted, failures = checker.extract_universal_apk(apks, temp_dir / "out")

        assert_equal(extracted, None)
        assert_failure_contains(failures, "universal.apk")


def test_empty_universal_apk_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        temp_dir = Path(tmp)
        apks = temp_dir / "empty-universal.apks"
        write_apks(apks, {"toc.pb": b"toc", "universal.apk": b""})

        extracted, failures = checker.extract_universal_apk(apks, temp_dir / "out")

        assert_equal(extracted, None)
        assert_failure_contains(failures, "universal.apk is empty")


def test_bad_zip_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        temp_dir = Path(tmp)
        apks = temp_dir / "bad.apks"
        apks.write_bytes(b"not a zip")

        extracted, failures = checker.extract_universal_apk(apks, temp_dir / "out")

        assert_equal(extracted, None)
        assert_failure_contains(failures, "valid ZIP")


def main() -> int:
    tests = [
        test_valid_badging_passes,
        test_allowed_permission_passes,
        test_metadata_uses_gradle_release_identity,
        test_wrong_target_sdk_fails,
        test_missing_application_label_fails,
        test_disallowed_platform_permission_fails,
        test_valid_apks_archive_extracts_universal_apk,
        test_missing_toc_fails,
        test_missing_universal_apk_fails,
        test_empty_universal_apk_fails,
        test_bad_zip_fails,
    ]
    for test in tests:
        test()
    print("PASS: AAB universal APK checker self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
