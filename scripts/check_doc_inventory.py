#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC_INVENTORY_PATH = "docs/doc_inventory.md"
ALLOWED_TABLE_ONLY_FILES = {
    "scripts/check_qa_evidence.py",
}
STORY_BIBLE_SCAN_DIRS = (
    "docs",
    "scripts",
    "app/src",
    "play-submission",
)

REQUIRED_FILES: dict[str, tuple[str, ...]] = {
    "README.md": ("Порядок 5", "scripts/verify_release_candidate.sh"),
    "AGENTS.md": ("Definition of Done", "Google Play release candidate"),
    "docs/product_decision.md": ("Выбранная идея", "Порядок 5"),
    "docs/product_spec.md": ("Core Loop", "80 задач"),
    "docs/tech_stack.md": ("Application id", "Compose BOM 2026.04.01", "targetSdk: 35"),
    "docs/tech_stack_decision.md": ("Kotlin + Jetpack Compose", "Compose BOM 2026.04.01", "Android Gradle Plugin 8.9.1"),
    "docs/stack_version_audit.md": ("Stack Version Audit", "Gradle wrapper", "Compose BOM"),
    "docs/clean_build_audit.md": ("Clean Build Audit", "gradlew clean", "play-submission"),
    "docs/aab_universal_apk_audit.md": ("AAB Universal APK Audit", "bundletool build-apks", "universal.apk"),
    "docs/release_plan.md": ("RC Target", "internal testing"),
    "docs/release_report.md": ("Release Build Status", "Оставшиеся ручные действия"),
    "docs/google_play_checklist.md": ("Privacy And Data Safety", "Manual Play Console Actions"),
    "docs/android_backup_policy_audit.md": ("Android Backup Policy Audit", "allowBackup", "dataExtractionRules"),
    "docs/play_console_submission.md": ("Data Safety", "Internal Testing Track"),
    "docs/play_console_forms_answers.json": ("collectsUserData", "targetAudienceAndContent"),
    "docs/policy_content_risk_audit.md": ("Policy Content Risk Audit", "LOCAL_PROVEN_FOR_CONTENT_SCAN"),
    "docs/qa_test_plan.md": ("Manual Emulator QA", "Android 16"),
    "docs/ui_audit.md": ("UI Audit", "Tap targets"),
    "docs/performance_notes.md": ("Performance", "DataStore"),
    "docs/packaged_app_contents_audit.md": ("Packaged App Contents Audit", "LOCAL_PROVEN", "check_packaged_app_contents.py"),
    "docs/native_library_packaging_audit.md": ("Native Library Packaging Audit", "zipalign -c -P 16", "uncompressed"),
    "docs/packaged_task_catalog_audit.md": ("Packaged Task Catalog Audit", "LOCAL_PROVEN", "check_packaged_task_catalog.py"),
    "docs/task_catalog_quality_audit.md": ("Task Catalog Quality Audit", "80 task", "LOCAL_PROVEN"),
    "docs/qa_evidence_audit.md": ("QA Evidence Audit", "LOCAL_PROVEN", "check_qa_evidence.py"),
    "docs/privacy_and_permissions.md": ("Google Play Data Safety", "Runtime permissions"),
    "docs/privacy_policy_draft_ru.md": ("Политика конфиденциальности", "не собирает"),
    "docs/privacy_policy_ru.html": ("Политика конфиденциальности", "не собирает"),
    "docs/art_direction.md": ("Art Direction", "Палитра"),
    "docs/asset_prompts.md": ("Asset Prompts", "Feature Graphic Concept"),
    "docs/asset_manifest.md": ("Asset Manifest", "Play Store app icon"),
    "docs/content_audit.md": ("Content Audit", "80"),
    "docs/accessibility_notes.md": ("Accessibility", "52dp"),
    "docs/store_listing_ru.md": ("Store Listing Draft", "Short Description"),
    "docs/store_listing_audit.md": ("Store Listing Audit", "Automated Gate"),
    "docs/screenshot_plan.md": ("Screenshot", "screenshots/play-store"),
    "docs/screenshot_manifest.md": ("Screenshot Manifest", "06-settings"),
    "docs/store_asset_pixel_audit.md": ("Store Asset Pixel Audit", "LOCAL_PROVEN", "check_store_asset_pixels.py"),
    "docs/play_store_icon.md": ("Play Store Icon", "512x512"),
    "docs/feature_graphic_candidate.md": ("Feature Graphic Candidate", "CONCEPT_CANDIDATE"),
    "docs/signing_setup.md": ("Release Signing Setup", "PORYADOK5_KEYSTORE_PATH"),
    "docs/release_hygiene.md": ("Release Hygiene", "check_release_hygiene.py", "LOCAL_PROVEN"),
    "docs/play_upload_preflight.md": ("Play Upload Preflight", "Strict Upload Gate"),
    "docs/play_upload_handoff.md": ("Play Upload Handoff", "prepare_play_upload_candidate.sh", "play-submission/release/app-release.aab"),
    "docs/rc_requirement_traceability.md": ("RC Requirement Traceability", "LOCAL_PROVEN", "EXTERNAL_REQUIRED"),
    "docs/emulator_android15_compose_bom_smoke_qa.md": (
        "Android 15 Compose BOM Smoke QA",
        "PASSED_WITH_AVD_CAVEAT",
        "qa/emulator-android15-compose-bom-smoke",
    ),
    "docs/emulator_android15_timer_double_submit_qa.md": (
        "Android 15 Timer Double-Submit QA",
        "PASSED_WITH_AVD_CAVEAT",
        "qa/emulator-android15-timer-double-submit",
    ),
    "docs/emulator_android16_home_filter_disclosure_qa_2026_06_06.md": (
        "Android 16 Home Filter Disclosure QA",
        "PASSED",
        "qa/emulator-android16-home-filter-disclosure-qa-2026-06-06",
    ),
    "docs/emulator_android15_home_filter_whole_row_qa_2026_06_06.md": (
        "Android 15 Home Filter Whole-Row QA",
        "PASSED",
        "qa/emulator-android15-home-filter-whole-row-qa-2026-06-06",
    ),
    "docs/emulator_android15_home_filter_chevron_qa_2026_06_06.md": (
        "Android 15 Home Filter Chevron QA",
        "PASSED",
        "qa/emulator-android15-home-filter-chevron-qa-2026-06-06",
    ),
    "docs/emulator_android16_home_filter_unframed_summary_qa_2026_06_06.md": (
        "Android 16 Home Filter Unframed Summary QA",
        "PASSED",
        "qa/emulator-android16-home-filter-unframed-summary-qa-2026-06-06",
    ),
    "docs/emulator_android15_home_result_preview_qa_2026_06_06.md": (
        "Android 15 Home Result Preview QA",
        "PASSED",
        "qa/emulator-android15-home-result-preview-qa-2026-06-06",
    ),
    "docs/emulator_android15_home_action_icons_qa_2026_06_06.md": (
        "Android 15 Home Action Icons QA",
        "PASSED",
        "qa/emulator-android15-home-action-icons-qa-2026-06-06",
    ),
    "docs/emulator_android15_main_flow_action_icons_qa_2026_06_06.md": (
        "Android 15 Main-Flow Action Icons QA",
        "PASSED",
        "qa/emulator-android15-main-flow-action-icons-qa-2026-06-06",
    ),
    "docs/emulator_android16_task_details_briefing_qa_2026_06_06.md": (
        "Android 16 Task Details Briefing QA",
        "PASSED",
        "qa/emulator-android16-task-details-briefing-qa-2026-06-06",
    ),
    "docs/emulator_android15_task_details_unframed_qa_2026_06_06.md": (
        "Android 15 Task Details Unframed Briefing QA",
        "PASSED",
        "qa/emulator-android15-task-details-unframed-qa-2026-06-06",
    ),
    "docs/emulator_android15_timer_completion_dock_qa_2026_06_06.md": (
        "Android 15 Timer Completion Dock QA",
        "PASSED",
        "qa/emulator-android15-timer-completion-dock-qa-2026-06-06",
    ),
    "docs/emulator_android15_timer_session_goal_qa_2026_06_06.md": (
        "Android 15 Timer Session Goal QA",
        "PASSED",
        "qa/emulator-android15-timer-session-goal-qa-2026-06-06",
    ),
    "docs/emulator_android15_timer_outcome_preview_qa_2026_06_06.md": (
        "Android 15 Timer Outcome Preview QA",
        "PASSED",
        "qa/emulator-android15-timer-outcome-preview-qa-2026-06-06",
    ),
    "docs/emulator_android16_timer_control_icons_qa_2026_06_06.md": (
        "Android 16 Timer Control Icons QA",
        "PASSED",
        "qa/emulator-android16-timer-control-icons-qa-2026-06-06",
    ),
    "docs/emulator_android15_result_details_first_qa_2026_06_06.md": (
        "Android 15 Result Details-First QA",
        "PASSED",
        "qa/emulator-android15-result-details-first-qa-2026-06-06",
    ),
    "docs/emulator_android16_result_content_focus_qa_2026_06_06.md": (
        "Android 16 Result Content Focus QA",
        "PASSED",
        "qa/emulator-android16-result-content-focus-qa-2026-06-06",
    ),
    "docs/emulator_android16_result_peer_icons_qa_2026_06_06.md": (
        "Android 16 Result Peer Icons QA",
        "PASSED",
        "qa/emulator-android16-result-peer-icons-qa-2026-06-06",
    ),
    "docs/emulator_android15_settings_privacy_summary_qa_2026_06_06.md": (
        "Android 15 Settings Privacy Summary QA",
        "PASSED",
        "qa/emulator-android15-settings-privacy-summary-qa-2026-06-06",
    ),
    "docs/emulator_android15_onboarding_flow_summary_qa_2026_06_06.md": (
        "Android 15 Onboarding Flow Summary QA",
        "PASSED",
        "qa/emulator-android15-onboarding-flow-summary-qa-2026-06-06",
    ),
    "docs/emulator_android15_task_status_pill_qa_2026_06_06.md": (
        "Android 15 Task Status Pill QA",
        "PASSED",
        "qa/emulator-android15-task-status-pill-qa-2026-06-06",
    ),
    "docs/emulator_android15_progress_rhythm_summary_qa_2026_06_06.md": (
        "Android 15 Progress Rhythm Summary QA",
        "PASSED",
        "qa/emulator-android15-progress-rhythm-summary-qa-2026-06-06",
    ),
    "docs/emulator_android16_progress_rhythm_unframed_qa_2026_06_06.md": (
        "Android 16 Progress Rhythm Unframed QA",
        "PASSED",
        "qa/emulator-android16-progress-rhythm-unframed-qa-2026-06-06",
    ),
    "docs/emulator_android16_settings_privacy_unframed_qa_2026_06_06.md": (
        "Android 16 Settings Privacy Unframed QA",
        "PASSED",
        "qa/emulator-android16-settings-privacy-unframed-qa-2026-06-06",
    ),
    "docs/emulator_android16_settings_about_summary_qa_2026_06_06.md": (
        "Android 16 Settings About Summary QA",
        "PASSED",
        "qa/emulator-android16-settings-about-summary-qa-2026-06-06",
    ),
    "docs/doc_inventory.md": ("Documentation Inventory", "story_bible.md"),
}

