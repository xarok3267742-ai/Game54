#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "scripts/check_task_catalog_quality.py"

spec = importlib.util.spec_from_file_location("task_catalog_quality_checker", CHECKER_PATH)
assert spec is not None and spec.loader is not None
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def assert_equal(actual: object, expected: object) -> None:
    assert actual == expected, f"expected {expected!r}, got {actual!r}"


def assert_failure_contains(failures: list[str], expected: str) -> None:
    assert any(expected in failure for failure in failures), failures


def task(
    *,
    area: str = "Home",
    number: int = 1,
    energy: str = "Light",
    minutes: int = 5,
    title_suffix: str = "",
) -> dict[str, object]:
    prefix = checker.AREA_PREFIXES[area]
    return {
        "id": f"{prefix}_{number:03d}",
        "area": area,
        "energy": energy,
        "minutes": minutes,
        "title": f"Убрать полку {number}{title_suffix}",
        "steps": [
            f"Освободите место номер {number}{title_suffix}.",
            f"Протрите поверхность номер {number}{title_suffix}.",
            f"Верните нужные вещи номер {number}{title_suffix}.",
        ],
        "resultText": f"Зона номер {number}{title_suffix} стала заметно спокойнее.",
    }


def valid_catalog() -> list[dict[str, object]]:
    catalog: list[dict[str, object]] = []
    energy_cycle = ["Light", "Medium", "Active", "Light", "Medium"]
    minute_cycle = [3, 5, 10, 3, 5]
    for area_index, area in enumerate(checker.AREA_PREFIXES):
        for number in range(1, checker.EXPECTED_TASKS_PER_AREA + 1):
            cycle_index = (number + area_index) % len(energy_cycle)
            catalog.append(
                task(
                    area=area,
                    number=number,
                    energy=energy_cycle[cycle_index],
                    minutes=minute_cycle[cycle_index],
                    title_suffix=f" {area_index}",
                )
            )
    return catalog


def check_catalog(catalog: list[object]) -> list[str]:
    failures: list[str] = []
    checked = [
        checked_task
        for index, raw_task in enumerate(catalog)
        if (checked_task := checker.check_task(index, raw_task, failures)) is not None
    ]
    checker.check_distribution(checked, failures)
    return failures


def test_valid_catalog_passes() -> None:
    failures = check_catalog(valid_catalog())
    assert_equal(failures, [])


def test_missing_key_fails() -> None:
    catalog = valid_catalog()
    del catalog[0]["resultText"]
    assert_failure_contains(check_catalog(catalog), "missing keys")


def test_id_prefix_mismatch_fails() -> None:
    catalog = valid_catalog()
    catalog[0]["id"] = "work_001"
    assert_failure_contains(check_catalog(catalog), "id prefix must match area")


def test_non_integer_minutes_fails() -> None:
    catalog = valid_catalog()
    catalog[0]["minutes"] = "5"
    assert_failure_contains(check_catalog(catalog), "minutes must be an integer")


def test_latin_text_fails() -> None:
    catalog = valid_catalog()
    catalog[0]["title"] = "Clean shelf now"
    failures = check_catalog(catalog)
    assert_failure_contains(failures, "must contain Cyrillic text")
    assert_failure_contains(failures, "must not contain Latin letters")


def test_result_without_punctuation_fails() -> None:
    catalog = valid_catalog()
    catalog[0]["resultText"] = "Зона стала заметно спокойнее"
    assert_failure_contains(check_catalog(catalog), "must end with sentence punctuation")


def test_repeated_step_fails() -> None:
    catalog = valid_catalog()
    catalog[0]["steps"] = [
        "Протрите поверхность аккуратно.",
        "Протрите поверхность аккуратно.",
        "Верните нужные вещи спокойно.",
    ]
    assert_failure_contains(check_catalog(catalog), "steps must not repeat within one task")


def test_duplicate_title_fails() -> None:
    catalog = valid_catalog()
    catalog[1]["title"] = catalog[0]["title"]
    assert_failure_contains(check_catalog(catalog), "duplicate task titles detected")


def test_area_count_fails() -> None:
    catalog = valid_catalog()
    catalog.pop()
    assert_failure_contains(check_catalog(catalog), "area Personal has 15 tasks")


def test_sequential_id_gap_fails() -> None:
    catalog = valid_catalog()
    catalog[0]["id"] = "home_099"
    assert_failure_contains(check_catalog(catalog), "ids must be sequential")


def test_draft_marker_fails() -> None:
    catalog = valid_catalog()
    catalog[0]["title"] = "Убрать полку " + ("TO" + "DO")
    assert_failure_contains(check_catalog(catalog), "contains a draft marker")


def test_load_catalog_temp_missing_path_fails() -> None:
    original_catalog = checker.CATALOG
    try:
        with tempfile.TemporaryDirectory() as tmp:
            checker.CATALOG = Path(tmp) / "missing.json"
            failures: list[str] = []
            assert_equal(checker.load_catalog(failures), [])
            assert_failure_contains(failures, "missing task catalog")
    finally:
        checker.CATALOG = original_catalog


def test_load_catalog_invalid_json_fails() -> None:
    original_catalog = checker.CATALOG
    try:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tasks.json"
            path.write_text("{bad json", encoding="utf-8")
            checker.CATALOG = path
            failures: list[str] = []
            assert_equal(checker.load_catalog(failures), [])
            assert_failure_contains(failures, "not valid JSON")
    finally:
        checker.CATALOG = original_catalog


def test_load_catalog_non_array_fails() -> None:
    original_catalog = checker.CATALOG
    try:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tasks.json"
            path.write_text(json.dumps({"tasks": []}), encoding="utf-8")
            checker.CATALOG = path
            failures: list[str] = []
            assert_equal(checker.load_catalog(failures), [])
            assert_failure_contains(failures, "root must be a JSON array")
    finally:
        checker.CATALOG = original_catalog


def main() -> int:
    tests = [
        test_valid_catalog_passes,
        test_missing_key_fails,
        test_id_prefix_mismatch_fails,
        test_non_integer_minutes_fails,
        test_latin_text_fails,
        test_result_without_punctuation_fails,
        test_repeated_step_fails,
        test_duplicate_title_fails,
        test_area_count_fails,
        test_sequential_id_gap_fails,
        test_draft_marker_fails,
        test_load_catalog_temp_missing_path_fails,
        test_load_catalog_invalid_json_fails,
        test_load_catalog_non_array_fails,
    ]
    for test in tests:
        test()
    print("PASS: task catalog quality checker self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
