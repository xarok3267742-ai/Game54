#!/usr/bin/env python3
from __future__ import annotations

import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEBUG_APK = ROOT / "app/build/outputs/apk/debug/app-debug.apk"
RELEASE_AAB = ROOT / "app/build/outputs/bundle/release/app-release.aab"

FORBIDDEN_PATH_FRAGMENTS = (
    "docs/",
    "qa/",
    "screenshots/",
    "store-assets/",
    "play-submission/",
    "privacy_policy",
    "store_listing",
    "feature-graphic",
    "feature_graphic",
    "play-store-icon",
    "play_store_icon",
    "artifact_manifest",
    "checksums.sha256",
)

FORBIDDEN_SUFFIXES = (
    ".jks",
    ".keystore",
    ".p12",
    ".pfx",
    ".pem",
    ".key",
    ".kt",
    ".java",
    ".rtf",
    ".docx",
)

FORBIDDEN_BASENAMES = {
    ".env",
    "keystore.properties",
    "signing.properties",
}


@dataclass(frozen=True)
class ArtifactSpec:
    label: str
    path: Path
    required_entries: tuple[str, ...]
    required_prefixes: tuple[str, ...]


ARTIFACTS = (
    ArtifactSpec(
        label="debug APK",
        path=DEBUG_APK,
        required_entries=(
            "AndroidManifest.xml",
            "classes.dex",
            "resources.arsc",
            "res/raw/tasks_ru.json",
            "res/drawable/ic_launcher_background.xml",
            "res/mipmap-anydpi-v26/ic_launcher.xml",
            "res/mipmap-anydpi-v26/ic_launcher_round.xml",
            "res/mipmap-xxxhdpi-v4/ic_launcher.png",
            "res/mipmap-xxxhdpi-v4/ic_launcher_foreground.png",
            "res/mipmap-xxxhdpi-v4/ic_launcher_round.png",
        ),
        required_prefixes=(
            "lib/",
            "META-INF/androidx.compose.",
            "META-INF/androidx.datastore",
        ),
    ),
    ArtifactSpec(
        label="release AAB",
        path=RELEASE_AAB,
        required_entries=(
            "BundleConfig.pb",
            "base/manifest/AndroidManifest.xml",
            "base/dex/classes.dex",
            "base/resources.pb",
            "base/res/raw/tasks_ru.json",
            "base/res/drawable/ic_launcher_background.xml",
            "base/res/mipmap-anydpi-v26/ic_launcher.xml",
            "base/res/mipmap-anydpi-v26/ic_launcher_round.xml",
            "base/res/mipmap-xxxhdpi-v4/ic_launcher.png",
            "base/res/mipmap-xxxhdpi-v4/ic_launcher_foreground.png",
            "base/res/mipmap-xxxhdpi-v4/ic_launcher_round.png",
        ),
        required_prefixes=(
            "base/lib/",
            "base/root/META-INF/androidx.compose.",
            "base/root/META-INF/androidx.datastore",
            "BUNDLE-METADATA/com.android.tools.build",
        ),
    ),
)


def zip_entries(path: Path) -> dict[str, zipfile.ZipInfo]:
    with zipfile.ZipFile(path) as archive:
        return {info.filename: info for info in archive.infolist() if not info.filename.endswith("/")}


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def validate_artifact(spec: ArtifactSpec, failures: list[str]) -> tuple[int, int]:
    if not spec.path.exists():
        failures.append(f"{spec.label} is missing: {display_path(spec.path)}")
        return 0, 0
    if spec.path.stat().st_size <= 0:
        failures.append(f"{spec.label} is empty: {display_path(spec.path)}")
        return 0, 0

    try:
        entries = zip_entries(spec.path)
    except zipfile.BadZipFile:
        failures.append(f"{spec.label} is not a readable ZIP artifact: {display_path(spec.path)}")
        return 0, 0

    for required in spec.required_entries:
        info = entries.get(required)
        if info is None:
            failures.append(f"{spec.label} missing required entry: {required}")
        elif info.file_size <= 0:
            failures.append(f"{spec.label} required entry is empty: {required}")

    for prefix in spec.required_prefixes:
        if not any(name.startswith(prefix) for name in entries):
            failures.append(f"{spec.label} missing required entry prefix: {prefix}")

    for name, info in entries.items():
        normalized = name.lower()
        basename = Path(name).name.lower()

        for fragment in FORBIDDEN_PATH_FRAGMENTS:
            if fragment in normalized:
                failures.append(f"{spec.label} contains workspace-only path fragment {fragment!r}: {name}")

        if basename in FORBIDDEN_BASENAMES:
            failures.append(f"{spec.label} contains forbidden local config filename: {name}")

        suffix = Path(name).suffix.lower()
        if suffix in FORBIDDEN_SUFFIXES:
            failures.append(f"{spec.label} contains forbidden source/secret-like suffix {suffix}: {name}")

        if info.file_size < 0:
            failures.append(f"{spec.label} has invalid entry size: {name}")

    return len(entries), spec.path.stat().st_size


def main() -> int:
    failures: list[str] = []
    summaries: list[str] = []

    for artifact in ARTIFACTS:
        count, byte_size = validate_artifact(artifact, failures)
        summaries.append(f"{artifact.label}: {count} entries, {byte_size} bytes")

    if failures:
        print("Packaged app contents check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: packaged app contents are scoped to runtime artifacts (" + "; ".join(summaries) + ")")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
