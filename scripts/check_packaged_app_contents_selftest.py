#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "scripts/check_packaged_app_contents.py"

spec = importlib.util.spec_from_file_location("packaged_app_contents_checker", CHECKER_PATH)
assert spec is not None and spec.loader is not None
checker = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = checker
spec.loader.exec_module(checker)

REQUIRED_ENTRIES = (
    "AndroidManifest.xml",
    "classes.dex",
    "res/raw/tasks_ru.json",
)
REQUIRED_PREFIXES = (
    "lib/",
    "META-INF/androidx.compose.",
)


def assert_equal(actual: object, expected: object) -> None:
    assert actual == expected, f"expected {expected!r}, got {actual!r}"


def assert_failure_contains(failures: list[str], expected: str) -> None:
    assert any(expected in failure for failure in failures), failures


def write_zip(path: Path, entries: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        for name, content in entries.items():
            archive.writestr(name, content)


def artifact_spec(path: Path) -> object:
    return checker.ArtifactSpec(
        label="test APK",
        path=path,
        required_entries=REQUIRED_ENTRIES,
        required_prefixes=REQUIRED_PREFIXES,
    )


def valid_entries() -> dict[str, bytes]:
    return {
        "AndroidManifest.xml": b"manifest",
        "classes.dex": b"dex",
        "res/raw/tasks_ru.json": b"{}",
        "lib/arm64-v8a/libnative.so": b"native",
        "META-INF/androidx.compose.runtime": b"metadata",
    }


def failures_for_zip(entries: dict[str, bytes]) -> tuple[list[str], tuple[int, int]]:
    with tempfile.TemporaryDirectory() as tmp:
        artifact = Path(tmp) / "artifact.apk"
        write_zip(artifact, entries)
        failures: list[str] = []
        summary = checker.validate_artifact(artifact_spec(artifact), failures)
        return failures, summary


def test_valid_runtime_zip_passes() -> None:
    failures, summary = failures_for_zip(valid_entries())
    assert_equal(failures, [])
    assert_equal(summary[0], len(valid_entries()))
    assert summary[1] > 0


def test_missing_required_entry_fails() -> None:
    entries = valid_entries()
    del entries["res/raw/tasks_ru.json"]
    failures, _ = failures_for_zip(entries)
    assert_failure_contains(failures, "missing required entry: res/raw/tasks_ru.json")


def test_empty_required_entry_fails() -> None:
    entries = valid_entries()
    entries["classes.dex"] = b""
    failures, _ = failures_for_zip(entries)
    assert_failure_contains(failures, "required entry is empty: classes.dex")


def test_missing_required_prefix_fails() -> None:
    entries = valid_entries()
    del entries["lib/arm64-v8a/libnative.so"]
    failures, _ = failures_for_zip(entries)
    assert_failure_contains(failures, "missing required entry prefix: lib/")


def test_workspace_only_path_fragment_fails() -> None:
    entries = valid_entries()
    entries["assets/docs/release_report.md"] = b"report"
    failures, _ = failures_for_zip(entries)
    assert_failure_contains(failures, "workspace-only path fragment")


def test_forbidden_suffix_fails() -> None:
    entries = valid_entries()
    entries["assets/MainActivity.kt"] = b"source"
    failures, _ = failures_for_zip(entries)
    assert_failure_contains(failures, "forbidden source/secret-like suffix .kt")


def test_forbidden_basename_fails() -> None:
    entries = valid_entries()
    entries["assets/keystore.properties"] = b"signing"
    failures, _ = failures_for_zip(entries)
    assert_failure_contains(failures, "forbidden local config filename")


def test_bad_zip_fails_without_root_relative_path() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        artifact = Path(tmp) / "bad.apk"
        artifact.write_bytes(b"not a zip")
        failures: list[str] = []
        summary = checker.validate_artifact(artifact_spec(artifact), failures)

        assert_equal(summary, (0, 0))
        assert_failure_contains(failures, "not a readable ZIP artifact")


def test_empty_artifact_fails_without_root_relative_path() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        artifact = Path(tmp) / "empty.apk"
        artifact.write_bytes(b"")
        failures: list[str] = []
        summary = checker.validate_artifact(artifact_spec(artifact), failures)

        assert_equal(summary, (0, 0))
        assert_failure_contains(failures, "is empty")


def test_missing_artifact_fails_without_root_relative_path() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        artifact = Path(tmp) / "missing.apk"
        failures: list[str] = []
        summary = checker.validate_artifact(artifact_spec(artifact), failures)

        assert_equal(summary, (0, 0))
        assert_failure_contains(failures, "is missing")


def main() -> int:
    tests = [
        test_valid_runtime_zip_passes,
        test_missing_required_entry_fails,
        test_empty_required_entry_fails,
        test_missing_required_prefix_fails,
        test_workspace_only_path_fragment_fails,
        test_forbidden_suffix_fails,
        test_forbidden_basename_fails,
        test_bad_zip_fails_without_root_relative_path,
        test_empty_artifact_fails_without_root_relative_path,
        test_missing_artifact_fails_without_root_relative_path,
    ]
    for test in tests:
        test()
    print("PASS: packaged app contents checker self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
