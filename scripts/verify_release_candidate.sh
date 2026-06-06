#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

fail() {
  printf 'FAIL: %s\n' "$1" >&2
  exit 1
}

pass() {
  printf 'PASS: %s\n' "$1"
}

note() {
  printf 'NOTE: %s\n' "$1"
}

find_android_sdk() {
  if [[ -n "${ANDROID_HOME:-}" && -d "$ANDROID_HOME" ]]; then
    printf '%s\n' "$ANDROID_HOME"
    return
  fi

  if [[ -f local.properties ]]; then
    local sdk_dir
    sdk_dir="$(awk -F= '/^sdk.dir=/{print substr($0, index($0,$2))}' local.properties | tail -n 1)"
    if [[ -n "$sdk_dir" && -d "$sdk_dir" ]]; then
      printf '%s\n' "$sdk_dir"
      return
    fi
  fi

  if [[ -d "$HOME/Library/Android/sdk" ]]; then
    printf '%s\n' "$HOME/Library/Android/sdk"
    return
  fi

  fail "Android SDK not found. Set ANDROID_HOME or local.properties sdk.dir."
}

find_zipalign() {
  local sdk="$1"
  local candidate
  candidate="$(find "$sdk/build-tools" -name zipalign -type f 2>/dev/null | sort | tail -n 1)"
  [[ -n "$candidate" ]] || fail "zipalign not found under $sdk/build-tools."
  printf '%s\n' "$candidate"
}

find_jarsigner() {
  if [[ -n "${JAVA_HOME:-}" && -x "$JAVA_HOME/bin/jarsigner" ]]; then
    printf '%s\n' "$JAVA_HOME/bin/jarsigner"
    return
  fi

  local studio_jbr="/Applications/Android Studio.app/Contents/jbr/Contents/Home/bin/jarsigner"
  if [[ -x "$studio_jbr" ]]; then
    printf '%s\n' "$studio_jbr"
    return
  fi

  local candidate
  candidate="$(command -v jarsigner || true)"
  if [[ -n "$candidate" ]]; then
    printf '%s\n' "$candidate"
    return
  fi

  fail "jarsigner not found. Install JDK or set JAVA_HOME."
}

check_no_matches() {
  local label="$1"
  shift

  set +e
  "$@"
  local status=$?
  set -e

  if [[ "$status" -eq 0 ]]; then
    fail "$label found unexpected matches."
  fi

  [[ "$status" -eq 1 ]] || fail "$label check failed with exit code $status."

  pass "$label"
}

validate_screenshots() {
  local expected_dir="screenshots/play-store"
  local expected_files=(
    "01-onboarding.png"
    "02-home.png"
    "03-timer.png"
    "04-result.png"
    "05-progress.png"
    "06-settings.png"
  )

  [[ -d "$expected_dir" ]] || fail "$expected_dir does not exist."

  local file
  for file in "${expected_files[@]}"; do
    [[ -f "$expected_dir/$file" ]] || fail "Missing screenshot: $expected_dir/$file"
  done

  if ! command -v sips >/dev/null 2>&1; then
    note "sips not found; screenshot dimensions were not checked."
    return
  fi

  local width height
  for file in "${expected_files[@]}"; do
    width="$(sips -g pixelWidth "$expected_dir/$file" 2>/dev/null | awk '/pixelWidth/{print $2}')"
    height="$(sips -g pixelHeight "$expected_dir/$file" 2>/dev/null | awk '/pixelHeight/{print $2}')"
    [[ "$width" == "1080" && "$height" == "2400" ]] ||
      fail "Unexpected screenshot size for $expected_dir/$file: ${width}x${height}"
  done

  pass "Play Store screenshots exist and are 1080x2400"
}

