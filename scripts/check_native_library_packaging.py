#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEBUG_APK = ROOT / "app/build/outputs/apk/debug/app-debug.apk"
RELEASE_AAB = ROOT / "app/build/outputs/bundle/release/app-release.aab"


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


def build_universal_apk(java: Path, aapt2: Path, temp_dir: Path) -> Path:
    classpath = bundletool_classpath()
    if "bundletool" not in classpath:
        raise RuntimeError("bundletool jar not found in Gradle cache")

    apks = temp_dir / "release-universal.apks"
    status, output = run(
        [
            str(java),
            "-cp",
            classpath,
            "com.android.tools.build.bundletool.BundleToolMain",
            "build-apks",
            f"--bundle={RELEASE_AAB}",
            f"--output={apks}",
            "--mode=universal",
            f"--aapt2={aapt2}",
        ],
    )
    if status != 0:
        raise RuntimeError(output)

    return extract_universal_apk(apks, temp_dir)


def extract_universal_apk(apks: Path, destination: Path) -> Path:
    if not apks.exists() or apks.stat().st_size <= 0:
        raise RuntimeError("bundletool did not create a non-empty .apks archive")

    with zipfile.ZipFile(apks) as archive:
        if "universal.apk" not in archive.namelist():
            raise RuntimeError(".apks archive is missing universal.apk")
        archive.extract("universal.apk", destination)

    universal_apk = destination / "universal.apk"
    if not universal_apk.exists() or universal_apk.stat().st_size <= 0:
        raise RuntimeError("universal.apk is missing or empty")
    return universal_apk


def native_libraries(apk: Path) -> list[zipfile.ZipInfo]:
    with zipfile.ZipFile(apk) as archive:
        return [
            info
            for info in archive.infolist()
            if info.filename.startswith("lib/") and info.filename.endswith(".so")
        ]


def native_entry_failures(entries: list[zipfile.ZipInfo], label: str) -> list[str]:
    failures: list[str] = []
    for info in entries:
        if info.compress_type != zipfile.ZIP_STORED:
            failures.append(f"{label}: native library is compressed: {info.filename}")
        if info.file_size <= 0:
            failures.append(f"{label}: native library is empty: {info.filename}")
    return failures


def verify_native_entries(apk: Path, label: str) -> list[str]:
    return native_entry_failures(native_libraries(apk), label)


def zipalign_failures(status: int, output: str, label: str) -> list[str]:
    if status == 0 and "Verification successful" in output:
        return []
    return [f"{label}: zipalign -P 16 check failed\n{output}"]


def verify_zipalign(zipalign: Path, apk: Path, label: str) -> list[str]:
    status, output = run([str(zipalign), "-c", "-P", "16", "-v", "4", str(apk)])
    return zipalign_failures(status, output, label)


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

    aapt2 = find_build_tool(sdk, "aapt2")
    zipalign = find_build_tool(sdk, "zipalign")
    if aapt2 is None:
        return fail(f"aapt2 not found under {sdk / 'build-tools'}")
    if zipalign is None:
        return fail(f"zipalign not found under {sdk / 'build-tools'}")

    temp_dir = Path(tempfile.mkdtemp(prefix="poryadok5-native-packaging-"))
    try:
        try:
            universal_apk = build_universal_apk(java, aapt2, temp_dir)
        except RuntimeError as exc:
            return fail(f"bundle-derived universal APK build failed: {exc}")

        failures: list[str] = []
        debug_entries = native_libraries(DEBUG_APK)
        universal_entries = native_libraries(universal_apk)

        failures.extend(verify_native_entries(DEBUG_APK, "debug APK"))
        failures.extend(verify_native_entries(universal_apk, "bundle-derived universal APK"))
        failures.extend(verify_zipalign(zipalign, DEBUG_APK, "debug APK"))
        failures.extend(verify_zipalign(zipalign, universal_apk, "bundle-derived universal APK"))

        if failures:
            print("Native library packaging check failed:", file=sys.stderr)
            for failure in failures:
                print(f"  {failure}", file=sys.stderr)
            return 1

        print(
            "PASS: native library packaging is install-ready "
            f"(debug APK libs: {len(debug_entries)}, bundle-derived universal APK libs: {len(universal_entries)}, "
            "uncompressed and zipalign -P 16 verified)",
        )
        return 0
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
