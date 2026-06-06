# QA Evidence Audit

## Status

`LOCAL_PROVEN`.

## Purpose

This audit records the local gate that verifies emulator QA evidence, not only the markdown summaries. The checked evidence covers Android 15 and Android 16 flows, offline behavior, timer background/resume, timer double-submit protection, Timer session goal visibility, Timer outcome preview, Timer completion dock reachability, Timer control icons, onboarding copy alignment, onboarding flow summary, Home stats icon clarity, Home filter disclosure, Home filter whole-row disclosure, Home filter chevron disclosure, Home filter unframed summary, Home result preview, Home action icons, main-flow CTA icons, Task status pill affordance, Task details briefing, Task details unframed briefing with compact `После` preview, Result action layout, Result details-first primary navigation, Result content focus with next-task outcome preview, Result peer icons, ProgressLine visuals, Progress rhythm summary, Progress rhythm unframed layout, Progress continue navigation, Settings privacy summary badges, Settings privacy unframed facts with compact explanations, Settings about summary facts, Settings safety flows, compact viewport, large viewport and large font scale.

## Automated Gate

`scripts/check_qa_evidence.py` validates:

- 38 emulator QA reports under `docs/`.
- 38 matching evidence directories under `qa/`.
- Required UI XML and PNG pairs for each documented flow.
- Key UI markers such as `Готово`, `Цель: 5 мин`, `1 дн.`, `1%`, `1 из 80`, `Пауза`, `Продолжить`, `Продолжить с задачей`, `Настройки`, `Отмена` and `Сбросить прогресс`.
- Gradle `applicationId` package markers in UI XML, focus evidence and app-specific crash checks.
- Offline proof `Active default network: none`.
- Timer proof points `2:58`, `2:28`, `2:09` and `2:05`.
- App-specific crash/error gates that must remain empty.
- Documented system crash caveats such as compact-screen system state and Android 15 Bluetooth service crashes as unrelated to `ru.poryadok5.app`.

`scripts/check_qa_evidence_selftest.py` verifies the gate itself with temporary QA fixtures for Gradle identity package marker drift, missing reports/directories, invalid PNG signatures, UI XML without the app package marker, missing snippet markers, non-empty zero-match logs and crash-log allowlist behavior.

Current local result:

```text
PASS: QA evidence covers 38 emulator reports, 173 UI XML/PNG pairs and 63 zero-match log gates
```

## Covered Reports

