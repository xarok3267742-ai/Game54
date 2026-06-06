#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "scripts/check_aab_metadata.py"

spec = importlib.util.spec_from_file_location("aab_metadata_checker", CHECKER_PATH)
assert spec is not None and spec.loader is not None
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

ANDROID_NS = "http://schemas.android.com/apk/res/android"
ANDROID_ATTR = checker.ANDROID_NS
ALLOWED = checker.allowed_app_permission()
CUSTOM_IDENTITY = {
    "appId": "com.example.custom",
    "versionCode": 7,
    "versionName": "2.3.0",
}

VALID_MANIFEST = f"""<manifest xmlns:android="{ANDROID_NS}"
    package="ru.poryadok5.app"
    android:versionCode="1"
    android:versionName="1.0.0-rc1"
    android:compileSdkVersion="35">
    <uses-sdk android:minSdkVersion="26" android:targetSdkVersion="35" />
    <application android:label="@string/app_name" />
</manifest>
"""


def assert_equal(actual: object, expected: object) -> None:
    assert actual == expected, f"expected {expected!r}, got {actual!r}"


def assert_failure_contains(failures: list[str], expected: str) -> None:
    assert any(expected in failure for failure in failures), failures


def failures_for(manifest_xml: str) -> list[str]:
    metadata, permissions = checker.metadata_from_manifest_xml(manifest_xml)
    return checker.metadata_failures(metadata, permissions)


def test_valid_manifest_passes() -> None:
    metadata, permissions = checker.metadata_from_manifest_xml(VALID_MANIFEST)
    assert_equal(metadata["package"], "ru.poryadok5.app")
    assert_equal(metadata[f"{ANDROID_ATTR}versionCode"], "1")
    assert_equal(metadata[f"{ANDROID_ATTR}versionName"], "1.0.0-rc1")
    assert_equal(metadata[f"{ANDROID_ATTR}compileSdkVersion"], "35")
    assert_equal(metadata["minSdkVersion"], "26")
    assert_equal(metadata["targetSdkVersion"], "35")
    assert_equal(metadata["applicationLabel"], "@string/app_name")
    assert_equal(permissions, [])
    assert_equal(checker.metadata_failures(metadata, permissions), [])


def test_allowed_permission_passes() -> None:
    manifest = VALID_MANIFEST.replace(
        "<uses-sdk",
        f'<uses-permission android:name="{ALLOWED}" />\n    <uses-sdk',
    )
    assert_equal(failures_for(manifest), [])


def test_metadata_uses_gradle_release_identity() -> None:
    manifest = (
        VALID_MANIFEST.replace("ru.poryadok5.app", "com.example.custom", 1)
        .replace('android:versionCode="1"', 'android:versionCode="7"')
        .replace('android:versionName="1.0.0-rc1"', 'android:versionName="2.3.0"')
    )
    metadata, permissions = checker.metadata_from_manifest_xml(manifest)

    assert_equal(checker.metadata_failures(metadata, permissions, CUSTOM_IDENTITY), [])
    assert_failure_contains(
        checker.metadata_failures(*checker.metadata_from_manifest_xml(VALID_MANIFEST), CUSTOM_IDENTITY),
        "package:",
    )


def test_wrong_package_fails() -> None:
    manifest = VALID_MANIFEST.replace("ru.poryadok5.app", "com.example.other", 1)
    assert_failure_contains(failures_for(manifest), "package:")


def test_wrong_target_sdk_fails() -> None:
    manifest = VALID_MANIFEST.replace('android:targetSdkVersion="35"', 'android:targetSdkVersion="34"')
    assert_failure_contains(failures_for(manifest), "targetSdkVersion:")


def test_wrong_application_label_fails() -> None:
    manifest = VALID_MANIFEST.replace('@string/app_name', '@string/other_name')
    assert_failure_contains(failures_for(manifest), "applicationLabel:")


def test_disallowed_platform_permission_fails() -> None:
    manifest = VALID_MANIFEST.replace(
        "<uses-sdk",
        '<uses-permission android:name="android.permission.INTERNET" />\n    <uses-sdk',
    )
    assert_failure_contains(failures_for(manifest), "disallowed uses-permission")


def test_missing_uses_sdk_fails() -> None:
    manifest = VALID_MANIFEST.replace(
        '    <uses-sdk android:minSdkVersion="26" android:targetSdkVersion="35" />\n',
        "",
    )
    failures = failures_for(manifest)
    assert_failure_contains(failures, "minSdkVersion:")
    assert_failure_contains(failures, "targetSdkVersion:")


def main() -> int:
    tests = [
        test_valid_manifest_passes,
        test_allowed_permission_passes,
        test_metadata_uses_gradle_release_identity,
        test_wrong_package_fails,
        test_wrong_target_sdk_fails,
        test_wrong_application_label_fails,
        test_disallowed_platform_permission_fails,
        test_missing_uses_sdk_fails,
    ]
    for test in tests:
        test()
    print("PASS: AAB metadata checker self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
