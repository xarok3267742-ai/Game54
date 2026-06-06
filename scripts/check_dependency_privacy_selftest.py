#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "scripts/check_dependency_privacy.py"

spec = importlib.util.spec_from_file_location("dependency_privacy_checker", CHECKER_PATH)
assert spec is not None and spec.loader is not None
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def assert_equal(actual: object, expected: object) -> None:
    assert actual == expected, f"expected {expected!r}, got {actual!r}"


def assert_failure_contains(failures: list[str], expected: str) -> None:
    assert any(expected in failure for failure in failures), failures


def test_androidx_runtime_dependencies_pass() -> None:
    output = """
+--- androidx.compose.ui:ui:1.10.0
+--- androidx.datastore:datastore-preferences:1.1.7
\\--- androidx.profileinstaller:profileinstaller:1.4.1
"""
    assert_equal(checker.find_forbidden_markers("releaseRuntimeClasspath", output), [])


def test_ads_marker_fails() -> None:
    output = "+--- com.google.android.gms:play-services-ads:24.0.0\n"
    failures = checker.find_forbidden_markers("releaseRuntimeClasspath", output)
    assert_failure_contains(failures, "ads")
    assert_failure_contains(failures, "play-services-ads")


def test_firebase_analytics_marker_fails() -> None:
    output = 'implementation("com.google.firebase:firebase-analytics-ktx:24.0.0")\n'
    failures = checker.find_forbidden_markers("app/build.gradle.kts", output)
    assert_failure_contains(failures, "analytics_or_measurement")
    assert_failure_contains(failures, "firebase-analytics")


def test_crash_reporting_marker_fails() -> None:
    output = "+--- io.sentry:sentry-android:8.0.0\n"
    failures = checker.find_forbidden_markers("releaseRuntimeClasspath", output)
    assert_failure_contains(failures, "crash_reporting")
    assert_failure_contains(failures, "sentry")


def test_tracking_marker_fails_case_insensitive() -> None:
    output = "+--- com.AppsFlyer:af-android-sdk:6.16.0\n"
    failures = checker.find_forbidden_markers("releaseRuntimeClasspath", output)
    assert_failure_contains(failures, "attribution_or_tracking")
    assert_failure_contains(failures, "appsflyer")


def test_firebase_platform_marker_fails() -> None:
    output = "+--- com.google.firebase:firebase-messaging:25.0.0\n"
    failures = checker.find_forbidden_markers("releaseRuntimeClasspath", output)
    assert_failure_contains(failures, "firebase_platform")
    assert_failure_contains(failures, "firebase-messaging")


def test_first_matching_line_is_reported() -> None:
    output = "\n".join(
        [
            "+--- androidx.compose.runtime:runtime:1.10.0",
            "+--- com.google.android.gms:play-services-measurement:24.0.0",
        ]
    )
    failures = checker.find_forbidden_markers("releaseRuntimeClasspath", output)
    assert_failure_contains(failures, "releaseRuntimeClasspath:2")


def main() -> int:
    tests = [
        test_androidx_runtime_dependencies_pass,
        test_ads_marker_fails,
        test_firebase_analytics_marker_fails,
        test_crash_reporting_marker_fails,
        test_tracking_marker_fails_case_insensitive,
        test_firebase_platform_marker_fails,
        test_first_matching_line_is_reported,
    ]
    for test in tests:
        test()
    print("PASS: dependency privacy checker self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
