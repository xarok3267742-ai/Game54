#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXPECTED = {
    "gradle": "8.11.1",
    "agp": "8.9.1",
    "kotlin": "2.0.21",
    "compose_bom": "2026.04.01",
    "namespace": "ru.poryadok5.app",
    "application_id": "ru.poryadok5.app",
    "min_sdk": "26",
    "compile_sdk": "35",
    "target_sdk": "35",
    "version_code": "1",
    "version_name": "1.0.0-rc1",
    "datastore": "1.1.7",
}


def read(relative_path: str) -> str:
    path = ROOT / relative_path
    if not path.exists():
        raise FileNotFoundError(relative_path)
    return path.read_text(encoding="utf-8")


def require(pattern: str, text: str, label: str, expected: str, failures: list[str]) -> None:
    match = re.search(pattern, text, flags=re.MULTILINE)
    if not match:
        failures.append(f"{label}: value not found")
        return
    actual = match.group(1)
    if actual != expected:
        failures.append(f"{label}: expected {expected}, got {actual}")


def require_contains(text: str, label: str, needle: str, failures: list[str]) -> None:
    if needle not in text:
        failures.append(f"{label}: missing {needle}")


def stack_version_failures(
    *,
    wrapper: str,
    root_gradle: str,
    app_gradle: str,
    tech_stack: str,
    tech_decision: str,
) -> list[str]:
    failures: list[str] = []

    require(r"gradle-([0-9.]+)-bin\.zip", wrapper, "Gradle wrapper", EXPECTED["gradle"], failures)
    require(r'id\("com\.android\.application"\) version "([^"]+)"', root_gradle, "Android Gradle Plugin", EXPECTED["agp"], failures)
    require(r'id\("org\.jetbrains\.kotlin\.android"\) version "([^"]+)"', root_gradle, "Kotlin Android plugin", EXPECTED["kotlin"], failures)
    require(r'id\("org\.jetbrains\.kotlin\.plugin\.compose"\) version "([^"]+)"', root_gradle, "Kotlin Compose plugin", EXPECTED["kotlin"], failures)

    require(r'namespace = "([^"]+)"', app_gradle, "Android namespace", EXPECTED["namespace"], failures)
    require(r'applicationId = "([^"]+)"', app_gradle, "applicationId", EXPECTED["application_id"], failures)
    require(r"minSdk = ([0-9]+)", app_gradle, "minSdk", EXPECTED["min_sdk"], failures)
    require(r"compileSdk = ([0-9]+)", app_gradle, "compileSdk", EXPECTED["compile_sdk"], failures)
    require(r"targetSdk = ([0-9]+)", app_gradle, "targetSdk", EXPECTED["target_sdk"], failures)
    require(r"versionCode = ([0-9]+)", app_gradle, "versionCode", EXPECTED["version_code"], failures)
    require(r'versionName = "([^"]+)"', app_gradle, "versionName", EXPECTED["version_name"], failures)
    require(r'androidx\.compose:compose-bom:([0-9.]+)', app_gradle, "Compose BOM", EXPECTED["compose_bom"], failures)
    require(r'androidx\.datastore:datastore-preferences:([0-9.]+)', app_gradle, "DataStore Preferences", EXPECTED["datastore"], failures)

    for label, doc in (("docs/tech_stack.md", tech_stack), ("docs/tech_stack_decision.md", tech_decision)):
        for key in ("agp", "kotlin", "compose_bom", "min_sdk", "compile_sdk", "target_sdk"):
            require_contains(doc, label, EXPECTED[key], failures)

    if "compileSdk = 35" in app_gradle and "targetSdk = 35" not in app_gradle:
        failures.append("compileSdk is 35 but targetSdk is not explicitly 35")

    return failures


def main() -> int:
    try:
        wrapper = read("gradle/wrapper/gradle-wrapper.properties")
        root_gradle = read("build.gradle.kts")
        app_gradle = read("app/build.gradle.kts")
        tech_stack = read("docs/tech_stack.md")
        tech_decision = read("docs/tech_stack_decision.md")
    except FileNotFoundError as error:
        print(f"FAIL: missing stack file: {error}", file=sys.stderr)
        return 1

    failures = stack_version_failures(
        wrapper=wrapper,
        root_gradle=root_gradle,
        app_gradle=app_gradle,
        tech_stack=tech_stack,
        tech_decision=tech_decision,
    )

    if failures:
        print("Stack version check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print(
        "PASS: stack versions match RC plan "
        f"(Gradle {EXPECTED['gradle']}, AGP {EXPECTED['agp']}, Kotlin {EXPECTED['kotlin']}, "
        f"Compose BOM {EXPECTED['compose_bom']}, SDK {EXPECTED['min_sdk']}/{EXPECTED['compile_sdk']}/{EXPECTED['target_sdk']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
