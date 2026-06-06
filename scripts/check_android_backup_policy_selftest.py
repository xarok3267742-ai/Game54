#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "scripts/check_android_backup_policy.py"

spec = importlib.util.spec_from_file_location("android_backup_policy_checker", CHECKER_PATH)
assert spec is not None and spec.loader is not None
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

VALID_MANIFEST = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <application android:allowBackup="false" />
</manifest>
"""

VALID_APK_XMLTREE = """
E: manifest (line=2)
  E: application (line=7)
    A: android:allowBackup(0x01010280)=(type 0x12)0x0
"""


def assert_passes(failures: list[str]) -> None:
    assert failures == [], failures


def assert_fails(failures: list[str], expected: str) -> None:
    assert any(expected in failure for failure in failures), failures


def test_valid_manifest_passes() -> None:
    assert_passes(checker.manifest_backup_failures(VALID_MANIFEST, "source"))


def test_manifest_allow_backup_true_fails() -> None:
    xml = VALID_MANIFEST.replace('android:allowBackup="false"', 'android:allowBackup="true"')
    assert_fails(checker.manifest_backup_failures(xml, "source"), 'android:allowBackup="false"')


def test_manifest_data_extraction_rules_fails() -> None:
    xml = VALID_MANIFEST.replace(
        'android:allowBackup="false"',
        'android:allowBackup="false" android:dataExtractionRules="@xml/data_extraction_rules"',
    )
    assert_fails(checker.manifest_backup_failures(xml, "source"), "android:dataExtractionRules")


def test_manifest_missing_application_fails() -> None:
    xml = '<manifest xmlns:android="http://schemas.android.com/apk/res/android" />'
    assert_fails(checker.manifest_backup_failures(xml, "source"), "missing <application>")


def test_valid_apk_xmltree_passes() -> None:
    assert_passes(checker.apk_xmltree_backup_failures(VALID_APK_XMLTREE))


def test_apk_xmltree_missing_allow_backup_fails() -> None:
    assert_fails(checker.apk_xmltree_backup_failures("E: manifest"), "missing android:allowBackup")


def test_apk_xmltree_allow_backup_true_fails() -> None:
    xmltree = VALID_APK_XMLTREE.replace("(type 0x12)0x0", "(type 0x12)0xffffffff")
    assert_fails(checker.apk_xmltree_backup_failures(xmltree), "must set android:allowBackup=false")


def test_apk_xmltree_backup_agent_fails() -> None:
    xmltree = VALID_APK_XMLTREE + "    A: android:backupAgent(0x0101027f)=@0x7f120001\n"
    assert_fails(checker.apk_xmltree_backup_failures(xmltree), "android:backupAgent")


def main() -> int:
    tests = [
        test_valid_manifest_passes,
        test_manifest_allow_backup_true_fails,
        test_manifest_data_extraction_rules_fails,
        test_manifest_missing_application_fails,
        test_valid_apk_xmltree_passes,
        test_apk_xmltree_missing_allow_backup_fails,
        test_apk_xmltree_allow_backup_true_fails,
        test_apk_xmltree_backup_agent_fails,
    ]
    for test in tests:
        test()
    print("PASS: Android backup policy checker self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
