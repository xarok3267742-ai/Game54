#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "play-submission"
ARTIFACT_STATUS = PACKET / "release" / "artifact_status.properties"

BASE_ALLOWED_FILES = {
    "README.md",
    "checksums.sha256",
    "assets/app-icon/play-store-icon-512.png",
    "assets/feature-graphic/feature-graphic-candidate-03.png",
    "assets/screenshots/01-onboarding.png",
    "assets/screenshots/02-home.png",
    "assets/screenshots/03-timer.png",
    "assets/screenshots/04-result.png",
    "assets/screenshots/05-progress.png",
    "assets/screenshots/06-settings.png",
    "docs/aab_metadata_audit.md",
    "docs/aab_universal_apk_audit.md",
    "docs/accessibility_notes.md",
    "docs/android_backup_policy_audit.md",
    "docs/apk_metadata_audit.md",
    "docs/art_direction.md",
    "docs/asset_manifest.md",
    "docs/asset_prompts.md",
    "docs/clean_build_audit.md",
    "docs/content_audit.md",
    "docs/dependency_privacy_audit.md",
    "docs/native_library_packaging_audit.md",
    "docs/packaged_app_contents_audit.md",
    "docs/packaged_task_catalog_audit.md",
    "docs/task_catalog_quality_audit.md",
    "docs/doc_inventory.md",
    "docs/emulator_android15_compose_bom_smoke_qa.md",
    "docs/emulator_android15_timer_completion_dock_qa_2026_06_06.md",
    "docs/emulator_android15_timer_double_submit_qa.md",
    "docs/emulator_android16_compact_screen_qa.md",
    "docs/emulator_android16_home_filter_disclosure_qa_2026_06_06.md",
    "docs/emulator_android15_home_filter_whole_row_qa_2026_06_06.md",
    "docs/emulator_android15_home_filter_chevron_qa_2026_06_06.md",
    "docs/emulator_android16_home_filter_unframed_summary_qa_2026_06_06.md",
    "docs/emulator_android15_home_result_preview_qa_2026_06_06.md",
    "docs/emulator_android15_home_action_icons_qa_2026_06_06.md",
    "docs/emulator_android15_main_flow_action_icons_qa_2026_06_06.md",
    "docs/emulator_android15_home_stats_icon_qa_2026_06_06.md",
    "docs/emulator_android16_task_details_briefing_qa_2026_06_06.md",
    "docs/emulator_android15_task_details_unframed_qa_2026_06_06.md",
    "docs/emulator_android15_result_details_first_qa_2026_06_06.md",
    "docs/emulator_android16_result_content_focus_qa_2026_06_06.md",
    "docs/emulator_android16_result_peer_icons_qa_2026_06_06.md",
    "docs/emulator_android15_timer_session_goal_qa_2026_06_06.md",
    "docs/emulator_android15_timer_outcome_preview_qa_2026_06_06.md",
    "docs/emulator_android16_timer_control_icons_qa_2026_06_06.md",
    "docs/emulator_android15_settings_privacy_summary_qa_2026_06_06.md",
    "docs/emulator_android15_onboarding_flow_summary_qa_2026_06_06.md",
    "docs/emulator_android15_task_status_pill_qa_2026_06_06.md",
    "docs/emulator_android15_progress_rhythm_summary_qa_2026_06_06.md",
    "docs/emulator_android16_progress_rhythm_unframed_qa_2026_06_06.md",
    "docs/emulator_android16_settings_privacy_unframed_qa_2026_06_06.md",
    "docs/emulator_android16_settings_about_summary_qa_2026_06_06.md",
    "docs/emulator_android16_large_font_qa.md",
    "docs/emulator_android16_large_screen_qa.md",
    "docs/emulator_android16_smoke_qa.md",
    "docs/emulator_no_internet_qa.md",
    "docs/emulator_timer_background_qa.md",
    "docs/feature_graphic_candidate.md",
    "docs/google_play_checklist.md",
    "docs/play_console_forms_answers.json",
    "docs/play_console_submission.md",
    "docs/policy_content_risk_audit.md",
    "docs/play_store_icon.md",
    "docs/play_upload_handoff.md",
    "docs/play_upload_preflight.md",
    "docs/qa_evidence_audit.md",
    "docs/qa_test_plan.md",
    "docs/rc_requirement_traceability.md",
    "docs/release_hygiene.md",
    "docs/release_plan.md",
    "docs/release_report.md",
    "docs/screenshot_manifest.md",
    "docs/screenshot_plan.md",
    "docs/signing_setup.md",
    "docs/stack_version_audit.md",
    "docs/store_asset_pixel_audit.md",
    "docs/store_listing_audit.md",
    "docs/performance_notes.md",
    "docs/privacy_and_permissions.md",
    "docs/product_decision.md",
    "docs/product_spec.md",
    "docs/tech_stack.md",
    "docs/tech_stack_decision.md",
    "docs/ui_audit.md",
    "project/AGENTS.md",
    "project/README.md",
    "release/artifact_manifest.json",
    "release/artifact_status.properties",
    "release/upload_blockers.json",
    "text/privacy_policy_draft_ru.md",
    "text/privacy_policy_ru.html",
    "text/store_listing_ru.md",
}

OPTIONAL_ALLOWED_FILES = {
    "text/privacy_policy_publishable_ru.html",
}

FORBIDDEN_SUFFIXES = {
    ".jks",
    ".keystore",
    ".p12",
    ".pfx",
    ".pem",
    ".key",
}

FORBIDDEN_NAMES = {
    ".env",
    "keystore.properties",
    "signing.properties",
}


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


def expected_files() -> set[str]:
    expected = set(BASE_ALLOWED_FILES)
    status = read_properties(ARTIFACT_STATUS)
    if status.get("signed_or_configured") == "true" and status.get("artifact") == "release/app-release.aab":
        expected.add("release/app-release.aab")
    for optional_file in OPTIONAL_ALLOWED_FILES:
        if (PACKET / optional_file).exists():
            expected.add(optional_file)
    return expected


def main() -> int:
    failures: list[str] = []

    if not PACKET.exists():
        print("FAIL: play-submission directory is missing", file=sys.stderr)
        return 1

    expected = expected_files()
    actual = {
        str(path.relative_to(PACKET))
        for path in PACKET.rglob("*")
        if path.is_file()
    }

    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing:
        failures.append("missing packet files: " + ", ".join(missing))
    if extra:
        failures.append("unexpected packet files: " + ", ".join(extra))

    for relative_path in sorted(actual):
        path = PACKET / relative_path
        if path.name in FORBIDDEN_NAMES or path.name.startswith(".env."):
            failures.append(f"forbidden local config file in packet: {relative_path}")
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            failures.append(f"forbidden key/keystore-like file in packet: {relative_path}")
        if relative_path.startswith(("app/build/", ".gradle/", "build/", "qa/")):
            failures.append(f"build or QA workspace output must not be copied into packet: {relative_path}")

    if "release/app-release.aab" in actual and "release/app-release.aab" not in expected:
        failures.append("release/app-release.aab is present even though artifact status is not signed/configured")

    if failures:
        print("Play submission packet contents check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print(f"PASS: play-submission contains exactly {len(expected)} allowed files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
