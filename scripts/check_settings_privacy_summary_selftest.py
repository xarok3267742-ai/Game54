#!/usr/bin/env python3
from __future__ import annotations

from check_settings_privacy_summary import QA_PLAN, UI_AUDIT, settings_privacy_summary_failures

VALID_APP = """
@Composable
private fun SettingsScreen() {
    AppCard(containerColor = SageSoft) {
        Text("Приватность", style = MaterialTheme.typography.titleLarge)
        Text("Прогресс хранится только на устройстве. Ничего не отправляем.", style = MaterialTheme.typography.bodyLarge)
        PrivacyBadgeGrid()
    }
}

@Composable
private fun PrivacyBadgeGrid() {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            PrivacyBadge("Без интернета", "работает офлайн", Modifier.weight(1f))
            PrivacyBadge("Без аккаунта", "вход не нужен", Modifier.weight(1f))
        }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            PrivacyBadge("Без рекламы", "нет баннеров", Modifier.weight(1f))
            PrivacyBadge("Без аналитики", "нет трекеров", Modifier.weight(1f))
        }
    }
}

@Composable
private fun PrivacyBadge(label: String, detail: String, modifier: Modifier = Modifier) {
    Row(
        modifier = modifier
            .defaultMinSize(minHeight = 56.dp)
            .padding(horizontal = 4.dp, vertical = 6.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalAlignment = Alignment.Top,
    ) {
        Box(
            modifier = Modifier
                .padding(top = 8.dp)
                .size(7.dp)
                .background(Sage, CircleShape),
        )
        Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
            Text(label, style = MaterialTheme.typography.labelLarge)
            Text(detail, style = MaterialTheme.typography.bodySmall, color = MutedText)
        }
    }
}

@Composable
private fun TaskCard() {}
"""

VALID_DOCS = {
    UI_AUDIT: "Settings uses unframed PrivacyBadgeGrid with работает офлайн and нет трекеров.",
    QA_PLAN: "check_settings_privacy_summary.py verifies unframed вход не нужен and нет баннеров.",
}


def failures_for(app: str = VALID_APP, docs: dict = VALID_DOCS) -> list[str]:
    return settings_privacy_summary_failures(app_source=app, doc_sources=docs)


def assert_passes(failures: list[str]) -> None:
    assert failures == [], failures


def assert_fails(failures: list[str], expected: str) -> None:
    assert any(expected in failure for failure in failures), failures


def test_valid_fixture_passes() -> None:
    assert_passes(failures_for())


def test_missing_badge_grid_fails() -> None:
    broken = VALID_APP.replace("        PrivacyBadgeGrid()\n", "")
    assert_fails(failures_for(app=broken), "PrivacyBadgeGrid")


def test_missing_badge_fails() -> None:
    broken = VALID_APP.replace('PrivacyBadge("Без аналитики", "нет трекеров", Modifier.weight(1f))', "")
    assert_fails(failures_for(app=broken), "Без аналитики")


def test_missing_badge_detail_fails() -> None:
    broken = VALID_APP.replace('"нет баннеров"', '"нет рекламы"')
    assert_fails(failures_for(app=broken), "нет баннеров")


def test_game_copy_fails() -> None:
    broken = VALID_APP.replace("Прогресс хранится", "Игра хранит прогресс")
    assert_fails(failures_for(app=broken), "app, not a game")


def test_missing_min_height_fails() -> None:
    broken = VALID_APP.replace(".defaultMinSize(minHeight = 56.dp)", ".defaultMinSize(minHeight = 32.dp)")
    assert_fails(failures_for(app=broken), "56.dp")


def test_framed_badge_fails() -> None:
    broken = VALID_APP.replace(
        "Row(\n        modifier = modifier",
        "Surface(\n        border = BorderStroke(1.dp, Sage.copy(alpha = 0.35f)),\n        modifier = modifier",
    )
    assert_fails(failures_for(app=broken), "unframed")


def test_interactive_badge_fails() -> None:
    broken = VALID_APP.replace(
        "verticalAlignment = Alignment.Top,",
        "verticalAlignment = Alignment.Top,\n        modifier = Modifier.clickable(onClick = {}),",
    )
    assert_fails(failures_for(app=broken), ".clickable(")


def test_missing_docs_fail() -> None:
    docs = dict(VALID_DOCS)
    docs[UI_AUDIT] = "Settings privacy is concise."
    assert_fails(failures_for(docs=docs), "docs/ui_audit.md")


def main() -> int:
    test_valid_fixture_passes()
    test_missing_badge_grid_fails()
    test_missing_badge_fails()
    test_missing_badge_detail_fails()
    test_game_copy_fails()
    test_missing_min_height_fails()
    test_framed_badge_fails()
    test_interactive_badge_fails()
    test_missing_docs_fail()
    print("PASS: Settings privacy summary checker self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
