#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib import error, request

from privacy_policy_common import (
    PRE_PUBLICATION_CONTACT_TEXT,
    REQUIRED_PRIVACY_SNIPPETS,
    extract_visible_text,
    validate_privacy_url,
    validate_publishable_policy as validate_publishable_policy_markup,
    validate_support_email,
)

ROOT = Path(__file__).resolve().parents[1]
AAB = ROOT / "app" / "build" / "outputs" / "bundle" / "release" / "app-release.aab"
PACKET = ROOT / "play-submission"
ARTIFACT_STATUS = PACKET / "release" / "artifact_status.properties"
RELEASE_ARTIFACT_MANIFEST = PACKET / "release" / "artifact_manifest.json"
RELEASE_ARTIFACT_CHECKER = ROOT / "scripts" / "check_release_artifact_manifest.py"
UPLOAD_BLOCKERS_CHECKER = ROOT / "scripts" / "check_play_upload_blockers.py"
PACKET_SYNC_CHECKER = ROOT / "scripts" / "check_play_submission_packet_sync.py"
PACKET_DOC_COVERAGE_CHECKER = ROOT / "scripts" / "check_play_submission_doc_coverage.py"
SIGNING_INPUT_CHECKER = ROOT / "scripts" / "check_release_signing_inputs.py"
PLAY_FORMS_CHECKER = ROOT / "scripts" / "check_play_console_forms.py"
POLICY_CONTENT_CHECKER = ROOT / "scripts" / "check_policy_content_risk.py"
PRIVACY_HTML = ROOT / "docs" / "privacy_policy_ru.html"
PUBLISHABLE_PRIVACY_HTML = PACKET / "text" / "privacy_policy_publishable_ru.html"
FEATURE_GRAPHIC = ROOT / "store-assets" / "feature-graphic" / "feature-graphic-candidate-03.png"
PLAY_STORE_ICON = ROOT / "store-assets" / "app-icon" / "play-store-icon-512.png"
FORMS_ANSWERS = ROOT / "docs" / "play_console_forms_answers.json"

YES_FLAGS = {
    "PORYADOK5_FEATURE_GRAPHIC_APPROVED": "feature graphic approved in Play Console preview",
    "PORYADOK5_DATA_SAFETY_CONFIRMED": "Data Safety form completed with no data collected/shared",
    "PORYADOK5_TARGET_AUDIENCE_CONFIRMED": "Target Audience and Content completed as 13+ / not children-directed",
    "PORYADOK5_CONTENT_RATING_CONFIRMED": "Content Rating questionnaire completed",
    "PORYADOK5_INTERNAL_TESTING_CONFIRMED": "internal testing track install flow checked from Play-distributed build",
}

REMOTE_PRIVACY_REQUIRED_SNIPPETS = REQUIRED_PRIVACY_SNIPPETS


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)


def warn(message: str) -> None:
    print(f"WARN: {message}")


def ok(message: str) -> None:
    print(f"PASS: {message}")


def note(message: str) -> None:
    print(f"NOTE: {message}")


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


