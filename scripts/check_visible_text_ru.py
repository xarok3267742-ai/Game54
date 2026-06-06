#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

VISIBLE_CALLS = {
    "Text",
    "PrimaryAction",
    "SecondaryAction",
    "ChoiceChip",
    "MetricPill",
    "StepRow",
    "TopBar",
    "HeaderAction",
    "LoadingState",
}

KOTLIN_VISIBLE_FILES = [
    ROOT / "app/src/main/java/ru/poryadok5/app/MainActivity.kt",
    ROOT / "app/src/main/java/ru/poryadok5/app/ui/PoryadokApp.kt",
    ROOT / "app/src/main/java/ru/poryadok5/app/ui/components/AppComponents.kt",
]

MODEL_FILE = ROOT / "app/src/main/java/ru/poryadok5/app/domain/Models.kt"
STRINGS_XML = ROOT / "app/src/main/res/values/strings.xml"

STRING_RE = re.compile(r'"((?:\\.|[^"\\])*)"')
LATIN_RE = re.compile(r"[A-Za-z]")
CYRILLIC_RE = re.compile(r"[А-Яа-яЁё]")
CALL_START_RE = re.compile(r"\b(" + "|".join(sorted(VISIBLE_CALLS)) + r")\s*\(")


def strip_kotlin_interpolation(value: str) -> str:
    value = re.sub(r"\$\{[^}]*}", "", value)
    value = re.sub(r"\$[A-Za-z_][A-Za-z0-9_]*", "", value)
    return value


def decode_kotlin_string(value: str) -> str:
    return (
        value.replace(r"\n", "\n")
        .replace(r"\"", '"')
        .replace(r"\\", "\\")
    )


def has_language_letters(value: str) -> bool:
    return bool(LATIN_RE.search(value) or CYRILLIC_RE.search(value))


def validate_visible_string(source: str, line_number: int, value: str, failures: list[str]) -> None:
    cleaned = strip_kotlin_interpolation(decode_kotlin_string(value)).strip()
    if not cleaned or not has_language_letters(cleaned):
        return

    if LATIN_RE.search(cleaned):
        failures.append(f"{source}:{line_number}: visible text contains Latin letters: {cleaned!r}")
        return

    if not CYRILLIC_RE.search(cleaned):
        failures.append(f"{source}:{line_number}: visible text has no Cyrillic letters: {cleaned!r}")


def paren_delta(line: str) -> int:
    sanitized = STRING_RE.sub('""', line)
    return sanitized.count("(") - sanitized.count(")")


def scan_visible_call_text(source: str, text: str, failures: list[str]) -> None:
    lines = text.splitlines()
    active_depth = 0

    for index, line in enumerate(lines, start=1):
        starts_call = bool(CALL_START_RE.search(line))
        if starts_call and active_depth == 0:
            active_depth = paren_delta(line)
            scan_line = True
        elif active_depth > 0:
            scan_line = True
            active_depth += paren_delta(line)
        else:
            scan_line = False

        if scan_line:
            for match in STRING_RE.finditer(line):
                validate_visible_string(source, index, match.group(1), failures)

        if active_depth <= 0:
            active_depth = 0


def scan_visible_calls(path: Path, failures: list[str]) -> None:
    relative = path.relative_to(ROOT)
    scan_visible_call_text(str(relative), path.read_text(encoding="utf-8"), failures)


def scan_model_label_text(source: str, text: str, failures: list[str]) -> None:
    for index, line in enumerate(text.splitlines(), start=1):
        if line.strip().startswith(("Home(", "Work(", "Digital(", "Kitchen(", "Personal(", "Light(", "Medium(", "Active(")):
            for match in STRING_RE.finditer(line):
                validate_visible_string(source, index, match.group(1), failures)


def scan_model_labels(failures: list[str]) -> None:
    relative = MODEL_FILE.relative_to(ROOT)
    scan_model_label_text(str(relative), MODEL_FILE.read_text(encoding="utf-8"), failures)


def scan_strings_xml_text(source: str, text: str, failures: list[str]) -> None:
    for index, line in enumerate(text.splitlines(), start=1):
        if "<string" not in line:
            continue
        text_value = re.sub(r"<[^>]+>", "", line).strip()
        validate_visible_string(source, index, text_value, failures)


def scan_strings_xml(failures: list[str]) -> None:
    relative = STRINGS_XML.relative_to(ROOT)
    scan_strings_xml_text(str(relative), STRINGS_XML.read_text(encoding="utf-8"), failures)


def visible_text_failures() -> list[str]:
    failures: list[str] = []

    for path in KOTLIN_VISIBLE_FILES:
        scan_visible_calls(path, failures)
    scan_model_labels(failures)
    scan_strings_xml(failures)

    return failures


def main() -> int:
    failures = visible_text_failures()

    if failures:
        print("Visible Russian text check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: visible app text is Russian")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