validate_feature_graphic_candidate() {
  local file="store-assets/feature-graphic/feature-graphic-candidate-03.png"
  [[ -f "$file" ]] || fail "Missing feature graphic candidate: $file"

  if ! command -v sips >/dev/null 2>&1; then
    note "sips not found; feature graphic dimensions were not checked."
    return
  fi

  local width height alpha
  width="$(sips -g pixelWidth "$file" 2>/dev/null | awk '/pixelWidth/{print $2}')"
  height="$(sips -g pixelHeight "$file" 2>/dev/null | awk '/pixelHeight/{print $2}')"
  alpha="$(sips -g hasAlpha "$file" 2>/dev/null | awk '/hasAlpha/{print $2}')"

  [[ "$width" == "1024" && "$height" == "500" ]] ||
    fail "Unexpected feature graphic candidate size for $file: ${width}x${height}"
  [[ "$alpha" == "no" ]] ||
    fail "Feature graphic candidate must not have alpha: $file"

  pass "Feature graphic candidate exists, is 1024x500 and has no alpha"
}

validate_submission_packet() {
  local packet="play-submission"
  [[ -d "$packet" ]] || fail "Missing Play submission packet. Run scripts/build_play_submission_packet.sh."

  local expected_files=(
    "README.md"
    "checksums.sha256"
    "project/README.md"
    "project/AGENTS.md"
    "docs/product_decision.md"
    "docs/product_spec.md"
    "docs/tech_stack.md"
    "docs/tech_stack_decision.md"
    "text/store_listing_ru.md"
    "docs/store_listing_audit.md"
    "text/privacy_policy_draft_ru.md"
    "text/privacy_policy_ru.html"
    "docs/play_console_submission.md"
    "docs/play_console_forms_answers.json"
    "docs/policy_content_risk_audit.md"
    "docs/play_upload_preflight.md"
    "docs/play_upload_handoff.md"
    "docs/rc_requirement_traceability.md"
    "docs/doc_inventory.md"
    "docs/stack_version_audit.md"
    "docs/clean_build_audit.md"
    "docs/release_plan.md"
    "docs/release_report.md"
    "docs/google_play_checklist.md"
    "docs/ui_audit.md"
    "docs/performance_notes.md"
    "docs/privacy_and_permissions.md"
    "docs/android_backup_policy_audit.md"
    "docs/aab_metadata_audit.md"
    "docs/aab_universal_apk_audit.md"
    "docs/apk_metadata_audit.md"
    "docs/dependency_privacy_audit.md"
    "docs/packaged_app_contents_audit.md"
    "docs/native_library_packaging_audit.md"
    "docs/packaged_task_catalog_audit.md"
    "docs/task_catalog_quality_audit.md"
    "docs/qa_evidence_audit.md"
    "docs/qa_test_plan.md"
    "docs/emulator_timer_background_qa.md"
    "docs/emulator_android15_timer_double_submit_qa.md"
    "docs/emulator_no_internet_qa.md"
    "docs/emulator_android15_compose_bom_smoke_qa.md"
    "docs/emulator_android16_smoke_qa.md"
    "docs/emulator_android16_compact_screen_qa.md"
    "docs/emulator_android16_large_screen_qa.md"
    "docs/emulator_android16_large_font_qa.md"
    "docs/emulator_android16_home_filter_disclosure_qa_2026_06_06.md"
    "docs/emulator_android15_home_filter_whole_row_qa_2026_06_06.md"
    "docs/emulator_android15_home_filter_chevron_qa_2026_06_06.md"
    "docs/emulator_android16_home_filter_unframed_summary_qa_2026_06_06.md"
    "docs/emulator_android16_task_details_briefing_qa_2026_06_06.md"
    "docs/emulator_android15_task_details_unframed_qa_2026_06_06.md"
    "docs/emulator_android15_timer_completion_dock_qa_2026_06_06.md"
    "docs/emulator_android15_timer_session_goal_qa_2026_06_06.md"
    "docs/emulator_android15_timer_outcome_preview_qa_2026_06_06.md"
    "docs/emulator_android16_timer_control_icons_qa_2026_06_06.md"
    "docs/emulator_android16_result_content_focus_qa_2026_06_06.md"
    "docs/emulator_android16_result_peer_icons_qa_2026_06_06.md"
    "docs/emulator_android15_settings_privacy_summary_qa_2026_06_06.md"
    "docs/emulator_android15_onboarding_flow_summary_qa_2026_06_06.md"
    "docs/emulator_android15_task_status_pill_qa_2026_06_06.md"
    "docs/emulator_android15_progress_rhythm_summary_qa_2026_06_06.md"
    "docs/emulator_android16_progress_rhythm_unframed_qa_2026_06_06.md"
    "docs/emulator_android16_settings_privacy_unframed_qa_2026_06_06.md"
    "docs/emulator_android16_settings_about_summary_qa_2026_06_06.md"
    "docs/screenshot_manifest.md"
    "docs/store_asset_pixel_audit.md"
    "docs/play_store_icon.md"
    "docs/feature_graphic_candidate.md"
    "docs/art_direction.md"
    "docs/asset_prompts.md"
    "docs/asset_manifest.md"
    "docs/content_audit.md"
    "docs/accessibility_notes.md"
    "docs/screenshot_plan.md"
    "docs/signing_setup.md"
    "docs/release_hygiene.md"
    "assets/app-icon/play-store-icon-512.png"
    "assets/screenshots/01-onboarding.png"
    "assets/screenshots/02-home.png"
    "assets/screenshots/03-timer.png"
    "assets/screenshots/04-result.png"
    "assets/screenshots/05-progress.png"
    "assets/screenshots/06-settings.png"
    "assets/feature-graphic/feature-graphic-candidate-03.png"
    "release/artifact_status.properties"
    "release/artifact_manifest.json"
    "release/upload_blockers.json"
  )

  local file
  for file in "${expected_files[@]}"; do
    [[ -f "$packet/$file" ]] || fail "Missing packet file: $packet/$file"
  done

  cmp -s docs/store_listing_ru.md "$packet/text/store_listing_ru.md" ||
    fail "Packet store listing is out of sync."
  cmp -s docs/store_listing_audit.md "$packet/docs/store_listing_audit.md" ||
    fail "Packet store listing audit is out of sync."
  cmp -s docs/privacy_policy_draft_ru.md "$packet/text/privacy_policy_draft_ru.md" ||
    fail "Packet privacy policy draft is out of sync."
  cmp -s docs/privacy_policy_ru.html "$packet/text/privacy_policy_ru.html" ||
    fail "Packet privacy policy HTML is out of sync."
  cmp -s README.md "$packet/project/README.md" ||
    fail "Packet project README is out of sync."
  cmp -s AGENTS.md "$packet/project/AGENTS.md" ||
    fail "Packet project AGENTS notes are out of sync."
  cmp -s docs/product_decision.md "$packet/docs/product_decision.md" ||
    fail "Packet product decision doc is out of sync."
  cmp -s docs/product_spec.md "$packet/docs/product_spec.md" ||
    fail "Packet product spec is out of sync."
  cmp -s docs/tech_stack.md "$packet/docs/tech_stack.md" ||
    fail "Packet tech stack doc is out of sync."
  cmp -s docs/tech_stack_decision.md "$packet/docs/tech_stack_decision.md" ||
    fail "Packet tech stack decision doc is out of sync."
  cmp -s docs/play_console_submission.md "$packet/docs/play_console_submission.md" ||
    fail "Packet Play Console submission map is out of sync."
  cmp -s docs/play_console_forms_answers.json "$packet/docs/play_console_forms_answers.json" ||
    fail "Packet Play Console forms answers are out of sync."
  cmp -s docs/policy_content_risk_audit.md "$packet/docs/policy_content_risk_audit.md" ||
    fail "Packet policy content risk audit is out of sync."
  cmp -s docs/play_upload_preflight.md "$packet/docs/play_upload_preflight.md" ||
    fail "Packet Play upload preflight doc is out of sync."
  cmp -s docs/play_upload_handoff.md "$packet/docs/play_upload_handoff.md" ||
    fail "Packet Play upload handoff doc is out of sync."
  cmp -s docs/rc_requirement_traceability.md "$packet/docs/rc_requirement_traceability.md" ||
    fail "Packet RC requirement traceability doc is out of sync."
  cmp -s docs/doc_inventory.md "$packet/docs/doc_inventory.md" ||
    fail "Packet documentation inventory is out of sync."
  cmp -s docs/stack_version_audit.md "$packet/docs/stack_version_audit.md" ||
    fail "Packet stack version audit is out of sync."
  cmp -s docs/clean_build_audit.md "$packet/docs/clean_build_audit.md" ||
    fail "Packet clean build audit is out of sync."
  cmp -s docs/release_plan.md "$packet/docs/release_plan.md" ||
    fail "Packet release plan is out of sync."
  cmp -s docs/release_report.md "$packet/docs/release_report.md" ||
    fail "Packet release report is out of sync."
  cmp -s docs/google_play_checklist.md "$packet/docs/google_play_checklist.md" ||
    fail "Packet Google Play checklist is out of sync."
  cmp -s docs/ui_audit.md "$packet/docs/ui_audit.md" ||
    fail "Packet UI audit is out of sync."
  cmp -s docs/performance_notes.md "$packet/docs/performance_notes.md" ||
    fail "Packet performance notes are out of sync."
  cmp -s docs/privacy_and_permissions.md "$packet/docs/privacy_and_permissions.md" ||
    fail "Packet privacy and permissions doc is out of sync."
  cmp -s docs/android_backup_policy_audit.md "$packet/docs/android_backup_policy_audit.md" ||
    fail "Packet Android backup policy audit is out of sync."
  cmp -s docs/aab_metadata_audit.md "$packet/docs/aab_metadata_audit.md" ||
    fail "Packet AAB metadata audit is out of sync."
  cmp -s docs/aab_universal_apk_audit.md "$packet/docs/aab_universal_apk_audit.md" ||
    fail "Packet AAB universal APK audit is out of sync."
  cmp -s docs/apk_metadata_audit.md "$packet/docs/apk_metadata_audit.md" ||
    fail "Packet APK metadata audit is out of sync."
  cmp -s docs/dependency_privacy_audit.md "$packet/docs/dependency_privacy_audit.md" ||
    fail "Packet dependency privacy audit is out of sync."
  cmp -s docs/packaged_app_contents_audit.md "$packet/docs/packaged_app_contents_audit.md" ||
    fail "Packet packaged app contents audit is out of sync."
  cmp -s docs/native_library_packaging_audit.md "$packet/docs/native_library_packaging_audit.md" ||
    fail "Packet native library packaging audit is out of sync."
  cmp -s docs/packaged_task_catalog_audit.md "$packet/docs/packaged_task_catalog_audit.md" ||
    fail "Packet packaged task catalog audit is out of sync."
  cmp -s docs/task_catalog_quality_audit.md "$packet/docs/task_catalog_quality_audit.md" ||
    fail "Packet task catalog quality audit is out of sync."
  cmp -s docs/qa_evidence_audit.md "$packet/docs/qa_evidence_audit.md" ||
    fail "Packet QA evidence audit is out of sync."
  cmp -s docs/qa_test_plan.md "$packet/docs/qa_test_plan.md" ||
    fail "Packet QA test plan is out of sync."
  cmp -s docs/emulator_timer_background_qa.md "$packet/docs/emulator_timer_background_qa.md" ||
    fail "Packet timer background QA report is out of sync."
  cmp -s docs/emulator_android15_timer_double_submit_qa.md "$packet/docs/emulator_android15_timer_double_submit_qa.md" ||
    fail "Packet timer double-submit QA report is out of sync."
  cmp -s docs/emulator_no_internet_qa.md "$packet/docs/emulator_no_internet_qa.md" ||
    fail "Packet no-internet QA report is out of sync."
  cmp -s docs/emulator_android15_compose_bom_smoke_qa.md "$packet/docs/emulator_android15_compose_bom_smoke_qa.md" ||
    fail "Packet Android 15 Compose BOM smoke QA report is out of sync."
  cmp -s docs/emulator_android16_smoke_qa.md "$packet/docs/emulator_android16_smoke_qa.md" ||
    fail "Packet Android 16 smoke QA report is out of sync."
  cmp -s docs/emulator_android16_compact_screen_qa.md "$packet/docs/emulator_android16_compact_screen_qa.md" ||
    fail "Packet Android 16 compact-screen QA report is out of sync."
  cmp -s docs/emulator_android16_large_screen_qa.md "$packet/docs/emulator_android16_large_screen_qa.md" ||
    fail "Packet Android 16 large-screen QA report is out of sync."
  cmp -s docs/emulator_android16_large_font_qa.md "$packet/docs/emulator_android16_large_font_qa.md" ||
    fail "Packet Android 16 large-font QA report is out of sync."
  cmp -s docs/emulator_android16_home_filter_disclosure_qa_2026_06_06.md "$packet/docs/emulator_android16_home_filter_disclosure_qa_2026_06_06.md" ||
    fail "Packet Android 16 Home filter disclosure QA report is out of sync."
  cmp -s docs/emulator_android15_home_filter_whole_row_qa_2026_06_06.md "$packet/docs/emulator_android15_home_filter_whole_row_qa_2026_06_06.md" ||
    fail "Packet Android 15 Home filter whole-row QA report is out of sync."
  cmp -s docs/emulator_android15_home_filter_chevron_qa_2026_06_06.md "$packet/docs/emulator_android15_home_filter_chevron_qa_2026_06_06.md" ||
    fail "Packet Android 15 Home filter chevron QA report is out of sync."
  cmp -s docs/emulator_android16_home_filter_unframed_summary_qa_2026_06_06.md "$packet/docs/emulator_android16_home_filter_unframed_summary_qa_2026_06_06.md" ||
    fail "Packet Android 16 Home filter unframed-summary QA report is out of sync."
  cmp -s docs/emulator_android16_task_details_briefing_qa_2026_06_06.md "$packet/docs/emulator_android16_task_details_briefing_qa_2026_06_06.md" ||
    fail "Packet Android 16 Task details briefing QA report is out of sync."
  cmp -s docs/emulator_android15_task_details_unframed_qa_2026_06_06.md "$packet/docs/emulator_android15_task_details_unframed_qa_2026_06_06.md" ||
    fail "Packet Android 15 Task details unframed QA report is out of sync."
  cmp -s docs/emulator_android15_timer_completion_dock_qa_2026_06_06.md "$packet/docs/emulator_android15_timer_completion_dock_qa_2026_06_06.md" ||
    fail "Packet Android 15 Timer completion dock QA report is out of sync."
  cmp -s docs/emulator_android15_timer_session_goal_qa_2026_06_06.md "$packet/docs/emulator_android15_timer_session_goal_qa_2026_06_06.md" ||
    fail "Packet Android 15 Timer session goal QA report is out of sync."
  cmp -s docs/emulator_android15_timer_outcome_preview_qa_2026_06_06.md "$packet/docs/emulator_android15_timer_outcome_preview_qa_2026_06_06.md" ||
    fail "Packet Android 15 Timer outcome preview QA report is out of sync."
  cmp -s docs/emulator_android16_timer_control_icons_qa_2026_06_06.md "$packet/docs/emulator_android16_timer_control_icons_qa_2026_06_06.md" ||
    fail "Packet Android 16 Timer control icons QA report is out of sync."
  cmp -s docs/emulator_android16_result_content_focus_qa_2026_06_06.md "$packet/docs/emulator_android16_result_content_focus_qa_2026_06_06.md" ||
    fail "Packet Android 16 Result content-focus QA report is out of sync."
  cmp -s docs/emulator_android16_result_peer_icons_qa_2026_06_06.md "$packet/docs/emulator_android16_result_peer_icons_qa_2026_06_06.md" ||
    fail "Packet Android 16 Result peer icons QA report is out of sync."
  cmp -s docs/emulator_android15_settings_privacy_summary_qa_2026_06_06.md "$packet/docs/emulator_android15_settings_privacy_summary_qa_2026_06_06.md" ||
    fail "Packet Android 15 Settings privacy summary QA report is out of sync."
  cmp -s docs/emulator_android15_onboarding_flow_summary_qa_2026_06_06.md "$packet/docs/emulator_android15_onboarding_flow_summary_qa_2026_06_06.md" ||
    fail "Packet Android 15 Onboarding flow summary QA report is out of sync."
  cmp -s docs/emulator_android15_task_status_pill_qa_2026_06_06.md "$packet/docs/emulator_android15_task_status_pill_qa_2026_06_06.md" ||
    fail "Packet Android 15 Task status pill QA report is out of sync."
  cmp -s docs/emulator_android15_progress_rhythm_summary_qa_2026_06_06.md "$packet/docs/emulator_android15_progress_rhythm_summary_qa_2026_06_06.md" ||
    fail "Packet Android 15 Progress rhythm summary QA report is out of sync."
  cmp -s docs/emulator_android16_progress_rhythm_unframed_qa_2026_06_06.md "$packet/docs/emulator_android16_progress_rhythm_unframed_qa_2026_06_06.md" ||
    fail "Packet Android 16 Progress rhythm unframed QA report is out of sync."
  cmp -s docs/emulator_android16_settings_privacy_unframed_qa_2026_06_06.md "$packet/docs/emulator_android16_settings_privacy_unframed_qa_2026_06_06.md" ||
    fail "Packet Android 16 Settings privacy unframed QA report is out of sync."
  cmp -s docs/emulator_android16_settings_about_summary_qa_2026_06_06.md "$packet/docs/emulator_android16_settings_about_summary_qa_2026_06_06.md" ||
    fail "Packet Android 16 Settings about summary QA report is out of sync."
  cmp -s docs/screenshot_manifest.md "$packet/docs/screenshot_manifest.md" ||
    fail "Packet screenshot manifest is out of sync."
  cmp -s docs/store_asset_pixel_audit.md "$packet/docs/store_asset_pixel_audit.md" ||
    fail "Packet store asset pixel audit is out of sync."
  cmp -s docs/play_store_icon.md "$packet/docs/play_store_icon.md" ||
    fail "Packet Play Store icon doc is out of sync."
  cmp -s docs/feature_graphic_candidate.md "$packet/docs/feature_graphic_candidate.md" ||
    fail "Packet feature graphic notes are out of sync."
  cmp -s docs/art_direction.md "$packet/docs/art_direction.md" ||
    fail "Packet art direction doc is out of sync."
  cmp -s docs/asset_prompts.md "$packet/docs/asset_prompts.md" ||
    fail "Packet asset prompts doc is out of sync."
  cmp -s docs/asset_manifest.md "$packet/docs/asset_manifest.md" ||
    fail "Packet asset manifest is out of sync."
  cmp -s docs/content_audit.md "$packet/docs/content_audit.md" ||
    fail "Packet content audit is out of sync."
  cmp -s docs/accessibility_notes.md "$packet/docs/accessibility_notes.md" ||
    fail "Packet accessibility notes are out of sync."
  cmp -s docs/screenshot_plan.md "$packet/docs/screenshot_plan.md" ||
    fail "Packet screenshot plan is out of sync."
  cmp -s docs/signing_setup.md "$packet/docs/signing_setup.md" ||
    fail "Packet signing setup is out of sync."
  cmp -s docs/release_hygiene.md "$packet/docs/release_hygiene.md" ||
    fail "Packet release hygiene doc is out of sync."
  cmp -s store-assets/app-icon/play-store-icon-512.png "$packet/assets/app-icon/play-store-icon-512.png" ||
    fail "Packet Play Store icon is out of sync."
  cmp -s store-assets/feature-graphic/feature-graphic-candidate-03.png "$packet/assets/feature-graphic/feature-graphic-candidate-03.png" ||
    fail "Packet feature graphic candidate is out of sync."

  local screenshot
  for screenshot in 01-onboarding 02-home 03-timer 04-result 05-progress 06-settings; do
    cmp -s "screenshots/play-store/${screenshot}.png" "$packet/assets/screenshots/${screenshot}.png" ||
      fail "Packet screenshot is out of sync: ${screenshot}.png"
  done

  (
    cd "$packet"
    shasum -a 256 -c checksums.sha256 >/dev/null
  ) || fail "Packet checksums failed."

  pass "Play submission packet exists, is synchronized and passes checksums"
}

