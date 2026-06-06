#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML_FILE = ROOT / "docs" / "privacy_policy_ru.html"

REQUIRED_SNIPPETS = (
    "Политика конфиденциальности: Порядок 5",
    "Дата обновления: 27 мая 2026",
    "не собирает и не передаёт персональные данные",
    "локальные настройки и прогресс",
    "не запрашивает runtime-разрешения Android",
    "не использует доступ к интернету",
    "не использует рекламу",
    "аналитические SDK",
    "crash-reporting SDK",
    "сбросить прогресс",
    "контактный email разработчика",
)

FORBIDDEN_PATTERNS = (
    r"<script\b",
    r"\bsrc\s*=\s*[\"']https?://",
    r"\bhref\s*=\s*[\"']https?://",
    r"googletagmanager",
    r"google-analytics",
    r"facebook",
    r"metrika",
    r"analytics",
)


class PrivacyPolicyParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.has_title = False
        self.has_h1 = False
        self.lang = ""
        self.external_refs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_map = {key: value or "" for key, value in attrs}
        if tag == "html":
            self.lang = attrs_map.get("lang", "")
        if tag == "title":
            self.has_title = True
        if tag == "h1":
            self.has_h1 = True
        for key in ("href", "src"):
            value = attrs_map.get(key, "")
            if value.startswith(("http://", "https://", "//")):
                self.external_refs.append(value)


def privacy_policy_failures(html: str) -> list[str]:
    lowered = html.lower()
    failures: list[str] = []

    parser = PrivacyPolicyParser()
    parser.feed(html)

    if parser.lang != "ru":
        failures.append("html lang must be ru")
    if not parser.has_title:
        failures.append("missing <title>")
    if not parser.has_h1:
        failures.append("missing <h1>")
    if parser.external_refs:
        failures.append(f"external references are not allowed: {parser.external_refs}")

    for snippet in REQUIRED_SNIPPETS:
        if snippet not in html:
            failures.append(f"missing required text: {snippet}")

    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, lowered):
            failures.append(f"forbidden pattern found: {pattern}")

    return failures


def main() -> int:
    if not HTML_FILE.exists():
        print(f"FAIL: privacy policy HTML is missing: {HTML_FILE}", file=sys.stderr)
        return 1

    html = HTML_FILE.read_text(encoding="utf-8")
    failures = privacy_policy_failures(html)

    if failures:
        print("Privacy policy HTML check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print(f"PASS: privacy policy HTML is self-contained and matches no-data-collection claims ({HTML_FILE})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
