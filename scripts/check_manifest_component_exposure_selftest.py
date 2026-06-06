#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "scripts/check_manifest_component_exposure.py"

spec = importlib.util.spec_from_file_location("manifest_exposure_checker", CHECKER_PATH)
assert spec is not None and spec.loader is not None
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

PACKAGE = "ru.poryadok5.app"
CUSTOM_PACKAGE = "com.example.custom"

VALID_SOURCE_MANIFEST = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <application android:allowBackup="false">
        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
"""

VALID_RELEASE_MANIFEST = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="ru.poryadok5.app">
    <application android:allowBackup="false">
        <activity android:name="ru.poryadok5.app.MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
        <provider android:name="androidx.startup.InitializationProvider" android:exported="false" />
        <receiver
            android:name="androidx.profileinstaller.ProfileInstallReceiver"
            android:exported="true"
            android:permission="android.permission.DUMP">
            <intent-filter>
                <action android:name="androidx.profileinstaller.action.INSTALL_PROFILE" />
            </intent-filter>
            <intent-filter>
                <action android:name="androidx.profileinstaller.action.SKIP_FILE" />
            </intent-filter>
            <intent-filter>
                <action android:name="androidx.profileinstaller.action.SAVE_PROFILE" />
            </intent-filter>
            <intent-filter>
                <action android:name="androidx.profileinstaller.action.BENCHMARK_OPERATION" />
            </intent-filter>
        </receiver>
    </application>
</manifest>
"""


def assert_passes(failures: list[str]) -> None:
    assert failures == [], failures


def assert_fails(failures: list[str], expected: str) -> None:
    assert any(expected in failure for failure in failures), failures


def test_valid_source_passes() -> None:
    assert_passes(checker.validate_source_manifest(VALID_SOURCE_MANIFEST, PACKAGE))


def test_valid_release_passes() -> None:
    assert_passes(checker.validate_release_manifest(VALID_RELEASE_MANIFEST, PACKAGE))


def test_main_activity_uses_gradle_release_identity() -> None:
    custom_release = VALID_RELEASE_MANIFEST.replace(PACKAGE, CUSTOM_PACKAGE)

    assert_passes(checker.validate_source_manifest(VALID_SOURCE_MANIFEST, CUSTOM_PACKAGE))
    assert_passes(checker.validate_release_manifest(custom_release, CUSTOM_PACKAGE))
    assert_fails(checker.validate_release_manifest(VALID_RELEASE_MANIFEST, CUSTOM_PACKAGE), "must include exactly one")


def test_source_permission_fails() -> None:
    xml = VALID_SOURCE_MANIFEST.replace(
        "<application",
        '<uses-permission android:name="android.permission.INTERNET" />\n    <application',
    )
    assert_fails(checker.validate_source_manifest(xml, PACKAGE), "must not request permission")


def test_release_unexpected_activity_fails() -> None:
    xml = VALID_RELEASE_MANIFEST.replace(
        "</activity>",
        "</activity>\n        <activity android:name=\"androidx.compose.ui.tooling.PreviewActivity\" android:exported=\"true\" />",
        1,
    )
    assert_fails(checker.validate_release_manifest(xml, PACKAGE), "unexpected activity")


def test_profile_receiver_missing_permission_fails() -> None:
    xml = VALID_RELEASE_MANIFEST.replace(' android:permission="android.permission.DUMP"', "")
    assert_fails(checker.validate_release_manifest(xml, PACKAGE), "must require android.permission.DUMP")


def test_release_cleartext_traffic_fails() -> None:
    xml = VALID_RELEASE_MANIFEST.replace(
        '<application android:allowBackup="false"',
        '<application android:allowBackup="false" android:usesCleartextTraffic="true"',
    )
    assert_fails(checker.validate_release_manifest(xml, PACKAGE), "usesCleartextTraffic=true")


def main() -> int:
    tests = [
        test_valid_source_passes,
        test_valid_release_passes,
        test_main_activity_uses_gradle_release_identity,
        test_source_permission_fails,
        test_release_unexpected_activity_fails,
        test_profile_receiver_missing_permission_fails,
        test_release_cleartext_traffic_fails,
    ]
    for test in tests:
        test()
    print("PASS: manifest component exposure self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
