#!/usr/bin/env python3
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from release_identity import read_gradle_release_identity

ROOT = Path(__file__).resolve().parents[1]
APP_PACKAGE_TOKEN = "{APP_PACKAGE}"
PACKAGE = APP_PACKAGE_TOKEN
PNG_HEADER = b"\x89PNG\r\n\x1a\n"


@dataclass(frozen=True)
class EvidenceSet:
    name: str
    report: str
    directory: str
    report_snippets: tuple[str, ...]
    pairs: tuple[str, ...]
    files: tuple[str, ...] = ()
    zero_byte_files: tuple[str, ...] = ()
    snippets: tuple[tuple[str, tuple[str, ...]], ...] = ()
    allow_crash_log_packages: tuple[str, ...] = ()


EVIDENCE_SETS: tuple[EvidenceSet, ...] = (
    EvidenceSet(
        name="Android 15 timer background/resume",
        report="docs/emulator_timer_background_qa.md",
        directory="qa/emulator-android15-timer-background",
        report_snippets=(
            "qa/emulator-android15-timer-background",
            "2:58",
            "2:28",
            "2:09",
            "2:05",
            "0 crash log lines",
        ),
        pairs=(
            "02-home",
            "03-timer-start",
            "04-timer-after-background",
            "06-timer-paused-after-wait",
            "07-timer-resumed",
            "08-result",
        ),
        files=("01-onboarding.xml", "05-timer-paused.xml", "timer-background-evidence.txt"),
        zero_byte_files=("crash-logcat.txt",),
        snippets=(
            ("03-timer-start.xml", ("Сложить плед", "2:58", "Пауза", "Готово", PACKAGE)),
            ("04-timer-after-background.xml", ("2:28", "Пауза", PACKAGE)),
            ("05-timer-paused.xml", ("2:09", "Продолжить", PACKAGE)),
            ("06-timer-paused-after-wait.xml", ("2:09", "Продолжить", PACKAGE)),
            ("07-timer-resumed.xml", ("2:05", "Пауза", PACKAGE)),
            ("08-result.xml", ("Готово", "1 дн.", "1%", PACKAGE)),
            ("timer-background-evidence.txt", ("background_start_utc=", "foreground_return_utc=")),
        ),
    ),
    EvidenceSet(
        name="Android 15 no-internet flow",
        report="docs/emulator_no_internet_qa.md",
        directory="qa/emulator-android15-no-internet",
        report_snippets=(
            "qa/emulator-android15-no-internet",
            "Active default network: none",
            "0 crash log lines",
        ),
        pairs=("01-onboarding", "02-home", "03-timer", "04-result"),
        files=("connectivity-disabled.txt", "connectivity-summary-before.txt", "connectivity-summary-after-flow.txt"),
        zero_byte_files=("crash-logcat.txt",),
        snippets=(
            ("connectivity-summary-before.txt", ("Active default network: none",)),
            ("03-timer.xml", ("Сложить плед", "2:58", "Пауза", "Готово", PACKAGE)),
            ("04-result.xml", ("Готово", "1 дн.", "1%", PACKAGE)),
        ),
    ),
    EvidenceSet(
        name="Android 15 Compose BOM smoke",
        report="docs/emulator_android15_compose_bom_smoke_qa.md",
        directory="qa/emulator-android15-compose-bom-smoke",
        report_snippets=(
            "qa/emulator-android15-compose-bom-smoke",
            "PASSED_WITH_AVD_CAVEAT",
            "clean-crash-buffer-after-cleanup.txt",
        ),
        pairs=(
            "01-onboarding",
            "02-home",
            "03-after-launch",
            "04-paused",
            "05-resumed",
            "10-result",
            "12-final-clean",
        ),
        files=(
            "10-result-summary.txt",
            "12-final-clean-summary.txt",
            "13-final-no-crash-relaunch.png",
            "focus-after-completion.txt",
            "focus-final-clean.txt",
            "packages-after-cleanup.txt",
        ),
        zero_byte_files=("clean-crash-buffer-after-cleanup.txt", "final-app-pid-error-matches.txt"),
        snippets=(
            ("03-after-launch-summary.txt", ("Протереть зеркало", "4:58", "Пауза", "Готово")),
            ("04-paused-summary.txt", ("4:30", "Продолжить")),
            ("10-result-summary.txt", ("Готово", "1 дн.", "1%")),
            ("12-final-clean-summary.txt", ("1 дн.", "1%", "Запустить таймер")),
            ("focus-after-completion.txt", (PACKAGE, "MainActivity")),
            ("focus-final-clean.txt", (PACKAGE, "MainActivity")),
            ("packages-after-cleanup.txt", (f"package:{PACKAGE}",)),
        ),
    ),
    EvidenceSet(
        name="Android 15 timer double-submit",
        report="docs/emulator_android15_timer_double_submit_qa.md",
        directory="qa/emulator-android15-timer-double-submit",
        report_snippets=(
            "qa/emulator-android15-timer-double-submit",
            "PASSED_WITH_AVD_CAVEAT",
            "1 из 80",
            "app-pid-error-filtered.txt",
        ),
        pairs=(
            "05-home-clean",
            "06-timer-clean-before",
            "07-result-after-double",
            "08-progress-after-double",
        ),
        files=("04-onboarding-clean.xml", "06-timer-double-complete-taps.txt", "focus-final.txt"),
        zero_byte_files=("app-pid-error-filtered.txt", "crash-buffer.txt"),
        snippets=(
            ("06-timer-clean-before.xml", ("Готово", PACKAGE)),
            ("06-timer-double-complete-taps.txt", ("540 1754",)),
            ("07-result-after-double.xml", ("Готово", "1 дн.", "1%", PACKAGE)),
            ("08-progress-after-double.xml", ("1 из 80", "Итоги", PACKAGE)),
            ("focus-final.txt", (PACKAGE, "MainActivity")),
        ),
    ),
    EvidenceSet(
        name="Android 15 Timer session goal",
        report="docs/emulator_android15_timer_session_goal_qa_2026_06_06.md",
        directory="qa/emulator-android15-timer-session-goal-qa-2026-06-06",
        report_snippets=(
            "qa/emulator-android15-timer-session-goal-qa-2026-06-06",
            "PASSED",
            "Цель: 5 мин",
            "screenshots/play-store/03-timer.png",
        ),
        pairs=("01-onboarding", "02-home", "03-timer"),
        files=(
            "wm-size.txt",
            "wm-density.txt",
            "android-release.txt",
            "android-sdk.txt",
            "resolve-activity.txt",
            "04-focus.txt",
            "08-screenshot-sizes.txt",
            "09-ui-marker-check.txt",
        ),
        zero_byte_files=("07-app-fatal-anr-matches.txt",),
        snippets=(
            ("android-release.txt", ("15",)),
            ("android-sdk.txt", ("35",)),
            ("resolve-activity.txt", (PACKAGE, "MainActivity")),
            ("03-timer.xml", ("Таймер", "Цель: 5 мин", "Пауза", "Сброс", "План", "Готово", PACKAGE)),
            ("04-focus.txt", (PACKAGE, "MainActivity")),
            ("08-screenshot-sizes.txt", ("03-timer.png: 1080x2400 RGBA",)),
            ("09-ui-marker-check.txt", ("PASS", "Цель: 5 мин", "Готово")),
        ),
    ),
    EvidenceSet(
        name="Android 15 Timer outcome preview",
        report="docs/emulator_android15_timer_outcome_preview_qa_2026_06_06.md",
        directory="qa/emulator-android15-timer-outcome-preview-qa-2026-06-06",
        report_snippets=(
            "qa/emulator-android15-timer-outcome-preview-qa-2026-06-06",
            "PASSED",
            "Timer outcome-preview",
            "screenshots/play-store/03-timer.png",
        ),
        pairs=("01-onboarding", "02-home", "03-timer"),
        files=(
            "wm-size.txt",
            "wm-density.txt",
            "android-release.txt",
            "android-sdk.txt",
            "avd-name.txt",
            "resolve-activity.txt",
            "04-focus.txt",
            "08-screenshot-sizes.txt",
        ),
        zero_byte_files=("07-app-fatal-anr-matches.txt",),
        snippets=(
            ("wm-size.txt", ("Physical size: 1080x2400",)),
            ("wm-density.txt", ("Physical density: 420",)),
            ("android-release.txt", ("15",)),
            ("android-sdk.txt", ("35",)),
            ("avd-name.txt", ("Medium_Phone_API_35_Default",)),
            ("resolve-activity.txt", (PACKAGE, "MainActivity")),
            ("01-onboarding.xml", ("Порядок 5", "Начать", PACKAGE)),
            ("02-home.xml", ("Подготовить спокойный угол", "Запустить таймер", "После", PACKAGE)),
            (
                "03-timer.xml",
                (
                    "Таймер",
                    "Подготовить спокойный угол",
                    "Цель: 5 мин",
                    "План",
                    "После",
                    "В комнате появился один аккуратный визуальный якорь.",
                    "Пауза",
                    "Сброс",
                    "Готово",
                    PACKAGE,
                ),
            ),
            ("04-focus.txt", (PACKAGE, "MainActivity")),
            ("08-screenshot-sizes.txt", ("03-timer.png", "pixelWidth: 1080", "pixelHeight: 2400")),
        ),
    ),
    EvidenceSet(
        name="Android 16 smoke",
        report="docs/emulator_android16_smoke_qa.md",
        directory="qa/emulator-android16-smoke",
        report_snippets=(
            "qa/emulator-android16-smoke",
            "Crash buffer contained 0 lines",
            "Force-stop/restart opened Home",
        ),
        pairs=(
            "01-onboarding",
            "02-home",
            "03-home-3min",
            "04-timer-start",
            "05-timer-paused",
            "06-timer-resumed",
            "07-result",
            "08-progress",
            "09-home-after-system-back",
            "10-settings",
            "11-restart-home-persisted",
        ),
        files=("device_api.txt", "device_android_release.txt", "resolve_activity.txt", "wm_size.txt", "wm_density.txt"),
        zero_byte_files=("crash.log",),
        snippets=(
            ("device_api.txt", ("36",)),
            ("device_android_release.txt", ("16",)),
            ("resolve_activity.txt", (PACKAGE, "MainActivity")),
            ("07-result.xml", ("Готово", "1 дн.", "1%", PACKAGE)),
            ("08-progress.xml", ("1 из 80", "Итоги", PACKAGE)),
            ("09-home-after-system-back.xml", ("Порядок 5", PACKAGE)),
            ("10-settings.xml", ("Настройки", PACKAGE)),
            ("11-restart-home-persisted.xml", ("1 дн.", "1%", PACKAGE)),
        ),
    ),
    EvidenceSet(
        name="Android 16 compact screen",
        report="docs/emulator_android16_compact_screen_qa.md",
        directory="qa/emulator-android16-compact-screen",
        report_snippets=(
            "qa/emulator-android16-compact-screen",
            "720x1280",
            "Primary actions",
            "app_logcat_error_matches.txt",
        ),
        pairs=(
            "01-onboarding-top",
            "02-onboarding-find-start-2",
            "03-home-top",
            "06-home-find-start-timer-2",
            "07-timer-top",
            "09-timer-paused",
            "12-timer-find-done-2",
            "13-result-top",
            "15-home-after-result",
            "17-settings-top",
            "19-settings-reset-confirm-visible",
        ),
        files=("compact_wm_size.txt", "compact_wm_density.txt", "restored_wm_size.txt", "restored_wm_density.txt"),
        zero_byte_files=("app_crash_package_matches.txt", "app_logcat_error_matches.txt"),
        snippets=(
            ("compact_wm_size.txt", ("Override size: 720x1280",)),
            ("compact_wm_density.txt", ("Override density: 320",)),
            ("02-onboarding-find-start-2.xml", ("Начать", PACKAGE)),
            ("06-home-find-start-timer-2.xml", ("Запустить таймер", PACKAGE)),
            ("09-timer-paused.xml", ("Продолжить", PACKAGE)),
            ("12-timer-find-done-2.xml", ("Готово", PACKAGE)),
            ("13-result-top.xml", ("Готово", "1 дн.", "1%", PACKAGE)),
            ("19-settings-reset-confirm-visible.xml", ("Сбросить прогресс", PACKAGE)),
        ),
        allow_crash_log_packages=("com.google.android.dialer",),
    ),
    EvidenceSet(
        name="Android 16 large screen",
        report="docs/emulator_android16_large_screen_qa.md",
        directory="qa/emulator-android16-large-screen",
        report_snippets=(
            "qa/emulator-android16-large-screen",
            "2000x2560",
            "max-width",
            "app_logcat_error_matches.txt",
        ),
        pairs=("01-onboarding", "02-home", "03-home-3min", "04-timer", "05-result", "06-home-after-result", "07-settings"),
        files=("large_wm_size.txt", "large_wm_density.txt", "restored_wm_size.txt", "restored_wm_density.txt"),
        zero_byte_files=("crash.log", "app_crash_package_matches.txt", "app_logcat_error_matches.txt"),
        snippets=(
            ("large_wm_size.txt", ("Override size: 2000x2560",)),
            ("large_wm_density.txt", ("Override density: 320",)),
            ("04-timer.xml", ("Готово", PACKAGE)),
            ("05-result.xml", ("Готово", "1 дн.", "1%", PACKAGE)),
            ("06-home-after-result.xml", ("Порядок 5", PACKAGE)),
            ("07-settings.xml", ("Настройки", PACKAGE)),
        ),
    ),
    EvidenceSet(
        name="Android 16 large font",
        report="docs/emulator_android16_large_font_qa.md",
        directory="qa/emulator-android16-large-font",
        report_snippets=(
            "qa/emulator-android16-large-font",
            "font_scale=1.3",
            "Primary actions",
            "app_logcat_error_matches.txt",
        ),
        pairs=(
            "01-onboarding-top",
            "03-home-top",
            "06-home-find-start-timer-1",
            "07-timer-top",
            "09-timer-paused",
            "12-timer-find-done-1",
            "13-result-top",
            "15-progress-top",
            "16-home-after-back",
            "18-settings-top",
            "20-settings-reset-confirm-visible",
        ),
        files=("baseline_font_scale.txt", "test_font_scale.txt", "restored_font_scale.txt"),
        zero_byte_files=("crash.log", "app_crash_package_matches.txt", "app_logcat_error_matches.txt"),
        snippets=(
            ("test_font_scale.txt", ("1.3",)),
            ("09-timer-paused.xml", ("Продолжить", PACKAGE)),
            ("13-result-top.xml", ("Готово", "1 дн.", "1%", PACKAGE)),
            ("15-progress-top.xml", ("1 из 80", "Итоги", PACKAGE)),
            ("20-settings-reset-confirm-visible.xml", ("Сбросить прогресс", PACKAGE)),
        ),
    ),
    EvidenceSet(
        name="Android 15 progress continue action",
        report="docs/emulator_android15_progress_continue_qa_2026_06_04.md",
        directory="qa/emulator-android15-progress-continue-qa-2026-06-04",
        report_snippets=(
            "qa/emulator-android15-progress-continue-qa-2026-06-04",
            "Продолжить с задачей",
            "1 из 80",
            "09-app-fatal-anr-matches.txt",
        ),
        pairs=(
            "01-onboarding",
            "02-home",
            "03-timer",
            "04-result",
            "05-progress",
            "06-home-after-continue",
        ),
        files=(
            "04-result-scrolled.xml",
            "05-progress-summary.txt",
            "06-home-after-continue-summary.txt",
            "07-focus.txt",
            "08-logcat.txt",
        ),
        zero_byte_files=("08-crash-buffer.txt", "09-app-fatal-anr-matches.txt"),
        snippets=(
            ("04-result-scrolled.xml", ("Посмотреть итоги", PACKAGE)),
            ("05-progress.xml", ("Итоги", "1 из 80", "Продолжить с задачей", PACKAGE)),
            ("06-home-after-continue.xml", ("Порядок 5", "Запустить таймер", "1 дн.", PACKAGE)),
            ("07-focus.txt", (PACKAGE, "MainActivity")),
        ),
    ),
    EvidenceSet(
        name="Android 15 result action layout",
        report="docs/emulator_android15_result_action_layout_qa_2026_06_05.md",
        directory="qa/emulator-android15-result-action-layout-qa-2026-06-05",
        report_snippets=(
            "qa/emulator-android15-result-action-layout-qa-2026-06-05",
            "На главный экран",
            "Посмотреть итоги",
            "08-app-fatal-anr-matches.txt",
        ),
        pairs=("01-onboarding", "02-home", "03-timer", "04-result"),
        files=(
            "04-result-summary.txt",
            "05-focus.txt",
            "06-logcat.txt",
            "wm-size.txt",
            "wm-density.txt",
            "android-release.txt",
        ),
        zero_byte_files=("07-crash-buffer.txt", "08-app-fatal-anr-matches.txt"),
        snippets=(
            ("wm-size.txt", ("Physical size: 1080x2400",)),
            ("wm-density.txt", ("Physical density: 420",)),
            ("android-release.txt", ("15",)),
            ("04-result.xml", ("Готово", "Запустить следующую", "На главный экран", "Посмотреть итоги", PACKAGE)),
            ("04-result-summary.txt", ("bounds=[53,2136][527,2273]", "bounds=[553,2136][1027,2273]")),
            ("05-focus.txt", (PACKAGE, "MainActivity")),
        ),
    ),
    EvidenceSet(
        name="Android 15 ProgressLine visuals",
        report="docs/emulator_android15_progress_line_qa_2026_06_05.md",
        directory="qa/emulator-android15-progress-line-qa-2026-06-05",
        report_snippets=(
            "qa/emulator-android15-progress-line-qa-2026-06-05",
            "ProgressLine",
            "false end-dot",
            "09-app-fatal-anr-matches.txt",
        ),
        pairs=("01-onboarding", "02-home", "03-timer", "04-result", "05-progress"),
        files=(
            "03-timer-summary.txt",
            "05-progress-summary.txt",
            "06-focus.txt",
            "07-logcat.txt",
            "wm-size.txt",
            "wm-density.txt",
            "android-release.txt",
            "resolve-activity.txt",
        ),
        zero_byte_files=("08-crash-buffer.txt", "09-app-fatal-anr-matches.txt"),
        snippets=(
            ("wm-size.txt", ("Physical size: 1080x2400",)),
            ("wm-density.txt", ("Physical density: 420",)),
            ("android-release.txt", ("15",)),
            ("resolve-activity.txt", (PACKAGE, "MainActivity")),
            ("03-timer.xml", ("Таймер", "Пауза", "Сброс", "Готово", PACKAGE)),
            ("05-progress.xml", ("Итоги", "1 из 80", "0 из 16", "Продолжить с задачей", PACKAGE)),
            ("06-focus.txt", (PACKAGE, "MainActivity")),
        ),
    ),
    EvidenceSet(
        name="Android 15 Progress rhythm summary",
        report="docs/emulator_android15_progress_rhythm_summary_qa_2026_06_06.md",
        directory="qa/emulator-android15-progress-rhythm-summary-qa-2026-06-06",
        report_snippets=(
            "qa/emulator-android15-progress-rhythm-summary-qa-2026-06-06",
            "Progress rhythm summary",
            "Серия",
            "Счётчик",
            "09-app-fatal-anr-matches.txt",
        ),
        pairs=("01-onboarding", "02-home", "03-timer", "04-result", "05-progress"),
        files=(
            "01-onboarding-summary.txt",
            "02-home-summary.txt",
            "03-timer-summary.txt",
            "04-result-summary.txt",
            "05-progress-summary.txt",
            "06-focus.txt",
            "07-logcat.txt",
            "10-screenshot-sizes.txt",
            "wm-size.txt",
            "wm-density.txt",
            "android-release.txt",
            "android-sdk.txt",
            "resolve-activity.txt",
        ),
        zero_byte_files=("08-crash-buffer.txt", "09-app-fatal-anr-matches.txt"),
        snippets=(
            ("wm-size.txt", ("Physical size: 1080x2400",)),
            ("wm-density.txt", ("Physical density: 420",)),
            ("android-release.txt", ("15",)),
            ("android-sdk.txt", ("35",)),
            ("resolve-activity.txt", (PACKAGE, "MainActivity")),
            ("01-onboarding.xml", ("Порядок 5", "Начать", PACKAGE)),
            ("02-home.xml", ("Порядок 5", "Запустить таймер", PACKAGE)),
            ("03-timer.xml", ("Таймер", "Готово", PACKAGE)),
            ("04-result.xml", ("Готово", "Посмотреть итоги", PACKAGE)),
            (
                "05-progress.xml",
                ("Итоги", "Ритм", "Серия", "1 раз в день", "Счётчик", "каждая задача", "Продолжить с задачей", PACKAGE),
            ),
            (
                "05-progress-summary.txt",
                ("TextView text=\"Серия\"", "TextView text=\"Счётчик\"", "Продолжить с задачей"),
            ),
            ("06-focus.txt", (PACKAGE, "MainActivity")),
            ("10-screenshot-sizes.txt", ("screenshots/play-store/05-progress.png", "pixelWidth: 1080", "pixelHeight: 2400")),
        ),
    ),
    EvidenceSet(
        name="Android 16 Progress rhythm unframed",
        report="docs/emulator_android16_progress_rhythm_unframed_qa_2026_06_06.md",
        directory="qa/emulator-android16-progress-rhythm-unframed-qa-2026-06-06",
        report_snippets=(
            "qa/emulator-android16-progress-rhythm-unframed-qa-2026-06-06",
            "PASSED",
            "unframed",
            "screenshots/play-store/05-progress.png",
        ),
        pairs=("01-onboarding", "02-home", "03-timer", "04-result", "05-progress"),
        files=(
            "wm-size.txt",
            "wm-density.txt",
            "android-release.txt",
            "android-sdk.txt",
            "resolve-activity.txt",
            "06-focus.txt",
            "10-screenshot-sizes.txt",
            "11-ui-marker-check.txt",
        ),
        zero_byte_files=("09-app-fatal-anr-matches.txt",),
        snippets=(
            ("wm-size.txt", ("Physical size: 1080x2400",)),
            ("wm-density.txt", ("Physical density: 420",)),
            ("android-release.txt", ("16",)),
            ("android-sdk.txt", ("36",)),
            ("resolve-activity.txt", (PACKAGE, "MainActivity")),
            ("01-onboarding.xml", ("Порядок 5", "Начать", PACKAGE)),
            ("02-home.xml", ("Порядок 5", "Запустить таймер", PACKAGE)),
            ("03-timer.xml", ("Таймер", "Цель: 5 мин", "Готово", PACKAGE)),
            ("04-result.xml", ("Готово", "Посмотреть итоги", PACKAGE)),
            (
                "05-progress.xml",
                ("Итоги", "Ритм", "Серия", "1 раз в день", "Счётчик", "каждая задача", "Продолжить с задачей", PACKAGE),
            ),
            ("06-focus.txt", (PACKAGE, "MainActivity")),
            ("10-screenshot-sizes.txt", ("05-progress.png: 1080x2400 RGBA",)),
            ("11-ui-marker-check.txt", ("PASS", "Ритм", "каждая задача")),
        ),
    ),
    EvidenceSet(
        name="Android 15 onboarding copy alignment",
        report="docs/emulator_android15_onboarding_copy_qa_2026_06_06.md",
        directory="qa/emulator-android15-onboarding-copy-qa-2026-06-06",
        report_snippets=(
            "qa/emulator-android15-onboarding-copy-qa-2026-06-06",
            "Выбираете стартовую зону.",
            "no longer promises energy selection",
            "05-app-fatal-anr-matches.txt",
        ),
        pairs=("01-onboarding",),
        files=(
            "01-onboarding-summary.txt",
            "02-focus.txt",
            "03-logcat.txt",
            "06-screenshot-size.txt",
            "wm-size.txt",
            "wm-density.txt",
            "android-release.txt",
            "resolve-activity.txt",
        ),
        zero_byte_files=("04-crash-buffer.txt", "05-app-fatal-anr-matches.txt"),
        snippets=(
            ("wm-size.txt", ("Physical size: 1080x2400",)),
            ("wm-density.txt", ("Physical density: 420",)),
            ("android-release.txt", ("15",)),
            ("resolve-activity.txt", (PACKAGE, "MainActivity")),
            ("01-onboarding.xml", ("Порядок 5", "Выбираете стартовую зону.", "Получаете задачу", "Начать", PACKAGE)),
            ("01-onboarding-summary.txt", ("Выбираете стартовую зону.", "Получаете задачу", "Начать")),
            ("02-focus.txt", (PACKAGE, "MainActivity")),
            ("06-screenshot-size.txt", ("pixelWidth: 1080", "pixelHeight: 2400")),
        ),
    ),
    EvidenceSet(
        name="Android 15 onboarding flow summary",
        report="docs/emulator_android15_onboarding_flow_summary_qa_2026_06_06.md",
        directory="qa/emulator-android15-onboarding-flow-summary-qa-2026-06-06",
        report_snippets=(
            "qa/emulator-android15-onboarding-flow-summary-qa-2026-06-06",
            "Первые 5 минут",
            "Как это работает",
            "screenshots/play-store/01-onboarding.png",
        ),
        pairs=("01-onboarding",),
        files=(
            "01-onboarding-summary.txt",
            "02-focus.txt",
            "03-logcat.txt",
            "06-screenshot-size.txt",
            "07-ui-marker-check.txt",
            "wm-size.txt",
            "wm-density.txt",
            "android-release.txt",
            "android-sdk.txt",
            "resolve-activity.txt",
        ),
        zero_byte_files=("04-crash-buffer.txt", "05-app-fatal-anr-matches.txt"),
        snippets=(
            ("wm-size.txt", ("Physical size: 1080x2400",)),
            ("wm-density.txt", ("Physical density: 420",)),
            ("android-release.txt", ("15",)),
            ("android-sdk.txt", ("35",)),
            ("resolve-activity.txt", (PACKAGE, "MainActivity")),
            (
                "01-onboarding.xml",
                (
                    "Порядок 5",
                    "Первые 5 минут",
                    "Сначала",
                    "Выбираете стартовую зону.",
                    "Затем",
                    "Получаете задачу",
                    "После",
                    "Запускаете таймер",
                    "Начать",
                    PACKAGE,
                ),
            ),
            ("01-onboarding-summary.txt", ("Первые 5 минут", "Сначала", "Затем", "После", "Начать")),
            ("02-focus.txt", (PACKAGE, "MainActivity")),
            ("06-screenshot-size.txt", ("pixelWidth: 1080", "pixelHeight: 2400")),
            ("07-ui-marker-check.txt", ("PASS onboarding flow summary markers",)),
        ),
    ),
    EvidenceSet(
        name="Android 16 Home filter disclosure",
        report="docs/emulator_android16_home_filter_disclosure_qa_2026_06_06.md",
        directory="qa/emulator-android16-home-filter-disclosure-qa-2026-06-06",
        report_snippets=(
            "qa/emulator-android16-home-filter-disclosure-qa-2026-06-06",
            "collapsed Home filter disclosure",
            "screenshots/play-store/02-home.png",
            "07-app-fatal-anr-matches.txt",
        ),
        pairs=("01-onboarding", "02-home-collapsed", "03-home-expanded", "03b-home-expanded-lower"),
        files=(
            "04-focus.txt",
            "05-logcat.txt",
            "08-screenshot-sizes.txt",
            "wm-size.txt",
            "wm-density.txt",
            "android-release.txt",
            "android-sdk.txt",
            "resolve-activity.txt",
        ),
        zero_byte_files=("06-crash-buffer.txt", "07-app-fatal-anr-matches.txt"),
        snippets=(
            ("wm-size.txt", ("Physical size: 1080x2400",)),
            ("wm-density.txt", ("Physical density: 420",)),
            ("android-release.txt", ("16",)),
            ("android-sdk.txt", ("36",)),
            ("resolve-activity.txt", (PACKAGE, "MainActivity")),
            ("01-onboarding.xml", ("Порядок 5", "Начать", PACKAGE)),
            (
                "02-home-collapsed.xml",
                ("Настроить подбор", "Изменить", "Запустить таймер", "Другая задача", PACKAGE),
            ),
            ("03-home-expanded.xml", ("Настроить подбор", "Скрыть", "Зона", "Работа", "Цифра", PACKAGE)),
            (
                "03b-home-expanded-lower.xml",
                ("Энергия", "Лёгкая", "Средняя", "Бодрая", "Время", "3 мин", "10 мин", PACKAGE),
            ),
            ("04-focus.txt", (PACKAGE, "MainActivity")),
            ("08-screenshot-sizes.txt", ("screenshots/play-store/02-home.png", "pixelWidth: 1080", "pixelHeight: 2400")),
        ),
    ),
    EvidenceSet(
        name="Android 15 Home filter whole-row disclosure",
        report="docs/emulator_android15_home_filter_whole_row_qa_2026_06_06.md",
        directory="qa/emulator-android15-home-filter-whole-row-qa-2026-06-06",
        report_snippets=(
            "qa/emulator-android15-home-filter-whole-row-qa-2026-06-06",
            "whole-row 56dp",
            "Настроить подбор",
            "screenshots/play-store/02-home.png",
        ),
        pairs=("01-onboarding", "02-home-collapsed", "03-home-expanded-by-summary", "04-home-expanded-lower"),
        files=(
            "01-start-tap.txt",
            "02-summary-row-tap.txt",
            "02-home-collapsed-summary.txt",
            "03-home-expanded-by-summary-summary.txt",
            "04-home-expanded-lower-summary.txt",
            "05-focus.txt",
            "06-logcat.txt",
            "09-screenshot-sizes.txt",
            "10-ui-marker-check.txt",
            "wm-size.txt",
            "wm-density.txt",
            "android-release.txt",
            "android-sdk.txt",
            "resolve-activity.txt",
        ),
        zero_byte_files=("07-crash-buffer.txt", "08-app-fatal-anr-matches.txt"),
        snippets=(
            ("wm-size.txt", ("Physical size: 1080x2400",)),
            ("wm-density.txt", ("Physical density: 420",)),
            ("android-release.txt", ("15",)),
            ("android-sdk.txt", ("35",)),
            ("resolve-activity.txt", (PACKAGE, "MainActivity")),
            (
                "02-home-collapsed.xml",
                ("Настроить подбор", "Изменить", "Запустить таймер", "Другая задача", PACKAGE),
            ),
            (
                "03-home-expanded-by-summary.xml",
                ("Настроить подбор", "Скрыть", "Зона", "Работа", "Цифра", PACKAGE),
            ),
            (
                "04-home-expanded-lower.xml",
                ("Энергия", "Лёгкая", "Средняя", "Бодрая", "Время", "3 мин", "5 мин", "10 мин", PACKAGE),
            ),
            ("05-focus.txt", (PACKAGE, "MainActivity")),
            (
                "09-screenshot-sizes.txt",
                ("02-home-collapsed.png", "03-home-expanded-by-summary.png", "pixelWidth: 1080", "pixelHeight: 2400"),
            ),
            ("10-ui-marker-check.txt", ("PASS whole-row filter disclosure markers",)),
        ),
    ),
    EvidenceSet(
        name="Android 15 Home filter chevron disclosure",
        report="docs/emulator_android15_home_filter_chevron_qa_2026_06_06.md",
        directory="qa/emulator-android15-home-filter-chevron-qa-2026-06-06",
        report_snippets=(
            "qa/emulator-android15-home-filter-chevron-qa-2026-06-06",
            "chevron indicator",
            "whole-row 56dp",
            "screenshots/play-store/02-home.png",
        ),
        pairs=("01-onboarding", "02-home-collapsed", "03-home-expanded-by-summary"),
        files=(
            "06-focus.txt",
            "09-screenshot-sizes.txt",
            "10-ui-marker-check.txt",
            "wm-size.txt",
            "wm-density.txt",
            "android-release.txt",
            "android-sdk.txt",
            "resolve-activity.txt",
        ),
        zero_byte_files=("07-crash-buffer.txt", "08-app-fatal-anr-matches.txt"),
        snippets=(
            ("wm-size.txt", ("Physical size: 1080x2400",)),
            ("wm-density.txt", ("Physical density: 420",)),
            ("android-release.txt", ("15",)),
            ("android-sdk.txt", ("35",)),
            ("resolve-activity.txt", (PACKAGE, "MainActivity")),
            ("01-onboarding.xml", ("Порядок 5", "С чего начнём?", "Начать", PACKAGE)),
            (
                "02-home-collapsed.xml",
                ("Настроить подбор", "Изменить", "Запустить таймер", "Другая задача", PACKAGE),
            ),
            (
                "03-home-expanded-by-summary.xml",
                ("Настроить подбор", "Скрыть", "Зона", "Работа", "Цифра", PACKAGE),
            ),
            ("06-focus.txt", (PACKAGE, "MainActivity")),
            (
                "09-screenshot-sizes.txt",
                ("02-home-collapsed.png", "03-home-expanded-by-summary.png", "screenshots/play-store/02-home.png", "pixelWidth: 1080", "pixelHeight: 2400"),
            ),
            ("10-ui-marker-check.txt", ("PASS Home filter chevron disclosure markers", "PASS collapsed Home hides lower filter controls")),
        ),
    ),
    EvidenceSet(
        name="Android 16 Home filter unframed summary",
        report="docs/emulator_android16_home_filter_unframed_summary_qa_2026_06_06.md",
        directory="qa/emulator-android16-home-filter-unframed-summary-qa-2026-06-06",
        report_snippets=(
            "qa/emulator-android16-home-filter-unframed-summary-qa-2026-06-06",
            "unframed summary row",
            "screenshots/play-store/02-home.png",
            "07-app-fatal-anr-matches.txt",
        ),
        pairs=("01-onboarding", "02-home-collapsed", "03-home-expanded", "04-home-expanded-scrolled"),
        files=(
            "06-logcat.txt",
            "08-screenshot-sizes.txt",
            "09-ui-marker-check.txt",
            "10-focus.txt",
            "wm-size.txt",
            "wm-density.txt",
            "android-release.txt",
            "android-sdk.txt",
            "resolve-activity.txt",
        ),
        zero_byte_files=("05-crash-buffer.txt", "07-app-fatal-anr-matches.txt"),
        snippets=(
            ("wm-size.txt", ("Physical size: 1080x2400",)),
            ("wm-density.txt", ("Physical density: 420",)),
            ("android-release.txt", ("16",)),
            ("android-sdk.txt", ("36",)),
            ("resolve-activity.txt", (PACKAGE, "MainActivity")),
            ("01-onboarding.xml", ("Порядок 5", "Начать", PACKAGE)),
            (
                "02-home-collapsed.xml",
                ("Настроить подбор", "Изменить", "Запустить таймер", "Другая задача", PACKAGE),
            ),
            ("03-home-expanded.xml", ("Настроить подбор", "Скрыть", "Зона", "Работа", "Цифра", PACKAGE)),
            (
                "04-home-expanded-scrolled.xml",
                ("Энергия", "Лёгкая", "Средняя", "Бодрая", "Время", "3 мин", "5 мин", "10 мин", PACKAGE),
            ),
            ("10-focus.txt", (PACKAGE, "MainActivity")),
            (
                "08-screenshot-sizes.txt",
                ("02-home-collapsed.png", "04-home-expanded-scrolled.png", "screenshots/play-store/02-home.png", "1080 x 2400"),
            ),
            ("09-ui-marker-check.txt", ("02-home-collapsed.xml", "03-home-expanded.xml", "04-home-expanded-scrolled.xml")),
        ),
    ),
    EvidenceSet(
        name="Android 15 Home stats icon",
        report="docs/emulator_android15_home_stats_icon_qa_2026_06_06.md",
        directory="qa/emulator-android15-home-stats-icon-qa-2026-06-06",
        report_snippets=(
            "qa/emulator-android15-home-stats-icon-qa-2026-06-06",
            "StatsIcon",
            "screenshots/play-store/02-home.png",
            "crash-logcat-package-matches.txt",
        ),
        pairs=("01-onboarding", "02-home-stats-icon"),
        files=(
            "01-onboarding-summary.txt",
            "02-home-stats-icon-summary.txt",
            "focus.txt",
            "wm-size.txt",
            "wm-density.txt",
            "android-release.txt",
            "android-sdk.txt",
            "resolve-activity.txt",
            "screenshot-size.txt",
        ),
        zero_byte_files=("crash-logcat-package-matches.txt",),
        snippets=(
            ("wm-size.txt", ("Physical size: 1080x2400",)),
            ("wm-density.txt", ("Physical density: 420",)),
            ("android-release.txt", ("15",)),
            ("android-sdk.txt", ("35",)),
            ("resolve-activity.txt", (PACKAGE, "MainActivity")),
            ("01-onboarding.xml", ("Порядок 5", "Начать", PACKAGE)),
            ("02-home-stats-icon.xml", ("Порядок 5", "Итоги", "Опции", "Запустить таймер", PACKAGE)),
            ("02-home-stats-icon-summary.txt", ("Button desc=\"Итоги\"", "Button desc=\"Опции\"", "Запустить таймер")),
            ("focus.txt", (PACKAGE, "MainActivity")),
            ("screenshot-size.txt", ("pixelWidth: 1080", "pixelHeight: 2400")),
        ),
    ),
    EvidenceSet(
        name="Android 15 Home result preview",
        report="docs/emulator_android15_home_result_preview_qa_2026_06_06.md",
        directory="qa/emulator-android15-home-result-preview-qa-2026-06-06",
        report_snippets=(
            "qa/emulator-android15-home-result-preview-qa-2026-06-06",
            "Home task result preview",
            "screenshots/play-store/02-home.png",
            "06-app-fatal-anr-matches.txt",
        ),
        pairs=("01-onboarding", "02-home-result-preview"),
        files=(
            "00-launch.txt",
            "02-focus-onboarding.txt",
            "03-focus-home.txt",
            "04-screenshot-sizes.txt",
            "07-ui-marker-check.txt",
            "wm-size.txt",
            "wm-density.txt",
            "android-release.txt",
            "android-sdk.txt",
            "resolve-activity.txt",
        ),
        zero_byte_files=("05-crash-buffer.txt", "06-app-fatal-anr-matches.txt"),
        snippets=(
            ("wm-size.txt", ("Physical size: 1080x2400",)),
            ("wm-density.txt", ("Physical density: 420",)),
            ("android-release.txt", ("15",)),
            ("android-sdk.txt", ("35",)),
            ("resolve-activity.txt", (PACKAGE, "MainActivity")),
            ("01-onboarding.xml", ("Порядок 5", "Начать", PACKAGE)),
            (
                "02-home-result-preview.xml",
                (
                    "Задача на сейчас",
                    "Первый шаг",
                    "После",
                    "В комнате появился один аккуратный визуальный якорь",
                    "Запустить таймер",
                    "Другая задача",
                    "Посмотреть шаги",
                    PACKAGE,
                ),
            ),
            ("03-focus-home.txt", (PACKAGE, "MainActivity")),
            (
                "04-screenshot-sizes.txt",
                ("02-home-result-preview.png", "screenshots/play-store/02-home.png", "pixelWidth: 1080", "pixelHeight: 2400"),
            ),
            ("07-ui-marker-check.txt", ("PASS: Home result preview markers visible", "old inline marker absent")),
        ),
    ),
    EvidenceSet(
        name="Android 15 Home action icons",
        report="docs/emulator_android15_home_action_icons_qa_2026_06_06.md",
        directory="qa/emulator-android15-home-action-icons-qa-2026-06-06",
        report_snippets=(
            "qa/emulator-android15-home-action-icons-qa-2026-06-06",
            "Home action icons",
            "screenshots/play-store/02-home.png",
            "06-app-fatal-anr-matches.txt",
        ),
        pairs=("01-onboarding", "02-home-action-icons"),
        files=(
            "00-launch.txt",
            "01-onboarding-start-node.txt",
            "03-focus-home.txt",
            "04-screenshot-sizes.txt",
            "07-ui-marker-check.txt",
            "wm-size.txt",
            "wm-density.txt",
            "android-release.txt",
            "android-sdk.txt",
            "resolve-activity.txt",
        ),
        zero_byte_files=("05-crash-buffer.txt", "06-app-fatal-anr-matches.txt"),
        snippets=(
            ("wm-size.txt", ("Physical size: 1080x2400",)),
            ("wm-density.txt", ("Physical density: 420",)),
            ("android-release.txt", ("15",)),
            ("android-sdk.txt", ("35",)),
            ("resolve-activity.txt", (PACKAGE, "MainActivity")),
            ("01-onboarding.xml", ("Порядок 5", "Начать", PACKAGE)),
            ("01-onboarding-start-node.txt", ("Начать", "bounds=")),
            (
                "02-home-action-icons.xml",
                ("Совпадает с выбором", "Запустить таймер", "Другая задача", "Все шаги", "Настроить подбор", PACKAGE),
            ),
            ("03-focus-home.txt", (PACKAGE, "MainActivity")),
            (
                "04-screenshot-sizes.txt",
                ("02-home-action-icons.png", "screenshots/play-store/02-home.png", "pixelWidth: 1080", "pixelHeight: 2400"),
            ),
            ("07-ui-marker-check.txt", ("PASS: Home action icon labels visible", "PASS: Home selection copy visible")),
        ),
    ),
    EvidenceSet(
        name="Android 15 main-flow action icons",
        report="docs/emulator_android15_main_flow_action_icons_qa_2026_06_06.md",
        directory="qa/emulator-android15-main-flow-action-icons-qa-2026-06-06",
        report_snippets=(
            "qa/emulator-android15-main-flow-action-icons-qa-2026-06-06",
            "main-flow CTA icons",
            "screenshots/play-store/05-progress.png",
            "10-app-fatal-anr-matches.txt",
        ),
        pairs=(
            "01-onboarding",
            "02-home",
            "03-details",
            "04-timer",
            "05-result",
            "06-progress",
        ),
        files=(
            "00-launch.txt",
            "00-pm-clear.txt",
            "07-focus.txt",
            "08-screenshot-sizes.txt",
            "11-ui-marker-check.txt",
            "wm-size.txt",
            "wm-density.txt",
            "android-release.txt",
            "android-sdk.txt",
            "resolve-activity.txt",
        ),
        zero_byte_files=("09-app-crash-package-matches.txt", "10-app-fatal-anr-matches.txt"),
        snippets=(
            ("wm-size.txt", ("Physical size: 1080x2400",)),
            ("wm-density.txt", ("Physical density: 420",)),
            ("android-release.txt", ("15",)),
            ("android-sdk.txt", ("35",)),
            ("resolve-activity.txt", (PACKAGE, "MainActivity")),
            ("01-onboarding.xml", ("Порядок 5", "Начать", PACKAGE)),
            ("02-home.xml", ("Порядок 5", "Совпадает с выбором", "Запустить таймер", "Все шаги", PACKAGE)),
            ("03-details.xml", ("Перед стартом", "Начать 5 мин", PACKAGE)),
            ("04-timer.xml", ("Таймер", "Готово", PACKAGE)),
            ("05-result.xml", ("Готово", "Посмотреть следующую", "Посмотреть итоги", PACKAGE)),
            ("06-progress.xml", ("Итоги", "1 из 80", "Продолжить с задачей", PACKAGE)),
            ("07-focus.txt", (PACKAGE, "MainActivity")),
            ("08-screenshot-sizes.txt", ("01-onboarding.png", "06-progress.png", "1080 x 2400")),
            ("11-ui-marker-check.txt", ("01-onboarding.xml: PASS", "06-progress.xml: PASS")),
        ),
    ),
    EvidenceSet(
        name="Android 15 Result details-first primary",
        report="docs/emulator_android15_result_details_first_qa_2026_06_06.md",
        directory="qa/emulator-android15-result-details-first-qa-2026-06-06",
        report_snippets=(
            "qa/emulator-android15-result-details-first-qa-2026-06-06",
            "Посмотреть следующую",
            "Запустить таймер",
            "crash-logcat-package-matches.txt",
        ),
        pairs=("01-onboarding", "02-home", "03-timer", "04-result-details-first", "05-details-from-result-primary"),
        files=(
            "01-onboarding-summary.txt",
            "02-home-summary.txt",
            "03-timer-summary.txt",
            "04-result-details-first-summary.txt",
            "05-details-from-result-primary-summary.txt",
            "focus.txt",
            "wm-size.txt",
            "wm-density.txt",
            "android-release.txt",
            "android-sdk.txt",
            "resolve-activity.txt",
            "screenshot-sizes.txt",
        ),
        zero_byte_files=("crash-logcat-package-matches.txt",),
        snippets=(
            ("wm-size.txt", ("Physical size: 1080x2400",)),
            ("wm-density.txt", ("Physical density: 420",)),
            ("android-release.txt", ("15",)),
            ("android-sdk.txt", ("35",)),
            ("resolve-activity.txt", (PACKAGE, "MainActivity")),
            (
                "04-result-details-first.xml",
                ("Готово", "Посмотреть следующую", "Запустить таймер", "На главный экран", "Посмотреть итоги", PACKAGE),
            ),
            ("04-result-details-first-summary.txt", ("Посмотреть следующую", "Запустить таймер")),
            (
                "05-details-from-result-primary.xml",
                ("Задача", "Выбранная задача", "Перед стартом", "Начать 5 мин", PACKAGE),
            ),
            ("focus.txt", (PACKAGE, "MainActivity")),
            ("screenshot-sizes.txt", ("screenshots/play-store/04-result.png", "pixelWidth: 1080", "pixelHeight: 2400")),
        ),
    ),
    EvidenceSet(
        name="Android 16 Result content focus",
        report="docs/emulator_android16_result_content_focus_qa_2026_06_06.md",
        directory="qa/emulator-android16-result-content-focus-qa-2026-06-06",
        report_snippets=(
            "qa/emulator-android16-result-content-focus-qa-2026-06-06",
            "Сделано",
            "Что изменилось",
            "generic amber",
            "09-app-fatal-anr-matches.txt",
        ),
        pairs=("01-onboarding", "02-home", "03-timer", "04-result-content-focus"),
        files=(
            "01-onboarding-summary.txt",
            "02-home-summary.txt",
            "03-timer-summary.txt",
            "04-result-content-focus-summary.txt",
            "focus.txt",
            "activity-focus.txt",
            "wm-size.txt",
            "wm-density.txt",
            "android-release.txt",
            "android-sdk.txt",
            "resolve-activity.txt",
            "10-screenshot-sizes.txt",
            "11-ui-marker-check.txt",
        ),
        zero_byte_files=("09-app-fatal-anr-matches.txt",),
        snippets=(
            ("wm-size.txt", ("Physical size: 1080x2400",)),
            ("wm-density.txt", ("Physical density: 420",)),
            ("android-release.txt", ("16",)),
            ("android-sdk.txt", ("36",)),
            ("resolve-activity.txt", (PACKAGE, "MainActivity")),
            ("01-onboarding.xml", ("Порядок 5", "Начать", PACKAGE)),
            ("02-home.xml", ("Порядок 5", "Запустить таймер", PACKAGE)),
            ("03-timer.xml", ("Таймер", "Готово", PACKAGE)),
            (
                "04-result-content-focus.xml",
                (
                    "Готово",
                    "Сделано: Подготовить спокойный угол",
                    "В комнате появился один аккуратный визуальный якорь",
                    "Дальше без повтора",
                    "Протереть зеркало",
                    "Первый шаг",
                    "После",
                    "Зеркало выглядит свежо, а задача заняла несколько минут",
                    "Посмотреть следующую",
                    "Запустить таймер",
                    "На главный экран",
                    "Посмотреть итоги",
                    PACKAGE,
                ),
            ),
            (
                "04-result-content-focus-summary.txt",
                (
                    "Сделано: Подготовить спокойный угол",
                    "Дальше без повтора",
                    "После",
                    "Зеркало выглядит свежо",
                    "Посмотреть следующую",
                    "Запустить таймер",
                ),
            ),
            ("focus.txt", (PACKAGE, "MainActivity")),
            ("activity-focus.txt", (PACKAGE, "topResumedActivity")),
            (
                "10-screenshot-sizes.txt",
                ("screenshots/play-store/04-result.png", "pixelWidth: 1080", "pixelHeight: 2400"),
            ),
            (
                "11-ui-marker-check.txt",
                ("PASS markers", "После", "PASS old generic result copy absent", "PASS app-specific fatal/ANR matches are empty"),
            ),
        ),
    ),
    EvidenceSet(
        name="Android 16 Result peer icons",
        report="docs/emulator_android16_result_peer_icons_qa_2026_06_06.md",
        directory="qa/emulator-android16-result-peer-icons-qa-2026-06-06",
        report_snippets=(
            "qa/emulator-android16-result-peer-icons-qa-2026-06-06",
            "Result peer-action icon polish",
            "screenshots/play-store/04-result.png",
            "07-app-fatal-anr-matches.txt",
        ),
        pairs=("01-onboarding", "02-home", "03-timer", "04-result"),
        files=(
            "01-onboarding-summary.txt",
            "02-home-summary.txt",
            "03-timer-summary.txt",
            "04-result-summary.txt",
            "08-screenshot-sizes.txt",
            "09-ui-marker-check.txt",
            "10-focus.txt",
            "wm-size.txt",
            "wm-density.txt",
            "android-release.txt",
            "android-sdk.txt",
            "resolve-activity.txt",
        ),
        zero_byte_files=("05-crash-buffer.txt", "07-app-fatal-anr-matches.txt"),
        snippets=(
            ("wm-size.txt", ("Physical size: 1080x2400",)),
            ("wm-density.txt", ("Physical density: 420",)),
            ("android-release.txt", ("16",)),
            ("android-sdk.txt", ("36",)),
            ("resolve-activity.txt", (PACKAGE, "MainActivity")),
            ("01-onboarding.xml", ("Порядок 5", "Начать", PACKAGE)),
            ("02-home.xml", ("Порядок 5", "Запустить таймер", PACKAGE)),
            ("03-timer.xml", ("Таймер", "Готово", PACKAGE)),
            (
                "04-result.xml",
                (
                    "Готово",
                    "Сделано: Подготовить спокойный угол",
                    "На главный экран",
                    "Посмотреть итоги",
                    PACKAGE,
                ),
            ),
            ("04-result-summary.txt", ("На главный экран", "Посмотреть итоги")),
            ("08-screenshot-sizes.txt", ("04-result.png", "1080 x 2400")),
            (
                "09-ui-marker-check.txt",
                (
                    "PASS result peer markers",
                    "PASS app-specific fatal/ANR matches are empty",
                ),
            ),
            ("10-focus.txt", (PACKAGE, "MainActivity")),
        ),
    ),
    EvidenceSet(
        name="Android 16 Task details briefing",
        report="docs/emulator_android16_task_details_briefing_qa_2026_06_06.md",
        directory="qa/emulator-android16-task-details-briefing-qa-2026-06-06",
        report_snippets=(
            "qa/emulator-android16-task-details-briefing-qa-2026-06-06",
            "Task details pre-start briefing",
            "Начать 5 мин",
            "08-app-fatal-anr-matches.txt",
        ),
        pairs=("01-onboarding", "02-home", "03-details", "03b-details-lower", "04-timer"),
        files=(
            "00-focus-after-launch.txt",
            "05-focus.txt",
            "06-logcat.txt",
            "09-screenshot-sizes.txt",
            "wm-size.txt",
            "wm-density.txt",
            "android-release.txt",
            "android-sdk.txt",
            "avd-name.txt",
            "resolve-activity.txt",
        ),
        zero_byte_files=("07-crash-buffer.txt", "08-app-fatal-anr-matches.txt"),
        snippets=(
            ("wm-size.txt", ("Physical size: 1080x2400",)),
            ("wm-density.txt", ("Physical density: 420",)),
            ("android-release.txt", ("16",)),
            ("android-sdk.txt", ("36",)),
            ("avd-name.txt", ("Medium_Phone_API_36",)),
            ("resolve-activity.txt", (PACKAGE, "MainActivity")),
            ("00-focus-after-launch.txt", (PACKAGE, "MainActivity")),
            ("01-onboarding.xml", ("Порядок 5", "Начать", PACKAGE)),
            ("02-home.xml", ("Порядок 5", "Посмотреть шаги", "Запустить таймер", PACKAGE)),
            (
                "03-details.xml",
                ("Выбранная задача", "Перед стартом", "зона", "энергия", "время", "Шаги", "Результат", PACKAGE),
            ),
            ("03b-details-lower.xml", ("Перед стартом", "Начать 5 мин", PACKAGE)),
            ("04-timer.xml", ("Таймер", "Пауза", PACKAGE)),
            ("05-focus.txt", (PACKAGE, "MainActivity")),
            ("09-screenshot-sizes.txt", ("03-details.png", "03b-details-lower.png", "pixelWidth: 1080", "pixelHeight: 2400")),
        ),
    ),
    EvidenceSet(
        name="Android 15 Task details unframed briefing",
        report="docs/emulator_android15_task_details_unframed_qa_2026_06_06.md",
        directory="qa/emulator-android15-task-details-unframed-qa-2026-06-06",
        report_snippets=(
            "qa/emulator-android15-task-details-unframed-qa-2026-06-06",
            "unframed 56dp",
            "Начать 5 мин",
            "07-app-fatal-anr-matches.txt",
        ),
        pairs=("01-onboarding", "02-home", "03-details-top", "03b-details-lower", "04-timer"),
        files=(
            "05-focus.txt",
            "08-screenshot-sizes.txt",
            "09-ui-marker-check.txt",
            "wm-size.txt",
            "wm-density.txt",
            "android-release.txt",
            "android-sdk.txt",
            "resolve-activity.txt",
        ),
        zero_byte_files=("06-crash-buffer.txt", "07-app-fatal-anr-matches.txt"),
        snippets=(
            ("wm-size.txt", ("Physical size: 1080x2400",)),
            ("wm-density.txt", ("Physical density: 420",)),
            ("android-release.txt", ("15",)),
            ("android-sdk.txt", ("35",)),
            ("resolve-activity.txt", (PACKAGE, "MainActivity")),
            ("01-onboarding.xml", ("Порядок 5", "Начать", PACKAGE)),
            ("02-home.xml", ("Порядок 5", "Все шаги", "Запустить таймер", PACKAGE)),
            (
                "03-details-top.xml",
                (
                    "Выбранная задача",
                    "выбрана",
                    "Перед стартом",
                    "зона",
                    "энергия",
                    "время",
                    "После",
                    "Шаги",
                    PACKAGE,
                ),
            ),
            ("03b-details-lower.xml", ("После", "Шаги", "Начать 5 мин", PACKAGE)),
            ("04-timer.xml", ("Таймер", "Цель: 5 мин", "Пауза", "Готово", PACKAGE)),
            ("05-focus.txt", (PACKAGE, "MainActivity")),
            (
                "08-screenshot-sizes.txt",
                ("03-details-top.png", "03b-details-lower.png", "04-timer.png", "pixelWidth: 1080", "pixelHeight: 2400"),
            ),
            (
                "09-ui-marker-check.txt",
                (
                    "PASS Task details unframed briefing markers",
                    "PASS Details lower keeps start dock and outcome preview",
                    "PASS Details start dock opens Timer",
                ),
            ),
        ),
    ),
    EvidenceSet(
        name="Android 15 Timer completion dock",
        report="docs/emulator_android15_timer_completion_dock_qa_2026_06_06.md",
        directory="qa/emulator-android15-timer-completion-dock-qa-2026-06-06",
        report_snippets=(
            "qa/emulator-android15-timer-completion-dock-qa-2026-06-06",
            "Timer completion dock",
            "screenshots/play-store/03-timer.png",
            "06-app-fatal-anr-matches.txt",
        ),
        pairs=("01-onboarding", "02-home", "03-timer"),
        files=(
            "04-focus.txt",
            "07-screenshot-sizes.txt",
            "wm-size.txt",
            "wm-density.txt",
            "android-release.txt",
            "android-sdk.txt",
            "resolve-activity.txt",
        ),
        zero_byte_files=("05-crash-buffer.txt", "06-app-fatal-anr-matches.txt"),
        snippets=(
            ("wm-size.txt", ("Physical size: 1080x2400",)),
            ("wm-density.txt", ("Physical density: 420",)),
            ("android-release.txt", ("15",)),
            ("android-sdk.txt", ("35",)),
            ("resolve-activity.txt", (PACKAGE, "MainActivity")),
            ("01-onboarding.xml", ("Порядок 5", "Начать", PACKAGE)),
            ("02-home.xml", ("Порядок 5", "Запустить таймер", PACKAGE)),
            ("03-timer.xml", ("Таймер", "Пауза", "Сброс", "План", "Готово", PACKAGE)),
            ("04-focus.txt", (PACKAGE, "MainActivity")),
            ("07-screenshot-sizes.txt", ("screenshots/play-store/03-timer.png", "pixelWidth: 1080", "pixelHeight: 2400")),
        ),
    ),
    EvidenceSet(
        name="Android 16 Timer control icons",
        report="docs/emulator_android16_timer_control_icons_qa_2026_06_06.md",
        directory="qa/emulator-android16-timer-control-icons-qa-2026-06-06",
        report_snippets=(
            "qa/emulator-android16-timer-control-icons-qa-2026-06-06",
            "Timer control icons",
            "screenshots/play-store/03-timer.png",
            "07-app-fatal-anr-matches.txt",
        ),
        pairs=("01-onboarding", "02-home", "03-timer", "04-timer-paused"),
        files=(
            "01-onboarding-summary.txt",
            "02-home-summary.txt",
            "03-timer-summary.txt",
            "04-timer-paused-summary.txt",
            "08-screenshot-sizes.txt",
            "09-ui-marker-check.txt",
            "10-focus.txt",
            "wm-size.txt",
            "wm-density.txt",
            "android-release.txt",
            "android-sdk.txt",
            "resolve-activity.txt",
        ),
        zero_byte_files=("05-crash-buffer.txt", "07-app-fatal-anr-matches.txt"),
        snippets=(
            ("wm-size.txt", ("Physical size: 1080x2400",)),
            ("wm-density.txt", ("Physical density: 420",)),
            ("android-release.txt", ("16",)),
            ("android-sdk.txt", ("36",)),
            ("resolve-activity.txt", (PACKAGE, "MainActivity")),
            ("01-onboarding.xml", ("Порядок 5", "Начать", PACKAGE)),
            ("02-home.xml", ("Порядок 5", "Запустить таймер", PACKAGE)),
            ("03-timer.xml", ("Таймер", "Цель: 5 мин", "Пауза", "Сброс", "Готово", PACKAGE)),
            ("04-timer-paused.xml", ("Таймер", "Продолжить", "Сброс", "Готово", PACKAGE)),
            ("08-screenshot-sizes.txt", ("03-timer.png", "04-timer-paused.png", "1080 x 2400")),
            (
                "09-ui-marker-check.txt",
                (
                    "PASS timer running markers",
                    "PASS timer paused markers",
                    "PASS app-specific fatal/ANR matches are empty",
                ),
            ),
            ("10-focus.txt", (PACKAGE, "MainActivity")),
        ),
    ),
    EvidenceSet(
        name="Android 15 Settings privacy summary",
        report="docs/emulator_android15_settings_privacy_summary_qa_2026_06_06.md",
        directory="qa/emulator-android15-settings-privacy-summary-qa-2026-06-06",
        report_snippets=(
            "qa/emulator-android15-settings-privacy-summary-qa-2026-06-06",
            "PrivacyBadgeGrid",
            "Без аналитики",
            "crash-logcat-package-matches.txt",
        ),
        pairs=("01-onboarding", "02-home", "03-settings-privacy-summary"),
        files=(
            "01-onboarding-summary.txt",
            "02-home-summary.txt",
            "03-settings-privacy-summary-summary.txt",
            "focus.txt",
            "wm-size.txt",
            "wm-density.txt",
            "android-release.txt",
            "android-sdk.txt",
            "resolve-activity.txt",
            "screenshot-sizes.txt",
        ),
        zero_byte_files=("crash-logcat-package-matches.txt",),
        snippets=(
            ("wm-size.txt", ("Physical size: 1080x2400",)),
            ("wm-density.txt", ("Physical density: 420",)),
            ("android-release.txt", ("15",)),
            ("android-sdk.txt", ("35",)),
            ("resolve-activity.txt", (PACKAGE, "MainActivity")),
            ("01-onboarding.xml", ("Порядок 5", "Начать", PACKAGE)),
            ("02-home.xml", ("Порядок 5", "Опции", PACKAGE)),
            (
                "03-settings-privacy-summary.xml",
                (
                    "Настройки",
                    "Приватность",
                    "Прогресс хранится только на устройстве",
                    "Без интернета",
                    "Без аккаунта",
                    "Без рекламы",
                    "Без аналитики",
                    "О приложении",
                    PACKAGE,
                ),
            ),
            (
                "03-settings-privacy-summary-summary.txt",
                ("Без интернета", "Без аккаунта", "Без рекламы", "Без аналитики"),
            ),
            ("focus.txt", (PACKAGE, "MainActivity")),
            (
                "screenshot-sizes.txt",
                ("screenshots/play-store/06-settings.png", "pixelWidth: 1080", "pixelHeight: 2400"),
            ),
        ),
    ),
    EvidenceSet(
        name="Android 16 Settings privacy unframed",
        report="docs/emulator_android16_settings_privacy_unframed_qa_2026_06_06.md",
        directory="qa/emulator-android16-settings-privacy-unframed-qa-2026-06-06",
        report_snippets=(
            "qa/emulator-android16-settings-privacy-unframed-qa-2026-06-06",
            "unframed",
            "screenshots/play-store/06-settings.png",
            "09-app-fatal-anr-matches.txt",
        ),
        pairs=("01-onboarding", "02-home", "03-settings-privacy-unframed"),
        files=(
            "01-onboarding-summary.txt",
            "02-home-summary.txt",
            "03-settings-privacy-unframed-summary.txt",
            "focus.txt",
            "activity-focus.txt",
            "wm-size.txt",
            "wm-density.txt",
            "android-release.txt",
            "android-sdk.txt",
            "resolve-activity.txt",
            "10-screenshot-sizes.txt",
            "11-ui-marker-check.txt",
        ),
        zero_byte_files=("09-app-fatal-anr-matches.txt",),
        snippets=(
            ("wm-size.txt", ("Physical size: 1080x2400",)),
            ("wm-density.txt", ("Physical density: 420",)),
            ("android-release.txt", ("16",)),
            ("android-sdk.txt", ("36",)),
            ("resolve-activity.txt", (PACKAGE, "MainActivity")),
            ("01-onboarding.xml", ("Порядок 5", "Начать", PACKAGE)),
            ("02-home.xml", ("Порядок 5", "Опции", PACKAGE)),
            (
                "03-settings-privacy-unframed.xml",
                (
                    "Настройки",
                    "Приватность",
                    "Прогресс хранится только на устройстве",
                    "Без интернета",
                    "работает офлайн",
                    "Без аккаунта",
                    "вход не нужен",
                    "Без рекламы",
                    "нет баннеров",
                    "Без аналитики",
                    "нет трекеров",
                    "О приложении",
                    PACKAGE,
                ),
            ),
            (
                "03-settings-privacy-unframed-summary.txt",
                (
                    "Без интернета",
                    "работает офлайн",
                    "Без аккаунта",
                    "вход не нужен",
                    "Без рекламы",
                    "нет баннеров",
                    "Без аналитики",
                    "нет трекеров",
                ),
            ),
            ("focus.txt", (PACKAGE, "MainActivity")),
            ("activity-focus.txt", (PACKAGE, "topResumedActivity")),
            (
                "10-screenshot-sizes.txt",
                ("screenshots/play-store/06-settings.png", "pixelWidth: 1080", "pixelHeight: 2400"),
            ),
            ("11-ui-marker-check.txt", ("PASS markers", "Без аналитики", "нет трекеров", PACKAGE)),
        ),
    ),
    EvidenceSet(
        name="Android 16 Settings about summary",
        report="docs/emulator_android16_settings_about_summary_qa_2026_06_06.md",
        directory="qa/emulator-android16-settings-about-summary-qa-2026-06-06",
        report_snippets=(
            "qa/emulator-android16-settings-about-summary-qa-2026-06-06",
            "PASSED",
            "Settings `О приложении` polish",
            "screenshots/play-store/06-settings.png",
        ),
        pairs=("01-onboarding", "02-home", "03-settings"),
        files=(
            "01-onboarding-summary.txt",
            "02-home-summary.txt",
            "03-settings-summary.txt",
            "04-focus.txt",
            "08-screenshot-sizes.txt",
            "09-ui-marker-check.txt",
            "wm-size.txt",
            "wm-density.txt",
            "android-release.txt",
            "android-sdk.txt",
            "avd-name.txt",
            "resolve-activity.txt",
        ),
        zero_byte_files=("07-app-fatal-anr-matches.txt",),
        snippets=(
            ("wm-size.txt", ("Physical size: 1080x2400",)),
            ("wm-density.txt", ("Physical density: 420",)),
            ("android-release.txt", ("16",)),
            ("android-sdk.txt", ("36",)),
            ("avd-name.txt", ("Medium_Phone_API_36",)),
            ("resolve-activity.txt", (PACKAGE, "MainActivity")),
            ("01-onboarding.xml", ("Порядок 5", "Начать", PACKAGE)),
            ("02-home.xml", ("Порядок 5", "Опции", "Настроить подбор", PACKAGE)),
            (
                "03-settings.xml",
                (
                    "Настройки",
                    "Приватность",
                    "О приложении",
                    "Порядок 5",
                    "Версия",
                    "1.0.0-rc1",
                    "Каталог",
                    "80 задач",
                    "Данные",
                    "на устройстве",
                    PACKAGE,
                ),
            ),
            (
                "03-settings-summary.txt",
                ("Версия", "1.0.0-rc1", "Каталог", "80 задач", "Данные", "на устройстве"),
            ),
            ("04-focus.txt", (PACKAGE, "MainActivity")),
            (
                "08-screenshot-sizes.txt",
                ("screenshots/play-store/06-settings.png", "pixelWidth: 1080", "pixelHeight: 2400"),
            ),
            (
                "09-ui-marker-check.txt",
                ("PASS markers", "Absent: Локальный каталог", PACKAGE),
            ),
        ),
    ),
    EvidenceSet(
        name="Android 15 Task status pill affordance",
        report="docs/emulator_android15_task_status_pill_qa_2026_06_06.md",
        directory="qa/emulator-android15-task-status-pill-qa-2026-06-06",
        report_snippets=(
            "qa/emulator-android15-task-status-pill-qa-2026-06-06",
            "TaskStatusPill",
            "screenshots/play-store/02-home.png",
            "crash-logcat-package-matches.txt",
        ),
        pairs=("01-onboarding", "02-home-status-pill", "03-timer", "04-result-status-pill"),
        files=(
            "01-onboarding-summary.txt",
            "02-home-status-pill-summary.txt",
            "04-result-status-pill-summary.txt",
            "focus.txt",
            "wm-size.txt",
            "wm-density.txt",
            "android-release.txt",
            "android-sdk.txt",
            "resolve-activity.txt",
            "screenshot-sizes.txt",
        ),
        zero_byte_files=("crash-logcat-package-matches.txt",),
        snippets=(
            ("wm-size.txt", ("Physical size: 1080x2400",)),
            ("wm-density.txt", ("Physical density: 420",)),
            ("android-release.txt", ("15",)),
            ("android-sdk.txt", ("35",)),
            ("resolve-activity.txt", (PACKAGE, "MainActivity")),
            ("01-onboarding.xml", ("Порядок 5", "Начать", PACKAGE)),
            (
                "02-home-status-pill.xml",
                ("Порядок 5", "Задача на сейчас", "новая", "Запустить таймер", "Другая задача", PACKAGE),
            ),
            (
                "04-result-status-pill.xml",
                ("Готово", "Дальше без повтора", "новая", "Посмотреть следующую", "Запустить таймер", PACKAGE),
            ),
            (
                "02-home-status-pill-summary.txt",
                ("TextView text=\"новая\"", "Запустить таймер", "Посмотреть шаги"),
            ),
            (
                "04-result-status-pill-summary.txt",
                ("TextView text=\"новая\"", "Посмотреть следующую", "На главный экран"),
            ),
            ("focus.txt", (PACKAGE, "MainActivity")),
            (
                "screenshot-sizes.txt",
                (
                    "screenshots/play-store/02-home.png",
                    "screenshots/play-store/04-result.png",
                    "pixelWidth: 1080",
                    "pixelHeight: 2400",
                ),
            ),
        ),
    ),
    EvidenceSet(
        name="Android 15 settings haptics row",
        report="docs/emulator_android15_settings_haptics_row_qa_2026_06_03.md",
        directory="qa/emulator-android15-settings-haptics-row-qa-2026-06-03",
        report_snippets=(
            "qa/emulator-android15-settings-haptics-row-qa-2026-06-03",
            "Тактильный отклик",
            "checked=true",
            "checked=false",
        ),
        pairs=("03-settings-before", "04-settings-after-label-tap"),
        files=("03-settings-before-ui-summary.txt", "04-settings-after-label-tap-ui-summary.txt"),
        zero_byte_files=("app-crash-matches.txt",),
        snippets=(
            ("03-settings-before.xml", ("Тактильный отклик", "checkable=\"true\"", "clickable=\"true\"", "checked=\"true\"", PACKAGE)),
            ("04-settings-after-label-tap.xml", ("Тактильный отклик", "checkable=\"true\"", "clickable=\"true\"", "checked=\"false\"", PACKAGE)),
        ),
    ),
    EvidenceSet(
        name="Android 15 settings reset cancel",
        report="docs/emulator_android15_settings_reset_cancel_qa_2026_06_03.md",
        directory="qa/emulator-android15-settings-reset-cancel-qa-2026-06-03",
        report_snippets=(
            "qa/emulator-android15-settings-reset-cancel-qa-2026-06-03",
            "Отмена",
            "Сбросить прогресс",
            "com.android.bluetooth",
        ),
        pairs=(
            "01-onboarding",
            "02-home",
            "03-settings-reset-before",
            "04-reset-confirm",
            "05-reset-after-cancel",
            "06-reset-confirm-second",
            "07-reset-after-confirm",
        ),
        files=("08-focus.txt", "10-logcat.txt", "12-crash-context-filter.txt"),
        zero_byte_files=("11-app-fatal-anr-matches.txt",),
        snippets=(
            ("03-settings-reset-before.xml", ("Подготовить сброс", PACKAGE)),
            ("04-reset-confirm.xml", ("Отмена", "Сбросить прогресс", "Подтвердите сброс", PACKAGE)),
            ("05-reset-after-cancel.xml", ("Подготовить сброс", PACKAGE)),
            ("06-reset-confirm-second.xml", ("Отмена", "Сбросить прогресс", PACKAGE)),
            ("07-reset-after-confirm.xml", ("Готово. Прогресс сброшен, можно начать заново.", "Подготовить сброс", PACKAGE)),
            ("08-focus.txt", (PACKAGE, "MainActivity")),
            ("12-crash-context-filter.txt", ("com.android.bluetooth", PACKAGE)),
        ),
        allow_crash_log_packages=("com.android.bluetooth", "droid.bluetooth"),
    ),
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def current_package_name() -> str:
    return str(read_gradle_release_identity()["appId"])


def resolve_marker(value: str, package_name: str) -> str:
    return value.replace(APP_PACKAGE_TOKEN, package_name)


def display_path(path: Path, root: Path = ROOT) -> str:
    return str(path.relative_to(root))


def validate_file(path: Path, failures: list[str], min_bytes: int = 1, root: Path = ROOT) -> None:
    if not path.exists():
        failures.append(f"missing evidence file: {display_path(path, root)}")
        return
    if not path.is_file():
        failures.append(f"evidence path is not a file: {display_path(path, root)}")
        return
    size = path.stat().st_size
    if size < min_bytes:
        failures.append(f"evidence file is too small: {display_path(path, root)} ({size} bytes)")


def validate_png(path: Path, failures: list[str], root: Path = ROOT) -> None:
    validate_file(path, failures, min_bytes=256, root=root)
    if path.exists() and path.is_file():
        header = path.read_bytes()[: len(PNG_HEADER)]
        if header != PNG_HEADER:
            failures.append(f"PNG evidence has invalid signature: {display_path(path, root)}")


def validate_xml(path: Path, failures: list[str], package_name: str, root: Path = ROOT) -> None:
    validate_file(path, failures, min_bytes=256, root=root)
    if path.exists() and path.is_file():
        text = read_text(path)
        if "<hierarchy" not in text or package_name not in text:
            failures.append(f"UI XML evidence is missing hierarchy/package markers: {display_path(path, root)}")


def validate_zero_byte(path: Path, failures: list[str], root: Path = ROOT) -> None:
    if not path.exists():
        failures.append(f"missing zero-match log gate file: {display_path(path, root)}")
        return
    if path.stat().st_size != 0:
        failures.append(f"expected empty zero-match log gate file: {display_path(path, root)}")


def validate_allowed_crash_log(
    directory: Path,
    packages: tuple[str, ...],
    failures: list[str],
    package_name: str,
    root: Path = ROOT,
) -> None:
    crash_log = directory / "crash.log"
    if not crash_log.exists():
        return
    text = read_text(crash_log)
    if package_name in text:
        failures.append(f"crash log contains app package: {display_path(crash_log, root)}")
    if text.strip() and not any(package in text for package in packages):
        failures.append(f"crash log has content outside allowed emulator packages: {display_path(crash_log, root)}")


def validate_snippets(
    path: Path,
    snippets: tuple[str, ...],
    failures: list[str],
    package_name: str,
    root: Path = ROOT,
) -> None:
    if not path.exists():
        failures.append(f"missing snippet evidence file: {display_path(path, root)}")
        return
    text = read_text(path)
    for snippet in snippets:
        expected = resolve_marker(snippet, package_name)
        if expected not in text:
            failures.append(f"{display_path(path, root)} is missing evidence marker: {expected}")


def qa_evidence_failures(
    root: Path = ROOT,
    evidence_sets: tuple[EvidenceSet, ...] = EVIDENCE_SETS,
    package_name: str | None = None,
) -> tuple[list[str], int, int]:
    failures: list[str] = []
    pair_count = 0
    zero_gate_count = 0
    if package_name is None:
        try:
            package_name = current_package_name()
        except (OSError, ValueError) as exc:
            return [f"release identity could not be read from Gradle: {exc}"], 0, 0

    for evidence in evidence_sets:
        report = root / evidence.report
        directory = root / evidence.directory

        validate_file(report, failures, min_bytes=300, root=root)
        validate_snippets(report, evidence.report_snippets, failures, package_name, root=root)

        if not directory.exists() or not directory.is_dir():
            failures.append(f"missing evidence directory: {evidence.directory}")
            continue

        for stem in evidence.pairs:
            validate_xml(directory / f"{stem}.xml", failures, package_name, root=root)
            validate_png(directory / f"{stem}.png", failures, root=root)
            pair_count += 1

        for filename in evidence.files:
            validate_file(directory / filename, failures, root=root)

        for filename in evidence.zero_byte_files:
            validate_zero_byte(directory / filename, failures, root=root)
            zero_gate_count += 1

        for filename, snippets in evidence.snippets:
            validate_snippets(directory / filename, snippets, failures, package_name, root=root)

        validate_allowed_crash_log(directory, evidence.allow_crash_log_packages, failures, package_name, root=root)

    return failures, pair_count, zero_gate_count


def main() -> int:
    failures, pair_count, zero_gate_count = qa_evidence_failures()
    if failures:
        print("QA evidence check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print(
        "PASS: QA evidence covers "
        f"{len(EVIDENCE_SETS)} emulator reports, {pair_count} UI XML/PNG pairs "
        f"and {zero_gate_count} zero-match log gates"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
