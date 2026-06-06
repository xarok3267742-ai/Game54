#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import sys
from urllib import error, request

from privacy_policy_common import (
    PRE_PUBLICATION_CONTACT_TEXT,
    REQUIRED_PRIVACY_SNIPPETS,
    extract_visible_text,
    validate_privacy_url,
    validate_support_email,
)


YES_FLAGS = {
    "PORYADOK5_FEATURE_GRAPHIC_APPROVED": "feature graphic approved in Play Console preview",
    "PORYADOK5_DATA_SAFETY_CONFIRMED": "Data Safety form completed with no data collected/shared",
    "PORYADOK5_TARGET_AUDIENCE_CONFIRMED": "Target Audience and Content completed as 13+ / not children-directed",
    "PORYADOK5_CONTENT_RATING_CONFIRMED": "Content Rating questionnaire completed",
    "PORYADOK5_INTERNAL_TESTING_CONFIRMED": "internal testing track install flow checked from Play-distributed build",
}


def remote_privacy_policy_failures(privacy_url: str, support_email: str) -> list[str]:
    failures: list[str] = []
    try:
        remote_request = request.Request(
            privacy_url,
            headers={"User-Agent": "Poryadok5ExternalInputsCheck/1.0"},
        )
        with request.urlopen(remote_request, timeout=10) as response:
            status = getattr(response, "status", 0)
            content_type = response.headers.get("Content-Type", "")
            raw = response.read(500_000)
    except error.HTTPError as exc:
        status = getattr(exc, "code", 0)
        return [f"privacy policy URL must return HTTP 200, got {status}"]
    except (error.URLError, OSError, TimeoutError) as exc:
        return [f"privacy policy URL is not reachable: {exc}"]

    if status != 200:
        return [f"privacy policy URL must return HTTP 200, got {status}"]

    charset = "utf-8"
    charset_match = re.search(r"charset=([\w.-]+)", content_type, re.IGNORECASE)
    if charset_match:
        charset = charset_match.group(1)

    try:
        body = raw.decode(charset)
    except (LookupError, UnicodeDecodeError):
        body = raw.decode("utf-8", errors="replace")

    visible_text = extract_visible_text(body)
    if len(raw) >= 500_000:
        failures.append("published privacy policy response is unexpectedly large")
    for snippet in REQUIRED_PRIVACY_SNIPPETS:
        if snippet not in visible_text:
            failures.append(f"published privacy policy is missing text: {snippet}")
    if PRE_PUBLICATION_CONTACT_TEXT in visible_text:
        failures.append("published privacy policy still contains the pre-publication contact instruction")
    if support_email not in visible_text:
        failures.append("published privacy policy does not contain PORYADOK5_SUPPORT_EMAIL")

    return failures


def external_input_failures(env: dict[str, str] | None = None) -> list[str]:
    values = env if env is not None else os.environ
    failures: list[str] = []

    privacy_url = values.get("PORYADOK5_PRIVACY_POLICY_URL", "").strip()
    support_email = values.get("PORYADOK5_SUPPORT_EMAIL", "").strip()

    privacy_url_valid = bool(privacy_url and validate_privacy_url(privacy_url))
    support_email_valid = bool(support_email and validate_support_email(support_email))

    if not privacy_url_valid:
        if privacy_url:
            failures.append("PORYADOK5_PRIVACY_POLICY_URL is set but is not a valid public HTTPS URL")
        else:
            failures.append("set PORYADOK5_PRIVACY_POLICY_URL to the published HTTPS privacy policy URL")

    if not support_email_valid:
        if support_email:
            failures.append("PORYADOK5_SUPPORT_EMAIL is set but is not a valid non-reserved support email")
        else:
            failures.append("set PORYADOK5_SUPPORT_EMAIL to the developer support email used in Play Console")

    for name, description in YES_FLAGS.items():
        value = values.get(name, "").strip().lower()
        if value != "yes":
            failures.append(f"set {name}=yes after confirming: {description}")

    if privacy_url_valid and support_email_valid:
        failures.extend(remote_privacy_policy_failures(privacy_url, support_email))

    return failures


def main() -> int:
    failures = external_input_failures()
    if failures:
        print("Play upload external input check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: Play upload external inputs are configured and privacy policy URL is live")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
