# Порядок 5 Play Submission Packet

This packet groups the current local materials for manual Play Console submission.

## Contents

- `text/store_listing_ru.md`: app name, short description, full description, release notes and screenshot captions.
- `docs/store_listing_audit.md`: Play field limits and automated store listing gate.
- `text/privacy_policy_draft_ru.md`: source text for the public privacy policy page.
- `text/privacy_policy_ru.html`: self-contained static HTML privacy policy template for hosting.
- `text/privacy_policy_publishable_ru.html`: generated publishable HTML privacy policy when `PORYADOK5_SUPPORT_EMAIL` is set.
- `project/README.md` and `project/AGENTS.md`: repository overview and agent/release-candidate working notes copied for full handoff context.
- `docs/product_decision.md`, `docs/product_spec.md`, `docs/tech_stack.md`, `docs/tech_stack_decision.md`, `docs/release_plan.md`, `docs/release_report.md`: product, stack and release-plan evidence.
- `docs/ui_audit.md`, `docs/performance_notes.md`, `docs/privacy_and_permissions.md`, `docs/art_direction.md`, `docs/asset_prompts.md`, `docs/asset_manifest.md`, `docs/content_audit.md`, `docs/accessibility_notes.md`, `docs/screenshot_plan.md`: design, content, accessibility, privacy and asset planning evidence.
- `assets/app-icon/play-store-icon-512.png`: Google Play 512x512 app icon PNG.
- `assets/screenshots/*.png`: real app screenshots from `ru.poryadok5.app`.
- `assets/feature-graphic/feature-graphic-candidate-03.png`: 1024x500 PNG feature graphic candidate.
- `docs/play_console_submission.md`: field-by-field Play Console map.
- `docs/play_console_forms_answers.json`: structured answers for App Access, Ads, Data Safety, Target Audience and Content Rating.
- `docs/policy_content_risk_audit.md`: local content-risk scan supporting Target Audience and Content Rating answers.
- `docs/play_upload_preflight.md`: local RC audit and strict upload gate instructions.
- `docs/play_upload_handoff.md`: final signed upload packet handoff sequence.
- `docs/rc_requirement_traceability.md`: original RC plan requirement-to-evidence matrix.
- `docs/doc_inventory.md`: required RC documentation inventory.
- `docs/stack_version_audit.md`: Gradle, Kotlin, Compose and Android SDK version audit.
- `docs/clean_build_audit.md`: clean Gradle build gate notes.
- `docs/google_play_checklist.md`: policy and release checklist.
- `docs/android_backup_policy_audit.md`: Android backup/data extraction manifest audit.
- `docs/aab_metadata_audit.md`: release AAB package, version, SDK and permission metadata audit.
- `docs/aab_universal_apk_audit.md`: bundletool universal APK expansion audit.
- `docs/apk_metadata_audit.md`: package, version and SDK metadata audit.
- `docs/dependency_privacy_audit.md`: release runtime dependency audit for ads, analytics and tracking SDK absence.
- `docs/packaged_app_contents_audit.md`: built APK/AAB ZIP contents audit for runtime scope and workspace-only file exclusion.
- `docs/native_library_packaging_audit.md`: installable APK native library compression and 16 KB alignment audit.
- `docs/packaged_task_catalog_audit.md`: packaged APK/AAB task catalog equality audit.
- `docs/task_catalog_quality_audit.md`: local 80-task catalog structure, distribution and text-quality audit.
- `docs/qa_evidence_audit.md`: local gate summary for emulator evidence files, screenshots, UI XML and crash/error gates.
- `docs/qa_test_plan.md`: automated and manual QA plan.
- `docs/emulator_timer_background_qa.md`: latest Android 15 timer background/resume QA evidence summary.
- `docs/emulator_android15_timer_double_submit_qa.md`: Android 15 timer double-submit QA evidence summary.
- `docs/emulator_no_internet_qa.md`: latest Android 15 no-internet flow QA evidence summary.
- `docs/emulator_android15_compose_bom_smoke_qa.md`: latest Android 15 post-Compose-BOM smoke QA evidence summary.
- `docs/emulator_android16_smoke_qa.md`: latest Android 16 smoke QA evidence summary.
- `docs/emulator_android16_compact_screen_qa.md`: latest Android 16 compact-screen QA evidence summary.
- `docs/emulator_android16_large_screen_qa.md`: latest Android 16 large-screen QA evidence summary.
- `docs/emulator_android16_large_font_qa.md`: latest Android 16 large-font QA evidence summary.
- `docs/emulator_android16_home_filter_disclosure_qa_2026_06_06.md`: Android 16 collapsed Home filter disclosure QA evidence summary.
- `docs/emulator_android15_home_filter_whole_row_qa_2026_06_06.md`: Android 15 Home filter whole-row disclosure QA evidence summary.
- `docs/emulator_android15_home_filter_chevron_qa_2026_06_06.md`: Android 15 Home filter chevron disclosure QA evidence summary.
- `docs/emulator_android16_home_filter_unframed_summary_qa_2026_06_06.md`: Android 16 Home filter unframed summary QA evidence summary.
- `docs/emulator_android15_home_stats_icon_qa_2026_06_06.md`: Android 15 Home stats icon QA evidence summary.
- `docs/emulator_android16_task_details_briefing_qa_2026_06_06.md`: Android 16 Task details briefing QA evidence summary.
- `docs/emulator_android15_task_details_unframed_qa_2026_06_06.md`: Android 15 Task details unframed briefing QA evidence summary.
- `docs/emulator_android15_timer_completion_dock_qa_2026_06_06.md`: Android 15 Timer completion dock QA evidence summary.
- `docs/emulator_android15_timer_session_goal_qa_2026_06_06.md`: Android 15 Timer session goal QA evidence summary.
- `docs/emulator_android15_timer_outcome_preview_qa_2026_06_06.md`: Android 15 Timer outcome preview QA evidence summary.
- `docs/emulator_android16_timer_control_icons_qa_2026_06_06.md`: Android 16 Timer control icons QA evidence summary.
- `docs/emulator_android15_result_details_first_qa_2026_06_06.md`: Android 15 Result details-first primary QA evidence summary.
- `docs/emulator_android16_result_content_focus_qa_2026_06_06.md`: Android 16 Result content-focus QA evidence summary.
- `docs/emulator_android16_result_peer_icons_qa_2026_06_06.md`: Android 16 Result peer-action icons QA evidence summary.
- `docs/emulator_android15_settings_privacy_summary_qa_2026_06_06.md`: Android 15 Settings privacy summary QA evidence summary.
- `docs/emulator_android15_onboarding_flow_summary_qa_2026_06_06.md`: Android 15 Onboarding flow summary QA evidence summary.
- `docs/emulator_android15_task_status_pill_qa_2026_06_06.md`: Android 15 Task status pill QA evidence summary.
- `docs/emulator_android15_progress_rhythm_summary_qa_2026_06_06.md`: Android 15 Progress rhythm summary QA evidence summary.
- `docs/emulator_android16_progress_rhythm_unframed_qa_2026_06_06.md`: Android 16 Progress rhythm unframed QA evidence summary.
- `docs/emulator_android16_settings_privacy_unframed_qa_2026_06_06.md`: Android 16 Settings privacy unframed QA evidence summary.
- `docs/emulator_android16_settings_about_summary_qa_2026_06_06.md`: Android 16 Settings about-summary QA evidence summary.
- `docs/store_asset_pixel_audit.md`: pixel-level PNG validation for screenshots, icon and feature graphic candidate.
- `docs/play_store_icon.md`: Play Store app icon source and validation notes.
- `docs/signing_setup.md`: signing setup notes.
- `docs/release_hygiene.md`: no-keystore/no-secret workspace hygiene gate.
- `scripts/check_play_submission_doc_coverage.py`, `scripts/check_release_signing_inputs.py` and `scripts/smoke_test_release_signing_pipeline.sh` are not copied into this packet, but are part of the repository handoff gates for validating required RC doc coverage, external keystore inputs and signed-AAB packet inclusion.
- `release/artifact_status.properties`: whether a signed AAB was included.
- `release/artifact_manifest.json`: generated APK/AAB identity, SHA-256, signing status and upload blocker manifest.
- `release/upload_blockers.json`: generated action/evidence handoff for every current upload blocker in `artifact_manifest.json`.
- `checksums.sha256`: SHA-256 checksums for packet files.

## External Steps Still Required

- Set `PORYADOK5_SUPPORT_EMAIL` to generate `text/privacy_policy_publishable_ru.html`, then publish that file or equivalent content.
- Publish the privacy policy at a stable public HTTPS URL.
- Configure upload signing and include a signed AAB before Play upload.
- Run `scripts/check_release_signing_inputs.py --require` before the final signed build.
- Use `scripts/smoke_test_release_signing_pipeline.sh` for a local temporary-key dry run if the signing pipeline changes.
- Approve the feature graphic in Play Console preview.
- Complete Play Console Data Safety, Target Audience and Content Rating forms.
- Use `release/upload_blockers.json` as the machine-readable action list until it has an empty `blockers` array.
