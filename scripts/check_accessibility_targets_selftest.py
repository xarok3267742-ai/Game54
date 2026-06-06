#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import importlib.util
import io
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "scripts/check_accessibility_targets.py"

spec = importlib.util.spec_from_file_location("accessibility_targets_checker", CHECKER_PATH)
assert spec is not None and spec.loader is not None
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

VALID_COMPONENTS = """
@Composable
fun PrimaryAction(text: String, onClick: () -> Unit) {
    Button(
        modifier = Modifier.defaultMinSize(minHeight = 52.dp),
        onClick = onClick,
        colors = ButtonDefaults.buttonColors(
            containerColor = Sage,
            contentColor = MaterialTheme.colorScheme.onPrimary,
        ),
    ) {
        Text(text, color = MaterialTheme.colorScheme.onPrimary)
    }
}

@Composable
fun SecondaryAction(text: String, onClick: () -> Unit, enabled: Boolean = true) {
    OutlinedButton(
        modifier = Modifier.defaultMinSize(minHeight = 52.dp),
        onClick = onClick,
        enabled = enabled,
    ) {}
}

@Composable
fun ChoiceChip(text: String, selected: Boolean, onClick: () -> Unit) {
    Surface(
        modifier = Modifier
            .clickable(role = Role.Button, onClick = onClick)
            .semantics {
                this.selected = selected
                stateDescription = if (selected) "Выбрано" else "Не выбрано"
            }
            .defaultMinSize(minHeight = 48.dp),
    ) {}
}

@Composable
fun TopBar(onBack: () -> Unit) {
    Surface(
        modifier = Modifier
            .size(48.dp)
            .semantics { contentDescription = "Назад" }
            .clickable(role = Role.Button, onClick = onBack),
    ) {}
}
"""

VALID_APP = """
@Composable
private fun HeaderAction(label: String, icon: String, onAction: () -> Unit) {
    Surface(
        modifier = Modifier
            .defaultMinSize(minWidth = 48.dp, minHeight = 48.dp)
            .clickable(role = Role.Button, onClick = onAction)
            .clearAndSetSemantics {
                role = Role.Button
                contentDescription = label
                onClick(label) {
                    onAction()
                    true
                }
            },
    ) {}
}

@Composable
private fun SettingsScreen(preferences: AppPreferences, onHaptics: (Boolean) -> Unit) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .defaultMinSize(minHeight = 56.dp)
            .toggleable(
                value = preferences.settings.hapticsEnabled,
                role = Role.Switch,
                onValueChange = onHaptics,
            ),
    ) {
        Switch(
            checked = preferences.settings.hapticsEnabled,
            onCheckedChange = null,
        )
    }
}

@Composable
private fun TimerScreen(remainingSeconds: Int, running: Boolean, onToggle: () -> Unit) {
    val timerExpired = remainingSeconds == 0
    SecondaryAction(
        text = when {
            timerExpired -> "Время вышло"
            running -> "Пауза"
            else -> "Продолжить"
        },
        onClick = onToggle,
        enabled = !timerExpired,
    )
}
"""


def run_checker(
    tmp_path: Path,
    components_source: str = VALID_COMPONENTS,
    app_source: str = VALID_APP,
    accessibility_notes: str = "Touch targets are 48dp or larger.",
    ui_audit: str = "Tap targets: 48dp minimum.",
) -> tuple[int, str]:
    components = tmp_path / "AppComponents.kt"
    app = tmp_path / "PoryadokApp.kt"
    notes = tmp_path / "accessibility_notes.md"
    audit = tmp_path / "ui_audit.md"
    components.write_text(components_source, encoding="utf-8")
    app.write_text(app_source, encoding="utf-8")
    notes.write_text(accessibility_notes, encoding="utf-8")
    audit.write_text(ui_audit, encoding="utf-8")

    original_paths = (
        checker.COMPONENTS,
        checker.APP,
        checker.ACCESSIBILITY_NOTES,
        checker.UI_AUDIT,
    )
    checker.COMPONENTS = components
    checker.APP = app
    checker.ACCESSIBILITY_NOTES = notes
    checker.UI_AUDIT = audit

    stdout = io.StringIO()
    stderr = io.StringIO()
    try:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            status = checker.main()
    finally:
        (
            checker.COMPONENTS,
            checker.APP,
            checker.ACCESSIBILITY_NOTES,
            checker.UI_AUDIT,
        ) = original_paths

    return status, stdout.getvalue() + stderr.getvalue()


def assert_passes(status: int, output: str) -> None:
    assert status == 0, output


def assert_fails(status: int, output: str, expected: str) -> None:
    assert status != 0, output
    assert expected in output, output


def test_valid_fixture_passes(tmp_path: Path) -> None:
    status, output = run_checker(tmp_path)
    assert_passes(status, output)


def test_header_action_without_minimum_target_fails(tmp_path: Path) -> None:
    broken_app = VALID_APP.replace(
        ".defaultMinSize(minWidth = 48.dp, minHeight = 48.dp)",
        ".padding(horizontal = 12.dp, vertical = 10.dp)",
    )
    status, output = run_checker(tmp_path, app_source=broken_app)
    assert_fails(status, output, "HeaderAction must keep a minimum 48dp tap target")


def test_primary_action_without_on_primary_contrast_fails(tmp_path: Path) -> None:
    broken_components = VALID_COMPONENTS.replace(
        "contentColor = MaterialTheme.colorScheme.onPrimary,",
        "",
    )
    status, output = run_checker(tmp_path, components_source=broken_components)
    assert_fails(status, output, "PrimaryAction must set Material button content color to onPrimary for sage buttons")


