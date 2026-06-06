#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "rc_requirement_traceability.md"

LOCAL_PROVEN = "LOCAL_PROVEN"
EXTERNAL_REQUIRED = "EXTERNAL_REQUIRED"

REQUIREMENTS: dict[str, dict[str, object]] = {
    "R01_PRODUCT_CHOICE": {
        "status": LOCAL_PROVEN,
        "evidence": {
            "docs/product_decision.md": ("Выбранная идея", "Порядок 5"),
            "docs/product_spec.md": ("Приложение, productivity/lifestyle", "Core Loop"),
        },
    },
    "R02_ANDROID_STACK": {
        "status": LOCAL_PROVEN,
        "evidence": {
            "app/build.gradle.kts": ("ru.poryadok5.app", "targetSdk = 35", "versionName = \"1.0.0-rc1\""),
            "docs/stack_version_audit.md": ("Compose BOM", "Kotlin", "Android Gradle Plugin"),
            "scripts/check_stack_versions.py": ("compose_bom", "target_sdk"),
            "scripts/check_stack_versions_selftest.py": ("test_wrong_gradle_wrapper_fails", "test_missing_target_sdk_fails_when_compile_sdk_35"),
            "scripts/check_aab_metadata_selftest.py": ("test_wrong_target_sdk_fails", "test_metadata_uses_gradle_release_identity"),
            "scripts/check_apk_metadata_selftest.py": ("test_wrong_target_sdk_fails", "test_metadata_uses_gradle_release_identity"),
        },
    },
    "R03_OFFLINE_PRIVACY_MODEL": {
        "status": LOCAL_PROVEN,
        "evidence": {
            "app/src/main/AndroidManifest.xml": ("android.intent.action.MAIN",),
            "docs/privacy_and_permissions.md": ("app does not collect or share user data", "allowBackup"),
            "scripts/check_dependency_privacy.py": ("analytics", "tracking"),
            "scripts/check_dependency_privacy_selftest.py": ("test_ads_marker_fails", "test_tracking_marker_fails_case_insensitive"),
            "scripts/check_privacy_policy_html_selftest.py": ("test_external_script_fails", "test_tracking_marker_fails"),
            "scripts/check_apk_permissions.py": ("read_gradle_release_identity", "DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION"),
            "scripts/check_apk_permissions_selftest.py": (
                "test_allowed_permission_uses_gradle_release_identity",
                "test_platform_internet_permission_fails",
            ),
            "scripts/check_android_backup_policy.py": ("allowBackup", "dataExtractionRules"),
            "scripts/check_android_backup_policy_selftest.py": ("test_manifest_data_extraction_rules_fails",),
            "scripts/check_manifest_component_exposure.py": ("read_gradle_release_identity", "usesCleartextTraffic"),
            "scripts/check_manifest_component_exposure_selftest.py": (
                "test_main_activity_uses_gradle_release_identity",
                "test_release_unexpected_activity_fails",
            ),
            "scripts/check_packaged_app_contents.py": ("workspace-only", "tasks_ru.json"),
            "scripts/check_packaged_app_contents_selftest.py": ("test_workspace_only_path_fragment_fails", "test_forbidden_basename_fails"),
            "docs/packaged_app_contents_audit.md": ("Packaged App Contents Audit", "LOCAL_PROVEN"),
        },
    },
    "R04_ARCHITECTURE_AND_PERSISTENCE": {
        "status": LOCAL_PROVEN,
        "evidence": {
            "app/src/main/java/ru/poryadok5/app/MainActivity.kt": (
                "collectAsStateWithLifecycle",
                "preferencesRepository.preferences",
            ),
            "app/src/main/java/ru/poryadok5/app/data/UserPreferencesRepository.kt": ("DataStore", "recordCompletion", "coerceAtLeast(0)"),
            "app/src/test/java/ru/poryadok5/app/UserPreferencesRepositoryTest.kt": (
                "writeProgressStoresProgressFields",
                "corruptedStoredProgressIsNormalizedForUi",
                "writeProgressNormalizesInvalidProgressBeforeStorage",
            ),
            "scripts/check_lifecycle_state_collection.py": ("collectAsStateWithLifecycle", "lifecycle-runtime-compose"),
            "scripts/check_lifecycle_state_collection_selftest.py": (
                "test_plain_collect_as_state_call_fails",
                "test_missing_lifecycle_dependency_fails",
            ),
            "scripts/check_progress_persistence_normalization.py": (
                "normalizedCompletedTaskIds",
                "normalizedLastDoneDate",
                "completed-task ids and last-done dates",
            ),
            "scripts/check_progress_persistence_normalization_selftest.py": (
                "test_preference_read_raw_blank_filter_fails",
                "test_preference_read_raw_last_done_date_fails",
                "test_missing_progress_whitespace_test_fails",
            ),
            "scripts/check_settings_enum_normalization.py": (
                "settings enum raw values",
                "value.trim()",
            ),
            "scripts/check_settings_enum_normalization_selftest.py": (
                "test_missing_trim_fails",
                "test_raw_value_matching_fails",
            ),
            "app/src/main/java/ru/poryadok5/app/domain/Models.kt": (
                "MicroTask",
                "UserProgress",
                "AppSettings",
                "isRouteSafeTaskId",
            ),
            "app/src/test/java/ru/poryadok5/app/ModelsTest.kt": ("taskIdsValidateRouteSafeCatalogShape",),
            "docs/product_spec.md": ("Progress", "Settings", "lifecycle-aware"),
        },
    },
    "R05_TASK_CATALOG": {
        "status": LOCAL_PROVEN,
        "evidence": {
            "app/src/main/res/raw/tasks_ru.json": ("resultText", "steps"),
            "app/src/test/java/ru/poryadok5/app/TaskCatalogTest.kt": (
                "80",
                "Duplicate task id",
                "taskParserRejectsBlankId",
                "taskParserRejectsRouteUnsafeId",
                "taskParserRejectsIdAreaMismatch",
                "taskParserRejectsDuplicateIds",
                "taskParserRejectsUnsupportedMinutes",
                "taskParserRejectsWrongStepCountBeforeUiCanReadFirstStep",
                "taskParserRejectsBlankResultText",
            ),
            "scripts/check_task_catalog_quality.py": ("EXPECTED_TOTAL_TASKS", "Cyrillic"),
            "scripts/check_task_catalog_quality_selftest.py": ("test_latin_text_fails", "test_sequential_id_gap_fails"),
            "scripts/check_task_repository_parser.py": (
                "parseTaskCatalog",
                "parseTaskId",
                "parseTaskMinutes",
                "parseTaskSteps",
                "parseRequiredText",
                "SupportedTaskMinutes",
                "isRouteSafeTaskId",
                "validateTaskIdArea",
            ),
            "scripts/check_task_repository_parser_selftest.py": (
                "test_area_fallback_fails",
                "test_technical_error_leak_fails",
                "test_missing_duration_validation_fails",
                "test_hardcoded_duration_set_fails",
                "test_missing_task_id_validator_fails",
                "test_local_task_id_pattern_fails",
                "test_missing_task_id_area_validation_fails",
                "test_missing_duplicate_id_parser_test_fails",
                "test_missing_step_count_validation_fails",
            ),
            "scripts/check_packaged_task_catalog.py": ("debug APK", "release AAB"),
            "scripts/check_packaged_task_catalog_selftest.py": ("test_unexpected_task_like_json_fails", "test_packaged_bytes_and_json_mismatch_are_detectable"),
            "docs/content_audit.md": ("80", "Content Audit"),
            "docs/packaged_task_catalog_audit.md": ("Packaged Task Catalog Audit", "LOCAL_PROVEN"),
            "docs/task_catalog_quality_audit.md": ("Task Catalog Quality Audit", "LOCAL_PROVEN"),
        },
    },
    "R06_CORE_SCREENS_AND_FLOW": {
        "status": LOCAL_PROVEN,
        "evidence": {
            "app/src/main/java/ru/poryadok5/app/ui/PoryadokApp.kt": (
                "OnboardingScreen",
                "HomeScreen",
                "TimerScreen",
                "ResultScreen",
                "SettingsScreen",
                "AppScreenSaver",
            ),
            "scripts/check_runtime_catalog_count.py": ("PoryadokEngine", "hardcoded UI text"),
            "scripts/check_runtime_catalog_count_selftest.py": (
                "test_hardcoded_progress_denominator_fails",
                "test_missing_runtime_ui_usage_fails",
            ),
            "scripts/check_engine_completed_id_normalization.py": (
                "engine normalizes completed ids",
                "progress counts",
                "completedCountByArea",
            ),
            "scripts/check_engine_completed_id_normalization_selftest.py": (
                "test_raw_suggestion_completed_ids_fail",
                "test_raw_progress_count_fails",
                "test_raw_area_progress_count_fails",
            ),
            "scripts/check_task_filter_minutes_normalization.py": (
                "task filter minutes are normalized",
                "normalizedTaskMinutes",
            ),
            "scripts/check_task_filter_minutes_normalization_selftest.py": (
                "test_raw_engine_filter_minutes_fail",
                "test_raw_app_filter_minutes_fail",
            ),
            "scripts/check_screen_state_saveability.py": ("rememberSaveable(stateSaver = AppScreenSaver)", "AppScreen.Timer"),
            "scripts/check_screen_state_saveability_selftest.py": (
                "test_plain_remember_screen_state_fails",
                "test_missing_result_restore_fails",
                "test_missing_route_task_id_validation_fails",
                "test_raw_nonblank_restore_fails",
            ),
            "app/src/test/java/ru/poryadok5/app/PoryadokEngineTest.kt": (
                "suggestTaskPrefersExactFilterMatch",
                "progressCountsOnlyKnownCatalogTaskIds",
                "suggestTaskNormalizesUnsupportedFilterMinutes",
                "completedCountByAreaUsesKnownTrimmedCatalogIds",
            ),
            "docs/product_spec.md": ("Onboarding", "Home", "Timer", "Result", "Settings"),
            "docs/emulator_android15_compose_bom_smoke_qa.md": ("Flow Evidence", "Completion/result"),
        },
    },
    "R07_TIMER_AND_PROGRESS_RULES": {
        "status": LOCAL_PROVEN,
        "evidence": {
            "app/src/main/java/ru/poryadok5/app/domain/CountdownTimerRules.kt": ("remainingSeconds", "nowMillis"),
            "app/src/test/java/ru/poryadok5/app/CountdownTimerRulesTest.kt": ("remainingSecondsCatchesUpAfterLongBackgroundGap", "RoundsUp"),
            "app/src/test/java/ru/poryadok5/app/ProgressRulesTest.kt": (
                "streak",
                "corruptedNegativeCountersAreNormalizedOnCompletion",
                "blankCompletionDoesNotIncrementProgress",
                "completionTaskIdIsTrimmedBeforeStorage",
                "existingCompletedTaskIdsAreTrimmedOnCompletion",
            ),
            "docs/emulator_timer_background_qa.md": ("background/resume", "Pause"),
            "docs/emulator_android15_timer_double_submit_qa.md": ("Double-Submit", "1 из 80"),
            "scripts/check_timer_session_goal.py": ("Timer session goal", "Цель: 5 мин"),
            "scripts/check_timer_session_goal_selftest.py": ("test_goal_after_progress_fails",),
            "scripts/check_timer_outcome_preview.py": ("Timer outcome preview", "После"),
            "scripts/check_timer_outcome_preview_selftest.py": ("test_preview_before_steps_fails",),
            "docs/emulator_android15_timer_session_goal_qa_2026_06_06.md": ("Timer Session Goal", "Цель: 5 мин"),
            "docs/emulator_android15_timer_outcome_preview_qa_2026_06_06.md": (
                "Timer Outcome Preview",
                "После",
            ),
            "docs/emulator_android16_timer_control_icons_qa_2026_06_06.md": (
                "Timer Control Icons",
                "Пауза",
                "Продолжить",
            ),
        },
    },
    "R08_RUSSIAN_UI_AND_ACCESSIBILITY": {
        "status": LOCAL_PROVEN,
        "evidence": {
            "scripts/check_visible_text_ru.py": ("visible app text", "Russian"),
            "scripts/check_visible_text_ru_selftest.py": (
                "test_single_line_latin_visible_text_fails",
                "test_model_label_latin_text_fails",
            ),
            "scripts/check_accessibility_targets.py": ("48dp", "HeaderAction", "contentDescription"),
            "scripts/check_accessibility_targets_selftest.py": ("test_header_action_without_minimum_target_fails",),
            "docs/accessibility_notes.md": ("Accessibility", "48dp"),
            "docs/ui_audit.md": ("Tap targets", "48dp"),
            "docs/emulator_android16_large_font_qa.md": ("font_scale=1.3", "Primary actions"),
        },
    },
    "R09_STORE_ASSETS": {
        "status": LOCAL_PROVEN,
        "evidence": {
            "screenshots/play-store/01-onboarding.png": (),
            "screenshots/play-store/06-settings.png": (),
            "screenshots/play-store": (),
            "store-assets/app-icon/play-store-icon-512.png": (),
            "store-assets/feature-graphic/feature-graphic-candidate-03.png": (),
            "docs/screenshot_manifest.md": ("06-settings", "1080x2400"),
            "scripts/check_play_store_icon_selftest.py": ("test_wrong_dimensions_fail", "test_rgb_png_fails"),
            "scripts/check_store_asset_pixels.py": ("EXPECTED_SCREENSHOTS", "average_hash"),
            "scripts/check_store_asset_pixels_selftest.py": ("test_rgba_png_with_transparency_fails", "test_wrong_dimensions_fail"),
            "docs/store_asset_pixel_audit.md": ("Store Asset Pixel Audit", "LOCAL_PROVEN"),
            "docs/feature_graphic_candidate.md": ("CONCEPT_CANDIDATE", "1024x500"),
        },
    },
        "R10_GOOGLE_PLAY_PACKET": {
            "status": LOCAL_PROVEN,
            "evidence": {
            "scripts/build_play_submission_packet.sh": ("play-submission", "checksums.sha256"),
            "scripts/check_play_submission_publishable_policy_packet.py": (
                "privacy_policy_publishable_ru.html",
                "checksums.sha256",
            ),
            "scripts/check_play_submission_publishable_policy_packet_selftest.py": (
                "test_missing_publishable_policy_fails",
                "test_missing_checksum_entry_fails",
            ),
            "scripts/check_store_listing_selftest.py": ("test_valid_listing_passes", "test_forbidden_promotional_claim_fails"),
            "scripts/check_play_submission_packet_contents.py": ("BASE_ALLOWED_FILES", "release/app-release.aab"),
            "scripts/check_play_submission_packet_sync.py": ("SOURCE_TO_PACKET", "checksum_failures"),
            "scripts/check_play_submission_doc_coverage.py": ("REQUIRED_FILES", "SPECIAL_PACKET_DESTINATIONS"),
            "scripts/check_play_submission_doc_coverage_selftest.py": (
                "test_missing_sync_mapping_fails",
                "test_stale_packet_copy_fails",
            ),
            "scripts/generate_play_upload_blockers.py": ("payload_from_manifest", "upload_blockers.json"),
            "scripts/check_play_upload_blockers.py": ("upload_blocker_handoff_failures", "BLOCKER_RECORD_KEYS"),
            "scripts/check_play_upload_blockers_selftest.py": (
                "test_generated_handoff_passes_checker",
                "test_record_content_drift_fails",
            ),
            "play-submission/project/README.md": ("Порядок 5", "scripts/verify_release_candidate.sh"),
            "play-submission/project/AGENTS.md": ("Definition of Done", "Google Play release candidate"),
            "play-submission/docs/product_spec.md": ("Core Loop", "80 задач"),
            "play-submission/docs/tech_stack.md": ("Application id", "targetSdk: 35"),
            "play-submission/docs/asset_manifest.md": ("Asset Manifest", "Submission packet"),
            "play-submission/docs/accessibility_notes.md": ("Accessibility", "48dp"),
            "scripts/check_play_submission_packet_sync_selftest.py": (
                "test_stale_packet_file_fails_even_when_checksums_match_packet",
                "test_stale_checksum_entry_fails",
            ),
            "play-submission/README.md": ("Play Submission Packet", "External Steps Still Required"),
            "play-submission/checksums.sha256": ("store_listing_ru.md", "privacy_policy_ru.html"),
            "play-submission/release/upload_blockers.json": ("release_signing_inputs_missing", "requiredAction"),
            "docs/play_console_submission.md": ("Data Safety", "Internal Testing Track"),
        },
    },
    "R11_AUTOMATED_RC_GATE": {
        "status": LOCAL_PROVEN,
        "evidence": {
            "scripts/verify_release_candidate.sh": ("gradlew clean", "bundleRelease", "check_policy_content_risk.py"),
            "docs/clean_build_audit.md": ("Clean Build Audit", "play-submission"),
            "docs/aab_universal_apk_audit.md": ("bundletool build-apks", "universal.apk"),
            "scripts/check_aab_universal_apk_selftest.py": (
                "test_missing_universal_apk_fails",
                "test_wrong_target_sdk_fails",
                "test_metadata_uses_gradle_release_identity",
            ),
            "docs/packaged_app_contents_audit.md": ("workspace-only", "runtime artifacts"),
            "scripts/check_packaged_app_contents_selftest.py": ("test_missing_required_entry_fails", "test_bad_zip_fails_without_root_relative_path"),
            "docs/native_library_packaging_audit.md": ("zipalign -c -P 16", "uncompressed"),
            "scripts/check_native_library_packaging_selftest.py": ("test_compressed_native_library_fails", "test_zipalign_success_requires_status_and_message"),
            "scripts/check_dependency_privacy_selftest.py": ("test_firebase_analytics_marker_fails", "test_crash_reporting_marker_fails"),
            "scripts/check_lifecycle_state_collection_selftest.py": (
                "test_plain_collect_as_state_import_fails",
                "test_missing_lifecycle_dependency_fails",
            ),
            "scripts/check_progress_persistence_normalization_selftest.py": (
                "test_completion_task_id_without_trim_fails",
                "test_missing_preference_write_whitespace_evidence_fails",
            ),
            "scripts/check_settings_enum_normalization_selftest.py": (
                "test_missing_preference_trim_test_fails",
                "test_missing_task_area_trim_test_fails",
            ),
            "scripts/check_task_filter_minutes_normalization_selftest.py": (
                "test_missing_model_normalizer_fails",
                "test_raw_engine_stable_index_fails",
            ),
            "docs/packaged_task_catalog_audit.md": ("debug APK", "release AAB"),
            "scripts/check_task_catalog_quality_selftest.py": ("test_area_count_fails", "test_draft_marker_fails"),
            "scripts/check_runtime_catalog_count_selftest.py": (
                "test_hardcoded_about_count_fails",
                "test_missing_unit_test_evidence_fails",
            ),
            "scripts/check_screen_state_saveability_selftest.py": (
                "test_plain_remember_screen_state_fails",
                "test_missing_timer_route_fails",
            ),
            "scripts/check_task_repository_parser_selftest.py": (
                "test_energy_fallback_fails",
                "test_missing_parser_test_fails",
                "test_hardcoded_duration_set_fails",
                "test_missing_task_id_validator_fails",
                "test_local_task_id_pattern_fails",
            ),
            "scripts/check_packaged_task_catalog_selftest.py": ("test_missing_packaged_catalog_fails", "test_bad_zip_fails_without_root_relative_path"),
            "docs/task_catalog_quality_audit.md": ("80 task", "LOCAL_PROVEN"),
            "docs/policy_content_risk_audit.md": ("Policy Content Risk Audit", "LOCAL_PROVEN_FOR_CONTENT_SCAN"),
            "scripts/check_qa_evidence.py": ("read_gradle_release_identity", "zero-match log gates"),
            "scripts/check_qa_evidence_selftest.py": (
                "test_package_markers_use_gradle_release_identity",
                "test_invalid_png_signature_fails",
                "test_non_empty_zero_log_fails",
            ),
            "docs/qa_evidence_audit.md": ("QA Evidence Audit", "LOCAL_PROVEN"),
            "scripts/check_doc_inventory_selftest.py": (
                "test_missing_document_fails",
                "test_inventory_table_unexpected_row_fails",
                "test_story_bible_file_fails",
                "test_story_bible_root_file_fails",
            ),
            "scripts/check_release_artifact_manifest_checker_selftest.py": (
                "test_signed_packet",
                "sha256",
                "test_artifact_record_path_mismatch_fails",
                "test_gradle_identity_mismatch_fails",
                "test_unexpected_top_level_key_fails",
                "test_unknown_upload_blocker_fails",
            ),
            "scripts/release_identity.py": ("parse_gradle_release_identity", "versionName"),
            "scripts/release_identity_selftest.py": ("test_valid_identity_parses", "test_missing_version_code_fails"),
            "scripts/check_release_artifact_manifest_selftest.py": (
                "test_main_uses_gradle_release_identity",
                "upload_blockers",
            ),
            "scripts/check_play_submission_packet_sync_selftest.py": (
                "test_missing_checksum_entry_fails",
                "test_checksum_mismatch_fails",
            ),
            "scripts/check_play_upload_blockers_selftest.py": (
                "test_generated_handoff_passes_checker",
                "test_missing_blocker_record_fails",
            ),
            "scripts/check_play_upload_readiness_selftest.py": (
                "test_upload_blocker_handoff_checker_fails_on_stale_handoff",
                "test_packet_sync_checker_fails_on_stale_packet",
                "test_packet_sync_checker_passes_through_success",
            ),
            "scripts/check_play_upload_candidate_handoff_selftest.py": ("packet_rebuild_before_signed_bundle", "strict_upload_gate"),
            "scripts/check_prepare_play_upload_candidate_negative_path.py": ("Step 1/8", "FORBIDDEN_OUTPUT_MARKERS"),
            "scripts/check_prepare_play_upload_candidate_external_inputs_negative_path.py": (
                "Step 2/8",
                "external upload inputs are absent",
            ),
            "scripts/check_release_hygiene_selftest.py": ("test_key_like_files", "private key block"),
            "scripts/check_rc_traceability_selftest.py": (
                "test_missing_report_row_fails",
                "test_missing_evidence_marker_fails",
                "test_report_row_status_mismatch_fails_even_when_status_exists_elsewhere",
                "test_unexpected_evidence_path_fails",
            ),
            "docs/release_report.md": ("scripts/verify_release_candidate.sh", "Release Build Status"),
        },
    },
    "R12_EMULATOR_QA": {
        "status": LOCAL_PROVEN,
        "evidence": {
            "docs/emulator_no_internet_qa.md": ("Active default network: none", "Result"),
            "docs/emulator_android15_timer_double_submit_qa.md": ("PASSED_WITH_AVD_CAVEAT", "app-pid-error-filtered.txt"),
            "docs/emulator_android15_timer_session_goal_qa_2026_06_06.md": (
                "Timer Session Goal",
                "Цель: 5 мин",
            ),
            "docs/emulator_android15_timer_outcome_preview_qa_2026_06_06.md": (
                "Timer Outcome Preview",
                "После",
            ),
            "docs/emulator_android16_timer_control_icons_qa_2026_06_06.md": (
                "Timer Control Icons",
                "Пауза",
                "Продолжить",
            ),
            "docs/emulator_android16_smoke_qa.md": ("Android 16", "Crash buffer contained 0 lines"),
            "docs/emulator_android16_compact_screen_qa.md": ("720x1280", "Primary actions"),
            "docs/emulator_android16_large_screen_qa.md": ("2000x2560", "max-width"),
            "docs/emulator_android15_settings_privacy_summary_qa_2026_06_06.md": (
                "PrivacyBadgeGrid",
                "Без аналитики",
            ),
            "docs/emulator_android15_onboarding_flow_summary_qa_2026_06_06.md": (
                "Onboarding Flow Summary",
                "Первые 5 минут",
            ),
            "docs/emulator_android15_home_filter_whole_row_qa_2026_06_06.md": (
                "Home Filter Whole-Row",
                "whole-row 56dp",
            ),
            "docs/emulator_android15_home_filter_chevron_qa_2026_06_06.md": (
                "Home Filter Chevron",
                "chevron indicator",
            ),
            "docs/emulator_android16_home_filter_unframed_summary_qa_2026_06_06.md": (
                "Home Filter Unframed Summary",
                "unframed summary row",
            ),
            "docs/emulator_android15_task_status_pill_qa_2026_06_06.md": (
                "TaskStatusPill",
                "screenshots/play-store/02-home.png",
            ),
            "docs/emulator_android15_task_details_unframed_qa_2026_06_06.md": (
                "Task Details Unframed",
                "unframed",
            ),
            "docs/emulator_android15_progress_rhythm_summary_qa_2026_06_06.md": (
                "Progress rhythm summary",
                "screenshots/play-store/05-progress.png",
            ),
            "docs/emulator_android16_progress_rhythm_unframed_qa_2026_06_06.md": (
                "Progress Rhythm Unframed",
                "unframed",
            ),
            "docs/emulator_android16_result_content_focus_qa_2026_06_06.md": (
                "Result Content Focus",
                "generic amber",
            ),
            "docs/emulator_android16_result_peer_icons_qa_2026_06_06.md": (
                "Result peer-action icon polish",
                "HomeIcon",
                "StatsIcon",
            ),
            "docs/emulator_android16_settings_privacy_unframed_qa_2026_06_06.md": (
                "Settings Privacy Unframed",
                "unframed",
            ),
            "docs/emulator_android16_settings_about_summary_qa_2026_06_06.md": (
                "Settings About Summary",
                "О приложении",
            ),
            "scripts/check_qa_evidence.py": ("Android 16 large font", "read_gradle_release_identity"),
            "scripts/check_qa_evidence_selftest.py": (
                "test_package_markers_use_gradle_release_identity",
                "test_app_package_crash_log_fails_even_when_allowlisted",
            ),
            "docs/qa_evidence_audit.md": ("38 emulator QA reports", "173 UI XML/PNG pairs"),
        },
    },
    "R13_UPLOAD_SIGNING": {
        "status": EXTERNAL_REQUIRED,
        "evidence": {
            "docs/signing_setup.md": ("PORYADOK5_KEYSTORE_PATH", "check_release_signing_inputs.py"),
            "docs/release_hygiene.md": ("Release Hygiene", "LOCAL_PROVEN"),
            "scripts/check_release_hygiene.py": ("FORBIDDEN_SUFFIXES", "KEYSTORE_PASSWORD"),
            "scripts/check_release_signing_inputs.py": ("PORYADOK5_KEYSTORE_PATH", "PrivateKeyEntry"),
            "scripts/check_release_signing_inputs_selftest.py": ("partial release signing configuration", "PrivateKeyEntry"),
            "scripts/smoke_test_release_signing_pipeline.sh": (
                "Temporary keystore",
                "signed release AAB",
                "restore unsigned local RC",
                "artifact=not_included_unsigned_local_rc",
            ),
            "scripts/check_play_upload_candidate_handoff.py": ("rebuilds signed bundle", "strict upload readiness"),
            "scripts/check_play_upload_candidate_handoff_selftest.py": (
                "test_missing_strict_signing_check_fails",
                "test_missing_external_input_preflight_fails",
                "test_multiple_packet_rebuilds_fail",
            ),
            "scripts/check_prepare_play_upload_candidate_negative_path.py": (
                "GRADLE_USER_HOME",
                "Step 1/8",
                "fails before verifier",
            ),
            "scripts/check_prepare_play_upload_candidate_external_inputs_negative_path.py": (
                "temporary signing inputs",
                "fails before verifier",
            ),
            "docs/play_upload_handoff.md": ("play-submission/release/app-release.aab", "Required Inputs"),
            "play-submission/release/artifact_status.properties": ("signed_or_configured=false",),
            "play-submission/release/artifact_manifest.json": ("release_signing_inputs_missing",),
            "play-submission/release/upload_blockers.json": ("signed_upload_aab_missing", "external_secret"),
        },
    },
    "R14_PRIVACY_POLICY_PUBLICATION": {
        "status": EXTERNAL_REQUIRED,
        "evidence": {
            "docs/privacy_policy_ru.html": ("Перед публикацией замените эту строку", "не собирает"),
            "docs/play_upload_preflight.md": ("PORYADOK5_PRIVACY_POLICY_URL", "HTTP 200"),
            "scripts/check_play_upload_readiness.py": ("REMOTE_PRIVACY_REQUIRED_SNIPPETS", "validate_email"),
            "scripts/check_play_upload_external_inputs.py": (
                "remote_privacy_policy_failures",
                "PORYADOK5_SUPPORT_EMAIL",
            ),
            "scripts/check_play_upload_external_inputs_selftest.py": (
                "test_complete_inputs_and_remote_policy_pass",
                "test_remote_policy_http_error_fails",
            ),
            "scripts/render_privacy_policy.py": ("PORYADOK5_SUPPORT_EMAIL", "privacy_policy_publishable_ru.html"),
            "scripts/check_publishable_privacy_policy.py": ("publishable privacy policy", "PORYADOK5_SUPPORT_EMAIL"),
            "scripts/check_publishable_privacy_policy_selftest.py": (
                "test_required_missing_support_email_fails",
                "test_reserved_support_email_fails",
            ),
            "scripts/check_privacy_policy_rendering_selftest.py": (
                "test_render_replaces_pre_publication_contact_line",
                "test_validation_requires_expected_support_email_when_supplied",
            ),
            "scripts/check_publishable_privacy_policy_cli_selftest.py": (
                "render_privacy_policy.py",
                "privacy_policy_publishable_ru.html",
            ),
            "scripts/check_play_submission_publishable_policy_packet.py": (
                "PORYADOK5_SUPPORT_EMAIL",
                "check_publishable_privacy_policy.py",
            ),
            "scripts/check_play_submission_publishable_policy_packet_selftest.py": ("test_missing_checksums_fails",),
        },
    },
    "R15_PLAY_CONSOLE_MANUAL_FORMS": {
        "status": EXTERNAL_REQUIRED,
        "evidence": {
            "docs/play_console_forms_answers.json": ("collectsUserData", "targetAudienceAndContent"),
            "scripts/check_play_console_forms.py": ("read_gradle_release_identity", "packageName"),
            "scripts/check_play_console_forms_selftest.py": (
                "test_package_name_uses_gradle_release_identity",
                "test_ads_claim_fails",
                "test_data_collection_claim_fails",
            ),
            "docs/policy_content_risk_audit.md": ("Policy Content Risk Audit", "EXTERNAL_REQUIRED_FOR_PLAY_FORM_SUBMISSION"),
            "scripts/check_policy_content_risk.py": ("RISK_CATEGORIES", "target audience"),
            "scripts/check_policy_content_risk_selftest.py": ("test_violence_term_in_task_text_fails", "test_children_directed_store_term_fails"),
            "scripts/generate_release_artifact_manifest.py": (
                "play_console_forms_evidence_failed",
                "policy_content_risk_evidence_failed",
            ),
            "docs/google_play_checklist.md": ("Manual Play Console Actions", "Data Safety"),
            "scripts/check_play_upload_readiness.py": (
                "PORYADOK5_DATA_SAFETY_CONFIRMED",
                "PORYADOK5_INTERNAL_TESTING_CONFIRMED",
                "verify_play_console_evidence",
            ),
        },
    },
    "R16_FEATURE_GRAPHIC_APPROVAL": {
        "status": EXTERNAL_REQUIRED,
        "evidence": {
            "docs/feature_graphic_candidate.md": ("CONCEPT_CANDIDATE", "Play Console preview"),
            "scripts/check_play_upload_readiness.py": ("PORYADOK5_FEATURE_GRAPHIC_APPROVED",),
        },
    },
}


