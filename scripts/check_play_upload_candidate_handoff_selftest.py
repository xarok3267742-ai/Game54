#!/usr/bin/env python3
from __future__ import annotations

import unittest

import check_play_upload_candidate_handoff as checker


VALID_HANDOFF = """#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

fail() {
  printf 'FAIL: %s\\n' "$1" >&2
  exit 1
}

printf 'Step 1/8: strict release signing input check\\n'
scripts/check_release_signing_inputs.py --require

printf 'Step 2/8: external Play upload input preflight\\n'
scripts/check_play_upload_external_inputs.py

printf 'Step 3/8: full local RC verification\\n'
scripts/verify_release_candidate.sh

printf 'Step 4/8: rebuild signed upload bundle after local verifier cleanup\\n'
./gradlew :app:printReleaseSigningStatus bundleRelease --console=plain

printf 'Step 5/8: rebuild Play submission packet with signed AAB\\n'
scripts/build_play_submission_packet.sh
scripts/check_release_artifact_manifest.py
scripts/check_play_upload_blockers.py
scripts/check_play_submission_packet_contents.py
scripts/check_play_submission_packet_sync.py

printf 'Step 6/8: strict upload readiness gate\\n'
scripts/check_play_upload_readiness.py --require-upload-ready

printf 'Step 7/8: packet checksum verification\\n'
(
  cd play-submission
  shasum -a 256 -c checksums.sha256
)

printf 'Step 8/8: upload artifact check\\n'
[[ -f play-submission/release/app-release.aab ]]
"""


class PlayUploadCandidateHandoffSelfTest(unittest.TestCase):
    def assertHasFailureContaining(self, text: str, needle: str) -> None:
        failures = checker.handoff_failures(text)
        self.assertTrue(
            any(needle in failure for failure in failures),
            msg=f"Expected failure containing {needle!r}; got {failures}",
        )

    def test_valid_handoff_fixture_passes(self) -> None:
        self.assertEqual([], checker.handoff_failures(VALID_HANDOFF))

    def test_missing_strict_signing_check_fails(self) -> None:
        handoff = VALID_HANDOFF.replace("scripts/check_release_signing_inputs.py --require\n", "")
        self.assertHasFailureContaining(handoff, "strict signing input check")

    def test_missing_external_input_preflight_fails(self) -> None:
        handoff = VALID_HANDOFF.replace("scripts/check_play_upload_external_inputs.py\n\n", "")
        self.assertHasFailureContaining(handoff, "external input preflight")

    def test_external_input_preflight_after_verifier_fails(self) -> None:
        handoff = VALID_HANDOFF.replace(
            "printf 'Step 2/8: external Play upload input preflight\\n'\n"
            "scripts/check_play_upload_external_inputs.py\n\n"
            "printf 'Step 3/8: full local RC verification\\n'\n"
            "scripts/verify_release_candidate.sh\n",
            "printf 'Step 3/8: full local RC verification\\n'\n"
            "scripts/verify_release_candidate.sh\n\n"
            "printf 'Step 2/8: external Play upload input preflight\\n'\n"
            "scripts/check_play_upload_external_inputs.py\n",
        )
        self.assertHasFailureContaining(handoff, "out of order")

    def test_packet_rebuild_before_signed_bundle_fails(self) -> None:
        handoff = VALID_HANDOFF.replace(
            "./gradlew :app:printReleaseSigningStatus bundleRelease --console=plain\n\n"
            "printf 'Step 5/8: rebuild Play submission packet with signed AAB\\n'\n"
            "scripts/build_play_submission_packet.sh\n",
            "printf 'Step 5/8: rebuild Play submission packet with signed AAB\\n'\n"
            "scripts/build_play_submission_packet.sh\n\n"
            "./gradlew :app:printReleaseSigningStatus bundleRelease --console=plain\n",
        )
        self.assertHasFailureContaining(handoff, "out of order")

    def test_multiple_packet_rebuilds_fail(self) -> None:
        handoff = VALID_HANDOFF.replace(
            "scripts/build_play_submission_packet.sh\n",
            "scripts/build_play_submission_packet.sh\nscripts/build_play_submission_packet.sh\n",
        )
        self.assertHasFailureContaining(handoff, "packet exactly once")

    def test_missing_strict_upload_gate_fails(self) -> None:
        handoff = VALID_HANDOFF.replace("scripts/check_play_upload_readiness.py --require-upload-ready\n", "")
        self.assertHasFailureContaining(handoff, "strict upload readiness")

    def test_missing_packet_sync_check_fails(self) -> None:
        handoff = VALID_HANDOFF.replace("scripts/check_play_submission_packet_sync.py\n", "")
        self.assertHasFailureContaining(handoff, "packet sync check")

    def test_missing_upload_blocker_handoff_check_fails(self) -> None:
        handoff = VALID_HANDOFF.replace("scripts/check_play_upload_blockers.py\n", "")
        self.assertHasFailureContaining(handoff, "upload blocker handoff check")

    def test_missing_shell_safety_fails(self) -> None:
        handoff = VALID_HANDOFF.replace("set -euo pipefail\n", "")
        self.assertHasFailureContaining(handoff, "safety marker")


if __name__ == "__main__":
    unittest.main(verbosity=2)
