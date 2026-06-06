#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "scripts/check_play_store_icon.py"

spec = importlib.util.spec_from_file_location("play_store_icon_checker", CHECKER_PATH)
assert spec is not None and spec.loader is not None
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def assert_equal(actual: object, expected: object) -> None:
    assert actual == expected, f"expected {expected!r}, got {actual!r}"


def assert_failure_contains(failures: list[str], expected: str) -> None:
    assert any(expected in failure for failure in failures), failures


def png_header(width: int = 512, height: int = 512, bit_depth: int = 8, color_type: int = 6) -> bytes:
    return checker.PNG_SIGNATURE + b"\x00" * 8 + struct.pack(">IIBB", width, height, bit_depth, color_type) + b"\x00" * 32


def test_valid_rgba_512_icon_passes() -> None:
    assert_equal(checker.play_store_icon_failures(png_header()), [])


def test_non_png_fails() -> None:
    failures = checker.play_store_icon_failures(b"not a png")
    assert_failure_contains(failures, "file is not a PNG")


def test_short_png_header_fails() -> None:
    failures = checker.play_store_icon_failures(checker.PNG_SIGNATURE + b"\x00" * 4)
    assert_failure_contains(failures, "PNG header is too short")


def test_wrong_dimensions_fail() -> None:
    failures = checker.play_store_icon_failures(png_header(width=513, height=512))
    assert_failure_contains(failures, "dimensions are 513x512")


def test_rgb_png_fails() -> None:
    failures = checker.play_store_icon_failures(png_header(color_type=2))
    assert_failure_contains(failures, "PNG must be 32-bit RGBA")


def test_wrong_bit_depth_fails() -> None:
    failures = checker.play_store_icon_failures(png_header(bit_depth=16))
    assert_failure_contains(failures, "bit depth 16")


def test_oversized_file_fails() -> None:
    failures = checker.play_store_icon_failures(png_header() + b"\x00" * 20, max_bytes=32)
    assert_failure_contains(failures, "limit is 32")


def main() -> int:
    tests = [
        test_valid_rgba_512_icon_passes,
        test_non_png_fails,
        test_short_png_header_fails,
        test_wrong_dimensions_fail,
        test_rgb_png_fails,
        test_wrong_bit_depth_fails,
        test_oversized_file_fails,
    ]
    for test in tests:
        test()
    print("PASS: Play Store icon checker self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
