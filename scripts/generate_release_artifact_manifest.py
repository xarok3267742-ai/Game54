#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

from privacy_policy_common import (
    PRE_PUBLICATION_CONTACT_TEXT,
    validate_privacy_url,
    validate_publishable_policy,
    validate_support_email,
)
from release_identity import read_gradle_release_identity

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "play-submission"
RELEASE_DIR = PACKET / "release"
ARTIFACT_STATUS = RELEASE_DIR / "artifact_status.properties"
DEBUG_APK = ROOT / "app" / "build" / "outputs" / "apk" / "debug" / "app-debug.apk"
RELEASE_AAB = ROOT / "app" / "build" / "outputs" / "bundle" / "release" / "app-release.aab"
PACKET_AAB = RELEASE_DIR / "app-release.aab"
PRIVACY_HTML = ROOT / "docs" / "privacy_policy_ru.html"
PUBLISHABLE_PRIVACY_HTML = PACKET / "text" / "privacy_policy_publishable_ru.html"
OUTPUT = RELEASE_DIR / "artifact_manifest.json"
SIGNING_INPUT_CHECKER = ROOT / "scripts" / "check_release_signing_inputs.py"
PLAY_FORMS_CHECKER = ROOT / "scripts" / "check_play_console_forms.py"
POLICY_CONTENT_CHECKER = ROOT / "scripts" / "check_policy_content_risk.py"

YES_FLAGS = {
    "PORYADOK5_FEATURE_GRAPHIC_APPROVED": "feature_graphic_not_confirmed",
    "PORYADOK5_DATA_SAFETY_CONFIRMED": "data_safety_not_confirmed",
    "PORYADOK5_TARGET_AUDIENCE_CONFIRMED": "target_audience_not_confirmed",
    "PORYADOK5_CONTENT_RATING_CONFIRMED": "content_rating_not_confirmed",
    "PORYADOK5_INTERNAL_TESTING_CONFIRMED": "internal_testing_not_confirmed",
}


def read_properties(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.lstrip().startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def artifact_record(path: Path, packet_relative_path: str) -> dict[str, object]:
    if not path.exists():
        return {
            "exists": False,
            "path": packet_relative_path,
        }
    return {
        "exists": True,
        "path": packet_relative_path,
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


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


def find_jarsigner() -> str | None:
    java_home = os.environ.get("JAVA_HOME", "").strip()
    if java_home:
        candidate = Path(java_home) / "bin" / "jarsigner"
        if candidate.exists() and os.access(candidate, os.X_OK):
            return str(candidate)

    studio_jbr = Path("/Applications/Android Studio.app/Contents/jbr/Contents/Home/bin/jarsigner")
    if studio_jbr.exists() and os.access(studio_jbr, os.X_OK):
        return str(studio_jbr)

    status, output = run(["/usr/bin/env", "sh", "-c", "command -v jarsigner"])
    if status == 0 and output.strip():
        return output.strip()
    return None


def aab_signature_status(path: Path) -> str:
    if not path.exists():
        return "missing"
    jarsigner = find_jarsigner()
    if jarsigner is None:
        return "unchecked_jarsigner_missing"
    status, output = run([jarsigner, "-verify", "-verbose", "-certs", str(path)])
    if status == 0 and "jar verified" in output and "jar is unsigned" not in output:
        return "signed_verified"
    if "jar is unsigned" in output:
        return "unsigned"
    return "unverified"


def validate_url(value: str) -> bool:
    return validate_privacy_url(value)


def validate_email(value: str) -> bool:
    return validate_support_email(value)


def publishable_privacy_policy_ready(support_email: str) -> bool:
    if not PUBLISHABLE_PRIVACY_HTML.exists():
        return False
    failures = validate_publishable_policy(PUBLISHABLE_PRIVACY_HTML.read_text(encoding="utf-8"), support_email)
    return not failures


def release_signing_inputs_ready() -> bool:
    if not SIGNING_INPUT_CHECKER.exists():
        return False
    status, _output = run([str(SIGNING_INPUT_CHECKER), "--require"])
    return status == 0


def checker_passes(path: Path) -> bool:
    if not path.exists():
        return False
    status, _output = run([sys.executable, str(path)])
    return status == 0


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def upload_blockers(signature_status: str, packet_aab_exists: bool) -> list[str]:
    blockers: list[str] = []

    if not release_signing_inputs_ready():
        blockers.append("release_signing_inputs_missing")

    if signature_status != "signed_verified" or not packet_aab_exists:
        blockers.append("signed_upload_aab_missing")

    privacy_url = os.environ.get("PORYADOK5_PRIVACY_POLICY_URL", "").strip()
    support_email = os.environ.get("PORYADOK5_SUPPORT_EMAIL", "").strip()
    if not validate_url(privacy_url):
        blockers.append("public_privacy_policy_url_missing")
    if not validate_email(support_email):
        blockers.append("support_email_missing")

    if (
        PRIVACY_HTML.exists()
        and PRE_PUBLICATION_CONTACT_TEXT in PRIVACY_HTML.read_text(encoding="utf-8")
        and not publishable_privacy_policy_ready(support_email)
    ):
        blockers.append("privacy_policy_contact_not_replaced")

    for env_name, blocker in YES_FLAGS.items():
        if os.environ.get(env_name, "").strip().lower() != "yes":
            blockers.append(blocker)

    if not checker_passes(PLAY_FORMS_CHECKER):
        blockers.append("play_console_forms_evidence_failed")
    if not checker_passes(POLICY_CONTENT_CHECKER):
        blockers.append("policy_content_risk_evidence_failed")

    return blockers


def main() -> int:
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)

    try:
        release_identity = read_gradle_release_identity()
    except (OSError, ValueError) as exc:
        print(f"FAIL: release identity could not be read from Gradle: {exc}", file=sys.stderr)
        return 1

    signature_status = aab_signature_status(RELEASE_AAB)
    debug_apk = artifact_record(DEBUG_APK, "app/build/outputs/apk/debug/app-debug.apk")
    release_aab = artifact_record(RELEASE_AAB, "app/build/outputs/bundle/release/app-release.aab")
    packet_release_aab = artifact_record(PACKET_AAB, "play-submission/release/app-release.aab")
    artifact_status = read_properties(ARTIFACT_STATUS)

    manifest = {
        "schemaVersion": 1,
        **release_identity,
        "localRcReady": bool(debug_apk["exists"] and release_aab["exists"]),
        "playUploadReady": False,
        "artifacts": {
            "debugApk": debug_apk,
            "releaseAab": {
                **release_aab,
                "signatureStatus": signature_status,
            },
            "packetReleaseAab": packet_release_aab,
        },
        "packetArtifactStatus": artifact_status,
        "uploadBlockers": upload_blockers(signature_status, bool(packet_release_aab["exists"])),
    }
    manifest["playUploadReady"] = not manifest["uploadBlockers"]

    OUTPUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Built {display_path(OUTPUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
