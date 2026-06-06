#!/usr/bin/env python3
from __future__ import annotations

from check_header_icon_vectors import header_icon_failures

VALID_APP = """
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Settings
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.graphics.vector.path

private val StatsIcon: ImageVector = ImageVector.Builder(
    name = "StatsBars",
)

@Composable
private fun HomeScreen() {
    HeaderAction(label = "Итоги", icon = StatsIcon, onAction = onProgress)
    HeaderAction(label = "Опции", icon = Icons.Filled.Settings, onAction = onSettings)
}

@Composable
private fun ProgressScreen() {
    HeaderAction(label = "Опции", icon = Icons.Filled.Settings, onAction = onSettings)
}

@Composable
private fun HeaderAction(label: String, icon: ImageVector, onAction: () -> Unit) {
    Surface(
        modifier = Modifier.clearAndSetSemantics {
            contentDescription = label
            onClick(label) { true }
        },
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
        )
    }
}
"""

VALID_COMPONENTS = """
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack

@Composable
fun TopBar() {
    Surface(
        modifier = Modifier.semantics {
            contentDescription = "Назад"
        },
    ) {
        Icon(
            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
            contentDescription = null,
        )
    }
}
"""

VALID_GRADLE = """
dependencies {
    implementation("androidx.compose.material:material-icons-core")
}
"""

VALID_DOCS = {
    "docs/ui_audit.md": "StatsIcon covers HeaderAction and Назад.",
    "docs/accessibility_notes.md": "StatsIcon keeps content descriptions.",
    "docs/qa_test_plan.md": "check_header_icon_vectors.py verifies StatsIcon.",
}


def failures_for(
    app: str = VALID_APP,
    components: str = VALID_COMPONENTS,
    gradle: str = VALID_GRADLE,
    docs: dict[str, str] = VALID_DOCS,
) -> list[str]:
    return header_icon_failures(
        app_source=app,
        components_source=components,
        gradle_source=gradle,
        docs=docs,
    )


def assert_passes(failures: list[str]) -> None:
    assert failures == [], failures


def assert_fails(failures: list[str], expected: str) -> None:
    assert any(expected in failure for failure in failures), failures


def test_valid_fixture_passes() -> None:
    assert_passes(failures_for())


def test_text_check_icon_fails() -> None:
    broken = VALID_APP.replace("icon = StatsIcon", 'icon = "✓"', 1)
    assert_fails(failures_for(app=broken), "text glyph")


def test_progress_check_icon_regression_fails() -> None:
    broken = VALID_APP.replace("icon = StatsIcon", "icon = Icons.Filled.Check", 1)
    assert_fails(failures_for(app=broken), "stats vector")


def test_text_settings_icon_fails() -> None:
    broken = VALID_APP.replace("icon = Icons.Filled.Settings", 'icon = "⚙"')
    assert_fails(failures_for(app=broken), "text glyph")


def test_text_back_icon_fails() -> None:
    broken = VALID_COMPONENTS + '\nText("‹")\n'
    assert_fails(failures_for(components=broken), "text glyph")


def test_missing_dependency_fails() -> None:
    assert_fails(failures_for(gradle="dependencies {}"), "dependency")


def test_header_action_text_renderer_fails() -> None:
    broken = VALID_APP.replace(
        "Icon(\n            imageVector = icon,\n            contentDescription = null,\n        )",
        'Text("icon")',
    )
    assert_fails(failures_for(app=broken), "HeaderAction should render Icon")


def test_missing_docs_fails() -> None:
    docs = dict(VALID_DOCS)
    docs["docs/ui_audit.md"] = "HeaderAction."
    assert_fails(failures_for(docs=docs), "docs/ui_audit.md")


def main() -> int:
    test_valid_fixture_passes()
    test_text_check_icon_fails()
    test_progress_check_icon_regression_fails()
    test_text_settings_icon_fails()
    test_text_back_icon_fails()
    test_missing_dependency_fails()
    test_header_action_text_renderer_fails()
    test_missing_docs_fails()
    print("PASS: header icon vector checker self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