def test_primary_action_without_explicit_label_contrast_fails(tmp_path: Path) -> None:
    broken_components = VALID_COMPONENTS.replace(
        "Text(text, color = MaterialTheme.colorScheme.onPrimary)",
        "Text(text)",
    )
    status, output = run_checker(tmp_path, components_source=broken_components)
    assert_fails(status, output, "PrimaryAction must explicitly render label text in onPrimary for contrast on sage buttons")


def test_secondary_action_without_enabled_state_fails(tmp_path: Path) -> None:
    broken_components = VALID_COMPONENTS.replace(
        "fun SecondaryAction(text: String, onClick: () -> Unit, enabled: Boolean = true)",
        "fun SecondaryAction(text: String, onClick: () -> Unit)",
    ).replace(
        "        enabled = enabled,\n",
        "",
    )
    status, output = run_checker(tmp_path, components_source=broken_components)
    assert_fails(status, output, "SecondaryAction must expose enabled state for disabled timer controls")


def test_choice_chip_without_selected_semantics_fails(tmp_path: Path) -> None:
    broken_components = VALID_COMPONENTS.replace("                this.selected = selected\n", "")
    status, output = run_checker(tmp_path, components_source=broken_components)
    assert_fails(status, output, "ChoiceChip must expose selected state semantics")


def test_choice_chip_without_russian_state_description_fails(tmp_path: Path) -> None:
    broken_components = VALID_COMPONENTS.replace(
        '                stateDescription = if (selected) "Выбрано" else "Не выбрано"\n',
        "",
    )
    status, output = run_checker(tmp_path, components_source=broken_components)
    assert_fails(status, output, "ChoiceChip must expose Russian selected/unselected state descriptions")


def test_header_action_without_button_role_fails(tmp_path: Path) -> None:
    broken_app = VALID_APP.replace(".clickable(role = Role.Button, onClick = onAction)", "")
    status, output = run_checker(tmp_path, app_source=broken_app)
    assert_fails(status, output, "HeaderAction must remain an explicit clickable top action with button role")


def test_back_action_without_russian_label_fails(tmp_path: Path) -> None:
    broken_components = VALID_COMPONENTS.replace('contentDescription = "Назад"', "")
    status, output = run_checker(tmp_path, components_source=broken_components)
    assert_fails(status, output, "TopBar back action must expose a Russian content description")


def test_header_action_without_accessible_label_fails(tmp_path: Path) -> None:
    broken_app = VALID_APP.replace("contentDescription = label", "")
    status, output = run_checker(tmp_path, app_source=broken_app)
    assert_fails(status, output, "HeaderAction must expose its Russian label as a content description")


def test_header_action_without_accessible_click_action_fails(tmp_path: Path) -> None:
    broken_app = VALID_APP.replace("onClick(label)", "onClick(\"Открыть\")")
    status, output = run_checker(tmp_path, app_source=broken_app)
    assert_fails(status, output, "HeaderAction must expose an accessible click action label")


def test_settings_haptics_without_full_row_toggle_fails(tmp_path: Path) -> None:
    broken_app = VALID_APP.replace(".toggleable(", ".clickable(")
    status, output = run_checker(tmp_path, app_source=broken_app)
    assert_fails(status, output, "Settings haptics row must expose a full-row switch toggle target")


def test_settings_haptics_without_display_only_switch_fails(tmp_path: Path) -> None:
    broken_app = VALID_APP.replace("onCheckedChange = null", "onCheckedChange = onHaptics")
    status, output = run_checker(tmp_path, app_source=broken_app)
    assert_fails(status, output, "Settings haptics Switch must be display-only so the row owns toggle semantics")


def test_timer_without_expired_disabled_state_fails(tmp_path: Path) -> None:
    broken_app = VALID_APP.replace("        enabled = !timerExpired,\n", "")
    status, output = run_checker(tmp_path, app_source=broken_app)
    assert_fails(status, output, "TimerScreen pause/resume control must be disabled after time expires")


def test_timer_without_expired_label_fails(tmp_path: Path) -> None:
    broken_app = VALID_APP.replace('            timerExpired -> "Время вышло"\n', "")
    status, output = run_checker(tmp_path, app_source=broken_app)
    assert_fails(status, output, "TimerScreen pause/resume control must show a clear expired label at zero")


def test_docs_without_target_size_fail(tmp_path: Path) -> None:
    status, output = run_checker(tmp_path, accessibility_notes="Touch target notes.")
    assert_fails(status, output, "must document 48dp minimum tap targets")


def main() -> int:
    tests = [
        test_valid_fixture_passes,
        test_header_action_without_minimum_target_fails,
        test_primary_action_without_on_primary_contrast_fails,
        test_primary_action_without_explicit_label_contrast_fails,
        test_secondary_action_without_enabled_state_fails,
        test_choice_chip_without_selected_semantics_fails,
        test_choice_chip_without_russian_state_description_fails,
        test_header_action_without_button_role_fails,
        test_back_action_without_russian_label_fails,
        test_header_action_without_accessible_label_fails,
        test_header_action_without_accessible_click_action_fails,
        test_settings_haptics_without_full_row_toggle_fails,
        test_settings_haptics_without_display_only_switch_fails,
        test_timer_without_expired_disabled_state_fails,
        test_timer_without_expired_label_fails,
        test_docs_without_target_size_fail,
    ]
    for test in tests:
        with tempfile.TemporaryDirectory() as tmp_dir:
            test(Path(tmp_dir))
    print("PASS: accessibility target checker self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
