#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "scripts/check_visible_text_ru.py"

spec = importlib.util.spec_from_file_location("visible_text_ru_checker", CHECKER_PATH)
assert spec is not None and spec.loader is not None
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def assert_equal(actual: object, expected: object) -> None:
    assert actual == expected, f"expected {expected!r}, got {actual!r}"


def assert_failure_contains(failures: list[str], expected: str) -> None:
    assert any(expected in failure for failure in failures), failures


def kotlin_failures(text: str) -> list[str]:
    failures: list[str] = []
    checker.scan_visible_call_text("Fixture.kt", text, failures)
    return failures


def model_failures(text: str) -> list[str]:
    failures: list[str] = []
    checker.scan_model_label_text("Models.kt", text, failures)
    return failures


def strings_failures(text: str) -> list[str]:
    failures: list[str] = []
    checker.scan_strings_xml_text("strings.xml", text, failures)
    return failures


def test_cyrillic_visible_text_passes() -> None:
    assert_equal(kotlin_failures('Text("Порядок на столе")'), [])


def test_interpolated_cyrillic_text_passes() -> None:
    assert_equal(kotlin_failures('Text("Осталось ${seconds} секунд")'), [])


def test_numeric_visible_text_is_ignored() -> None:
    assert_equal(kotlin_failures('MetricPill("5")'), [])


def test_non_visible_latin_string_is_ignored() -> None:
    assert_equal(kotlin_failures('val route = "HomeScreen"'), [])


def test_single_line_latin_visible_text_fails() -> None:
    failures = kotlin_failures('Text("Start cleaning")')
    assert_failure_contains(failures, "visible text contains Latin letters")


def test_multiline_latin_visible_text_fails() -> None:
    failures = kotlin_failures(
        """
PrimaryAction(
    text = "Start",
    onClick = {}
)
"""
    )
    assert_failure_contains(failures, "visible text contains Latin letters")


def test_model_label_latin_text_fails() -> None:
    failures = model_failures('Home("Home", "Дом")')
    assert_failure_contains(failures, "visible text contains Latin letters")


def test_strings_xml_latin_text_fails() -> None:
    failures = strings_failures('<string name="app_name">Poryadok 5</string>')
    assert_failure_contains(failures, "visible text contains Latin letters")


def main() -> int:
    tests = [
        test_cyrillic_visible_text_passes,
        test_interpolated_cyrillic_text_passes,
        test_numeric_visible_text_is_ignored,
        test_non_visible_latin_string_is_ignored,
        test_single_line_latin_visible_text_fails,
        test_multiline_latin_visible_text_fails,
        test_model_label_latin_text_fails,
        test_strings_xml_latin_text_fails,
    ]
    for test in tests:
        test()
    print("PASS: visible Russian text checker self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