printf '== Poryadok 5 RC verification ==\n'

./gradlew clean :app:printReleaseSigningStatus test lint assembleDebug bundleRelease --console=plain
pass "Gradle clean, signing status, tests, lint, debug APK and release AAB"

forbidden_pattern="$(printf '%s|%s|%s|%s|%s' 'TO''DO' 'FIX''ME' 'Lor''em' 'place''holder' 'Hello ''world')"
check_no_matches "Temporary content markers" \
  rg -n "$forbidden_pattern" . --glob '!app/build*/**' --glob '!.gradle/**'

check_no_matches "Android platform permissions in source manifest" \
  rg -n "<uses-permission|android.permission" app/src/main

scripts/check_aab_metadata.py
scripts/check_aab_metadata_selftest.py
scripts/check_aab_universal_apk.py
scripts/check_aab_universal_apk_selftest.py
scripts/check_apk_metadata.py
scripts/check_apk_metadata_selftest.py
scripts/check_apk_permissions.py
scripts/check_apk_permissions_selftest.py
scripts/check_android_backup_policy.py
scripts/check_android_backup_policy_selftest.py
scripts/check_manifest_component_exposure.py
scripts/check_packaged_app_contents.py
scripts/check_packaged_app_contents_selftest.py
scripts/check_native_library_packaging.py
scripts/check_native_library_packaging_selftest.py
scripts/check_dependency_privacy.py
scripts/check_dependency_privacy_selftest.py
scripts/check_stack_versions.py
scripts/check_stack_versions_selftest.py
scripts/check_lifecycle_state_collection.py
scripts/check_lifecycle_state_collection_selftest.py
scripts/check_loading_state_layout.py
scripts/check_loading_state_layout_selftest.py
scripts/check_progress_persistence_normalization.py
scripts/check_progress_persistence_normalization_selftest.py
scripts/check_settings_enum_normalization.py
scripts/check_settings_enum_normalization_selftest.py
scripts/check_task_filter_minutes_normalization.py
scripts/check_task_filter_minutes_normalization_selftest.py
scripts/release_identity_selftest.py
scripts/check_task_catalog_quality.py
scripts/check_task_catalog_quality_selftest.py
scripts/check_engine_completed_id_normalization.py
scripts/check_engine_completed_id_normalization_selftest.py
scripts/check_runtime_catalog_count.py
scripts/check_runtime_catalog_count_selftest.py
scripts/check_screen_state_saveability.py
scripts/check_screen_state_saveability_selftest.py
scripts/check_task_repository_parser.py
scripts/check_task_repository_parser_selftest.py
scripts/check_startup_error_retry.py
scripts/check_startup_error_retry_selftest.py
scripts/check_packaged_task_catalog.py
scripts/check_packaged_task_catalog_selftest.py
scripts/check_store_listing.py
scripts/check_store_listing_selftest.py
scripts/check_play_store_icon.py
scripts/check_play_store_icon_selftest.py
scripts/check_store_asset_pixels.py
scripts/check_store_asset_pixels_selftest.py
scripts/check_play_console_forms.py
scripts/check_play_console_forms_selftest.py
scripts/check_policy_content_risk.py
scripts/check_policy_content_risk_selftest.py
scripts/check_qa_evidence.py
scripts/check_qa_evidence_selftest.py
scripts/check_doc_inventory.py
scripts/check_doc_inventory_selftest.py
scripts/check_accessibility_targets.py
scripts/check_accessibility_targets_selftest.py
scripts/check_header_icon_vectors.py
scripts/check_header_icon_vectors_selftest.py
scripts/check_onboarding_copy_alignment.py
scripts/check_onboarding_copy_alignment_selftest.py
scripts/check_home_filter_disclosure.py
scripts/check_home_filter_disclosure_selftest.py
scripts/check_home_action_icons.py
scripts/check_home_action_icons_selftest.py
scripts/check_main_flow_action_icons.py
scripts/check_main_flow_action_icons_selftest.py
scripts/check_task_result_preview.py
scripts/check_task_result_preview_selftest.py
scripts/check_home_skip_exhausted_hint.py
scripts/check_home_skip_exhausted_hint_selftest.py
scripts/check_task_details_briefing.py
scripts/check_task_details_briefing_selftest.py
scripts/check_task_details_start_dock.py
scripts/check_task_details_start_dock_selftest.py
scripts/check_timer_session_goal.py
scripts/check_timer_session_goal_selftest.py
scripts/check_timer_outcome_preview.py
scripts/check_timer_outcome_preview_selftest.py
scripts/check_timer_completion_dock.py
scripts/check_timer_completion_dock_selftest.py
scripts/check_progress_line_component.py
scripts/check_progress_line_component_selftest.py
scripts/check_progress_focus_summary.py
scripts/check_progress_focus_summary_selftest.py
scripts/check_progress_rhythm_summary.py
scripts/check_progress_rhythm_summary_selftest.py
scripts/check_ui_label_consistency.py
scripts/check_ui_label_consistency_selftest.py
scripts/check_result_next_details.py
scripts/check_result_next_details_selftest.py
scripts/check_result_action_layout.py
scripts/check_result_action_layout_selftest.py
scripts/check_result_content_focus.py
scripts/check_result_content_focus_selftest.py
scripts/check_progress_continue_action.py
scripts/check_progress_continue_action_selftest.py
scripts/check_settings_danger_action.py
scripts/check_settings_danger_action_selftest.py
scripts/check_settings_reset_cancel.py
scripts/check_settings_reset_cancel_selftest.py
scripts/check_settings_privacy_summary.py
scripts/check_settings_privacy_summary_selftest.py
scripts/check_settings_about_summary.py
scripts/check_settings_about_summary_selftest.py
scripts/check_privacy_policy_html.py
scripts/check_privacy_policy_html_selftest.py
scripts/check_privacy_policy_rendering_selftest.py
scripts/check_publishable_privacy_policy_selftest.py
scripts/check_publishable_privacy_policy_cli_selftest.py
scripts/check_play_submission_publishable_policy_packet.py
scripts/check_play_submission_publishable_policy_packet_selftest.py
scripts/check_play_upload_external_inputs_selftest.py
scripts/check_play_upload_readiness_selftest.py
scripts/check_play_upload_blockers_selftest.py
scripts/check_release_artifact_manifest_checker_selftest.py
scripts/check_release_artifact_manifest_selftest.py
scripts/check_play_submission_packet_contents_selftest.py
scripts/check_play_submission_packet_sync_selftest.py
scripts/check_play_submission_doc_coverage_selftest.py
scripts/check_release_hygiene.py
scripts/check_release_hygiene_selftest.py
scripts/check_release_signing_inputs_selftest.py
scripts/check_manifest_component_exposure_selftest.py
scripts/check_play_upload_candidate_handoff_selftest.py
scripts/check_play_upload_candidate_handoff.py
scripts/check_prepare_play_upload_candidate_negative_path.py
scripts/check_prepare_play_upload_candidate_external_inputs_negative_path.py
scripts/smoke_test_release_signing_pipeline.sh
scripts/check_release_signing_inputs.py

