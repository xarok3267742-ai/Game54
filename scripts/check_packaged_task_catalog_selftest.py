#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "scripts/check_packaged_task_catalog.py"

spec = importlib.util.spec_from_file_location("packaged_task_catalog_checker", CHECKER_PATH)
assert spec is not None and spec.loader is not None
checker = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = checker
spec.loader.exec_module(checker)

ENTRY = "res/raw/tasks_ru.json"


def assert_equal(actual: object, expected: object) -> None:
    assert actual == expected, f"expected {expected!r}, got {actual!r}"


def assert_failure_contains(failures: list[str], expected: str) -> None:
    assert any(expected in failure for failure in failures), failures


def catalog(task_count: int = 80, title_prefix: str = "Задача") -> list[dict[str, object]]:
    return [
        {
            "id": f"task_{index:03d}",
            "area": "Home",
            "energy": "Light",
            "minutes": 5,
            "title": f"{title_prefix} {index}",
            "steps": ["Шаг один", "Шаг два", "Шаг три"],
            "resultText": "Готово",
        }
        for index in range(1, task_count + 1)
    ]


def catalog_bytes(task_count: int = 80, title_prefix: str = "Задача") -> bytes:
    return json.dumps(catalog(task_count, title_prefix), ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def write_zip(path: Path, entries: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        for name, content in entries.items():
            archive.writestr(name, content)


def artifact(path: Path, entry: str = ENTRY) -> object:
    return checker.CatalogArtifact(label="test APK", path=path, entry=entry)


def test_valid_catalog_parses() -> None:
    failures: list[str] = []
    parsed = checker.parse_catalog(catalog_bytes(), "source", failures)
    assert_equal(len(parsed), 80)
    assert_equal(failures, [])


def test_invalid_json_fails() -> None:
    failures: list[str] = []
    parsed = checker.parse_catalog(b"{not json", "source", failures)
    assert_equal(parsed, [])
    assert_failure_contains(failures, "not valid UTF-8 JSON")


def test_non_array_catalog_fails() -> None:
    failures: list[str] = []
    parsed = checker.parse_catalog(b"{}", "source", failures)
    assert_equal(parsed, [])
    assert_failure_contains(failures, "root must be a JSON array")


def test_wrong_task_count_fails() -> None:
    failures: list[str] = []
    parsed = checker.parse_catalog(catalog_bytes(task_count=79), "source", failures)
    assert_equal(len(parsed), 79)
    assert_failure_contains(failures, "expected 80")


def test_read_zip_entry_passes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        zip_path = Path(tmp) / "artifact.apk"
        expected = catalog_bytes()
        write_zip(zip_path, {ENTRY: expected})
        failures: list[str] = []

        actual = checker.read_zip_entry(artifact(zip_path), failures)

        assert_equal(actual, expected)
        assert_equal(failures, [])


def test_missing_packaged_catalog_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        zip_path = Path(tmp) / "artifact.apk"
        write_zip(zip_path, {"assets/other.json": b"{}"})
        failures: list[str] = []

        actual = checker.read_zip_entry(artifact(zip_path), failures)

        assert_equal(actual, None)
        assert_failure_contains(failures, "missing packaged task catalog")


def test_unexpected_task_like_json_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        zip_path = Path(tmp) / "artifact.apk"
        write_zip(
            zip_path,
            {
                ENTRY: catalog_bytes(),
                "assets/tasks_debug.json": catalog_bytes(),
            },
        )
        failures: list[str] = []

        actual = checker.read_zip_entry(artifact(zip_path), failures)

        assert actual is not None
        assert_failure_contains(failures, "unexpected task-like JSON entries")


def test_bad_zip_fails_without_root_relative_path() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        zip_path = Path(tmp) / "bad.apk"
        zip_path.write_bytes(b"not a zip")
        failures: list[str] = []

        actual = checker.read_zip_entry(artifact(zip_path), failures)

        assert_equal(actual, None)
        assert_failure_contains(failures, "not a readable ZIP artifact")


def test_missing_artifact_fails_without_root_relative_path() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        zip_path = Path(tmp) / "missing.apk"
        failures: list[str] = []

        actual = checker.read_zip_entry(artifact(zip_path), failures)

        assert_equal(actual, None)
        assert_failure_contains(failures, "is missing")


def test_packaged_bytes_and_json_mismatch_are_detectable() -> None:
    source_bytes = catalog_bytes(title_prefix="Source")
    packaged_bytes = catalog_bytes(title_prefix="Packaged")
    failures: list[str] = []

    source_catalog = checker.parse_catalog(source_bytes, "source", failures)
    packaged_catalog = checker.parse_catalog(packaged_bytes, "test APK", failures)

    assert_equal(failures, [])
    assert source_bytes != packaged_bytes
    assert packaged_catalog != source_catalog


def main() -> int:
    tests = [
        test_valid_catalog_parses,
        test_invalid_json_fails,
        test_non_array_catalog_fails,
        test_wrong_task_count_fails,
        test_read_zip_entry_passes,
        test_missing_packaged_catalog_fails,
        test_unexpected_task_like_json_fails,
        test_bad_zip_fails_without_root_relative_path,
        test_missing_artifact_fails_without_root_relative_path,
        test_packaged_bytes_and_json_mismatch_are_detectable,
    ]
    for test in tests:
        test()
    print("PASS: packaged task catalog checker self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
