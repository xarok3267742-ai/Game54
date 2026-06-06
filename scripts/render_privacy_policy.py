#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from privacy_policy_common import (
    render_publishable_policy,
    validate_publishable_policy,
    validate_support_email,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "privacy_policy_ru.html"
OUTPUT = ROOT / "play-submission" / "text" / "privacy_policy_publishable_ru.html"


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render the publishable Poryadok 5 privacy policy with a real support email.",
    )
    parser.add_argument("--support-email", default=os.environ.get("PORYADOK5_SUPPORT_EMAIL", "").strip())
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--require", action="store_true")
    args = parser.parse_args()

    support_email = args.support_email.strip()
    if not support_email:
        if args.require:
            print("FAIL: set PORYADOK5_SUPPORT_EMAIL before rendering the publishable privacy policy", file=sys.stderr)
            return 1
        print("NOTE: PORYADOK5_SUPPORT_EMAIL is not set; publishable privacy policy was not generated")
        return 0

    if not validate_support_email(support_email):
        print("FAIL: PORYADOK5_SUPPORT_EMAIL must be a real non-reserved email address", file=sys.stderr)
        return 1

    source = args.source
    output = args.output
    if not source.exists():
        print(f"FAIL: privacy policy source is missing: {source}", file=sys.stderr)
        return 1

    try:
        rendered = render_publishable_policy(source.read_text(encoding="utf-8"), support_email)
    except ValueError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    failures = validate_publishable_policy(rendered, support_email)
    if failures:
        print("Publishable privacy policy render check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")
    print(f"Built {display_path(output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