| Report | Evidence | Coverage |
|---|---|---|
| `docs/emulator_timer_background_qa.md` | `qa/emulator-android15-timer-background` | Android 15 timer background/resume, pause stability and completion |
| `docs/emulator_android15_timer_double_submit_qa.md` | `qa/emulator-android15-timer-double-submit` | Android 15 rapid double-submit guard and unique completion count |
| `docs/emulator_no_internet_qa.md` | `qa/emulator-android15-no-internet` | Android 15 no-internet onboarding, home, timer and result flow |
| `docs/emulator_android15_compose_bom_smoke_qa.md` | `qa/emulator-android15-compose-bom-smoke` | Android 15 post-Compose-BOM smoke flow with AVD caveat evidence |
| `docs/emulator_android15_settings_haptics_row_qa_2026_06_03.md` | `qa/emulator-android15-settings-haptics-row-qa-2026-06-03` | Android 15 Settings haptics row full-target toggle behavior |
| `docs/emulator_android15_settings_reset_cancel_qa_2026_06_03.md` | `qa/emulator-android15-settings-reset-cancel-qa-2026-06-03` | Android 15 Settings reset confirmation, cancel path and success notice |
| `docs/emulator_android15_progress_continue_qa_2026_06_04.md` | `qa/emulator-android15-progress-continue-qa-2026-06-04` | Android 15 Progress “Продолжить с задачей” action and Home return |
| `docs/emulator_android15_result_action_layout_qa_2026_06_05.md` | `qa/emulator-android15-result-action-layout-qa-2026-06-05` | Android 15 Result compact peer action row and refreshed Result Play screenshot |
| `docs/emulator_android15_progress_line_qa_2026_06_05.md` | `qa/emulator-android15-progress-line-qa-2026-06-05` | Android 15 ProgressLine visual QA and refreshed Timer/Progress Play screenshots |
| `docs/emulator_android15_progress_rhythm_summary_qa_2026_06_06.md` | `qa/emulator-android15-progress-rhythm-summary-qa-2026-06-06` | Android 15 Progress rhythm summary QA and refreshed Progress Play screenshot |
| `docs/emulator_android16_progress_rhythm_unframed_qa_2026_06_06.md` | `qa/emulator-android16-progress-rhythm-unframed-qa-2026-06-06` | Android 16 Progress rhythm unframed layout QA and refreshed Progress Play screenshot |
| `docs/emulator_android15_onboarding_copy_qa_2026_06_06.md` | `qa/emulator-android15-onboarding-copy-qa-2026-06-06` | Android 15 onboarding copy alignment and refreshed Onboarding Play screenshot |
| `docs/emulator_android15_onboarding_flow_summary_qa_2026_06_06.md` | `qa/emulator-android15-onboarding-flow-summary-qa-2026-06-06` | Android 15 unframed onboarding flow summary QA and refreshed Onboarding Play screenshot |
| `docs/emulator_android16_home_filter_disclosure_qa_2026_06_06.md` | `qa/emulator-android16-home-filter-disclosure-qa-2026-06-06` | Android 16 collapsed Home filter disclosure QA and refreshed Home Play screenshot |
| `docs/emulator_android15_home_filter_whole_row_qa_2026_06_06.md` | `qa/emulator-android15-home-filter-whole-row-qa-2026-06-06` | Android 15 Home filter whole-row disclosure QA and refreshed Home Play screenshot |
| `docs/emulator_android15_home_filter_chevron_qa_2026_06_06.md` | `qa/emulator-android15-home-filter-chevron-qa-2026-06-06` | Android 15 Home filter chevron disclosure QA and refreshed Home Play screenshot |
| `docs/emulator_android16_home_filter_unframed_summary_qa_2026_06_06.md` | `qa/emulator-android16-home-filter-unframed-summary-qa-2026-06-06` | Android 16 Home filter unframed summary QA and refreshed Home Play screenshot |
| `docs/emulator_android15_home_stats_icon_qa_2026_06_06.md` | `qa/emulator-android15-home-stats-icon-qa-2026-06-06` | Android 15 Home `StatsIcon` header QA and refreshed Home Play screenshot |
| `docs/emulator_android15_home_result_preview_qa_2026_06_06.md` | `qa/emulator-android15-home-result-preview-qa-2026-06-06` | Android 15 Home result preview QA and refreshed Home Play screenshot |
| `docs/emulator_android15_home_action_icons_qa_2026_06_06.md` | `qa/emulator-android15-home-action-icons-qa-2026-06-06` | Android 15 Home action icons QA and refreshed Home Play screenshot |
| `docs/emulator_android15_main_flow_action_icons_qa_2026_06_06.md` | `qa/emulator-android15-main-flow-action-icons-qa-2026-06-06` | Android 15 main-flow CTA icons QA and refreshed Onboarding/Home/Timer/Result/Progress Play screenshots |
| `docs/emulator_android15_result_details_first_qa_2026_06_06.md` | `qa/emulator-android15-result-details-first-qa-2026-06-06` | Android 15 Result details-first primary QA and refreshed Result Play screenshot |
| `docs/emulator_android16_result_content_focus_qa_2026_06_06.md` | `qa/emulator-android16-result-content-focus-qa-2026-06-06` | Android 16 Result content-focus, next-task outcome preview QA and refreshed Result Play screenshot |
| `docs/emulator_android16_result_peer_icons_qa_2026_06_06.md` | `qa/emulator-android16-result-peer-icons-qa-2026-06-06` | Android 16 Result peer-action icons QA and refreshed Result Play screenshot |
| `docs/emulator_android15_settings_privacy_summary_qa_2026_06_06.md` | `qa/emulator-android15-settings-privacy-summary-qa-2026-06-06` | Android 15 Settings privacy summary badges QA and refreshed Settings Play screenshot |
| `docs/emulator_android16_settings_privacy_unframed_qa_2026_06_06.md` | `qa/emulator-android16-settings-privacy-unframed-qa-2026-06-06` | Android 16 Settings privacy unframed facts with compact explanations QA and refreshed Settings Play screenshot |
| `docs/emulator_android16_settings_about_summary_qa_2026_06_06.md` | `qa/emulator-android16-settings-about-summary-qa-2026-06-06` | Android 16 Settings about-summary facts QA and refreshed Settings Play screenshot |
| `docs/emulator_android15_task_status_pill_qa_2026_06_06.md` | `qa/emulator-android15-task-status-pill-qa-2026-06-06` | Android 15 Task status pill affordance QA and refreshed Home/Result Play screenshots |
| `docs/emulator_android16_task_details_briefing_qa_2026_06_06.md` | `qa/emulator-android16-task-details-briefing-qa-2026-06-06` | Android 16 Task details briefing QA and Details-to-Timer flow evidence |
| `docs/emulator_android15_task_details_unframed_qa_2026_06_06.md` | `qa/emulator-android15-task-details-unframed-qa-2026-06-06` | Android 15 Task details unframed briefing, compact outcome preview and Details-to-Timer flow evidence |
| `docs/emulator_android15_timer_completion_dock_qa_2026_06_06.md` | `qa/emulator-android15-timer-completion-dock-qa-2026-06-06` | Android 15 Timer completion dock QA and refreshed Timer Play screenshot |
| `docs/emulator_android15_timer_session_goal_qa_2026_06_06.md` | `qa/emulator-android15-timer-session-goal-qa-2026-06-06` | Android 15 Timer session goal QA and refreshed Timer Play screenshot |
| `docs/emulator_android15_timer_outcome_preview_qa_2026_06_06.md` | `qa/emulator-android15-timer-outcome-preview-qa-2026-06-06` | Android 15 Timer outcome preview QA and refreshed Timer Play screenshot |
| `docs/emulator_android16_timer_control_icons_qa_2026_06_06.md` | `qa/emulator-android16-timer-control-icons-qa-2026-06-06` | Android 16 Timer control icons QA, running/paused states and refreshed Timer Play screenshot |
| `docs/emulator_android16_smoke_qa.md` | `qa/emulator-android16-smoke` | Android 16 primary flow, Back behavior, settings and restart persistence |
| `docs/emulator_android16_compact_screen_qa.md` | `qa/emulator-android16-compact-screen` | Android 16 compact viewport scroll reachability |
| `docs/emulator_android16_large_screen_qa.md` | `qa/emulator-android16-large-screen` | Android 16 large viewport max-width behavior |
| `docs/emulator_android16_large_font_qa.md` | `qa/emulator-android16-large-font` | Android 16 large font usability |

## Release Impact

This gate strengthens the local RC claim by ensuring that QA summaries stay synchronized with the captured files. It does not replace manual Play Console review, upload signing, hosted privacy policy publication, Data Safety confirmation, content rating confirmation or feature graphic approval.
