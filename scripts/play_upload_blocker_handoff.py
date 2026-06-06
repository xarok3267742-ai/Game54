#!/usr/bin/env python3
from __future__ import annotations

from typing import Any

HANDOFF_SCHEMA_VERSION = 1
HANDOFF_GENERATED_FROM = "play-submission/release/artifact_manifest.json"
TOP_LEVEL_KEYS = {
    "schemaVersion",
    "appId",
    "versionCode",
    "versionName",
    "playUploadReady",
    "generatedFrom",
    "blockers",
}
BLOCKER_RECORD_KEYS = {
    "id",
    "status",
    "category",
    "scope",
    "requiredAction",
    "evidence",
    "verification",
}

BLOCKER_DETAILS: dict[str, dict[str, str]] = {
    "release_signing_inputs_missing": {
        "category": "signing",
        "scope": "external_secret",
        "requiredAction": (
            "Configure PORYADOK5_KEYSTORE_PATH, PORYADOK5_KEYSTORE_PASSWORD, "
            "PORYADOK5_KEY_ALIAS and PORYADOK5_KEY_PASSWORD from environment or "
            "a user Gradle properties file outside the repository."
        ),
        "evidence": "Strict release signing preflight does not pass in the current environment.",
        "verification": "scripts/check_release_signing_inputs.py --require passes.",
    },
    "signed_upload_aab_missing": {
        "category": "signing",
        "scope": "external_secret",
        "requiredAction": (
            "Run scripts/prepare_play_upload_candidate.sh after release signing inputs are available "
            "so play-submission/release/app-release.aab is included."
        ),
        "evidence": "The packet does not contain a jarsigner-verified signed upload AAB.",
        "verification": (
            "scripts/check_release_artifact_manifest.py passes with packetReleaseAab sha256 "
            "matching the current signed release AAB."
        ),
    },
    "public_privacy_policy_url_missing": {
        "category": "privacy",
        "scope": "external_hosting",
        "requiredAction": (
            "Host play-submission/text/privacy_policy_publishable_ru.html or equivalent content "
            "at a stable public HTTPS URL and export PORYADOK5_PRIVACY_POLICY_URL."
        ),
        "evidence": "No valid public privacy policy URL is configured for the current upload gate.",
        "verification": "scripts/check_play_upload_external_inputs.py reaches and validates the live URL.",
    },
    "support_email_missing": {
        "category": "privacy",
        "scope": "external_account",
        "requiredAction": (
            "Export PORYADOK5_SUPPORT_EMAIL with the developer support email used in Play Console."
        ),
        "evidence": "No valid non-reserved support email is configured for the current upload gate.",
        "verification": "scripts/check_play_upload_external_inputs.py accepts PORYADOK5_SUPPORT_EMAIL.",
    },
    "privacy_policy_contact_not_replaced": {
        "category": "privacy",
        "scope": "external_hosting",
        "requiredAction": (
            "Generate the publishable privacy policy with PORYADOK5_SUPPORT_EMAIL and publish "
            "content that does not contain the pre-publication contact instruction."
        ),
        "evidence": "The local template still contains the pre-publication contact instruction.",
        "verification": (
            "scripts/check_publishable_privacy_policy.py passes and the live policy contains "
            "the configured support email."
        ),
    },
    "feature_graphic_not_confirmed": {
        "category": "store_asset",
        "scope": "play_console_manual",
        "requiredAction": (
            "Preview the feature graphic in Play Console and export "
            "PORYADOK5_FEATURE_GRAPHIC_APPROVED=yes after approval."
        ),
        "evidence": "Feature graphic approval has not been confirmed in the current environment.",
        "verification": "scripts/check_play_upload_readiness.py --require-upload-ready reports the flag confirmed.",
    },
    "data_safety_not_confirmed": {
        "category": "play_console_form",
        "scope": "play_console_manual",
        "requiredAction": (
            "Complete the Play Console Data Safety form as no data collected/shared and export "
            "PORYADOK5_DATA_SAFETY_CONFIRMED=yes."
        ),
        "evidence": "Data Safety completion has not been confirmed in the current environment.",
        "verification": "scripts/check_play_upload_readiness.py --require-upload-ready reports the flag confirmed.",
    },
    "target_audience_not_confirmed": {
        "category": "play_console_form",
        "scope": "play_console_manual",
        "requiredAction": (
            "Complete Target Audience and Content as 13+ and not children-directed, then export "
            "PORYADOK5_TARGET_AUDIENCE_CONFIRMED=yes."
        ),
        "evidence": "Target Audience and Content completion has not been confirmed in the current environment.",
        "verification": "scripts/check_play_upload_readiness.py --require-upload-ready reports the flag confirmed.",
    },
    "content_rating_not_confirmed": {
        "category": "play_console_form",
        "scope": "play_console_manual",
        "requiredAction": (
            "Complete the Play Console Content Rating questionnaire and export "
            "PORYADOK5_CONTENT_RATING_CONFIRMED=yes."
        ),
        "evidence": "Content Rating completion has not been confirmed in the current environment.",
        "verification": "scripts/check_play_upload_readiness.py --require-upload-ready reports the flag confirmed.",
    },
    "internal_testing_not_confirmed": {
        "category": "play_console_testing",
        "scope": "play_console_manual",
        "requiredAction": (
            "Install the Play-distributed build from the internal testing track and export "
            "PORYADOK5_INTERNAL_TESTING_CONFIRMED=yes after the flow is checked."
        ),
        "evidence": "Internal testing track install verification has not been confirmed in the current environment.",
        "verification": "scripts/check_play_upload_readiness.py --require-upload-ready reports the flag confirmed.",
    },
    "play_console_forms_evidence_failed": {
        "category": "local_evidence",
        "scope": "repository",
        "requiredAction": "Fix docs/play_console_forms_answers.json or its checker evidence before upload.",
        "evidence": "scripts/check_play_console_forms.py does not pass against current repository state.",
        "verification": "scripts/check_play_console_forms.py passes.",
    },
    "policy_content_risk_evidence_failed": {
        "category": "local_evidence",
        "scope": "repository",
        "requiredAction": "Fix store listing or task catalog content that contradicts low-risk Play form answers.",
        "evidence": "scripts/check_policy_content_risk.py does not pass against current repository state.",
        "verification": "scripts/check_policy_content_risk.py passes.",
    },
}


def blocker_record(blocker_id: str) -> dict[str, str]:
    details = BLOCKER_DETAILS.get(blocker_id)
    if details is None:
        raise ValueError(f"unknown upload blocker: {blocker_id}")
    return {
        "id": blocker_id,
        "status": "open",
        **details,
    }


def payload_from_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    blockers = manifest.get("uploadBlockers")
    if not isinstance(blockers, list) or not all(isinstance(item, str) for item in blockers):
        raise ValueError("artifact manifest uploadBlockers must be a list of strings")

    return {
        "schemaVersion": HANDOFF_SCHEMA_VERSION,
        "appId": manifest.get("appId"),
        "versionCode": manifest.get("versionCode"),
        "versionName": manifest.get("versionName"),
        "playUploadReady": manifest.get("playUploadReady"),
        "generatedFrom": HANDOFF_GENERATED_FROM,
        "blockers": [blocker_record(blocker_id) for blocker_id in blockers],
    }
