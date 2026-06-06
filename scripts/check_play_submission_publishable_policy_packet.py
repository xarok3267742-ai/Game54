#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "play-submission"
PUBLISHABLE_POLICY = PACKET / "text" / "privacy_policy_publishable_ru.html"
CHECKSUMS = PACKET / "checksums.sha256"
PUBLISHABLE_POLICY_CHECKSUM_ENTRY = "./text/privacy_policy_publishable_ru.html"
TEST_SUPPORT_EMAIL = "support@poryadok5.app"


def run(command: list[str], *, env: dict[str, str]) -> tuple[int, str]:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    return completed.returncode, completed.stdout


def fail(message: str, output: str = "") -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    if output:
        print(output, file=sys.stderr)


def build_packet(env: dict[str, str]) -> tuple[int, str]:
    return run([str(ROOT / "scripts" / "build_play_submission_packet.sh")], env=env)


def publishable_policy_packet_file_failures(packet: Path = PACKET) -> list[str]:
    failures: list[str] = []
    publishable_policy = packet / "text" / "privacy_policy_publishable_ru.html"
    checksums = packet / "checksums.sha256"

    if not publishable_policy.exists():
        failures.append("packet builder did not generate text/privacy_policy_publishable_ru.html")
    if checksums.exists():
        checksums_text = checksums.read_text(encoding="utf-8")
        if PUBLISHABLE_POLICY_CHECKSUM_ENTRY not in checksums_text:
            failures.append("checksums.sha256 does not include text/privacy_policy_publishable_ru.html")
    else:
        failures.append("checksums.sha256 is missing after packet build")

    return failures


def restore_packet(original_support_email: str | None) -> list[str]:
    restore_env = os.environ.copy()
    if original_support_email is None:
        restore_env.pop("PORYADOK5_SUPPORT_EMAIL", None)
    else:
        restore_env["PORYADOK5_SUPPORT_EMAIL"] = original_support_email

    status, output = build_packet(restore_env)
    if status != 0:
        return [f"failed to restore play-submission packet after publishable-policy smoke:\n{output}"]

    return []


def main() -> int:
    original_support_email = os.environ.get("PORYADOK5_SUPPORT_EMAIL")
    failures: list[str] = []

    try:
        test_env = os.environ.copy()
        test_env["PORYADOK5_SUPPORT_EMAIL"] = TEST_SUPPORT_EMAIL

        status, output = build_packet(test_env)
        if status != 0:
            failures.append(f"packet builder failed with a real support email:\n{output}")
        else:
            failures.extend(publishable_policy_packet_file_failures(PACKET))

            checks = (
                [
                    str(ROOT / "scripts" / "check_publishable_privacy_policy.py"),
                    "--require",
                    "--support-email",
                    TEST_SUPPORT_EMAIL,
                ],
                [str(ROOT / "scripts" / "check_play_submission_packet_contents.py")],
                ["shasum", "-a", "256", "-c", "checksums.sha256"],
            )
            for command in checks:
                cwd = PACKET if command[0] == "shasum" else ROOT
                completed = subprocess.run(
                    command,
                    cwd=cwd,
                    env=test_env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    check=False,
                )
                if completed.returncode != 0:
                    failures.append(f"{' '.join(command)} failed:\n{completed.stdout}")

    finally:
        failures.extend(restore_packet(original_support_email))

    if failures:
        print("Play submission publishable policy packet check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: Play submission packet includes validated publishable privacy policy when support email is set")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