def display_path(path: Path, root: Path = ROOT) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def traceability_table_rows(text: str) -> dict[str, dict[str, object]]:
    rows: dict[str, dict[str, object]] = {}
    duplicate_ids: set[str] = set()
    in_table = False

    for line in text.splitlines():
        if line.strip() == "| ID | Requirement | Status | Evidence |":
            in_table = True
            continue
        if not in_table:
            continue
        if not line.startswith("|"):
            break
        if re.fullmatch(r"\|\s*-+\s*\|\s*-+\s*\|\s*-+\s*\|\s*-+\s*\|", line.strip()):
            continue

        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 4:
            continue

        requirement_id = cells[0]
        if requirement_id in rows:
            duplicate_ids.add(requirement_id)
            continue

        rows[requirement_id] = {
            "status": cells[2],
            "evidence_paths": tuple(re.findall(r"`([^`]+)`", cells[3])),
        }

    if duplicate_ids:
        rows["__DUPLICATE_IDS__"] = {
            "status": "",
            "evidence_paths": tuple(sorted(duplicate_ids)),
        }

    return rows


def traceability_table_failures(
    report_text: str,
    requirements: dict[str, dict[str, object]],
) -> list[str]:
    rows = traceability_table_rows(report_text)
    failures: list[str] = []

    if not rows:
        return ["traceability report table is missing or has no requirement rows"]

    duplicate_record = rows.pop("__DUPLICATE_IDS__", None)
    if duplicate_record is not None:
        for requirement_id in duplicate_record["evidence_paths"]:
            failures.append(f"traceability report table has duplicate row for {requirement_id}")

    expected_ids = set(requirements)
    actual_ids = set(rows)

    for requirement_id in sorted(expected_ids - actual_ids):
        failures.append(f"traceability report table is missing row for {requirement_id}")
    for requirement_id in sorted(actual_ids - expected_ids):
        failures.append(f"traceability report table has unexpected row for {requirement_id}")

    for requirement_id in sorted(expected_ids & actual_ids):
        row = rows[requirement_id]
        expected_status = str(requirements[requirement_id]["status"])
        if row["status"] != expected_status:
            failures.append(
                f"traceability report row {requirement_id} has status {row['status']} "
                f"instead of {expected_status}"
            )

        evidence = requirements[requirement_id]["evidence"]
        assert isinstance(evidence, dict)
        expected_evidence_paths = set(evidence)
        row_evidence_paths = set(row["evidence_paths"])
        if not row_evidence_paths:
            failures.append(f"traceability report row {requirement_id} has no evidence paths")
            continue

        if expected_evidence_paths.isdisjoint(row_evidence_paths):
            failures.append(f"traceability report row {requirement_id} has no recognized evidence paths")
        for evidence_path in sorted(row_evidence_paths - expected_evidence_paths):
            failures.append(
                f"traceability report row {requirement_id} has unexpected evidence path: {evidence_path}"
            )

    return failures


