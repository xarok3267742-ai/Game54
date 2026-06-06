#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "scripts" / "prepare_play_upload_candidate.sh"

FORBIDDEN_OUTPUT_MARKERS = (
    "Step 2/8",
    "external Play upload input preflight",
    "Step 3/8",
    "full local RC verification",
    "Step 4/8",
    "bundleRelease",
    "Step 5/8",
    "Built play-submission",
    "check_play_submission_packet_sync.py",
    "Play upload candidate is ready",
)


def main() -> int:
    if not HANDOFF.exists():
        print(f"FAIL: handoff script is missing: {HANDOFF.relative_to(ROOT)}", file=sys.stderr)
        return 1

    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("PORYADOK5_")
    }

    with tempfile.TemporaryDirectory(prefix="poryadok5-empty-gradle-home.") as gradle_home:
        env["GRADLE_USER_HOME"] = gradle_home
        completed = subprocess.run(
            [str(HANDOFF)],
            cwd=ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=30,
            check=False,
        )

    output = completed.stdout
    failures: list[str] = []

    if completed.returncode == 0:
        failures.append("handoff unexpectedly passed without release signing inputs")
    if "Step 1/8: strict release signing input check" not in output:
        failures.append("handoff did not reach the strict signing input check")
    if "release signing inputs are not configured" not in output:
        failures.append("handoff did not report missing release signing inputs")
    for marker in FORBIDDEN_OUTPUT_MARKERS:
        if marker in output:
            failures.append(f"handoff continued past signing preflight: {marker}")

    if failures:
        print("Prepare Play upload candidate negative-path check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        print(output, file=sys.stderr)
        return 1

    print("PASS: Play upload candidate handoff fails before verifier when signing inputs are absent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
