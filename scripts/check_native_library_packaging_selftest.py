#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "scripts/check_native_library_packaging.py"

spec = importlib.util.spec_from_file_location("native_library_packaging_checker", CHECKER_PATH)
assert spec is not None and spec.loader is not None
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def assert_equal(actual: object, expected: object) -> None:
    assert actual == expected, f"expected {expected!r}, got {actual!r}"


def assert_failure_contains(failures: list[str], expected: str) -> None:
    assert any(expected in failure for failure in failures), failures


def write_zip(path: Path, entries: list[tuple[str, bytes, int]]) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        for name, content, compression in entries:
            archive.writestr(name, content, compress_type=compression)


def test_native_libraries_filters_so_entries() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        apk = Path(tmp) / "app.apk"
        write_zip(
            apk,
            [
                ("lib/arm64-v8a/libkeep.so", b"native", zipfile.ZIP_STORED),
                ("lib/arm64-v8a/readme.txt", b"text", zipfile.ZIP_STORED),
                ("assets/libignored.so", b"asset", zipfile.ZIP_STORED),
            ],
        )

        entries = checker.native_libraries(apk)

        assert_equal([entry.filename for entry in entries], ["lib/arm64-v8a/libkeep.so"])
        assert_equal(checker.verify_native_entries(apk, "apk"), [])


def test_compressed_native_library_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        apk = Path(tmp) / "compressed.apk"
        write_zip(apk, [("lib/arm64-v8a/libbad.so", b"native", zipfile.ZIP_DEFLATED)])

        assert_failure_contains(checker.verify_native_entries(apk, "apk"), "compressed")


def test_empty_native_library_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        apk = Path(tmp) / "empty.apk"
        write_zip(apk, [("lib/arm64-v8a/libempty.so", b"", zipfile.ZIP_STORED)])

        assert_failure_contains(checker.verify_native_entries(apk, "apk"), "empty")


def test_zipalign_success_requires_status_and_message() -> None:
    assert_equal(checker.zipalign_failures(0, "Verification successful\n", "apk"), [])
    assert_failure_contains(checker.zipalign_failures(1, "bad alignment\n", "apk"), "zipalign -P 16")
    assert_failure_contains(checker.zipalign_failures(0, "unexpected output\n", "apk"), "zipalign -P 16")


def test_extract_universal_apk_passes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        temp_dir = Path(tmp)
        apks = temp_dir / "release.apks"
        write_zip(apks, [("universal.apk", b"apk", zipfile.ZIP_STORED)])

        extracted = checker.extract_universal_apk(apks, temp_dir / "out")

        assert_equal(extracted.read_bytes(), b"apk")


def test_extract_universal_apk_missing_entry_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        temp_dir = Path(tmp)
        apks = temp_dir / "missing.apks"
        write_zip(apks, [("toc.pb", b"toc", zipfile.ZIP_STORED)])

        try:
            checker.extract_universal_apk(apks, temp_dir / "out")
        except RuntimeError as exc:
            assert "universal.apk" in str(exc), exc
            return
        raise AssertionError("missing universal.apk should fail")


def test_extract_universal_apk_empty_entry_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        temp_dir = Path(tmp)
        apks = temp_dir / "empty.apks"
        write_zip(apks, [("universal.apk", b"", zipfile.ZIP_STORED)])

        try:
            checker.extract_universal_apk(apks, temp_dir / "out")
        except RuntimeError as exc:
            assert "empty" in str(exc), exc
            return
        raise AssertionError("empty universal.apk should fail")


def main() -> int:
    tests = [
        test_native_libraries_filters_so_entries,
        test_compressed_native_library_fails,
        test_empty_native_library_fails,
        test_zipalign_success_requires_status_and_message,
        test_extract_universal_apk_passes,
        test_extract_universal_apk_missing_entry_fails,
        test_extract_universal_apk_empty_entry_fails,
    ]
    for test in tests:
        test()
    print("PASS: native library packaging checker self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
