#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "play-submission"
CHECKSUMS = PACKET / "checksums.sha256"

SOURCE_TO_PACKET: tuple[tuple[str, str], ...] = (
    ("README.md", "project/README.md"),
    ("AGENTS.md", "project/AGENTS.md"),
    ("docs/product_decision.md", "docs/product_decision.md"),
    ("docs/product_spec.md", "docs/product_spec.md"),
    ("docs/tech_stack.md", "docs/tech_stack.md"),
    ("docs/tech_stack_decision.md", "docs/tech_stack_decision.md"),
    ("docs/store_listing_ru.md", "text/store_listing_ru.md"),
    ("docs/store_listing_audit.md", "docs/store_listing_audit.md"),
    ("docs/privacy_policy_draft_ru.md", "text/privacy_policy_draft_ru.md"),
    ("docs/privacy_policy_ru.html", "text/privacy_policy_ru.html"),
    ("docs/play_console_submission.md", "docs/play_console_submission.md"),
    ("docs/play_console_forms_answers.json", "docs/play_console_forms_answers.json"),
    ("docs/policy_content_risk_audit.md", "docs/policy_content_risk_audit.md"),
    ("docs/play_upload_preflight.md", "docs/play_upload_preflight.md"),
    ("docs/play_upload_handoff.md", "docs/play_upload_handoff.md"),
    ("docs/rc_requirement_traceability.md", "docs/rc_requirement_traceability.md"),
    ("docs/doc_inventory.md", "docs/doc_inventory.md"),
    ("docs/stack_version_audit.md", "docs/stack_version_audit.md"),
    ("docs/clean_build_audit.md", "docs/clean_build_audit.md"),
    ("docs/release_plan.md", "docs/release_plan.md"),
    ("docs/release_report.md", "docs/release_report.md"),
    ("docs/google_play_checklist.md", "docs/google_play_checklist.md"),
    ("docs/ui_audit.md", "docs/ui_audit.md"),
    ("docs/performance_notes.md", "docs/performance_notes.md"),
    ("docs/privacy_and_permissions.md", "docs/privacy_and_permissions.md"),
    ("docs/android_backup_policy_audit.md", "docs/android_backup_policy_audit.md"),
    ("docs/aab_metadata_audit.md", "docs/aab_metadata_audit.md"),
    ("docs/aab_universal_apk_audit.md", "docs/aab_universal_apk_audit.md"),
    ("docs/apk_metadata_audit.md", "docs/apk_metadata_audit.md"),
    ("docs/dependency_privacy_audit.md", "docs/dependency_privacy_audit.md"),
    ("docs/packaged_app_contents_audit.md", "docs/packaged_app_contents_audit.md"),
    ("docs/native_library_packaging_audit.md", "docs/native_library_packaging_audit.md"),
    ("docs/packaged_task_catalog_audit.md", "docs/packaged_task_catalog_audit.md"),
    ("docs/task_catalog_quality_audit.md", "docs/task_catalog_quality_audit.md"),
    ("docs/qa_evidence_audit.md", "docs/qa_evidence_audit.md"),
    ("docs/qa_test_plan.md", "docs/qa_test_plan.md"),
    ("docs/emulator_timer_background_qa.md", "docs/emulator_timer_background_qa.md"),
    (
        "docs/emulator_android15_timer_double_submit_qa.md",
        "docs/emulator_android15_timer_double_submit_qa.md",
    ),
    ("docs/emulator_no_internet_qa.md", "docs/emulator_no_internet_qa.md"),
    (
        "docs/emulator_android15_compose_bom_smoke_qa.md",
        "docs/emulator_android15_compose_bom_smoke_qa.md",
    ),
    ("docs/emulator_android16_smoke_qa.md", "docs/emulator_android16_smoke_qa.md"),
    ("docs/emulator_android16_compact_screen_qa.md", "docs/emulator_android16_compact_screen_qa.md"),
    ("docs/emulator_android16_large_screen_qa.md", "docs/emulator_android16_large_screen_qa.md"),
    ("docs/emulator_android16_large_font_qa.md", "docs/emulator_android16_large_font_qa.md"),
    (
        "docs/emulator_android16_home_filter_disclosure_qa_2026_06_06.md",
        "docs/emulator_android16_home_filter_disclosure_qa_2026_06_06.md",
    ),
    (
        "docs/emulator_android15_home_filter_whole_row_qa_2026_06_06.md",
        "docs/emulator_android15_home_filter_whole_row_qa_2026_06_06.md",
    ),
    (
        "docs/emulator_android15_home_filter_chevron_qa_2026_06_06.md",
        "docs/emulator_android15_home_filter_chevron_qa_2026_06_06.md",
    ),
    (
        "docs/emulator_android16_home_filter_unframed_summary_qa_2026_06_06.md",
        "docs/emulator_android16_home_filter_unframed_summary_qa_2026_06_06.md",
    ),
    (
        "docs/emulator_android15_home_result_preview_qa_2026_06_06.md",
        "docs/emulator_android15_home_result_preview_qa_2026_06_06.md",
    ),
    (
        "docs/emulator_android15_home_action_icons_qa_2026_06_06.md",
        "docs/emulator_android15_home_action_icons_qa_2026_06_06.md",
    ),
    (
        "docs/emulator_android15_main_flow_action_icons_qa_2026_06_06.md",
        "docs/emulator_android15_main_flow_action_icons_qa_2026_06_06.md",
    ),
    (
        "docs/emulator_android15_home_stats_icon_qa_2026_06_06.md",
        "docs/emulator_android15_home_stats_icon_qa_2026_06_06.md",
    ),
    (
        "docs/emulator_android16_task_details_briefing_qa_2026_06_06.md",
        "docs/emulator_android16_task_details_briefing_qa_2026_06_06.md",
    ),
    (
        "docs/emulator_android15_task_details_unframed_qa_2026_06_06.md",
        "docs/emulator_android15_task_details_unframed_qa_2026_06_06.md",
    ),
    (
        "docs/emulator_android15_timer_completion_dock_qa_2026_06_06.md",
        "docs/emulator_android15_timer_completion_dock_qa_2026_06_06.md",
    ),
    (
        "docs/emulator_android15_timer_session_goal_qa_2026_06_06.md",
        "docs/emulator_android15_timer_session_goal_qa_2026_06_06.md",
    ),
    (
        "docs/emulator_android15_timer_outcome_preview_qa_2026_06_06.md",
        "docs/emulator_android15_timer_outcome_preview_qa_2026_06_06.md",
    ),
    (
        "docs/emulator_android16_timer_control_icons_qa_2026_06_06.md",
        "docs/emulator_android16_timer_control_icons_qa_2026_06_06.md",
    ),
    (
        "docs/emulator_android15_result_details_first_qa_2026_06_06.md",
        "docs/emulator_android15_result_details_first_qa_2026_06_06.md",
    ),
    (
        "docs/emulator_android16_result_content_focus_qa_2026_06_06.md",
        "docs/emulator_android16_result_content_focus_qa_2026_06_06.md",
    ),
    (
        "docs/emulator_android16_result_peer_icons_qa_2026_06_06.md",
        "docs/emulator_android16_result_peer_icons_qa_2026_06_06.md",
    ),
    (
        "docs/emulator_android15_settings_privacy_summary_qa_2026_06_06.md",
        "docs/emulator_android15_settings_privacy_summary_qa_2026_06_06.md",
    ),
    (
        "docs/emulator_android15_onboarding_flow_summary_qa_2026_06_06.md",
        "docs/emulator_android15_onboarding_flow_summary_qa_2026_06_06.md",
    ),
    (
        "docs/emulator_android15_task_status_pill_qa_2026_06_06.md",
        "docs/emulator_android15_task_status_pill_qa_2026_06_06.md",
    ),
    (
        "docs/emulator_android15_progress_rhythm_summary_qa_2026_06_06.md",
        "docs/emulator_android15_progress_rhythm_summary_qa_2026_06_06.md",
    ),
    (
        "docs/emulator_android16_progress_rhythm_unframed_qa_2026_06_06.md",
        "docs/emulator_android16_progress_rhythm_unframed_qa_2026_06_06.md",
    ),
    (
        "docs/emulator_android16_settings_privacy_unframed_qa_2026_06_06.md",
        "docs/emulator_android16_settings_privacy_unframed_qa_2026_06_06.md",
    ),
    (
        "docs/emulator_android16_settings_about_summary_qa_2026_06_06.md",
        "docs/emulator_android16_settings_about_summary_qa_2026_06_06.md",
    ),
    ("docs/screenshot_manifest.md", "docs/screenshot_manifest.md"),
    ("docs/store_asset_pixel_audit.md", "docs/store_asset_pixel_audit.md"),
    ("docs/play_store_icon.md", "docs/play_store_icon.md"),
    ("docs/feature_graphic_candidate.md", "docs/feature_graphic_candidate.md"),
    ("docs/art_direction.md", "docs/art_direction.md"),
    ("docs/asset_prompts.md", "docs/asset_prompts.md"),
    ("docs/asset_manifest.md", "docs/asset_manifest.md"),
    ("docs/content_audit.md", "docs/content_audit.md"),
    ("docs/accessibility_notes.md", "docs/accessibility_notes.md"),
    ("docs/screenshot_plan.md", "docs/screenshot_plan.md"),
    ("docs/signing_setup.md", "docs/signing_setup.md"),
    ("docs/release_hygiene.md", "docs/release_hygiene.md"),
    ("store-assets/app-icon/play-store-icon-512.png", "assets/app-icon/play-store-icon-512.png"),
    ("screenshots/play-store/01-onboarding.png", "assets/screenshots/01-onboarding.png"),
    ("screenshots/play-store/02-home.png", "assets/screenshots/02-home.png"),
    ("screenshots/play-store/03-timer.png", "assets/screenshots/03-timer.png"),
    ("screenshots/play-store/04-result.png", "assets/screenshots/04-result.png"),
    ("screenshots/play-store/05-progress.png", "assets/screenshots/05-progress.png"),
    ("screenshots/play-store/06-settings.png", "assets/screenshots/06-settings.png"),
    (
        "store-assets/feature-graphic/feature-graphic-candidate-03.png",
        "assets/feature-graphic/feature-graphic-candidate-03.png",
    ),
)


