#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

fail() {
  printf 'FAIL: %s\n' "$1" >&2
  exit 1
}

printf '== Poryadok 5 Play upload candidate ==\n'
printf 'Step 1/8: strict release signing input check\n'
scripts/check_release_signing_inputs.py --require

printf 'Step 2/8: external Play upload input preflight\n'
scripts/check_play_upload_external_inputs.py

printf 'Step 3/8: full local RC verification\n'
scripts/verify_release_candidate.sh

printf 'Step 4/8: rebuild signed upload bundle after local verifier cleanup\n'
./gradlew :app:printReleaseSigningStatus bundleRelease --console=plain

printf 'Step 5/8: rebuild Play submission packet with signed AAB\n'
scripts/build_play_submission_packet.sh
scripts/check_release_artifact_manifest.py
scripts/check_play_upload_blockers.py
scripts/check_play_submission_packet_contents.py
scripts/check_play_submission_packet_sync.py

printf 'Step 6/8: strict upload readiness gate\n'
scripts/check_play_upload_readiness.py --require-upload-ready

printf 'Step 7/8: packet checksum verification\n'
(
  cd play-submission
  shasum -a 256 -c checksums.sha256
)

printf 'Step 8/8: upload artifact check\n'
[[ -f play-submission/release/app-release.aab ]] ||
  fail "play-submission/release/app-release.aab is missing"

printf 'PASS: Play upload candidate is ready at play-submission/release/app-release.aab\n'
