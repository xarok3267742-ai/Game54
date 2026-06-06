#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from privacy_policy_common import validate_publishable_policy, validate_support_email

ROOT = Path(__file__).resolve().parents[1]
PUBLISHABLE_HTML = ROOT / "play-submission" / "text" / "privacy_policy_publishable_ru.html"


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def publishable_privacy_policy_failures(policy_file: Path, require: bool, support_email: str) -> list[str]:
    support_email = support_email.strip()
    if require and not support_email:
        return ["set PORYADOK5_SUPPORT_EMAIL when requiring publishable privacy policy validation"]

    if not policy_file.exists():
        if require:
            return [f"publishable privacy policy is missing: {policy_file}"]
        return []

    if support_email and not validate_support_email(support_email):
        return ["PORYADOK5_SUPPORT_EMAIL must be a real non-reserved email address"]

    return validate_publishable_policy(policy_file.read_text(encoding="utf-8"), support_email)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the generated publishable privacy policy file.")
    parser.add_argument("--require", action="store_true")
    parser.add_argument("--support-email", default=os.environ.get("PORYADOK5_SUPPORT_EMAIL", "").strip())
    parser.add_argument("--file", type=Path, default=PUBLISHABLE_HTML)
    args = parser.parse_args()

    policy_file = args.file
    support_email = args.support_email.strip()

    if not policy_file.exists() and not args.require:
        print("PASS: publishable privacy policy is optional in local RC mode and is not generated")
        return 0

    failures = publishable_privacy_policy_failures(policy_file, args.require, support_email)
    if failures:
        print("Publishable privacy policy check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print(f"PASS: publishable privacy policy is ready for hosting ({display_path(policy_file)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