MIN_BYTES = 120


def doc_inventory_table_paths(text: str) -> list[str]:
    paths: list[str] = []
    in_inventory_table = False

    for line in text.splitlines():
        if line.strip() == "| Requirement | File | Status |":
            in_inventory_table = True
            continue
        if not in_inventory_table:
            continue
        if not line.startswith("|"):
            break
        if re.fullmatch(r"\|\s*-+\s*\|\s*-+\s*\|\s*-+\s*\|", line.strip()):
            continue

        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 3:
            continue
        file_match = re.fullmatch(r"`([^`]+)`", cells[1])
        if file_match:
            paths.append(file_match.group(1))

    return paths


def doc_inventory_table_failures(
    root: Path,
    required_files: dict[str, tuple[str, ...]],
) -> list[str]:
    inventory_path = root / DOC_INVENTORY_PATH
    if not inventory_path.exists() or not inventory_path.is_file():
        return []

    table_paths = doc_inventory_table_paths(inventory_path.read_text(encoding="utf-8"))
    if not table_paths:
        return ["documentation inventory table is missing or has no file rows"]

    failures: list[str] = []
    seen: set[str] = set()
    duplicates: set[str] = set()
    for table_path in table_paths:
        if table_path in seen:
            duplicates.add(table_path)
        seen.add(table_path)

    for duplicate in sorted(duplicates):
        failures.append(f"documentation inventory table has duplicate file row: {duplicate}")

    required_set = set(required_files)
    missing_rows = sorted(required_set - seen)
    unexpected_rows = sorted(seen - required_set - ALLOWED_TABLE_ONLY_FILES)

    for missing in missing_rows:
        failures.append(f"documentation inventory table is missing required file row: {missing}")
    for unexpected in unexpected_rows:
        failures.append(f"documentation inventory table has unexpected file row: {unexpected}")

    return failures


