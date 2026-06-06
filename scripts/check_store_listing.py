#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STORE_LISTING = ROOT / "docs" / "store_listing_ru.md"
SCREENSHOT_DIR = ROOT / "screenshots" / "play-store"

LIMITS = {
    "App Name": 30,
    "Short Description": 80,
    "Full Description": 4000,
    "Release Notes": 500,
}

REQUIRED_SECTIONS = (
    "App Name",
    "Short Description",
    "Full Description",
    "Release Notes",
    "Screenshot Captions",
    "Search Keywords",
)

FORBIDDEN_PATTERNS = (
    r"(?i)#\s*1",
    r"(?i)\bbest\s+of\s+play\b",
    r"(?i)\bapp\s+of\s+the\s+year\b",
    r"(?i)\bgoogle\s+play\s+badge\b",
    r"(?i)\bfree\s+for\s+a\s+limited\s+time\b",
    r"(?i)\bcash\s*back\b",
    r"(?i)\bguaranteed\b",
    r"(?i)\bguarantee\b",
    r"скидк",
    r"гарантир",
)


def parse_sections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current: str | None = None

    for line in text.splitlines():
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if match:
            current = match.group(1)
            sections[current] = []
            continue
        if current is not None:
            sections[current].append(line)

    return {key: "\n".join(value).strip() for key, value in sections.items()}


def visible_length(value: str) -> int:
    return len(value.strip())


def screenshot_count() -> int:
    if not SCREENSHOT_DIR.exists():
        return 0
    return len(sorted(SCREENSHOT_DIR.glob("*.png")))


def bullet_items(section: str) -> list[str]:
    return [
        line[2:].strip()
        for line in section.splitlines()
        if line.startswith("- ") and line[2:].strip()
    ]


def store_listing_failures(text: str, *, screenshot_total: int) -> tuple[list[str], dict[str, str], list[str]]:
    sections = parse_sections(text)
    failures: list[str] = []

    for section in REQUIRED_SECTIONS:
        if section not in sections or not sections[section].strip():
            failures.append(f"missing required section: {section}")

    for section, limit in LIMITS.items():
        value = sections.get(section, "")
        length = visible_length(value)
        if length == 0:
            continue
        if length > limit:
            failures.append(f"{section} is {length} characters; limit is {limit}")

    short_description = sections.get("Short Description", "").strip()
    full_description = sections.get("Full Description", "").strip()
    if short_description and full_description and short_description in full_description:
        failures.append("Full Description repeats the Short Description verbatim")

    captions = bullet_items(sections.get("Screenshot Captions", ""))
    if screenshot_total == 0:
        failures.append(f"no PNG screenshots found in {SCREENSHOT_DIR}")
    elif len(captions) != screenshot_total:
        failures.append(f"Screenshot Captions has {len(captions)} items, but {screenshot_total} screenshots exist")

    for index, caption in enumerate(captions, start=1):
        if visible_length(caption) > 80:
            failures.append(f"Screenshot caption {index} is longer than 80 characters")

    keywords = [item.strip() for item in sections.get("Search Keywords", "").split(",") if item.strip()]
    if len(keywords) < 5:
        failures.append("Search Keywords should include at least five relevant terms")
    if len(set(keyword.lower() for keyword in keywords)) != len(keywords):
        failures.append("Search Keywords contains duplicates")

    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, text):
            failures.append(f"store listing contains risky promotional or ranking claim: {pattern}")

    return failures, sections, captions


def main() -> int:
    if not STORE_LISTING.exists():
        print(f"FAIL: store listing draft is missing: {STORE_LISTING}", file=sys.stderr)
        return 1

    text = STORE_LISTING.read_text(encoding="utf-8")
    shots = screenshot_count()
    failures, sections, captions = store_listing_failures(text, screenshot_total=shots)

    if failures:
        print("Store listing check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print(
        "PASS: store listing fits Play field limits "
        f"(name {visible_length(sections['App Name'])}/30, "
        f"short {visible_length(sections['Short Description'])}/80, "
        f"full {visible_length(sections['Full Description'])}/4000, "
        f"release notes {visible_length(sections['Release Notes'])}/500, "
        f"captions {len(captions)}/{shots})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
