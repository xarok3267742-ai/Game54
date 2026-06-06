#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "scripts/check_apk_permissions.py"

spec = importlib.util.spec_from_file_location("apk_permissions_checker", CHECKER_PATH)
assert spec is not None and spec.loader is not None
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

DEFAULT_IDENTITY = {"appId": "ru.poryadok5.app", "versionCode": 1, "versionName": "1.0.0-rc1"}
CUSTOM_IDENTITY = {"appId": "com.example.custom", "versionCode": 7, "versionName": "2.3.0"}
ALLOWED = checker.allowed_app_permission(DEFAULT_IDENTITY)


def assert_equal(actual: object, expected: object) -> None:
    assert actual == expected, f"expected {expected!r}, got {actual!r}"


def test_empty_permission_dump_passes() -> None:
    permissions = checker.parse_permissions("package: ru.poryadok5.app\n")
    assert_equal(permissions, [])
    assert_equal(checker.disallowed_permissions(permissions, DEFAULT_IDENTITY), [])


def test_allowed_androidx_permission_passes() -> None:
    output = f"uses-permission: name='{ALLOWED}'\n"
    permissions = checker.parse_permissions(output)
    assert_equal(permissions, [ALLOWED])
    assert_equal(checker.disallowed_permissions(permissions, DEFAULT_IDENTITY), [])


def test_allowed_permission_uses_gradle_release_identity() -> None:
    custom_allowed = checker.allowed_app_permission(CUSTOM_IDENTITY)
    permissions = checker.parse_permissions(f"uses-permission: name='{custom_allowed}'\n")

    assert_equal(checker.disallowed_permissions(permissions, CUSTOM_IDENTITY), [])
    assert_equal(checker.disallowed_permissions(permissions, DEFAULT_IDENTITY), [custom_allowed])


def test_platform_internet_permission_fails() -> None:
    output = "uses-permission: name='android.permission.INTERNET'\n"
    permissions = checker.parse_permissions(output)
    assert_equal(checker.disallowed_permissions(permissions, DEFAULT_IDENTITY), ["android.permission.INTERNET"])


def test_dangerous_location_permission_fails() -> None:
    output = "uses-permission: name='android.permission.ACCESS_FINE_LOCATION'\n"
    permissions = checker.parse_permissions(output)
    assert_equal(checker.disallowed_permissions(permissions, DEFAULT_IDENTITY), ["android.permission.ACCESS_FINE_LOCATION"])


def test_unexpected_app_specific_permission_fails() -> None:
    output = "uses-permission: name='com.example.other.PERMISSION'\n"
    permissions = checker.parse_permissions(output)
    assert_equal(checker.disallowed_permissions(permissions, DEFAULT_IDENTITY), ["com.example.other.PERMISSION"])


def test_parser_ignores_non_permission_lines() -> None:
    output = """
package: ru.poryadok5.app
permission: ru.poryadok5.app.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION
uses-permission: name='android.permission.POST_NOTIFICATIONS'
"""
    permissions = checker.parse_permissions(output)
    assert_equal(permissions, ["android.permission.POST_NOTIFICATIONS"])


def main() -> int:
    tests = [
        test_empty_permission_dump_passes,
        test_allowed_androidx_permission_passes,
        test_allowed_permission_uses_gradle_release_identity,
        test_platform_internet_permission_fails,
        test_dangerous_location_permission_fails,
        test_unexpected_app_specific_permission_fails,
        test_parser_ignores_non_permission_lines,
    ]
    for test in tests:
        test()
    print("PASS: APK permissions checker self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
