#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

from release_identity import read_gradle_release_identity

ROOT = Path(__file__).resolve().parents[1]
APK = ROOT / "app/build/outputs/apk/debug/app-debug.apk"

STATIC_EXPECTED = {
    "compileSdkVersion": "35",
    "sdkVersion": "26",
    "targetSdkVersion": "35",
    "application-label": "Порядок 5",
}


def fail(message: str) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def expected_metadata(release_identity: dict[str, object] | None = None) -> dict[str, str]:
    identity = release_identity or read_gradle_release_identity()
    return {
        "package": str(identity["appId"]),
        "versionCode": str(identity["versionCode"]),
        "versionName": str(identity["versionName"]),
        **STATIC_EXPECTED,
    }


def find_android_sdk() -> Path | None:
    android_home = os.environ.get("ANDROID_HOME")
    if android_home and Path(android_home).is_dir():
        return Path(android_home)

    local_properties = ROOT / "local.properties"
    if local_properties.exists():
        for line in local_properties.read_text(encoding="utf-8").splitlines():
            if line.startswith("sdk.dir="):
                sdk = Path(line.split("=", 1)[1])
                if sdk.is_dir():
                    return sdk

    default_sdk = Path.home() / "Library/Android/sdk"
    if default_sdk.is_dir():
        return default_sdk

    return None


def find_aapt(sdk: Path) -> Path | None:
    candidates = sorted((sdk / "build-tools").glob("*/aapt"))
    return candidates[-1] if candidates else None


def parse_badging(output: str) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for line in output.splitlines():
        if line.startswith("package:"):
            for key in ("name", "versionCode", "versionName", "compileSdkVersion"):
                match = re.search(rf"{key}='([^']+)'", line)
                if match:
                    metadata["package" if key == "name" else key] = match.group(1)
        elif line.startswith("sdkVersion:"):
            metadata["sdkVersion"] = line.split("'", 2)[1]
        elif line.startswith("targetSdkVersion:"):
            metadata["targetSdkVersion"] = line.split("'", 2)[1]
        elif line.startswith("application-label:"):
            metadata["application-label"] = line.split("'", 2)[1]
    return metadata


def metadata_failures(
    metadata: dict[str, str],
    release_identity: dict[str, object] | None = None,
) -> list[str]:
    failures: list[str] = []
    for key, expected in expected_metadata(release_identity).items():
        actual = metadata.get(key)
        if actual != expected:
            failures.append(f"{key}: expected {expected!r}, got {actual!r}")
    return failures


def main() -> int:
    if not APK.exists():
        return fail(f"Missing APK: {APK.relative_to(ROOT)}")

    try:
        release_identity = read_gradle_release_identity()
    except (OSError, ValueError) as exc:
        return fail(f"release identity could not be read from Gradle: {exc}")

    sdk = find_android_sdk()
    if sdk is None:
        return fail("Android SDK not found. Set ANDROID_HOME or local.properties sdk.dir.")

    aapt = find_aapt(sdk)
    if aapt is None:
        return fail(f"aapt not found under {sdk / 'build-tools'}")

    result = subprocess.run(
        [str(aapt), "dump", "badging", str(APK)],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if result.returncode != 0:
        print(result.stdout, file=sys.stderr)
        return fail("aapt dump badging failed.")

    metadata = parse_badging(result.stdout)
    failures = metadata_failures(metadata, release_identity)

    if failures:
        for item in failures:
            print(item, file=sys.stderr)
        return fail("APK metadata does not match RC expectations.")

    expected = expected_metadata(release_identity)
    print(
        "PASS: APK metadata matches RC expectations "
        f"({expected['package']}, version {expected['versionName']}, "
        f"minSdk {expected['sdkVersion']}, targetSdk {expected['targetSdkVersion']})",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