def doc_inventory_failures(
    root: Path = ROOT,
    required_files: dict[str, tuple[str, ...]] | None = None,
    min_bytes: int = MIN_BYTES,
) -> list[str]:
    required = required_files or REQUIRED_FILES
    failures: list[str] = []

    for relative_path, required_snippets in required.items():
        path = root / relative_path
        if not path.exists():
            failures.append(f"missing required document: {relative_path}")
            continue
        if not path.is_file():
            failures.append(f"required document is not a file: {relative_path}")
            continue
        text = path.read_text(encoding="utf-8")
        if len(text.encode("utf-8")) < min_bytes:
            failures.append(f"document is too small to prove coverage: {relative_path}")
        for snippet in required_snippets:
            if snippet not in text:
                failures.append(f"{relative_path} is missing required marker: {snippet}")

    story_bible_matches = list(iter_story_bible_matches(root))
    if story_bible_matches:
        failures.append(
            "story bible files must be absent for this non-story product: "
            + ", ".join(str(path.relative_to(root)) for path in story_bible_matches)
        )

    failures.extend(doc_inventory_table_failures(root, required))

    return failures


def iter_story_bible_matches(root: Path):
    for path in root.iterdir():
        if path.is_file() and "story_bible" in path.name.lower():
            yield path

    for relative_dir in STORY_BIBLE_SCAN_DIRS:
        scan_root = root / relative_dir
        if not scan_root.exists():
            continue
        for path in scan_root.rglob("*"):
            if path.is_file() and "story_bible" in path.name.lower():
                yield path


def main() -> int:
    failures = doc_inventory_failures()

    if failures:
        print("Documentation inventory check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print(f"PASS: documentation inventory covers {len(REQUIRED_FILES)} required RC documents and story_bible.md is absent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
