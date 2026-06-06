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
    "Step 3/8",
    "full local RC verification",
    "Step 4/8",
    "bundleRelease",
    "Step 5/8",
    "Built play-submission",
    "check_play_submission_packet_sync.py",
    "Play upload candidate is ready",
)


def find_keytool() -> str | None:
    java_home = os.environ.get("JAVA_HOME", "").strip()
    if java_home:
        candidate = Path(java_home) / "bin" / "keytool"
        if candidate.exists() and os.access(candidate, os.X_OK):
            return str(candidate)

    studio_jbr = Path("/Applications/Android Studio.app/Contents/jbr/Contents/Home/bin/keytool")
    if studio_jbr.exists() and os.access(studio_jbr, os.X_OK):
        return str(studio_jbr)

    completed = subprocess.run(
        ["/usr/bin/env", "sh", "-c", "command -v keytool"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    value = completed.stdout.strip()
    return value if completed.returncode == 0 and value else None


def create_temp_keystore(keytool: str, tmp_path: Path) -> tuple[Path, str, str]:
    keystore = tmp_path / "poryadok5-upload-negative-path.jks"
    alias = "poryadok5-upload-negative-path"
    password = "Poryadok5NegativePath123"
    completed = subprocess.run(
        [
            keytool,
            "-genkeypair",
            "-v",
            "-keystore",
            str(keystore),
            "-storetype",
            "JKS",
            "-storepass",
            password,
            "-keypass",
            password,
            "-alias",
            alias,
            "-keyalg",
            "RSA",
            "-keysize",
            "2048",
            "-validity",
            "30",
            "-dname",
            "CN=Poryadok5 External Inputs Negative Path, OU=Local QA, O=Ivliev, L=Local, ST=Local, C=US",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"keytool failed to create temporary keystore:\n{completed.stdout}")
    return keystore, alias, password


def main() -> int:
    if not HANDOFF.exists():
        print(f"FAIL: handoff script is missing: {HANDOFF.relative_to(ROOT)}", file=sys.stderr)
        return 1

    keytool = find_keytool()
    if keytool is None:
        print("FAIL: keytool not found. Install JDK or set JAVA_HOME.", file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory(prefix="poryadok5-external-inputs-negative-path.") as tmp_dir:
        tmp_path = Path(tmp_dir)
        gradle_home = tmp_path / "gradle-user-home"
        gradle_home.mkdir()
        keystore, alias, password = create_temp_keystore(keytool, tmp_path)

        env = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith("PORYADOK5_")
        }
        env.update(
            {
                "GRADLE_USER_HOME": str(gradle_home),
                "PORYADOK5_KEYSTORE_PATH": str(keystore),
                "PORYADOK5_KEYSTORE_PASSWORD": password,
                "PORYADOK5_KEY_ALIAS": alias,
                "PORYADOK5_KEY_PASSWORD": password,
            },
        )

        completed = subprocess.run(
            [str(HANDOFF)],
            cwd=ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=60,
            check=False,
        )

    output = completed.stdout
    failures: list[str] = []

    if completed.returncode == 0:
        failures.append("handoff unexpectedly passed without external Play upload inputs")
    if "Step 1/8: strict release signing input check" not in output:
        failures.append("handoff did not reach the strict signing input check")
    if "PASS: release signing inputs are complete" not in output:
        failures.append("handoff did not pass signing preflight with temporary signing inputs")
    if "Step 2/8: external Play upload input preflight" not in output:
        failures.append("handoff did not reach external input preflight")
    if "Play upload external input check failed" not in output:
        failures.append("handoff did not report external input preflight failure")
    if "set PORYADOK5_PRIVACY_POLICY_URL" not in output:
        failures.append("handoff did not report missing privacy policy URL")
    if "set PORYADOK5_SUPPORT_EMAIL" not in output:
        failures.append("handoff did not report missing support email")
    for marker in FORBIDDEN_OUTPUT_MARKERS:
        if marker in output:
            failures.append(f"handoff continued past external input preflight: {marker}")

    if failures:
        print("Prepare Play upload candidate external-input negative-path check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        print(output, file=sys.stderr)
        return 1

    print("PASS: Play upload candidate handoff fails before verifier when external upload inputs are absent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
