#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_MANIFEST = ROOT / "app/src/main/AndroidManifest.xml"
DEBUG_APK = ROOT / "app/build/outputs/apk/debug/app-debug.apk"
RELEASE_AAB = ROOT / "app/build/outputs/bundle/release/app-release.aab"
ANDROID_NS = "{http://schemas.android.com/apk/res/android}"
FORBIDDEN_BACKUP_ATTRS = (
    "backupAgent",
    "fullBackupContent",
    "dataExtractionRules",
)


def fail(message: str) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


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


def find_aapt(sdk: Path) -> Path | None:
    candidates = sorted((sdk / "build-tools").glob("*/aapt"))
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


def manifest_backup_failures(xml_text: str, label: str) -> list[str]:
    manifest = ET.fromstring(xml_text)
    application = manifest.find("application")
    if application is None:
        return [f"{label} manifest is missing <application>"]

    failures: list[str] = []
    if application.attrib.get(f"{ANDROID_NS}allowBackup") != "false":
        failures.append(f'{label} manifest application must set android:allowBackup="false"')

    for attr in FORBIDDEN_BACKUP_ATTRS:
        if f"{ANDROID_NS}{attr}" in application.attrib:
            failures.append(f"{label} manifest must not define android:{attr}")

    return failures


def apk_xmltree_backup_failures(output: str) -> list[str]:
    failures: list[str] = []
    if "android:allowBackup" not in output:
        failures.append("debug APK manifest is missing android:allowBackup")
    elif "android:allowBackup(0x01010280)=(type 0x12)0x0" not in output:
        failures.append("debug APK manifest must set android:allowBackup=false")

    for attr in FORBIDDEN_BACKUP_ATTRS:
        if f"android:{attr}" in output:
            failures.append(f"debug APK manifest must not define android:{attr}")

    return failures


def source_manifest_failures() -> list[str]:
    if not SOURCE_MANIFEST.exists():
        return [f"source manifest is missing: {SOURCE_MANIFEST.relative_to(ROOT)}"]

    return manifest_backup_failures(SOURCE_MANIFEST.read_text(encoding="utf-8"), "source")


def aab_manifest_failures(java: Path) -> list[str]:
    classpath = bundletool_classpath()
    if "bundletool" not in classpath:
        return ["bundletool jar not found in Gradle cache"]

    status, output = run(
        [
            str(java),
            "-cp",
            classpath,
            "com.android.tools.build.bundletool.BundleToolMain",
            "dump",
            "manifest",
            f"--bundle={RELEASE_AAB}",
            "--module=base",
        ],
    )
    if status != 0:
        return [f"bundletool manifest dump failed:\n{output}"]

    return manifest_backup_failures(output, "release AAB")


def apk_manifest_failures(aapt: Path) -> list[str]:
    status, output = run([str(aapt), "dump", "xmltree", str(DEBUG_APK), "AndroidManifest.xml"])
    if status != 0:
        return [f"aapt dump xmltree failed:\n{output}"]

    return apk_xmltree_backup_failures(output)


def main() -> int:
    if not DEBUG_APK.exists():
        return fail(f"Missing debug APK: {DEBUG_APK.relative_to(ROOT)}")
    if not RELEASE_AAB.exists():
        return fail(f"Missing release AAB: {RELEASE_AAB.relative_to(ROOT)}")

    java = find_java()
    if java is None:
        return fail("Java runtime not found. Set JAVA_HOME or install Android Studio JBR.")

    sdk = find_android_sdk()
    if sdk is None:
        return fail("Android SDK not found. Set ANDROID_HOME or local.properties sdk.dir.")
    aapt = find_aapt(sdk)
    if aapt is None:
        return fail(f"aapt not found under {sdk / 'build-tools'}")

    failures = source_manifest_failures()
    failures.extend(apk_manifest_failures(aapt))
    failures.extend(aab_manifest_failures(java))

    if failures:
        print("Android backup policy check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: Android backup/data extraction is disabled in source manifest, debug APK and release AAB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
