#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RENDERER = ROOT / "scripts" / "render_privacy_policy.py"
CHECKER = ROOT / "scripts" / "check_publishable_privacy_policy.py"
SOURCE = ROOT / "docs" / "privacy_policy_ru.html"
SUPPORT_EMAIL = "support@poryadok5.app"


def run(command: list[str], env: dict[str, str] | None = None) -> tuple[int, str]:
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


def without_poryadok_env() -> dict[str, str]:
    return {key: value for key, value in os.environ.items() if not key.startswith("PORYADOK5_")}


def main() -> int:
    failures: list[str] = []

    for script in (RENDERER, CHECKER):
        if not script.exists():
            failures.append(f"missing script: {script.relative_to(ROOT)}")
        elif not os.access(script, os.X_OK):
            failures.append(f"script must be executable: {script.relative_to(ROOT)}")
    if not SOURCE.exists():
        failures.append(f"missing privacy policy source: {SOURCE.relative_to(ROOT)}")

    if failures:
        print("Publishable privacy policy CLI self-test failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory(prefix="poryadok5-policy-cli.") as tmp_dir:
        output = Path(tmp_dir) / "privacy_policy_publishable_ru.html"
        base_env = without_poryadok_env()

        status, text = run(
            [
                str(RENDERER),
                "--source",
                str(SOURCE),
                "--output",
                str(output),
                "--support-email",
                SUPPORT_EMAIL,
                "--require",
            ],
            env=base_env,
        )
        if status != 0:
            failures.append("renderer failed with explicit support email")
            failures.append(text.strip())
        elif not output.exists():
            failures.append("renderer did not create the requested output file")

        status, text = run(
            [
                str(CHECKER),
                "--file",
                str(output),
                "--support-email",
                SUPPORT_EMAIL,
                "--require",
            ],
            env=base_env,
        )
        if status != 0:
            failures.append("checker rejected renderer output")
            failures.append(text.strip())

        missing_email_output = Path(tmp_dir) / "missing_email.html"
        status, text = run(
            [
                str(RENDERER),
                "--source",
                str(SOURCE),
                "--output",
                str(missing_email_output),
                "--require",
            ],
            env=base_env,
        )
        if status == 0:
            failures.append("renderer unexpectedly passed --require without support email")
        if missing_email_output.exists():
            failures.append("renderer created output even though support email was absent")
        if "set PORYADOK5_SUPPORT_EMAIL" not in text:
            failures.append("renderer did not report the missing support email")

        status, text = run(
            [
                str(CHECKER),
                "--file",
                str(output),
                "--support-email",
                "support@example.com",
                "--require",
            ],
            env=base_env,
        )
        if status == 0:
            failures.append("checker unexpectedly accepted a reserved support email domain")
        if "real non-reserved email address" not in text:
            failures.append("checker did not report reserved support email")

    if failures:
        print("Publishable privacy policy CLI self-test failed:", file=sys.stderr)
        for failure in failures:
            if failure:
                print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: publishable privacy policy CLI renders and validates host-ready HTML")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
