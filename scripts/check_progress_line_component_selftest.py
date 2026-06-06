#!/usr/bin/env python3
from __future__ import annotations

from check_progress_line_component import ACCESSIBILITY_NOTES, QA_PLAN, UI_AUDIT, progress_line_failures

VALID_COMPONENTS = """
@Composable
fun ProgressLine(progress: Float) {
    val normalized = progress.coerceIn(0f, 1f)
    Box(
        modifier = Modifier
            .clip(MaterialTheme.shapes.extraSmall)
            .semantics {
                progressBarRangeInfo = ProgressBarRangeInfo(normalized, 0f..1f)
            },
    ) {
        if (normalized > 0f) {
            Box(Modifier.fillMaxWidth(normalized))
        }
    }
}
"""

VALID_APP = """
import ru.poryadok5.app.ui.components.ProgressLine

@Composable
private fun TimerScreen() {
    ProgressLine(
        progress = progress,
        trackColor = MaterialTheme.colorScheme.surface,
    )
}

@Composable
private fun ProgressScreen() {
    ProgressLine(progress = catalogPercent / 100f)
}

@Composable
private fun AreaProgressRow() {
    ProgressLine(progress = progress, height = 6.dp)
}
"""

VALID_DOCS = {
    UI_AUDIT: "ProgressLine убирает ложный end-dot у нулевых progress bars.",
    ACCESSIBILITY_NOTES: "ProgressLine exposes ProgressBarRangeInfo.",
    QA_PLAN: "check_progress_line_component.py проверяет ProgressLine.",
}


def failures_for(
    components: str = VALID_COMPONENTS,
    app: str = VALID_APP,
    docs: dict = VALID_DOCS,
) -> list[str]:
    return progress_line_failures(components_source=components, app_source=app, docs=docs)


def assert_passes(failures: list[str]) -> None:
    assert failures == [], failures


def assert_fails(failures: list[str], expected: str) -> None:
    assert any(expected in failure for failure in failures), failures


def test_valid_fixture_passes() -> None:
    assert_passes(failures_for())


def test_material_linear_progress_fails() -> None:
    broken = VALID_APP + "\nLinearProgressIndicator(progress = { progress })\n"
    assert_fails(failures_for(app=broken), "LinearProgressIndicator")


def test_missing_semantics_fails() -> None:
    broken = VALID_COMPONENTS.replace("progressBarRangeInfo = ProgressBarRangeInfo(normalized, 0f..1f)", "")
    assert_fails(failures_for(components=broken), "ProgressBarRangeInfo")


def test_missing_zero_guard_fails() -> None:
    broken = VALID_COMPONENTS.replace("if (normalized > 0f)", "if (normalized >= 0f)")
    assert_fails(failures_for(components=broken), "if (normalized > 0f)")


def test_area_row_missing_compact_height_fails() -> None:
    broken = VALID_APP.replace("ProgressLine(progress = progress, height = 6.dp)", "ProgressLine(progress = progress)")
    assert_fails(failures_for(app=broken), "height = 6.dp")


def test_missing_docs_fails() -> None:
    docs = dict(VALID_DOCS)
    docs[UI_AUDIT] = "ProgressLine проверен."
    assert_fails(failures_for(docs=docs), "docs/ui_audit.md")


def main() -> int:
    test_valid_fixture_passes()
    test_material_linear_progress_fails()
    test_missing_semantics_fails()
    test_missing_zero_guard_fails()
    test_area_row_missing_compact_height_fails()
    test_missing_docs_fails()
    print("PASS: ProgressLine checker self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
