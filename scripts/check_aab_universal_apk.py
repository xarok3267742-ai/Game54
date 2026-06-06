#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from release_identity import read_gradle_release_identity

ROOT = Path(__file__).resolve().parents[1]
AAB = ROOT / "app/build/outputs/bundle/release/app-release.aab"

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


def find_build_tool(sdk: Path, name: str) -> Path | None:
    candidates = sorted((sdk / "build-tools").glob(f"*/{name}"))
    return candidates[-1] if candidates else None


def bundletool_classpath() -> str:
    jars = sorted((Path.home() / ".gradle/caches/modules-2/files-2.1").glob("**/*.jar"))
    return ":".join(str(jar) for jar in jars)


def run(command: list[str]) -> tuple[int, str]:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    return completed.returncode, completed.stdout


def build_universal_apks(java: Path, aapt2: Path, output: Path) -> tuple[int, str]:
    classpath = bundletool_classpath()
    if "bundletool" not in classpath:
        return 1, "bundletool jar not found in Gradle cache"

    return run(
        [
            str(java),
            "-cp",
            classpath,
            "com.android.tools.build.bundletool.BundleToolMain",
            "build-apks",
            f"--bundle={AAB}",
            f"--output={output}",
            "--mode=universal",
            f"--aapt2={aapt2}",
        ],
    )


def parse_badging(output: str) -> tuple[dict[str, str], list[str]]:
    metadata: dict[str, str] = {}
    permissions: list[str] = []
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
        elif line.startswith("uses-permission:"):
            match = re.search(r"name='([^']+)'", line)
            if match:
                permissions.append(match.group(1))
    return metadata, permissions


def metadata_failures(
    metadata: dict[str, str],
    permissions: list[str],
    release_identity: dict[str, object] | None = None,
) -> list[str]:
    failures: list[str] = []
    for key, expected in expected_metadata(release_identity).items():
        actual = metadata.get(key)
        if actual != expected:
            failures.append(f"{key}: expected {expected!r}, got {actual!r}")

    allowed_permission = allowed_app_permission(release_identity)
    disallowed_permissions = [
        permission for permission in permissions if permission != allowed_permission
    ]
    if disallowed_permissions:
        failures.extend(f"disallowed uses-permission: {permission}" for permission in disallowed_permissions)

    return failures


def extract_universal_apk(apks: Path, destination: Path) -> tuple[Path | None, list[str]]:
    if not apks.exists() or apks.stat().st_size <= 0:
        return None, ["bundletool did not create a non-empty .apks archive"]

    try:
        with zipfile.ZipFile(apks) as archive:
            names = set(archive.namelist())
            failures: list[str] = []
            if "toc.pb" not in names:
                failures.append(".apks archive is missing toc.pb")
            if "universal.apk" not in names:
                failures.append(".apks archive is missing universal.apk")
            if failures:
                return None, failures

            archive.extract("universal.apk", destination)
    except zipfile.BadZipFile:
        return None, [".apks archive is not a valid ZIP file"]

    universal_apk = destination / "universal.apk"
    if universal_apk.stat().st_size <= 0:
        return None, ["universal.apk is empty"]

    return universal_apk, []


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

    sdk = find_android_sdk()
    if sdk is None:
        return fail("Android SDK not found. Set ANDROID_HOME or local.properties sdk.dir.")

    aapt = find_build_tool(sdk, "aapt")
    aapt2 = find_build_tool(sdk, "aapt2")
    if aapt is None:
        return fail(f"aapt not found under {sdk / 'build-tools'}")
    if aapt2 is None:
        return fail(f"aapt2 not found under {sdk / 'build-tools'}")

    temp_dir = Path(tempfile.mkdtemp(prefix="poryadok5-aab-universal-"))
    try:
        apks = temp_dir / "release-universal.apks"
        status, output = build_universal_apks(java, aapt2, apks)
        if status != 0:
            print(output, file=sys.stderr)
            return fail("bundletool build-apks --mode=universal failed")

        universal_apk, archive_failures = extract_universal_apk(apks, temp_dir)
        if archive_failures or universal_apk is None:
            for item in archive_failures:
                print(item, file=sys.stderr)
            return fail("bundletool universal APK archive is invalid")

        status, output = run([str(aapt), "dump", "badging", str(universal_apk)])
        if status != 0:
            print(output, file=sys.stderr)
            return fail("aapt dump badging failed for universal.apk")

        metadata, permissions = parse_badging(output)
        failures = metadata_failures(metadata, permissions, release_identity)

        if failures:
            for item in failures:
                print(item, file=sys.stderr)
            return fail("bundle-derived universal APK metadata does not match RC expectations")

        expected = expected_metadata(release_identity)
        print(
            "PASS: release AAB builds a universal APK with expected metadata "
            f"({expected['package']}, version {expected['versionName']}, "
            f"minSdk {expected['sdkVersion']}, targetSdk {expected['targetSdkVersion']})",
        )
        return 0
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