def run(command: list[str], cwd: Path = ROOT) -> tuple[int, str]:
    completed = subprocess.run(
        command,
        cwd=cwd,
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
    if status == 0:
        value = output.strip()
        if value:
            return value

    return None


def verify_packet_checksums() -> bool:
    if not PACKET.exists():
        fail("play-submission directory is missing; run scripts/build_play_submission_packet.sh")
        return False
    checksum_file = PACKET / "checksums.sha256"
    if not checksum_file.exists():
        fail("play-submission/checksums.sha256 is missing")
        return False
    status, output = run(["shasum", "-a", "256", "-c", "checksums.sha256"], cwd=PACKET)
    if status != 0:
        fail("play-submission checksums failed")
        print(output)
        return False
    ok("play-submission checksums are valid")
    return True


def verify_signature(require_upload_ready: bool) -> bool:
    if not AAB.exists():
        fail(f"release AAB is missing: {AAB}")
        return False

    jarsigner = find_jarsigner()
    if jarsigner is None:
        if require_upload_ready:
            fail("jarsigner is required for upload readiness signature verification")
            return False
        warn("jarsigner not found; signature status was not checked in soft RC mode")
        return True

    status, output = run([jarsigner, "-verify", "-verbose", "-certs", str(AAB)])
    unsigned = "jar is unsigned" in output
    signed = status == 0 and "jar verified" in output and not unsigned

    if signed:
        ok("release AAB signature verifies with jarsigner")
        return True

    if unsigned and not require_upload_ready:
        note("release AAB is unsigned; acceptable only for local RC, not Play upload")
        return True

    if unsigned:
        fail("release AAB is unsigned; configure PORYADOK5 signing inputs and rebuild before Play upload")
    else:
        fail("release AAB signature status is not verified")
        print(output)
    return False


def validate_url(value: str) -> bool:
    return validate_privacy_url(value)


def validate_email(value: str) -> bool:
    return validate_support_email(value)


def verify_remote_privacy_policy(privacy_url: str, support_email: str, require_upload_ready: bool) -> bool:
    if not privacy_url:
        return True
    if not validate_url(privacy_url):
        return True

    try:
        remote_request = request.Request(
            privacy_url,
            headers={"User-Agent": "Poryadok5ReleaseCheck/1.0"},
        )
        with request.urlopen(remote_request, timeout=10) as response:
            status = getattr(response, "status", 0)
            content_type = response.headers.get("Content-Type", "")
            raw = response.read(500_000)
    except error.HTTPError as exc:
        status = getattr(exc, "code", 0)
        if require_upload_ready:
            fail(f"privacy policy URL must return HTTP 200, got {status}")
            return False
        warn(f"privacy policy URL returned HTTP {status}; strict upload gate will fail until fixed")
        return True
    except (error.URLError, OSError, TimeoutError) as exc:
        if require_upload_ready:
            fail(f"privacy policy URL is not reachable: {exc}")
            return False
        warn(f"privacy policy URL was not reachable during soft audit: {exc}")
        return True

    if status != 200:
        if require_upload_ready:
            fail(f"privacy policy URL must return HTTP 200, got {status}")
            return False
        warn(f"privacy policy URL returned HTTP {status}; strict upload gate will fail until fixed")
        return True

    charset = "utf-8"
    charset_match = re.search(r"charset=([\w.-]+)", content_type, re.IGNORECASE)
    if charset_match:
        charset = charset_match.group(1)

    try:
        body = raw.decode(charset)
    except (LookupError, UnicodeDecodeError):
        body = raw.decode("utf-8", errors="replace")

    visible_text = extract_visible_text(body)
    failures: list[str] = []

    if len(raw) >= 500_000:
        failures.append("published privacy policy response is unexpectedly large")
    for snippet in REMOTE_PRIVACY_REQUIRED_SNIPPETS:
        if snippet not in visible_text:
            failures.append(f"published privacy policy is missing text: {snippet}")
    if PRE_PUBLICATION_CONTACT_TEXT in visible_text:
        failures.append("published privacy policy still contains the pre-publication contact instruction")
    if support_email and validate_email(support_email) and support_email not in visible_text:
        failures.append("published privacy policy does not contain PORYADOK5_SUPPORT_EMAIL")

    if failures:
        for failure in failures:
            if require_upload_ready:
                fail(failure)
            else:
                warn(failure)
        return not require_upload_ready

    ok("published privacy policy URL is reachable and matches no-data claims")
    return True


def publishable_privacy_policy_failures(support_email: str) -> list[str]:
    if not PUBLISHABLE_PRIVACY_HTML.exists():
        try:
            display_path = PUBLISHABLE_PRIVACY_HTML.relative_to(ROOT)
        except ValueError:
            display_path = PUBLISHABLE_PRIVACY_HTML
        return [f"publishable privacy policy is missing: {display_path}"]
    return validate_publishable_policy_markup(PUBLISHABLE_PRIVACY_HTML.read_text(encoding="utf-8"), support_email)


def publishable_privacy_policy_ready(support_email: str) -> bool:
    return not publishable_privacy_policy_failures(support_email)


def verify_manual_upload_inputs(require_upload_ready: bool) -> bool:
    passed = True

    privacy_url = os.environ.get("PORYADOK5_PRIVACY_POLICY_URL", "").strip()
    support_email = os.environ.get("PORYADOK5_SUPPORT_EMAIL", "").strip()

    privacy_url_valid = bool(privacy_url and validate_url(privacy_url))
    if privacy_url_valid:
        ok("PORYADOK5_PRIVACY_POLICY_URL is a stable-looking HTTPS URL")
    elif require_upload_ready:
        if privacy_url:
            fail("PORYADOK5_PRIVACY_POLICY_URL is set but is not a valid public HTTPS URL")
        else:
            fail("set PORYADOK5_PRIVACY_POLICY_URL to the published HTTPS privacy policy URL")
        passed = False
    elif privacy_url:
        warn("PORYADOK5_PRIVACY_POLICY_URL is set but is not a valid public HTTPS URL for Play upload")
    else:
        note("PORYADOK5_PRIVACY_POLICY_URL is not set; public privacy URL remains an external action")

    support_email_valid = bool(support_email and validate_email(support_email))
    if support_email_valid:
        ok("PORYADOK5_SUPPORT_EMAIL is set")
    elif require_upload_ready:
        if support_email:
            fail("PORYADOK5_SUPPORT_EMAIL is set but is not a valid non-reserved support email")
        else:
            fail("set PORYADOK5_SUPPORT_EMAIL to the developer support email used in Play Console")
        passed = False
    elif support_email:
        warn("PORYADOK5_SUPPORT_EMAIL is set but is not a valid non-reserved support email")
    else:
        note("PORYADOK5_SUPPORT_EMAIL is not set; developer contact remains an external action")

    if PRIVACY_HTML.exists():
        html = PRIVACY_HTML.read_text(encoding="utf-8")
        if PRE_PUBLICATION_CONTACT_TEXT in html:
            policy_failures = publishable_privacy_policy_failures(support_email if support_email_valid else "")
            if not policy_failures:
                ok("publishable privacy policy contains a real developer contact line")
            elif require_upload_ready:
                fail("generate and host a publishable privacy policy with a real developer contact line before Play upload")
                for policy_failure in policy_failures:
                    fail(policy_failure)
                passed = False
            else:
                note("privacy policy HTML still contains the pre-publication contact instruction")
                if PUBLISHABLE_PRIVACY_HTML.exists():
                    for policy_failure in policy_failures:
                        warn(policy_failure)
        else:
            ok("privacy policy HTML contact line has been replaced locally")
    else:
        fail(f"privacy policy HTML is missing: {PRIVACY_HTML}")
        passed = False

    if privacy_url_valid:
        passed = verify_remote_privacy_policy(privacy_url, support_email, require_upload_ready) and passed

    if FEATURE_GRAPHIC.exists():
        ok("feature graphic candidate exists")
    else:
        fail(f"feature graphic candidate is missing: {FEATURE_GRAPHIC}")
        passed = False

    if PLAY_STORE_ICON.exists():
        ok("Play Store app icon exists")
    else:
        fail(f"Play Store app icon is missing: {PLAY_STORE_ICON}")
        passed = False

    if FORMS_ANSWERS.exists():
        ok("structured Play Console form answers exist")
    else:
        fail(f"structured Play Console form answers are missing: {FORMS_ANSWERS}")
        passed = False

    for name, description in YES_FLAGS.items():
        value = os.environ.get(name, "").strip().lower()
        if value == "yes":
            ok(f"{description}: confirmed")
            continue
        if require_upload_ready:
            fail(f"set {name}=yes after confirming: {description}")
            passed = False
        elif value:
            warn(f"{name} is set to {value!r}; use yes only after confirming: {description}")
        else:
            note(f"{description}: not confirmed in environment")

    return passed


def verify_packet_artifact_state(require_upload_ready: bool) -> bool:
    values = read_properties(ARTIFACT_STATUS)
    if not values:
        fail(f"artifact status file is missing or empty: {ARTIFACT_STATUS}")
        return False

    signed_or_configured = values.get("signed_or_configured") == "true"
    artifact = values.get("artifact", "")

    if signed_or_configured and artifact == "release/app-release.aab":
        packet_aab = PACKET / artifact
        if packet_aab.exists():
            ok("play-submission includes release/app-release.aab")
            return True
        fail("artifact status says signed AAB is included, but release/app-release.aab is missing")
        return False

    if require_upload_ready:
        fail("play-submission does not include a signed/configured release AAB")
        return False

    note("play-submission marks the AAB as not included for upload because signing inputs are absent")
    return True


def verify_artifact_manifest_upload_state(require_upload_ready: bool) -> bool:
    if not RELEASE_ARTIFACT_MANIFEST.exists():
        message = f"release artifact manifest is missing: {RELEASE_ARTIFACT_MANIFEST}"
        if require_upload_ready:
            fail(message)
            return False
        warn(f"{message}; strict upload gate will fail until the packet is rebuilt")
        return True

    try:
        manifest = json.loads(RELEASE_ARTIFACT_MANIFEST.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        message = f"release artifact manifest is invalid JSON: {exc}"
        if require_upload_ready:
            fail(message)
            return False
        warn(f"{message}; strict upload gate will fail until the packet is rebuilt")
        return True

    upload_blockers = manifest.get("uploadBlockers")
    play_upload_ready = manifest.get("playUploadReady")

    if not isinstance(upload_blockers, list) or not all(isinstance(item, str) for item in upload_blockers):
        message = "release artifact manifest uploadBlockers must be a list of strings"
        if require_upload_ready:
            fail(message)
            return False
        warn(f"{message}; strict upload gate will fail until the packet is rebuilt")
        return True

    if not isinstance(play_upload_ready, bool):
        message = "release artifact manifest playUploadReady must be a boolean"
        if require_upload_ready:
            fail(message)
            return False
        warn(f"{message}; strict upload gate will fail until the packet is rebuilt")
        return True

    expected_ready = not upload_blockers
    if play_upload_ready != expected_ready:
        message = "release artifact manifest playUploadReady is out of sync with uploadBlockers"
        if require_upload_ready:
            fail(message)
            return False
        warn(f"{message}; strict upload gate will fail until the packet is rebuilt")
        return True

    if upload_blockers:
        blocker_text = ", ".join(upload_blockers)
        if require_upload_ready:
            fail(f"release artifact manifest still has upload blockers: {blocker_text}")
            return False
        note(f"release artifact manifest upload blockers remain external or signing-gated: {blocker_text}")
        return True

    if play_upload_ready is True:
        ok("release artifact manifest marks Play upload as ready")
        return True

    message = "release artifact manifest does not mark playUploadReady=true"
    if require_upload_ready:
        fail(message)
        return False
    warn(f"{message}; strict upload gate will fail until the packet is rebuilt")
    return True


def verify_artifact_manifest_current_state() -> bool:
    if not RELEASE_ARTIFACT_CHECKER.exists():
        fail(f"release artifact manifest checker is missing: {RELEASE_ARTIFACT_CHECKER}")
        return False

    status, output = run([sys.executable, str(RELEASE_ARTIFACT_CHECKER)])
    if status == 0:
        print(output.rstrip())
        return True

    fail("release artifact manifest does not match current build and packet state")
    print(output)
    return False


def verify_upload_blocker_handoff_state() -> bool:
    if not UPLOAD_BLOCKERS_CHECKER.exists():
        fail(f"Play upload blocker handoff checker is missing: {UPLOAD_BLOCKERS_CHECKER}")
        return False

    status, output = run([sys.executable, str(UPLOAD_BLOCKERS_CHECKER)])
    if output.strip():
        print(output.rstrip())
    if status == 0:
        return True

    fail("Play upload blocker handoff is not synchronized with the release artifact manifest")
    return False


def verify_packet_sync_state() -> bool:
    if not PACKET_SYNC_CHECKER.exists():
        fail(f"Play submission packet sync checker is missing: {PACKET_SYNC_CHECKER}")
        return False

    status, output = run([sys.executable, str(PACKET_SYNC_CHECKER)])
    if output.strip():
        print(output.rstrip())
    if status == 0:
        return True

    fail("Play submission packet is not synchronized with source materials")
    return False


def verify_packet_doc_coverage_state() -> bool:
    if not PACKET_DOC_COVERAGE_CHECKER.exists():
        fail(f"Play submission documentation coverage checker is missing: {PACKET_DOC_COVERAGE_CHECKER}")
        return False

    status, output = run([sys.executable, str(PACKET_DOC_COVERAGE_CHECKER)])
    if output.strip():
        print(output.rstrip())
    if status == 0:
        return True

    fail("Play submission packet does not cover required RC documentation")
    return False


def verify_release_signing_inputs(require_upload_ready: bool) -> bool:
    if not SIGNING_INPUT_CHECKER.exists():
        fail(f"release signing input checker is missing: {SIGNING_INPUT_CHECKER}")
        return False

    command = [sys.executable, str(SIGNING_INPUT_CHECKER)]
    if require_upload_ready:
        command.append("--require")

    status, output = run(command)
    if status == 0:
        print(output.rstrip())
        return True

    if require_upload_ready:
        fail("release signing inputs are required for Play upload readiness")
    else:
        fail("release signing inputs are partially configured or invalid")
    print(output)
    return False


def verify_play_console_evidence() -> bool:
    passed = True
    for label, checker in (
        ("Play Console forms checker", PLAY_FORMS_CHECKER),
        ("policy content risk checker", POLICY_CONTENT_CHECKER),
    ):
        if not checker.exists():
            fail(f"{label} is missing: {checker}")
            passed = False
            continue

        status, output = run([sys.executable, str(checker)])
        if output.strip():
            print(output.rstrip())
        if status == 0:
            continue

        fail(f"{label} failed")
        passed = False

    return passed


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Poryadok 5 Play upload readiness.")
    parser.add_argument(
        "--require-upload-ready",
        action="store_true",
        help="fail unless signed AAB, public privacy URL and manual Play Console confirmations are present",
    )
    args = parser.parse_args()

    require_upload_ready = args.require_upload_ready
    print("== Poryadok 5 Play upload readiness ==")
    if require_upload_ready:
        print("Mode: strict upload gate")
    else:
        print("Mode: local RC audit")

    checks = [
        verify_packet_checksums(),
        verify_packet_sync_state(),
        verify_packet_doc_coverage_state(),
        verify_packet_artifact_state(require_upload_ready),
        verify_artifact_manifest_current_state(),
        verify_upload_blocker_handoff_state(),
        verify_artifact_manifest_upload_state(require_upload_ready),
        verify_release_signing_inputs(require_upload_ready),
        verify_signature(require_upload_ready),
        verify_play_console_evidence(),
        verify_manual_upload_inputs(require_upload_ready),
    ]

    if all(checks):
        if require_upload_ready:
            ok("Play upload readiness gate passed")
        else:
            ok("Local RC audit passed; remaining Play upload work is explicitly external")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
