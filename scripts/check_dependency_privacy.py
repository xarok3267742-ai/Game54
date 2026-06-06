#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRADLEW = ROOT / "gradlew"
BUILD_FILE = ROOT / "app" / "build.gradle.kts"
REPORT_DIR = ROOT / "build" / "reports" / "dependency-privacy"
RUNTIME_REPORT = REPORT_DIR / "releaseRuntimeClasspath.txt"

FORBIDDEN_MARKERS: dict[str, tuple[str, ...]] = {
    "ads": (
        "play-services-ads",
        "mobile-ads",
        "ads-identifier",
        "admob",
        "applovin",
        "ironsource",
        "unity-ads",
        "chartboost",
        "adcolony",
    ),
    "analytics_or_measurement": (
        "firebase-analytics",
        "play-services-analytics",
        "play-services-measurement",
        "app-measurement",
        "google.android.gms:measurement",
        "analytics-ktx",
    ),
    "crash_reporting": (
        "crashlytics",
        "firebase-crashlytics",
        "sentry",
        "bugsnag",
        "datadog",
    ),
    "attribution_or_tracking": (
        "adjust",
        "appsflyer",
        "facebook-android-sdk",
        "facebook-core",
        "facebook-applinks",
        "fb-android-sdk",
        "flurry",
        "appmetrica",
        "mytracker",
        "amplitude",
        "mixpanel",
        "onesignal",
    ),
    "firebase_platform": (
        "com.google.firebase",
        "firebase-bom",
        "firebase-common",
        "firebase-installations",
        "firebase-messaging",
    ),
}


def run_gradle_dependencies() -> str:
    result = subprocess.run(
        [
            str(GRADLEW),
            ":app:dependencies",
            "--configuration",
            "releaseRuntimeClasspath",
            "--console=plain",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    RUNTIME_REPORT.write_text(output, encoding="utf-8")

    if result.returncode != 0:
        print(output, file=sys.stderr)
        raise SystemExit("FAIL: Gradle releaseRuntimeClasspath dependency report failed.")

    return output


def find_forbidden_markers(source_name: str, text: str) -> list[str]:
    lowered = text.lower()
    violations: list[str] = []
    lines = text.splitlines()

    for category, markers in FORBIDDEN_MARKERS.items():
        for marker in markers:
            if marker not in lowered:
                continue
            for line_number, line in enumerate(lines, start=1):
                if marker in line.lower():
                    clean_line = line.strip()
                    violations.append(
                        f"{source_name}:{line_number}: {category}: {marker}: {clean_line}"
                    )
                    break

    return violations


def main() -> int:
    if not GRADLEW.exists():
        print(f"FAIL: Gradle wrapper not found: {GRADLEW}", file=sys.stderr)
        return 1
    if not BUILD_FILE.exists():
        print(f"FAIL: Gradle build file not found: {BUILD_FILE}", file=sys.stderr)
        return 1

    runtime_output = run_gradle_dependencies()
    build_text = BUILD_FILE.read_text(encoding="utf-8")

    violations = []
    violations.extend(find_forbidden_markers("releaseRuntimeClasspath", runtime_output))
    violations.extend(find_forbidden_markers("app/build.gradle.kts", build_text))

    if violations:
        print("FAIL: privacy-sensitive dependency marker(s) found.", file=sys.stderr)
        for violation in violations:
            print(violation, file=sys.stderr)
        return 1

    print(f"PASS: release dependency privacy audit ({RUNTIME_REPORT})")
    print("PASS: no ads, analytics, crash-reporting, attribution or tracking SDK markers found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