scripts/build_play_submission_packet.sh
pass "Play submission packet refreshed after clean build"
scripts/check_publishable_privacy_policy.py
scripts/check_rc_traceability.py
scripts/check_rc_traceability_selftest.py
scripts/check_release_artifact_manifest.py
scripts/check_play_upload_blockers.py
scripts/check_play_submission_packet_contents.py
scripts/check_play_submission_packet_sync.py
scripts/check_play_submission_doc_coverage.py

scripts/check_play_upload_readiness.py
scripts/check_visible_text_ru.py
scripts/check_visible_text_ru_selftest.py

validate_screenshots
validate_feature_graphic_candidate
validate_submission_packet

aab="app/build/outputs/bundle/release/app-release.aab"
apk="app/build/outputs/apk/debug/app-debug.apk"
[[ -f "$aab" ]] || fail "Missing release AAB: $aab"
[[ -f "$apk" ]] || fail "Missing debug APK: $apk"
pass "Build artifacts exist"

sdk="$(find_android_sdk)"
zipalign_bin="$(find_zipalign "$sdk")"
"$zipalign_bin" -c -P 16 -v 4 "$aab" >/dev/null
pass "Release AAB passes 16 KB zip alignment check"

jarsigner_bin="$(find_jarsigner)"
signing_output="$("$jarsigner_bin" -verify -verbose -certs "$aab" 2>&1 || true)"

if printf '%s\n' "$signing_output" | rg -q "jar verified" &&
  ! printf '%s\n' "$signing_output" | rg -q "jar is unsigned"; then
  pass "Release AAB signature verified"
else
  if printf '%s\n' "$signing_output" | rg -q "jar is unsigned"; then
    note "Release AAB is unsigned because release signing inputs are not configured."
  else
    printf '%s\n' "$signing_output"
    fail "Unexpected jarsigner output for unsigned local RC."
  fi
fi

printf '== RC verification finished ==\n'
