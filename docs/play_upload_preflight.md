# Play Upload Preflight

This preflight separates local RC evidence from actual Play upload readiness.

## Local RC Audit

Run this after building the submission packet:

```bash
scripts/build_play_submission_packet.sh
scripts/check_play_upload_readiness.py
```

Expected in the current repository: pass, with notes for external actions that cannot be completed locally without secrets, a public URL and Play Console access.

The local audit checks:

- `play-submission/checksums.sha256` is valid;
- copied packet project notes, docs, assets and screenshots match source materials byte-for-byte through `scripts/check_play_submission_packet_sync.py`;
- every required RC document from `scripts/check_doc_inventory.py` is present in the packet with the expected destination and allowlist entry through `scripts/check_play_submission_doc_coverage.py`;
- `scripts/check_play_upload_readiness.py` runs the same packet sync and documentation coverage gates, so a self-consistent but stale or incomplete packet cannot pass local or strict readiness;
- `play-submission/release/artifact_manifest.json` matches the strict expected schema, current Gradle release identity, APK/AAB bytes, SHA-256 values, signing status, signing-input blocker state, Play form/policy evidence blocker state and packet state through `scripts/check_release_artifact_manifest.py`;
- `play-submission/release/artifact_manifest.json` reports whether `playUploadReady` is blocked and lists the remaining `uploadBlockers`, including missing current signing inputs or failed Play form/policy evidence;
- `play-submission/release/upload_blockers.json` expands those blockers into action/evidence records and is synchronized with `artifact_manifest.json` through `scripts/check_play_upload_blockers.py`;
- packet artifact status matches the current signing state;
- `app/build/outputs/bundle/release/app-release.aab` exists;
- signature status is understood;
- structured Play Console form answers pass `scripts/check_play_console_forms.py`, including `packageName` synchronization with Gradle `applicationId`;
- policy content risk scan passes `scripts/check_policy_content_risk.py`;
- privacy policy HTML exists;
- publishable privacy policy generation is skipped unless `PORYADOK5_SUPPORT_EMAIL` is set;
- publishable privacy policy rendering, validation and packet inclusion rules are covered by `scripts/check_privacy_policy_rendering_selftest.py`, `scripts/check_publishable_privacy_policy_cli_selftest.py` and `scripts/check_play_submission_publishable_policy_packet.py`;
- invalid optional external env values are called out as warnings instead of being described as absent;
- feature graphic candidate exists;
- manual Play Console confirmations are explicitly listed.

The strict URL, email, published policy content, Play Console form evidence, policy content risk, publishable policy rendering, artifact-manifest freshness, upload-blocker handoff, packet sync, packet documentation coverage and blocker rules are covered by `scripts/check_privacy_policy_rendering_selftest.py`, `scripts/check_publishable_privacy_policy_cli_selftest.py`, `scripts/check_play_upload_external_inputs_selftest.py`, `scripts/check_play_upload_readiness_selftest.py`, `scripts/check_release_artifact_manifest_checker_selftest.py`, `scripts/check_release_artifact_manifest_selftest.py`, `scripts/check_play_upload_blockers_selftest.py`, `scripts/check_play_submission_packet_sync_selftest.py` and `scripts/check_play_submission_doc_coverage_selftest.py`, which are also run by `scripts/verify_release_candidate.sh`. The final handoff ordering is covered by `scripts/check_play_upload_candidate_handoff_selftest.py`; the missing-signing early-fail path is covered by `scripts/check_prepare_play_upload_candidate_negative_path.py`.

## Strict Upload Gate

Run this only after release signing, public policy hosting and Play Console manual confirmations are complete:

```bash
export PORYADOK5_SUPPORT_EMAIL="support@poryadok5.app"
export PORYADOK5_FEATURE_GRAPHIC_APPROVED=yes
export PORYADOK5_DATA_SAFETY_CONFIRMED=yes
export PORYADOK5_TARGET_AUDIENCE_CONFIRMED=yes
export PORYADOK5_CONTENT_RATING_CONFIRMED=yes
export PORYADOK5_INTERNAL_TESTING_CONFIRMED=yes

scripts/build_play_submission_packet.sh
# Publish play-submission/text/privacy_policy_publishable_ru.html at your real HTTPS URL.
export PORYADOK5_PRIVACY_POLICY_URL="https://privacy.poryadok5.app/policy"
scripts/check_play_upload_readiness.py --require-upload-ready
```

Strict mode additionally requires:

- current release signing inputs pass `scripts/check_release_signing_inputs.py --require`;
- `play-submission` is synchronized with source materials through `scripts/check_play_submission_packet_sync.py`;
- release AAB verifies as signed with `jarsigner`;
- `play-submission/release/app-release.aab` is included;
- release artifact manifest matches the current Gradle release identity, build and packet state;
- `play-submission/release/artifact_manifest.json` has `playUploadReady=true` and an empty `uploadBlockers` list;
- `play-submission/release/upload_blockers.json` matches the manifest and has an empty `blockers` array;
- Play Console form answers and policy content risk checks pass against current docs and task catalog;
- `play-submission/text/privacy_policy_publishable_ru.html` exists when the source policy still has the pre-publication contact instruction;
- privacy policy URL is HTTPS and not a reserved example/local domain;
- developer support email is set and not an example-domain address;
- privacy policy URL returns HTTP 200 and contains the expected no-data-collection claims;
- HTTP error and timeout cases are reported as explicit upload blockers in strict mode;
- the published privacy policy uses a real contact line;
- feature graphic has been approved in Play Console preview;
- Data Safety, Target Audience and Content Rating are confirmed;
- internal testing track install flow has been checked from the Play-distributed build.

## One-Command Handoff

After signing, privacy hosting and Play Console confirmations are available, run:

```bash
scripts/prepare_play_upload_candidate.sh
```

This script checks release signing inputs and external upload inputs before expensive rebuild work, runs the full local RC verifier, rebuilds the signed upload bundle and packet after verifier cleanup, then runs the strict upload gate, checksum verification and final artifact existence check. The signing-missing and external-input-missing early-fail paths are covered by `scripts/check_prepare_play_upload_candidate_negative_path.py` and `scripts/check_prepare_play_upload_candidate_external_inputs_negative_path.py`. Details are in `docs/play_upload_handoff.md`.

## Current State

Current local state remains RC-ready but not upload-ready because signing inputs, public privacy URL and manual Play Console confirmations are external.
