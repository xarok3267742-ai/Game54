#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from release_identity import read_gradle_release_identity

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "play-submission" / "release" / "artifact_manifest.json"
DEBUG_APK = ROOT / "app" / "build" / "outputs" / "apk" / "debug" / "app-debug.apk"
RELEASE_AAB = ROOT / "app" / "build" / "outputs" / "bundle" / "release" / "app-release.aab"
PACKET_AAB = ROOT / "play-submission" / "release" / "app-release.aab"
ARTIFACT_STATUS = ROOT / "play-submission" / "release" / "artifact_status.properties"
SIGNING_INPUT_CHECKER = ROOT / "scripts" / "check_release_signing_inputs.py"
PLAY_FORMS_CHECKER = ROOT / "scripts" / "check_play_console_forms.py"
POLICY_CONTENT_CHECKER = ROOT / "scripts" / "check_policy_content_risk.py"

EXPECTED_TOP_LEVEL_KEYS = {
    "schemaVersion",
    "appId",
    "versionCode",
    "versionName",
    "localRcReady",
    "playUploadReady",
    "artifacts",
    "packetArtifactStatus",
    "uploadBlockers",
}
EXPECTED_ARTIFACT_KEYS = {"debugApk", "releaseAab", "packetReleaseAab"}
EXPECTED_ARTIFACT_STATUS_KEYS = {"signed_or_configured", "artifact", "reason"}
KNOWN_UPLOAD_BLOCKERS = {
    "release_signing_inputs_missing",
    "signed_upload_aab_missing",
    "public_privacy_policy_url_missing",
    "support_email_missing",
    "privacy_policy_contact_not_replaced",
    "feature_graphic_not_confirmed",
    "data_safety_not_confirmed",
    "target_audience_not_confirmed",
    "content_rating_not_confirmed",
    "internal_testing_not_confirmed",
    "play_console_forms_evidence_failed",
    "policy_content_risk_evidence_failed",
}
KNOWN_SIGNATURE_STATUSES = {
    "missing",
    "signed_verified",
    "unchecked_jarsigner_missing",
    "unsigned",
    "unverified",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def require_exact_keys(
    failures: list[str],
    *,
    label: str,
    record: dict[str, object],
    expected_keys: set[str],
) -> None:
    actual_keys = set(record)
    missing_keys = sorted(expected_keys - actual_keys)
    unexpected_keys = sorted(actual_keys - expected_keys)
    if missing_keys:
        failures.append(f"{label} is missing keys: {', '.join(missing_keys)}")
    if unexpected_keys:
        failures.append(f"{label} contains unexpected keys: {', '.join(unexpected_keys)}")


def expected_artifact_record_keys(key: str, path: Path) -> set[str]:
    keys = {"exists", "path"}
    if path.exists():
        keys.update({"bytes", "sha256"})
    if key == "releaseAab":
        keys.add("signatureStatus")
    return keys


def release_signing_inputs_ready() -> bool:
    if not SIGNING_INPUT_CHECKER.exists():
        return False
    completed = subprocess.run(
        [sys.executable, str(SIGNING_INPUT_CHECKER), "--require"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    return completed.returncode == 0


def checker_passes(path: Path) -> bool:
    if not path.exists():
        return False
    completed = subprocess.run(
        [sys.executable, str(path)],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    return completed.returncode == 0


def require_artifact_matches(
    failures: list[str],
    manifest: dict[str, object],
    key: str,
    path: Path,
    *,
    expected_record_path: str,
    required: bool,
) -> None:
    artifacts = manifest.get("artifacts", {})
    if not isinstance(artifacts, dict):
        failures.append("manifest artifacts section is missing")
        return
    record = artifacts.get(key)
    if not isinstance(record, dict):
        failures.append(f"manifest artifact record is missing: {key}")
        return
    require_exact_keys(
        failures,
        label=f"{key} artifact record",
        record=record,
        expected_keys=expected_artifact_record_keys(key, path),
    )

    if record.get("path") != expected_record_path:
        failures.append(
            f"{key} path is out of sync: expected {expected_record_path!r}, got {record.get('path')!r}"
        )
    if key == "releaseAab" and record.get("signatureStatus") not in KNOWN_SIGNATURE_STATUSES:
        failures.append(f"{key} signatureStatus is not recognized: {record.get('signatureStatus')!r}")

    exists = bool(record.get("exists"))
    if required and not path.exists():
        failures.append(f"required artifact is missing: {path.relative_to(ROOT)}")
        return
    if exists != path.exists():
        failures.append(f"{key} exists flag is out of sync")
        return
    if not path.exists():
        return

    if record.get("bytes") != path.stat().st_size:
        failures.append(f"{key} byte size is out of sync")
    if record.get("sha256") != sha256(path):
        failures.append(f"{key} sha256 is out of sync")


def main() -> int:
    failures: list[str] = []

    if not MANIFEST.exists():
        print(f"FAIL: release artifact manifest is missing: {MANIFEST.relative_to(ROOT)}", file=sys.stderr)
        return 1

    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"FAIL: release artifact manifest is invalid JSON: {exc}", file=sys.stderr)
        return 1
    if not isinstance(manifest, dict):
        print("FAIL: release artifact manifest must be a JSON object", file=sys.stderr)
        return 1

    require_exact_keys(
        failures,
        label="release artifact manifest",
        record=manifest,
        expected_keys=EXPECTED_TOP_LEVEL_KEYS,
    )

    if manifest.get("schemaVersion") != 1:
        failures.append("schemaVersion must be 1")

    try:
        expected_identity = read_gradle_release_identity()
    except (OSError, ValueError) as exc:
        failures.append(f"release identity could not be read from Gradle: {exc}")
        expected_identity = {}

    for key, expected_value in expected_identity.items():
        if manifest.get(key) != expected_value:
            failures.append(f"{key} is out of sync with app/build.gradle.kts")

    artifacts_section = manifest.get("artifacts", {})
    if isinstance(artifacts_section, dict):
        require_exact_keys(
            failures,
            label="manifest artifacts section",
            record=artifacts_section,
            expected_keys=EXPECTED_ARTIFACT_KEYS,
        )
    else:
        failures.append("manifest artifacts section is missing")

    require_artifact_matches(
        failures,
        manifest,
        "debugApk",
        DEBUG_APK,
        expected_record_path="app/build/outputs/apk/debug/app-debug.apk",
        required=True,
    )
    require_artifact_matches(
        failures,
        manifest,
        "releaseAab",
        RELEASE_AAB,
        expected_record_path="app/build/outputs/bundle/release/app-release.aab",
        required=True,
    )
    require_artifact_matches(
        failures,
        manifest,
        "packetReleaseAab",
        PACKET_AAB,
        expected_record_path="play-submission/release/app-release.aab",
        required=False,
    )

    artifact_status = read_properties(ARTIFACT_STATUS)
    if manifest.get("packetArtifactStatus") != artifact_status:
        failures.append("packetArtifactStatus is out of sync with artifact_status.properties")
    packet_artifact_status = manifest.get("packetArtifactStatus")
    if isinstance(packet_artifact_status, dict):
        require_exact_keys(
            failures,
            label="packetArtifactStatus",
            record=packet_artifact_status,
            expected_keys=EXPECTED_ARTIFACT_STATUS_KEYS,
        )
    else:
        failures.append("packetArtifactStatus must be an object")

    artifacts = manifest.get("artifacts", {})
    release_record = artifacts.get("releaseAab", {}) if isinstance(artifacts, dict) else {}
    packet_record = artifacts.get("packetReleaseAab", {}) if isinstance(artifacts, dict) else {}
    signature_status = release_record.get("signatureStatus") if isinstance(release_record, dict) else None
    packet_included = bool(packet_record.get("exists")) if isinstance(packet_record, dict) else False
    upload_blockers = manifest.get("uploadBlockers")
    if not isinstance(upload_blockers, list):
        failures.append("uploadBlockers must be a list")
        upload_blockers = []
    elif not all(isinstance(item, str) for item in upload_blockers):
        failures.append("uploadBlockers must contain only strings")
        upload_blockers = [item for item in upload_blockers if isinstance(item, str)]
    duplicate_blockers = sorted({item for item in upload_blockers if upload_blockers.count(item) > 1})
    if duplicate_blockers:
        failures.append(f"uploadBlockers contains duplicates: {', '.join(duplicate_blockers)}")
    unknown_blockers = sorted(set(upload_blockers) - KNOWN_UPLOAD_BLOCKERS)
    if unknown_blockers:
        failures.append(f"uploadBlockers contains unknown blockers: {', '.join(unknown_blockers)}")

    signing_inputs_ready = release_signing_inputs_ready()
    has_signing_input_blocker = "release_signing_inputs_missing" in upload_blockers
    if signing_inputs_ready and has_signing_input_blocker:
        failures.append("release_signing_inputs_missing blocker must be absent when current signing inputs pass strict preflight")
    if not signing_inputs_ready and not has_signing_input_blocker:
        failures.append("release_signing_inputs_missing blocker must be present when current signing inputs do not pass strict preflight")

    evidence_checks = (
        (PLAY_FORMS_CHECKER, "play_console_forms_evidence_failed", "Play Console form evidence"),
        (POLICY_CONTENT_CHECKER, "policy_content_risk_evidence_failed", "policy content risk evidence"),
    )
    for checker, blocker, description in evidence_checks:
        checker_ready = checker_passes(checker)
        has_blocker = blocker in upload_blockers
        if checker_ready and has_blocker:
            failures.append(f"{blocker} blocker must be absent when current {description} passes")
        if not checker_ready and not has_blocker:
            failures.append(f"{blocker} blocker must be present when current {description} does not pass")

    if signature_status == "signed_verified":
        if not packet_included:
            failures.append("signed release AAB must be included in play-submission/release")
        else:
            if artifact_status.get("signed_or_configured") != "true":
                failures.append("packet artifact status must mark signed_or_configured=true when signed AAB is included")
            if artifact_status.get("artifact") != "release/app-release.aab":
                failures.append("packet artifact status must point to release/app-release.aab when signed AAB is included")
            if release_record.get("sha256") != packet_record.get("sha256"):
                failures.append("packet release AAB sha256 must match current release AAB sha256")
            if release_record.get("bytes") != packet_record.get("bytes"):
                failures.append("packet release AAB byte size must match current release AAB byte size")
            if "signed_upload_aab_missing" in upload_blockers:
                failures.append("signed_upload_aab_missing blocker must be absent when signed AAB is included")
    else:
        if packet_included:
            failures.append("unsigned or unverified AAB must not be included as a Play upload artifact")
        if artifact_status.get("signed_or_configured") == "true":
            failures.append("packet artifact status must not mark unsigned or unverified AAB as signed/configured")
        if "signed_upload_aab_missing" not in upload_blockers:
            failures.append("unsigned or unverified local RC must report signed_upload_aab_missing")

    if bool(manifest.get("playUploadReady")) != (not upload_blockers):
        failures.append("playUploadReady must match empty uploadBlockers")
    if not manifest.get("localRcReady"):
        failures.append("localRcReady must be true after verifier build")

    if failures:
        print("Release artifact manifest check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: release artifact manifest matches current build and packet state")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
