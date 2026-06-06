#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app/src/main/java/ru/poryadok5/app/ui/PoryadokApp.kt"
UI_AUDIT = ROOT / "docs/ui_audit.md"
QA_PLAN = ROOT / "docs/qa_test_plan.md"

BADGE_LABELS: tuple[str, ...] = (
    "Без интернета",
    "Без аккаунта",
    "Без рекламы",
    "Без аналитики",
)

BADGE_DETAILS: tuple[str, ...] = (
    "работает офлайн",
    "вход не нужен",
    "нет баннеров",
    "нет трекеров",
)


def function_body(source: str, name: str) -> str:
    marker = f"fun {name}("
    start = source.find(marker)
    if start < 0:
        return ""
    next_match = re.search(r"\n@Composable\n(?:private\s+)?fun\s+", source[start + len(marker):])
    if next_match is None:
        return source[start:]
    return source[start:start + len(marker) + next_match.start()]


def settings_privacy_summary_failures(
    app_source: str | None = None,
    doc_sources: dict[Path, str] | None = None,
) -> list[str]:
    failures: list[str] = []

    if app_source is None:
        if not APP.exists():
            return [f"missing app file: {APP.relative_to(ROOT)}"]
        app_source = APP.read_text(encoding="utf-8")

    settings_screen = function_body(app_source, "SettingsScreen")
    badge_grid = function_body(app_source, "PrivacyBadgeGrid")
    badge_component = function_body(app_source, "PrivacyBadge")

    if not settings_screen:
        failures.append("SettingsScreen body was not found")
    else:
        if 'Text("Приватность"' not in settings_screen:
            failures.append("Settings privacy card is missing the Приватность title")
        if "PrivacyBadgeGrid()" not in settings_screen:
            failures.append("Settings privacy card must call PrivacyBadgeGrid")
        if "Прогресс хранится только на устройстве" not in settings_screen:
            failures.append("Settings privacy copy must say progress stays on device")
        if "Игра" in settings_screen or "игра" in settings_screen:
            failures.append("Settings privacy copy must describe the product as an app, not a game")

    if not badge_grid:
        failures.append("PrivacyBadgeGrid component is missing")
    else:
        if badge_grid.count("Row(horizontalArrangement = Arrangement.spacedBy(8.dp))") < 2:
            failures.append("PrivacyBadgeGrid should use two compact rows for four status facts")
        for label, detail in zip(BADGE_LABELS, BADGE_DETAILS):
            if f'PrivacyBadge("{label}", "{detail}"' not in badge_grid:
                failures.append(f"PrivacyBadgeGrid is missing fact: {label} / {detail}")

    if not badge_component:
        failures.append("PrivacyBadge component is missing")
    else:
        for marker in (
            ".defaultMinSize(minHeight = 56.dp)",
            "padding(horizontal = 4.dp, vertical = 6.dp)",
            "Arrangement.spacedBy(8.dp)",
            "verticalAlignment = Alignment.Top",
            ".padding(top = 8.dp)",
            ".background(Sage, CircleShape)",
            "style = MaterialTheme.typography.labelLarge",
            "style = MaterialTheme.typography.bodySmall",
            "color = MutedText",
        ):
            if marker not in badge_component:
                failures.append(f"PrivacyBadge is missing marker: {marker}")
        for marker in (
            "Surface(",
            "border =",
            "BorderStroke(",
            "MaterialTheme.shapes.small",
            "MaterialTheme.colorScheme.surface",
        ):
            if marker in badge_component:
                failures.append(f"PrivacyBadge must stay unframed inside the privacy card: {marker}")
        for marker in (".clickable(", "Role.Button", "onClick"):
            if marker in badge_component:
                failures.append(f"PrivacyBadge must stay non-interactive: {marker}")

    doc_sources = doc_sources or {}
    for path, markers in (
        (UI_AUDIT, ("PrivacyBadgeGrid", "unframed", "работает офлайн", "нет трекеров")),
        (QA_PLAN, ("check_settings_privacy_summary.py", "unframed", "вход не нужен", "нет баннеров")),
    ):
        if path in doc_sources:
            text = doc_sources[path]
        elif path.exists():
            text = path.read_text(encoding="utf-8")
        else:
            failures.append(f"missing documentation file: {path.relative_to(ROOT)}")
            continue
        for marker in markers:
            if marker not in text:
                failures.append(f"{path.relative_to(ROOT)} is missing marker: {marker}")

    return failures


def main() -> int:
    failures = settings_privacy_summary_failures()
    if failures:
        print("Settings privacy summary check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: Settings privacy summary is scannable and app-specific")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
