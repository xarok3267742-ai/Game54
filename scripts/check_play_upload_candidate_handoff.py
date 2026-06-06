#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "scripts" / "prepare_play_upload_candidate.sh"

ORDERED_MARKERS = (
    "scripts/check_release_signing_inputs.py --require",
    "scripts/check_play_upload_external_inputs.py",
    "scripts/verify_release_candidate.sh",
    "rebuild signed upload bundle after local verifier cleanup",
    "./gradlew :app:printReleaseSigningStatus bundleRelease --console=plain",
    "scripts/build_play_submission_packet.sh",
    "scripts/check_release_artifact_manifest.py",
    "scripts/check_play_upload_blockers.py",
    "scripts/check_play_submission_packet_contents.py",
    "scripts/check_play_submission_packet_sync.py",
    "scripts/check_play_upload_readiness.py --require-upload-ready",
    "shasum -a 256 -c checksums.sha256",
    "[[ -f play-submission/release/app-release.aab ]]",
)

REQUIRED_SNIPPETS = (
    "#!/usr/bin/env bash",
    "set -euo pipefail",
    'ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"',
    'cd "$ROOT_DIR"',
    "fail()",
)


def handoff_failures(text: str) -> list[str]:
    failures: list[str] = []

    for snippet in REQUIRED_SNIPPETS:
        if snippet not in text:
            failures.append(f"missing handoff safety marker: {snippet}")

    last_index = -1
    for marker in ORDERED_MARKERS:
        index = text.find(marker)
        if index == -1:
            failures.append(f"missing handoff marker: {marker}")
            continue
        if index <= last_index:
            failures.append(f"handoff marker is out of order: {marker}")
        last_index = index

    if "Step 1/8" not in text or "Step 8/8" not in text:
        failures.append("handoff script step count must cover 8 ordered steps")
    if text.count("scripts/check_release_signing_inputs.py --require") != 1:
        failures.append("handoff script must run strict signing input check exactly once")
    if text.count("scripts/check_play_upload_external_inputs.py") != 1:
        failures.append("handoff script must run the external input preflight exactly once")
    if text.count("scripts/verify_release_candidate.sh") != 1:
        failures.append("handoff script must run the full verifier exactly once")
    if text.count("./gradlew :app:printReleaseSigningStatus bundleRelease --console=plain") != 1:
        failures.append("handoff script must rebuild the signed bundle exactly once")
    if text.count("scripts/build_play_submission_packet.sh") != 1:
        failures.append("handoff script must rebuild the packet exactly once after the signed bundle rebuild")
    if text.count("scripts/check_play_submission_packet_sync.py") != 1:
        failures.append("handoff script must run packet sync check exactly once")
    if text.count("scripts/check_play_upload_blockers.py") != 1:
        failures.append("handoff script must run upload blocker handoff check exactly once")
    if text.count("scripts/check_play_upload_readiness.py --require-upload-ready") != 1:
        failures.append("handoff script must run the strict upload readiness gate exactly once")
    if text.find("scripts/check_play_upload_external_inputs.py") > text.find("scripts/verify_release_candidate.sh"):
        failures.append("external input preflight must happen before the full verifier")
    if text.find("scripts/verify_release_candidate.sh") > text.find("./gradlew :app:printReleaseSigningStatus bundleRelease"):
        failures.append("signed bundle rebuild must happen after the full verifier")
    if text.find("./gradlew :app:printReleaseSigningStatus bundleRelease") > text.find("scripts/check_play_upload_readiness.py --require-upload-ready"):
        failures.append("signed bundle rebuild must happen before strict upload readiness")
    if text.find("scripts/check_play_submission_packet_sync.py") > text.find("scripts/check_play_upload_readiness.py --require-upload-ready"):
        failures.append("packet sync check must happen before strict upload readiness")
    if text.find("scripts/check_play_upload_blockers.py") > text.find("scripts/check_play_upload_readiness.py --require-upload-ready"):
        failures.append("upload blocker handoff check must happen before strict upload readiness")

    return failures


def main() -> int:
    failures: list[str] = []

    if not HANDOFF.exists():
        print(f"FAIL: handoff script is missing: {HANDOFF.relative_to(ROOT)}", file=sys.stderr)
        return 1

    if not os.access(HANDOFF, os.X_OK):
        failures.append("handoff script must be executable")

    syntax = subprocess.run(
        ["bash", "-n", str(HANDOFF)],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if syntax.returncode != 0:
        failures.append("handoff script has invalid bash syntax")
        failures.append(syntax.stdout.strip())

    text = HANDOFF.read_text(encoding="utf-8")
    failures.extend(handoff_failures(text))

    if failures:
        print("Play upload handoff check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: Play upload handoff rebuilds signed bundle and packet after local verifier cleanup")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
