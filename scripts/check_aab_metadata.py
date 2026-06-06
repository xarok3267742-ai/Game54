#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from release_identity import read_gradle_release_identity

ROOT = Path(__file__).resolve().parents[1]
AAB = ROOT / "app/build/outputs/bundle/release/app-release.aab"
ANDROID_NS = "{http://schemas.android.com/apk/res/android}"

STATIC_EXPECTED = {
    f"{ANDROID_NS}compileSdkVersion": "35",
    "minSdkVersion": "26",
    "targetSdkVersion": "35",
    "applicationLabel": "@string/app_name",
}


def fail(message: str) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def expected_metadata(release_identity: dict[str, object] | None = None) -> dict[str, str]:
    identity = release_identity or read_gradle_release_identity()
    return {
        "package": str(identity["appId"]),
        f"{ANDROID_NS}versionCode": str(identity["versionCode"]),
        f"{ANDROID_NS}versionName": str(identity["versionName"]),
        **STATIC_EXPECTED,
    }


def allowed_app_permission(release_identity: dict[str, object] | None = None) -> str:
    identity = release_identity or read_gradle_release_identity()
    return f"{identity['appId']}.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION"


def find_java() -> Path | None:
    java_home = os.environ.get("JAVA_HOME")
    if java_home and (Path(java_home) / "bin/java").is_file():
        return Path(java_home) / "bin/java"

    studio_java = Path("/Applications/Android Studio.app/Contents/jbr/Contents/Home/bin/java")
    if studio_java.is_file():
        return studio_java

    return None


def bundletool_classpath() -> str:
    jars = sorted((Path.home() / ".gradle/caches/modules-2/files-2.1").glob("**/*.jar"))
    return ":".join(str(jar) for jar in jars)


def dump_manifest(java: Path) -> str:
    classpath = bundletool_classpath()
    if "bundletool" not in classpath:
        raise RuntimeError("bundletool jar not found in Gradle cache.")

    result = subprocess.run(
        [
            str(java),
            "-cp",
            classpath,
            "com.android.tools.build.bundletool.BundleToolMain",
            "dump",
            "manifest",
            f"--bundle={AAB}",
            "--module=base",
        ],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stdout)
    return result.stdout


def metadata_from_manifest_xml(manifest_xml: str) -> tuple[dict[str, str | None], list[str]]:
    manifest = ET.fromstring(manifest_xml)
    application = manifest.find("application")
    uses_sdk = manifest.find("uses-sdk")
    uses_permissions = [
        node.attrib.get(f"{ANDROID_NS}name")
        for node in manifest.findall("uses-permission")
        if node.attrib.get(f"{ANDROID_NS}name")
    ]

    actual = {
        "package": manifest.attrib.get("package"),
        f"{ANDROID_NS}versionCode": manifest.attrib.get(f"{ANDROID_NS}versionCode"),
        f"{ANDROID_NS}versionName": manifest.attrib.get(f"{ANDROID_NS}versionName"),
        f"{ANDROID_NS}compileSdkVersion": manifest.attrib.get(f"{ANDROID_NS}compileSdkVersion"),
        "minSdkVersion": uses_sdk.attrib.get(f"{ANDROID_NS}minSdkVersion") if uses_sdk is not None else None,
        "targetSdkVersion": uses_sdk.attrib.get(f"{ANDROID_NS}targetSdkVersion") if uses_sdk is not None else None,
        "applicationLabel": application.attrib.get(f"{ANDROID_NS}label") if application is not None else None,
    }
    return actual, uses_permissions


def metadata_failures(
    actual: dict[str, str | None],
    uses_permissions: list[str],
    release_identity: dict[str, object] | None = None,
) -> list[str]:
    failures: list[str] = []
    expected_metadata_values = expected_metadata(release_identity)
    for key, expected in expected_metadata_values.items():
        if actual.get(key) != expected:
            failures.append(f"{key}: expected {expected!r}, got {actual.get(key)!r}")

    allowed_permission = allowed_app_permission(release_identity)
    disallowed_permissions = [
        permission
        for permission in uses_permissions
        if permission != allowed_permission
    ]
    if disallowed_permissions:
        failures.extend(f"disallowed uses-permission: {permission}" for permission in disallowed_permissions)

    return failures


def main() -> int:
    if not AAB.exists():
        return fail(f"Missing AAB: {AAB.relative_to(ROOT)}")

    try:
        release_identity = read_gradle_release_identity()
    except (OSError, ValueError) as exc:
        return fail(f"release identity could not be read from Gradle: {exc}")

    java = find_java()
    if java is None:
        return fail("Java runtime not found. Set JAVA_HOME or install Android Studio JBR.")

    try:
        manifest_xml = dump_manifest(java)
    except Exception as exc:
        return fail(f"bundletool manifest dump failed: {exc}")

    actual, uses_permissions = metadata_from_manifest_xml(manifest_xml)
    failures = metadata_failures(actual, uses_permissions, release_identity)

    if failures:
        for item in failures:
            print(item, file=sys.stderr)
        return fail("AAB metadata does not match RC expectations.")

    expected = expected_metadata(release_identity)
    print(
        "PASS: AAB metadata matches RC expectations "
        f"({expected['package']}, version {expected[f'{ANDROID_NS}versionName']}, "
        f"minSdk {expected['minSdkVersion']}, targetSdk {expected['targetSdkVersion']})",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