def traceability_failures(
    root: Path = ROOT,
    report: Path = REPORT,
    requirements: dict[str, dict[str, object]] = REQUIREMENTS,
    min_local_count: int = 10,
    expected_external_count: int = 4,
) -> list[str]:
    failures: list[str] = []

    if not report.exists():
        failures.append(f"missing traceability report: {display_path(report, root)}")
    else:
        report_text = report.read_text(encoding="utf-8")
        failures.extend(traceability_table_failures(report_text, requirements))
        for requirement_id, metadata in requirements.items():
            expected_status = str(metadata["status"])
            if requirement_id not in report_text:
                failures.append(f"traceability report is missing {requirement_id}")
            if f"| {requirement_id} |" not in report_text:
                failures.append(f"traceability report table is missing row for {requirement_id}")
            if expected_status not in report_text:
                failures.append(f"traceability report is missing status {expected_status}")

    for requirement_id, metadata in requirements.items():
        evidence = metadata["evidence"]
        assert isinstance(evidence, dict)
        for relative_path, snippets in evidence.items():
            path = root / relative_path
            if not path.exists():
                failures.append(f"{requirement_id}: missing evidence file {relative_path}")
                continue
            if snippets:
                text = path.read_text(encoding="utf-8", errors="ignore")
                for snippet in snippets:
                    if snippet not in text:
                        failures.append(f"{requirement_id}: {relative_path} is missing evidence marker {snippet!r}")

    local_count = sum(1 for metadata in requirements.values() if metadata["status"] == LOCAL_PROVEN)
    external_count = sum(1 for metadata in requirements.values() if metadata["status"] == EXTERNAL_REQUIRED)

    if local_count < min_local_count:
        failures.append("traceability coverage is unexpectedly low for local requirements")
    if external_count != expected_external_count:
        failures.append(f"expected {expected_external_count} external requirements, found {external_count}")

    return failures


def main() -> int:
    failures = traceability_failures()

    local_count = sum(1 for metadata in REQUIREMENTS.values() if metadata["status"] == LOCAL_PROVEN)
    external_count = sum(1 for metadata in REQUIREMENTS.values() if metadata["status"] == EXTERNAL_REQUIRED)

    if failures:
        print("RC requirement traceability check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print(
        "PASS: RC requirement traceability covers "
        f"{len(REQUIREMENTS)} requirements ({local_count} local, {external_count} external)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
