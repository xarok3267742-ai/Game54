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


def fail(message: str) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


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


def parse_permissions(output: str) -> list[str]:
    permissions: list[str] = []
    for line in output.splitlines():
        match = re.match(r"uses-permission:\s+name='([^']+)'", line.strip())
        if match:
            permissions.append(match.group(1))
    return permissions


def allowed_app_permission(release_identity: dict[str, object] | None = None) -> str:
    identity = release_identity or read_gradle_release_identity()
    return f"{identity['appId']}.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION"


def disallowed_permissions(
    permissions: list[str],
    release_identity: dict[str, object] | None = None,
) -> list[str]:
    allowed_permission = allowed_app_permission(release_identity)
    return [
        permission
        for permission in permissions
        if permission != allowed_permission
    ]


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
        [str(aapt), "dump", "permissions", str(APK)],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if result.returncode != 0:
        print(result.stdout, file=sys.stderr)
        return fail("aapt dump permissions failed.")

    permissions = parse_permissions(result.stdout)
    disallowed = disallowed_permissions(permissions, release_identity)

    if disallowed:
        for permission in disallowed:
            print(f"Disallowed APK permission: {permission}", file=sys.stderr)
        return fail("APK declares user-facing/platform or unexpected permissions.")

    if permissions:
        print(f"PASS: APK permissions contain only allowed app-specific signature permission: {permissions[0]}")
    else:
        print("PASS: APK declares no uses-permission entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
