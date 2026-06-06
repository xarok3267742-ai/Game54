# Play Upload Handoff

This is the final handoff path for producing the upload packet after all external Play Console inputs are available.

## Required Inputs

Release signing can come from environment variables or from a local Gradle properties file outside this repository:

- `PORYADOK5_KEYSTORE_PATH`
- `PORYADOK5_KEYSTORE_PASSWORD`
- `PORYADOK5_KEY_ALIAS`
- `PORYADOK5_KEY_PASSWORD`

Strict Play upload confirmation values must be exported in the shell that runs the handoff:

```bash
export PORYADOK5_SUPPORT_EMAIL="support@poryadok5.app"
export PORYADOK5_FEATURE_GRAPHIC_APPROVED=yes
export PORYADOK5_DATA_SAFETY_CONFIRMED=yes
export PORYADOK5_TARGET_AUDIENCE_CONFIRMED=yes
export PORYADOK5_CONTENT_RATING_CONFIRMED=yes
export PORYADOK5_INTERNAL_TESTING_CONFIRMED=yes
```

With `PORYADOK5_SUPPORT_EMAIL` set, `scripts/build_play_submission_packet.sh` generates `play-submission/text/privacy_policy_publishable_ru.html`. Publish that file, or equivalent content, at a stable public HTTPS URL and then export it before running the final handoff:

```bash
export PORYADOK5_PRIVACY_POLICY_URL="https://privacy.poryadok5.app/policy"
```

## Command

Run:

```bash
scripts/prepare_play_upload_candidate.sh
```

The script performs:

1. Strict release signing input check through `scripts/check_release_signing_inputs.py --require`.
2. External upload input preflight through `scripts/check_play_upload_external_inputs.py`, covering support email, public privacy URL, live privacy policy content and manual Play Console confirmation flags before expensive local rebuild work starts.
3. Full local RC verification through `scripts/verify_release_candidate.sh`.
4. Signed release bundle rebuild through `./gradlew :app:printReleaseSigningStatus bundleRelease --console=plain`, because the local verifier deliberately restores the unsigned RC state after its temporary signing smoke test.
5. Play submission packet rebuild through `scripts/build_play_submission_packet.sh`, followed by `scripts/check_release_artifact_manifest.py`, `scripts/check_play_upload_blockers.py`, `scripts/check_play_submission_packet_contents.py` and `scripts/check_play_submission_packet_sync.py`.
6. Strict upload gate through `scripts/check_play_upload_readiness.py --require-upload-ready`, including release signing input validation, generated privacy policy contact validation, Play Console form evidence, policy content risk, release artifact manifest freshness and blocker validation, a live HTTP 200 check for the published privacy policy URL and expected no-data-collection text.
7. `play-submission/checksums.sha256` verification.
8. Final check that `play-submission/release/app-release.aab` exists.

## Expected Output

When all external inputs are complete, the upload artifact is:

```text
play-submission/release/app-release.aab
```

The `play-submission` packet also contains Play listing text, privacy policy HTML, generated publishable privacy policy HTML when support email is set, Play Console form answers, project README/agent notes, the full RC documentation set from `docs/doc_inventory.md`, store screenshots, app icon, feature graphic candidate, release docs and checksums.

Release artifact identity is recorded in `play-submission/release/artifact_manifest.json`, including Gradle-derived app id/version metadata, APK/AAB SHA-256 values, byte sizes, signing status, Play form/policy evidence state and current upload blockers. `play-submission/release/upload_blockers.json` expands those blocker ids into the current action/evidence handoff and is checked against the artifact manifest by `scripts/check_play_upload_blockers.py`.

Packet contents are allowlisted by `scripts/check_play_submission_packet_contents.py`, so unexpected build outputs, QA files, local config files and key/keystore-like artifacts fail the local RC verifier. Packet source freshness is checked by `scripts/check_play_submission_packet_sync.py`, which compares copied project notes, docs, assets and screenshots byte-for-byte with source files and validates that `checksums.sha256` covers the current packet files without stale entries. Required RC documentation coverage is checked by `scripts/check_play_submission_doc_coverage.py`, which ties the packet back to `scripts/check_doc_inventory.py`.

`scripts/check_release_artifact_manifest.py` also verifies that app id/version metadata stays synchronized with `app/build.gradle.kts`, that artifact path fields point to the expected local and packet outputs, that an included signed packet AAB has the same SHA-256 and byte size as the current release AAB, that unsigned or unverified AABs are not marked as upload artifacts, and that Play form/policy evidence blockers match the current checker results. The strict upload gate runs the same checker and the upload-blocker handoff checker again, verifies the current external signing inputs, reruns Play Console forms and policy content evidence, then requires the generated manifest to report `playUploadReady=true` with no `uploadBlockers` and the blocker handoff to have an empty `blockers` array.

The handoff ordering is checked by `scripts/check_play_upload_candidate_handoff.py` so external upload inputs are checked before the full verifier, and the signed AAB is rebuilt after local verifier cleanup and before strict upload readiness. `scripts/check_play_upload_candidate_handoff_selftest.py` covers the handoff checker against missing strict signing checks, missing external input preflight, packet rebuilds before the signed bundle, duplicate packet rebuilds, missing strict upload gates and missing shell safety markers. `scripts/check_prepare_play_upload_candidate_negative_path.py` runs the handoff with isolated empty signing configuration and verifies that it fails at Step 1 before the external input preflight, full verifier, signed rebuild or packet rebuild. `scripts/check_prepare_play_upload_candidate_external_inputs_negative_path.py` runs the handoff with a temporary external keystore and verifies that missing privacy/support/manual Play inputs fail at Step 2 before the full verifier or rebuild work.

## Current Expected Failure

In the current local environment the handoff is expected to fail strict mode because the signed upload AAB, public privacy policy URL, real support email and Play Console manual confirmations are not available locally. That failure is intentional and keeps the local RC packet separate from an actual Play-upload-ready packet.
