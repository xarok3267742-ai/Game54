#!/usr/bin/env python3
from __future__ import annotations

import unittest

from check_home_action_icons import home_action_icon_failures

VALID_APP = """
import androidx.compose.material.icons.automirrored.filled.List
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Refresh

@Composable
private fun HomeScreen() {
    PrimaryAction(
        text = "Запустить таймер",
        onClick = onStartTask,
        icon = Icons.Filled.PlayArrow,
    )
    SecondaryAction(
        text = "Другая задача",
        onClick = onSkipTask,
        icon = Icons.Filled.Refresh,
    )
    SecondaryAction(
        text = "Все шаги",
        onClick = onOpenTask,
        icon = Icons.AutoMirrored.Filled.List,
    )
}

@Composable
private fun TaskDetailsScreen() {}
"""

VALID_COMPONENTS = """
@Composable
fun PrimaryAction(icon: ImageVector? = null) {
    if (icon != null) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            modifier = Modifier.size(20.dp),
        )
        Spacer(Modifier.width(8.dp))
    }
}

@Composable
fun SecondaryAction(icon: ImageVector? = null) {
    if (icon != null) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            modifier = Modifier.size(20.dp),
        )
        Spacer(Modifier.width(8.dp))
    }
}

@Composable
fun DangerAction() {}
"""

VALID_DOCS = {
    "docs/product_spec.md": "Home uses decorative action icons for Запустить таймер.",
    "docs/ui_audit.md": "Home action icons use PlayArrow, Refresh and List.",
    "docs/accessibility_notes.md": "Home action icons are decorative and keep text labels.",
    "docs/qa_test_plan.md": "check_home_action_icons.py verifies Home action icons.",
}


def assert_passes(failures: list[str]) -> None:
    if failures:
        raise AssertionError("expected no failures, got: " + "; ".join(failures))


def assert_fails(failures: list[str], marker: str) -> None:
    if not any(marker in failure for failure in failures):
        raise AssertionError(f"expected failure containing {marker!r}, got: {failures!r}")


class HomeActionIconsSelfTest(unittest.TestCase):
    def test_valid_fixture_passes(self) -> None:
        assert_passes(home_action_icon_failures(app_source=VALID_APP, components_source=VALID_COMPONENTS, docs=VALID_DOCS))

    def test_missing_primary_icon_fails(self) -> None:
        broken = VALID_APP.replace("icon = Icons.Filled.PlayArrow,", "")
        assert_fails(home_action_icon_failures(app_source=broken, components_source=VALID_COMPONENTS, docs=VALID_DOCS), "PlayArrow")

    def test_missing_secondary_icon_fails(self) -> None:
        broken = VALID_APP.replace("icon = Icons.Filled.Refresh,", "")
        assert_fails(home_action_icon_failures(app_source=broken, components_source=VALID_COMPONENTS, docs=VALID_DOCS), "Refresh")

    def test_accessible_button_text_must_remain(self) -> None:
        broken = VALID_APP.replace('text = "Все шаги"', 'text = ""')
        assert_fails(home_action_icon_failures(app_source=broken, components_source=VALID_COMPONENTS, docs=VALID_DOCS), "Все шаги")

    def test_icon_must_be_decorative(self) -> None:
        broken = VALID_COMPONENTS.replace("contentDescription = null", "contentDescription = text", 1)
        assert_fails(home_action_icon_failures(app_source=VALID_APP, components_source=broken, docs=VALID_DOCS), "decorative")

    def test_missing_component_icon_spacing_fails(self) -> None:
        broken = VALID_COMPONENTS.replace("Spacer(Modifier.width(8.dp))", "")
        assert_fails(home_action_icon_failures(app_source=VALID_APP, components_source=broken, docs=VALID_DOCS), "Spacer")

    def test_missing_docs_fail(self) -> None:
        docs = dict(VALID_DOCS)
        docs["docs/ui_audit.md"] = "Home action icons."
        assert_fails(home_action_icon_failures(app_source=VALID_APP, components_source=VALID_COMPONENTS, docs=docs), "docs/ui_audit.md")


if __name__ == "__main__":
    unittest.main(verbosity=2)