def display_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def normalize_checksum_path(raw_path: str) -> str:
    relative = raw_path.strip()
    if relative.startswith("*"):
        relative = relative[1:]
    if relative.startswith("./"):
        relative = relative[2:]
    return relative


def read_checksum_entries(checksum_file: Path) -> tuple[dict[str, str], list[str]]:
    failures: list[str] = []
    entries: dict[str, str] = {}

    if not checksum_file.exists():
        return entries, [f"missing packet checksum file: {display_path(checksum_file, ROOT)}"]

    for line_number, line in enumerate(checksum_file.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        if len(line) < 67:
            failures.append(f"malformed checksum line {line_number}: too short")
            continue

        digest = line[:64]
        raw_path = line[64:].strip()
        if not re.fullmatch(r"[0-9a-fA-F]{64}", digest) or not raw_path:
            failures.append(f"malformed checksum line {line_number}")
            continue

        relative_path = normalize_checksum_path(raw_path)
        if relative_path in entries:
            failures.append(f"duplicate checksum entry: {relative_path}")
            continue
        entries[relative_path] = digest.lower()

    return entries, failures


def checksum_failures(packet: Path = PACKET) -> list[str]:
    checksum_file = packet / "checksums.sha256"
    entries, failures = read_checksum_entries(checksum_file)
    if failures and not entries:
        return failures

    actual_files = {
        str(path.relative_to(packet))
        for path in packet.rglob("*")
        if path.is_file() and path.name != "checksums.sha256"
    }

    missing_entries = sorted(actual_files - set(entries))
    stale_entries = sorted(set(entries) - actual_files)

    for relative_path in missing_entries:
        failures.append(f"packet file missing checksum entry: {relative_path}")
    for relative_path in stale_entries:
        failures.append(f"checksum entry points to missing packet file: {relative_path}")

    for relative_path in sorted(actual_files & set(entries)):
        actual_digest = hashlib.sha256((packet / relative_path).read_bytes()).hexdigest()
        if actual_digest != entries[relative_path]:
            failures.append(f"checksum mismatch for packet file: {relative_path}")

    return failures


def packet_sync_failures(
    root: Path = ROOT,
    packet: Path = PACKET,
    mappings: tuple[tuple[str, str], ...] = SOURCE_TO_PACKET,
) -> list[str]:
    failures: list[str] = []

    if not packet.exists():
        return [f"missing Play submission packet: {display_path(packet, root)}"]

    for source_relative, packet_relative in mappings:
        source_path = root / source_relative
        packet_path = packet / packet_relative

        if not source_path.exists():
            failures.append(f"missing source file: {source_relative}")
            continue
        if not packet_path.exists():
            failures.append(f"missing packet file: {packet_relative}")
            continue
        if source_path.read_bytes() != packet_path.read_bytes():
            failures.append(f"packet file is stale: {packet_relative} differs from {source_relative}")

    failures.extend(checksum_failures(packet))
    return failures


def main() -> int:
    failures = packet_sync_failures()
    if failures:
        print("Play submission packet sync check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print(
        "PASS: Play submission packet files match source materials and checksums cover current packet files"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
